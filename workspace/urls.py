from django.urls import path
from .views import (
    PerfilProfissionalListCreateView, PerfilProfissionalDetailView,
    UsuarioListCreateView, UsuarioMeView,
    SalaListCreateView, SalaDetailView, SalaStatusView,
    PostoListView, PostoDetailView, PostoSugestaoView, PostoSugestaoEquipeView,
    RecursoListView,
    ReservaListCreateView, ReservaCancelView, ReservaHistoricoView,
    IAMapearView, IARotularPostoView, IAEditarLayoutView,
    HealthView,
)

urlpatterns = [
    path('health/', HealthView.as_view(), name='health'),

    path('perfis/', PerfilProfissionalListCreateView.as_view(), name='perfis-list-create'),
    path('perfis/<int:pk>/', PerfilProfissionalDetailView.as_view(), name='perfis-detail'),

    path('usuarios/', UsuarioListCreateView.as_view(), name='usuarios-list-create'),
    path('usuarios/me/', UsuarioMeView.as_view(), name='usuarios-me'),

    path('salas/', SalaListCreateView.as_view(), name='salas-list-create'),
    path('salas/<int:pk>/', SalaDetailView.as_view(), name='salas-detail'),
    path('salas/<int:pk>/status/', SalaStatusView.as_view(), name='salas-status'),
    path('salas/<int:pk>/posicoes/', PostoListView.as_view(), name='posicoes-list'),
    path('salas/<int:pk>/recursos/', RecursoListView.as_view(), name='recursos-list'),

    path('posicoes/sugestoes/', PostoSugestaoView.as_view(), name='posicoes-sugestoes'),
    path('posicoes/sugestoes/equipe/', PostoSugestaoEquipeView.as_view(), name='posicoes-sugestoes-equipe'),
    path('posicoes/<int:pk>/', PostoDetailView.as_view(), name='posicoes-detail'),

    path('reservas/', ReservaListCreateView.as_view(), name='reservas-list-create'),
    path('reservas/historico/', ReservaHistoricoView.as_view(), name='reservas-historico'),
    path('reservas/<int:pk>/', ReservaCancelView.as_view(), name='reservas-cancel'),

    path('ia/mapear/', IAMapearView.as_view(), name='ia-mapear'),
    path('ia/posicoes/<int:pk>/rotular/', IARotularPostoView.as_view(), name='ia-rotular-posicao'),
    path('ia/layout/<int:pk>/editar/', IAEditarLayoutView.as_view(), name='ia-editar-layout'),
]