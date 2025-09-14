from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Producto, Categ_producto
from .forms import ProductoForm
import os
from django.conf import settings

def agregar_o_modificar_producto(request, pk=None):
    # Si se proporciona pk, estamos editando un producto existente
    if pk:
        producto = get_object_or_404(Producto, pk=pk)
    else:
        producto = None  # Si no hay pk, estamos creando un nuevo producto

    # Verifica si el usuario está autenticado
    if not request.user.is_authenticated:
        messages.error(request, "Debes iniciar sesión para agregar o modificar productos.")
        return redirect('iniciar_sesion')

    if request.method == "POST":
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        
        # 🔹 Depuración: Verificar si el formulario es válido
        if not form.is_valid():
            print("Errores en el formulario:", form.errors)
            messages.error(request, "Hay errores en el formulario. Revisa los campos.")
        else:
            producto = form.save(commit=False)  # No guardar aún en la BD

            # 🔹 Manejo de imágenes (si se reemplazan)
            for campo in ['imagen', 'imagen2', 'imagen3', 'imagen4', 'imagen5']:
                nueva_imagen = request.FILES.get(campo)  # Obtener nueva imagen
                imagen_actual = getattr(producto, campo)  # Obtener imagen actual en la BD

                if nueva_imagen:  # Si el usuario sube una nueva imagen
                    if imagen_actual:  # Si hay una imagen guardada, eliminarla antes de reemplazarla
                        ruta_imagen = os.path.join(settings.MEDIA_ROOT, str(imagen_actual))
                        if os.path.exists(ruta_imagen):
                            os.remove(ruta_imagen)  # 🔹 Eliminar imagen anterior

                    setattr(producto, campo, nueva_imagen)  # Guardar la nueva imagen en el modelo

            producto.save()  # 🔹 Ahora sí, guardar en la BD
            messages.success(request, "Producto guardado correctamente.")
            return redirect('CarritoApp:agregar_producto')

    else:
        form = ProductoForm(instance=producto)  # Si es GET, cargar el formulario con los datos existentes

    # Filtrar productos por categoría
    categoria_id = request.GET.get('categoria', None)
    if categoria_id:
        productos = Producto.objects.filter(categoria_id=categoria_id)
    else:
        productos = Producto.objects.all()

    categorias = Categ_producto.objects.all()

    return render(request, 'agregar_producto.html', {
        'form': form,
        'productos': productos,
        'categorias': categorias,
    })


#-------------Eliminar Producto-------------------------------------------#

from django.shortcuts import get_object_or_404, redirect
from .models import Producto

def eliminar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    producto.delete()  # Elimina el producto
    return redirect('CarritoApp:agregar_producto')  # Redirige a la vista de agregar productos


#-----------Agregar Compra---------------------------------#
# -----apps/CarritoApp/views.py -- 
# apps/CarritoApp/views.py

from django.contrib import messages
from .models import Compra, Producto
from .forms import CompraForm
from django.shortcuts import render, get_object_or_404, redirect

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Compra, Producto
from .forms import CompraForm

TEMPLATE_AGREGAR_COMPRA = 'agregar_compra.html'  # 👈 así, sin prefijo

def agregar_compra(request):
    compras = Compra.objects.all().order_by('-fecha_compra')

    producto_pre = None
    pid = (request.GET.get('producto_id') or '').strip()
    if pid.isdigit():
        producto_pre = get_object_or_404(Producto, pk=int(pid))

    if request.method == 'POST':
        form = CompraForm(request.POST, request.FILES)

        numero_producto = (request.POST.get('numero_producto') or '').strip()
        producto_id = (request.POST.get('producto_id') or '').strip()

        producto = None
        if numero_producto.isdigit():
            producto = Producto.objects.filter(numero_producto=numero_producto).first()
        if not producto and producto_id.isdigit():
            producto = Producto.objects.filter(id=int(producto_id)).first()
        if not producto and producto_pre:
            producto = producto_pre

        if not producto:
            messages.error(request, "No se encontró el producto. Verificá el número o seleccioná uno.")
            return render(request, TEMPLATE_AGREGAR_COMPRA,  # 👈 nombre corto
                          {'form': form, 'compras': compras, 'producto': producto_pre})

        if form.is_valid():
            compra = form.save(commit=False)
            compra.producto = producto
            compra.save()
            messages.success(request, "¡Compra guardada correctamente!")
            return redirect('CarritoApp:agregar_producto')

        messages.error(request, "Hay errores en el formulario. Verificá los datos.")
        return render(request, TEMPLATE_AGREGAR_COMPRA,
                      {'form': form, 'compras': compras, 'producto': producto_pre})

    form = CompraForm()
    return render(request, TEMPLATE_AGREGAR_COMPRA,
                  {'form': form, 'compras': compras, 'producto': producto_pre})











#-----------de compra... es un JSON----------------------------------------#
from django.http import JsonResponse
from .models import Producto

def obtener_producto(request):
    numero_producto = request.GET.get('numero_producto')
    try:
        producto = Producto.objects.get(numero_producto=numero_producto)
        return JsonResponse({'nombre_producto': producto.nombre_producto})
    except Producto.DoesNotExist:
        return JsonResponse({'nombre_producto': ''})  # Retorna vacío si no existe

from django.http import JsonResponse
from .models import Producto

#-----------de compra... es un JSON 22222----------------------------------------#
from django.http import JsonResponse
from .models import Producto

def obtener_nombre_producto(request):
    numero_producto = request.GET.get('numero_producto')
    if numero_producto:
        try:
            producto = Producto.objects.get(numero_producto=numero_producto)
            return JsonResponse({'nombre_producto': producto.nombre_producto})
        except Producto.DoesNotExist:
            return JsonResponse({'nombre_producto': ''})  # Producto no encontrado
    return JsonResponse({'nombre_producto': ''})  # Número de producto no proporcionado

#-----------de compra... es un JSON 22222----------------------------------------#
from django.http import JsonResponse
from .models import Producto

def obtener_numero_producto(request):
    nombre_producto = request.GET.get('nombre_producto', '')
    try:
        producto = Producto.objects.get(nombre_producto__iexact=nombre_producto)
        return JsonResponse({'numero_producto': producto.numero_producto})
    except Producto.DoesNotExist:
        return JsonResponse({'numero_producto': ''})

#-----------buscar producto de compra----------------------------------------#
from django.http import JsonResponse
from .models import Producto
from django.http import JsonResponse
from .models import Producto

def buscar_productos(request):
    query = request.GET.get('query', '').strip()  # Elimina espacios adicionales al inicio y al final
    print(f"Consulta recibida: '{query}'")  # Depuración: Verifica el valor de query

    if query:
        productos = Producto.objects.filter(nombre_producto__icontains=query).values('nombre_producto', 'numero_producto')
        print(f"Productos encontrados: {list(productos)}")  # Depuración: Muestra los productos encontrados
        return JsonResponse({'productos': list(productos)}, status=200)
    
    print("No se recibió una consulta válida.")  # Depuración: No se recibió query
    return JsonResponse({'productos': []}, status=200)


#-----------Modificar Compra----------------------------------------#
def modificar_compra(request, pk):
    compra = get_object_or_404(Compra, pk=pk)
    print("Compra seleccionada:", compra)  # Depuración
    if request.method == 'POST':
        form = CompraForm(request.POST, instance=compra)
        if form.is_valid():
            form.save()
            return redirect('CarritoApp:planilla_compra')
    else:
        form = CompraForm(instance=compra)
    print("Formulario cargado:", form)  # Depuración
    return render(request, 'CarritoApp/modificar_compra.html', {'form': form})


#-----------Eliminar Compra----------------------------------------#
from django.shortcuts import get_object_or_404, redirect
from .models import Compra, Producto

def eliminar_compra(request, pk):
    compra = get_object_or_404(Compra, pk=pk)
    
    if request.method == 'POST':
        # Obtener el producto relacionado
        producto = compra.producto  # Asumiendo que hay un ForeignKey a Producto en el modelo Compra
        
        # Actualizar el stock del producto
        if producto:
            producto.stock -= compra.cantidad  # Sumar la cantidad de la compra al stock
            producto.save()
        
        # Eliminar la compra
        compra.delete()
        
        # Redirigir a la vista de agregar compras
        return redirect('CarritoApp:planilla_compra')
    
    # Renderizar una confirmación de eliminación (opcional)
    return render(request, 'confirmar_eliminar.html', {'compra': compra})


# ---------Planilla de Compra - planilla de Compra con filtros --------------
from django.shortcuts import render
from .models import Compra
from decimal import Decimal

# Planilla1
def planilla_compra(request):
    compras = Compra.objects.all()

    # Filtros
    producto = request.GET.get('producto')
    fecha_compra = request.GET.get('fecha_compra')
    factura = request.GET.get('factura')
    proveedor = request.GET.get('proveedor')

    if producto:
        compras = compras.filter(producto__nombre_producto__icontains=producto)
    if fecha_compra:
        compras = compras.filter(fecha_compra=fecha_compra)
    if factura:
        compras = compras.filter(factura_compra__icontains=factura)
    if proveedor:
        compras = compras.filter(provedor__nombre__icontains=proveedor)

    # 🔽 orden: fecha desc, y de yapa id desc para desempatar
    compras = compras.order_by('-fecha_compra', '-id')

    # Totales
    total_cantidad = sum(c.cantidad for c in compras if c.cantidad)
    from decimal import Decimal
    total_precio = sum(Decimal(c.precio_compra) for c in compras if c.precio_compra)

    return render(request, 'CarritoApp/planilla_compra.html', {
        'compras': compras,
        'total_cantidad': total_cantidad,
        'total_precio': total_precio,
    })



# --------------------Listado de Compra - listado de Compra con filtros --------------
#------------------Agregar_categorias-------------------------------
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import CategoriaForm
from .models import Categ_producto

def agregar_categoria(request):
    categorias = Categ_producto.objects.all()

    # Manejo de eliminación
    if 'delete_id' in request.GET:
        delete_id = request.GET.get('delete_id')
        categoria = get_object_or_404(Categ_producto, id=delete_id)
        categoria.delete()
        messages.success(request, "Categoría eliminada exitosamente.")
        return redirect('CarritoApp:agregar_categoria')

    # Manejo de modificación
    if 'edit_id' in request.GET:
        edit_id = request.GET.get('edit_id')
        categoria = get_object_or_404(Categ_producto, id=edit_id)
        form = CategoriaForm(request.POST or None, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, "Categoría modificada exitosamente.")
            return redirect('CarritoApp:agregar_categoria')
    else:
        # Formulario para agregar nuevas categorías
        form = CategoriaForm(request.POST or None)
        if form.is_valid():
            form.save()
            messages.success(request, "Categoría agregada exitosamente.")
            return redirect('CarritoApp:agregar_categoria')

    return render(request, 'agregar_categoria.html', {
        'form': form,
        'categorias': categorias,
    })

#-------------------------------------#
#-----Agregar_provedores----------------------------

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import ProvedorForm
from .models import Provedor

def agregar_provedor(request):
    provedores = Provedor.objects.all()

    # Manejo de eliminación
    if 'delete_id' in request.GET:
        delete_id = request.GET.get('delete_id')
        provedor = get_object_or_404(Provedor, id=delete_id)
        provedor.delete()
        messages.success(request, "Proveedor eliminado exitosamente.")
        return redirect('CarritoApp:agregar_provedor')

    # Manejo de modificación
    if 'edit_id' in request.GET:
        edit_id = request.GET.get('edit_id')
        provedor = get_object_or_404(Provedor, id=edit_id)
        form = ProvedorForm(request.POST or None, instance=provedor)
        if form.is_valid():
            form.save()
            messages.success(request, "Proveedor modificado exitosamente.")
            return redirect('CarritoApp:agregar_provedor')
    else:
        # Formulario para agregar nuevos proveedores
        form = ProvedorForm(request.POST or None)
        if form.is_valid():
            form.save()
            messages.success(request, "Proveedor agregado exitosamente.")
            return redirect('CarritoApp:agregar_provedor')

    return render(request, 'agregar_provedor.html', {
        'form': form,
        'provedores': provedores,
    })


#-----------------------------REALIZAR VENTAS -----------------------#
from django.shortcuts import render, redirect
from .forms import VentaForm
from .models import Venta, Producto
import logging

logger = logging.getLogger(__name__)

def realizar_venta(request):
    mensaje = None
    if request.method == 'POST':
        form = VentaForm(request.POST)
        if form.is_valid():
            venta = form.save(commit=False)  # No guarda aún en la BD
            producto = venta.producto  # Obtiene el producto asociado
            
            # Validación de stock
            if venta.cantidad > producto.stock:
                mensaje = "Stock insuficiente. No se pudo realizar la venta."
            else:
                # Registra el stock antes y después de la operación
                logger.info(f"Stock antes: {producto.stock} - Cantidad vendida: {venta.cantidad}")
                producto.stock -= venta.cantidad
                producto.save()  # Guarda el producto con el stock actualizado
                logger.info(f"Stock después: {producto.stock}")
                
                venta.usuario = request.user  # Asigna el usuario actual
                venta.save()  # Guarda la venta
                mensaje = "Venta registrada con éxito."
                form = VentaForm()  # Reinicia el formulario
        else:
            mensaje = "Por favor completa todos los campos correctamente."
    else:
        form = VentaForm()

    ventas = Venta.objects.all()  # Obtén todas las ventas para mostrar
    return render(request, 'realizar_venta.html', {
        'form': form,
        'ventas': ventas,
        'mensaje': mensaje
    })

#--------------------Listado de Ventas-----------------------

from django.shortcuts import render
from .models import Venta

def listar_ventas(request):
    ventas = Venta.objects.all()
    return render(request, 'listar_ventas.html', {'ventas': ventas})



#----------------- ----Calcular Total  Carrito----------------- -- 
from django.shortcuts import render, get_object_or_404, redirect
from .models import Producto

def calcular_total_carrito(carrito):
    total = 0
    for item in carrito.values():
        total += item['cantidad'] * item['precio']
    return total

#---------------------RESTAR del Carrito-------------/views.py --

from django.shortcuts import get_object_or_404, redirect
from .models import Producto

def restar_del_carrito(request, producto_id):
    carrito = request.session.get('carrito', {})  # Obtén el carrito de la sesión

    if str(producto_id) in carrito:
        if carrito[str(producto_id)]['cantidad'] > 1:
            # Resta una unidad del producto en el carrito
            carrito[str(producto_id)]['cantidad'] -= 1
            carrito[str(producto_id)]['acumulado'] -= float(carrito[str(producto_id)]['precio'])
        else:
            # Si la cantidad es 1, elimina el producto del carrito
            del carrito[str(producto_id)]
    
    request.session['carrito'] = carrito  # Actualiza el carrito en la sesión
    return redirect('CarritoApp:ver_carrito')


#---------------------Sumar del Carrito-------------/views.py --
def sumar_producto(request, producto_id):
    carrito = request.session.get('carrito', {})  # Obtén el carrito de la sesión

    if str(producto_id) in carrito:
        carrito[str(producto_id)]['cantidad'] += 1
        carrito[str(producto_id)]['acumulado'] += float(carrito[str(producto_id)]['precio'])

    request.session['carrito'] = carrito  # Actualiza el carrito en la sesión
    return redirect('CarritoApp:ver_carrito')  # Redirigir a la plantilla carrito



#---------------Limpiar Carrito----------------------------- --

def limpiar_carrito(request):
    request.session['carrito'] = {}
    return redirect('CarritoApp:ver_carrito')

#----------------- ----TIENDA aqui enumera la factura-------------/views.py --
from datetime import datetime
from .models import Factura, Producto, Categ_producto
from django.shortcuts import render
from django.core.paginator import Paginator

def tienda(request):
    # Verificar si el usuario está autenticado
    if request.user.is_authenticated:
        usuario = request.user
        nombre_usuario = usuario.first_name
        apellido_usuario = usuario.last_name
    else:
        nombre_usuario = "Desconocido"
        apellido_usuario = "Usuario"
    #------------------------------
    # Obtener la última factura registrada
    ultima_factura = Factura.objects.order_by('-id').first()  # Se asegura de obtener la última factura creada

    # Verificar que exista una factura previa y que su número sea válido
    if ultima_factura and ultima_factura.numero_factura.isdigit():
        numero_factura = str(int(ultima_factura.numero_factura) + 1).zfill(5)  # Incrementa el número y lo formatea a 5 dígitos
    else:
        numero_factura = "00001"  # Si no hay facturas previas, inicia desde 00001
    #------------------------------
    # Filtro por categoría
    categoria_id = request.GET.get('categoria')  # Obtiene el ID de la categoría desde el parámetro GET
    if categoria_id:
        productos = Producto.objects.filter(categoria_id=categoria_id)  # Filtra productos por categoría seleccionada
    else:
        productos = Producto.objects.all()  # Muestra todos los productos si no se selecciona categoría

    # Paginación
    paginator = Paginator(productos, 5)  # Muestra 3 productos por página
    page_number = request.GET.get('page')  # Obtiene el número de página desde el parámetro GET
    productos_pagina = paginator.get_page(page_number)  # Obtiene los productos de la página actual

    # Obtener todas las categorías para mostrar en el filtro
    categorias = Categ_producto.objects.all()

    # Verificar si se agregó un producto al carrito
    producto_en_carrito = False
    if request.GET.get('producto_id'):
        producto_en_carrito = True

    # Otros datos
    fecha_actual = datetime.now().strftime('%Y-%m-%d')
    carrito = request.session.get('carrito', {})
    total_carrito = calcular_total_carrito(carrito)

    # Contexto para renderizar
    context = {
        'productos_pagina': productos_pagina,  # Productos paginados
        'categorias': categorias,  # Todas las categorías
        'carrito': carrito,  # Carrito de compras
        'total_carrito': total_carrito,  # Total del carrito
        'numero_factura': numero_factura,  # Número de la factura
        'fecha': fecha_actual,  # Fecha actual
        'nombre': nombre_usuario,  # Nombre del usuario
        'apellido': apellido_usuario,  # Apellido del usuario
        'categoria_seleccionada': categoria_id,  # Categoría seleccionada
        'producto_en_carrito': producto_en_carrito,  # Variable para mostrar el modal
    }

    return render(request, 'tienda.html', context)



#---------------------AGREGAR AL CARRITO-------------/views.py --
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Producto

def agregar_al_carrito(request, producto_id):

    # Verifica si el usuario está autenticado
    if not request.user.is_authenticated:
        
        return redirect('tienda')  # En lugar de redirigir a iniciar sesión, lo redirige a la tienda
    
    # Si está autenticado, agrega el producto al carrito
    producto = get_object_or_404(Producto, id=producto_id)
    carrito = request.session.get('carrito', {})

    if str(producto_id) not in carrito:
        carrito[str(producto_id)] = {
            'producto_id': producto_id,  # Incluye el ID del producto aquí
            'nombre': producto.nombre_producto,  # Ajusta según tu modelo
            'precio': float(producto.precio),
            'cantidad': 1,
            'acumulado': float(producto.precio),
        }
    else:
        carrito[str(producto_id)]['cantidad'] += 1
        carrito[str(producto_id)]['acumulado'] += float(producto.precio)

    request.session['carrito'] = carrito
    return redirect('CarritoApp:tienda')  # Redirige a la tienda o donde prefieras


#----------------- CARRITO por falta de mercaderia ------------------------------------
from django.shortcuts import render

def carrito(request):
    carrito = request.session.get('carrito', {})
    return render(request, 'CarritoApp/carrito.html', {'carrito': carrito})

#---------------------pago_fallido------------------
from django.shortcuts import render
   
def pago_fallo(request):
    return render(request, 'CarritoApp/pago_fallo.html')

def pago_pendiente(request):
    return render(request, 'CarritoApp/pago_pendiente.html')

#-------------------------------------------------------------------------------
from django.shortcuts import redirect

def pago_fallido(request):
    # Podés mostrar un mensaje con messages.error si querés
    return redirect('CarritoApp:tienda')







#------------------- Confirmar Pago --------------------------

from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from .models import Factura, Producto

def confirmar_pago(request):
    if request.method == 'POST':
        metodo_pago = request.POST.get('metodo_pago')
        carrito = request.session.get('carrito', {})

        if not carrito:
            messages.error(request, 'No hay productos en el carrito.')
            return redirect('CarritoApp:carrito')

        # Crear la nueva factura
        nueva_factura = Factura.objects.create(
            numero_factura=Factura.objects.count() + 1,
            fecha=datetime.now(),
            nombre_cliente=request.user.first_name,
            apellido_cliente=request.user.last_name,
            metodo_pago=metodo_pago,
            total=sum(item['acumulado'] for item in carrito.values())
        )

        # Recorrer los productos en el carrito
        for item_id, item_data in carrito.items():
            producto = get_object_or_404(Producto, id=item_data['producto_id'])

            # Guardar la cantidad vendida
            nueva_factura.productos.add(
                producto,
                through_defaults={'cantidad_vendida': item_data['cantidad']}
            )

            # Restar el stock del producto
            producto.stock -= item_data['cantidad']
            producto.save()

        # Limpiar el carrito
        del request.session['carrito']
        request.session.modified = True

        messages.success(request, 'Factura guardada exitosamente.')
        return redirect('CarritoApp:tienda')

    messages.error(request, 'Método no permitido.')
    return redirect('CarritoApp:carrito')




#-------------Listar factura es del listado de facturas---------------------

from django.db.models import Sum, Value, Case, When, CharField, F, ExpressionWrapper, DecimalField, Q
from django.db.models.functions import Trim, Lower
from django.shortcuts import render
from apps.CarritoApp.models import Factura, MetodoPago, CuentaCorriente

def lista_cierre_de_caja(request):
    facturas = Factura.objects.all().order_by('-fecha', '-numero_factura')

    # Filtros
    vendedor = request.GET.get('vendedor', '')
    fecha_desde = request.GET.get('fecha_desde', '')
    fecha_hasta = request.GET.get('fecha_hasta', '')
    metodo_pago = request.GET.get('metodo_pago', '')

    if vendedor:
        facturas = facturas.filter(vendedor__icontains=vendedor)
    if fecha_desde:
        facturas = facturas.filter(fecha__gte=fecha_desde)
    if fecha_hasta:
        facturas = facturas.filter(fecha__lte=fecha_hasta)
    if metodo_pago:
        metodo_obj = MetodoPago.objects.filter(tarjeta_nombre=metodo_pago).first()
        if metodo_obj:
            facturas = facturas.filter(metodo_pago=metodo_obj)

    # Agrupación por vendedor
    totales_por_vendedor = (
        facturas
        .annotate(vendedor_normalizado=Trim(Lower('vendedor')))
        .values('vendedor_normalizado')
        .annotate(total=Sum('total_con_interes'))
        .order_by('vendedor_normalizado')
    )

    # Agrupación por método de pago (para visualización)
    totales_por_metodo = (
        facturas
        .annotate(
            metodo_normalizado=Case(
                When(metodo_pago__tarjeta_nombre__isnull=False, then=Trim(Lower('metodo_pago__tarjeta_nombre'))),
                When(metodo_pago_manual__isnull=False, then=Trim(Lower('metodo_pago_manual'))),
                default=Value('sin especificar'),
                output_field=CharField(),
            )
        )
        .values('metodo_normalizado')
        .annotate(total=Sum('total_con_interes'))
        .order_by('metodo_normalizado')
    )

    # Agrupación por método de pago (por nombre)
    totales_por_metodo_nombre = (
        facturas
        .values('metodo_pago__tarjeta_nombre')
        .annotate(total=Sum('total_con_interes'))
        .order_by('metodo_pago__tarjeta_nombre')
    )

    # 💰 Pagos de Cuenta Corriente (con los mismos filtros)
    pagos_cta_corriente = CuentaCorriente.objects.filter(
        Q(factura__metodo_pago__tarjeta_nombre__iexact="cuenta corriente") |
        Q(factura__metodo_pago_manual__iexact="cuenta corriente")
    )
    if fecha_desde:
        pagos_cta_corriente = pagos_cta_corriente.filter(fecha_cuota__gte=fecha_desde)
    if fecha_hasta:
        pagos_cta_corriente = pagos_cta_corriente.filter(fecha_cuota__lte=fecha_hasta)
    if vendedor:
        pagos_cta_corriente = pagos_cta_corriente.filter(factura__vendedor__icontains=vendedor)

    # Optimiza acceso a factura desde pagos
    pagos_cta_corriente = pagos_cta_corriente.select_related('factura').order_by('-fecha_cuota')

    total_cuotas = pagos_cta_corriente.aggregate(total=Sum('imp_cuota_pagadas'))['total'] or 0
    total_entregas = pagos_cta_corriente.aggregate(total=Sum('entrega_cta'))['total'] or 0
    total_cta_corriente_cobrado = total_cuotas + total_entregas

    # 💵 Total en caja (sin cuenta corriente)
    total_en_caja = 0
    for item in totales_por_metodo_nombre:
        nombre_metodo = item['metodo_pago__tarjeta_nombre']
        if nombre_metodo and nombre_metodo.lower() == 'cuenta corriente':
            continue
        total_en_caja += item['total'] or 0
    total_en_caja_con_credito = total_en_caja + total_cta_corriente_cobrado

    # Pendiente en cta cte (si tu modelo CuentaCorriente tiene total_con_interes)
    pendiente_qs = CuentaCorriente.objects.filter(
        factura__metodo_pago__tarjeta_nombre__iexact="cuenta corriente"
    ).annotate(
        pendiente=ExpressionWrapper(
            F('total_con_interes') - F('imp_cuota_pagadas') - F('entrega_cta'),
            output_field=DecimalField(max_digits=10, decimal_places=2)
        )
    )
    pendiente_cta_corriente = pendiente_qs.aggregate(total=Sum('pendiente'))['total'] or 0

    # 🧮 Agrupación real de pagos desde CuentaCorriente (no usado en la tabla unificada, se mantiene por si lo mostrás)
    pagos_agrupados = (
        CuentaCorriente.objects
        .annotate(
            metodo=Case(
                When(metodo_pago__tarjeta_nombre__isnull=False, then=Trim(Lower('metodo_pago__tarjeta_nombre'))),
                default=Value('cuenta corriente'),
                output_field=CharField()
            )
        )
        .values('metodo')
        .annotate(total=Sum('imp_cuota_pagadas') + Sum('entrega_cta'))
        .order_by('metodo')
    )

    facturado_cta_corriente = 0

    # Datos adicionales
    metodos_pago = MetodoPago.objects.all()
    vendedores = Factura.objects.values_list('vendedor', flat=True).distinct().order_by('vendedor')

    # 🧮 Total Caja SIN contar nada facturado en Cuenta Corriente (aunque no esté cobrado)
    total_facturado_cta_cte = next(
        (item['total'] for item in totales_por_metodo if item['metodo_normalizado'] == 'cuenta corriente'), 0
    )
    total_en_caja_sin_cta_corriente_facturada = total_en_caja - total_facturado_cta_cte

    # Nuevo total: caja real + lo cobrado de cuenta corriente
    total_real_con_credito = total_en_caja_sin_cta_corriente_facturada + total_cta_corriente_cobrado


    # ==== Resumen por método (FACTURADO) ====
    resumen_metodos = (
        facturas
        .annotate(
            metodo_nombre=Case(
                When(metodo_pago__tarjeta_nombre__isnull=False, then=Trim('metodo_pago__tarjeta_nombre')),
                When(metodo_pago_manual__isnull=False, then=Trim('metodo_pago_manual')),
                default=Value('Sin especificar'),
                output_field=CharField(),
            )
        )
        .values('metodo_nombre')
        .annotate(total=Sum('total_con_interes'))
        .order_by('metodo_nombre')
    )

    # ==== Cuenta Corriente COBRADO (pagos registrados en CuentaCorriente) ====
    cobro_cta_corriente = pagos_cta_corriente.aggregate(
        total=Sum('imp_cuota_pagadas') + Sum('entrega_cta')
    )['total'] or 0


    # ---------------------------------------------------------------------
    # 👇 NUEVO: Unificar facturas + pagos en "movimientos" y ordenar por fecha
    movimientos = []

    # Facturas -> movimientos
    for f in facturas:
        movimientos.append({
            'tipo': 'factura',
            'fecha': f.fecha,  # DateField
            'numero': f.numero_factura,
            'dni': f.dni_cliente,
            'cliente': f"{f.nombre_cliente} {f.apellido_cliente}".strip(),
            'vendedor': f.vendedor,
            'metodo': (
                f.metodo_pago.tarjeta_nombre if getattr(f, 'metodo_pago', None)
                else (f.metodo_pago_manual or 'Sin especificar')
            ),
            'estado_credito': getattr(f, 'estado_credito', ''),

            # 👇 ESTO FALTABA: pasar el valor crudo que está guardado en la BD
            'estado_entrega': f.estado_entrega,                   # 'pendiente' | 'aceptado' | 'rechazado'
            'estado_entrega_label': f.get_estado_entrega_display(),  # opcional

            'tarjeta_numero': getattr(f, 'tarjeta_numero', ''),
            'numero_tiket': getattr(f, 'numero_tiket', ''),
            'total': f.total_con_interes,
            'imagen_url': f.imagen_factura.url if getattr(f, 'imagen_factura', None) else '',
            'id': f.id,
            'factura_id': f.id,   # para links desde la tabla
            'orden': 0,           # para ordenar dentro del mismo día (0=factura, 1=pago). Cambiá si querés pagos primero.
        })


    # Pagos cta cte -> movimientos
    # Pagos cta cte -> movimientos
    for p in pagos_cta_corriente:
        monto_pago = (p.imp_cuota_pagadas or 0) + (p.entrega_cta or 0)
        movimientos.append({
            'tipo': 'pago',
            'fecha': p.fecha_cuota,
            'numero': p.numero_factura,
            'dni': getattr(p.factura, 'dni_cliente', '') if p.factura_id else '',
            'cliente': (
                f"{getattr(p.factura, 'nombre_cliente', '')} {getattr(p.factura, 'apellido_cliente', '')}".strip()
                if p.factura_id else ''
            ),
            'vendedor': getattr(p.factura, 'vendedor', '-') if p.factura_id else '-',
            'metodo': 'Pago Cuenta Corriente',
            'estado_credito': 'Pago',
            'tarjeta_numero': '-',
            'numero_tiket': '-',
            'total': monto_pago,
            'imagen_url': p.imagen_pago.url if getattr(p, 'imagen_pago', None) else '',
            'id': p.id,
            'factura_id': p.factura_id,
            'descripcion': getattr(p, 'descripcion', ''),
            'orden': 1,
        })




    # Ordenar por fecha desc y, dentro del mismo día, por 'orden'
    # (reverse=True -> fechas más nuevas primero; y 1 > 0: pagos se muestran antes que facturas si ponés pago=1)
    movimientos.sort(key=lambda x: (x['fecha'], x['orden']), reverse=True)
    # ---------------------------------------------------------------------

    return render(request, 'CarritoApp/lista_cierre_de_caja.html', {
        'facturas': facturas,
        'vendedor': vendedor,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'metodo_pago': metodo_pago,
        'metodos_pago': metodos_pago,
        'vendedores': vendedores,
        'totales_por_vendedor': totales_por_vendedor,
        'totales_por_metodo': totales_por_metodo,
        'total_en_caja': total_en_caja,
        'total_cta_corriente_cobrado': total_cta_corriente_cobrado,
        'total_en_caja_con_credito': total_en_caja_con_credito,
        'pagos_cta_corriente': pagos_cta_corriente,
        'pendiente_cta_corriente': pendiente_cta_corriente,
        'facturado_cta_corriente': facturado_cta_corriente,
        'total_en_caja_sin_cta_corriente_facturada': total_en_caja_sin_cta_corriente_facturada,
        'total_real_con_credito': total_real_con_credito,
        'movimientos': movimientos,  # ✅ CONTEXTO: lo qu
        'resumen_metodos': resumen_metodos,
        'cobro_cta_corriente': cobro_cta_corriente,
    })



#--------------------- apps/CarritoApp/views.py
from django.shortcuts import redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from apps.CarritoApp.models import Factura

@require_POST
def actualizar_estado_entrega(request, factura_id):
    estado = request.POST.get("estado")
    next_url = request.POST.get("next") or request.META.get("HTTP_REFERER") or "/"

    # Validar valores esperados
    validos = {"pendiente", "aceptado", "rechazado"}
    if estado not in validos:
        messages.error(request, "Estado inválido.")
        return redirect(next_url)

    factura = get_object_or_404(Factura, pk=factura_id)
    factura.estado_entrega = estado
    factura.save(update_fields=["estado_entrega"])

    messages.success(request, "Estado de entrega actualizado.")
    return redirect(next_url)









#---------LISTA VENDEDOR-- (es del listado para vendedores )------------------------
from django.shortcuts import render
from django.db.models import Sum, Value
from django.db.models.functions import Lower, Trim
from django.db.models import Case, When, CharField
from apps.CarritoApp.models import Factura, MetodoPago, CuentaCorriente
from django.db.models.functions import Trim, Lower
from django.db.models import F, ExpressionWrapper, DecimalField, Value
from django.db.models.functions import Lower, Trim
from django.db.models import Case, When, CharField
from django.db.models import Q


def lista_vendedor(request):
    facturas = Factura.objects.all().order_by('-fecha', '-numero_factura')

    # Filtros
    vendedor = request.GET.get('vendedor', '')
    fecha_desde = request.GET.get('fecha_desde', '')
    fecha_hasta = request.GET.get('fecha_hasta', '')
    metodo_pago = request.GET.get('metodo_pago', '')

    if vendedor:
        facturas = facturas.filter(vendedor__icontains=vendedor)
    if fecha_desde:
        facturas = facturas.filter(fecha__gte=fecha_desde)
    if fecha_hasta:
        facturas = facturas.filter(fecha__lte=fecha_hasta)
    if metodo_pago:
        metodo_obj = MetodoPago.objects.filter(tarjeta_nombre=metodo_pago).first()
        if metodo_obj:
            facturas = facturas.filter(metodo_pago=metodo_obj)

    # Agrupación por vendedor
    totales_por_vendedor = (
        facturas
        .annotate(vendedor_normalizado=Trim(Lower('vendedor')))
        .values('vendedor_normalizado')
        .annotate(total=Sum('total_con_interes'))
        .order_by('vendedor_normalizado')
    )

    # Agrupación por método de pago (para visualización)
    totales_por_metodo = (
        facturas
        .annotate(
            metodo_normalizado=Case(
                When(metodo_pago__tarjeta_nombre__isnull=False, then=Trim(Lower('metodo_pago__tarjeta_nombre'))),
                When(metodo_pago_manual__isnull=False, then=Trim(Lower('metodo_pago_manual'))),
                default=Value('sin especificar'),
                output_field=CharField(),
            )
        )
        .values('metodo_normalizado')
        .annotate(total=Sum('total_con_interes'))
        .order_by('metodo_normalizado')
    )

    # Agrupación por método de pago (por nombre)
    totales_por_metodo_nombre = (
        facturas
        .values('metodo_pago__tarjeta_nombre')
        .annotate(total=Sum('total_con_interes'))
        .order_by('metodo_pago__tarjeta_nombre')
    )

    # 💰 Cálculo del total cobrado en cuenta corriente (fuera del modelo Factura)

    pagos_cta_corriente = CuentaCorriente.objects.filter(
        Q(factura__metodo_pago__tarjeta_nombre__iexact="cuenta corriente") |
        Q(factura__metodo_pago_manual__iexact="cuenta corriente")
    ).order_by('-fecha_cuota')
    
    total_cuotas = pagos_cta_corriente.aggregate(total=Sum('imp_cuota_pagadas'))['total'] or 0
    total_entregas = pagos_cta_corriente.aggregate(total=Sum('entrega_cta'))['total'] or 0
    total_cta_corriente_cobrado = total_cuotas + total_entregas

    print("Pagos cuenta corriente encontrados:")
    for p in pagos_cta_corriente:
        print(p.numero_factura, p.imp_cuota_pagadas, p.entrega_cta)

    # 💵 Total en caja (sin cuenta corriente)
    total_en_caja = 0
    for item in totales_por_metodo_nombre:
        nombre_metodo = item['metodo_pago__tarjeta_nombre']
        if nombre_metodo and nombre_metodo.lower() == 'cuenta corriente':
            continue
        total_en_caja += item['total'] or 0
    total_en_caja_con_credito = total_en_caja + total_cta_corriente_cobrado

    # ⚠️ ---------------------------------------------------
    from django.db.models import F, ExpressionWrapper, DecimalField

    pendiente_qs = CuentaCorriente.objects.filter(
        factura__metodo_pago__tarjeta_nombre__iexact="cuenta corriente"
    ).annotate(
        pendiente=ExpressionWrapper(
            F('total_con_interes') - F('imp_cuota_pagadas') - F('entrega_cta'),
            output_field=DecimalField(max_digits=10, decimal_places=2)
        )
    )
    pendiente_cta_corriente = pendiente_qs.aggregate(total=Sum('pendiente'))['total'] or 0
    # ⚠️ ---------------------------------------------------

    # 🧮 Agrupación real de pagos desde CuentaCorriente
    
    pagos_agrupados = (
        CuentaCorriente.objects
        .annotate(
            metodo=Case(
                When(metodo_pago__tarjeta_nombre__isnull=False, then=Trim(Lower('metodo_pago__tarjeta_nombre'))),
                default=Value('cuenta corriente'),
                output_field=CharField()
            )
        )
        .values('metodo')
        .annotate(
            total=Sum('imp_cuota_pagadas') + Sum('entrega_cta')
        )
        .order_by('metodo')
    )

    # ⚠️ Para evitar el error por variable faltante (aunque ya no se usa)
    facturado_cta_corriente = 0

    # Datos adicionales
    metodos_pago = MetodoPago.objects.all()
    vendedores = Factura.objects.values_list('vendedor', flat=True).distinct().order_by('vendedor')

    # 🧮 Total Caja SIN contar nada facturado en Cuenta Corriente (aunque no esté cobrado)
    total_facturado_cta_cte = next(
        (item['total'] for item in totales_por_metodo if item['metodo_normalizado'] == 'cuenta corriente'), 0
    )
    total_en_caja_sin_cta_corriente_facturada = total_en_caja - total_facturado_cta_cte

    # Nuevo total: caja real + lo cobrado de cuenta corriente
    total_real_con_credito = total_en_caja_sin_cta_corriente_facturada + total_cta_corriente_cobrado

    return render(request, 'CarritoApp/lista_vendedor.html', {
        'facturas': facturas,
        'vendedor': vendedor,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'metodo_pago': metodo_pago,
        'metodos_pago': metodos_pago,
        'vendedores': vendedores,
        'totales_por_vendedor': totales_por_vendedor,
        'totales_por_metodo': totales_por_metodo,
        'total_en_caja': total_en_caja,
        'total_cta_corriente_cobrado': total_cta_corriente_cobrado,
        'total_en_caja_con_credito': total_en_caja_con_credito,
        'pagos_cta_corriente': pagos_cta_corriente,
        'pendiente_cta_corriente': pendiente_cta_corriente,
        'facturado_cta_corriente': facturado_cta_corriente,
        'total_en_caja_sin_cta_corriente_facturada': total_en_caja_sin_cta_corriente_facturada,  # ✅ ESTA LÍNEA
        'total_real_con_credito': total_real_con_credito,
    })


#---------------------------DETALLE factura------------------------------------#

from django.shortcuts import render, get_object_or_404
from .models import Factura
import json

def detalle_factura(request, factura_id):
    # Obtener la factura
    factura = get_object_or_404(Factura, id=factura_id)

    # Decodificar el JSON de detalle_productos
    try:
        detalle_productos = json.loads(factura.detalle_productos)
    except json.JSONDecodeError:
        detalle_productos = []

    # Renderizar la plantilla
    return render(request, 'detalle_factura.html', {
        'factura': factura,
        'detalle_productos': detalle_productos,
        'pdf_url': request.build_absolute_uri(f"/CarritoApp/factura/{factura.id}/pdf/")
    })
#---------------------------GENERAR PDF FACTURA web------------------------------------#
import os
import json
from reportlab.pdfgen import canvas
from django.conf import settings
from django.http import HttpResponse
from .models import Factura

def generar_pdf_factura(request, factura_id):
    factura = Factura.objects.get(id=factura_id)

    try:
        productos = json.loads(factura.detalle_productos)
    except json.JSONDecodeError:
        productos = []

    # Definir ruta de guardado
    nombre_archivo = f"factura_{factura.id}.pdf"
    ruta_carpeta = os.path.join(settings.MEDIA_ROOT, 'facturas')
    os.makedirs(ruta_carpeta, exist_ok=True)
    ruta_pdf = os.path.join(ruta_carpeta, nombre_archivo)

    # Crear PDF en disco
    pdf = canvas.Canvas(ruta_pdf)
    y_position = 800

    text_object = pdf.beginText()
    text_object.setTextOrigin(100, y_position)
    text_object.setFont("Helvetica-Bold", 16)
    text_object.textOut("Factura ")
    text_object.setFont("Helvetica", 12)
    text_object.textOut(f"N°: {factura.numero_factura}")
    pdf.drawText(text_object)

    y_position -= 25
    pdf.drawString(100, y_position, f"Fecha: {factura.fecha}")
    y_position -= 20
    pdf.drawString(100, y_position, f"Cliente: {factura.nombre_cliente} {factura.apellido_cliente}")
    y_position -= 20
    pdf.drawString(100, y_position, f"Vendedor gener: {factura.vendedor}")
    y_position -= 20
    pdf.drawString(100, y_position, f"Método de Pago: {factura.metodo_pago}")
    y_position -= 20

    text_object = pdf.beginText()
    text_object.setTextOrigin(100, y_position)
    text_object.setFont("Helvetica-Bold", 16)
    text_object.textOut("Total: ")
    text_object.setFont("Helvetica", 12)
    text_object.textOut(f"${factura.total:.2f}")
    pdf.drawText(text_object)

    y_position -= 30
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(100, y_position, "Productos Comprados:")
    y_position -= 20
    pdf.line(100, y_position, 500, y_position)
    y_position -= 20

    pdf.drawString(100, y_position, "Producto")
    pdf.drawString(250, y_position, "Cantidad")
    pdf.drawString(350, y_position, "Precio Unitario")
    pdf.drawString(450, y_position, "Subtotal")
    y_position -= 20
    pdf.line(100, y_position, 500, y_position)
    y_position -= 20

    for producto in productos:
        pdf.drawString(100, y_position, producto.get("nombre_producto", "N/A"))
        pdf.drawString(250, y_position, str(producto.get("cantidad_vendida", 0)))
        pdf.drawString(350, y_position, f"${producto.get('precio_unitario', 0.00):.2f}")
        pdf.drawString(450, y_position, f"${producto.get('subtotal', 0.00):.2f}")
        y_position -= 20
        if y_position < 100:
            pdf.showPage()
            y_position = 800

    pdf.showPage()
    pdf.save()

    # También devolverlo por navegador (opcional)
    with open(ruta_pdf, 'rb') as archivo_pdf:
        response = HttpResponse(archivo_pdf.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{nombre_archivo}"'
        return response

#---------------------------FACTURAS USUARIO------------------------------------#

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Factura

@login_required
def facturas_usuario(request):
    # Obtener solo las facturas asociadas al usuario autenticado
    usuario = request.user
    facturas = Factura.objects.filter(
        nombre_cliente=usuario.first_name,
        apellido_cliente=usuario.last_name
    ).order_by('-numero_factura') 

    return render(request, 'facturas_usuario.html', {'facturas': facturas})


#-------------------subir una imagen factura---------------------------------------------#
from django import forms
from django.contrib import messages
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
import base64
from .models import Factura
from django.urls import reverse          # << necesario para fallback
from django.contrib import messages       # << necesario para messages
from django.core.files.base import ContentFile



# ---------- Formulario ----------
class SubirImagenFacturaForm(forms.ModelForm):
    class Meta:
        model = Factura
        fields = ['imagen_factura']


# ---------- Vista ----------
from django.urls import reverse          # << necesario para fallback
from django.contrib import messages       # << necesario para messages
from django.core.files.base import ContentFile

def subir_imagen_factura(request, factura_id):
    factura = get_object_or_404(Factura, id=factura_id)

    # A dónde volver: ?next=... o listado por defecto
    fallback = reverse('CarritoApp:listar_facturas')
    next_url = request.GET.get('next') or request.POST.get('next') or fallback

    if request.method == 'POST':
        # 1) Imagen capturada (base64 desde cámara)
        captured_image_data = request.POST.get('captured_image')
        if captured_image_data:
            try:
                # Espera algo como: data:image/png;base64,AAAA...
                format_part, img_b64 = captured_image_data.split(';base64,', 1)
                ext = (format_part.split('/')[-1] or 'png').lower()

                image_data = ContentFile(
                    base64.b64decode(img_b64),
                    name=f"factura_{factura.numero_factura}.{ext}"
                )

                # Borrar anterior si existía
                if factura.imagen_factura:
                    factura.imagen_factura.delete(save=False)

                factura.imagen_factura = image_data
                factura.save(update_fields=['imagen_factura'])
                messages.success(request, 'Imagen de factura subida correctamente.')
            except Exception as e:
                messages.error(request, f'No se pudo procesar la imagen capturada: {e}')
            return redirect(next_url)

        # 2) Imagen subida como archivo (PC) - directo desde request.FILES
        uploaded = request.FILES.get('imagen_factura')
        if uploaded:
            # si había una imagen previa, borrarla
            if factura.imagen_factura:
                factura.imagen_factura.delete(save=False)

            # asignar y guardar
            factura.imagen_factura = uploaded
            factura.save(update_fields=['imagen_factura'])
            messages.success(request, 'Imagen de factura actualizada correctamente.')
            return redirect(next_url)
        else:
            messages.warning(request, 'No seleccionaste ningún archivo.')
            return render(
                request,
                'subir_imagen_factura.html',
                {'form': SubirImagenFacturaForm(instance=factura), 'factura': factura, 'next': next_url},
            )

    # GET: mostrar formulario
    form = SubirImagenFacturaForm(instance=factura)
    return render(
        request,
        'subir_imagen_factura.html',
        {'form': form, 'factura': factura, 'next': next_url},
    )

#----------------------------------------------------------------#
# apps/CarritoApp/views.py
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.contrib import messages
from .models import CuentaCorriente
from .forms import SubirImagenPagoForm

def subir_imagen_pago(request, pago_id):
    pago = get_object_or_404(CuentaCorriente, pk=pago_id)
    next_url = request.GET.get('next') or request.POST.get('next') or reverse('CarritoApp:listar_facturas')

    if request.method == 'POST':
        form = SubirImagenPagoForm(request.POST, request.FILES, instance=pago)
        if form.is_valid():
            form.save()
            messages.success(request, 'Comprobante guardado en el pago.')
            return redirect(next_url)
    else:
        form = SubirImagenPagoForm(instance=pago)

    return render(request, 'CarritoApp/subir_imagen_pago.html', {
        'form': form, 'pago': pago, 'next': next_url
    })


def eliminar_imagen_pago(request, pago_id):
    pago = get_object_or_404(CuentaCorriente, pk=pago_id)
    next_url = request.GET.get('next') or reverse('CarritoApp:listar_facturas')
    if pago.imagen_pago:
        pago.imagen_pago.delete(save=True)
        messages.success(request, 'Comprobante eliminado del pago.')
    return redirect(next_url)



#----------------------------Eliminar Imagen Factura------------------------------------#

from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages

from .models import Factura

def eliminar_imagen_factura(request, factura_id):
    factura = get_object_or_404(Factura, id=factura_id)

    # a dónde volver: ?next=... o al listado por defecto
    fallback = reverse('CarritoApp:lista_vendedor')
    next_url = request.GET.get('next') or fallback

    if factura.imagen_factura:
        # borra el archivo y limpia el campo
        factura.imagen_factura.delete(save=False)
        factura.imagen_factura = None
        factura.save(update_fields=['imagen_factura'])
        messages.success(request, 'Imagen de factura eliminada.')
    else:
        messages.info(request, 'La factura no tenía imagen cargada.')

    return redirect(next_url)






#---------------------------------levantar_imagen_usuario------------------------------------#

# CarritoApp/views.py
import base64
from django.contrib import messages
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404, render, redirect

from .models import Factura

def levantar_imagen_usuario(request, pk):
    factura = get_object_or_404(Factura, pk=pk)

    if request.method == 'POST':
        # --- 1) Cámara (base64) ---
        captured = request.POST.get('captured_image')
        if captured:
            try:
                if ';base64,' not in captured:
                    raise ValueError('Formato base64 inválido.')
                fmt, b64 = captured.split(';base64,', 1)
                ext = (fmt.split('/')[-1] or 'jpg').lower()
                if ext == 'jpeg':
                    ext = 'jpg'

                image_file = ContentFile(
                    base64.b64decode(b64),
                    name=f"factura_{factura.numero_factura}.{ext}"
                )
                if factura.imagen_factura:
                    factura.imagen_factura.delete(save=False)
                factura.imagen_factura = image_file
                factura.save(update_fields=['imagen_factura'])
                messages.success(request, 'Imagen guardada desde cámara.')
                return redirect('CarritoApp:facturas_usuario')
            except Exception as e:
                messages.error(request, f'No se pudo procesar la imagen capturada: {e}')
                # cae a render con error visible

        # --- 2) Archivo (input file) ---
        if 'imagen_factura' not in request.FILES:
            messages.warning(request, 'No llegó ningún archivo. Verificá que el formulario tenga enctype="multipart/form-data" y seleccionaste un archivo.')
            return render(request, 'levantar_imagen_usuario.html', {'factura': factura})

        uploaded = request.FILES['imagen_factura']
        if not uploaded or not getattr(uploaded, 'name', ''):
            messages.warning(request, 'No seleccionaste un archivo válido.')
            return render(request, 'levantar_imagen_usuario.html', {'factura': factura})

        # Reemplaza si había una previa
        if factura.imagen_factura:
            factura.imagen_factura.delete(save=False)

        factura.imagen_factura = uploaded
        factura.save(update_fields=['imagen_factura'])
        messages.success(request, 'Imagen guardada desde archivo.')
        return redirect('CarritoApp:facturas_usuario')

    # GET
    return render(request, 'levantar_imagen_usuario.html', {'factura': factura})




#---------------------------------ACTUALIZAR PRECIO DE PRODUTO------------------------------#
from decimal import Decimal
from django.shortcuts import render, redirect
from .models import Producto, Categ_producto
from django.contrib import messages

def actualizar_precios(request):
    if request.method == "POST":
        categoria_id = request.POST.get("categoria")
        porcentaje = Decimal(request.POST.get("porcentaje"))  # Convertir a Decimal

        if categoria_id:
            # Actualizar precios de una categoría específica
            productos = Producto.objects.filter(categoria_id=categoria_id)
        else:
            # Actualizar precios de todos los productos
            productos = Producto.objects.all()

        # Aplicar el cambio de precio
        for producto in productos:
            nuevo_precio = producto.precio * (1 + porcentaje / Decimal(100))
            producto.precio = round(nuevo_precio, 2)  # Redondear a 2 decimales
            producto.save()

        messages.success(request, "Precios actualizados correctamente.")
        return redirect("CarritoApp:agregar_producto")

    return redirect("CarritoApp:agregar_producto")


#---------------------ver carrito-------------------#
from datetime import date
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Factura, TipoPago

def ver_carrito(request):
    if not request.user.is_authenticated:
        messages.error(request, "Debes iniciar sesión o registrarte para agregar productos al carrito.")
        return redirect('tienda')

    carrito = request.session.get('carrito', {})
    total_carrito = 0

    for key, value in carrito.items():
        value['importe'] = value['precio'] * value['cantidad']
        total_carrito += value['importe']

    ultima_factura = Factura.objects.last()
    if ultima_factura and ultima_factura.numero_factura.isdigit():
        numero_factura = str(int(ultima_factura.numero_factura) + 1).zfill(5)
    else:
        numero_factura = "00001"

    fecha_actual = date.today()

    if request.user.is_authenticated:
        nombre_usuario = request.user.first_name
        apellido_usuario = request.user.last_name
        usuario_no_registrado = False
    else:
        nombre_usuario = "Desconocido"
        apellido_usuario = "Usuario"
        usuario_no_registrado = True

    # ✅ Traer los métodos de pago desde la base
    tipos_pago = TipoPago.objects.all()

    return render(request, 'carrito.html', {
        'carrito': carrito,
        'total_carrito': total_carrito,
        'numero_factura': numero_factura,
        'fecha': fecha_actual,
        'nombre_usuario': nombre_usuario,
        'apellido_usuario': apellido_usuario,
        'usuario_no_registrado': usuario_no_registrado,
        'tipos_pago': tipos_pago,  # ← lo pasás a la plantilla
    })


#---------------------- REPAGINAR-------------------------------------------

from django.core.paginator import Paginator

def vista_productos(request):
    productos = Producto.objects.all()  # Obtén los productos
    paginator = Paginator(productos, 6)  # 6 productos por página (3 columnas x 2 filas)
    page_number = request.GET.get('page')  # Obtiene el número de página de la solicitud
    page_obj = paginator.get_page(page_number)  # Obtén los productos de la página actual
    return render(request, 'tu_plantilla.html', {'page_obj': page_obj})

#---------------------- BALANCE TOTAL-------------------------------------------

from django.shortcuts import render
from django.db.models import Sum
from .models import Producto, Compra, Factura
import json  # Para manejar JSON
from django.shortcuts import render
from django.db.models import Sum
from .models import Producto, Compra, Factura
import json  # Para manejar JSON

from django.shortcuts import render
from django.db.models import Sum, Max
from .models import Producto, Compra, Factura
import json  # Para manejar JSON

def balance_total(request):
    # Obtener los parámetros de fecha
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')

    # Filtrar productos por rango de fechas si ambos parámetros están presentes
    productos = Producto.objects.all()
    if fecha_desde and fecha_hasta:
        productos = productos.filter(fecha_creacion__range=[fecha_desde, fecha_hasta])

    # Crear diccionarios para cálculos
    cantidades_por_producto = Compra.objects.values('producto_id').annotate(total_comprado=Sum('cantidad'))
    cantidades_por_producto = {item['producto_id']: item['total_comprado'] for item in cantidades_por_producto}

    cantidades_vendidas_por_producto = {}
    facturas = Factura.objects.all()
    for factura in facturas:
        try:
            detalle_productos = json.loads(factura.detalle_productos)
            for detalle in detalle_productos:
                producto = Producto.objects.filter(nombre_producto=detalle.get('nombre_producto')).first()
                if producto:
                    cantidad_vendida = detalle.get('cantidad_vendida', 0)
                    producto_id = producto.id
                    cantidades_vendidas_por_producto[producto_id] = (
                        cantidades_vendidas_por_producto.get(producto_id, 0) + cantidad_vendida
                    )
        except json.JSONDecodeError:
            print(f"Error al decodificar JSON en la factura {factura.numero_factura}")

    # Obtener el precio_compra de la última compra de cada producto
    costos_por_producto = {}
    compras = Compra.objects.values('producto_id').annotate(ultima_fecha=Max('fecha_compra'))
    for compra in compras:
        ultima_compra = Compra.objects.filter(
            producto_id=compra['producto_id'], fecha_compra=compra['ultima_fecha']
        ).first()
        if ultima_compra:
            costos_por_producto[compra['producto_id']] = ultima_compra.precio_compra

    precios_venta_por_producto = {producto.id: producto.precio for producto in productos}

    ganancias_por_producto = {
        producto_id: precios_venta_por_producto.get(producto_id, 0) - costos_por_producto.get(producto_id, 0)
        for producto_id in precios_venta_por_producto
    }

    total_caja_por_producto = {
        producto_id: ganancias_por_producto.get(producto_id, 0) * cantidades_vendidas_por_producto.get(producto_id, 0)
        for producto_id in ganancias_por_producto
    }

    # Calcular el total general de la caja
    total_caja = sum(total_caja_por_producto.values())

    # Calcular el total del stock
    total_stock = productos.aggregate(total_stock=Sum('stock'))['total_stock'] or 0

    return render(request, 'CarritoApp/balance_total.html', {
        'productos': productos,
        'total_stock': total_stock,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'cantidades_por_producto': cantidades_por_producto,
        'cantidades_vendidas_por_producto': cantidades_vendidas_por_producto,
        'costos_por_producto': costos_por_producto,
        'precios_venta_por_producto': precios_venta_por_producto,
        'ganancias_por_producto': ganancias_por_producto,
        'total_caja_por_producto': total_caja_por_producto,
        'total_caja': total_caja,  # Pasar el total general
    })




#-----------------------------------------------------#
from django.shortcuts import render
from django.db.models import Sum
from .models import Compra
from .models import Producto, Compra

def balance_ganancia(request):
    # Obtener todos los productos con su precio_compra desde la tabla Compra
    productos_con_precios = Compra.objects.values(
        'producto__nombre_producto'
    ).annotate(precio_compra=Sum('precio_compra'))

    return render(request, 'CarritoApp/balance_ganancia.html', {
        'productos_con_precios': productos_con_precios,
    })

#-------------------Modificar Stock------------------------------------#
from django.shortcuts import render, get_object_or_404, redirect
from .models import Producto

# Vista para modificar el stock de un producto específico
def modificar_stock(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        nuevo_stock = request.POST.get('stock')  # Obtener el valor del formulario
        if nuevo_stock and nuevo_stock.isdigit():
            producto.stock = int(nuevo_stock)  # Actualizar el stock
            producto.save()
            return redirect('CarritoApp:modificacion_stock')  # Redirigir después de guardar
        else:
            error = "El stock debe ser un número válido."
            return render(request, 'CarritoApp/modificar_stock.html', {'producto': producto, 'error': error})
    return render(request, 'CarritoApp/modificar_stock.html', {'producto': producto})

#--------------Moificacion Stock---------------------------------------#
from django.shortcuts import render
from .models import Producto

def modificacion_stock(request):
    productos = Producto.objects.all()
    return render(request, 'CarritoApp/modificacion_stock.html', {'productos': productos})


#--------------movimiento_cliente---------------------------------------#
def movimiento_cliente(request):
    facturas = Factura.objects.all().order_by('-fecha', '-numero_factura')
    apellido_cliente = request.GET.get('apellido_cliente', '')
    fecha_desde = request.GET.get('fecha_desde', '')
    fecha_hasta = request.GET.get('fecha_hasta', '')

    if apellido_cliente:
        facturas = facturas.filter(apellido_cliente__icontains=apellido_cliente)

    if fecha_desde:
        facturas = facturas.filter(fecha__gte=fecha_desde)

    if fecha_hasta:
        facturas = facturas.filter(fecha__lte=fecha_hasta)

    return render(request, 'CarritoApp/movimiento_cliente.html', {'facturas': facturas})



#-------------------productos_vendidos------------------------------------#
from django.shortcuts import render
from .models import Factura
import json

def productos_vendidos(request):
    productos_vendidos = []
    total_cantidad_vendida = 0
    total_precio_unitario = 0
    total_precio = 0

    # Filtros
    nombre_producto = request.GET.get('nombre_producto', '')
    fecha_desde = request.GET.get('fecha_desde', None)
    fecha_hasta = request.GET.get('fecha_hasta', None)

    facturas = Factura.objects.all()

    # Aplicar filtros
    if fecha_desde:
        facturas = facturas.filter(fecha__gte=fecha_desde)
    if fecha_hasta:
        facturas = facturas.filter(fecha__lte=fecha_hasta)

    for factura in facturas:
        try:
            detalle_productos = json.loads(factura.detalle_productos)
            for detalle in detalle_productos:
                nombre = detalle.get('nombre_producto', '')
                cantidad_vendida = detalle.get('cantidad_vendida', 0)
                precio_unitario = detalle.get('precio_unitario', 0)

                if nombre_producto.lower() in nombre.lower():
                    total = cantidad_vendida * precio_unitario
                    total_cantidad_vendida += cantidad_vendida
                    total_precio_unitario += precio_unitario
                    total_precio += total

                    productos_vendidos.append({
                        'fecha': factura.fecha,
                        'nombre_producto': nombre,
                        'cantidad_vendida': cantidad_vendida,
                        'precio_unitario': precio_unitario,
                        'total': total,
                    })
        except json.JSONDecodeError:
            print(f"Error al decodificar JSON en la factura {factura.numero_factura}")

    productos_vendidos.sort(key=lambda x: x['fecha'], reverse=True)

    return render(request, 'CarritoApp/productos_vendidos.html', {
        'productos_vendidos': productos_vendidos,
        'filtro_nombre_producto': nombre_producto,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'total_cantidad_vendida': total_cantidad_vendida,
        'total_precio_unitario': total_precio_unitario,
        'total_precio': total_precio,
    })


#-----------------------------------------------------------------------------
from django.http import JsonResponse
from apps.CarritoApp.models import Producto  # Asegúrate de importar el modelo correcto

def obtener_stock(request):
    numero_producto = request.GET.get('numero_producto', None)
    
    if numero_producto:
        try:
            # Buscar el producto en la base de datos
            producto = Producto.objects.get(numero_producto=numero_producto)
            return JsonResponse({'stock': producto.stock})  # Devolver el stock
        except Producto.DoesNotExist:
            return JsonResponse({'stock': 0})  # Si no existe, stock = 0

    return JsonResponse({'error': 'Número de producto no proporcionado'}, status=400)



#-------------------MOSTRAR CARRITO FACTURA------------------------------------#

import json
from django.shortcuts import render
from .models import Factura

def mostrar_carrito_factura(request, factura_id):
    try:
        factura = Factura.objects.get(id=factura_id)
        
        # 🔹 Deserializar detalle_productos (convertir JSON a lista de diccionarios)
        detalle_productos = json.loads(factura.detalle_productos)

        return render(request, 'CarritoApp/mostrar_carrito_factura.html', {
            'factura': factura,
            'detalle_productos': detalle_productos,  # Ahora es una lista de productos correcta
        })
    except Factura.DoesNotExist:
        return render(request, 'CarritoApp/error_factura.html', {"error": "La factura no existe."})





#-------------------Imprimir Caja------------------------------------#

from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from apps.CarritoApp.models import Factura, CuentaCorriente
from django.db.models import Sum
from datetime import datetime

def imprimir_caja(request):
    dni_cliente = request.GET.get('dni_cliente', '').strip()
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    metodo_pago = request.GET.get('metodo_pago', '').strip()

    facturas = Factura.objects.all()

    if dni_cliente:
        facturas = facturas.filter(dni_cliente=dni_cliente)

    if fecha_desde and fecha_hasta:
        try:
            fecha_inicio = datetime.strptime(fecha_desde, "%Y-%m-%d")
            fecha_fin = datetime.strptime(fecha_hasta, "%Y-%m-%d")
            facturas = facturas.filter(fecha__range=[fecha_inicio, fecha_fin])
        except ValueError:
            pass

    if metodo_pago:
        facturas = facturas.filter(metodo_pago=metodo_pago)

    facturas = facturas.order_by('-fecha')  # ✅ Acá aplicás el orden solo una vez

    pagos_cta_corriente = CuentaCorriente.objects.filter(factura__in=facturas)


    # 🔄 Solo mostrar pagos de las facturas filtradas
    pagos_cta_corriente = pagos_cta_corriente.filter(factura__in=facturas)

    # Totales
    total_con_interes = facturas.aggregate(Sum('total_con_interes'))['total_con_interes__sum'] or 0


    totales_por_vendedor = (
        facturas.values('vendedor')
        .annotate(total=Sum('total_con_interes'))
        .order_by('vendedor')
    )

    totales_por_metodo = (
        facturas.values('metodo_pago')
        .annotate(total=Sum('total_con_interes'))
        .order_by('metodo_pago')
    )
    total_en_caja = sum(item['total'] for item in totales_por_metodo if item['metodo_pago'] != 'Cuenta Corriente')

    total_cta_corriente_cobrado = pagos_cta_corriente.aggregate(
        total=Sum('imp_cuota_pagadas') + Sum('entrega_cta')
    )['total'] or 0

    total_general = total_en_caja + total_cta_corriente_cobrado

    # Generar PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="resumen_caja.pdf"'
    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    y = height - 40
    p.setFont("Helvetica-Bold", 16)
    p.drawString(180, y, "Resumen de Caja")
    y -= 30

    p.setFont("Helvetica", 10)
    p.drawString(50, y, f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    y -= 30

    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, "Totales por Vendedor")
    y -= 20
    p.setFont("Helvetica", 10)
    for item in totales_por_vendedor:
        p.drawString(60, y, f"{item['vendedor']}: ${item['total']:.2f}")
        y -= 15

    y -= 10
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, "Totales por Método de Pago")
    y -= 20
    p.setFont("Helvetica", 10)
    for item in totales_por_metodo:
        nota = " (No en caja)" if item['metodo_pago'] == "Cuenta Corriente" else ""
        p.drawString(60, y, f"{item['metodo_pago']}: ${item['total']:.2f}{nota}")
        y -= 15

    y -= 20
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, f"Cuenta Corriente Cobrado: ${total_cta_corriente_cobrado:.2f}")
    y -= 20
    p.drawString(50, y, f"Total en Caja: ${total_en_caja:.2f}")
    y -= 20
    p.setFillColorRGB(0, 0.4, 0)
    p.drawString(50, y, f"Total General Cobrado: ${total_general:.2f}")

    p.showPage()
    p.save()
    return response


# ------------------Totales factura para el CELULAR PDF------------------------------------------
# ------------------Totales factura para el CELULAR PDF------------------------------------------
# ------------------Totales factura para el CELULAR PDF------------------------------------------

import os
import json
from reportlab.pdfgen import canvas
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from .models import Factura

def vista_resumen_factura(request, factura_id):
    factura = get_object_or_404(Factura, id=factura_id)

    # Crear carpeta si no existe
    ruta_carpeta = os.path.join(settings.MEDIA_ROOT, 'facturas')
    os.makedirs(ruta_carpeta, exist_ok=True)

    # Nombre y ruta del archivo PDF
    nombre_pdf = f"factura_{factura.id}.pdf"
    ruta_pdf = os.path.join(ruta_carpeta, nombre_pdf)

    # Intentar decodificar productos
    try:
        productos = json.loads(factura.detalle_productos)
    except json.JSONDecodeError:
        productos = []

    # Generar PDF solo si no existe
    if True:
        pdf = canvas.Canvas(ruta_pdf)
        y = 800
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(100, y, f"FACTURA N°: {factura.numero_factura}")
        y -= 20
        pdf.setFont("Helvetica", 12)
        pdf.drawString(100, y, f"Fecha: {factura.fecha}")
        y -= 20
        pdf.drawString(100, y, f"Cliente: {factura.nombre_cliente} {factura.apellido_cliente}")
        y -= 20
        pdf.drawString(100, y, f"CUIL: {factura.cuil}")
        y -= 20
        pdf.drawString(100, y, f"Vendedor: {factura.vendedor}")
        y -= 20
        pdf.drawString(100, y, f"Método de Pago: {factura.metodo_pago}")
        y -= 20
        pdf.drawString(100, y,  f"Nº Ticket: {factura.numero_tiket or '-'}")
        y -= 20
        pdf.drawString(100, y,  f"Nº Tarjeta : {factura.tarjeta_numero or '-'}")
        y -= 30
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(100, y, "Productos:")
        y -= 20
        pdf.setFont("Helvetica", 10)

        for producto in productos:
            pdf.drawString(110, y, f"{producto.get('nombre_producto')} x {producto.get('cantidad_vendida')} - ${producto.get('subtotal')}")
            y -= 20
            if y < 100:
                pdf.showPage()
                y = 800

        y -= 10
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(100, y, f"Total: ${factura.total}")
        pdf.save()

    # URL pública para el PDF
    pdf_url = f"http://146.190.66.18/media/facturas/{nombre_pdf}"

    return render(request, 'detalle_factura.html', {
        'factura': factura,
        'detalle_productos': productos,
        'pdf_url': pdf_url,
    })


#-------------------------------------------------------------------------------
#---------------------Guardar factura mercadopago  Carrito--------------------------#
# ---------------------- IMPORTS NECESARIOS ----------------------
import json
import mercadopago
from django.conf import settings
from django.shortcuts import render, redirect
from .models import Producto

def guardar_factura(request):
    if request.method == 'POST':
        metodo_pago = request.POST.get('metodo_pago', '')

        if metodo_pago != "Mercado Pago":
            return redirect("CarritoApp:tienda")

        carrito = request.session.get('carrito', {})
        total = 0
        detalle_productos = []

        for key, value in carrito.items():
            try:
                producto = Producto.objects.get(id=value['producto_id'])
                cantidad = value['cantidad']
                subtotal = float(producto.precio) * cantidad
                total += subtotal
                detalle_productos.append({
                    "nombre_producto": producto.nombre_producto,
                    "cantidad_vendida": cantidad,
                    "precio_unitario": float(producto.precio),
                    "subtotal": subtotal,
                })
            except Producto.DoesNotExist:
                continue

        if total <= 0:
            return render(request, "CarritoApp/error_mercadopago.html", {
                "error": "El total de la compra debe ser mayor a 0."
            })

        # Guardar datos temporales en sesión
        request.session['factura_datos'] = {
            "metodo_pago": metodo_pago,
            "total": total,
            "detalle": detalle_productos
        }

        sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)

        success_url = "https://146.190.66.18/CarritoApp/pago/exito/"
        failure_url = "https://146.190.66.18/CarritoApp/pago/fallo/"
        pending_url = "https://146.190.66.18/CarritoApp/pago/pendiente/"

        preference_data = {
            "items": [
                {
                    "title": "Compra desde tienda",
                    "quantity": 1,
                    "currency_id": "ARS",
                    "unit_price": float(total)
                }
            ],
            
            "payer": {
            "email": "TESTUSER1704254126@testuser.com"
            },
            "back_urls": {
                "success": success_url,
                "failure": failure_url,
                "pending": pending_url
            },


            "auto_return": "approved"
        }

        try:
            preference_response = sdk.preference().create(preference_data)
            print("🔍 preference_response:", json.dumps(preference_response, indent=4))
        except Exception as e:
            return render(request, "CarritoApp/error_mercadopago.html", {
                "error": f"Error al crear preferencia en Mercado Pago: {str(e)}"
            })

        if "response" in preference_response and "init_point" in preference_response["response"]:
            return redirect(preference_response["response"]["init_point"])
        else:
            return render(request, "CarritoApp/error_mercadopago.html", {
                "error": "No se pudo generar el enlace de pago.",
                "detalle": json.dumps(preference_response, indent=4)
            })

    return redirect("CarritoApp:tienda")

#----------------------pago_exitoso Mercado Pago------------------
import json
import mercadopago
from django.conf import settings
import requests
from datetime import date
from django.shortcuts import render, redirect
from django.conf import settings
from .models import Producto, Factura

def pago_exitoso(request):
    # 📦 Recuperar datos de sesión y pago
    datos = request.session.pop("factura_datos", None)
    payment_id = request.GET.get("payment_id")

    if not datos or not payment_id:
        return render(request, "CarritoApp/error_mercadopago.html", {
            "error": "Faltan datos del pago o de la factura."
        })

    # ✅ Consultar el estado del pago en la API de Mercado Pago
    try:
        response = requests.get(
            f"https://api.mercadopago.com/v1/payments/{payment_id}",
            headers={"Authorization": f"Bearer {settings.MERCADOPAGO_ACCESS_TOKEN}"}
        )
        status = response.json().get("status", "")

        if status != "approved":
            return render(request, "CarritoApp/error_mercadopago.html", {
                "error": f"El pago no fue aprobado. Estado actual: {status}"
            })
    except Exception as e:
        return render(request, "CarritoApp/error_mercadopago.html", {
            "error": f"No se pudo verificar el estado del pago: {e}"
        })

    # 🧾 Validar método de pago
    metodo = datos.get("metodo_pago", "Efectivo").strip().title()
    if metodo not in [op[0] for op in Factura._meta.get_field("metodo_pago").choices]:
        metodo = "Efectivo"

    # 🧾 Crear factura y descontar stock
    try:
        factura = Factura.objects.create(
            fecha=date.today(),
            dni_cliente=datos["dni"],
            nombre_cliente=datos["nombre"],
            apellido_cliente=datos["apellido"],
            metodo_pago=metodo,
            total=datos["total"],
            total_con_interes=datos["total"],
            vendedor="Carrito Web",
            detalle_productos=json.dumps(datos["detalle"])
        )
        factura.numero_factura = str(factura.id).zfill(5)
        factura.save()

        for item in datos["detalle"]:
            producto = Producto.objects.filter(nombre_producto=item["nombre_producto"]).first()
            if producto:
                producto.stock -= item["cantidad_vendida"]
                producto.save()

    except Exception as e:
        return render(request, "CarritoApp/error_mercadopago.html", {
            "error": f"Error al guardar la factura: {e}"
        })

    # 🧹 Limpiar carrito y redirigir
    request.session["carrito"] = {}
    request.session.modified = True

    return redirect("CarritoApp:detalle_factura", factura_id=factura.id)


#---------------------Guardar factura efectivo  Carrito--------------------------#
#-------------------------------------------------------------------------------
from apps.CarritoApp.models import TipoPago  # Asegurate de importarlo si no está

def guardar_efectivo(request): 
    if request.method == 'POST':
        print("✅ POST recibido:", request.POST.dict())

        metodo_pago_id = request.POST.get('metodo_pago')
        print("🎯 metodo_pago_id recibido:", metodo_pago_id)

        metodo_pago_instancia = None  # Dejamos el FK nulo
        metodo_pago_manual = "Sin especificar"

        if metodo_pago_id == "Efectivo":
            metodo_pago_manual = "Efectivo"
        else:
            try:
                tipo_pago_obj = TipoPago.objects.get(id=int(metodo_pago_id))
                metodo_pago_manual = tipo_pago_obj.tipo_pago
                print("🟢 TipoPago encontrado:", metodo_pago_manual)
            except TipoPago.DoesNotExist:
                print("❌ TipoPago no encontrado")

        numero_tiket = request.POST.get('numero_tiket', '')

        # Datos del usuario
        if request.user.is_authenticated:
            dni_cliente = request.user.dni_usuario
            nombre_cliente = request.user.first_name
            apellido_cliente = request.user.last_name
        else:
            dni_cliente = "No registrado"
            nombre_cliente = "Desconocido"
            apellido_cliente = "Usuario"

        carrito = request.session.get('carrito', {})
        total = 0
        detalle_productos = []
        errores_stock = []

        for key, value in carrito.items():
            try:
                producto = Producto.objects.get(id=value['producto_id'])
                cantidad = value['cantidad']
                precio_unitario = float(producto.precio)
                subtotal = precio_unitario * cantidad
                total += subtotal

                if producto.stock >= cantidad:
                    detalle_productos.append({
                        'nombre_producto': producto.nombre_producto,
                        'cantidad_vendida': cantidad,
                        'precio_unitario': precio_unitario,
                        'subtotal': subtotal,
                    })
                    producto.stock -= cantidad
                    producto.save()
                else:
                    errores_stock.append({
                        'nombre_producto': producto.nombre_producto,
                        'stock_disponible': producto.stock,
                        'cantidad_solicitada': cantidad
                    })
            except Producto.DoesNotExist:
                continue

        if errores_stock:
            return render(request, 'CarritoApp/error_stock.html', {'errores_stock': errores_stock})

        # Crear la factura
        nueva_factura = Factura.objects.create(
            fecha=date.today(),
            dni_cliente=dni_cliente,
            nombre_cliente=nombre_cliente,
            apellido_cliente=apellido_cliente,
            metodo_pago=None,  # FK vacío
            metodo_pago_manual=metodo_pago_manual,
            total=total,
            total_con_interes=total,
            vendedor="Carrito Web",
            numero_tiket=numero_tiket,
            detalle_productos=json.dumps(detalle_productos)
        )
        nueva_factura.numero_factura = str(nueva_factura.id).zfill(5)
        nueva_factura.save()

        print("✅ Factura creada:", nueva_factura.numero_factura)

        # Limpiar carrito
        request.session['carrito'] = {}
        request.session.modified = True

        return redirect('CarritoApp:vista_resumen_factura', factura_id=nueva_factura.id)

    return redirect('CarritoApp:tienda')

#---------------------Tipo de pago carrito--------------------------#
from django.shortcuts import render, redirect
from .models import TipoPago
from .forms import TipoPagoForm  # 👈 Import necesario para el formulario

# Vista para listar y eliminar tipos de pago
def tipo_pago_list(request):
    tipos_pago = TipoPago.objects.all()

    if request.method == "POST":
        seleccionados = request.POST.getlist("seleccionados")
        accion = request.POST.get("accion")

        if accion == "eliminar" and seleccionados:
            TipoPago.objects.filter(id__in=seleccionados).delete()
            return redirect('CarritoApp:tipo_pago_list')

    return render(request, 'CarritoApp/tipo_pago_carrito_list.html', {
        'tipos_pago': tipos_pago
    })

# ✅ NUEVA vista para agregar tipo de pago
def tipo_pago_create(request):
    if request.method == 'POST':
        form = TipoPagoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('CarritoApp:tipo_pago_list')
    else:
        form = TipoPagoForm()
    return render(request, 'CarritoApp/tipo_pago_create.html', {'form': form})



# ---------------✅ aceptado o rechazado entrega -------------------------------
# views.py
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
# from .models import Factura

@require_POST
def actualizar_estado_entrega(request, factura_id):
    estado = (request.POST.get('estado') or '').strip().lower()

    # Aceptamos ambos por si el template manda "entregado"
    alias = {'entregado': 'aceptado'}
    estado = alias.get(estado, estado)

    VALIDOS = {'pendiente', 'aceptado', 'rechazado'}
    if estado not in VALIDOS:
        messages.error(request, "Estado inválido.")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    factura = get_object_or_404(Factura, pk=factura_id)
    if factura.estado_entrega != estado:
        factura.estado_entrega = estado
        factura.save(update_fields=['estado_entrega'])

    messages.success(request, "Estado de entrega actualizado.")
    # Vuelve a la misma página con los filtros
    return redirect(request.META.get('HTTP_REFERER', '/'))




#---------------lista_cuenta_corriente-------------------------------------#
from django.shortcuts import render
from apps.CarritoApp.models import Factura

def lista_cuenta_corriente(request):
    apellido_cliente = request.GET.get('apellido_cliente', '')
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')

    # 🔎 Solo trae facturas con "Cuenta Corriente"
    facturas = Factura.objects.filter(metodo_pago_manual="Cuenta Corriente").order_by('-numero_factura')

    if apellido_cliente:
        facturas = facturas.filter(apellido_cliente__icontains=apellido_cliente)

    if fecha_desde:
        facturas = facturas.filter(fecha__gte=fecha_desde)

    if fecha_hasta:
        facturas = facturas.filter(fecha__lte=fecha_hasta)

    context = {
        'facturas': facturas
    }

    return render(request, 'CarritoApp/lista_cuenta_corriente.html', context)

#---------------lista_cuenta_corriente de las facturas-------------------------------------#
from django.shortcuts import render, get_object_or_404
from django.db.models import Sum
from apps.CarritoApp.models import Factura, CuentaCorriente

def pagos_cuenta_corriente(request, factura_id):
    factura = get_object_or_404(Factura, id=factura_id)
    pagos = CuentaCorriente.objects.filter(factura=factura)

    estado_credito_factura = "Pagado" if all(p.estado_credito == "Pagado" for p in pagos) else "Pendiente"

    return render(request, 'CarritoApp/detalle_pagos_cta_cte.html', {
        'factura': factura,
        'pagos': pagos,
        'estado_credito_factura': estado_credito_factura
    })


# ---------------=== MERCADO PAGO ===-----------------------------
import time, json
import mercadopago
from django.conf import settings
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt

sdk = mercadopago.SDK(settings.MP_ACCESS_TOKEN)

def _carrito_a_items_mp(carrito):
    """Convierte el carrito de sesión en items para MP (o en 1 ítem totalizado)."""
    items = []
    for it in carrito.values():
        items.append({
            "title": it.get("nombre", "Producto"),
            "quantity": int(it.get("cantidad", 1)),
            "unit_price": float(it.get("precio", 0.0)),
            "currency_id": "ARS",
            "id": str(it.get("producto_id")),
        })
    if not items:
        return []
    # Opción A: enviar itemizado
    return items
    # Opción B (si preferís 1 solo ítem):
    # total = sum(i["quantity"] * i["unit_price"] for i in items)
    # return [{"title": "Compra en tienda", "quantity": 1, "unit_price": total, "currency_id": "ARS"}]

def _back_url(request, path):
    return request.build_absolute_uri(path)

def _notification_url(request):
    # asegurate de tener esta url en urls.py
    return request.build_absolute_uri("/CarritoApp/mercadopago/webhook/")

from datetime import date, datetime
from django.shortcuts import redirect

def mp_checkout(request):
    # Debe haber carrito
    carrito = request.session.get("carrito", {})
    if not carrito:
        return render(request, "CarritoApp/error_mercadopago.html", {
            "error": "No hay productos en el carrito."
        })

    # Datos del usuario
    if request.user.is_authenticated:
        dni = getattr(request.user, "dni_usuario", "") or "No registrado"
        nombre = request.user.first_name or "Desconocido"
        apellido = request.user.last_name or "Usuario"
        email = getattr(request.user, "email", "") or "comprador@example.com"
    else:
        dni, nombre, apellido, email = "No registrado", "Desconocido", "Usuario", "comprador@example.com"

    items = _carrito_a_items_mp(carrito)
    if not items:
        return render(request, "CarritoApp/error_mercadopago.html", {
            "error": "No hay productos válidos en el carrito."
        })

    total = sum(i["quantity"] * i["unit_price"] for i in items)

    # Guardamos en sesión lo necesario para crear la factura al volver
    request.session["factura_datos"] = {
        "dni": dni,
        "nombre": nombre,
        "apellido": apellido,
        "total": total,
        "detalle": [{
            "nombre_producto": it["title"],
            "cantidad_vendida": it["quantity"],
            "precio_unitario": it["unit_price"],
            "subtotal": it["quantity"] * it["unit_price"],
        } for it in items]
    }
    request.session.modified = True


    # Referencia externa para matchear en webhook (opcional)
    external_reference = f"ORDER-{request.user.id if request.user.is_authenticated else 'anon'}-{int(time.time())}"

    preference_data = {
        "items": items,
        "payer": {"email": email},
        "external_reference": external_reference,
        "back_urls": {
            # asegurate de tener estas vistas/urls
            "success": _back_url(request, "/CarritoApp/pago/exito/"),
            "pending": _back_url(request, "/CarritoApp/pago/pendiente/"),
            "failure": _back_url(request, "/CarritoApp/pago/fallo/"),
        },
        "auto_return": "approved",
        "notification_url": _notification_url(request),  # webhook
        "statement_descriptor": "TU TIENDA",
    }

    try:
        pref = sdk.preference().create(preference_data)
        init_point = pref["response"].get("init_point")
        if not init_point:
            return render(request, "CarritoApp/error_mercadopago.html", {
                "error": "Mercado Pago no devolvió init_point.",
                "detalle": json.dumps(pref, indent=2, ensure_ascii=False)
            })
        return redirect(init_point)
    except Exception as e:
        return render(request, "CarritoApp/error_mercadopago.html", {
            "error": f"Error creando la preferencia: {e}"
        })

#---------- Pago exitoso ---------------------------------

import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont  # pip install Pillow (ya lo usa Django para ImageField)
from django.core.files.base import ContentFile

def pago_exitoso(request):
    datos = request.session.pop("factura_datos", None)
    payment_id = request.GET.get("payment_id")

    if not datos or not payment_id:
        return render(request, "CarritoApp/error_mercadopago.html", {
            "error": "Faltan datos del pago o de la compra."
        })

    # 1) Confirmar contra MP
    try:
        r = requests.get(
            f"https://api.mercadopago.com/v1/payments/{payment_id}",
            headers={"Authorization": f"Bearer {settings.MP_ACCESS_TOKEN}"}
        )
        pay = r.json()
        status = pay.get("status", "")
        if status != "approved":
            return render(request, "CarritoApp/error_mercadopago.html", {
                "error": f"El pago no fue aprobado (estado: {status})."
            })
    except Exception as e:
        return render(request, "CarritoApp/error_mercadopago.html", {
            "error": f"No se pudo verificar el pago: {e}"
        })

    # ---- Datos útiles para el “ticket” ----
    monto = pay.get("transaction_amount")              # 100.0
    fecha_aprob = pay.get("date_approved", "")         # ISO
    external_ref = pay.get("external_reference", "")   # ORDER-...
    payer_email = (pay.get("payer") or {}).get("email", "")

    # 2) Crear factura (GUARDAMOS payment_id como numero_tiket)
    try:
        factura = Factura.objects.create(
            fecha=date.today(),
            dni_cliente=datos["dni"],
            nombre_cliente=datos["nombre"],
            apellido_cliente=datos["apellido"],
            metodo_pago_manual="Mercado Pago",
            total=datos["total"],
            total_con_interes=datos["total"],
            vendedor="Carrito Web",
            detalle_productos=json.dumps(datos["detalle"], ensure_ascii=False),
            numero_tiket=str(payment_id),   # ← Referencia de pago de MP
        )
        factura.numero_factura = str(factura.id).zfill(5)

        # 3) Generar una imagen simple de comprobante y guardarla en imagen_factura
        try:
            w, h = 900, 520
            img = Image.new("RGB", (w, h), (255, 255, 255))
            draw = ImageDraw.Draw(img)
            # Fuentes
            try:
                # si no hay TTF en el server, va a usar la default
                font_title = ImageFont.truetype("arial.ttf", 28)
                font_body = ImageFont.truetype("arial.ttf", 22)
            except:
                font_title = ImageFont.load_default()
                font_body  = ImageFont.load_default()

            y = 30
            draw.text((30, y), "Comprobante de Pago - Mercado Pago", fill=(0, 0, 0), font=font_title); y += 50
            draw.text((30, y), f"Factura N°: {factura.numero_factura}", fill=(0,0,0), font=font_body); y += 35
            draw.text((30, y), f"Referencia de pago (MP): {payment_id}", fill=(0,0,0), font=font_body); y += 35
            draw.text((30, y), f"Referencia del vendedor: {external_ref or '-'}", fill=(0,0,0), font=font_body); y += 35
            draw.text((30, y), f"Monto: ${monto:.2f}" if monto is not None else "Monto: -", fill=(0,0,0), font=font_body); y += 35
            draw.text((30, y), f"Fecha aprobación: {fecha_aprob or '-'}", fill=(0,0,0), font=font_body); y += 35
            draw.text((30, y), f"Payer email: {payer_email or '-'}", fill=(0,0,0), font=font_body); y += 35
            draw.text((30, y), "Método: Mercado Pago", fill=(0,0,0), font=font_body)

            buf = BytesIO()
            img.save(buf, format="PNG")
            buf.seek(0)
            factura.imagen_factura.save(f"mp_ticket_{payment_id}.png", ContentFile(buf.getvalue()), save=False)
        except Exception as e_img:
            # Si falla la imagen, seguimos igual con la factura
            print("No se pudo generar imagen de ticket:", e_img)

        factura.save()

        # 4) Descontar stock
        for item in datos["detalle"]:
            prod = Producto.objects.filter(nombre_producto=item["nombre_producto"]).first()
            if prod:
                prod.stock = max(0, prod.stock - int(item["cantidad_vendida"]))
                prod.save()

    except Exception as e:
        return render(request, "CarritoApp/error_mercadopago.html", {
            "error": f"Error al guardar la factura: {e}"
        })

    # Limpiar carrito
    request.session["carrito"] = {}
    request.session.modified = True

    return redirect("CarritoApp:detalle_factura", factura_id=factura.id)


# ---------------mp_webhook--------------------icar que llega
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def mp_webhook(request):
    """Webhook de Mercado Pago (recibe notificaciones)."""
    try:
        event_type = request.GET.get("type") or request.GET.get("topic")
        data_id = request.GET.get("data.id") or request.GET.get("id")

        body = {}
        if request.method == "POST":
            try:
                body = json.loads(request.body.decode() or "{}")
                event_type = event_type or body.get("type") or body.get("topic")
                data = body.get("data") or {}
                data_id = data_id or data.get("id")
            except Exception:
                body = {}

        # Log simple para verificar que llega
        print("MP Webhook:", {"event_type": event_type, "data_id": data_id, "body": body})

        # (Opcional) acá podrías consultar el pago y actualizar tu DB
        return JsonResponse({"received": True})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


# -----------------------------------------------------------------------


# apps/CarritoApp/views_mensajes.py
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import MensajeClienteForm
from .models import MensajeCliente


def es_staff(user):
    return user.is_staff or user.groups.filter(name__in=["Administradores", "Facturadores"]).exists()


# --- CLIENTE crea mensaje (requiere login) -----------------------------------
@login_required
@require_POST
def crear_mensaje(request):
    """
    Crea un mensaje de cliente. Por seguridad, sobrescribe apellido, nombre y
    email con los del usuario autenticado si existen.
    """
    form = MensajeClienteForm(request.POST)
    if not form.is_valid():
        messages.error(request, "Revisá los datos del formulario.")
        return redirect(request.META.get("HTTP_REFERER", "/"))

    obj = form.save(commit=False)
    u = request.user
    obj.creado_por = u

    # Forzar datos del usuario si están presentes
    if getattr(u, "last_name", ""):
        obj.apellido = u.last_name
    if getattr(u, "first_name", ""):
        obj.nombre = u.first_name
    if not obj.email_contacto and getattr(u, "email", ""):
        obj.email_contacto = u.email

    obj.save()
    messages.success(request, "¡Tu mensaje fue enviado! Pronto te contactaremos.")
    return redirect(request.META.get("HTTP_REFERER", "/"))


# --- ADMIN: listado, responder y eliminar ------------------------------------
@user_passes_test(es_staff)
def lista_mensajes(request):
    """
    Lista de mensajes para el administrador con búsqueda.
    """
    q = request.GET.get("q", "").strip()
    mensajes = MensajeCliente.objects.filter(activo=True).order_by("-creado_en")
    if q:
        mensajes = mensajes.filter(
            Q(pedido__icontains=q) |
            Q(apellido__icontains=q) |
            Q(nombre__icontains=q) |
            Q(respuesta__icontains=q)
        )
    return render(request, "CarritoApp/mensajes_admin.html", {"mensajes": mensajes, "q": q})


@user_passes_test(es_staff)
@require_POST
def responder_mensaje(request, pk):
    msg = get_object_or_404(MensajeCliente, pk=pk, activo=True)
    respuesta = request.POST.get("respuesta", "").strip()
    if not respuesta:
        messages.error(request, "La respuesta no puede estar vacía.")
        return redirect("CarritoApp:mensajes_admin")

    msg.respuesta = respuesta
    msg.respondido = True
    msg.respondido_por = request.user
    msg.respondido_en = timezone.now()
    msg.save()

    # (Opcional) Enviar email si dejó correo
    # if msg.email_contacto:
    #     from django.core.mail import send_mail
    #     send_mail(
    #         subject=f"Respuesta a tu mensaje #{msg.id}",
    #         message=respuesta,
    #         from_email=None,
    #         recipient_list=[msg.email_contacto],
    #         fail_silently=True,
    #     )

    messages.success(request, f"Mensaje #{msg.id} respondido.")
    return redirect("CarritoApp:mensajes_admin")


@user_passes_test(es_staff)
@require_POST
def eliminar_mensaje(request, pk):
    msg = get_object_or_404(MensajeCliente, pk=pk, activo=True)
    msg.activo = False
    msg.save(update_fields=["activo"])
    messages.success(request, f"Mensaje #{msg.id} eliminado.")
    return redirect("CarritoApp:mensajes_admin")


# --- CLIENTE: ver sus propios mensajes (solo lectura) ------------------------
@login_required
def mis_mensajes(request):
    """
    El cliente ve sus mensajes y respuestas. Filtro por creado_por o por email.
    """
    q = request.GET.get("q", "").strip()
    solo_respondidos = request.GET.get("respondidos") == "1"

    mensajes = (MensajeCliente.objects
                .filter(activo=True)
                .filter(Q(creado_por=request.user) | Q(email_contacto=request.user.email))
                .order_by("-creado_en"))

    if q:
        mensajes = mensajes.filter(Q(pedido__icontains=q) | Q(respuesta__icontains=q))
    if solo_respondidos:
        mensajes = mensajes.filter(respondido=True)

    return render(
        request,
        "CarritoApp/mis_mensajes.html",
        {"mensajes": mensajes, "q": q, "solo_respondidos": solo_respondidos},
    )