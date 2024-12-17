from django import forms
from .models import Cotizacion, DireccionEnvio
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

# Formulario de registro de usuario
class FormularioRegistro(UserCreationForm):
    email = forms.EmailField(required=True, label="Correo Electrónico")

    class Meta:
        model = User
        fields = ['first_name', 'email', 'password1', 'password2']
        labels = {
            'first_name': 'Nombre de usuario',
            'email': 'Correo Electrónico',
            'password1': 'Contraseña',
            'password2': 'Confirmar Contraseña',
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Validar que el email sea único
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo ya está registrado.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']

        # Asigna el email como username si el username está vacío
        if not user.username or user.username.strip() == '':
            user.username = user.email

        if commit:
            user.save()
        return user


# Formulario de autenticación personalizado
class CustomAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label="Correo Electrónico")


# Formulario para cotizaciones
class CotizacionForm(forms.ModelForm):
    class Meta:
        model = Cotizacion
        fields = ['nombre', 'correo', 'telefono', 'mensaje']
        labels = {
            'nombre': 'Nombre',
            'correo': 'Correo Electrónico',
            'telefono': 'Teléfono',
            'mensaje': 'Comentarios o Preguntas',
        }


# Formulario para dirección de envío
REGIONES_CHILE = [
    ('Arica y Parinacota', 'Arica y Parinacota'),
    ('Tarapacá', 'Tarapacá'),
    ('Antofagasta', 'Antofagasta'),
    ('Atacama', 'Atacama'),
    ('Coquimbo', 'Coquimbo'),
    ('Valparaíso', 'Valparaíso'),
    ('Metropolitana', 'Metropolitana'),
    ('O’Higgins', 'O’Higgins'),
    ('Maule', 'Maule'),
    ('Ñuble', 'Ñuble'),
    ('Biobío', 'Biobío'),
    ('La Araucanía', 'La Araucanía'),
    ('Los Ríos', 'Los Ríos'),
    ('Los Lagos', 'Los Lagos'),
    ('Aysén', 'Aysén'),
    ('Magallanes', 'Magallanes'),
]

class DireccionEnvioForm(forms.ModelForm):
    class Meta:
        model = DireccionEnvio
        fields = ['direccion', 'ciudad', 'region', 'codigo_postal']
        widgets = {
            'direccion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dirección'}),
            'ciudad': forms.Select(attrs={'class': 'form-control'}),
            'region': forms.Select(attrs={'class': 'form-control'}),
            'codigo_postal': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Código Postal'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Cargar las regiones estáticas
        self.fields['region'].choices = [('', 'Selecciona una Región')] + REGIONES_CHILE
        self.fields['ciudad'].choices = [('', 'Selecciona una Ciudad')]

        # Cargar ciudades si hay datos previos
        if 'region' in self.data:
            region = self.data.get('region')
            self.fields['ciudad'].choices += self.get_ciudades_por_region(region)
        elif self.instance.pk and self.instance.region:
            self.fields['ciudad'].choices += self.get_ciudades_por_region(self.instance.region)

    def get_ciudades_por_region(self, region):
        # Simulación de ciudades por región
        CIUDADES_POR_REGION = {
            'Metropolitana': ['Santiago', 'Puente Alto', 'Maipú'],
            'Valparaíso': ['Valparaíso', 'Viña del Mar', 'Quilpué'],
            'Biobío': ['Concepción', 'Los Ángeles', 'Chillán'],
            'La Araucanía': ['Temuco', 'Villarrica', 'Angol'],
        }
        return [(ciudad, ciudad) for ciudad in CIUDADES_POR_REGION.get(region, [])]