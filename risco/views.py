from datetime import date, datetime
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Sum
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import login
from django.contrib.auth import load_backend
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.views.generic.edit import FormView
from django.urls import reverse
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.db import transaction
from .models import CarritoArriendo, CarritoVenta, DetalleArriendo, DetalleVenta, Pedido, Producto, DetalleOrden, DireccionEnvio, Cotizacion
from .forms import CotizacionForm, DireccionEnvioForm, FormularioRegistro




def html(request):
    return render(request, 'risco/html.html')


################################################################




def nosotros(request):
    return render(request, 'risco/nosotros.html')





################################################################



@login_required
def despacho(request):
    # Obtener carritos de venta y arriendo
    carrito_venta = CarritoVenta.objects.filter(usuario=request.user)
    carrito_arriendo = CarritoArriendo.objects.filter(usuario=request.user)
    form = DireccionEnvioForm()

    if request.method == 'POST':
        form = DireccionEnvioForm(request.POST)
        if form.is_valid():
            # Guardar los datos del formulario
            direccion = form.cleaned_data['direccion']
            ciudad = form.cleaned_data['ciudad']
            region = form.cleaned_data['region']
            codigo_postal = form.cleaned_data['codigo_postal']

            # Calcular el total
            total_venta = sum(item.cantidad * item.precio_producto for item in carrito_venta)
            total_arriendo = sum(item.total_precio for item in carrito_arriendo)
            total_general = total_venta + total_arriendo

            try:
                with transaction.atomic():
                    # Crear el pedido
                    pedido = Pedido.objects.create(
                        usuario=request.user,
                        direccion=direccion,
                        ciudad=ciudad,
                        region=region,
                        codigo_postal=codigo_postal,
                        total=total_general
                    )

                    # Procesar productos de venta
                    for item in carrito_venta:
                        producto = item.producto
                        if producto.stock >= item.cantidad:
                            producto.stock -= item.cantidad
                            producto.save()

                            # Crear detalle de venta
                            DetalleVenta.objects.create(
                                pedido=pedido,
                                producto=producto,
                                cantidad=item.cantidad,
                                precio_unitario=item.precio_producto
                            )
                        else:
                            raise ValueError(f"Stock insuficiente para el producto {producto.nombre}.")

                    # Procesar productos de arriendo
                    for item in carrito_arriendo:
                        producto = item.producto
                        if producto.stock >= item.cantidad:
                            producto.stock -= item.cantidad
                            producto.save()

                            # Crear detalle de arriendo
                            DetalleArriendo.objects.create(
                                pedido=pedido,
                                producto=producto,
                                cantidad=item.cantidad,
                                fecha_inicio=item.fecha_inicio,
                                fecha_fin=item.fecha_fin
                            )
                        else:
                            raise ValueError(f"Stock insuficiente para el producto {producto.nombre}.")

                    # Vaciar los carritos
                    carrito_venta.delete()
                    carrito_arriendo.delete()

                    # Enviar correo de confirmación
                    enviar_correo_confirmacion(pedido, request.user.email)

                    messages.success(request, "Pedido creado exitosamente.")
                    return redirect('confirmacion')

            except ValueError as e:
                messages.error(request, str(e))
            except Exception as e:
                messages.error(request, "Ocurrió un error al procesar tu pedido. Por favor, intenta nuevamente.")

        else:
            messages.error(request, "Por favor, completa todos los campos correctamente.")

    return render(request, 'risco/despacho.html', {
        'carrito_venta': carrito_venta,
        'carrito_arriendo': carrito_arriendo,
        'form': form,
    })




def enviar_correo_confirmacion(pedido, correo_usuario):
    asunto = f"Confirmación de Pedido #{pedido.id}"
    mensaje_usuario = f"""
    Hola {pedido.usuario.first_name},

    Gracias por tu pedido en Risco Colorado. Aquí están los detalles de tu pedido:

    Dirección de envío:
    {pedido.direccion}, {pedido.ciudad}, {pedido.region}, {pedido.codigo_postal}

    Total a pagar: ${pedido.total:.2f}

    Productos comprados:
    """
    # Acceder a los detalles de venta usando el related_name correcto
    for detalle in pedido.detalles_venta.all():
        mensaje_usuario += f"- {detalle.producto.nombre} x{detalle.cantidad} (${detalle.total_precio:.2f})\n"

    mensaje_usuario += "\nProductos arrendados:\n"
    # Acceder a los detalles de arriendo usando el related_name correcto
    for detalle in pedido.detalles_arriendo.all():
        mensaje_usuario += (
            f"- {detalle.producto.nombre} x{detalle.cantidad} "
            f"(desde {detalle.fecha_inicio} hasta {detalle.fecha_fin}) - ${detalle.total_precio:.2f}\n"
        )

    mensaje_usuario += "\n¡Gracias por confiar en nosotros!"

    try:
        send_mail(
            asunto,
            mensaje_usuario,
            'riscocoloradopruebas@gmail.com',
            [correo_usuario, 'riscocoloradopruebas@gmail.com']
        )
    except Exception as e:
        print(f"Error al enviar el correo: {str(e)}")





def get_ciudades(request):
    region = request.GET.get('region')
    CIUDADES_POR_REGION = {
        'Metropolitana': [{'id': 'santiago', 'nombre': 'Santiago'}, {'id': 'puente_alto', 'nombre': 'Puente Alto'}],
        'Valparaíso': [{'id': 'valparaiso', 'nombre': 'Valparaíso'}, {'id': 'vina_del_mar', 'nombre': 'Viña del Mar'}],
        'Biobío': [{'id': 'concepcion', 'nombre': 'Concepción'}, {'id': 'los_angeles', 'nombre': 'Los Ángeles'}],
        'La Araucanía': [{'id': 'temuco', 'nombre': 'Temuco'}, {'id': 'villarrica', 'nombre': 'Villarrica'}],
    }

    ciudades = CIUDADES_POR_REGION.get(region, [])
    return JsonResponse({'ciudades': ciudades})




################################################################


def confirmacion(request):
    return render(request, 'risco/confirmacion.html')



################################################################





# Registro #

def registro(request):
    if request.method == 'POST':
        formulario = FormularioRegistro(request.POST)
        if formulario.is_valid():
            usuario = formulario.save()
            
            
            backend = load_backend('risco.backends.EmailBackend')
            usuario.backend = backend.__class__.__module__ + '.' + backend.__class__.__name__
            login(request, usuario)  
            
            return redirect('home')
    else:
        formulario = FormularioRegistro()
    return render(request, 'risco/registro.html', {'formulario': formulario})





################################################################

# Cotizacion #

def cotizacion(request):
    cotizacionform = CotizacionForm(request.POST or None)

    if request.method == 'POST':
        if cotizacionform.is_valid():
            # Guardar la cotización en la base de datos
            cotizacion = cotizacionform.save()

            # Configurar el correo para ti (administrador)
            asunto = f"Nueva Cotización de {cotizacion.nombre}"
            mensaje = f"""
            Has recibido una nueva cotización desde la página web:
            
            Nombre: {cotizacion.nombre}
            Correo: {cotizacion.correo}
            Teléfono: {cotizacion.telefono}
            Mensaje: {cotizacion.mensaje}
            """
            remitente = cotizacion.correo
            destinatarios = ['riscocoloradopruebas@gmail.com']  # Cambia por tu correo

            try:
                send_mail(asunto, mensaje, remitente, destinatarios)
                return redirect('home')  
            except Exception as e:
                print(f"Error al enviar el correo: {str(e)}")
                return render(request, 'risco/cotizacion.html', {
                    'cotizacionform': cotizacionform,
                    'error': 'No se pudo enviar el correo. Inténtalo de nuevo.',
                })
        else:
            print(cotizacionform.errors)

    return render(request, 'risco/cotizacion.html', {'cotizacionform': cotizacionform})




################################################################




# Perfil Usuario #

@login_required
def miperfil(request):
    user = request.user
    
    if request.method == 'POST':
        if 'password_actual' in request.POST:  # Cambiar contraseña
            password_actual = request.POST.get('password_actual')
            password_nueva = request.POST.get('password_nueva')
            if user.check_password(password_actual):
                user.set_password(password_nueva)
                user.save()
                messages.success(request, 'Contraseña actualizada correctamente.')
            else:
                messages.error(request, 'La contraseña actual es incorrecta.')
        else:  # Actualizar perfil
            user.first_name = request.POST.get('nombre')
            user.email = request.POST.get('email')
            user.save()
            messages.success(request, 'Datos actualizados correctamente.')

    # Obtener las compras asociadas al usuario
    compras = DetalleOrden.objects.filter(orden__usuario=user)

    return render(request, 'risco/miperfil.html', {'usuario': user, 'compras': compras})


def editar_datos(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('nombre')
        user.email = request.POST.get('email')
        user.save()
        return redirect('miperfil')  

    return redirect('miperfil')



def subir_foto(request):
    if request.method == 'POST':
        user = request.user
        user.profile.image = request.FILES['foto']  
        user.save()
        messages.success(request, 'Foto de perfil actualizada.')
    return redirect('miperfil')




################################################################



# home #


def home(request):
    productos_venta = Producto.objects.filter(tipo='Venta')
    productos_arriendo = Producto.objects.filter(tipo='Arriendo')

    context = {
        'productos_venta': productos_venta,
        'productos_arriendo': productos_arriendo,
    }

    return render(request, 'risco/home.html', context)




################################################################


# carrito #


@login_required
def carrito(request):
    carrito_venta = CarritoVenta.objects.filter(usuario=request.user)
    carrito_arriendo = CarritoArriendo.objects.filter(usuario=request.user)

    total_venta = sum(item.total_precio for item in carrito_venta)
    total_arriendo = sum(item.total_precio for item in carrito_arriendo)
    total_general = total_venta + total_arriendo

    context = {
        'carrito_venta': carrito_venta,
        'carrito_arriendo': carrito_arriendo,
        'total_precio_venta': total_venta,
        'total_precio_arriendo': total_arriendo,
        'total_precio': total_general,
    }

    return render(request, 'risco/carrito.html', context)



@login_required
def agregar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    if producto.tipo == 'Venta':
        carrito_item, created = CarritoVenta.objects.get_or_create(
            usuario=request.user,
            producto=producto,
            defaults={'precio_producto': producto.precio}
        )
    elif producto.tipo == 'Arriendo':
        carrito_item, created = CarritoArriendo.objects.get_or_create(
            usuario=request.user,
            producto=producto,
            defaults={'precio_producto': producto.precio}
        )
    else:
   
        return redirect('carrito')

    if not created:
        carrito_item.cantidad += 1
        carrito_item.save()

    return redirect('carrito')



@login_required
def agregar_producto_venta(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id, tipo='Venta')
    
    # Crear o actualizar el carrito de venta
    carrito_item, created = CarritoVenta.objects.get_or_create(
        usuario=request.user,
        producto=producto,
        defaults={
            'nombre_producto': producto.nombre,
            'precio_producto': producto.precio,
            'imagen_producto': producto.imagen,
        }
    )
    if not created:
        # Si ya existe, aumenta la cantidad
        carrito_item.cantidad += 1
        carrito_item.save()

    return redirect('carrito')



@login_required
def agregar_producto_arriendo(request, producto_id):
    if request.method == 'POST':
        producto = get_object_or_404(Producto, id=producto_id, tipo='Arriendo')
        
        fecha_inicio = request.POST.get('fecha_inicio')
        fecha_fin = request.POST.get('fecha_fin')
        cantidad = int(request.POST.get('cantidad', 1))
        
        try:
            fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d')
            fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d')
        except ValueError:
            return redirect('home')

        if producto.stock < cantidad:
            return redirect('home')

        carrito_item, created = CarritoArriendo.objects.get_or_create(
            usuario=request.user,
            producto=producto,
            defaults={
                'fecha_inicio': fecha_inicio,
                'fecha_fin': fecha_fin,
                'cantidad': cantidad,
            }
        )

        if not created:
            carrito_item.cantidad += cantidad
            carrito_item.fecha_inicio = fecha_inicio
            carrito_item.fecha_fin = fecha_fin
            carrito_item.save()

        producto.stock -= cantidad
        producto.save()

        return redirect('carrito')

def aumentar_cantidad(request, producto_id):
    # Intentar en el carrito de venta
    try:
        carrito_item = CarritoVenta.objects.get(producto_id=producto_id, usuario=request.user)
    except CarritoVenta.DoesNotExist:
        # Si no está en venta, buscar en el carrito de arriendo
        carrito_item = get_object_or_404(CarritoArriendo, producto_id=producto_id, usuario=request.user)

    # Incrementar la cantidad si hay suficiente stock
    if carrito_item.producto.stock > carrito_item.cantidad:
        carrito_item.cantidad += 1
        carrito_item.save()
        carrito_item.producto.stock -= 1
        carrito_item.producto.save()

    return redirect('carrito')


def disminuir_cantidad(request, producto_id):
    # Intentar en el carrito de venta
    try:
        carrito_item = CarritoVenta.objects.get(producto_id=producto_id, usuario=request.user)
    except CarritoVenta.DoesNotExist:
        # Si no está en venta, buscar en el carrito de arriendo
        carrito_item = get_object_or_404(CarritoArriendo, producto_id=producto_id, usuario=request.user)

    # Disminuir la cantidad si es mayor a 1
    if carrito_item.cantidad > 1:
        carrito_item.cantidad -= 1
        carrito_item.save()
        carrito_item.producto.stock += 1
        carrito_item.producto.save()
    else:
        # Si la cantidad es 1, eliminar el producto
        carrito_item.producto.stock += carrito_item.cantidad
        carrito_item.producto.save()
        carrito_item.delete()

    return redirect('carrito')


def eliminar_producto_carrito(request, producto_id):
   
    try:
        carrito_item = CarritoVenta.objects.get(producto_id=producto_id, usuario=request.user)
    except CarritoVenta.DoesNotExist:
    
        carrito_item = get_object_or_404(CarritoArriendo, producto_id=producto_id, usuario=request.user)


    carrito_item.producto.stock += carrito_item.cantidad
    carrito_item.producto.save()

    # Eliminar el producto del carrito
    carrito_item.delete()

    return redirect('carrito')



################################################################



# gestion de usuario para admin   #


@user_passes_test(lambda u: u.is_staff or u.is_superuser)
@login_required
def gestion_usuarios(request):
    usuarios = User.objects.all()  
    return render(request, 'risco/gestion_usuarios.html', {'usuarios': usuarios})


@user_passes_test(lambda u: u.is_staff or u.is_superuser)
@login_required
def registrar_usuario(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        is_superuser = request.POST.get('is_superuser') == 'on'
        is_staff = request.POST.get('is_staff') == 'on'

        user = User.objects.create_user(username=username, password=password, email=email)
        user.first_name = first_name
        user.last_name = last_name
        user.is_superuser = is_superuser
        user.is_staff = is_staff
        user.save()

        return redirect('gestion_usuarios')

    return render(request, 'risco/registrar_usuario.html')


@user_passes_test(lambda u: u.is_staff or u.is_superuser)
@login_required
def editar_usuario(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.username = request.POST.get('username')
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.is_superuser = request.POST.get('is_superuser') == 'on'
        user.is_staff = request.POST.get('is_staff') == 'on'
        user.save()

        return redirect('gestion_usuarios')

    return render(request, 'risco/editar_usuario.html', {'usuario': user})


@user_passes_test(lambda u: u.is_staff or u.is_superuser)
@login_required
def eliminar_usuario(request, user_id):
    if request.method == 'POST':
        try:
            user = get_object_or_404(User, id=user_id)
            user.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)





################################################################

# gestion de productos de admin #


@user_passes_test(lambda u: u.is_staff or u.is_superuser)
@login_required
def gestion_productos(request):
    productos_venta = Producto.objects.filter(tipo="Venta")
    productos_arriendo = Producto.objects.filter(tipo="Arriendo")
    return render(request, 'risco/gestion_productos.html', {
        'productos_venta': productos_venta,
        'productos_arriendo': productos_arriendo,
        'categoria_choices': Producto.CATEGORIA_CHOICES,
        'tipo_choices': Producto.TIPO_CHOICES,
    })



@user_passes_test(lambda u: u.is_staff or u.is_superuser)
@login_required
def registrar_producto(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        precio = request.POST.get('precio')
        stock = request.POST.get('stock')
        categoria = request.POST.get('categoria')
        tipo = request.POST.get('tipo')
        imagen = request.FILES.get('imagen')  # Manejo del archivo cargado

        # Crear el producto y guardar en la base de datos
        nuevo_producto = Producto(
            nombre=nombre,
            descripcion=descripcion,
            precio=precio,
            stock=stock,
            categoria=categoria,
            tipo=tipo,
            imagen=imagen
        )
        nuevo_producto.save()

        return redirect('gestion_productos')  # Redirige de vuelta a la página de gestión de productos

    # Si es GET, renderizar el formulario
    return render(request, 'gestion_productos')


@user_passes_test(lambda u: u.is_staff or u.is_superuser)
@login_required
def editar_producto(request, id):
    producto = get_object_or_404(Producto, id=id)

    if request.method == 'POST':
        producto.nombre = request.POST.get('nombre')
        producto.descripcion = request.POST.get('descripcion')
        producto.precio = request.POST.get('precio')
        producto.stock = request.POST.get('stock')
        producto.categoria = request.POST.get('categoria')
        producto.tipo = request.POST.get('tipo')
        if 'imagen' in request.FILES:
            producto.imagen = request.FILES['imagen']
        producto.save()
        return redirect('gestion_productos')

    return render(request, 'risco/editar_producto.html', {'producto': producto})


@user_passes_test(lambda u: u.is_staff or u.is_superuser)
@login_required
def eliminar_producto(request):
    if request.method == "POST":
        producto_id = request.POST.get("producto_id")
        stock_eliminar = int(request.POST.get("stock_eliminar", 0))
        producto = get_object_or_404(Producto, id=producto_id)

        if stock_eliminar > 0 and stock_eliminar <= producto.stock:
            producto.stock -= stock_eliminar
            if producto.stock == 0:
                producto.delete()
            else:
                producto.save()

    return redirect('gestion_productos')





################################################################


# Gestion de cambio de contraseña


class CustomPasswordResetConfirmView(FormView):
    template_name = 'risco/password_reset_confirm.html'
    form_class = SetPasswordForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        email = self.request.GET.get('email')
        user = User.objects.filter(email=email).first()

        if not user:
            raise ValueError("No se encontró un usuario con este correo electrónico.")

        # Agrega el usuario a los argumentos del formulario
        kwargs['user'] = user
        return kwargs

    def form_valid(self, form):
        # Guarda la nueva contraseña
        form.save()
        
        return redirect('home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['email'] = self.request.GET.get('email')  # Pasar el email al contexto
        return context
 


class CustomPasswordResetView(FormView):
    template_name = 'risco/password_reset_form.html'
    form_class = PasswordResetForm

    def form_valid(self, form):
        # Obtén el correo del formulario
        email = form.cleaned_data.get('email')

        # Verifica si el usuario existe
        user = User.objects.filter(email=email).first()
        if user:
            # Redirige al formulario de establecer nueva contraseña con el correo en los parámetros
            return redirect(f"{reverse('password_reset_confirm')}?email={email}")
        else:
            # Si el correo no existe, muestra un mensaje o redirige
            form.add_error('email', 'No existe un usuario con este correo.')
            return self.form_invalid(form)



################################################################











