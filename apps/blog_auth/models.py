from django.contrib.auth.models import User
from django.db import models

# Agregar campos adicionales al modelo User sin reemplazarlo
User.add_to_class('dni_usuario', models.CharField(max_length=20, blank=True, null=True, verbose_name="DNI"))
User.add_to_class('domicilio_usuario', models.CharField(max_length=255, blank=True, null=True, verbose_name="Domicilio"))
User.add_to_class('tel1_usuario', models.CharField(max_length=15, blank=True, null=True, verbose_name="Teléfono 1"))
User.add_to_class('tel2_usuario', models.CharField(max_length=15, blank=True, null=True, verbose_name="Teléfono 2"))
User.add_to_class('cuil', models.CharField(max_length=13, blank=True, null=True, verbose_name="CUIL"))

# Agregar imagen de usuario
User.add_to_class('imagen_usuario', models.ImageField(upload_to='usuarios/', blank=True, null=True, verbose_name="Imagen"))

# Opciones de IVA
TIPO_IVA_CHOICES = [
    ('RI', 'Responsable Inscripto'),
    ('M', 'Monotributista'),
    ('CF', 'Consumidor Final'),
    ('EX', 'Exento'),
]

User.add_to_class('iva', models.CharField(max_length=2, choices=TIPO_IVA_CHOICES, blank=True, null=True, verbose_name="IVA"))