# Generated by Django 5.1.3 on 2024-11-27 17:51

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Compra',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_cliente', models.CharField(max_length=50)),
                ('fecha', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='Cotizacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('correo', models.EmailField(max_length=254)),
                ('telefono', models.CharField(max_length=15)),
                ('mensaje', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Producto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=255)),
                ('precio', models.DecimalField(decimal_places=2, max_digits=10)),
                ('imagen', models.ImageField(blank=True, null=True, upload_to='productos/')),
            ],
        ),
        migrations.CreateModel(
            name='Productos',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('descripcion', models.CharField(max_length=100)),
                ('precio', models.DecimalField(decimal_places=2, max_digits=10)),
                ('stock', models.PositiveIntegerField()),
                ('categoria', models.CharField(choices=[('Materiales de Construcción', 'Materiales de Construcción'), ('Cemento y Hormigón', 'Cemento y Hormigón'), ('Arena y Áridos', 'Arena y Áridos'), ('Grava y Piedra', 'Grava y Piedra'), ('Maicillo', 'Maicillo'), ('Ladrillos y Bloques', 'Ladrillos y Bloques'), ('Yeso y Mortero', 'Yeso y Mortero'), ('Acero y Varillas', 'Acero y Varillas'), ('Madera y Tableros', 'Madera y Tableros'), ('Aislantes e Impermeabilizantes', 'Aislantes e Impermeabilizantes'), ('Maquinaria Pesada', 'Maquinaria Pesada'), ('Retroexcavadoras', 'Retroexcavadoras'), ('Excavadoras', 'Excavadoras'), ('Bulldozers', 'Bulldozers'), ('Motoniveladoras', 'Motoniveladoras'), ('Compactadoras y Rodillos', 'Compactadoras y Rodillos'), ('Cargadores Frontales', 'Cargadores Frontales'), ('Gruas y Montacargas', 'Gruas y Montacargas'), ('Dumpers y Camiones Tolva', 'Dumpers y Camiones Tolva'), ('Herramientas Eléctricas', 'Herramientas Eléctricas'), ('Taladros y Rotomartillos', 'Taladros y Rotomartillos'), ('Amoladoras y Pulidoras', 'Amoladoras y Pulidoras'), ('Sierras y Cortadoras', 'Sierras y Cortadoras'), ('Generadores Eléctricos', 'Generadores Eléctricos'), ('Compresores de Aire', 'Compresores de Aire'), ('Martillos Neumáticos', 'Martillos Neumáticos'), ('Equipos para Construcción', 'Equipos para Construcción'), ('Andamios y Escaleras', 'Andamios y Escaleras'), ('Mezcladoras de Cemento', 'Mezcladoras de Cemento'), ('Torres de Iluminación', 'Torres de Iluminación'), ('Vibradores de Concreto', 'Vibradores de Concreto'), ('Bateas y Carretillas', 'Bateas y Carretillas'), ('Equipos de Protección Personal', 'Equipos de Protección Personal'), ('Cascos de Seguridad', 'Cascos de Seguridad'), ('Guantes y Gafas de Protección', 'Guantes y Gafas de Protección'), ('Chalecos Reflectantes', 'Chalecos Reflectantes'), ('Botas de Seguridad', 'Botas de Seguridad'), ('Arnés y Equipos de Altura', 'Arnés y Equipos de Altura'), ('Accesorios y Repuestos', 'Accesorios y Repuestos'), ('Repuestos para Maquinaria', 'Repuestos para Maquinaria'), ('Lubricantes y Aceites', 'Lubricantes y Aceites'), ('Filtros y Mangueras', 'Filtros y Mangueras'), ('Equipos para Transporte', 'Equipos para Transporte'), ('Carros de Mano', 'Carros de Mano'), ('Pallets y Elevadores', 'Pallets y Elevadores'), ('Cintas Transportadoras', 'Cintas Transportadoras'), ('Equipos para Demolición', 'Equipos para Demolición'), ('Martillos Hidráulicos', 'Martillos Hidráulicos'), ('Cortadoras de Pavimento', 'Cortadoras de Pavimento'), ('Perforadoras y Equipos de Demolición', 'Perforadoras y Equipos de Demolición')], default='Construcción', max_length=255)),
                ('tipo', models.CharField(choices=[('Venta', 'Venta'), ('Arriendo', 'Arriendo')], default='Venta', max_length=10)),
                ('imagen', models.ImageField(blank=True, null=True, upload_to='productos/')),
            ],
        ),
        migrations.CreateModel(
            name='Carrito',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.PositiveIntegerField(default=1)),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='risco.productos')),
            ],
        ),
        migrations.CreateModel(
            name='ProductosCompra',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.IntegerField()),
                ('id_compra', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='risco.compra')),
                ('id_producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='risco.producto')),
            ],
        ),
    ]