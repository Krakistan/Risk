from django.conf import settings
from django.contrib.auth.models import User
from django.db import models

class Productos(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    
    # Categorías posibles para productos
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
    
    categoria = models.CharField(
        max_length=255,
        choices=CATEGORIA_CHOICES,
        default='Construcción'
    )
    
    TIPO_CHOICES = [
        ('Venta', 'Venta'),
        ('Arriendo', 'Arriendo'),
    ]
    
    tipo = models.CharField(
        max_length=10,
        choices=TIPO_CHOICES,
        default='Venta'
    )
    
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    nombre = models.CharField(max_length=255)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)

    def __str__(self):
        return self.nombre

class Maquinaria(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    disponible = models.BooleanField(default=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)

    @property
    def imagenURL(self):
        if self.imagen:
            return self.imagen.url
        return '/static/images/default.png'

    def _str_(self):
        return f"Maquinaria de {self.nombre}"
    
class Reserva(models.Model):
    id = models.AutoField(primary_key=True)
    maquinaria = models.ForeignKey(Maquinaria, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    estado = models.BooleanField(default=True, verbose_name='Estado')


class Orden(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name="ordenes"  # Relación inversa clara para el usuario
    )
    direccion_envio = models.OneToOneField(
        'DireccionEnvio', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='orden_asociada'  # Cambiar el related_name para evitar conflicto
    )
    fecha_orden = models.DateTimeField(auto_now_add=True)
    completo = models.BooleanField(default=False)
    transaccion_id = models.CharField(max_length=200, null=True, blank=True)

    @property
    def get_total_carrito(self):
        return sum(articulo.get_total for articulo in self.articuloorden_set.all())

    @property
    def get_cantidad_carrito(self):
        return sum(articulo.cantidad for articulo in self.articuloorden_set.all())


class DireccionEnvio(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    orden = models.OneToOneField(
        Orden, 
        on_delete=models.CASCADE, 
        related_name='direccion_asignada'  # Cambiar el related_name para evitar conflicto
    )
    direccion = models.CharField(max_length=200)
    ciudad = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    codigo_postal = models.CharField(max_length=20)
    fecha_agregado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.direccion}, {self.ciudad}, {self.region} ({self.codigo_postal})"





class DetalleOrden(models.Model):
    orden = models.ForeignKey(
        'Orden', 
        related_name='detalles', 
        on_delete=models.CASCADE
    )
    producto = models.CharField(max_length=255)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.cantidad} x {self.producto} (Orden ID: {self.orden.id})"

    @property
    def get_total(self):
        return self.precio * self.cantidad






class ArticuloOrden(models.Model):
    orden = models.ForeignKey(Orden, related_name='articuloorden_set', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField(default=0)

    def _str_(self):
        return f"{self.cantidad} de {self.producto.nombre}"

    @property
    def get_total(self):
        return self.producto.precio * self.cantidad


class Region(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class Ciudad(models.Model):
    nombre = models.CharField(max_length=100)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='ciudades')

    def __str__(self):
        return f"{self.nombre} ({self.region.nombre})"


class Compra(models.Model):
    nombre_cliente = models.CharField(max_length=50)
    fecha = models.DateField()

class ProductosCompra(models.Model):
    id_producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    id_compra = models.ForeignKey(Compra, on_delete=models.CASCADE)
    cantidad = models.IntegerField()


class Cotizacion(models.Model):
    nombre = models.CharField(max_length=100)
    correo = models.EmailField()
    telefono = models.CharField(max_length=15)
    mensaje = models.TextField()

    def __str__(self):
        return self.nombre
    

class Carrito(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    producto = models.ForeignKey(Productos, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.usuario.username} - {self.producto.nombre} ({self.cantidad})"



class RentalCartItem(models.Model):
    producto = models.ForeignKey(Productos, on_delete=models.CASCADE)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    cantidad = models.IntegerField(default=1)

