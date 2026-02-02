from django.contrib import admin
from .models import Motivo, Oficina, Turno

@admin.register(Motivo)
class MotivoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "precio", "activo", "orden")
    list_editable = ("precio", "activo", "orden")
    search_fields = ("nombre",)


@admin.register(Oficina)
class OficinaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "ciudad", "provincia", "activo", "orden")
    list_filter = ("activo", "provincia")
    search_fields = ("nombre", "direccion", "ciudad", "provincia")
    ordering = ("orden", "nombre")


@admin.register(Turno)
class TurnoAdmin(admin.ModelAdmin):
    list_display = ("dni", "motivo", "oficina", "fecha", "hora", "estado", "creado_en")
    list_filter = ("estado", "fecha", "oficina", "motivo")
    search_fields = ("dni", "motivo__nombre", "oficina__nombre")
    ordering = ("-creado_en",)
