from django.urls import path
from . import views

app_name = "turnos"

urlpatterns = [
    # Wizard
    path("", views.paso1_dni, name="paso1_dni"),
    path("motivo/", views.paso2_motivo, name="paso2_motivo"),
    path("oficina/", views.paso3_oficina, name="paso3_oficina"),
    path("fecha/", views.paso4_fecha, name="paso4_fecha"),
    path("hora/", views.paso5_hora, name="paso5_hora"),
    path("confirmar/", views.paso6_confirmar, name="paso6_confirmar"),
    path("exito/<uuid:turno_id>/", views.exito, name="exito"),

    # Mercado Pago
    path("pago/mercadopago/", views.mp_checkout, name="mp_checkout"),
    path("pago/success/", views.mp_success, name="mp_success"),
    path("pago/failure/", views.mp_failure, name="mp_failure"),
    path("pago/pending/", views.mp_pending, name="mp_pending"),

    # Cancelación por DNI
    path("cancelar/", views.cancelar_wizard, name="cancelar"),
    path("cancelar/lista/", views.cancelar_lista, name="cancelar_lista"),
    path("cancelar/<uuid:turno_id>/", views.cancelar_confirmar, name="cancelar_confirmar"),

    path("listado/", views.listado_turnos, name="listado"),
    path("estado/<uuid:turno_id>/", views.cambiar_estado_turno, name="cambiar_estado"),
]
