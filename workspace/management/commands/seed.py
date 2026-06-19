from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta, time, date


class Command(BaseCommand):
    help = 'Popula o banco com dados de demonstração expandidos'

    def handle(self, *args, **kwargs):
        from workspace.models import (
            PerfilProfissional, Usuario, Equipe, Sala,
            PostoDeTrabalho, Reserva, ConfiguracaoSala,
        )

        self.stdout.write('Limpando dados anteriores...')
        Reserva.objects.all().delete()
        PostoDeTrabalho.objects.all().delete()
        ConfiguracaoSala.objects.all().delete()
        Sala.objects.all().delete()
        Equipe.objects.all().delete()
        Usuario.objects.exclude(is_superuser=True).delete()
        PerfilProfissional.objects.all().delete()

        self.stdout.write('Criando perfis profissionais...')
        perfil_dev = PerfilProfissional.objects.create(
            nome='Desenvolvedor',
            descricao='Engenheiro de software backend e frontend',
            tipos_recurso_necessarios=['COMPUTADOR', 'MONITOR'],
        )
        perfil_devops = PerfilProfissional.objects.create(
            nome='DevOps',
            descricao='Infraestrutura, CI/CD e cloud',
            tipos_recurso_necessarios=['COMPUTADOR', 'MONITOR'],
        )
        perfil_designer = PerfilProfissional.objects.create(
            nome='Designer',
            descricao='UX/UI e design de produto',
            tipos_recurso_necessarios=['COMPUTADOR', 'MONITOR'],
        )
        perfil_qa = PerfilProfissional.objects.create(
            nome='QA',
            descricao='Qualidade e testes de software',
            tipos_recurso_necessarios=['COMPUTADOR'],
        )
        perfil_analista = PerfilProfissional.objects.create(
            nome='Analista de Negócios',
            descricao='Levantamento de requisitos e processos',
            tipos_recurso_necessarios=['COMPUTADOR'],
        )
        perfil_consultor = PerfilProfissional.objects.create(
            nome='Consultor',
            descricao='Consultoria estratégica e entrega ao cliente',
            tipos_recurso_necessarios=['COMPUTADOR'],
        )
        perfil_gestor = PerfilProfissional.objects.create(
            nome='Gestor',
            descricao='Gestão de times e projetos',
            tipos_recurso_necessarios=['COMPUTADOR'],
        )
        perfil_visitante = PerfilProfissional.objects.create(
            nome='Visitante',
            descricao='Colaborador externo ou temporário',
            tipos_recurso_necessarios=[],
        )

        self.stdout.write('Criando usuários...')
        admin = Usuario.objects.create_user(
            username='admin@growup.com', email='admin@growup.com',
            password='admin123', tipo_perfil='ADMIN',
            departamento='TI', perfil_profissional=perfil_gestor,
            first_name='Admin', last_name='GrowUp',
        )
        felipe = Usuario.objects.create_user(
            username='felipe@growup.com', email='felipe@growup.com',
            password='felipe123', tipo_perfil='PADRAO',
            departamento='Engenharia', perfil_profissional=perfil_dev,
            first_name='Felipe', last_name='Santos',
        )
        ana = Usuario.objects.create_user(
            username='ana@growup.com', email='ana@growup.com',
            password='ana123', tipo_perfil='PADRAO',
            departamento='Design', perfil_profissional=perfil_designer,
            first_name='Ana', last_name='Lima',
        )
        carlos = Usuario.objects.create_user(
            username='carlos@growup.com', email='carlos@growup.com',
            password='carlos123', tipo_perfil='LIDER',
            departamento='Engenharia', perfil_profissional=perfil_gestor,
            first_name='Carlos', last_name='Oliveira',
        )
        mariana = Usuario.objects.create_user(
            username='mariana@growup.com', email='mariana@growup.com',
            password='mariana123', tipo_perfil='PADRAO',
            departamento='Engenharia', perfil_profissional=perfil_dev,
            first_name='Mariana', last_name='Costa',
        )
        pedro = Usuario.objects.create_user(
            username='pedro@growup.com', email='pedro@growup.com',
            password='pedro123', tipo_perfil='PADRAO',
            departamento='Engenharia', perfil_profissional=perfil_devops,
            first_name='Pedro', last_name='Alves',
        )
        julia = Usuario.objects.create_user(
            username='julia@growup.com', email='julia@growup.com',
            password='julia123', tipo_perfil='PADRAO',
            departamento='Design', perfil_profissional=perfil_designer,
            first_name='Júlia', last_name='Ferreira',
        )
        rafael = Usuario.objects.create_user(
            username='rafael@growup.com', email='rafael@growup.com',
            password='rafael123', tipo_perfil='PADRAO',
            departamento='Qualidade', perfil_profissional=perfil_qa,
            first_name='Rafael', last_name='Mendes',
        )
        beatriz = Usuario.objects.create_user(
            username='beatriz@growup.com', email='beatriz@growup.com',
            password='beatriz123', tipo_perfil='PADRAO',
            departamento='Negócios', perfil_profissional=perfil_analista,
            first_name='Beatriz', last_name='Souza',
        )
        lucas = Usuario.objects.create_user(
            username='lucas@growup.com', email='lucas@growup.com',
            password='lucas123', tipo_perfil='LIDER',
            departamento='Consultoria', perfil_profissional=perfil_consultor,
            first_name='Lucas', last_name='Rocha',
        )
        camila = Usuario.objects.create_user(
            username='camila@growup.com', email='camila@growup.com',
            password='camila123', tipo_perfil='PADRAO',
            departamento='Consultoria', perfil_profissional=perfil_consultor,
            first_name='Camila', last_name='Neves',
        )
        thiago = Usuario.objects.create_user(
            username='thiago@growup.com', email='thiago@growup.com',
            password='thiago123', tipo_perfil='PADRAO',
            departamento='Engenharia', perfil_profissional=perfil_dev,
            first_name='Thiago', last_name='Barbosa',
        )
        visitante = Usuario.objects.create_user(
            username='visitante@growup.com', email='visitante@growup.com',
            password='visitante123', tipo_perfil='PADRAO',
            departamento='', perfil_profissional=perfil_visitante,
            first_name='João', last_name='Visitante',
        )

        self.stdout.write('Criando equipes...')
        squad_backend = Equipe.objects.create(
            nome='Squad Backend',
            descricao='Time de desenvolvimento backend — APIs, banco de dados e infraestrutura',
        )
        squad_backend.membros.set([felipe, mariana, thiago, pedro])

        squad_design = Equipe.objects.create(
            nome='Squad Design',
            descricao='Time de design de produto e experiência do usuário',
        )
        squad_design.membros.set([ana, julia])

        squad_qa = Equipe.objects.create(
            nome='Squad QA',
            descricao='Time de qualidade e testes automatizados',
        )
        squad_qa.membros.set([rafael, beatriz])

        lideranca = Equipe.objects.create(
            nome='Liderança',
            descricao='Gestores e líderes técnicos',
        )
        lideranca.membros.set([carlos, lucas, admin])

        self.stdout.write('Criando salas...')
        sala_a = Sala.objects.create(
            nome='Sala Accenture A1',
            localizacao='Andar 3 — Bloco A',
            capacidade=20,
            status='LIVRE',
            tem_projetor=True,
            tem_videoconferencia=True,
            tem_computadores=True,
        )
        sala_b = Sala.objects.create(
            nome='Sala Accenture B2',
            localizacao='Andar 5 — Bloco B',
            capacidade=15,
            status='LIVRE',
            tem_televisao=True,
            tem_computadores=True,
        )
        sala_c = Sala.objects.create(
            nome='Sala Reunião C3',
            localizacao='Andar 2 — Bloco C',
            capacidade=8,
            status='LIVRE',
            tem_projetor=True,
            tem_videoconferencia=True,
        )
        sala_d = Sala.objects.create(
            nome='Sala Colaborativa D4',
            localizacao='Andar 4 — Bloco D',
            capacidade=12,
            status='LIVRE',
            tem_televisao=True,
        )

        self.stdout.write('Criando configurações de sala...')
        ConfiguracaoSala.objects.create(
            sala=sala_a,
            dias_funcionamento=[0, 1, 2, 3, 4],
            hora_abertura=time(8, 0),
            hora_fechamento=time(20, 0),
            antecedencia_minima_minutos=30,
            feriados=[],
        )
        ConfiguracaoSala.objects.create(
            sala=sala_b,
            dias_funcionamento=[0, 1, 2, 3, 4],
            hora_abertura=time(8, 0),
            hora_fechamento=time(18, 0),
            antecedencia_minima_minutos=30,
            feriados=[],
        )
        ConfiguracaoSala.objects.create(
            sala=sala_c,
            dias_funcionamento=[0, 1, 2, 3, 4],
            hora_abertura=time(9, 0),
            hora_fechamento=time(18, 0),
            antecedencia_minima_minutos=60,
            feriados=[],
        )
        ConfiguracaoSala.objects.create(
            sala=sala_d,
            dias_funcionamento=[0, 1, 2, 3, 4, 5],
            hora_abertura=time(8, 0),
            hora_fechamento=time(22, 0),
            antecedencia_minima_minutos=30,
            feriados=[],
        )

        self.stdout.write('Criando postos de trabalho...')
        postos_a = []
        for i in range(5):
            for j in range(4):
                posto = PostoDeTrabalho.objects.create(
                    sala=sala_a,
                    coord_x=100 + i * 65,
                    coord_y=100 + j * 55,
                    disponivel=True,
                    tem_maquina=True,
                    tipo='INDIVIDUAL',
                )
                postos_a.append(posto)

        postos_b = []
        for i in range(5):
            for j in range(3):
                posto = PostoDeTrabalho.objects.create(
                    sala=sala_b,
                    coord_x=80 + i * 65,
                    coord_y=80 + j * 55,
                    disponivel=True,
                    tem_maquina=True,
                    tipo='INDIVIDUAL',
                )
                postos_b.append(posto)

        postos_c = []
        for i in range(2):
            for j in range(3):
                posto = PostoDeTrabalho.objects.create(
                    sala=sala_c,
                    coord_x=120 + i * 120,
                    coord_y=100 + j * 80,
                    disponivel=True,
                    tem_maquina=False,
                    tipo='REUNIAO',
                )
                postos_c.append(posto)

        postos_d = []
        for i in range(4):
            for j in range(3):
                posto = PostoDeTrabalho.objects.create(
                    sala=sala_d,
                    coord_x=80 + i * 70,
                    coord_y=80 + j * 60,
                    disponivel=True,
                    tem_maquina=False,
                    tipo='COLABORATIVO',
                )
                postos_d.append(posto)

        self.stdout.write('Criando reservas...')
        agora = timezone.now()
        hoje = agora.replace(hour=0, minute=0, second=0, microsecond=0)
        amanha = hoje + timedelta(days=1)
        depois = hoje + timedelta(days=2)

        def reserva(usuario, posto, dia, h_ini, h_fim, status='CONFIRMADA'):
            try:
                Reserva.objects.create(
                    usuario=usuario,
                    posto=posto,
                    data_hora_inicio=dia.replace(hour=h_ini, minute=0),
                    data_hora_fim=dia.replace(hour=h_fim, minute=0),
                    status=status,
                )
            except Exception:
                pass

        # Hoje — Squad Backend na Sala A (manhã)
        reserva(felipe, postos_a[0], agora, 9, 17)
        reserva(mariana, postos_a[1], agora, 9, 17)
        reserva(thiago, postos_a[2], agora, 9, 17)
        reserva(pedro, postos_a[3], agora, 9, 17)

        # Hoje — Squad Design na Sala A (tarde)
        reserva(ana, postos_a[4], agora, 13, 18)
        reserva(julia, postos_a[5], agora, 13, 18)

        # Hoje — QA na Sala B
        reserva(rafael, postos_b[0], agora, 8, 12)
        reserva(beatriz, postos_b[1], agora, 8, 12)

        # Hoje — Reunião de liderança na Sala C
        reserva(carlos, postos_c[0], agora, 10, 12)
        reserva(lucas, postos_c[1], agora, 10, 12)
        reserva(admin, postos_c[2], agora, 10, 12)

        # Hoje — Consultores na Sala D
        reserva(camila, postos_d[0], agora, 14, 18)
        reserva(lucas, postos_d[1], agora, 14, 18)

        # Hoje — Visitante na Sala D
        reserva(visitante, postos_d[2], agora, 9, 11)

        # Amanhã — Squad Backend volta
        reserva(felipe, postos_a[0], amanha, 9, 17)
        reserva(mariana, postos_a[1], amanha, 9, 17)
        reserva(thiago, postos_a[2], amanha, 9, 17)

        # Amanhã — QA Sala B tarde
        reserva(rafael, postos_b[3], amanha, 13, 17)
        reserva(beatriz, postos_b[4], amanha, 13, 17)

        # Amanhã — Design Sala A
        reserva(ana, postos_a[6], amanha, 9, 18)
        reserva(julia, postos_a[7], amanha, 9, 18)

        # Depois de amanhã
        reserva(felipe, postos_a[0], depois, 9, 13)
        reserva(pedro, postos_b[0], depois, 8, 12)
        reserva(camila, postos_d[0], depois, 10, 16)

        # Reservas passadas (já ocorridas)
        ontem = hoje - timedelta(days=1)
        reserva(felipe, postos_a[8], ontem, 9, 17)
        reserva(ana, postos_a[9], ontem, 13, 18)
        reserva(carlos, postos_c[3], ontem, 14, 16)

        # Reserva cancelada
        reserva(rafael, postos_b[5], amanha, 9, 12, status='CANCELADA')

        self.stdout.write(self.style.SUCCESS('\nSeed concluído.'))
        self.stdout.write(f'  Perfis: {PerfilProfissional.objects.count()}')
        self.stdout.write(f'  Usuários: {Usuario.objects.exclude(is_superuser=True).count()}')
        self.stdout.write(f'  Equipes: {Equipe.objects.count()}')
        self.stdout.write(f'  Salas: {Sala.objects.count()}')
        self.stdout.write(f'  Postos: {PostoDeTrabalho.objects.count()}')
        self.stdout.write(f'  Reservas: {Reserva.objects.count()}')
        self.stdout.write('')
        self.stdout.write('Credenciais:')
        self.stdout.write('  admin@growup.com / admin123 (ADMIN)')
        self.stdout.write('  carlos@growup.com / carlos123 (LIDER — Squad Backend)')
        self.stdout.write('  felipe@growup.com / felipe123 (Dev — Squad Backend)')
        self.stdout.write('  ana@growup.com / ana123 (Designer — Squad Design)')
        self.stdout.write('  rafael@growup.com / rafael123 (QA — Squad QA)')
        self.stdout.write('  lucas@growup.com / lucas123 (LIDER — Liderança)')
        self.stdout.write('  visitante@growup.com / visitante123 (Visitante)')