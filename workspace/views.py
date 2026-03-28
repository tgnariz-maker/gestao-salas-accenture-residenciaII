from rest_framework import generics
from .models import Sala
from .serializers import SalaSerializer

class SalaListCreate(generics.ListCreateAPIView):
    queryset = Sala.objects.all()
    serializer_class = SalaSerializer