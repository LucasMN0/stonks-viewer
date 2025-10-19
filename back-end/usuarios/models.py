from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class Transacao(models.Model):
    TIPO_CHOICES = [
        ('expense', 'Gasto fixo'),
        ('extra', 'Gasto extra'),
        ('income', 'Ganho fixo'),
        ('investment', 'Ganho extra'),
        ('other', 'Outro'),
    ]
    class Meta:
        verbose_name = 'Transação'
        verbose_name_plural = 'Transações'

    data = models.DateField()
    descricao = models.CharField(max_length=255)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    valor = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.descricao} - {self.valor}"


class MetaFinanceira(models.Model):
    nome = models.CharField(max_length=255)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    concluida = models.BooleanField(default=False)

    def __str__(self):
        return self.nome


class Lembrete(models.Model):
    nome = models.CharField(max_length=255)
    descricao = models.TextField(blank=True)
    data = models.DateField()

    def __str__(self):
        return self.nome


class CustomUserManager(BaseUserManager):
    def create_user(self,email,password=None,first_name=None, **extra_fields):
        if not email:
            raise ValueError("Este Campo é obrigatório.")
        if not password:
            raise ValueError("Este Campo é obrigatório.")
        if not first_name:
            raise ValueError("Este Campo é obrigatório.")
        email = self.normalize_email(email)
        user = self.model(email=email,first_name=first_name, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, first_name='Admin',**extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, first_name, **extra_fields)

class CustomUser(AbstractBaseUser,PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
    def __str__(self):
        return self.email