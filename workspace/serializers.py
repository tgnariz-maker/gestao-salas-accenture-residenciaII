from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import Usuario, Sala, Recurso, PostoDeTrabalho, Reserva


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'departamento', 'tipo_perfil']
        read_only_fields = ['id']


class UsuarioCadastroSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = Usuario
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'departamento', 'tipo_perfil', 'password']
        read_only_fields = ['id']

    def create(self, validated_data):
        return Usuario.objects.create_user(**validated_data)


class RecursoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recurso
        fields = ['id', 'tipo', 'marca', 'modelo', 'numero_serie', 'disponivel', 'especificacoes']
        read_only_fields = ['id']

    def validate(self, data):
        tipo = data.get('tipo', getattr(self.instance, 'tipo', None))
        especificacoes = data.get('especificacoes', {})

        campos_obrigatorios = {
            Recurso.Tipo.MONITOR: ['resolucao', 'tamanho_polegadas'],
            Recurso.Tipo.COMPUTADOR: ['processador', 'ram_gb', 'storage_gb'],
            Recurso.Tipo.PROJETOR: ['resolucao', 'lumens'],
            Recurso.Tipo.TELEVISAO: ['tamanho_polegadas'],
            Recurso.Tipo.IMPRESSORA: ['colorida', 'tipo_impressora'],
        }

        obrigatorios = campos_obrigatorios.get(tipo, [])
        faltando = [campo for campo in obrigatorios if campo not in especificacoes]

        if faltando:
            raise serializers.ValidationError(
                {campo: 'Este campo é obrigatório para o tipo selecionado.' for campo in faltando}
            )

        return data


class SalaListSerializer(serializers.ModelSerializer):
    total_postos = serializers.IntegerField(source='postos.count', read_only=True)
    postos_disponiveis = serializers.SerializerMethodField()

    class Meta:
        model = Sala
        fields = [
            'id', 'nome', 'localizacao', 'capacidade', 'status',
            'tem_projetor', 'tem_videoconferencia', 'tem_computadores',
            'tem_televisao', 'tem_impressora', 'total_postos', 'postos_disponiveis'
        ]

    def get_postos_disponiveis(self, obj):
        return obj.postos.filter(disponivel=True).count()


class SalaDetailSerializer(serializers.ModelSerializer):
    recursos = RecursoSerializer(many=True, read_only=True)
    total_postos = serializers.IntegerField(source='postos.count', read_only=True)
    postos_disponiveis = serializers.SerializerMethodField()

    class Meta:
        model = Sala
        fields = [
            'id', 'nome', 'localizacao', 'capacidade', 'status',
            'motivo_manutencao', 'prazo_estimado',
            'tem_projetor', 'tem_videoconferencia', 'tem_computadores',
            'tem_televisao', 'tem_impressora',
            'total_postos', 'postos_disponiveis', 'recursos'
        ]

    def get_postos_disponiveis(self, obj):
        return obj.postos.filter(disponivel=True).count()


class SalaEscritaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sala
        fields = [
            'id', 'nome', 'localizacao', 'capacidade', 'status',
            'motivo_manutencao', 'prazo_estimado',
            'tem_projetor', 'tem_videoconferencia', 'tem_computadores',
            'tem_televisao', 'tem_impressora'
        ]
        read_only_fields = ['id']

    def validate(self, data):
        status = data.get('status', getattr(self.instance, 'status', None))

        if status == Sala.Status.MANUTENCAO:
            motivo = data.get('motivo_manutencao', getattr(self.instance, 'motivo_manutencao', ''))
            prazo = data.get('prazo_estimado', getattr(self.instance, 'prazo_estimado', None))

            if not motivo:
                raise serializers.ValidationError({'motivo_manutencao': 'Obrigatório quando status é Manutenção.'})
            if not prazo:
                raise serializers.ValidationError({'prazo_estimado': 'Obrigatório quando status é Manutenção.'})

        return data


class PostoDeTrabalhoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostoDeTrabalho
        fields = ['id', 'sala', 'coord_x', 'coord_y', 'disponivel']
        read_only_fields = ['id', 'sala']


class ReservaLeituraSerializer(serializers.ModelSerializer):
    usuario = UsuarioSerializer(read_only=True)
    posto = PostoDeTrabalhoSerializer(read_only=True)

    class Meta:
        model = Reserva
        fields = ['id', 'usuario', 'posto', 'data_hora_inicio', 'data_hora_fim', 'status']
        read_only_fields = ['id', 'status']


class ReservaEscritaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reserva
        fields = ['id', 'posto', 'data_hora_inicio', 'data_hora_fim']
        read_only_fields = ['id']

    def validate(self, data):
        inicio = data.get('data_hora_inicio')
        fim = data.get('data_hora_fim')

        if inicio and fim and fim <= inicio:
            raise serializers.ValidationError({'data_hora_fim': 'Deve ser posterior à data/hora de início.'})

        return data