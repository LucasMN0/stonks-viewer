from django.contrib.auth import get_user_model,authenticate, login, logout
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import LoginForm
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
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
def sair_view(request):
    logout(request)  # encerra a sessão do usuário
    return redirect('login')  # redireciona para login após logout

#def sobre_view(request):
    #return render(request, 'usuarios/sobre.html')
def recuperar_senha(request):
    if request.method == "POST":
        email = request.POST.get('email')
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            messages.error(request, "Usuário com esse email não encontrado")
            return redirect('recuperar')
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_url = request.build_absolute_uri(
            reverse("password_reset_confirm",kwargs={'uidb64':uid, 'token':token})
        )
        assunto = "Redefinição de senha de StonksViewer"
        mensagem = (f"olá {user.first_name},\n\n clique no link abaixo para redefinir sua senha: \n{reset_url}\n\n"
                    f"Se Você não solicitou, ingore esse email.")

        send_mail(
            assunto,
            mensagem,
            None,
            [email],
            fail_silently=False
        )

        messages.success(request, f"um link de redefinição de senha foi enviado para esse {user.email}")
        return redirect('login')
    return render(request, 'usuarios/recuperar.html')