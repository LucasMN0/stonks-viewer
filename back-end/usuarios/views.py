from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
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
from decimal import Decimal, InvalidOperation

from .forms import LoginForm
from .models import CustomUser, Transacao, MetaFinanceira, Lembrete


# =========================
# AUTENTICAÇÃO
# =========================
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            if user:
                login(request, user)
                return redirect('perfil')
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
        try:
            validate_password(password)
        except ValidationError as e:
            errors.extend(e.messages)
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
            messages.error(request, "E-mail não encontrado.")
            return redirect('recuperar')
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_url = request.build_absolute_uri(
            reverse("password_reset_confirm", kwargs={'uidb64': uid, 'token': token})
        )
        assunto = "Redefinição de senha - StonksViewer"
        mensagem = (
            f"Olá {user.first_name},\n\n"
            f"Clique para redefinir sua senha:\n{reset_url}\n\n"
            f"Se você não solicitou isso, ignore este e-mail."
        )
        send_mail(assunto, mensagem, None, [email], fail_silently=False)
        messages.success(request, "Um link foi enviado ao seu email.")
        return redirect('login')
    return render(request, 'usuarios/recuperar.html')


def redefinir_senha(request, uidb64, token):
    User = get_user_model()
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except:
        user = None
    if not (user and default_token_generator.check_token(user, token)):
        messages.error(request, "Link inválido ou expirado.")
        return redirect('recuperar')
    if request.method == "POST":
        new_password = request.POST.get('novaSenha')
        confirm_password = request.POST.get('confirmarSenha')
        if new_password != confirm_password:
            messages.error(request, "As senhas não coincidem.")
            return redirect(request.path)
        try:
            validate_password(new_password, user)
            user.set_password(new_password)
            user.save()
            messages.success(request, "Senha redefinida!")
            return redirect('login')
        except ValidationError as e:
            for msg in e.messages:
                messages.error(request, msg)
            return redirect(request.path)
    return render(request, 'usuarios/reset_password_form.html')


def sair_view(request):
    logout(request)
    return redirect('login')


@login_required
def perfil(request):
    return render(request, 'usuarios/perfil.html')


@login_required
def dashboard(request):
    transacoes = Transacao.objects.filter(usuario=request.user)
    ganhos = sum([t.valor for t in transacoes if t.tipo == 'income'])
    gastos = sum([t.valor for t in transacoes if t.tipo == 'expense'])
    saldo = ganhos - gastos
    return render(request, 'usuarios/perfil.html', {
        'ganhos': ganhos,
        'gastos': gastos,
        'saldo': saldo,
        'transacoes': transacoes,
    })


# =========================
# TRANSAÇÕES
# =========================
@login_required
def listar_transacoes(request):
    transacoes = Transacao.objects.filter(usuario=request.user).order_by('-data')
    data = [
        {
            'id': t.id,
            'data': t.data.strftime('%Y-%m-%d'),
            'descricao': t.descricao,
            'valor': float(t.valor),
            'tipo': t.tipo,
        }
        for t in transacoes
    ]
    return JsonResponse({'transacoes': data})


@csrf_exempt
@login_required
def adicionar_transacao(request):
    if request.method != "POST":
        return JsonResponse({'error': "Método inválido"}, status=405)
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
                'tipo': t.tipo,
            }
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
@login_required
def excluir_transacao(request, transacao_id):
    if request.method != "DELETE":
        return JsonResponse({'error': "Método inválido"}, status=405)
    transacao = get_object_or_404(Transacao, id=transacao_id, usuario=request.user)
    transacao.delete()
    return JsonResponse({'status': 'ok'})


# NOVA VIEW: EDITAR TRANSAÇÃO
@csrf_exempt
@login_required
def editar_transacao(request, transacao_id):
    if request.method not in ["PATCH", "POST"]:
        return JsonResponse({'error': "Método inválido"}, status=405)
    transacao = get_object_or_404(Transacao, id=transacao_id, usuario=request.user)
    try:
        body = json.loads(request.body)
        descricao = body.get('descricao')
        valor = body.get('valor')
        tipo = body.get('tipo')

        if descricao is not None:
            transacao.descricao = descricao
        if valor is not None:
            try:
                transacao.valor = Decimal(str(valor))
            except (InvalidOperation, TypeError, ValueError):
                return JsonResponse({'error': 'Valor inválido'}, status=400)
        if tipo is not None:
            transacao.tipo = tipo

        transacao.save()
        return JsonResponse({
            'status': 'ok',
            'transacao': {
                'id': transacao.id,
                'data': transacao.data.strftime('%Y-%m-%d'),
                'descricao': transacao.descricao,
                'valor': float(transacao.valor),
                'tipo': transacao.tipo,
            }
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

# =========================
# METAS FINANCEIRAS
# =========================
@login_required
def listar_metas(request):
    return render(request, 'usuarios/metas.html')


@login_required
def listar_metas_json(request):
    metas = MetaFinanceira.objects.filter(usuario=request.user).order_by('-data_criacao')
    data = [
        {
            'id': m.id,
            'nome': m.nome,
            'valor': float(m.valor),
            'valor_atual': float(m.valor_atual),
            'data_inicial': m.data_inicial.strftime('%Y-%m-%d'),
            'data_final': m.data_final.strftime('%Y-%m-%d'),
            'status': m.status,
            'porcentagem': round((m.valor_atual / m.valor) * 100, 1) if m.valor > 0 else 0
        }
        for m in metas
    ]
    return JsonResponse({'metas': data})


@csrf_exempt
@login_required
def adicionar_meta(request):
    if request.method != "POST":
        return JsonResponse({'error': "Método inválido"}, status=405)

    try:
        body = json.loads(request.body)
        nome = body.get('nome')
        valor = body.get('valor')
        data_inicial = body.get('data_inicial')
        data_final = body.get('data_final')

        if not nome or valor is None or not data_inicial or not data_final:
            return JsonResponse({'error': 'Dados incompletos'}, status=400)

        try:
            valor = Decimal(str(valor))
        except (InvalidOperation, TypeError, ValueError):
            return JsonResponse({'error': 'Valor inválido'}, status=400)

        meta = MetaFinanceira.objects.create(
            usuario=request.user,
            nome=nome,
            valor=valor,
            data_inicial=data_inicial,
            data_final=data_final
        )

        return JsonResponse({
            'status': 'ok',
            'meta': {
                'id': meta.id,
                'nome': meta.nome,
                'valor': float(meta.valor),
                'valor_atual': float(meta.valor_atual),
                'data_inicial': meta.data_inicial.strftime('%Y-%m-%d'),
                'data_final': meta.data_final.strftime('%Y-%m-%d'),
                'status': meta.status,
            }
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
@login_required
def adicionar_progresso_meta(request, meta_id):
    if request.method != "POST":
        return JsonResponse({'error': "Método inválido"}, status=405)

    try:
        body = json.loads(request.body)
        valor_add = body.get('valor', 0)

        # converter para Decimal
        try:
            valor_add = Decimal(str(valor_add))
        except (InvalidOperation, TypeError):
            return JsonResponse({'error': "Valor inválido"}, status=400)

        if valor_add <= 0:
            return JsonResponse({'error': "Valor inválido"}, status=400)

        meta = get_object_or_404(MetaFinanceira, id=meta_id, usuario=request.user)
        meta.adicionar_progresso(valor_add)  # salva no banco

        return JsonResponse({
            'status': 'ok',
            'nova_meta': {
                'id': meta.id,
                'valor_atual': float(meta.valor_atual),
                'status': meta.status,
            }
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
@login_required
def excluir_meta(request, meta_id):
    if request.method != "DELETE":
        return JsonResponse({'error': "Método inválido"}, status=405)
    meta = get_object_or_404(MetaFinanceira, id=meta_id, usuario=request.user)
    meta.delete()
    return JsonResponse({'status': 'ok'})


# =========================
# LEMBRETES
# =========================
@login_required
def listar_lembretes(request):
    lembretes = Lembrete.objects.filter(usuario=request.user).order_by('data')
    data = [
        {
            'id': l.id,
            'nome': l.nome,
            'descricao': l.descricao,
            'data': l.data.strftime('%Y-%m-%d'),
        }
        for l in lembretes
    ]
    return JsonResponse({'lembretes': data})


@csrf_exempt
@login_required
def adicionar_lembrete(request):
    if request.method != "POST":
        return JsonResponse({'error': "Método inválido"}, status=405)
    try:
        body = json.loads(request.body)
        l = Lembrete.objects.create(
            usuario=request.user,
            nome=body['nome'],
            descricao=body.get('descricao', ''),
            data=body['data'],
        )
        return JsonResponse({
            'status': 'ok',
            'lembrete': {
                'id': l.id,
                'nome': l.nome,
                'descricao': l.descricao,
                'data': l.data.strftime('%Y-%m-%d'),
            }
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
@login_required
def excluir_lembrete(request, lembrete_id):
    if request.method != "DELETE":
        return JsonResponse({'error': "Método inválido"}, status=405)
    lembrete = get_object_or_404(Lembrete, id=lembrete_id, usuario=request.user)
    lembrete.delete()
    return JsonResponse({'status': 'ok'})
