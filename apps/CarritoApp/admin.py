from django.contrib import admin
from .models import Factura, Producto, Compra, Provedor, Venta, Categ_producto, CuentaCorriente
# Registro de modelos con admin.site.register

admin.site.register(Venta)
admin.site.register(Provedor)
from django.contrib import admin
from .models import Factura
from django.contrib import admin
from .models import Factura

@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    list_display = (
        'numero_factura',
        'fecha',
        'dni_cliente',
        'nombre_cliente',
        'apellido_cliente',
        'vendedor',
        'mostrar_metodo_pago',  # <- este es el nuevo campo
        'total_con_interes',
        'cuotas',
        'cuota_mensual',
        'estado_entrega',
    )
    search_fields = ('numero_factura', 'nombre_cliente', 'apellido_cliente', 'dni_cliente')
    list_filter = ('vendedor', 'metodo_pago', 'estado_entrega', 'fecha')

    def mostrar_metodo_pago(self, obj):
        return obj.metodo_pago.tarjeta_nombre if obj.metodo_pago else obj.metodo_pago_manual or "Sin especificar"
    
    mostrar_metodo_pago.short_description = "Método de pago"


#---------------------------------------------------------------#
#admin.site.register(CuentaCorriente)
# Registro de modelos con decoradores
@admin.register(Categ_producto)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')  # Combina las opciones que necesites
    # Puedes agregar más configuraciones aquí
#---------------------------------------------------------------#
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre_producto', 'categoria', 'precio', 'stock')

#---------------------------------------------------------------#
from django.contrib import admin
from .models import MetodoPago
from django.contrib import admin
from .models import TipoPago

@admin.register(TipoPago)
class TipoPagoAdmin(admin.ModelAdmin):
    list_display = ['tipo_pago', 'alias', 'cbu', 'vista_logo']
    readonly_fields = ['vista_logo']

    def vista_logo(self, obj):
        if obj.tipo_logo:
            return f'<img src="{obj.tipo_logo.url}" width="60" height="60" style="object-fit:cover;border-radius:10%;">'
        return "Sin logo"
    vista_logo.allow_tags = True
    vista_logo.short_description = 'Logo'


#---------------------------------------------------------------#
from django.contrib import admin
from apps.CarritoApp.models import CuentaCorriente

@admin.register(CuentaCorriente)
class CuentaCorrienteAdmin(admin.ModelAdmin):
    list_display = (
        'numero_factura', 'factura', 'fecha_cuota',
        'cuota_total', 'cuota_paga', 'cuota_debe',
        'imp_mensual', 'imp_cuota_pagadas', 'entrega_cta',
        'metodo_pago_display',  # ✅ Agregado aquí
        'estado_credito_factura',  # ✅ esto es lo que ves en Factura
    )
    list_filter = ('fecha_cuota', 'metodo_pago')
    search_fields = (
        'numero_factura',
        'factura__dni_cliente',
        'factura__nombre_cliente',
        'factura__apellido_cliente',
        'metodo_pago_display',
    )

    def metodo_pago_display(self, obj):
        if obj.metodo_pago:
            return obj.metodo_pago.tarjeta_nombre
        return "Efectivo"

    metodo_pago_display.short_description = "Método Pago"

    def estado_credito_factura(self, obj):
        return obj.factura.estado_credito
    estado_credito_factura.short_description = "Estado Crédito (Factura)"

#---------------------------------------------------------------#
#---------------------------------------------------------------#
#---------------------------------------------------------------#
#---------------------------------------------------------------#
from django.contrib import admin
from .models import MetodoPago, CuotaInteres

class CuotaInteresInline(admin.TabularInline):
    model = CuotaInteres
    extra = 1
    min_num = 0
    max_num = 12

#---------------------------------------------------------------#
#---------------------------------------------------------------#
@admin.register(MetodoPago)
class MetodoPagoAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'tarjeta_nombre',
        'cantidad_cuotas',
        'porcentaje_total'
    )
    search_fields = ('tarjeta_nombre',)
    ordering = ('tarjeta_nombre',)
    list_per_page = 20
    inlines = [CuotaInteresInline]

    def cantidad_cuotas(self, obj):
        return obj.cuotas_interes.count()
    cantidad_cuotas.short_description = "Cuotas"

    def porcentaje_total(self, obj):
        cuotas = obj.cuotas_interes.all()
        return ", ".join([f"{c.cantidad_cuotas}x{c.porcentaje_interes:.2f}%" for c in cuotas]) if cuotas else "-"
    porcentaje_total.short_description = "Interés (%)"

# Registrar CuotaInteres por separado para visualizarla también desde el admin (si querés)
admin.site.register(CuotaInteres)



# -------------------------------------------------
# apps/CarritoApp/admin.py
from django.contrib import admin
from .models import MensajeCliente

@admin.register(MensajeCliente)
class MensajeClienteAdmin(admin.ModelAdmin):
    list_display = ("id", "apellido", "nombre", "pedido", "creado_en", "respondido", "activo")
    list_filter = ("respondido", "activo", "creado_en")
    search_fields = ("apellido", "nombre", "pedido", "email_contacto")

# -------------------------------------------------
from .models import ChatEstado

@admin.register(ChatEstado)
class ChatEstadoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "cliente_id",
        "nombre_cliente",
        "cleaned_sender_pn",
        "paso",
        "esperando_opcion",
        "precio_total",
        "creado_en",
    )

    list_filter = ("esperando_opcion", "paso", "creado_en")

    search_fields = (
        "cliente_id",
        "nombre_cliente",
        "cleaned_sender_pn",
        "ultimo_texto",
    )

    readonly_fields = ("creado_en", "actualizado_en")

# ----------Compra---------------------------------------
from django.contrib import admin
from .models import Compra
from django.contrib import admin
from .models import Compra


@admin.register(Compra)
class CompraAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'producto',
        'cantidad',
        'precio_compra',
        'factura_compra',
        'fecha_compra',
        'provedor',
    )

    list_filter = (
        'fecha_compra',
        'provedor',
        'producto',
    )

    search_fields = (
        'factura_compra',
        'producto__nombre_producto',
        'provedor__nombre',
    )

    ordering = ('-fecha_compra',)
    list_per_page = 25
