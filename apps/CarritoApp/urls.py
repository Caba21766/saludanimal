from django.urls import path
from . import views
from apps.CarritoApp.views import imprimir_caja, obtener_stock
from .views import vista_resumen_factura
from .views import pago_exitoso, pago_fallo, pago_pendiente
from . import views as vm   

# Importa las vistas correctas

app_name = 'CarritoApp'  # Especificar el espacio de nombres para las rutas
# Define las URLs de la app
urlpatterns = [
    #---------------------------------------------------------------------------------------------
    #path('listado_compra/', views.listado_compra, name='listado_compra'), 
    path('agregar_categoria/', views.agregar_categoria, name='agregar_categoria'),
    path('agregar_producto/', views.agregar_o_modificar_producto, name='agregar_producto'),
    path('modificar_producto/<int:pk>/', views.agregar_o_modificar_producto, name='modificar_producto'),
    path('eliminar_producto/<int:pk>/', views.eliminar_producto, name='eliminar_producto'),
    path('agregar-provedor/', views.agregar_provedor, name='agregar_provedor'),
    path('agregar-compra/', views.agregar_compra, name='agregar_compra'),
    path('agregar_compra/', views.agregar_compra, name='agregar_compra'),
    path('modificar_compra/<int:pk>/', views.modificar_compra, name='modificar_compra'),
    path('eliminar_compra/<int:pk>/', views.eliminar_compra, name='eliminar_compra'),
    path('realizar_venta/', views.realizar_venta, name='realizar_venta'),
    path('listar_ventas/', views.listar_ventas, name='listar_ventas'),
    path('tienda/', views.tienda, name='tienda'),
    path('agregar/<int:producto_id>/', views.agregar_al_carrito, name='Add'),
    path('restar/<int:producto_id>/', views.restar_del_carrito, name='Sub'),
    path('limpiar/', views.limpiar_carrito, name='limpiar_carrito'),
    path('guardar_factura/', views.guardar_factura, name='guardar_factura'),
    
    path('detalle_factura/<int:factura_id>/', views.detalle_factura, name='detalle_factura'),
    path('lista-vendedor/', views.lista_vendedor, name='lista_vendedor'),
    path('factura/<int:factura_id>/pdf/', views.generar_pdf_factura, name='generar_pdf_factura'),
    path('mis_facturas/', views.facturas_usuario, name='mis_facturas'),  # Vista para usuario a
    path('subir_imagen_factura/<int:factura_id>/', views.subir_imagen_factura, name='subir_imagen_factura'),
    path('eliminar_imagen_factura/<int:factura_id>/', views.eliminar_imagen_factura, name='eliminar_imagen_factura'),
    path('levantar_imagen_usuario/<int:pk>/', views.levantar_imagen_usuario, name='levantar_imagen_usuario'),
    path('mis_facturas/', views.facturas_usuario, name='facturas_usuario'),
    path('actualizar_precios/', views.actualizar_precios, name='actualizar_precios'),
    
    path('agregar-al-carrito/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),


    path('listar_facturas/', views.lista_cierre_de_caja, name='listar_facturas'),
    path('cierre_de_caja/', views.lista_cierre_de_caja, name='cierre_de_caja'),

    #-------------------- todo sobre CARRITO LIMPIAR - MOSTRAR CARRITO
    path('carrito/', views.ver_carrito, name='ver_carrito'),  # Esta es la vista que muestra el carrito
    path('carrito/', views.carrito, name='carrito'),  # Esta es la vista por stock negativo
    path('limpiar/', views.limpiar_carrito, name='limpiar_carrito'),  # Limpiar carrito
    path('sumar/<int:producto_id>/', views.sumar_producto, name='sumar_producto'),
    
    path('', views.vista_productos, name='vista_productos'),
    path('modificar_compra/<int:pk>/', views.modificar_compra, name='modificar_compra'),
    path('balance-total/', views.balance_total, name='balance_total'),
    path('balance-ganancia/', views.balance_ganancia, name='balance_ganancia'),
    path('modificacion-stock/', views.modificacion_stock, name='modificacion_stock'),
    path('modificar-stock/<int:pk>/', views.modificar_stock, name='modificar_stock'),
    path('movimiento-cliente/', views.movimiento_cliente, name='movimiento_cliente'),
    path('productos-vendidos/', views.productos_vendidos, name='productos_vendidos'),
    path('carrito/', views.carrito, name='carrito'),
    path('api/productos/', views.obtener_producto, name='obtener_productos'),
    path('api/obtener-nombre-producto/', views.obtener_nombre_producto, name='obtener_nombre_producto'),
    path('api/obtener-numero-producto/', views.obtener_numero_producto, name='obtener_numero_producto'),
    path('buscar_productos/', views.buscar_productos, name='buscar_productos'),
    path('obtener-producto/', views.obtener_producto, name='obtener_producto'),
    path('planilla_compra/', views.planilla_compra, name='planilla_compra'),
    path('api/obtener-stock/', obtener_stock, name='obtener_stock'),

#------------------------es para la mostra la factura en pdf--------------------
    path('mostrar_carrito_factura/<int:factura_id>/', views.mostrar_carrito_factura, name='mostrar_carrito_factura'),
    path('caja/imprimir/', imprimir_caja, name='imprimir_caja'),
#------------------------es para la mostra la factura en pdf en el celular--------------------
    
    path('factura/<int:factura_id>/resumen/', vista_resumen_factura, name='resumen_factura'),
    path('factura/<int:factura_id>/resumen/', views.vista_resumen_factura, name='resumen_factura'),

# ------------------------ Pago con Mercado Pago ------------------------
    path('pago/exito/', views.pago_exitoso, name='pago_exitoso'),
    path('pago/fallo/', views.pago_fallido, name='pago_fallo'),
    path('pago/pendiente/', views.pago_pendiente, name='pago_pendiente'),
    path('pago_fallido/', views.pago_fallido, name='pago_fallido'),  # ⚠️ si lo estás usando en otra parte

    # Si usás otra vista para efectivo:
    path('guardar_factura/', views.guardar_factura, name='guardar_factura'),
    path('guardar_efectivo/', views.guardar_efectivo, name='guardar_efectivo'),
    path('factura/<int:factura_id>/', views.vista_resumen_factura, name='vista_resumen_factura'),


    path('tipo-pago/', views.tipo_pago_list, name='tipo_pago_list'),
    path('tipo-pago/nuevo/', views.tipo_pago_create, name='tipo_pago_create'),  # 👈 ESTA LÍNEA
    path('resumen-factura/<int:factura_id>/', vista_resumen_factura, name='resumen_factura'),
    path('factura/<int:factura_id>/estado/', views.actualizar_estado_entrega, name='actualizar_estado_entrega'),
    path('lista-cuenta-corriente/', views.lista_cuenta_corriente, name='lista_cuenta_corriente'),
    path('factura/<int:factura_id>/cuenta-corriente/', views.pagos_cuenta_corriente, name='pagos_cuenta_corriente'),
    path('factura/<int:factura_id>/', views.vista_resumen_factura, name='detalle_factura'),


    # ✅ Checkout Pro de Mercado Pago
    path('mercadopago/checkout/', views.mp_checkout, name='mp_checkout'),
    path('mercadopago/webhook/', views.mp_webhook, name='mp_webhook'),

    # back_urls de Mercado Pago (ya están bien así)
    path('pago/exito/', views.pago_exitoso, name='pago_exitoso'),
    path('pago/pendiente/', views.pago_pendiente, name='pago_pendiente'),
    path('pago/fallo/', views.pago_fallido, name='pago_fallo'),

    # apps/CarritoApp/urls.py
    path('compra/agregar/', views.agregar_compra, name='agregar_compra'),
    

    # MENSAJES... tus rutas previas
    path("mensajes/enviar/", vm.crear_mensaje, name="crear_mensaje"),
    path("admin/mensajes/", vm.lista_mensajes, name="mensajes_admin"),
    path("admin/mensajes/<int:pk>/responder/", vm.responder_mensaje, name="responder_mensaje"),
    path("admin/mensajes/<int:pk>/eliminar/", vm.eliminar_mensaje, name="eliminar_mensaje"),

    path("mis-mensajes/", vm.mis_mensajes, name="mis_mensajes"),

    path('lista-vendedor/', lambda r: redirect(reverse('CarritoApp:listar_facturas')), name='lista_vendedor'),
    path('listar_facturas/', views.lista_cierre_de_caja, name='listar_facturas'),

    path('pago/<int:pago_id>/imagen/subir/', views.subir_imagen_pago, name='subir_imagen_pago'),
    path('pago/<int:pago_id>/imagen/eliminar/', views.eliminar_imagen_pago, name='eliminar_imagen_pago'),

   
    path(
        "facturas/<int:factura_id>/estado/", views.actualizar_estado_entrega, name="actualizar_estado_entrega",
    ),


]
#---------------------------------------------------------------------------------------------
         

