from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator


class Usuario(AbstractUser):
    class TipoPerfil(models.TextChoices):
        ADMIN = 'ADMIN', 'Administrador'
        LIDER = 'LIDER', 'Líder'
        PADRAO = 'PADRAO', 'Padrão'

    departamento = models.CharField(max_length=100, blank=True)
    tipo_perfil = models.CharField(
        max_length=20,
        choices=TipoPerfil.choices,
        default=TipoPerfil.PADRAO,
    )
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='usuarios',
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='usuarios',
        blank=True,
    )

    def __str__(self):
        return self.username


class Sala(models.Model):
    class Status(models.TextChoices):
        LIVRE = 'LIVRE', 'Livre'
        RESERVADA = 'RESERVADA', 'Reservada'
        OCUPADA = 'OCUPADA', 'Ocupada'
        MANUTENCAO = 'MANUTENCAO', 'Manutenção'

    nome = models.CharField(max_length=100)
    localizacao = models.CharField(max_length=100)
    capacidade = models.IntegerField(validators=[MinValueValidator(1)])
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.LIVRE,
    )

    def __str__(self):
        return self.nome


class Recurso(models.Model):
    sala = models.ForeignKey(Sala, on_delete=models.CASCADE, related_name='recursos')
    nome = models.CharField(max_length=50)
    tipo = models.CharField(max_length=50)

    def __str__(self):
        return f'{self.tipo} — {self.nome}'


class PostoDeTrabalho(models.Model):
    sala = models.ForeignKey(Sala, on_delete=models.CASCADE, related_name='postos')
    coord_x = models.IntegerField()
    coord_y = models.IntegerField()
    disponivel = models.BooleanField(default=True)

    def __str__(self):
        return f'Posto ({self.coord_x}, {self.coord_y}) — {self.sala.nome}'


class Reserva(models.Model):
    class Status(models.TextChoices):
        CONFIRMADA = 'CONFIRMADA', 'Confirmada'
        CANCELADA = 'CANCELADA', 'Cancelada'
        PENDENTE = 'PENDENTE', 'Pendente'

    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='reservas')
    posto = models.ForeignKey(PostoDeTrabalho, on_delete=models.CASCADE, related_name='reservas')
    data_hora_inicio = models.DateTimeField()
    data_hora_fim = models.DateTimeField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDENTE,
    )

    def __str__(self):
        return f'Reserva {self.usuario.username} — {self.posto}'