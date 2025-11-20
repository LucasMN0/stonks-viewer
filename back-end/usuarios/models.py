from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


# ============================================================
# USER MODEL
# ============================================================

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, first_name=None, **extra_fields):
        if not email:
            raise ValueError("Este Campo é obrigatório.")
        if not password:
            raise ValueError("Este Campo é obrigatório.")
        if not first_name:
            raise ValueError("Este Campo é obrigatório.")

        email = self.normalize_email(email)
        user = self.model(email=email, first_name=first_name, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, first_name="Admin", **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, first_name, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"

    def __str__(self):
        return self.email


# ============================================================
# TRANSAÇÕES
# ============================================================

class Transacao(models.Model):
    TIPO_CHOICES = [
        ("income", "Ganho fixo"),
        ("investment", "Ganho extra"),
        ("expense", "Gasto fixo"),
        ("extra", "Gasto extra"),
        ("other", "Outro"),
    ]

    usuario = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="transacoes")
    data = models.DateField()
    descricao = models.CharField(max_length=255)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)

    class Meta:
        verbose_name = "Transação"
        verbose_name_plural = "Transações"

    def __str__(self):
        return f"{self.descricao} - {self.valor}"


# ============================================================
# METAS FINANCEIRAS (ajustado para funcionar com as views)
# ============================================================

class MetaFinanceira(models.Model):
    STATUS_CHOICES = [
        ("Pendente", "Pendente"),
        ("Em andamento", "Em andamento"),
        ("Concluída", "Concluída"),
    ]

    usuario = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="metas")

    nome = models.CharField(max_length=255)
    valor = models.DecimalField(max_digits=10, decimal_places=2)       # valor alvo
    valor_atual = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    data_inicial = models.DateField()
    data_final = models.DateField()
    data_criacao = models.DateTimeField(auto_now_add=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pendente")

    class Meta:
        verbose_name = "Meta Financeira"
        verbose_name_plural = "Metas Financeiras"

    def __str__(self):
        return self.nome

    # ===========================================
    # FUNÇÃO QUE AS VIEWS VÃO USAR DIRETAMENTE
    # ===========================================
    def adicionar_progresso(self, valor):
        """Adiciona progresso e atualiza status automaticamente."""
        self.valor_atual += valor

        if self.valor_atual <= 0:
            self.valor_atual = 0

        if self.valor_atual >= self.valor:
            self.valor_atual = self.valor
            self.status = "Concluída"
        elif self.valor_atual > 0:
            self.status = "Em andamento"
        else:
            self.status = "Pendente"

        self.save()


# ============================================================
# LEMBRETES
# ============================================================

class Lembrete(models.Model):
    usuario = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="lembretes")
    nome = models.CharField(max_length=255)
    descricao = models.TextField(blank=True)
    data = models.DateField()

    class Meta:
        verbose_name = "Lembrete"
        verbose_name_plural = "Lembretes"

    def __str__(self):
        return self.nome
