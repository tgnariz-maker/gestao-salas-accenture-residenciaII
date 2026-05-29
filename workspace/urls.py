from django.urls import path
from .views import (
    PerfilProfissionalListCreateView, PerfilProfissionalDetailView,
    UsuarioListCreateView, UsuarioMeView,
    SalaListCreateView, SalaDetailView, SalaStatusView,
    PostoListView, PostoDetailView, PostoSugestaoView,
    RecursoListView,
    ReservaListCreateView, ReservaCancelView, ReservaHistoricoView,
    IAMapearView, IARotularPostoView, IAEditarLayoutView,
    HealthView,
)

urlpatterns = [
    # Health
    path('health/', HealthView.as_view(), name='health'),

    # Perfis profissionais
    path('perfis/', PerfilProfissionalListCreateView.as_view(), name='perfis-list-create'),
    path('perfis/<int:pk>/', PerfilProfissionalDetailView.as_view(), name='perfis-detail'),

    # Usuários
    path('usuarios/', UsuarioListCreateView.as_view(), name='usuarios-list-create'),
    path('usuarios/me/', UsuarioMeView.as_view(), name='usuarios-me'),

    # Salas
    path('salas/', SalaListCreateView.as_view(), name='salas-list-create'),
    path('salas/<int:pk>/', SalaDetailView.as_view(), name='salas-detail'),
    path('salas/<int:pk>/status/', SalaStatusView.as_view(), name='salas-status'),
    path('salas/<int:pk>/postos/', PostoListView.as_view(), name='postos-list'),
    path('salas/<int:pk>/recursos/', RecursoListView.as_view(), name='recursos-list'),

    # Postos
    path('postos/sugestoes/', PostoSugestaoView.as_view(), name='postos-sugestoes'),
    path('postos/<int:pk>/', PostoDetailView.as_view(), name='postos-detail'),

    # Reservas
    path('reservas/', ReservaListCreateView.as_view(), name='reservas-list-create'),
    path('reservas/historico/', ReservaHistoricoView.as_view(), name='reservas-historico'),
    path('reservas/<int:pk>/', ReservaCancelView.as_view(), name='reservas-cancel'),

    # IA
    path('ia/mapear/', IAMapearView.as_view(), name='ia-mapear'),
    path('ia/postos/<int:pk>/rotular/', IARotularPostoView.as_view(), name='ia-rotular-posto'),
    path('ia/layout/<int:pk>/editar/', IAEditarLayoutView.as_view(), name='ia-editar-layout'),
]