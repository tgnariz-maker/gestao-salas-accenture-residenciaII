from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, extend_schema_view

from . import selectors, services
from .models import Sala, PostoDeTrabalho, Reserva, PerfilProfissional
from .permissions import IsAdmin, IsAdminOrReadOnly, IsOwnerOrAdmin
from .serializers import (
    PerfilProfissionalSerializer,
    UsuarioSerializer, UsuarioCadastroSerializer,
    SalaListSerializer, SalaDetailSerializer, SalaEscritaSerializer,
    PostoDeTrabalhoSerializer, RecursoSerializer,
    ReservaLeituraSerializer, ReservaEscritaSerializer,
    EquipeSerializer, ConfiguracaoSalaSerializer,
)


@extend_schema_view(
    get=extend_schema(tags=['perfis'], summary='Lista perfis profissionais', responses=PerfilProfissionalSerializer),
    post=extend_schema(tags=['perfis'], summary='Cria perfil profissional', request=PerfilProfissionalSerializer, responses=PerfilProfissionalSerializer),
)
class PerfilProfissionalListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsAdmin()]

    def get(self, request):
        perfis = selectors.get_todos_perfis_profissionais()
        serializer = PerfilProfissionalSerializer(perfis, many=True)
        return Response(serializer.data)

    def post(self, request):
        perfil = services.criar_perfil_profissional(request.data)
        serializer = PerfilProfissionalSerializer(perfil)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@extend_schema_view(
    patch=extend_schema(tags=['perfis'], summary='Atualiza perfil profissional', request=PerfilProfissionalSerializer, responses=PerfilProfissionalSerializer),
    delete=extend_schema(tags=['perfis'], summary='Remove perfil profissional', responses={204: None}),
)
class PerfilProfissionalDetailView(APIView):
    permission_classes = [IsAdmin]

    def patch(self, request, pk):
        perfil = get_object_or_404(PerfilProfissional, pk=pk)
        perfil = services.atualizar_perfil_profissional(perfil, request.data)
        serializer = PerfilProfissionalSerializer(perfil)
        return Response(serializer.data)

    def delete(self, request, pk):
        perfil = get_object_or_404(PerfilProfissional, pk=pk)
        services.deletar_perfil_profissional(perfil)
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema_view(
    get=extend_schema(tags=['usuarios'], summary='Lista todos os usuários', responses=UsuarioSerializer),
    post=extend_schema(tags=['usuarios'], summary='Cadastra novo usuário', request=UsuarioCadastroSerializer, responses=UsuarioSerializer),
)
class UsuarioListCreateView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        usuarios = selectors.get_todos_usuarios()
        serializer = UsuarioSerializer(usuarios, many=True)
        return Response(serializer.data)

    def post(self, request):
        usuario = services.criar_usuario(request.data)
        serializer = UsuarioSerializer(usuario)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@extend_schema_view(
    get=extend_schema(tags=['usuarios'], summary='Retorna dados do usuário logado', responses=UsuarioSerializer),
    patch=extend_schema(tags=['usuarios'], summary='Atualiza perfil do usuário logado', request=UsuarioSerializer, responses=UsuarioSerializer),
)
class UsuarioMeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UsuarioSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        usuario = services.atualizar_perfil(request.user, request.data)
        serializer = UsuarioSerializer(usuario)
        return Response(serializer.data)


@extend_schema_view(
    get=extend_schema(tags=['salas'], summary='Lista salas com filtros', responses=SalaListSerializer),
    post=extend_schema(tags=['salas'], summary='Cria nova sala', request=SalaEscritaSerializer, responses=SalaDetailSerializer),
)
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


@extend_schema_view(
    get=extend_schema(tags=['salas'], summary='Detalha sala específica', responses=SalaDetailSerializer, operation_id='sala_detalhe'),
    delete=extend_schema(tags=['salas'], summary='Remove sala', responses={204: None}, operation_id='sala_deletar'),
)
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


@extend_schema_view(
    patch=extend_schema(tags=['salas'], summary='Atualiza status da sala', request=SalaEscritaSerializer, responses=SalaDetailSerializer),
)
class SalaStatusView(APIView):
    permission_classes = [IsAdmin]

    def patch(self, request, pk):
        sala = get_object_or_404(Sala, pk=pk)
        serializer = SalaEscritaSerializer(sala, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        sala = services.atualizar_status_sala(sala, serializer.validated_data)
        return Response(SalaDetailSerializer(sala).data)


@extend_schema_view(
    get=extend_schema(tags=['posicoes'], summary='Lista posições de uma sala', responses=PostoDeTrabalhoSerializer),
)
class PostoListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        get_object_or_404(Sala, pk=pk)
        postos = selectors.get_postos_by_sala(pk)
        serializer = PostoDeTrabalhoSerializer(postos, many=True)
        return Response(serializer.data)


@extend_schema_view(
    patch=extend_schema(tags=['posicoes'], summary='Bloqueia ou desbloqueia posição', request=PostoDeTrabalhoSerializer, responses=PostoDeTrabalhoSerializer),
)
class PostoDetailView(APIView):
    permission_classes = [IsAdmin]

    def patch(self, request, pk):
        posto = get_object_or_404(PostoDeTrabalho, pk=pk)
        posto = services.atualizar_posto(posto, request.data)
        serializer = PostoDeTrabalhoSerializer(posto)
        return Response(serializer.data)


@extend_schema_view(
    get=extend_schema(tags=['posicoes'], summary='Sugestões de posições por perfil profissional', responses=PostoDeTrabalhoSerializer),
)
class PostoSugestaoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        postos = selectors.get_sugestoes_por_perfil(request.user)
        serializer = PostoDeTrabalhoSerializer(postos, many=True)
        return Response(serializer.data)


@extend_schema_view(
    get=extend_schema(
        tags=['posicoes'],
        summary='Sugestões de posições por necessidades coletivas da equipe',
        responses=PostoDeTrabalhoSerializer,
        parameters=[
            {
                'name': 'equipe_id',
                'in': 'query',
                'required': True,
                'schema': {'type': 'integer'},
                'description': 'ID da equipe para análise coletiva de necessidades',
            }
        ],
    ),
)
class PostoSugestaoEquipeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        equipe_id = request.query_params.get('equipe_id')
        if not equipe_id:
            return Response(
                {'erro': 'Parâmetro equipe_id é obrigatório.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        postos = selectors.get_sugestoes_por_equipe(request.user, int(equipe_id))
        serializer = PostoDeTrabalhoSerializer(postos, many=True)
        return Response(serializer.data)


@extend_schema_view(
    get=extend_schema(tags=['salas'], summary='Lista recursos de uma sala', responses=RecursoSerializer),
)
class RecursoListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        get_object_or_404(Sala, pk=pk)
        recursos = selectors.get_recursos_by_sala(pk)
        serializer = RecursoSerializer(recursos, many=True)
        return Response(serializer.data)


@extend_schema_view(
    get=extend_schema(tags=['reservas'], summary='Lista reservas do usuário logado', responses=ReservaLeituraSerializer),
    post=extend_schema(tags=['reservas'], summary='Cria nova reserva', request=ReservaEscritaSerializer, responses=ReservaLeituraSerializer),
)
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


@extend_schema_view(
    delete=extend_schema(tags=['reservas'], summary='Cancela reserva', responses={204: None}),
)
class ReservaCancelView(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def delete(self, request, pk):
        reserva = get_object_or_404(Reserva, pk=pk)
        self.check_object_permissions(request, reserva)
        services.cancelar_reserva(reserva, request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema_view(
    get=extend_schema(tags=['reservas'], summary='Histórico de reservas', responses=ReservaLeituraSerializer),
)
class ReservaHistoricoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.tipo_perfil == 'ADMIN':
            reservas = selectors.get_historico_completo()
        else:
            reservas = selectors.get_historico_by_usuario(request.user.id)
        serializer = ReservaLeituraSerializer(reservas, many=True)
        return Response(serializer.data)


@extend_schema(
    tags=['ia'],
    summary='Dispara mapeamento assíncrono de planta baixa',
    description='Recebe imagem de planta baixa e sala_id. O processamento ocorre em background via Celery. Consulte o resultado em GET /api/v1/salas/{id}/layout-preview.',
    request={
        'multipart/form-data': {
            'type': 'object',
            'properties': {
                'imagem': {'type': 'string', 'format': 'binary'},
                'sala_id': {'type': 'integer'},
            },
            'required': ['imagem', 'sala_id'],
        }
    },
    responses={202: {'type': 'object', 'properties': {'mensagem': {'type': 'string'}, 'sala_id': {'type': 'integer'}}}},
)
class IAMapearView(APIView):
    permission_classes = [IsAdmin]
    parser_classes = [MultiPartParser]

    def post(self, request):
        from .tasks import processar_planta_baixa_task

        imagem = request.FILES.get('imagem')
        sala_id = request.data.get('sala_id')

        if not imagem:
            return Response({'erro': 'Campo imagem é obrigatório.'}, status=status.HTTP_400_BAD_REQUEST)
        if not sala_id:
            return Response({'erro': 'Campo sala_id é obrigatório.'}, status=status.HTTP_400_BAD_REQUEST)

        imagem_bytes = imagem.read()
        imagem_hex = imagem_bytes.hex()

        processar_planta_baixa_task.delay(imagem_hex, int(sala_id))

        return Response(
            {'mensagem': 'Processamento iniciado.', 'sala_id': int(sala_id)},
            status=status.HTTP_202_ACCEPTED,
        )


@extend_schema(
    tags=['ia'],
    summary='Consulta resultado do mapeamento assíncrono',
    responses={200: {'type': 'object'}},
)
class IALayoutPreviewView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request, pk):
        from django.core.cache import cache
        cache_key = f'layout_preview:{pk}'
        resultado = cache.get(cache_key)

        if not resultado:
            return Response(
                {'status': 'pending', 'mensagem': 'Processamento ainda não iniciado ou expirado.'},
                status=status.HTTP_200_OK,
            )

        return Response(resultado)


@extend_schema(
    tags=['ia'],
    summary='Confirma ou ajusta layout gerado pela IA',
    request=PostoDeTrabalhoSerializer,
    responses={200: PostoDeTrabalhoSerializer},
)
class IALayoutConfirmarView(APIView):
    permission_classes = [IsAdmin]

    def put(self, request, pk):
        get_object_or_404(Sala, pk=pk)
        postos_data = request.data.get('postos', [])

        if not postos_data:
            return Response({'erro': 'Campo postos é obrigatório.'}, status=status.HTTP_400_BAD_REQUEST)

        postos_atualizados = []
        for posto_data in postos_data:
            posto_id = posto_data.get('id')
            if not posto_id:
                continue
            posto = get_object_or_404(PostoDeTrabalho, pk=posto_id, sala_id=pk)
            for campo in ['coord_x', 'coord_y', 'tipo', 'tem_maquina', 'disponivel']:
                if campo in posto_data:
                    setattr(posto, campo, posto_data[campo])
            posto.save()
            postos_atualizados.append(posto)

        serializer = PostoDeTrabalhoSerializer(postos_atualizados, many=True)
        return Response(serializer.data)


@extend_schema(
    tags=['ia'],
    summary='Rotula ou ajusta manualmente uma posição identificada pela IA',
    request=PostoDeTrabalhoSerializer,
    responses={200: PostoDeTrabalhoSerializer},
)
class IARotularPostoView(APIView):
    permission_classes = [IsAdmin]

    def patch(self, request, pk):
        posto = get_object_or_404(PostoDeTrabalho, pk=pk)
        posto = services.rotular_posto(posto, request.data)
        serializer = PostoDeTrabalhoSerializer(posto)
        return Response(serializer.data)


@extend_schema(
    tags=['ia'],
    summary='Edita layout — reposiciona posição manualmente',
    request=PostoDeTrabalhoSerializer,
    responses={200: PostoDeTrabalhoSerializer},
)
class IAEditarLayoutView(APIView):
    permission_classes = [IsAdmin]

    def patch(self, request, pk):
        posto = get_object_or_404(PostoDeTrabalho, pk=pk)
        campos_permitidos = ['coord_x', 'coord_y', 'tipo', 'tem_maquina', 'disponivel']
        for campo in campos_permitidos:
            if campo in request.data:
                setattr(posto, campo, request.data[campo])
        posto.save()
        serializer = PostoDeTrabalhoSerializer(posto)
        return Response(serializer.data)


@extend_schema(tags=['sistema'], summary='Verifica status da API', responses={200: None})
class HealthView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({'status': 'ok'})


@extend_schema_view(
    get=extend_schema(tags=['equipes'], summary='Lista equipes', responses=EquipeSerializer),
    post=extend_schema(tags=['equipes'], summary='Cria equipe', request=EquipeSerializer, responses=EquipeSerializer),
)
class EquipeListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsAdmin()]

    def get(self, request):
        equipes = selectors.get_todas_equipes()
        serializer = EquipeSerializer(equipes, many=True)
        return Response(serializer.data)

    def post(self, request):
        equipe = services.criar_equipe(request.data)
        serializer = EquipeSerializer(equipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@extend_schema_view(
    get=extend_schema(tags=['equipes'], summary='Detalha equipe', responses=EquipeSerializer),
    patch=extend_schema(tags=['equipes'], summary='Atualiza equipe', request=EquipeSerializer, responses=EquipeSerializer),
    delete=extend_schema(tags=['equipes'], summary='Remove equipe', responses={204: None}),
)
class EquipeDetailView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsAdmin()]

    def get(self, request, pk):
        from .models import Equipe
        equipe = get_object_or_404(Equipe, pk=pk)
        serializer = EquipeSerializer(equipe)
        return Response(serializer.data)

    def patch(self, request, pk):
        from .models import Equipe
        equipe = get_object_or_404(Equipe, pk=pk)
        equipe = services.atualizar_equipe(equipe, request.data)
        serializer = EquipeSerializer(equipe)
        return Response(serializer.data)

    def delete(self, request, pk):
        from .models import Equipe
        equipe = get_object_or_404(Equipe, pk=pk)
        equipe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(
    tags=['salas'],
    summary='Consulta disponibilidade de posições por data',
    parameters=[
        {
            'name': 'data',
            'in': 'query',
            'required': True,
            'schema': {'type': 'string', 'format': 'date'},
            'description': 'Data no formato YYYY-MM-DD',
        }
    ],
    responses={200: {'type': 'object'}},
)
class SalaDisponibilidadeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        data_str = request.query_params.get('data')
        if not data_str:
            return Response(
                {'erro': 'Parâmetro data é obrigatório. Formato: YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            from datetime import date
            data = date.fromisoformat(data_str)
        except ValueError:
            return Response(
                {'erro': 'Formato de data inválido. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        resultado = selectors.get_disponibilidade_sala(pk, data)
        return Response(resultado)


@extend_schema_view(
    get=extend_schema(tags=['salas'], summary='Consulta configuração da sala', responses=ConfiguracaoSalaSerializer),
    put=extend_schema(tags=['salas'], summary='Cria ou atualiza configuração da sala', request=ConfiguracaoSalaSerializer, responses=ConfiguracaoSalaSerializer),
)
class SalaConfiguracaoView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request, pk):
        sala = get_object_or_404(Sala, pk=pk, ativo=True)
        try:
            config = sala.configuracao
            serializer = ConfiguracaoSalaSerializer(config)
            return Response(serializer.data)
        except Exception:
            return Response(
                {'mensagem': 'Configuração não definida. Use PUT para criar.'},
                status=status.HTTP_200_OK,
            )

    def put(self, request, pk):
        sala = get_object_or_404(Sala, pk=pk, ativo=True)
        try:
            config = sala.configuracao
            serializer = ConfiguracaoSalaSerializer(config, data=request.data, partial=True)
        except Exception:
            serializer = ConfiguracaoSalaSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        config = serializer.save(sala=sala)
        return Response(ConfiguracaoSalaSerializer(config).data)