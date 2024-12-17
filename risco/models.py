from datetime import timedelta, timezone
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.forms import ValidationError
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _




class Producto(models.Model):

    CATEGORIA_CHOICES = [
        ('Materiales de Construcción', 'Materiales de Construcción'),
        ('Cemento y Hormigón', 'Cemento y Hormigón'),
        ('Arena y Áridos', 'Arena y Áridos'),
        ('Grava y Piedra', 'Grava y Piedra'),
        ('Maicillo', 'Maicillo'),
        ('Ladrillos y Bloques', 'Ladrillos y Bloques'),
        ('Yeso y Mortero', 'Yeso y Mortero'),
        ('Acero y Varillas', 'Acero y Varillas'),
        ('Madera y Tableros', 'Madera y Tableros'),
        ('Aislantes e Impermeabilizantes', 'Aislantes e Impermeabilizantes'),
        ('Maquinaria Pesada', 'Maquinaria Pesada'),
        ('Retroexcavadoras', 'Retroexcavadoras'),
        ('Excavadoras', 'Excavadoras'),
        ('Bulldozers', 'Bulldozers'),
        ('Motoniveladoras', 'Motoniveladoras'),
        ('Compactadoras y Rodillos', 'Compactadoras y Rodillos'),
        ('Cargadores Frontales', 'Cargadores Frontales'),
        ('Gruas y Montacargas', 'Gruas y Montacargas'),
        ('Dumpers y Camiones Tolva', 'Dumpers y Camiones Tolva'),
        ('Herramientas Eléctricas', 'Herramientas Eléctricas'),
        ('Taladros y Rotomartillos', 'Taladros y Rotomartillos'),
        ('Amoladoras y Pulidoras', 'Amoladoras y Pulidoras'),
        ('Sierras y Cortadoras', 'Sierras y Cortadoras'),
        ('Generadores Eléctricos', 'Generadores Eléctricos'),
        ('Compresores de Aire', 'Compresores de Aire'),
        ('Martillos Neumáticos', 'Martillos Neumáticos'),
        ('Equipos para Construcción', 'Equipos para Construcción'),
        ('Andamios y Escaleras', 'Andamios y Escaleras'),
        ('Mezcladoras de Cemento', 'Mezcladoras de Cemento'),
        ('Torres de Iluminación', 'Torres de Iluminación'),
        ('Vibradores de Concreto', 'Vibradores de Concreto'),
        ('Bateas y Carretillas', 'Bateas y Carretillas'),
        ('Equipos de Protección Personal', 'Equipos de Protección Personal'),
        ('Cascos de Seguridad', 'Cascos de Seguridad'),
        ('Guantes y Gafas de Protección', 'Guantes y Gafas de Protección'),
        ('Chalecos Reflectantes', 'Chalecos Reflectantes'),
        ('Botas de Seguridad', 'Botas de Seguridad'),
        ('Arnés y Equipos de Altura', 'Arnés y Equipos de Altura'),
        ('Accesorios y Repuestos', 'Accesorios y Repuestos'),
        ('Repuestos para Maquinaria', 'Repuestos para Maquinaria'),
        ('Lubricantes y Aceites', 'Lubricantes y Aceites'),
        ('Filtros y Mangueras', 'Filtros y Mangueras'),
        ('Equipos para Transporte', 'Equipos para Transporte'),
        ('Carros de Mano', 'Carros de Mano'),
        ('Pallets y Elevadores', 'Pallets y Elevadores'),
        ('Cintas Transportadoras', 'Cintas Transportadoras'),
        ('Equipos para Demolición', 'Equipos para Demolición'),
        ('Martillos Hidráulicos', 'Martillos Hidráulicos'),
        ('Cortadoras de Pavimento', 'Cortadoras de Pavimento'),
        ('Perforadoras y Equipos de Demolición', 'Perforadoras y Equipos de Demolición')
    ]

    TIPO_CHOICES = [
        ('Venta', 'Venta'),
        ('Arriendo', 'Arriendo'),
    ]

    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default='Venta')
    categoria = models.CharField(max_length=255, choices=CATEGORIA_CHOICES, default='Materiales de Construcción')
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} ({self.tipo})"





# Modelo para productos en venta
class CarritoVenta(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    nombre_producto = models.CharField(max_length=100)
    precio_producto = models.DecimalField(max_digits=10, decimal_places=2)
    imagen_producto = models.ImageField(upload_to='carrito/venta/', blank=True, null=True)

    @property
    def total_precio(self):
        return self.cantidad * self.precio_producto

    def __str__(self):
        return f"{self.cantidad} x {self.nombre_producto} (Venta - {self.usuario.username})"


# Modelo para productos en arriendo


class CarritoArriendo(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="arriendos")
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="arriendos")
    cantidad = models.PositiveIntegerField(default=1)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()

    class Meta:
        verbose_name = _("Carrito de Arriendo")
        verbose_name_plural = _("Carritos de Arriendo")

    def clean(self):
        # Validar fechas
        if self.fecha_fin < self.fecha_inicio:
            raise ValidationError(_("La fecha de fin debe ser posterior o igual a la fecha de inicio."))
        
        # Validar stock
        if self.cantidad > self.producto.stock:
            raise ValidationError(_(f"Stock insuficiente para el producto '{self.producto.nombre}'. Disponible: {self.producto.stock}."))

    @property
    def dias_arriendo(self):
        return (self.fecha_fin - self.fecha_inicio).days + 1

    @property
    def total_precio(self):
        return self.cantidad * self.producto.precio * self.dias_arriendo

    def reducir_stock(self):
        if self.producto.stock >= self.cantidad:
            self.producto.stock -= self.cantidad
            self.producto.save()
        else:
            raise ValidationError(_(f"Stock insuficiente para reducir del producto '{self.producto.nombre}'."))

    def save(self, *args, **kwargs):
        # Ejecutar validaciones
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre} - {self.dias_arriendo} días ({self.usuario.username})"






# Modelo para las órdenes (cuando el carrito se finaliza)
class Orden(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    completo = models.BooleanField(default=False)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def calcular_totales(self):
        detalles = self.detalleorden_set.all()
        self.total = sum(detalle.total_precio for detalle in detalles)
        self.save()

    def __str__(self):
        return f"Orden {self.id} - {self.usuario.username}"


# Detalles de la orden (relación con los productos comprados/rentados)
class DetalleOrden(models.Model):
    orden = models.ForeignKey(Orden, related_name="detalleorden_set", on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def total_precio(self):
        return self.cantidad * self.precio_unitario

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre} (Orden {self.orden.id})"

class DetalleVenta(models.Model):
    pedido = models.ForeignKey('Pedido', related_name="detalles_venta", on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def total_precio(self):
        return self.cantidad * self.precio_unitario

class DetalleArriendo(models.Model):
    pedido = models.ForeignKey('Pedido', related_name="detalles_arriendo", on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()

    @property
    def dias_arriendo(self):
        return (self.fecha_fin - self.fecha_inicio).days + 1

    @property
    def total_precio(self):
        return self.cantidad * self.producto.precio * self.dias_arriendo


class Pedido(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    direccion = models.CharField(max_length=255)
    ciudad = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    codigo_postal = models.CharField(max_length=10)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pedido #{self.id} - {self.usuario.username}"






# Modelo para la dirección de envío
class DireccionEnvio(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    orden = models.OneToOneField(Orden, on_delete=models.CASCADE, related_name="direccion_envio")
    direccion = models.CharField(max_length=255)
    ciudad = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    codigo_postal = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.direccion}, {self.ciudad}, {self.region} ({self.codigo_postal})"


#Cotizacion 

class Cotizacion(models.Model):
    nombre = models.CharField(max_length=100)
    correo = models.EmailField()
    telefono = models.CharField(max_length=15)
    mensaje = models.TextField()

    def __str__(self):
        return self.nombre
    



class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)

    def is_valid(self):
        expiration_time = self.created_at + timedelta(hours=1)
        return not self.used and timezone.now() < expiration_time