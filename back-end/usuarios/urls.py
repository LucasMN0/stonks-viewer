
from django.urls import path
from . import views
urlpatterns = [
    path('', views.login_view, name='login'),
    path('cadastro/', views.cadastro, name='cadastro'),
    path('perfil/',views.perfil, name = 'perfil'),
    path('sobre/', views.sobre_view, name='sobre'),
    path('recuperar-senha/', views.recuperar_senha, name='recuperar'),
    path('sair/', views.sair_view, name='sair'),


    #path('recuperar-senha/', views.recuperar_senha, name='recuperar_senha'),
]
