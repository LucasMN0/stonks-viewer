from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # ================================
    # AUTENTICAÇÃO
    # ================================
    path('', views.login_view, name='login'),
    path('cadastro/', views.cadastro, name='cadastro'),
    path('sair/', views.sair_view, name='sair'),

    # ================================
    # PERFIL
    # ================================
    path('perfil/', views.perfil, name='perfil'),

    # ================================
    # RECUPERAÇÃO DE SENHA (custom)
    # ================================
    path('recuperar-senha/', views.recuperar_senha, name='recuperar'),
    path('reset/<uidb64>/<token>/', views.redefinir_senha, name='password_reset_confirm'),

    # ================================
    # DASHBOARD
    # ================================
    path('dashboard/', views.dashboard, name='dashboard'),

    # ================================
    # TRANSAÇÕES
    # ================================
    path('transacoes/', views.listar_transacoes, name='listar_transacoes'),
    path('transacoes/adicionar/', views.adicionar_transacao, name='adicionar_transacao'),
    path('transacoes/excluir/<int:transacao_id>/', views.excluir_transacao, name='excluir_transacao'),
    path('transacoes/editar/<int:transacao_id>/', views.editar_transacao, name='editar_transacao'),  # NOVA ROTA

    # ================================
    # METAS FINANCEIRAS
    # ================================
    # Página HTML
    path('metas/', views.listar_metas, name='listar_metas'),

    # JSON necessário para carregar metas
    path('metas/listar/', views.listar_metas_json, name='listar_metas_json'),

    # Criar meta
    path('metas/adicionar/', views.adicionar_meta, name='adicionar_meta'),

    # Adicionar progresso
    path('metas/progresso/<int:meta_id>/', views.adicionar_progresso_meta, name='adicionar_progresso_meta'),

    # Excluir meta
    path('metas/excluir/<int:meta_id>/', views.excluir_meta, name='excluir_meta'),

    # ================================
    # LEMBRETES
    # ================================
    path('lembretes/', views.listar_lembretes, name='listar_lembretes'),
    path('lembretes/adicionar/', views.adicionar_lembrete, name='adicionar_lembrete'),
    path('lembretes/excluir/<int:lembrete_id>/', views.excluir_lembrete, name='excluir_lembrete'),
]
