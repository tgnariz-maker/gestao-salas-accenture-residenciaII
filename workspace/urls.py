from django.urls import path
from .views import (
    UsuarioListCreateView, UsuarioMeView,
    SalaListCreateView, SalaDetailView, SalaStatusView,
    PostoListView, PostoDetailView,
    RecursoListView,
    ReservaListCreateView, ReservaCancelView, ReservaHistoricoView,
    HealthView,
)

urlpatterns = [
    path('usuarios/', UsuarioListCreateView.as_view(), name='usuario-list-create'),
    path('usuarios/me/', UsuarioMeView.as_view(), name='usuario-me'),

    path('salas/', SalaListCreateView.as_view(), name='sala-list-create'),
    path('salas/<int:pk>/', SalaDetailView.as_view(), name='sala-detail'),
    path('salas/<int:pk>/status/', SalaStatusView.as_view(), name='sala-status'),
    path('salas/<int:pk>/postos/', PostoListView.as_view(), name='posto-list'),
    path('salas/<int:pk>/recursos/', RecursoListView.as_view(), name='recurso-list'),

    path('postos/<int:pk>/', PostoDetailView.as_view(), name='posto-detail'),

    path('reservas/', ReservaListCreateView.as_view(), name='reserva-list-create'),
    path('reservas/<int:pk>/', ReservaCancelView.as_view(), name='reserva-cancel'),
    path('reservas/historico/', ReservaHistoricoView.as_view(), name='reserva-historico'),

    path('health/', HealthView.as_view(), name='health'),
]