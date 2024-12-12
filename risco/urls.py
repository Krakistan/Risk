from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth import views as auth_views
from risco import views as pagweb_views
from .forms import CustomAuthenticationForm
from risco.views import CustomPasswordResetView, CustomPasswordResetConfirmView, direccion_despacho_view
from . import views

urlpatterns = [
    path('', views.html, name='html'), 
    path('password_reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password_reset_confirm/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password_reset_complete/', auth_views.PasswordResetCompleteView.as_view(template_name='risco/password_reset_complete.html'), name='password_reset_complete'),
    path('home/', views.home, name='home'),
    path('carrito/', views.carrito, name='carrito'),  
    path('carrito/<int:indx>/', views.carrito, name='carrito_with_id'), 
    path('anadir_producto_carro/<int:indx>/', views.anadir_al_carro, name='anadirproducto'),
    path('carrito/<int:indx>/', views.carrito, name='carrito_with_id'),


    path('eliminar_producto_carro/<int:indx>', views.eliminar_del_carro, name='eliminarproducto'),
    path('aumentar_cantidad/<int:indx>', views.aumentar_cantidad, name="aumentarcant"),
    path('disminuir_cantidad/<int:indx>', views.disminuir_cantidad, name="disminuircant"),
    path('confirmar_compra', views.confirmar_compra, name="confirmarcompra"),
    path('pagar/', views.pagar, name='pagar'),
    path('checkout/', views.checkout, name='checkout'),
    path('confirmacion/', views.confirmacion, name='confirmacion'),
    path('nosotros/', views.nosotros, name='nosotros'),
    path('registro/', pagweb_views.registro, name='registro'),
    path('cotizacion/', views.cotizacion, name='cotizacion'),
    path('iniciar-sesion/', auth_views.LoginView.as_view(
        template_name='risco/iniciar_sesion.html',
        authentication_form=CustomAuthenticationForm,
        redirect_authenticated_user=True,
    ), name='iniciar_sesion'),
    path('miperfil/', views.miperfil, name='miperfil'),
    path('editar-datos/', views.editar_datos, name='editar_datos'),
    path('subir-foto/', views.subir_foto, name='subir_foto'),
    path('gestion-productos/', views.gestion_productos, name='gestion_productos'),
    path('registrar-producto/', views.registrar_producto, name='registrar_producto'),
    path('editar-producto/<int:id>/', views.editar_producto, name='editar_producto'),
    path('eliminar-producto/<int:id>/', views.eliminar_producto, name='eliminar_producto'),
    path('eliminar-producto/', views.eliminar_producto, name='eliminar_producto'),

    path('agregar_arriendo/<int:id>/', views.agregar_arriendo, name='agregar_arriendo'),
    path('formulario-despacho/', views.formulario_despacho, name='formulario_despacho'),

    path('gestion-usuarios/', views.gestion_usuarios, name='gestion_usuarios'),
    path('registrar-usuario/', views.registrar_usuario, name='registrar_usuario'),
    path('editar-usuario/<int:user_id>/', views.editar_usuario, name='editar_usuario'),
    path('eliminar-usuario/<int:user_id>/', views.eliminar_usuario, name='eliminar_usuario'),


    path('cerrar-sesion/', auth_views.LogoutView.as_view(next_page='iniciar_sesion'), name='cerrar_sesion'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)