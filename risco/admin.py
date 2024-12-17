from django.contrib import admin
from .models import Producto, Cotizacion, DetalleOrden

admin.site.register(Producto)
admin.site.register(DetalleOrden)
admin.site.register(Cotizacion)
