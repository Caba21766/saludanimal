from . import views
from django.urls import path
from django.urls import path
from .views import mostrar_factura_con_botones
from .views import registrar_credito
from apps.modulo1.views import forma_pago, prueba
from apps.modulo1.urls import forma_pago
from .views import vista_prueba_pdf
from .views import generar_factura_pdf
from apps.modulo1.views import generar_factura_pdf

app_name = 'modulo1'
urlpatterns = [
    # Rutas relacionadas con facturas
    path('crear_factura/', views.crear_factura, name='crear_factura'), 
    path('lista_facturas/', views.lista_facturas, name='lista_facturas'), 
    path('factura/<int:factura_id>/pdf/', views.generar_facturaprueba_pdf, name='generar_factura_pdf'), 
    #path('prueba/', views.prueba, name='prueba'),
    # Rutas relacionadas con mercadería
    path('buscar-mercaderia/', views.buscar_mercaderia, name='buscar_mercaderia'), 
    path('guardar-prueba/', views.guardar_prueba, name='guardar_prueba'),
    path('factura/<int:factura_id>/mostrar/', views.mostrar_factura_con_botones, name='mostrar_factura_con_botones'),
    path('factura/<int:factura_id>/pdf/', views.mostrar_factura_con_botones, name='generar_factura_pdf'),
    path('prueba/', views.prueba, name='ruta_del_formulario_principal'),
    path('factura/<int:factura_id>/pdf/', mostrar_factura_con_botones, name='facturaprueba_pdf'),
    path('registrar-credito/<int:factura_id>/', registrar_credito, name='registrar_credito'),  
    path('factura/<int:factura_id>/mostrar/', mostrar_factura_con_botones, name='mostrar_factura_con_botones'),
    path('ruta_de_lista/', views.listar_ctacorriente, name='listar_ctacorriente'),
    path('prueba/', forma_pago, name="prueba"),
    path("prueba/", prueba, name="prueba"),
    path('forma-pago/', forma_pago, name="forma_pago"),
    path('forma-pago/', views.forma_pago, name='forma_pago'),
    path('prueba/', views.prueba, name='prueba'),
    path('agregar_metodo_pago/', views.agregar_metodo_pago, name='agregar_metodo_pago'),
    path('eliminar_metodo_pago/<int:metodo_id>/', views.eliminar_metodo_pago, name='eliminar_metodo_pago'),
    path('factura/<int:factura_id>/pdf/', views.generar_facturaprueba_pdf, name='generar_factura_pdf_directo'),
    #path('factura/<int:factura_id>/pdf/', generar_factura_pdf, name='ver_factura_pdf'),
    path('factura/pdf_directo/<int:factura_id>/', generar_factura_pdf, name='factura_pdf_directo'),
    path('metodo-pago/editar/<int:metodo_id>/', views.editar_metodo_pago, name='editar_metodo_pago'),
    path('asignar_cuotas/<int:metodo_id>/', views.asignar_cuotas, name='asignar_cuotas'),
    path('eliminar_cuota/<int:cuota_id>/', views.eliminar_cuota, name='eliminar_cuota'),
    #path('agregar_metodo_pago/', views.agregar_metodo_pago, name='agregar_metodo_pago'),
    path('api/cuotas/<str:tarjeta_nombre>/', views.obtener_cuotas_tarjeta, name='cuotas_tarjeta'),
    path('prueba/', views.prueba, name='vista_prueba'),
    path('api/buscar-clientes/', views.buscar_clientes, name='buscar_clientes'),
]

 

    
    
 