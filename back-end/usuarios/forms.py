from django import forms

class LoginForm(forms.Form):
    email = forms.EmailField(label='E-mail', widget=forms.EmailInput(attrs={
        'placeholder': 'E-mail',
        'required': True
    }))
    password = forms.CharField(label='Senha', widget=forms.PasswordInput(attrs={
        'placeholder': 'Senha',
        'required': True
    }))
