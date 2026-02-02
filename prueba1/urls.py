from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from . import views
from .views import HomeView
from .views import tienda 
from apps.CarritoApp.views import tienda
from apps.CarritoApp import views as carrito_views

from django.contrib.sitemaps.views import sitemap
from .sitemaps import StaticViewSitemap

sitemaps = {
    "static": StaticViewSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", tienda, name='index'),
    path('tienda/', views.tienda, name='tienda'),

    path('carrito/', carrito_views.ver_carrito, name='ver_carrito'),
    path('', include("apps.CarritoApp.urls")),

    path('users/', include('apps.blog_auth.urls')),
    #path('formulario/', views.contacto_view, name='formulario'),
    path('gracias/', views.gracias_view, name='gracias'),
    path('nosotros/', views.nosotros_view, name='nosotros'),
    #path('curriculom/', views.curriculom_view, name='curriculom'),
    
    path('opiniones/', include('apps.opiniones.urls')),
    path('modulo1/', include('apps.modulo1.urls')),  # Ruta principal
    path('libros/', include('apps.libros.urls')),  # Ruta principal
    path('mascotas/', include('apps.mascota.urls')),
    path('usuarios/', include(('apps.blog_auth.urls', 'blog_auth'), namespace='blog_auth')),
    path('respaldos/', include(('apps.backup.urls', 'backup'), namespace='backup')),
   

    path("turnos/", include("apps.turnos.urls")),

    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
    path("robots.txt", views.robots_txt, name="robots_txt"),
   
]
if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
