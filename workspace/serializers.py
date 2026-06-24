from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import Usuario, Sala, Recurso, PostoDeTrabalho, Reserva, PerfilProfissional, Equipe, ConfiguracaoSala


class ConfiguracaoSalaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfiguracaoSala
        fields = [
            'id', 'sala', 'dias_funcionamento', 'hora_abertura',
            'hora_fechamento', 'antecedencia_minima_minutos', 'feriados',
        ]
        read_only_fields = ['id', 'sala']

    def validate_dias_funcionamento(self, value):
        invalidos = [d for d in value if d not in range(7)]
        if invalidos:
            raise serializers.ValidationError('Dias válidos: 0 (Segunda) a 6 (Domingo).')
        return value

    def validate(self, data):
        abertura = data.get('hora_abertura')
        fechamento = data.get('hora_fechamento')
        if abertura and fechamento and fechamento <= abertura:
            raise serializers.ValidationError({'hora_fechamento': 'Deve ser posterior à hora de abertura.'})
        return data


class PerfilProfissionalSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerfilProfissional
        fields = ['id', 'nome', 'descricao', 'tipos_recurso_necessarios']
        read_only_fields = ['id']

    def validate_tipos_recurso_necessarios(self, value):
        tipos_validos = [t[0] for t in PerfilProfissional.TIPOS_RECURSO]
        invalidos = [t for t in value if t not in tipos_validos]
        if invalidos:
            raise serializers.ValidationError(
                f'Tipos inválidos: {invalidos}. Escolha entre: {tipos_validos}'
            )
        return value


class UsuarioSerializer(serializers.ModelSerializer):
    perfil_profissional = PerfilProfissionalSerializer(read_only=True)

    class Meta:
        model = Usuario
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'departamento', 'tipo_perfil', 'perfil_profissional']
        read_only_fields = ['id']


class UsuarioCadastroSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = Usuario
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'departamento', 'tipo_perfil', 'perfil_profissional', 'password']
        read_only_fields = ['id']

    def create(self, validated_data):
        return Usuario.objects.create_user(**validated_data)


class EquipeSerializer(serializers.ModelSerializer):
    membros = UsuarioSerializer(many=True, read_only=True)
    membros_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Usuario.objects.all(),
        source='membros',
        write_only=True,
        required=False,
    )

    class Meta:
        model = Equipe
        fields = ['id', 'nome', 'descricao', 'membros', 'membros_ids']
        read_only_fields = ['id']

    def create(self, validated_data):
        membros = validated_data.pop('membros', [])
        equipe = Equipe.objects.create(**validated_data)
        equipe.membros.set(membros)
        return equipe

    def update(self, instance, validated_data):
        membros = validated_data.pop('membros', None)
        for campo, valor in validated_data.items():
            setattr(instance, campo, valor)
        instance.save()
        if membros is not None:
            instance.membros.set(membros)
        return instance


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

    def get_postos_disponiveis(self, obj) -> int:
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

    def get_postos_disponiveis(self, obj) -> int:
        return obj.postos.filter(disponivel=True).count()


class SalaEscritaSerializer(serializers.ModelSerializer):
    capacidade = serializers.IntegerField(required=False, allow_null=True, min_value=1)

    class Meta:
        model = Sala
        fields = [
            'id', 'nome', 'localizacao', 'capacidade', 'status',
            'motivo_manutencao', 'prazo_estimado',
            'tem_projetor', 'tem_videoconferencia', 'tem_computadores',
            'tem_televisao', 'tem_impressora'
        ]
        read_only_fields = ['id']

    def to_internal_value(self, data):
        data = data.copy()
        if 'capacidade' in data and data['capacidade'] == '':
            data['capacidade'] = None
        return super().to_internal_value(data)


class PostoDeTrabalhoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostoDeTrabalho
        fields = ['id', 'sala', 'coord_x', 'coord_y', 'disponivel', 'tem_maquina', 'tipo']
        read_only_fields = ['id', 'sala', 'coord_x', 'coord_y']


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