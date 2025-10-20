from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import LoginForm
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Bem-vindo, {user.first_name}!')
                return redirect('perfil')  # redireciona para a página de perfil
            else:
                messages.error(request, 'E-mail ou senha inválidos.')
    else:
        form = LoginForm()

    return render(request, 'usuarios/index.html', {'form': form})


def cadastro(request):
    errors = []
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        #validação de senha
        try:
            validate_password(password)
        except ValidationError as e:
            errors = e.messages

        User = get_user_model()
        if User.objects.filter(email=email).exists():
            errors.append("Este email já está cadastrado.")
        if not errors:
            user = User.objects.create_user(email=email,password=password,first_name=first_name)
            login(request,user)
            #redireciona pra página inicial após cadastro
            return redirect('perfil')
    return render(request, 'usuarios/cadastro.html', {'errors': errors})#caso nao cadastre redirecionado para a mesma página

@login_required
def perfil(request):
    return render(request, 'usuarios/perfil.html')

def sair(request):
    logout(request)
    return redirect('login')