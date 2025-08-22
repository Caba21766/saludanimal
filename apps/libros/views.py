from datetime import datetime
from decimal import Decimal

from django.db.models import Q, Sum, Value, DecimalField
from django.db.models.functions import Coalesce
from django.shortcuts import render

from apps.CarritoApp.models import Factura, CuentaCorriente, MetodoPago

def listar_ctacorriente(request):
    dni_cliente = (request.GET.get('dni_cliente') or '').strip()
    fecha = (request.GET.get('fecha') or '').strip()

    base_qs = Factura.objects.filter(
        Q(metodo_pago__tarjeta_nombre__iexact="Cuenta Corriente") |
        Q(metodo_pago_manual__iexact="Cuenta Corriente")
    ).select_related('metodo_pago')

    if request.user.is_staff:
        facturas = base_qs
        if dni_cliente:
            facturas = facturas.filter(dni_cliente=dni_cliente)
    else:
        facturas = base_qs.filter(dni_cliente=getattr(request.user, "dni_usuario", None))

    if fecha:
        try:
            ini = datetime.strptime(fecha, "%Y-%m-%d")
            fin = ini.replace(hour=23, minute=59, second=59)
            facturas = facturas.filter(fecha__range=[ini, fin])
        except ValueError:
            pass

    facturas = facturas.order_by('-numero_factura')

    # 👉 Valor cero decimal para Coalesce
    ZERO = Value(Decimal('0.00'),
                 output_field=DecimalField(max_digits=12, decimal_places=2))

    pagos_por_factura = {}
    for f in facturas:
        agg = CuentaCorriente.objects.filter(factura=f).aggregate(
            cuotas=Coalesce(Sum('imp_cuota_pagadas'), ZERO),
            entregas=Coalesce(Sum('entrega_cta'), ZERO),
        )
        total_pagado = (agg['cuotas'] or Decimal('0')) + (agg['entregas'] or Decimal('0'))
        pagos_por_factura[f.id] = total_pagado

    deuda_por_factura = {}
    for f in facturas:
        total = Decimal(getattr(f, 'total_con_interes', 0) or 0)
        pagado = pagos_por_factura.get(f.id, Decimal('0'))
        deuda = total - pagado
        if deuda < 0:
            deuda = Decimal('0')
        deuda_por_factura[f.id] = deuda

    facturas = [f for f in facturas if deuda_por_factura.get(f.id, Decimal('0')) > 0]

    total_general = sum(Decimal(getattr(f, 'total_con_interes', 0) or 0) for f in facturas)
    total_pagos   = sum(pagos_por_factura.get(f.id, Decimal('0')) for f in facturas)
    total_deuda   = sum(deuda_por_factura.get(f.id, Decimal('0')) for f in facturas)

    metodos_pago = MetodoPago.objects.exclude(
        tarjeta_nombre__iexact="Cuenta Corriente"
    ).order_by('tarjeta_nombre')

    return render(request, 'libros/listar_ctacorriente.html', {
        'facturas': facturas,
        'total_general': total_general,
        'total_pagos': total_pagos,
        'total_deuda': total_deuda,
        'pagos_por_factura': pagos_por_factura,
        'deuda_por_factura': deuda_por_factura,
        'metodos_pago': metodos_pago,
    })




#------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from apps.CarritoApp.models import Factura  # Asegúrate de tener un modelo Factura

def ver_factura_pdf(request, factura_id):
    # Busca la factura en la base de datos
    factura = Factura.objects.get(id=factura_id)

    # Configura la respuesta como PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Factura_{factura.numero_factura}.pdf"'

    # Genera el PDF
    p = canvas.Canvas(response)
    p.drawString(100, 750, f"Factura Nº: {factura.numero_factura}")
    p.drawString(100, 730, f"Cliente: {factura.nombre_cliente} {factura.apellido_cliente}")
    p.drawString(100, 710, f"Total: ${factura.total}")
    p.drawString(100, 690, f"Fecha: {factura.fecha}")

    p.showPage()
    p.save()

    return response

#------------------------------------------------------------------------
import json
from django.shortcuts import get_object_or_404, render
from apps.CarritoApp.models import Factura

def mostrar_factura_cta(request, factura_id):
    """Vista para mostrar los detalles de una factura incluyendo los productos vendidos."""

    # Obtener la factura o devolver error 404 si no existe
    factura = get_object_or_404(Factura, id=factura_id)

    # Intentar deserializar `detalle_productos` desde JSON
    try:
        detalles_productos = json.loads(factura.detalle_productos)  # Convierte JSON en lista de diccionarios
        print("Productos cargados:", detalles_productos)  # 🔍 Verifica si los productos se cargan correctamente
    except (json.JSONDecodeError, TypeError) as e:
        print("Error al cargar detalle_productos:", e)  # 🔍 Imprime el error en la consola
        detalles_productos = []  # Si hay un error, usar lista vacía

    # Renderizar la plantilla con los datos de la factura
    return render(request, 'libros/factura_detalle.html', {
        'factura': factura,
        'detalles_productos': detalles_productos
    })




#------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------

from django.shortcuts import render, get_object_or_404
from django.db.models import Sum
from django.utils.timezone import now
from decimal import Decimal
from django.http import JsonResponse
from apps.CarritoApp.models import Factura, CuentaCorriente, MetodoPago

def pago_credito(request, factura_id):
    factura = get_object_or_404(Factura, id=factura_id)
    cuenta_corriente = CuentaCorriente.objects.filter(factura=factura)

    # Totales previos
    total_pagos_data = cuenta_corriente.aggregate(
        total_cuotas=Sum('imp_cuota_pagadas', default=Decimal(0)),
        total_entregas=Sum('entrega_cta', default=Decimal(0))
    )
    total_pagos = (total_pagos_data['total_cuotas'] or Decimal(0)) + (total_pagos_data['total_entregas'] or Decimal(0))
    total_deuda = max(Decimal("0.00"), (factura.total_con_interes or Decimal(0)) - total_pagos)

    # ----- Suma de cuotas pagadas (tracking de cuotas) -----
    cantidad_cuotas = Decimal(request.POST.get("cantidad_cuotas", "1") or "1")
    cuotas_anteriores = CuentaCorriente.objects.filter(
        factura=factura
    ).aggregate(suma_total=Sum('cuota_paga'))['suma_total'] or Decimal("0.00")
    suma_actualizada = cuotas_anteriores + cantidad_cuotas
    cuota_total = Decimal(factura.cuotas or 0)
    cuota_debe = max(Decimal("0.00"), cuota_total - suma_actualizada)
    # -------------------------------------------------------

    if request.method == "POST":
        print("📌 Datos recibidos en Django:", request.POST)

        tipo_pago = request.POST.get("tipo_pago")  # "cuota" | "entrega"
        metodo_pago_id = request.POST.get("metodo_pago")  # ID o "Efectivo"

        # Datos comunes
        tarjeta_nombre = (request.POST.get("tarjeta_nombre") or "").strip()
        tarjeta_numero = (request.POST.get("tarjeta_numero") or "").strip()
        interes_aplicado = Decimal(request.POST.get("interes_aplicado", "0") or "0")

        # Resolver método de pago (FK) si no es efectivo
        if metodo_pago_id == "Efectivo":
            metodo_pago = None
        else:
            try:
                metodo_pago = MetodoPago.objects.get(id=int(metodo_pago_id))
            except (ValueError, MetodoPago.DoesNotExist):
                return JsonResponse({"success": False, "error": "Método de pago no válido."})

        # Normalización según tipo de pago (LIMPIA, sin duplicados)
        if tipo_pago == "cuota":
            # cuántas cuotas paga y cuánto representa en dinero
            cantidad_cuotas = Decimal(request.POST.get("cantidad_cuotas", "1") or "1")
            monto_por_cuota = factura.cuota_mensual or (
                (factura.total_con_interes or Decimal(0)) / Decimal(factura.cuotas or 1)
            )
            imp_cuota_pagadas = (monto_por_cuota * cantidad_cuotas)
            entrega_cta = Decimal(0)
            cuota_paga = cantidad_cuotas
            monto_pagado = imp_cuota_pagadas  # lo que efectivamente paga ahora
        else:
            # entrega a cuenta (no suma cuota)
            monto_pagado = Decimal(request.POST.get("monto_pagado", "0") or "0")
            imp_cuota_pagadas = Decimal(0)
            entrega_cta = monto_pagado
            cuota_paga = Decimal(0)

        # Validación de sobrepago
        if total_pagos + (monto_pagado or Decimal(0)) > (factura.total_con_interes or Decimal(0)):
            return JsonResponse({"success": False, "error": "El pago ingresado excede la deuda."})

        print(f"🛠️ imp_cuota_pagadas antes de guardar: {imp_cuota_pagadas}")

        # Guardar movimiento
        CuentaCorriente.objects.create(
            factura=factura,
            numero_factura=factura.numero_factura,
            descripcion=f"Pago de {tipo_pago} con {metodo_pago.tarjeta_nombre if metodo_pago else 'Efectivo'}",
            total_con_interes=factura.total_con_interes,
            fecha_cuota=now().date(),
            imp_cuota_pagadas=imp_cuota_pagadas,
            entrega_cta=entrega_cta,
            metodo_pago=metodo_pago,           # auditoría
            tarjeta_nombre="Cuenta Corriente", # mantener etiqueta del método original
            tarjeta_numero=tarjeta_numero if metodo_pago else None,
            cuota_total=factura.cuotas,
            cuota_paga=cuota_paga,
            cuota_suma=suma_actualizada,
            cuota_debe=cuota_debe,
            interes_aplicado=interes_aplicado,
        )

        # Recalcular totales luego del alta
        nuevo_total = CuentaCorriente.objects.filter(factura=factura).aggregate(
            total_cuotas=Sum('imp_cuota_pagadas', default=Decimal(0)),
            total_entregas=Sum('entrega_cta', default=Decimal(0))
        )
        total_pagado_final = (nuevo_total['total_cuotas'] or Decimal(0)) + (nuevo_total['total_entregas'] or Decimal(0))

        # Cerrar crédito si corresponde (SIN doble seteo)
        if total_pagado_final >= (factura.total_con_interes or Decimal(0)):
            factura.estado_credito = "Pagado"

            # Mantener "Cuenta Corriente" si originalmente lo era
            if not (
                factura.metodo_pago_manual == "Cuenta Corriente" or
                (factura.metodo_pago and factura.metodo_pago.tarjeta_nombre == "Cuenta Corriente")
            ):
                # Si se saldó con entrega en efectivo exacta y no era CC
                if tipo_pago == "entrega" and metodo_pago_id == "Efectivo" and monto_pagado == factura.total_con_interes:
                    factura.metodo_pago = None
                    factura.metodo_pago_manual = "Efectivo"
                else:
                    factura.metodo_pago = metodo_pago
                    factura.metodo_pago_manual = metodo_pago.tarjeta_nombre if metodo_pago else "Sin especificar"

            factura.save()

        return JsonResponse({"success": True, "message": "Pago registrado con éxito."})

    # GET: datos para renderizar
    total_cuotas_pagadas = cuenta_corriente.aggregate(suma=Sum('cuota_paga'))['suma'] or 0
    cuotas_restantes = max(0, (factura.cuotas or 0) - total_cuotas_pagadas)

    nuevo_total_pagado = CuentaCorriente.objects.filter(factura=factura).aggregate(
        total_cuotas=Sum('imp_cuota_pagadas', default=Decimal(0)),
        total_entregas=Sum('entrega_cta', default=Decimal(0))
    )
    total_pagado_final = (nuevo_total_pagado['total_cuotas'] or Decimal(0)) + (nuevo_total_pagado['total_entregas'] or Decimal(0))
    estado_credito = "Pagado" if total_pagado_final >= (factura.total_con_interes or Decimal(0)) else "Pendiente"

    metodos_pago = MetodoPago.objects.all()
    return render(request, "libros/pago_credito.html", {
        "factura": factura,
        "total_pagos": total_pagos,
        "total_deuda": total_deuda,
        "metodos_pago": metodos_pago,
        "total_cuotas_pagadas": total_cuotas_pagadas,
        "cuotas_restantes": cuotas_restantes,
        "estado_credito": estado_credito,
    })





#------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------
import json
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from fpdf import FPDF # type: ignore
from apps.CarritoApp.models import Factura

def generar_factura_pdf(request, factura_id):
    # Obtén la factura
    factura = get_object_or_404(Factura, id=factura_id)

    # Deserializa el campo detalle_productos
    try:
        detalles = json.loads(factura.detalle_productos)  # Convierte el JSON a una lista de diccionarios
    except json.JSONDecodeError:
        detalles = []  # Si no es un JSON válido, usamos una lista vacía

    # Crear el PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Encabezado
    pdf.cell(200, 10, txt="Factura Detallada", ln=True, align='C')
    pdf.ln(10)

    # Información general
    pdf.cell(200, 10, txt=f"Factura Nº: {factura.numero_factura}", ln=True)
    pdf.cell(200, 10, txt=f"Cliente: {factura.nombre_cliente} {factura.apellido_cliente}", ln=True)
    pdf.cell(200, 10, txt=f"Fecha: {factura.fecha}", ln=True)
    pdf.cell(200, 10, txt=f"Estado Crédito: {factura.estado_credito}", ln=True)
    pdf.cell(200, 10, txt=f"Cuotas: {factura.cuotas}", ln=True)
    pdf.cell(200, 10, txt=f"Interés (%): {factura.interes}", ln=True)
    pdf.cell(200, 10, txt=f"Total con Interés: ${factura.total_con_interes}", ln=True)
    pdf.ln(10)

    # Tabla de productos
    pdf.set_font("Arial", size=10)
    pdf.cell(40, 10, txt="N° Producto", border=1, align='C')
    pdf.cell(80, 10, txt="Nombre Producto", border=1, align='C')
    pdf.cell(30, 10, txt="Cantidad", border=1, align='C')
    pdf.cell(40, 10, txt="Precio Unitario", border=1, align='C')
    pdf.ln()

    for detalle in detalles:
        pdf.cell(40, 10, txt=detalle.get('numero_producto', ''), border=1)
        pdf.cell(80, 10, txt=detalle.get('nombre_producto', ''), border=1)
        pdf.cell(30, 10, txt=str(detalle.get('cantidad_vendida', '')), border=1)
        pdf.cell(40, 10, txt=f"${detalle.get('precio_unitario', '')}", border=1)
        pdf.ln()

    # Pie de página
    pdf.ln(10)
    pdf.cell(200, 10, txt="Gracias por su compra.", ln=True, align='C')

    # Devuelve el PDF como respuesta HTTP
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Factura_{factura.numero_factura}.pdf"'
    response.write(pdf.output(dest='S').encode('latin1'))
    return response

#------------------------------------------------------------------------------------
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Sum
from apps.CarritoApp.models import CuentaCorriente

def eliminar_pago_credito(request, pago_id):
    # Intentar obtener el registro, si no existe, redirigir con un mensaje de error
    pago = CuentaCorriente.objects.filter(id=pago_id).first()
    
    if not pago:
        print(f"⚠️ ERROR: No se encontró el pago con ID {pago_id}")
        return redirect("libros:listar_ctacorriente")  # Redirigir a la lista si no existe
    
    factura_id = pago.factura.id  # Guardamos el ID de la factura antes de eliminar
    
    pago.delete()  # Eliminar el pago
    
    # Recalcular la suma de pagos después de eliminar (corregido el nombre del campo)
    total_pagos = CuentaCorriente.objects.filter(factura_id=factura_id).aggregate(
        total_pagado=Sum('imp_cuota_pagadas') + Sum('entrega_cta')
    )['total_pagado'] or 0  # Si no hay registros, poner 0

    return redirect("libros:pago_credito", factura_id)

#-----------------------------------------------------------------from django.db.models 
from django.db.models import Sum
from django.shortcuts import render, get_object_or_404
from apps.CarritoApp.models import CuentaCorriente, Factura

def listar_cuenta_corriente(request, factura_id):
    print(f"🔹 Buscando pagos en CuentaCorriente para factura ID: {factura_id}")

    # Obtener la factura
    factura = get_object_or_404(Factura, id=factura_id)

    factura_id = factura.id # Guardamos el ID de la factura antes de eliminar

    # Filtrar pagos por factura_id y excluir valores NULL
    cuentas_corrientes = CuentaCorriente.objects.filter(factura_id=factura_id).exclude(imp_cuota_pagadas__isnull=True)

    # Obtener la suma de imp_cuota_pagadas
    imp_cuotas_abonadas = cuentas_corrientes.aggregate(total=Sum('imp_cuota_pagadas'))['total'] or 0

    # Depuración en la terminal
    print("✅ --- DEPURACIÓN EN TERMINAL --- ✅")
    print(f"🔹 ID de la Factura Pasado a la Plantilla: {factura_id}")
    print("✅ --- FIN DEPURACIÓN --- ✅")

    # Pasar los datos a la plantilla
    return render(request, 'libros/factura_detalle.html', {
        'factura': factura,
        'cuentas_corrientes': cuentas_corrientes,
        'Imp_Cuotas_Abonadas': imp_cuotas_abonadas,
        'factura_id': factura_id  # Asegurar que la plantilla reciba factura_id
    })

#------------------------------------------------------------------------------------

from django.http import JsonResponse, HttpResponse
from django.db.models import Sum
from apps.CarritoApp.models import CuentaCorriente
import logging
logger = logging.getLogger(__name__)

def sumar_imp_cuota(request, factura_id):
    logger.info(f"🔹 Calculando total de imp_cuota_pagadas para factura ID: {factura_id}")

    total_imp_cuota = CuentaCorriente.objects.filter(factura_id=factura_id).aggregate(total=Sum('imp_cuota_pagadas'))['total'] or 0

    logger.info("✅ --- DEPURACIÓN EN TERMINAL --- ✅")
    logger.info(f"🔹 Total Imp Cuota Pagadas: {total_imp_cuota}")
    logger.info("✅ --- FIN DEPURACIÓN --- ✅")

    return JsonResponse({'total_imp_cuota_pagadas': total_imp_cuota})

#------------------------------------------------------------------------------------
from django.http import HttpResponse  
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from apps.CarritoApp.models import Factura

def generar_pdf_credito(request, factura_id):
    factura = Factura.objects.get(id=factura_id)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="factura_{factura_id}.pdf"'

    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    p.setFont("Helvetica-Bold", 16)
    p.drawString(200, height - 50, f"Pago crédito de Factura Nº {factura.numero_factura}")

    p.setFont("Helvetica", 12)
    p.drawString(50, height - 100, f"Fecha: {factura.fecha}")
    p.drawString(50, height - 120, f"Cliente: {factura.nombre_cliente} {factura.apellido_cliente}")
    p.drawString(50, height - 140, f"DNI Cliente: {factura.dni_cliente}")
    p.drawString(50, height - 160, f"Total Crédito: ${factura.total_con_interes}")

    # ------------------Dibujar una línea horizontal antes del historial ----------------------
    y_position = height - 180  # Definir un valor inicial para y_position
    p.line(50, y_position, 400, y_position)
    y_position -= 30  # Espaciado adicional después de la línea

    # Título del Historial de Pagos
    p.drawString(50, y_position, "Historial de Pagos:")
    y_position -= 20  # Espaciado antes de la lista de pagos

    # Variables para almacenar los totales
    total_cuotas_pagadas = 0
    total_entregas_cta = 0

    ultimo_pago = factura.cuenta_corriente.order_by('-fecha_cuota').first()

    for pago in factura.cuenta_corriente.all():
        if pago.imp_cuota_pagadas > 0:  # Solo mostrar si es mayor a 0
            p.drawString(50, y_position, f"{pago.fecha_cuota} - {pago.descripcion} - Cuota Pagada:${pago.imp_cuota_pagadas}")
            total_cuotas_pagadas += pago.imp_cuota_pagadas  # Acumulando la suma
            y_position -= 20

        if pago.entrega_cta > 0:  # Solo mostrar si es mayor a 0
            p.drawString(50, y_position, f"{pago.fecha_cuota} - Entrega a Cuenta: ${pago.entrega_cta}")
            total_entregas_cta += pago.entrega_cta  # Acumulando la suma
            y_position -= 20

    # Espaciado antes de mostrar el total final
    y_position -= 20

    # Calcular la suma total de Cuotas Pagadas + Entregas a Cuenta
    total_pago_realizado = total_cuotas_pagadas + total_entregas_cta

    # ------------------Dibujar una línea horizontal antes del total ----------------------
    p.line(50, y_position, 400, y_position)
    y_position -= 30  # Espaciado adicional después de la línea

    # Mostrar el total pago realizado
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y_position, f"Total Pago Realizado: ${total_pago_realizado}")
    y_position -= 20  # Espaciado antes de mostrar el total restante

    # Calcular el total restante a pagar
    total_restante = factura.total_con_interes - total_pago_realizado

    # Dibujar una línea antes del total restante
    p.line(50, y_position, 400, y_position)
    y_position -= 30  # Espaciado adicional después de la línea

    # Mostrar el total restante
    p.setFont("Helvetica-Bold", 12)
    p.setFillColorRGB(1, 0, 0)  # Color rojo para resaltar la deuda
    p.drawString(50, y_position, f"Total Restante a Pagar: ${total_restante}")
    
    ultimo_pago = factura.cuenta_corriente.last()
    y_position -= 20  # 👈 bajamos para evitar que se superpongan
    
    if ultimo_pago:
        p.drawString(50, y_position, f"Interés Varios: ${ultimo_pago.interes_aplicado}")
        p.setFillColorRGB(0, 0, 0)  # Volver al color negro normal
    else:
        p.drawString(50, y_position, "Interés Varios: -")

    p.showPage()
    p.save()
    return response















