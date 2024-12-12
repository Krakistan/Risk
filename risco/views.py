from datetime import date, datetime, timezone
from pyexpat.errors import messages
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import login
from .models import ArticuloOrden, Orden, Productos,Compra, ProductosCompra
from .forms import CotizacionForm, DireccionEnvio, DireccionEnvioForm, FormularioRegistro
from django.contrib.auth import load_backend
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.views.generic.edit import FormView
from django.urls import reverse
from .models import Producto, Carrito, Cotizacion, DetalleOrden
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.utils.html import strip_tags



def html(request):
    return render(request, 'risco/html.html')



def miperfil(request):
    user = request.user  # Usuario autenticado
    
    # Si el método es POST, actualizamos los datos
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
        else:  # Actualizar datos del perfil
            user.first_name = request.POST.get('nombre')
            user.email = request.POST.get('email')
            user.save()
            messages.success(request, 'Datos actualizados correctamente.')

    # Obtenemos las compras asociadas al usuario (usando nombre_cliente)
    compras = Compra.objects.filter(nombre_cliente=user.username)

    return render(request, 'risco/miperfil.html', {'usuario': user, 'compras': compras})

def editar_datos(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('nombre')
        user.email = request.POST.get('email')
        user.save()
        return redirect('miperfil')  # Redirige de vuelta al perfil

    return redirect('miperfil')



def subir_foto(request):
    if request.method == 'POST':
        user = request.user
        user.profile.image = request.FILES['foto']  # Asegúrate de que el modelo tenga un campo `image`
        user.save()
        messages.success(request, 'Foto de perfil actualizada.')
    return redirect('miperfil')





@user_passes_test(lambda u: u.is_staff or u.is_superuser)
@login_required
def gestion_usuarios(request):
    usuarios = User.objects.all()  # Obtiene todos los usuarios
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






@user_passes_test(lambda u: u.is_staff or u.is_superuser)
@login_required
def gestion_productos(request):
    productos_venta = Productos.objects.filter(tipo="Venta")
    productos_arriendo = Productos.objects.filter(tipo="Arriendo")
    return render(request, 'risco/gestion_productos.html', {
        'productos_venta': productos_venta,
        'productos_arriendo': productos_arriendo,
        'categoria_choices': Productos.CATEGORIA_CHOICES,
        'tipo_choices': Productos.TIPO_CHOICES,
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
        nuevo_producto = Productos(
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
    producto = get_object_or_404(Productos, id=id)

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
        producto = get_object_or_404(Productos, id=producto_id)

        if stock_eliminar > 0 and stock_eliminar <= producto.stock:
            producto.stock -= stock_eliminar
            if producto.stock == 0:
                producto.delete()
            else:
                producto.save()

    return redirect('gestion_productos')




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




def home(request):
    productos_venta = Productos.objects.filter(tipo='Venta').distinct()
    productos_arriendo = Productos.objects.filter(tipo='Arriendo').distinct()
    
    context = {
        'productos_venta': productos_venta,
        'productos_arriendo': productos_arriendo,
    }
    return render(request, 'risco/home.html', context)





def carrito(request, indx=None):
    # Inicializar el carrito en la sesión si no existe
    if 'carro' not in request.session:
        request.session['carro'] = []

    carro = request.session['carro']

    # Agregar producto al carrito si se proporciona un índice
    if indx:
        try:
            producto = Productos.objects.get(id=indx)
            # Verificar si el producto ya está en el carrito
            producto_en_carro = next((item for item in carro if item["id_producto"] == producto.id), None)
            if producto_en_carro:
                # Incrementar cantidad si el stock lo permite
                if producto_en_carro["cantidad"] < producto.stock:
                    producto_en_carro["cantidad"] += 1
                else:
                    messages.warning(request, f"No hay más stock disponible para {producto.nombre}.")
            else:
                # Agregar producto al carrito si hay stock disponible
                if producto.stock > 0:
                    carro.append({
                        "id_producto": producto.id,
                        "nombre": producto.nombre,
                        "cantidad": 1,
                        "precio": float(producto.precio),
                        "imagen": producto.imagen.url if producto.imagen else None,
                        "tipo": producto.tipo.lower(),
                    })
                else:
                    messages.warning(request, f"El producto {producto.nombre} está agotado.")
        except Productos.DoesNotExist:
            messages.error(request, f"El producto con ID {indx} no existe.")

    # Procesar los productos en el carrito
    total_precio = 0
    carrito_venta = []
    carrito_arriendo = []

    for item in carro:
        try:
            producto = Productos.objects.get(id=item["id_producto"])
            # Actualizar información del producto en el carrito
            item["nombre"] = producto.nombre
            item["precio"] = float(producto.precio)
            item["imagen"] = producto.imagen.url if producto.imagen else None

            # Separar productos en venta y arriendo
            if producto.tipo.lower() == 'venta':
                carrito_venta.append(item)
            elif producto.tipo.lower() == 'arriendo':
                carrito_arriendo.append(item)

            total_precio += item["precio"] * item["cantidad"]
        except Productos.DoesNotExist:
            # Remover productos no válidos del carrito
            carro.remove(item)

    # Actualizar el carrito en la sesión
    request.session['carro'] = carro

    # Preparar el formulario de despacho
    form = DireccionEnvioForm()

    context = {
        'carrito_venta': carrito_venta,
        'carrito_arriendo': carrito_arriendo,
        'total_precio': total_precio,
        'form': form,
    }

    return render(request, 'risco/carrito.html', context)






def pagar(request):
    # Obtén el carrito del usuario
    carrito = Carrito.objects.filter(usuario=request.user)

    # Verifica que el carrito no esté vacío
    if not carrito.exists():
        
        return redirect('carrito')

    # Valida la existencia de stock para cada producto en el carrito
    for item in carrito:
        producto = get_object_or_404(Producto, id=item.producto.id)

        # Verifica si el producto tiene suficiente stock
        if producto.stock < item.cantidad:
            messages.error(
                request,
                f"El producto '{producto.nombre}' no tiene suficiente stock. "
            )
            return redirect('carrito')


    return redirect(checkout)





def anadir_al_carro(request, indx):
    if 'carro' not in request.session:
        request.session['carro'] = []

    carro_actual = request.session['carro']

    # Obtener el producto que se quiere agregar
    producto = Productos.objects.filter(id=indx).first()
    if not producto:
        messages.error(request, "El producto no existe.")
        return redirect('carrito')

    # Verificar si ya hay productos en el carrito
    if carro_actual:
        # Comprobar el tipo del primer producto en el carrito
        tipo_actual = carro_actual[0].get("tipo")
        if tipo_actual != producto.tipo:
            # Bloquear la mezcla de tipos
            messages.error(request, f"No puedes mezclar productos de tipo '{tipo_actual}' y '{producto.tipo}'.")
            return redirect('carrito')

    # Verificar si el producto ya está en el carrito
    producto_existente = next((p for p in carro_actual if p["id_producto"] == indx), None)
    if producto_existente:
        producto_existente["cantidad"] += 1
    else:
        # Agregar el nuevo producto al carrito
        carro_actual.append({
            "id_producto": producto.id,
            "nombre": producto.nombre,
            "cantidad": 1,
            "precio": float(producto.precio),
            "tipo": producto.tipo,  # Guardar el tipo del producto
            "imagen": producto.imagen.url if producto.imagen else None
        })

    # Guardar el carrito actualizado en la sesión
    request.session['carro'] = carro_actual
    messages.success(request, f"Producto '{producto.nombre}' agregado al carrito.")
    return redirect('carrito')



 

def eliminar_del_carro(request, indx):
    carro_actual = request.session.get('carro', [])
    carro_actual = [producto for producto in carro_actual if producto["id_producto"] != indx]

    # Si el carrito está vacío, elimina la sesión
    if not carro_actual:
        request.session.pop('carro', None)
    else:
        request.session['carro'] = carro_actual

    return redirect('carrito')


def aumentar_cantidad(request, indx):
    carro_actual = request.session['carro']
    for producto in carro_actual:
        if producto["id_producto"] == indx:
            producto["cantidad"] += 1
    request.session['carro'] = carro_actual
    return redirect('carrito')

def disminuir_cantidad(request, indx):
    carro_actual = request.session['carro']
    for producto in carro_actual:
        if producto["id_producto"] == indx:
            producto["cantidad"] -= 1
            if producto["cantidad"] <= 0:
                carro_actual = [prod for prod in carro_actual if prod["id_producto"] != indx]
    request.session['carro'] = carro_actual
    return redirect('carrito')




def agregar_arriendo(request, producto_id=None):
    if request.method == 'POST':
        # Get the product
        producto = get_object_or_404(Productos, id=producto_id)
        
        # Get dates from form
        fecha_inicio_str = request.POST.get('fecha_inicio')
        fecha_fin_str = request.POST.get('fecha_fin')
        
        # Convert strings to date objects
        try:
            fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
            fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
        except ValueError:
            return render(request, 'error.html', {'message': 'Fechas inválidas'})
        
        # Validate dates
        today = timezone.now().date()
        if fecha_inicio <= today:
            return render(request, 'error.html', {'message': 'La fecha de inicio debe ser posterior a la fecha actual'})
        
        if fecha_fin <= fecha_inicio:
            return render(request, 'error.html', {'message': 'La fecha de fin debe ser posterior a la fecha de inicio'})
        
        # Calculate rental duration
        duracion = (fecha_fin - fecha_inicio).days
        
        # Get current cart from session
        if 'carro' not in request.session:
            request.session['carro'] = []
        
        carro = request.session['carro']
        
        # Create cart item
        rental_item = {
            "id_producto": producto.id,
            "nombre": producto.nombre,
            "cantidad": 1,
            "precio": float(producto.precio),
            "imagen": producto.imagen.url if producto.imagen else None,
            "tipo": "arriendo",
            "fecha_inicio": fecha_inicio.strftime('%Y-%m-%d'),
            "fecha_fin": fecha_fin.strftime('%Y-%m-%d'),
            "duracion": duracion
        }
        
        # Add to cart
        carro.append(rental_item)
        request.session['carro'] = carro
        
        return redirect('carrito')  # Redirect to cart page
    
    # If not POST, show the date selection form
    if producto_id:
        producto = get_object_or_404(Productos, id=producto_id)
        return render(request, 'risco/agregar_arriendo.html', {'producto': producto})
    else:
        # If no producto_id is provided, redirect to a product list or show an error
        return redirect('lista_productos')  # Replace 'lista_productos' with your actual product list URL name



def confirmar_compra(request):
    if not request.user.is_authenticated:
        messages.error(request, "Debes iniciar sesión para confirmar la compra")
        return redirect('iniciar_sesion')

    carro_actual = request.session.get('carro', [])
    if not carro_actual:
        messages.error(request, "No hay productos en el carrito")
        return redirect('carrito')

    compra = Compra(nombre_cliente=request.user.username, fecha=date.today())
    compra.save()

    for item in carro_actual:
        producto = get_object_or_404(Productos, id=item["id_producto"])
        ProductosCompra.objects.create(
            id_producto=producto,
            id_compra=compra,
            cantidad=item["cantidad"]
        )

    request.session['carro'] = []
    messages.success(request, "Compra confirmada con éxito")
    return redirect('home')




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
                return redirect('home')  # Redirigir tras enviar la cotización
            except Exception as e:
                print(f"Error al enviar el correo: {str(e)}")
                return render(request, 'risco/cotizacion.html', {
                    'cotizacionform': cotizacionform,
                    'error': 'No se pudo enviar el correo. Inténtalo de nuevo.',
                })
        else:
            print(cotizacionform.errors)

    return render(request, 'risco/cotizacion.html', {'cotizacionform': cotizacionform})


def nosotros(request):
    return render(request, 'risco/nosotros.html')

def confirmacion(request):
    return render(request, 'risco/confirmacion.html')

def checkout(request):
    if request.method == 'POST':
        direccion = request.POST.get('direccion')
        ciudad = request.POST.get('ciudad')
        region = request.POST.get('region')
        codigo_postal = request.POST.get('codigo_postal')

        if direccion and ciudad and region and codigo_postal:
            try:
                # Guardar la dirección de envío
                direccion_envio = DireccionEnvio.objects.create(
                    user=request.user,
                    direccion=direccion,
                    ciudad=ciudad,
                    region=region,
                    codigo_postal=codigo_postal,
                )

                # Obtener productos del carrito
                carrito_items = Carrito.objects.filter(usuario=request.user)
                productos = [
                    {
                        'nombre': item.producto.nombre,
                        'precio': item.producto.precio,
                        'cantidad': item.cantidad,
                    } for item in carrito_items
                ]

                # Enviar correo al usuario
                asunto_usuario = "Confirmación de tu compra - El Risco Colorado"
                mensaje_html_usuario = render_to_string('correo_confirmacion.html', {
                    'user': request.user,
                    'direccion_envio': direccion_envio,
                    'productos': productos,
                })
                mensaje_texto_usuario = strip_tags(mensaje_html_usuario)
                send_mail(
                    asunto_usuario,
                    mensaje_texto_usuario,
                    'empresa@example.com',
                    [request.user.email],
                    html_message=mensaje_html_usuario
                )

                # Enviar correo a la empresa
                asunto_empresa = "Nueva orden de compra"
                mensaje_html_empresa = render_to_string('correo_empresa.html', {
                    'user': request.user,
                    'direccion_envio': direccion_envio,
                    'productos': productos,
                })
                mensaje_texto_empresa = strip_tags(mensaje_html_empresa)
                send_mail(
                    asunto_empresa,
                    mensaje_texto_empresa,
                    'empresa@example.com',
                    ['empresa@example.com'],
                    html_message=mensaje_html_empresa
                )

                # Mensaje de éxito
                messages.success(request, "¡Tu orden ha sido procesada! Revisa tu correo para más detalles.")
                return redirect('home')

            except Exception as e:
                # Enviar error al correo de la empresa y mostrar mensaje de error
                send_mail(
                    'Error en Checkout - El Risco Colorado',
                    str(e),
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.DEFAULT_COMPANY_EMAIL],
                )
                messages.error(request, f"Hubo un problema al procesar tu orden: {str(e)}")
                return redirect('checkout')

        else:
            messages.error(request, "Por favor, completa todos los campos.")
            return redirect('checkout')

    return render(request, 'risco/checkout.html')





def direccion_despacho_view(request):
    user = request.user
    carrito = Carrito.objects.filter(usuario=user)
    total = sum(item.producto.precio * item.cantidad for item in carrito)

    if request.method == 'POST':
        form = DireccionEnvioForm(request.POST)
        if form.is_valid():
            direccion = form.save(commit=False)
            direccion.usuario = user
            direccion.save()

            # Crear la orden
            orden = Orden.objects.create(usuario=user, completo=True)
            for item in carrito:
                ArticuloOrden.objects.create(
                    orden=orden,
                    producto=item.producto,
                    cantidad=item.cantidad
                )
            direccion.orden = orden
            direccion.save()

            # Vaciar el carrito
            carrito.delete()

            # Enviar correos
            enviar_correos_confirmacion(user, orden, direccion)

            messages.success(request, "¡Compra confirmada! Revisa tu correo para más detalles.")
            return redirect('home')
    else:
        form = DireccionEnvioForm()

    return render(request, 'direccion_despacho.html', {
        'form': form,
        'carrito': carrito,
        'total': total,
    })




def enviar_correos_confirmacion(user, orden, direccion):
    productos = orden.articulos.all()

    # Correo al usuario
    asunto_usuario = "Confirmación de tu compra - El Risco Colorado"
    mensaje_html_usuario = render_to_string('correo_confirmacion.html', {
        'user': user,
        'direccion': direccion,
        'productos': productos,
        'total': orden.get_total_carrito(),
    })
    mensaje_texto_usuario = strip_tags(mensaje_html_usuario)

    send_mail(
        asunto_usuario,
        mensaje_texto_usuario,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=mensaje_html_usuario,
    )

    # Correo a la empresa
    asunto_empresa = "Nueva orden recibida - El Risco Colorado"
    mensaje_html_empresa = render_to_string('correo_empresa.html', {
        'user': user,
        'direccion': direccion,
        'productos': productos,
        'total': orden.get_total_carrito(),
    })
    mensaje_texto_empresa = strip_tags(mensaje_html_empresa)

    send_mail(
        asunto_empresa,
        mensaje_texto_empresa,
        settings.DEFAULT_FROM_EMAIL,
        [settings.DEFAULT_COMPANY_EMAIL],
        html_message=mensaje_html_empresa,
    )






def formulario_despacho(request):
    user = request.user
    carrito_items = Carrito.objects.filter(usuario=user)

    # Verifica si el carrito está vacío
    if not carrito_items.exists():
        messages.error(request, "Tu carrito está vacío. Agrega productos antes de continuar.")
        return redirect('carrito')

    if request.method == 'POST':
        form = DireccionEnvioForm(request.POST)
        if form.is_valid():
            direccion_envio = form.save(commit=False)
            direccion_envio.user = user
            direccion_envio.save()

            # Crear la orden
            orden = Orden.objects.create(
                user=user,
                direccion_envio=direccion_envio,
                completo=False
            )

            # Crear los detalles de la orden
            for item in carrito_items:
                DetalleOrden.objects.create(
                    orden=orden,
                    producto=item.producto.nombre,
                    precio=item.producto.precio,
                    cantidad=item.cantidad
                )

            # Vaciar el carrito
            carrito_items.delete()

            # Enviar correos de confirmación
            enviar_correos_confirmacion(orden)

            # Mensaje de éxito y redirección
            messages.success(request, "Tu orden ha sido procesada con éxito. Revisa tu correo para más detalles.")
            return redirect('home')

    else:
        form = DireccionEnvioForm()

    return render(request, 'risco/despacho.html', {'form': form})




def enviar_correos_confirmacion(orden):
    user = orden.user
    direccion_envio = orden.direccion_envio
    detalles = orden.detalles.all()  # Asegúrate de usar `related_name='detalles'` en `DetalleOrden`
    total = sum(detalle.precio * detalle.cantidad for detalle in detalles)

    # Correo para el usuario
    asunto_usuario = "Confirmación de tu Orden - El Risco Colorado"
    mensaje_html_usuario = render_to_string('correo_confirmacion.html', {
        'user': user,
        'direccion_envio': direccion_envio,
        'detalles': detalles,
        'total': total,
    })
    mensaje_texto_usuario = strip_tags(mensaje_html_usuario)

    send_mail(
        asunto_usuario,
        mensaje_texto_usuario,
        'noreply@elriscocolorado.com',  # Cambia esto por el correo de tu empresa
        [user.email],
        html_message=mensaje_html_usuario,
    )

    # Correo para la empresa
    asunto_empresa = "Nueva Orden Recibida - El Risco Colorado"
    mensaje_html_empresa = render_to_string('correo_empresa.html', {
        'user': user,
        'direccion_envio': direccion_envio,
        'detalles': detalles,
        'total': total,
    })
    mensaje_texto_empresa = strip_tags(mensaje_html_empresa)

    send_mail(
        asunto_empresa,
        mensaje_texto_empresa,
        'noreply@elriscocolorado.com',
        ['empresa@elriscocolorado.com'],  # Cambia por el correo de la empresa
        html_message=mensaje_html_empresa,
    )
