from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()

# -------------------- REGISTRO --------------------
class RegistrarseForm(UserCreationForm):
    cuil = forms.CharField(max_length=13, required=True, label="CUIL")
    iva = forms.ChoiceField(choices=User._meta.get_field('iva').choices, required=True, label="Condición de IVA")
    imagen_usuario = forms.ImageField(required=False, label="Imagen de Perfil")

    class Meta:
        model = User
        # No incluimos 'username'; lo generamos con el DNI
        fields = [
            'first_name', 'last_name', 'email',
            'dni_usuario', 'domicilio_usuario', 'tel1_usuario', 'tel2_usuario',
            'cuil', 'iva', 'imagen_usuario',
            'password1', 'password2'
        ]

    # --- Validaciones ---
    def clean_dni_usuario(self):
        dni = (self.cleaned_data.get("dni_usuario") or "").strip()
        if not dni.isdigit():
            raise ValidationError("El DNI debe contener solo números.")
        if User.objects.filter(dni_usuario=dni).exists():
            raise ValidationError("⚠️ Ya existe un usuario registrado con este DNI.")
        return dni

    def clean_imagen_usuario(self):
        imagen = self.cleaned_data.get('imagen_usuario')
        if imagen:
            if imagen.size > 500 * 1024:  # 500 KB
                raise ValidationError("La imagen no puede pesar más de 500 KB.")
            try:
                width, height = imagen.image.size
                if width > 1024 or height > 768:
                    raise ValidationError("La imagen no puede superar 1024 x 768 píxeles.")
            except AttributeError:
                raise ValidationError("No se pudo verificar la resolución de la imagen.")
        return imagen

    # --- Guardado ---
    def save(self, commit=True):
        """
        Crea el usuario y asegura username = DNI (requisito de auth.User).
        """
        user = super().save(commit=False)
        dni = self.cleaned_data.get('dni_usuario') or ''
        user.username = dni  # evita "Column 'username' cannot be null"
        if commit:
            user.save()
        return user


# -------------------- EDICIÓN DE PERFIL --------------------
class EditarUsuarioForm(forms.ModelForm):
    imagen_usuario = forms.ImageField(required=False, label="Imagen de Perfil")

    class Meta:
        model = User
        # No permitimos editar 'username' directamente
        fields = [
            'first_name', 'last_name', 'email', 'dni_usuario',
            'domicilio_usuario', 'tel1_usuario', 'tel2_usuario',
            'cuil', 'iva', 'imagen_usuario'
        ]

    def save(self, commit=True):
        user = super().save(commit=False)
        # Si cambian el DNI, sincronizamos username = nuevo DNI
        nuevo_dni = self.cleaned_data.get('dni_usuario')
        if nuevo_dni:
            user.username = nuevo_dni
        if commit:
            user.save()
        return user


# -------------------- LOGIN POR DNI --------------------
class CustomLoginForm(AuthenticationForm):
    # Mantiene name="username" por compatibilidad, pero se rotula como DNI.
    username = forms.CharField(
        label="DNI",
        widget=forms.TextInput(attrs={
            'autocomplete': 'off',
            'class': 'form-control',
            'placeholder': 'Ingresá tu DNI (solo números)',
            'id': 'dni',
        })
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'current-password',
            'class': 'form-control',
            'placeholder': 'Contraseña',
            'id': 'password',
        })
    )
