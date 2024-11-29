from datetime import date
from pyexpat.errors import messages

from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import login
from .models import Orden, Productos,Compra, ProductosCompra
from .forms import CotizacionForm, DireccionEnvioForm, FormularioRegistro
from django.contrib.auth import load_backend
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.views.generic.edit import FormView
from django.urls import reverse
from .models import Producto, Carrito
from django.contrib.auth.models import User



def html(request):
    return render(request, 'risco/html.html')

def checkout(request):
    return render(request, 'risco/checkout.html')

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
    productos_venta = Productos.objects.filter(tipo='Venta')
    productos_arriendo = Productos.objects.filter(tipo='Arriendo')

    
    context = {
        'productos_venta': productos_venta,
        'productos_arriendo': productos_arriendo,
        
    }    
    return render(request, 'risco/home.html', context)


def carrito(request, indx=None):
    if 'carro' not in request.session:
        request.session['carro'] = []

    carro = request.session['carro']

    if indx:
        producto = Productos.objects.filter(id=indx).first()
        if producto:
            carro.append({
                "id_producto": producto.id,
                "nombre": producto.nombre,
                "cantidad": 1,
                "precio": float(producto.precio),
                "imagen": producto.imagen.url if producto.imagen else None,
                "tipo": producto.tipo,
            })

    total_precio = 0
    total_items = 0
    for c in carro:
        producto = Productos.objects.filter(id=c["id_producto"]).first()
        if producto:
            c["nombre"] = producto.nombre
            c["precio"] = float(producto.precio)
            c["imagen"] = producto.imagen.url if producto.imagen else None
            total_precio += c["precio"] * c["cantidad"]
            total_items += c["cantidad"]
        else:
            c["nombre"] = "Producto no disponible"
            c["precio"] = 0.0

    request.session['carro'] = carro
    context = {
        'carrito': carro,
        'total_precio': total_precio,
        'total_items': total_items,
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
            cotizacionform.save()
            return redirect('home')  
        else:
            print(cotizacionform.errors)  

    return render(request, 'risco/cotizacion.html', {'cotizacionform': cotizacionform})



def nosotros(request):
    return render(request, 'risco/nosotros.html')

def confirmacion(request):
    return render(request, 'risco/confirmacion.html')

def checkout(request):

    if request.method == 'POST':
        form = DireccionEnvioForm(request.POST)
        if form.is_valid():
            # Crear una instancia del modelo sin guardarlo aún
            direccion_envio = form.save(commit=False)

            # Asignar el usuario y la orden activa (si corresponde)
            user, created = User.objects.get_or_create(username=request.user.username)  # Cambiado de usuario a username
            ultima_orden = Orden.objects.filter(user=user, completo=False).last()  # Cambiado user_profile a user
            if ultima_orden:
                direccion_envio.orden = ultima_orden

            direccion_envio.user = user
            direccion_envio.save()  # Guardar en la base de datos

            return redirect('confirmacion')
    
    else:
        form = DireccionEnvioForm()

    return render(request, 'risco/checkout.html', {'form': form})
