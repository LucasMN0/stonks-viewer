from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from .forms import LoginForm
from .models import CustomUser, Transacao, MetaFinanceira, Lembrete

# ===========================
# AUTENTICAÇÃO
# ===========================

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('perfil')
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

        # Validação de senha
        try:
            validate_password(password)
        except ValidationError as e:
            errors = e.messages

        User = get_user_model()
        if User.objects.filter(email=email).exists():
            errors.append("Este email já está cadastrado.")

        if not errors:
            user = User.objects.create_user(email=email, password=password, first_name=first_name)
            login(request, user)
            return redirect('perfil')

    return render(request, 'usuarios/cadastro.html', {'errors': errors})

def recuperar_senha(request):
    if request.method == "POST":
        email = request.POST.get('email')
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            messages.error(request, "Usuário com esse email não encontrado.")
            return redirect('recuperar')

        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_url = request.build_absolute_uri(
            reverse("password_reset_confirm", kwargs={'uidb64': uid, 'token': token})
        )
        assunto = "Redefinição de senha - StonksViewer"
        mensagem = (
            f"Olá {user.first_name},\n\n"
            f"Clique no link abaixo para redefinir sua senha:\n{reset_url}\n\n"
            f"Se você não solicitou, ignore este e-mail."
        )

        send_mail(assunto, mensagem, None, [email], fail_silently=False)
        messages.success(request, f"Um link de redefinição foi enviado para {user.email}")
        return redirect('login')

    return render(request, 'usuarios/recuperar.html')

def sair_view(request):
    logout(request)
    return redirect('login')

@login_required
def perfil(request):
    return render(request, 'usuarios/perfil.html')

@login_required
def dashboard(request):
    transacoes = Transacao.objects.filter(usuario=request.user)
    ganhos = sum(t.valor for t in transacoes if t.tipo == 'income')
    gastos = sum(t.valor for t in transacoes if t.tipo == 'expense')
    saldo = ganhos - gastos

    return render(request, 'usuarios/perfil.html', {
        'ganhos': ganhos,
        'gastos': gastos,
        'saldo': saldo,
        'transacoes': transacoes,
    })

# ===========================
# TRANSAÇÕES
# ===========================

@login_required
def listar_transacoes(request):
    transacoes = Transacao.objects.filter(usuario=request.user).order_by('-data')
    data = [
        {
            'id': t.id,
            'data': t.data.strftime('%Y-%m-%d'),
            'descricao': t.descricao,
            'valor': float(t.valor),
            'tipo': t.tipo
        }
        for t in transacoes
    ]
    return JsonResponse({'transacoes': data})

@csrf_exempt
@login_required
def adicionar_transacao(request):
    if request.method != "POST":
        return JsonResponse({'error': 'Método inválido'}, status=405)

    try:
        body = json.loads(request.body)
        t = Transacao.objects.create(
            usuario=request.user,
            data=body['data'],
            descricao=body['descricao'],
            valor=body['valor'],
            tipo=body['tipo']
        )
        return JsonResponse({
            'status': 'ok',
            'transacao': {
                'id': t.id,
                'data': t.data.strftime('%Y-%m-%d'),
                'descricao': t.descricao,
                'valor': float(t.valor),
                'tipo': t.tipo
            }
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
@login_required
def excluir_transacao(request, transacao_id):
    if request.method != "DELETE":
        return JsonResponse({'error': 'Método inválido'}, status=405)

    transacao = get_object_or_404(Transacao, id=transacao_id, usuario=request.user)
    transacao.delete()
    return JsonResponse({'status': 'ok'})

# ===========================
# METAS FINANCEIRAS
# ===========================

@login_required
def listar_metas(request):
    metas = MetaFinanceira.objects.filter(usuario=request.user)
    data = [
        {
            'id': m.id,
            'nome': m.nome,
            'valor': float(m.valor),
            'status': m.status
        }
        for m in metas
    ]
    return JsonResponse({'metas': data})

@csrf_exempt
@login_required
def adicionar_meta(request):
    if request.method != "POST":
        return JsonResponse({'error': 'Método inválido'}, status=405)

    try:
        body = json.loads(request.body)
        m = MetaFinanceira.objects.create(
            usuario=request.user,
            nome=body['nome'],
            valor=body['valor']
        )
        return JsonResponse({
            'status': 'ok',
            'meta': {
                'id': m.id,
                'nome': m.nome,
                'valor': float(m.valor),
                'status': m.status
            }
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
@login_required
def excluir_meta(request, meta_id):
    if request.method != "DELETE":
        return JsonResponse({'error': 'Método inválido'}, status=405)

    meta = get_object_or_404(MetaFinanceira, id=meta_id, usuario=request.user)
    meta.delete()
    return JsonResponse({'status': 'ok'})

# ===========================
# LEMBRETES
# ===========================

@login_required
def listar_lembretes(request):
    lembretes = Lembrete.objects.filter(usuario=request.user).order_by('data')
    data = [
        {
            'id': l.id,
            'nome': l.nome,
            'descricao': l.descricao,
            'data': l.data.strftime('%Y-%m-%d')
        }
        for l in lembretes
    ]
    return JsonResponse({'lembretes': data})

@csrf_exempt
@login_required
def adicionar_lembrete(request):
    if request.method != "POST":
        return JsonResponse({'error': 'Método inválido'}, status=405)

    try:
        body = json.loads(request.body)
        l = Lembrete.objects.create(
            usuario=request.user,
            nome=body['nome'],
            descricao=body.get('descricao', ''),
            data=body['data']
        )
        return JsonResponse({
            'status': 'ok',
            'lembrete': {
                'id': l.id,
                'nome': l.nome,
                'descricao': l.descricao,
                'data': l.data.strftime('%Y-%m-%d')
            }
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
@login_required
def excluir_lembrete(request, lembrete_id):
    if request.method != "DELETE":
        return JsonResponse({'error': 'Método inválido'}, status=405)

    lembrete = get_object_or_404(Lembrete, id=lembrete_id, usuario=request.user)
    lembrete.delete()
    return JsonResponse({'status': 'ok'})
