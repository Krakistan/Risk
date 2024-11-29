from django import forms
from .models import Cotizacion
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
        

from .models import DireccionEnvio
from datetime import date

class DireccionEnvioForm(forms.ModelForm):
    class Meta:
        model = DireccionEnvio
        fields = ['direccion', 'ciudad', 'region', 'codigo_postal']
        widgets = {
            'direccion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dirección'}),
            'ciudad': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ciudad'}),
            'region': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Región'}),
            'codigo_postal': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Código Postal'}),
        }