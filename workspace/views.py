from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404

from . import selectors, services
from .models import Sala, PostoDeTrabalho, Reserva
from .permissions import IsAdmin, IsAdminOrReadOnly, IsOwnerOrAdmin
from .serializers import (
    UsuarioSerializer, UsuarioCadastroSerializer,
    SalaListSerializer, SalaDetailSerializer, SalaEscritaSerializer,
    PostoDeTrabalhoSerializer, RecursoSerializer,
    ReservaLeituraSerializer, ReservaEscritaSerializer,
)


class UsuarioListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAdmin()]
        return [AllowAny()]

    def get(self, request):
        usuarios = selectors.get_todos_usuarios()
        serializer = UsuarioSerializer(usuarios, many=True)
        return Response(serializer.data)

    def post(self, request):
        usuario = services.criar_usuario(request.data)
        serializer = UsuarioSerializer(usuario)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UsuarioMeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UsuarioSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        usuario = services.atualizar_perfil(request.user, request.data)
        serializer = UsuarioSerializer(usuario)
        return Response(serializer.data)


class SalaListCreateView(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request):
        filtros = {
            k: v for k, v in request.query_params.items()
            if k in ['status', 'capacidade_min', 'tem_projetor', 'tem_videoconferencia',
                     'tem_computadores', 'tem_televisao', 'tem_impressora']
        }
        salas = selectors.get_todas_salas(filtros or None)
        serializer = SalaListSerializer(salas, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = SalaEscritaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sala = services.criar_sala(serializer.validated_data)
        return Response(SalaDetailSerializer(sala).data, status=status.HTTP_201_CREATED)


class SalaDetailView(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request, pk):
        sala = get_object_or_404(Sala, pk=pk)
        serializer = SalaDetailSerializer(sala)
        return Response(serializer.data)

    def delete(self, request, pk):
        sala = get_object_or_404(Sala, pk=pk)
        services.deletar_sala(sala)
        return Response(status=status.HTTP_204_NO_CONTENT)


class SalaStatusView(APIView):
    permission_classes = [IsAdmin]

    def patch(self, request, pk):
        sala = get_object_or_404(Sala, pk=pk)
        serializer = SalaEscritaSerializer(sala, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        sala = services.atualizar_status_sala(sala, serializer.validated_data)
        return Response(SalaDetailSerializer(sala).data)


class PostoListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        get_object_or_404(Sala, pk=pk)
        postos = selectors.get_postos_by_sala(pk)
        serializer = PostoDeTrabalhoSerializer(postos, many=True)
        return Response(serializer.data)


class PostoDetailView(APIView):
    permission_classes = [IsAdmin]

    def patch(self, request, pk):
        posto = get_object_or_404(PostoDeTrabalho, pk=pk)
        posto = services.atualizar_posto(posto, request.data)
        serializer = PostoDeTrabalhoSerializer(posto)
        return Response(serializer.data)


class RecursoListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        get_object_or_404(Sala, pk=pk)
        recursos = selectors.get_recursos_by_sala(pk)
        serializer = RecursoSerializer(recursos, many=True)
        return Response(serializer.data)


class ReservaListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.tipo_perfil == 'ADMIN':
            reservas = selectors.get_todas_reservas()
        else:
            reservas = selectors.get_reservas_by_usuario(request.user.id)
        serializer = ReservaLeituraSerializer(reservas, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ReservaEscritaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reserva = services.criar_reserva(request.user, serializer.validated_data)
        return Response(ReservaLeituraSerializer(reserva).data, status=status.HTTP_201_CREATED)


class ReservaCancelView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        reserva = get_object_or_404(Reserva, pk=pk)
        self.check_object_permissions(request, reserva)
        services.cancelar_reserva(reserva, request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ReservaHistoricoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.tipo_perfil == 'ADMIN':
            reservas = selectors.get_historico_completo()
        else:
            reservas = selectors.get_historico_by_usuario(request.user.id)
        serializer = ReservaLeituraSerializer(reservas, many=True)
        return Response(serializer.data)


class HealthView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({'status': 'ok'})