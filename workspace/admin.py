from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    PerfilProfissional, Usuario, Sala, Recurso,
    PostoDeTrabalho, Reserva, Equipe, ConfiguracaoSala,
)


@admin.register(PerfilProfissional)
class PerfilProfissionalAdmin(admin.ModelAdmin):
    list_display = ['nome', 'descricao']
    search_fields = ['nome']


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ['username', 'email', 'tipo_perfil', 'departamento', 'perfil_profissional']
    list_filter = ['tipo_perfil', 'departamento']
    search_fields = ['username', 'email']
    fieldsets = UserAdmin.fieldsets + (
        ('GrowUp', {'fields': ('tipo_perfil', 'departamento', 'perfil_profissional')}),
    )


@admin.register(Sala)
class SalaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'localizacao', 'capacidade', 'status', 'ativo']
    list_filter = ['status', 'ativo']
    search_fields = ['nome', 'localizacao']


@admin.register(ConfiguracaoSala)
class ConfiguracaoSalaAdmin(admin.ModelAdmin):
    list_display = ['sala', 'hora_abertura', 'hora_fechamento', 'antecedencia_minima_minutos']


@admin.register(Recurso)
class RecursoAdmin(admin.ModelAdmin):
    list_display = ['tipo', 'marca', 'modelo', 'numero_serie', 'sala', 'disponivel']
    list_filter = ['tipo', 'disponivel']
    search_fields = ['marca', 'modelo', 'numero_serie']


@admin.register(PostoDeTrabalho)
class PostoDeTrabalhoAdmin(admin.ModelAdmin):
    list_display = ['id', 'sala', 'tipo', 'coord_x', 'coord_y', 'disponivel', 'tem_maquina']
    list_filter = ['tipo', 'disponivel', 'tem_maquina']


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'posto', 'data_hora_inicio', 'data_hora_fim', 'status']
    list_filter = ['status']
    search_fields = ['usuario__username']


@admin.register(Equipe)
class EquipeAdmin(admin.ModelAdmin):
    list_display = ['nome', 'descricao']
    search_fields = ['nome']
    filter_horizontal = ['membros']