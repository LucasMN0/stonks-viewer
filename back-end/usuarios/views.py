from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .forms import LoginForm

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
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Aqui você pode adicionar validações, criar o usuário, etc.
        User = get_user_model()
        user = User.objects.create_user(email=email, password=password, first_name=first_name)

        # Depois do cadastro, redireciona para alguma página, por exemplo login
        return redirect('login')  # ou qualquer outra página

    return render(request, 'usuarios/cadastro.html')
