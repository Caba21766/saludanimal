from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.images import get_image_dimensions
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.conf import settings
from io import BytesIO
from pathlib import Path
from PIL import Image, ImageFile

ImageFile.LOAD_TRUNCATED_IMAGES = True  # evita errores con JPG "raros"
User = get_user_model()

# ====== Config de imágenes (podés mover a settings.py) ======
MAX_IMG_BYTES = getattr(settings, "USER_IMG_MAX_BYTES", 1 * 1024 * 1024)  # 1 MB final
MAX_IMG_W     = getattr(settings, "USER_IMG_MAX_W",     1024)             # límite duro p/validación
MAX_IMG_H     = getattr(settings, "USER_IMG_MAX_H",     1024)
# objetivo de avatar (rápido y liviano)
AVATAR_MAX_W  = getattr(settings, "USER_AVATAR_MAX_W",  512)
AVATAR_MAX_H  = getattr(settings, "USER_AVATAR_MAX_H",  512)
AVATAR_QUALITY = getattr(settings, "USER_AVATAR_QUALITY", 80)
ALLOWED_CTYPES = ("image/jpeg", "image/png", "image/webp")

def _optimize_image(uploaded, max_w=AVATAR_MAX_W, max_h=AVATAR_MAX_H, quality=AVATAR_QUALITY):
    """
    Redimensiona y comprime a JPEG optimizado en memoria.
    """
    # Abrimos con PIL
    img = Image.open(uploaded)
    # Normalizamos a RGB (PNG/WebP con transparencia)
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    # Reducción proporcional (thumbnail mantiene aspect ratio)
    img.thumbnail((max_w, max_h))
    # Guardamos en buffer
    buf = BytesIO()
    img.save(buf, format="JPEG", optimize=True, quality=quality)
    buf.seek(0)

    filename = Path(getattr(uploaded, "name", "avatar")).stem + ".jpg"
    optimized = InMemoryUploadedFile(
        buf, field_name="ImageField", name=filename,
        content_type="image/jpeg", size=buf.getbuffer().nbytes, charset=None
    )
    return optimized

def _validar_basica(uploaded):
    """
    Validación básica previa (tipo). Dimensiones pesadas las resuelve PIL al optimizar.
    """
    if not uploaded:
        return
    ctype = getattr(uploaded, "content_type", None)
    if ctype and ctype not in ALLOWED_CTYPES:
        raise ValidationError("Formato no permitido. Usá JPG, PNG o WebP.")

def limpiar_y_optimizar(imagen):
    """
    1) Validación básica de tipo.
    2) Optimización (resize + compresión).
    3) Validación final de tamaño.
    """
    _validar_basica(imagen)
    optimizada = _optimize_image(imagen)
    if optimizada.size > MAX_IMG_BYTES:
        mb = MAX_IMG_BYTES // (1024 * 1024)
        raise ValidationError(f"La imagen optimizada supera {mb} MB. Probá con una foto más chica.")
    return optimizada


# -------------------- REGISTRO AlTA Minima --------------------
class RegistrarseForm(UserCreationForm):
    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'dni_usuario',
            'domicilio_usuario',
            'tel1_usuario',
            'password1',
            'password2'
        ]
        # 🔹 Etiquetas visibles en el navegador
        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'dni_usuario': 'DNI',
            'domicilio_usuario': 'Domicilio',
            'tel1_usuario': 'Tel o Celular ',
            'password1': 'Contraseña',
            'password2': 'Confirmación de contraseña',
        }
        # 🔹 Placeholders / clases Bootstrap (opcional)
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingresá tu nombre'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingresá tu Apellido'}),
            'dni_usuario': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Solo números'}),
            'domicilio_usuario': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Calle y número'}),
            'tel1_usuario': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 3644 555555'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Sacar help_texts y setear labels de password por si acaso
        self.fields['password1'].help_text = ''
        self.fields['password2'].help_text = ''
        self.fields['password1'].label = 'Contraseña'
        self.fields['password2'].label = 'Confirmación de contraseña'

        # Asegurar clase en todos los widgets (incluye passwords)
        for name, f in self.fields.items():
            f.widget.attrs.setdefault('class', 'form-control')

    # --- Validaciones ---
    def clean_dni_usuario(self):
        dni = (self.cleaned_data.get("dni_usuario") or "").strip()
        if not dni.isdigit():
            raise ValidationError("El DNI debe contener solo números.")
        if User.objects.filter(dni_usuario=dni).exists():
            raise ValidationError("⚠️ Ya esta registrado este DNI.")
        return dni

    # --- Guardado ---
    def save(self, commit=True):
        """
        Crea el usuario y asegura username = DNI (para autenticación por DNI).
        """
        user = super().save(commit=False)
        dni = self.cleaned_data.get('dni_usuario') or ''
        user.username = dni
        if commit:
            user.save()
        return user

# -------------------- EDICIÓN DE PERFIL o modificacion --------------------
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

    def clean_imagen_usuario(self):
        imagen = self.cleaned_data.get('imagen_usuario')
        if imagen:
            imagen = limpiar_y_optimizar(imagen)
        return imagen

    def save(self, commit=True):
        user = super().save(commit=False)
        # Si cambian el DNI, sincronizamos username = nuevo DNI
        nuevo_dni = (self.cleaned_data.get('dni_usuario') or '').strip()
        if nuevo_dni:
            user.username = nuevo_dni
        if commit:
            user.save()
        return user


# -------------------- LOGIN POR DNI --------------------
class CustomLoginForm(AuthenticationForm):
    # Mantiene name="username" por compatibilidad, pero se rotula como DNI.
    error_messages = {
            "invalid_login": "⚠️ DNI o contraseña incorrectos.",
            "inactive": "⚠️ Esta cuenta está desactivada.",
        }

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