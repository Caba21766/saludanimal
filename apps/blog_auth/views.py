from django.http import Http404
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy
from django.views.generic import FormView, UpdateView, TemplateView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .forms import RegistrarseForm, EditarUsuarioForm, CustomLoginForm

User = get_user_model()

# ======== Helper: bloquear vistas si ya está autenticado ========
class AnonymousRequiredMixin:
    """Redirige si el usuario YA está autenticado (para register/login)."""
    redirect_url = 'index'  # cambialo si querés

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(self.redirect_url)
        return super().dispatch(request, *args, **kwargs)


# -------------------- REGISTRO --------------------
class RegistrarseView(FormView):
    template_name = 'users/registrarse.html'
    form_class = RegistrarseForm
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        """
        Tu RegistrarseForm.save() ya hace:
        - username = dni_usuario
        - guarda imagen si viene en request.FILES
        - valida tamaños
        Por eso, no hace falta reasignar campos acá.
        """
        form.save()  # guarda todo, incluyendo imagen
        messages.success(self.request, "Tu cuenta ha sido creada exitosamente.")
        return super().form_valid(form)


# -------------------- LOGIN --------------------
class IniciarSesionView(LoginView):
    template_name = 'users/iniciar_sesion.html'
    authentication_form = CustomLoginForm


# -------------------- EDICIÓN (CBV) --------------------
class EditarPerfil(LoginRequiredMixin, UpdateView):
    model = User
    form_class = EditarUsuarioForm       # <- usar form de edición, no el de registro
    template_name = 'users/editar_usuario.html'
    success_url = reverse_lazy('index')

    def get_object(self, queryset=None):
        """
        Edita SIEMPRE el usuario logueado.
        Si además pasás pk en la URL, podés validar que coincida.
        """
        obj = get_object_or_404(User, pk=self.request.user.pk)
        # Si viene pk en la ruta, validamos que coincida:
        url_pk = self.kwargs.get('pk')
        if url_pk and str(url_pk) != str(self.request.user.pk):
            raise Http404("No tienes permiso para editar este perfil.")
        return obj

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Perfil actualizado correctamente.")
        return super().form_valid(form)


# -------------------- EDICIÓN (FBV alternativa) --------------------
# Si preferís función en lugar de la CBV de arriba, dejá ESTA y borra EditarPerfil.
@login_required
def editar_usuario(request, pk):
    if str(pk) != str(request.user.pk):
        raise Http404("No tienes permiso para editar este perfil.")
    usuario = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = EditarUsuarioForm(request.POST, request.FILES, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil actualizado correctamente.")
            return redirect('apps.blog_auth:perfil')
    else:
        form = EditarUsuarioForm(instance=usuario)
    return render(request, 'users/editar_usuario.html', {'form': form})


# -------------------- VARIOS --------------------
def perfil_view(request):
    return render(request, 'users/perfil.html', {'user': request.user})


def pedir_con_view(request):
    return render(request, 'users/pedir_con.html')


def lista_usuarios(request):
    usuarios = User.objects.all()
    return render(request, 'users/lista_usuarios.html', {'usuarios': usuarios})


class TuVista(TemplateView):
    template_name = 'tu_template.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context


# -------------------- editar usuario admin --------------------
from django.http import Http404
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model

from .forms import EditarUsuarioForm

User = get_user_model()


@login_required
def edit_usuario_admin(request, pk):
    # ✅ Solo staff/admin
    if not request.user.is_staff:
        raise Http404("No tienes permiso para acceder a esta página.")

    usuario = get_object_or_404(User, pk=pk)

    if request.method == "POST":
        form = EditarUsuarioForm(request.POST, request.FILES, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, f"Usuario {usuario.username} actualizado correctamente.")
            return redirect("apps.blog_auth:lista_usuarios")
    else:
        form = EditarUsuarioForm(instance=usuario)

    # ✅ IMPORTANTE: si tu template está en templates/editar_usuario.html (sin carpeta users)
    # cambiá a 'editar_usuario.html'
    return render(request, "users/editar_usuario.html", {"form": form, "usuario": usuario})




from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

from .forms import EditarUsuarioForm

User = get_user_model()

@login_required
def editar_usuario_turnos(request):
    """
    Edita el usuario encontrado en Turnos (guardado en session['turno_wizard']['user_id']).
    """
    wiz = request.session.get("turno_wizard", {})
    user_id = wiz.get("user_id")

    if not user_id:
        messages.error(request, "Primero ingresá el DNI y presioná Aceptar para cargar el titular.")
        return redirect("turnos:paso1_dni")

    usuario = get_object_or_404(User, pk=user_id)

    if request.method == "POST":
        form = EditarUsuarioForm(request.POST, request.FILES, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Datos actualizados correctamente.")
            return redirect("turnos:paso1_dni")
    else:
        # ✅ ESTO precarga los datos
        form = EditarUsuarioForm(instance=usuario)

    return render(request, "users/editar_usuario.html", {
        "form": form,
        "usuario": usuario,
        "desde_turnos": True,
    })
