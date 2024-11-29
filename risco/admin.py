from django.contrib import admin
from .models import Productos, Cotizacion, Compra, DireccionEnvio

admin.site.register(Productos)
admin.site.register(Cotizacion)
admin.site.register(Compra)
admin.site.register(DireccionEnvio)
