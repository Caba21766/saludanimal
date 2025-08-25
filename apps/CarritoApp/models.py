#--------------Categoria-------------------------------------------------#
from django.db import models
class Categ_producto(models.Model):  # Este es el modelo de categorías
    nombre = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.nombre
    
#---------------------------------------------------------------#
#-------------------Proveedor--------------------------------------------#
from django.db import models
class Provedor(models.Model):
    nombre = models.CharField(max_length=100)
    direccion = models.TextField(blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)  # Teléfono
    email = models.EmailField(blank=True, null=True)  # Correo electrónico

    def __str__(self):
        return self.nombre

#---------------------------------------------------------------#
#--------------Producto-------------------------------------------------#
from .models import Categ_producto 

class Producto(models.Model):
    numero_producto = models.PositiveIntegerField(unique=True, null=True, blank=True) 

    nombre_producto = models.CharField(max_length=255, default="Nombre del producto")
    descripcion = models.TextField(default="Sin descripción")
    imagen = models.ImageField(upload_to='productos/', blank=False, null=False)
    categoria = models.ForeignKey(Categ_producto, on_delete=models.CASCADE,
    related_name='productos', default=1  # Cambia '1' por el ID de tu categoría predeterminada
)
    stock = models.PositiveIntegerField(default=0)
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, blank=False, null=False)

    # Imágenes adicionales
    imagen2 = models.ImageField(upload_to='productos/', null=True, blank=True)
    imagen3 = models.ImageField(upload_to='productos/', null=True, blank=True)
    imagen4 = models.ImageField(upload_to='productos/', null=True, blank=True)
    imagen5 = models.ImageField(upload_to='productos/', null=True, blank=True)

    def __str__(self):
        return self.nombre_producto

#---------------------------------------------------------------#
#----------------Compra----------------------------------------------#
class Compra(models.Model):
    
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2)
    factura_compra = models.CharField(max_length=100)
    fecha_compra = models.DateField()
    provedor = models.ForeignKey('Provedor', on_delete=models.SET_NULL, null=True)

    def save(self, *args, **kwargs):
        # Obtén el producto relacionado
        producto = self.producto
        if self.pk is None:  # Si es una nueva compra
            producto.stock += self.cantidad  # Suma la cantidad al stock actual
        else:
            # Si se actualiza una compra existente, ajusta el stock
            compra_original = Compra.objects.get(pk=self.pk)
            diferencia = self.cantidad - compra_original.cantidad
            producto.stock += diferencia

        producto.save()  # Guarda los cambios en el producto
        super().save(*args, **kwargs)  # Guarda la compra

#---------------------------------------------------------------#
#-----------------Venta----------------------------------------------#
from django.db import models
from django.contrib.auth.models import User
class Venta(models.Model):
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=False, default=1)
    fecha = models.DateTimeField(auto_now_add=True)  # Cambiado a DateTimeField

#---------------------------------------------------------------#
from django.db import models
import uuid
from django.conf import settings  # si no está arriba
class Factura(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    id = models.AutoField(primary_key=True)
    numero_factura = models.CharField(max_length=10)
    fecha = models.DateField()
    nombre_cliente = models.CharField(max_length=255)
    apellido_cliente = models.CharField(max_length=255)
    domicilio = models.CharField(max_length=255, blank=True, null=True)  # ✅ Permite nulo
    cuil = models.CharField(max_length=20, blank=True, null=True)  # Nuevo campo
    iva = models.CharField(max_length=50, blank=True, null=True)  # Nuevo campo
   
    # ✅ Modificación en el campo `metodo_pago`
    metodo_pago = models.ForeignKey(
    'MetodoPago',
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='facturas',
    verbose_name="Método de pago"
)
    metodo_pago_manual = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Método de pago (manual)"
    )

    total = models.DecimalField(max_digits=10, decimal_places=2)
    detalle_productos = models.TextField(default="Sin detalles")
    imagen_factura = models.ImageField(upload_to='factura_images/', null=True, blank=True)
    #---------------------------------------------------------------#
    dni_cliente = models.CharField(max_length=20, null=True, blank=True)
    vendedor = models.CharField(max_length=100, default='Sin asignar')
    descuento = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    total_descuento = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    estado_credito = models.CharField(max_length=50, default='Cuenta Corriente')
    
    interes = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    #---------------------------------------------------------------#
    total_con_interes = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    #---------------------------------------------------------------#
    cuotas = models.IntegerField(default=0)
    #---------------------------------------------------------------#
    cuota_mensual = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    # ✅ Nuevos campos para tarjetas
    tarjeta_nombre = models.CharField(max_length=50, blank=True, null=True)  # Nombre de la tarjeta
    tarjeta_numero = models.CharField(max_length=20, blank=True, null=True)  # Número de tarjeta
    numero_tiket = models.CharField(max_length=50, blank=True, null=True)  # Número de ticket
    ESTADO_ENTREGA = [
    ('pendiente', 'Pendiente'),
    ('aceptado', 'Aceptado'),
    ('rechazado', 'Rechazado'),
    ]

    estado_entrega = models.CharField(
        max_length=10,
        choices=ESTADO_ENTREGA,
        default='pendiente',
        verbose_name="Estado de entrega"
    )
    def __str__(self):
        return f"Factura {self.numero_factura} - {self.nombre_cliente} {self.apellido_cliente}"

    @property
    def estado_credito_real(self):
        from django.db.models import Sum
        from decimal import Decimal

        pagos = self.cuenta_corriente.aggregate(
            total_cuotas=Sum('imp_cuota_pagadas'),
            total_entregas=Sum('entrega_cta')
        )
        total_cuotas = pagos['total_cuotas'] or Decimal(0)
        total_entregas = pagos['total_entregas'] or Decimal(0)
        total_pagado = total_cuotas + total_entregas
        return "Pagado" if total_pagado >= self.total_con_interes else "Pendiente"


#-------------esta parte del codigo no se si sirve---------------------#
class FacturaProducto(models.Model):
    factura = models.ForeignKey(Factura, on_delete=models.CASCADE)  # Relación con Factura
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE)  # Relación con Producto
    cantidad = models.PositiveIntegerField()  # Cantidad vendida de este producto
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)  # Subtotal por producto

    def __str__(self):
        return f"{self.producto.nombre_producto} x {self.cantidad} en {self.factura.numero_factura}"

def generar_numero_factura():
        ultima_factura = Factura.objects.all().order_by('id').last()
        if ultima_factura:
            ultimo_numero = int(ultima_factura.numero_factura)
            nuevo_numero = f"{ultimo_numero + 1:05d}"
        else:
            nuevo_numero = "00001"
        return nuevo_numero


#----------------------es de la tarjetas para cargar cuotas--------------------#
class MetodoPago(models.Model):
    tarjeta_nombre = models.CharField(max_length=100, unique=True)
    tarjeta_cuota = models.IntegerField(default=0)
    tarjeta_porcentaje = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.tarjeta_nombre}"
        
#------------------------------------------#
class CuotaInteres(models.Model):
    metodo_pago = models.ForeignKey(MetodoPago, on_delete=models.CASCADE, related_name='cuotas_interes')
    cantidad_cuotas = models.IntegerField()
    porcentaje_interes = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"{self.metodo_pago.tarjeta_nombre} - {self.cantidad_cuotas} cuotas - {self.porcentaje_interes}%"

#-----------------Cuenta Corrientes----------------------------------------------#
from decimal import Decimal
class CuentaCorriente(models.Model):
    factura = models.ForeignKey(Factura, on_delete=models.CASCADE, related_name="cuenta_corriente")
    numero_factura = models.CharField(max_length=10)
    descripcion = models.TextField()  
    fecha_cuota = models.DateField()
    total_con_interes = models.DecimalField(max_digits=10, decimal_places=2)  
    cuota_total = models.IntegerField(default=0)  
    cuota_paga = models.IntegerField(default=0)  
    cuota_debe = models.IntegerField(default=0)  # 🔹
    cuota_suma = models.IntegerField(default=0)  # 🔹
    imp_mensual = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal(0))
    imp_cuota_pagadas = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal(0))  
    entrega_cta = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal(0))  
    metodo_pago = models.ForeignKey(MetodoPago, on_delete=models.SET_NULL, null=True, blank=True)
    tarjeta_nombre = models.CharField(max_length=255, blank=True, null=True)
    tarjeta_numero = models.CharField(max_length=20, blank=True, null=True)
    interes_aplicado = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal(0))
    imagen_pago = models.ImageField(upload_to="pago_images/", blank=True, null=True)

    def __str__(self):
        return f"Cuenta Corriente - Factura {self.numero_factura} - Estado: {self.estado_credito} - Pago: {self.metodo_pago}"

    @property
    def estado_credito(self):
        return "Pagado" if self.cuota_debe == 0 else "Pendiente"

    @property
    def metodo_pago_display(self):
        if self.metodo_pago:
            partes = []

            # Nombre de la tarjeta o tipo de pago
            tarjeta_nombre = getattr(self.metodo_pago, 'tarjeta_nombre', '')
            alias = getattr(self.metodo_pago, 'alias', '')
            tipo_pago = getattr(self.metodo_pago, 'tipo_pago', '')

            if tarjeta_nombre:
                partes.append(tarjeta_nombre)
            elif tipo_pago:
                partes.append(tipo_pago)

            # Número de tarjeta (últimos 4 dígitos)
            if self.tarjeta_numero:
                partes.append(f"Nro: ****{self.tarjeta_numero[-4:]}")

            # Alias si existe
            if alias:
                partes.append(f"Alias: {alias}")

            return " - ".join(partes)

        return "Efectivo"

#-----------------tarjeta es para online o sea el carrito-----------------------------#

from django.db import models

class TipoPago(models.Model):
    tipo_pago = models.CharField(max_length=50)
    tipo_logo = models.ImageField(upload_to='logos_pago/')
    alias = models.CharField(max_length=100, blank=True, null=True)
    cbu = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.tipo_pago


#----------------Mensajes al Administrador-----------------------------#

# apps/CarritoApp/models.py
from django.db import models
from django.conf import settings

class MensajeCliente(models.Model):
    # ID autoincremental (id) lo crea Django
    apellido = models.CharField(max_length=80)
    nombre = models.CharField(max_length=80)
    pedido = models.CharField("Mensaje / Pedido", max_length=255)
    email_contacto = models.EmailField(blank=True, null=True)  # opcional, por si querés responder por mail
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        related_name="mensajes_enviados", null=True, blank=True
    )
    creado_en = models.DateTimeField(auto_now_add=True)

    # Respuesta del admin
    respondido = models.BooleanField(default=False)
    respuesta = models.TextField(blank=True, null=True)
    respondido_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        related_name="mensajes_respondidos", null=True, blank=True
    )
    respondido_en = models.DateTimeField(null=True, blank=True)

    # “Eliminado” lógico para no perder historial
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ["-creado_en"]

    def __str__(self):
        return f"{self.id} - {self.apellido}, {self.nombre}"
