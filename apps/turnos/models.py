from django.db import models
from django.utils import timezone
import uuid

class Motivo(models.Model):
    nombre = models.CharField(max_length=140)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # ✅ NUEVO
    activo = models.BooleanField(default=True)
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["orden", "nombre"]

    def __str__(self):
        return self.nombre




class Oficina(models.Model):
    nombre = models.CharField(max_length=160)
    direccion = models.CharField(max_length=200, blank=True)
    ciudad = models.CharField(max_length=120, blank=True)
    provincia = models.CharField(max_length=120, blank=True)
    activo = models.BooleanField(default=True)
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["orden", "nombre"]

    def __str__(self):
        return self.nombre


class Turno(models.Model):
    ESTADOS = (
        ("RESERVADO", "Reservado"),
        ("CANCELADO", "Cancelado"),
        ("ATENDIDO", "Atendido"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dni = models.CharField(max_length=11, db_index=True)

    motivo = models.ForeignKey(Motivo, on_delete=models.PROTECT, related_name="turnos")
    oficina = models.ForeignKey(Oficina, on_delete=models.PROTECT, related_name="turnos", null=True, blank=True)

    fecha = models.DateField(db_index=True)
    hora = models.TimeField(db_index=True)

    estado = models.CharField(max_length=10, choices=ESTADOS, default="RESERVADO", db_index=True)

    creado_en = models.DateTimeField(default=timezone.now)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["fecha", "hora"]),
            models.Index(fields=["oficina", "fecha"]),
        ]

    def __str__(self):
        return f"{self.dni} - {self.fecha} {self.hora} - {self.motivo}"
