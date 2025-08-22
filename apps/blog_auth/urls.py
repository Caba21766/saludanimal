# apps/blog_auth/urls.py
from django.urls import path
from .views import RegistrarseView, EditarPerfil, IniciarSesionView  # <-- importa tu clase
from . import views

app_name = 'apps.blog_auth'

urlpatterns = [
    path("registrarse/", RegistrarseView.as_view(), name='registrarse'),

    # USAR tu clase, no LoginView directo
    path("iniciar_sesion/", IniciarSesionView.as_view(), name='iniciar_sesion'),

    path("cerrar_sesion/", views.LogoutView.as_view(), name='cerrar_sesion'),
    path('perfil/', views.perfil_view, name='perfil'),
    path('pedir_con/', views.pedir_con_view, name='pedir_con'),
    path("editar_perfil/<int:pk>", EditarPerfil.as_view(), name='editar_perfil'),
    path('editar/<int:pk>/', views.editar_usuario, name='editar_usuario'),
    path('', views.lista_usuarios, name='lista_usuarios'),
    path('lista/', views.lista_usuarios, name='lista_usuarios'),
]
