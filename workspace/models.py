from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.contrib.postgres.fields import ArrayField


class PerfilProfissional(models.Model):
    TIPOS_RECURSO = [
        ('MONITOR', 'Monitor'),
        ('COMPUTADOR', 'Computador'),
        ('PROJETOR', 'Projetor'),
        ('TELEVISAO', 'Televisão'),
        ('IMPRESSORA', 'Impressora'),
    ]

    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True)
    tipos_recurso_necessarios = ArrayField(
        models.CharField(max_length=20, choices=TIPOS_RECURSO),
        default=list,
        blank=True,
    )

    def __str__(self):
        return self.nome


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
    perfil_profissional = models.ForeignKey(
        PerfilProfissional,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='usuarios',
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


class ConfiguracaoSala(models.Model):
    DIAS_SEMANA = [
        (0, 'Segunda'),
        (1, 'Terça'),
        (2, 'Quarta'),
        (3, 'Quinta'),
        (4, 'Sexta'),
        (5, 'Sábado'),
        (6, 'Domingo'),
    ]

    sala = models.OneToOneField(
        'Sala',
        on_delete=models.CASCADE,
        related_name='configuracao',
    )
    dias_funcionamento = ArrayField(
        models.IntegerField(choices=DIAS_SEMANA),
        default=list,
        help_text='Dias da semana em que a sala funciona (0=Segunda, 6=Domingo)',
    )
    hora_abertura = models.TimeField(default='08:00')
    hora_fechamento = models.TimeField(default='18:00')
    antecedencia_minima_minutos = models.IntegerField(
        default=30,
        validators=[MinValueValidator(0)],
    )
    feriados = ArrayField(
        models.DateField(),
        default=list,
        blank=True,
    )

    def __str__(self):
        return f'Configuração — {self.sala.nome}'


class Sala(models.Model):
    class Status(models.TextChoices):
        LIVRE = 'LIVRE', 'Livre'
        RESERVADA = 'RESERVADA', 'Reservada'
        OCUPADA = 'OCUPADA', 'Ocupada'
        MANUTENCAO = 'MANUTENCAO', 'Manutenção'

    nome = models.CharField(max_length=100)
    localizacao = models.CharField(max_length=100)
    capacidade = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1)])
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.LIVRE,
    )
    ativo = models.BooleanField(default=True)
    motivo_manutencao = models.TextField(blank=True)
    prazo_estimado = models.DateField(null=True, blank=True)

    tem_projetor = models.BooleanField(default=False)
    tem_videoconferencia = models.BooleanField(default=False)
    tem_computadores = models.BooleanField(default=False)
    tem_televisao = models.BooleanField(default=False)
    tem_impressora = models.BooleanField(default=False)

    def __str__(self):
        return self.nome


class Recurso(models.Model):
    class Tipo(models.TextChoices):
        MONITOR = 'MONITOR', 'Monitor'
        COMPUTADOR = 'COMPUTADOR', 'Computador'
        PROJETOR = 'PROJETOR', 'Projetor'
        TELEVISAO = 'TELEVISAO', 'Televisão'
        IMPRESSORA = 'IMPRESSORA', 'Impressora'

    sala = models.ForeignKey(Sala, on_delete=models.CASCADE, related_name='recursos')
    tipo = models.CharField(max_length=20, choices=Tipo.choices)
    marca = models.CharField(max_length=100)
    modelo = models.CharField(max_length=100)
    numero_serie = models.CharField(max_length=100, unique=True)
    disponivel = models.BooleanField(default=True)
    especificacoes = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f'{self.get_tipo_display()} — {self.marca} {self.modelo}'


class Monitor(Recurso):
    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        self.tipo = Recurso.Tipo.MONITOR
        super().save(*args, **kwargs)


class Computador(Recurso):
    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        self.tipo = Recurso.Tipo.COMPUTADOR
        super().save(*args, **kwargs)


class Projetor(Recurso):
    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        self.tipo = Recurso.Tipo.PROJETOR
        super().save(*args, **kwargs)


class Televisao(Recurso):
    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        self.tipo = Recurso.Tipo.TELEVISAO
        super().save(*args, **kwargs)


class Impressora(Recurso):
    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        self.tipo = Recurso.Tipo.IMPRESSORA
        super().save(*args, **kwargs)


class PostoDeTrabalho(models.Model):
    class Tipo(models.TextChoices):
        INDIVIDUAL = 'INDIVIDUAL', 'Posto Individual'
        REUNIAO = 'REUNIAO', 'Sala de Reunião'
        COLABORATIVO = 'COLABORATIVO', 'Espaço Colaborativo'

    sala = models.ForeignKey(Sala, on_delete=models.CASCADE, related_name='postos')
    coord_x = models.IntegerField()
    coord_y = models.IntegerField()
    disponivel = models.BooleanField(default=True)
    tem_maquina = models.BooleanField(default=True)
    tipo = models.CharField(
        max_length=20,
        choices=Tipo.choices,
        default=Tipo.INDIVIDUAL,
    )

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


class Equipe(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True)
    membros = models.ManyToManyField(
        Usuario,
        related_name='equipes',
        blank=True,
    )

    def __str__(self):
        return self.nome