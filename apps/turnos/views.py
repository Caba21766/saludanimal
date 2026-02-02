from datetime import timedelta, time
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse

from .models import Motivo, Oficina, Turno
from .forms import DniForm, MotivoForm, OficinaForm, FechaRangoForm

# ✅ Horarios (editá a gusto)
TIME_SLOTS = [
    time(6, 0), time(6, 30), time(6, 50),
    time(7, 10), time(7, 50),
    time(8, 30), time(8, 50),
    time(9, 10), time(9, 30), time(9, 50),
    time(10, 10), time(10, 30), time(10, 50),
    time(12, 10),
]

DAYS_FORWARD = 30  # días a futuro visibles

def _get_wizard(request):
    return request.session.get("turno_wizard", {})

def _set_wizard(request, data):
    request.session["turno_wizard"] = data
    request.session.modified = True

def _clear_wizard(request):
    request.session.pop("turno_wizard", None)
    request.session.modified = True


from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

@login_required
def cancelar_wizard(request):
    return redirect("turnos:cancelar_lista")



# paso 1
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.urls import reverse
from urllib.parse import urlencode
from django.db.models import Q

User = get_user_model()

def paso1_dni(request):
    wiz = _get_wizard(request)
    cliente = None
    mostrar_datos = False

    if request.method == "POST":
        form = DniForm(request.POST)
        if form.is_valid():
            dni = form.cleaned_data["dni"]
            dni = "".join(ch for ch in str(dni) if ch.isdigit())

            accion = request.POST.get("accion")  # aceptar / continuar

            if accion == "aceptar":
                # ✅ ACÁ "encontrás el cliente"
                cliente = User.objects.filter(
                    Q(dni_usuario=str(dni)) | Q(username=str(dni))
                ).first()

                if not cliente:
                    params = urlencode({"dni": dni, "next": reverse("turnos:paso1_dni")})
                    return redirect(f"/users/registrarse/?{params}")

                # ✅ ACÁ MISMO guardás quién es el titular del turno
                wiz["dni"] = dni
                wiz["user_id"] = cliente.id   # 👈 ESTE ES EL QUE TE FALTABA
                _set_wizard(request, wiz)

                mostrar_datos = True

            elif accion == "continuar":
                # opcional: por si querés asegurarte que quede guardado
                wiz["dni"] = dni
                _set_wizard(request, wiz)
                return redirect("turnos:paso2_motivo")

    else:
        form = DniForm(initial={"dni": wiz.get("dni", "")})

    return render(request, "turnos/paso1_dni.html", {
        "form": form,
        "cliente": cliente,
        "mostrar_datos": mostrar_datos,
        "step": 1
    })

#####---------------------------#########-----------------------------


# paso 2
def paso2_motivo(request):
    wiz = _get_wizard(request)
    if not wiz.get("dni"):
        return redirect("turnos:paso1_dni")

    if request.method == "POST":
        form = MotivoForm(request.POST)
        if form.is_valid():
            wiz["motivo_id"] = form.cleaned_data["motivo"].id

            # (opcional) si querés limpiar oficina previa por si venía cargada:
            wiz.pop("oficina_id", None)

            _set_wizard(request, wiz)

            # ✅ antes: return redirect("turnos:paso3_oficina")
            return redirect("turnos:paso4_fecha")
    else:
        initial = {}
        if wiz.get("motivo_id"):
            initial["motivo"] = wiz["motivo_id"]
        form = MotivoForm(initial=initial)

    return render(request, "turnos/paso2_motivo.html", {"form": form, "step": 2})


def paso3_oficina(request):
    wiz = _get_wizard(request)
    if not wiz.get("dni") or not wiz.get("motivo_id"):
        return redirect("turnos:paso1_dni")

    # ✅ Si querés “una sola oficina fija”, podés setearla acá y saltar:
    # oficina_default = Oficina.objects.filter(activo=True).order_by("orden").first()
    # if oficina_default:
    #     wiz["oficina_id"] = oficina_default.id
    #     _set_wizard(request, wiz)
    #     return redirect("turnos:paso4_fecha")

    if request.method == "POST":
        form = OficinaForm(request.POST)
        if form.is_valid():
            wiz["oficina_id"] = form.cleaned_data["oficina"].id
            _set_wizard(request, wiz)
            return redirect("turnos:paso4_fecha")
    else:
        initial = {}
        if wiz.get("oficina_id"):
            initial["oficina"] = wiz["oficina_id"]
        form = OficinaForm(initial=initial)

    return render(request, "turnos/paso3_oficina.html", {"form": form, "step": 3})


def paso4_fecha(request):
    wiz = _get_wizard(request)
    if not wiz.get("dni") or not wiz.get("motivo_id"):
        return redirect("turnos:paso1_dni")

    # oficina opcional
    oficina_id = wiz.get("oficina_id")
    oficina = Oficina.objects.filter(id=oficina_id).first() if oficina_id else None

    hoy = timezone.localdate()
    dias = [hoy + timedelta(days=i) for i in range(0, DAYS_FORWARD + 1)]

    # Turnos reservados en rango para marcar días con ocupación
    qs = Turno.objects.filter(
        estado="RESERVADO",
        fecha__range=(dias[0], dias[-1]),
    )
    if oficina:
        qs = qs.filter(oficina=oficina)

    ocupados_por_dia = {}
    for t in qs.only("fecha", "hora"):
        ocupados_por_dia.setdefault(t.fecha, set()).add(t.hora)

    # día habilitado si tiene al menos 1 slot libre
    dias_info = []
    for d in dias:
        ocupados = ocupados_por_dia.get(d, set())
        libre = any(slot not in ocupados for slot in TIME_SLOTS)
        dias_info.append({"fecha": d, "habilitado": libre})

    if request.method == "POST":
        form = FechaRangoForm({"fecha": request.POST.get("fecha")}, dias_hacia_adelante=DAYS_FORWARD)
        if form.is_valid():
            wiz["fecha"] = str(form.cleaned_data["fecha"])
            _set_wizard(request, wiz)
            return redirect("turnos:paso5_hora")
    else:
        form = FechaRangoForm(dias_hacia_adelante=DAYS_FORWARD)

    return render(request, "turnos/paso4_fecha.html", {
        "step": 4,
        "dias_info": dias_info,
        "form": form,
        "oficina": oficina,
        "wiz": wiz,
    })


def paso5_hora(request):
    wiz = _get_wizard(request)
    if not wiz.get("dni") or not wiz.get("motivo_id") or not wiz.get("fecha"):
        return redirect("turnos:paso1_dni")

    oficina = Oficina.objects.filter(id=wiz.get("oficina_id")).first() if wiz.get("oficina_id") else None
    fecha = timezone.datetime.fromisoformat(wiz["fecha"]).date()

    qs = Turno.objects.filter(estado="RESERVADO", fecha=fecha)
    if oficina:
        qs = qs.filter(oficina=oficina)

    ocupados = set(qs.values_list("hora", flat=True))

    # agrupar por hora para mostrar “bloques” tipo ANSES
    grupos = {}
    for slot in TIME_SLOTS:
        grupos.setdefault(slot.hour, []).append({
            "hora": slot,
            "ocupado": slot in ocupados,
        })

    if request.method == "POST":
        hora_str = request.POST.get("hora")  # "HH:MM"
        try:
            hh, mm = hora_str.split(":")
            hora = time(int(hh), int(mm))
        except Exception:
            hora = None

        if hora not in TIME_SLOTS:
            messages.error(request, "Horario inválido.")
        else:
            # validar disponible
            existe = Turno.objects.filter(
                estado="RESERVADO",
                fecha=fecha,
                hora=hora,
            )
            if oficina:
                existe = existe.filter(oficina=oficina)
            if existe.exists():
                messages.error(request, "Ese horario ya fue tomado. Elegí otro.")
            else:
                wiz["hora"] = hora.strftime("%H:%M")
                _set_wizard(request, wiz)
                return redirect("turnos:paso6_confirmar")

    return render(request, "turnos/paso5_hora.html", {
        "step": 5,
        "grupos": grupos,
        "fecha": fecha,
        "oficina": oficina,
        "wiz": wiz,
    })


def paso6_confirmar(request):
    wiz = _get_wizard(request)
    if not wiz.get("dni") or not wiz.get("motivo_id") or not wiz.get("fecha") or not wiz.get("hora"):
        return redirect("turnos:paso1_dni")

    motivo = get_object_or_404(Motivo, id=wiz["motivo_id"])
    oficina = Oficina.objects.filter(id=wiz.get("oficina_id")).first() if wiz.get("oficina_id") else None
    fecha = timezone.datetime.fromisoformat(wiz["fecha"]).date()
    hh, mm = wiz["hora"].split(":")
    hora = time(int(hh), int(mm))

    # ✅ precio desde motivo (ajustá el nombre del campo si es distinto)
    precio = getattr(motivo, "precio", None) or 0

    return render(request, "turnos/paso6_confirmar.html", {
        "step": 6,
        "motivo": motivo,
        "oficina": oficina,
        "fecha": fecha,
        "hora": hora,
        "dni": wiz["dni"],
        "precio": precio,
    })


def exito(request, turno_id):
    turno = get_object_or_404(Turno, id=turno_id)
    return render(request, "turnos/exito.html", {"turno": turno})



#-------------- Cancelar listas-------------------------------------------

from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from .models import Turno

from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from .models import Turno


def _dni_user(request):
    dni = getattr(request.user, "dni_usuario", None) or request.user.username
    return "".join(ch for ch in str(dni) if ch.isdigit())


@login_required
@require_http_methods(["GET"])
def cancelar_lista(request):
    dni = _dni_user(request)

    if not dni:
        messages.error(request, "Tu usuario no tiene DNI/CUIL cargado.")
        return redirect("turnos:paso1_dni")  # o a donde quieras mandarlo

    turnos = (
        Turno.objects
        .filter(dni=dni, estado="RESERVADO")
        .select_related("motivo", "oficina")
        .order_by("fecha", "hora")
    )

    return render(request, "turnos/cancelar_lista.html", {
        "dni": dni,
        "turnos": turnos
    })


@login_required
@require_http_methods(["GET", "POST"])
def cancelar_confirmar(request, turno_id):
    dni = _dni_user(request)

    if not dni:
        messages.error(request, "Tu usuario no tiene DNI/CUIL cargado.")
        return redirect("turnos:cancelar_lista")

    turno = get_object_or_404(Turno, id=turno_id, dni=dni)

    if request.method == "POST":
        if turno.estado != "RESERVADO":
            messages.warning(request, "Ese turno ya no está en estado RESERVADO.")
            return redirect("turnos:cancelar_lista")

        turno.estado = "CANCELADO"

        # Evita error si tu modelo no tiene actualizado_en
        if hasattr(turno, "actualizado_en"):
            turno.actualizado_en = timezone.now()
            turno.save(update_fields=["estado", "actualizado_en"])
        else:
            turno.save(update_fields=["estado"])

        messages.success(request, "Turno cancelado correctamente.")
        return redirect("turnos:cancelar_lista")

    return render(request, "turnos/cancelar_confirmar.html", {"turno": turno})

#------------------- fin de cancelar----------------------------------------


from django.conf import settings
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
import mercadopago

def confirmar_turno(request):
    # ✅ EJEMPLO: estos datos normalmente los tenés en session por los pasos previos
    motivo   = request.session.get("motivo_nombre", "Turno")
    dni      = request.session.get("dni", "")
    fecha    = request.session.get("fecha", "")
    hora     = request.session.get("hora", "")
    oficina  = request.session.get("oficina_nombre", "")

    # ✅ Precio del turno (poné el tuyo)
    precio = float(request.session.get("precio_turno", 1000))

    if not settings.MP_ACCESS_TOKEN:
        messages.error(request, "Falta configurar MP_ACCESS_TOKEN en el servidor.")
        return render(request, "turnos/confirmar_turno.html", {
            "motivo": {"nombre": motivo},
            "dni": dni,
            "fecha": fecha,
            "hora": hora,
            "oficina": {"nombre": oficina} if oficina else None,
            "precio": precio,
            "mp_init_point": None,
        })

    # 👉 Cuando el usuario haga click en "Pagar", creamos la preferencia y mostramos el link
    # (podés crearlo en GET también, pero mejor en POST para no generar preferencias por refresh)
    if request.method == "POST":
        sdk = mercadopago.SDK(settings.MP_ACCESS_TOKEN)

        success_url = request.build_absolute_uri(reverse("turnos:mp_success"))
        failure_url = request.build_absolute_uri(reverse("turnos:mp_failure"))
        pending_url = request.build_absolute_uri(reverse("turnos:mp_pending"))

        preference_data = {
            "items": [{
                "title": f"Turno - {motivo} - {fecha} {hora}",
                "quantity": 1,
                "currency_id": "ARS",
                "unit_price": precio,
            }],
            "payer": {
                "identification": {
                    "type": "DNI",
                    "number": str(dni) if dni else "",
                }
            },
            "back_urls": {
                "success": success_url,
                "failure": failure_url,
                "pending": pending_url,
            },
            "auto_return": "approved",
            # si querés: "external_reference": "algo-para-tus-registros",
        }

        pref = sdk.preference().create(preference_data)
        init_point = (pref.get("response") or {}).get("init_point")

        if not init_point:
            messages.error(request, "Mercado Pago no devolvió el link de pago (init_point).")
            return redirect("turnos:confirmar")

        # ✅ Redirige directo a MP para pagar
        return redirect(init_point)

    # GET: render normal
    return render(request, "turnos/confirmar_turno.html", {
        "motivo": {"nombre": motivo},
        "dni": dni,
        "fecha": fecha,
        "hora": hora,
        "oficina": {"nombre": oficina} if oficina else None,
        "precio": precio,
    })



def mp_success(request):
    turno_id = request.GET.get("external_reference") or request.session.get("turno_mp_id")
    if turno_id:
        return redirect("turnos:exito", turno_id=turno_id)
    return render(request, "turnos/mp_resultado.html", {"titulo": "Pago exitoso"})

def mp_failure(request):
    turno_id = request.GET.get("external_reference") or request.session.get("turno_mp_id")
    if turno_id:
        # ✅ libero el horario cancelando el turno
        Turno.objects.filter(id=turno_id).update(estado="CANCELADO")
    return render(request, "turnos/mp_resultado.html", {"titulo": "Pago rechazado / cancelado"})

def mp_pending(request):
    return render(request, "turnos/mp_resultado.html", {"titulo": "Pago pendiente"})







import mercadopago
from django.conf import settings
from django.db import transaction
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_POST

@require_POST
def mp_checkout(request):
    wiz = _get_wizard(request)
    if not wiz.get("dni") or not wiz.get("motivo_id") or not wiz.get("fecha") or not wiz.get("hora"):
        messages.error(request, "Faltan datos del turno. Volvé y confirmá nuevamente.")
        return redirect("turnos:paso6_confirmar")

    if not getattr(settings, "MP_ACCESS_TOKEN", None):
        messages.error(request, "Falta configurar MP_ACCESS_TOKEN en el servidor.")
        return redirect("turnos:paso6_confirmar")

    motivo = get_object_or_404(Motivo, id=wiz["motivo_id"])
    oficina = Oficina.objects.filter(id=wiz.get("oficina_id")).first() if wiz.get("oficina_id") else None
    fecha = timezone.datetime.fromisoformat(wiz["fecha"]).date()
    hh, mm = wiz["hora"].split(":")
    hora = time(int(hh), int(mm))

    precio = getattr(motivo, "precio", None) or 0
    try:
        precio = float(precio)
    except:
        precio = 0

    if precio <= 0:
        messages.error(request, "El precio quedó en $0. Revisá el campo precio del Motivo.")
        return redirect("turnos:paso6_confirmar")

    # ✅ Reservo el slot (creo el turno) con lock para evitar que lo tomen al mismo tiempo
    with transaction.atomic():
        existe = Turno.objects.select_for_update().filter(
            estado="RESERVADO",
            fecha=fecha,
            hora=hora,
        )
        if oficina:
            existe = existe.filter(oficina=oficina)

        if existe.exists():
            messages.error(request, "Ese horario se ocupó recién. Elegí otro.")
            return redirect("turnos:paso5_hora")

        turno = Turno.objects.create(
            dni=wiz["dni"],
            motivo=motivo,
            oficina=oficina,
            fecha=fecha,
            hora=hora,
            estado="RESERVADO",
        )

    # guardo el turno en sesión por si MP no manda external_reference
    request.session["turno_mp_id"] = str(turno.id)
    request.session.modified = True

    sdk = mercadopago.SDK(settings.MP_ACCESS_TOKEN)

    success_url = request.build_absolute_uri(reverse("turnos:mp_success"))
    failure_url = request.build_absolute_uri(reverse("turnos:mp_failure"))
    pending_url = request.build_absolute_uri(reverse("turnos:mp_pending"))

    preference_data = {
        "items": [{
            "title": f"Turno - {motivo.nombre} - {fecha} {hora.strftime('%H:%M')}",
            "quantity": 1,
            "currency_id": "ARS",
            "unit_price": precio,
        }],
        "external_reference": str(turno.id),
        "back_urls": {
            "success": success_url,
            "failure": failure_url,
            "pending": pending_url,
        },
        "auto_return": "approved",
    }

    pref = sdk.preference().create(preference_data)
    init_point = (pref.get("response") or {}).get("init_point")

    if not init_point:
        messages.error(request, "Mercado Pago no devolvió init_point.")
        return redirect("turnos:paso6_confirmar")

    # ✅ importante: ahora sí te manda a MP
    _clear_wizard(request)
    return redirect(init_point)


#-----------Listado de Turnos --------------------------------------

from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q, OuterRef, Subquery, Value, CharField
from django.db.models.functions import Coalesce
from django.contrib.auth import get_user_model
from django.db.models import Sum, DecimalField
from django.core.paginator import Paginator

User = get_user_model()

@staff_member_required
def listado_turnos(request):
    q = (request.GET.get("q") or "").strip()
    estado = (request.GET.get("estado") or "").strip()
    desde = request.GET.get("desde")  # YYYY-MM-DD
    hasta = request.GET.get("hasta")  # YYYY-MM-DD

    qs = Turno.objects.select_related("motivo", "oficina").order_by("-fecha", "-hora")

    # filtros
    if q:
        qs = qs.filter(
            Q(dni__icontains=q) |
            Q(motivo__nombre__icontains=q)
        )

    if estado:
        qs = qs.filter(estado=estado)

    if desde:
        qs = qs.filter(fecha__gte=desde)
    if hasta:
        qs = qs.filter(fecha__lte=hasta)

    # ✅ traer datos del usuario por DNI (dni_usuario o username)
    u_qs = User.objects.filter(
        Q(dni_usuario=OuterRef("dni")) | Q(username=OuterRef("dni"))
    )

    qs = qs.annotate(
        apellido=Coalesce(Subquery(u_qs.values("last_name")[:1]), Value("-", output_field=CharField())),
        nombre=Coalesce(Subquery(u_qs.values("first_name")[:1]), Value("-", output_field=CharField())),
        celular=Coalesce(Subquery(u_qs.values("tel1_usuario")[:1]), Value("-", output_field=CharField())),
        domicilio=Coalesce(Subquery(u_qs.values("domicilio_usuario")[:1]), Value("-", output_field=CharField())),
    )

    # ✅ TOTAL en SQL
    total_importe = qs.aggregate(
        total=Coalesce(
            Sum("motivo__precio"),
            Value(0),
            output_field=DecimalField(max_digits=12, decimal_places=2)
        )
    )["total"]

    return render(request, "turnos/listado_turnos.html", {
        "turnos": qs,
        "total_importe": total_importe,   # ✅
        "q": q,
        "estado": estado,
        "desde": desde,
        "hasta": hasta,
        "estados": ["RESERVADO", "CANCELADO", "ATENDIDO"],
    })



#--------- --------------------------------------
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.urls import reverse

from .models import Turno

@staff_member_required
@require_POST
def cambiar_estado_turno(request, turno_id):
    turno = get_object_or_404(Turno, id=turno_id)

    nuevo = (request.POST.get("estado") or "").strip().upper()
    estados_validos = {"RESERVADO", "CANCELADO", "ATENDIDO"}

    if nuevo not in estados_validos:
        messages.error(request, "Estado inválido.")
        return redirect(request.POST.get("next") or reverse("turnos:listado"))

    # guarda
    turno.estado = nuevo
    turno.save(update_fields=["estado", "actualizado_en"])

    messages.success(request, f"Estado actualizado a {nuevo}.")
    return redirect(request.POST.get("next") or reverse("turnos:listado"))
