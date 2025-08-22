# tu_app/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

# Admin personalizado para mostrar/editar DNI y demás extras
class CustomUserAdmin(BaseUserAdmin):
    # columnas en el listado
    list_display = ("username", "email", "first_name", "last_name", "dni_usuario", "is_staff")
    search_fields = ("username", "email", "first_name", "last_name", "dni_usuario")
    list_filter = BaseUserAdmin.list_filter  # podés agregar filtros propios si querés

    # mostrar tus campos extra en los formularios del admin
    fieldsets = BaseUserAdmin.fieldsets + (
        (_("Datos adicionales"), {
            "fields": ("dni_usuario", "domicilio_usuario", "tel1_usuario", "tel2_usuario", "cuil", "iva", "imagen_usuario"),
        }),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (_("Datos adicionales"), {
            "classes": ("wide",),
            "fields": ("dni_usuario", "domicilio_usuario", "tel1_usuario", "tel2_usuario", "cuil", "iva", "imagen_usuario"),
        }),
    )

# Desregistrar y registrar de nuevo para evitar AlreadyRegistered
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

admin.site.register(User, CustomUserAdmin)
