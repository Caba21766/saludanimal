from django import forms
from django.utils import timezone
from datetime import timedelta
import re
from .models import Motivo, Oficina
from django.core.exceptions import ValidationError

class DniForm(forms.Form):
    dni = forms.CharField(
        label="Número de DNI",
        max_length=8,
        widget=forms.TextInput(attrs={
            "class": "form-control form-control-lg",
            "inputmode": "numeric",
            "maxlength": "8",
            "pattern": r"\d{8}",
            "placeholder": "Documento",
        })
    )

    def clean_dni(self):
        dni = self.cleaned_data["dni"]
        dni = "".join(ch for ch in str(dni) if ch.isdigit())
        if len(dni) != 8:
            raise ValidationError("El DNI debe tener 8 dígitos.")
        return dni


class MotivoChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        # podés cambiar formato si querés
        return f"{obj.nombre} — ${int(obj.precio)}"

class MotivoForm(forms.Form):
    motivo = MotivoChoiceField(
        queryset=Motivo.objects.filter(activo=True).order_by("orden", "nombre"),
        empty_label=None,
        widget=forms.RadioSelect
    )

class OficinaForm(forms.Form):
    oficina = forms.ModelChoiceField(
        label="Seleccioná la oficina",
        queryset=Oficina.objects.filter(activo=True).order_by("orden", "nombre"),
        empty_label=None,
        widget=forms.RadioSelect
    )

class FechaRangoForm(forms.Form):
    # Solo para validar fecha elegida en rango
    fecha = forms.DateField()

    def __init__(self, *args, **kwargs):
        self.dias_hacia_adelante = kwargs.pop("dias_hacia_adelante", 30)
        super().__init__(*args, **kwargs)

    def clean_fecha(self):
        f = self.cleaned_data["fecha"]
        hoy = timezone.localdate()
        maximo = hoy + timedelta(days=self.dias_hacia_adelante)

        if f < hoy:
            raise forms.ValidationError("La fecha no puede ser anterior a hoy.")
        if f > maximo:
            raise forms.ValidationError("La fecha elegida está fuera del rango permitido.")
        return f
