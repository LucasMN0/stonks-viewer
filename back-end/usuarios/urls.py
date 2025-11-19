from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('cadastro/', views.cadastro, name='cadastro'),
    path('perfil/', views.perfil, name='perfil'),
    path('recuperar-senha/', views.recuperar_senha, name='recuperar'),
    path('sair/', views.sair_view, name='sair'),
    path('reset/<uidb64>/<token>/', views.redefinir_senha, name='password_reset_confirm'),


    # Reset de senha usando views do Django
    path(
        'reset_password/',
        auth_views.PasswordResetView.as_view(
            template_name="usuarios/reset_password.html",
            email_template_name="usuarios/reset_password_email.html",
            subject_template_name="usuarios/reset_password_subject.txt",
        ),
        name="reset_password"
    ),
    path(
        'reset_password_sent/',
        auth_views.PasswordResetDoneView.as_view(template_name="usuarios/reset_password_sent.html"),
        name="password_reset_done"
    ),
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(template_name="usuarios/reset_password_form.html"),
        name="password_reset_confirm"
    ),
    path(
        'reset_password_complete/',
        auth_views.PasswordResetCompleteView.as_view(template_name="usuarios/reset_password_complete.html"),
        name="password_reset_complete"
    ),

    path('dashboard/', views.dashboard, name='dashboard'),

    # Transações
    path('transacoes/', views.listar_transacoes, name='listar_transacoes'),
    path('transacoes/adicionar/', views.adicionar_transacao, name='adicionar_transacao'),
    path('transacoes/excluir/<int:transacao_id>/', views.excluir_transacao, name='excluir_transacao'),

    # Metas financeiras
    path('metas/', views.listar_metas, name='listar_metas'),
    path('metas/adicionar/', views.adicionar_meta, name='adicionar_meta'),
    path('metas/excluir/<int:meta_id>/', views.excluir_meta, name='excluir_meta'),

    # Lembretes
    path('lembretes/', views.listar_lembretes, name='listar_lembretes'),
    path('lembretes/adicionar/', views.adicionar_lembrete, name='adicionar_lembrete'),
    path('lembretes/excluir/<int:lembrete_id>/', views.excluir_lembrete, name='excluir_lembrete'),
]
