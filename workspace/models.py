from django.db import models
from django.core.validators import MinValueValidator

class Sala (models.Model):
    nome = models.CharField (max_length=100)
    localizacao = models.CharField (max_length=100)
    capacidade = models.IntegerField (validators=[MinValueValidator(1)])

    def __str__(self):
        return self.nome