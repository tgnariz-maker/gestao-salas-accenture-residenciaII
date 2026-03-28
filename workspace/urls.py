from django.urls import path
from .views import SalaListCreate

urlpatterns = [
    path('salas/', SalaListCreate.as_view(), name='salas-list'),
]