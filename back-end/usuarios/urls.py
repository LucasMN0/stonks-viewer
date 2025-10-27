
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('cadastro/', views.cadastro, name='cadastro'),
    path('perfil/',views.perfil, name = 'perfil'),
    #path('sobre/', views.sobre_view, name='sobre'),
    path('recuperar-senha/', views.recuperar_senha, name='recuperar'),
    path('sair/', views.sair_view, name='sair'),

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
]
