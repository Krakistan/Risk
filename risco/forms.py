from django import forms
from .models import Ciudad, Cotizacion, DireccionEnvio, Region
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from .backends import EmailBackend

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


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label="Correo Electrónico")

class CotizacionForm(forms.ModelForm):
    class Meta:
        model = Cotizacion
        fields = ['nombre', 'correo', 'telefono', 'mensaje']
        labels = {
            'nombre': 'Nombre',
            'email': 'Email',
            'telefono': 'Teléfono',
            'mensaje': 'Comentarios o preguntas',    
        }
        

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
        self.fields['region'].choices = [
            ('Arica y Parinacota', 'Arica y Parinacota'),
            ('Tarapacá', 'Tarapacá'),
            ('Antofagasta', 'Antofagasta'),
            ('Atacama', 'Atacama'),
            ('Coquimbo', 'Coquimbo'),
            ('Valparaíso', 'Valparaíso'),
            ('Santiago', 'Santiago'),
            ('Libertador General Bernardo O\'Higgins', 'Libertador General Bernardo O\'Higgins'),
            ('Maule', 'Maule'),
            ('Ñuble', 'Ñuble'),
            ('Biobío', 'Biobío'),
            ('La Araucanía', 'La Araucanía'),
            ('Los Ríos', 'Los Ríos'),
            ('Los Lagos', 'Los Lagos'),
            ('Aysén del General Carlos Ibáñez del Campo', 'Aysén del General Carlos Ibáñez del Campo'),
            ('Magallanes y de la Antártica Chilena', 'Magallanes y de la Antártica Chilena'),
        ]

        self.fields['ciudad'].choices = [
            ('Arica', 'Arica'),
            ('Iquique', 'Iquique'),
            ('Antofagasta', 'Antofagasta'),
            ('Calama', 'Calama'),
            ('Copiapó', 'Copiapó'),
            ('La Serena', 'La Serena'),
            ('Coquimbo', 'Coquimbo'),
            ('Valparaíso', 'Valparaíso'),
            ('Viña del Mar', 'Viña del Mar'),
            ('Santiago', 'Santiago'),
            ('Rancagua', 'Rancagua'),
            ('Talca', 'Talca'),
            ('Curicó', 'Curicó'),
            ('Linares', 'Linares'),
            ('Chillán', 'Chillán'),
            ('Los Ángeles', 'Los Ángeles'),
            ('Temuco', 'Temuco'),
            ('Valdivia', 'Valdivia'),
            ('Osorno', 'Osorno'),
            ('Puerto Montt', 'Puerto Montt'),
            ('Coyhaique', 'Coyhaique'),
            ('Punta Arenas', 'Punta Arenas'),
        ]

        

class DireccionEnvio(forms.ModelForm):
    class Meta:
        model = DireccionEnvio
        fields = ['direccion', 'region', 'ciudad', 'codigo_postal']
        widgets = {
            'direccion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dirección'}),
            'region': forms.Select(attrs={'class': 'form-control'}),
            'ciudad': forms.Select(attrs={'class': 'form-control'}),
            'codigo_postal': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Código Postal'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Cargar las regiones de la base de datos
        self.fields['region'].queryset = Region.objects.all()
        
        # Si ya hay una región seleccionada, cargar las ciudades correspondientes
        if 'region' in self.data:
            try:
                region_id = int(self.data.get('region'))
                self.fields['ciudad'].queryset = Ciudad.objects.filter(region_id=region_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['ciudad'].queryset = self.instance.region.ciudades.all()