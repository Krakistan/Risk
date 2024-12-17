from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth import views as auth_views
from risco import views as pagweb_views
from risco import views
from .forms import CustomAuthenticationForm
from risco.views import CustomPasswordResetView, CustomPasswordResetConfirmView, agregar_producto, confirmacion, despacho, eliminar_producto_carrito

urlpatterns = [
    # Página principal
    path('', views.html, name='html'),  

    # Autenticación
    path('iniciar-sesion/', auth_views.LoginView.as_view(
        template_name='risco/iniciar_sesion.html',
        authentication_form=CustomAuthenticationForm,
        redirect_authenticated_user=True,
    ), name='iniciar_sesion'),
    path('cerrar-sesion/', auth_views.LogoutView.as_view(next_page='iniciar_sesion'), name='cerrar_sesion'),
    path('registro/', pagweb_views.registro, name='registro'),

    # Recuperación de contraseñas
    path('password_reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password_reset_confirm/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password_reset_complete/', auth_views.PasswordResetCompleteView.as_view(template_name='risco/password_reset_complete.html'), name='password_reset_complete'),

    # Páginas principales
    path('home/', views.home, name='home'),
    path('nosotros/', views.nosotros, name='nosotros'),
    path('miperfil/', views.miperfil, name='miperfil'),
    path('editar-datos/', views.editar_datos, name='editar_datos'),
    path('subir-foto/', views.subir_foto, name='subir_foto'),
    path('carrito/', views.carrito, name='carrito'),
    path('despacho/', despacho, name='despacho'),
    path('confirmacion/', confirmacion, name='confirmacion'),

    # Gestión de productos
    path('gestion-productos/', views.gestion_productos, name='gestion_productos'),
    path('registrar-producto/', views.registrar_producto, name='registrar_producto'),
    path('editar-producto/<int:id>/', views.editar_producto, name='editar_producto'),
    path('eliminar-producto/<int:id>/', views.eliminar_producto, name='eliminar_producto'),
    path('eliminar-producto/', views.eliminar_producto, name='eliminar_producto'),

    # Gestión de usuarios
    path('gestion-usuarios/', views.gestion_usuarios, name='gestion_usuarios'),
    path('registrar-usuario/', views.registrar_usuario, name='registrar_usuario'),
    path('editar-usuario/<int:user_id>/', views.editar_usuario, name='editar_usuario'),
    path('eliminar-usuario/<int:user_id>/', views.eliminar_usuario, name='eliminar_usuario'),

    # Cotización
    path('cotizacion/', views.cotizacion, name='cotizacion'),

    # Carrito de compras
    path('agregar_producto_venta/<int:producto_id>/', views.agregar_producto_venta, name='agregar_producto_venta'),
    path('agregar_producto_arriendo/<int:producto_id>/', views.agregar_producto_arriendo, name='agregar_producto_arriendo'),    
    path('aumentar_cantidad/<int:producto_id>/', views.aumentar_cantidad, name='aumentar_cantidad'),
    path('disminuir_cantidad/<int:producto_id>/', views.disminuir_cantidad, name='disminuir_cantidad'),
    path('eliminar_producto/<int:producto_id>/', views.eliminar_producto_carrito, name='eliminar_producto_carrito'),



    # Confirmación

    path('confirmacion/', views.confirmacion, name='confirmacion'),

    # Despacho
    path('get_ciudades/', views.get_ciudades, name='get_ciudades'),
]

# Configuración de archivos estáticos y media (solo en DEBUG)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
