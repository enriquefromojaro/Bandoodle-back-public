from django import forms
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class LoginForm(forms.Form):
	usuario = forms.CharField(label='Nombre de usuario')
	password = forms.CharField(label='Contraseña del usuario', widget=forms.PasswordInput)


class PasswordResetForm(forms.Form):
	password = forms.CharField(label='Nueva contraseña', widget=forms.PasswordInput, min_length=8)
	repeated_password = forms.CharField(label='Repita la nueva contraseña', widget=forms.PasswordInput)

	def clean(self):
		super_assertion = super().clean()
		# TODO: Check if the password passes the Django's User conditions for the password
		if self.cleaned_data.get('password') != self.cleaned_data.get('repeated_password'):
			raise ValidationError('Las contraseñas no coinciden')
		return self.cleaned_data

	def is_valid(self, user):
		self.user=user
		return super().is_valid()


