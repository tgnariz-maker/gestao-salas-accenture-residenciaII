from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta, time


class Command(BaseCommand):
    help = 'Popula o banco com dados de demonstração'

    def handle(self, *args, **kwargs):
        from workspace.models import (
            PerfilProfissional, Usuario, Equipe, Sala,
            PostoDeTrabalho, Reserva, ConfiguracaoSala,
        )

        self.stdout.write('Limpando dados anteriores de seed...')
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
            descricao='Engenheiro de software',
            tipos_recurso_necessarios=['COMPUTADOR', 'MONITOR'],
        )
        perfil_designer = PerfilProfissional.objects.create(
            nome='Designer',
            descricao='Designer de produto',
            tipos_recurso_necessarios=['COMPUTADOR', 'MONITOR'],
        )
        perfil_gestor = PerfilProfissional.objects.create(
            nome='Gestor',
            descricao='Gerente de projeto',
            tipos_recurso_necessarios=['COMPUTADOR'],
        )
        perfil_visitante = PerfilProfissional.objects.create(
            nome='Visitante',
            descricao='Colaborador externo sem equipamento fixo',
            tipos_recurso_necessarios=[],
        )

        self.stdout.write('Criando usuários...')
        admin = Usuario.objects.create_user(
            username='admin@growup.com',
            email='admin@growup.com',
            password='admin123',
            tipo_perfil='ADMIN',
            departamento='TI',
            perfil_profissional=perfil_gestor,
            first_name='Admin',
            last_name='GrowUp',
        )
        felipe = Usuario.objects.create_user(
            username='felipe@growup.com',
            email='felipe@growup.com',
            password='felipe123',
            tipo_perfil='PADRAO',
            departamento='Engenharia',
            perfil_profissional=perfil_dev,
            first_name='Felipe',
            last_name='Santos',
        )
        ana = Usuario.objects.create_user(
            username='ana@growup.com',
            email='ana@growup.com',
            password='ana123',
            tipo_perfil='PADRAO',
            departamento='Design',
            perfil_profissional=perfil_designer,
            first_name='Ana',
            last_name='Lima',
        )
        carlos = Usuario.objects.create_user(
            username='carlos@growup.com',
            email='carlos@growup.com',
            password='carlos123',
            tipo_perfil='LIDER',
            departamento='Engenharia',
            perfil_profissional=perfil_gestor,
            first_name='Carlos',
            last_name='Oliveira',
        )
        visitante = Usuario.objects.create_user(
            username='visitante@growup.com',
            email='visitante@growup.com',
            password='visitante123',
            tipo_perfil='PADRAO',
            departamento='',
            perfil_profissional=perfil_visitante,
            first_name='João',
            last_name='Visitante',
        )

        self.stdout.write('Criando equipes...')
        equipe_eng = Equipe.objects.create(
            nome='Squad Engenharia',
            descricao='Time de desenvolvimento backend e frontend',
        )
        equipe_eng.membros.set([felipe, carlos])

        equipe_design = Equipe.objects.create(
            nome='Squad Design',
            descricao='Time de design de produto e UX',
        )
        equipe_design.membros.set([ana])

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
            capacidade=10,
            status='LIVRE',
            tem_televisao=True,
        )
        sala_c = Sala.objects.create(
            nome='Sala Reunião C3',
            localizacao='Andar 2 — Bloco C',
            capacidade=8,
            status='LIVRE',
            tem_projetor=True,
        )

        self.stdout.write('Criando configurações de sala...')
        ConfiguracaoSala.objects.create(
            sala=sala_a,
            dias_funcionamento=[0, 1, 2, 3, 4],
            hora_abertura=time(8, 0),
            hora_fechamento=time(18, 0),
            antecedencia_minima_minutos=30,
            feriados=[],
        )
        ConfiguracaoSala.objects.create(
            sala=sala_b,
            dias_funcionamento=[0, 1, 2, 3, 4],
            hora_abertura=time(9, 0),
            hora_fechamento=time(17, 0),
            antecedencia_minima_minutos=60,
            feriados=[],
        )

        self.stdout.write('Criando posições de trabalho...')
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
            for j in range(2):
                posto = PostoDeTrabalho.objects.create(
                    sala=sala_b,
                    coord_x=80 + i * 65,
                    coord_y=80 + j * 55,
                    disponivel=True,
                    tem_maquina=False,
                    tipo='COLABORATIVO',
                )
                postos_b.append(posto)

        self.stdout.write('Criando reservas...')
        agora = timezone.now()
        amanha = agora + timedelta(days=1)

        Reserva.objects.create(
            usuario=felipe,
            posto=postos_a[0],
            data_hora_inicio=amanha.replace(hour=9, minute=0, second=0, microsecond=0),
            data_hora_fim=amanha.replace(hour=12, minute=0, second=0, microsecond=0),
            status='CONFIRMADA',
        )
        Reserva.objects.create(
            usuario=carlos,
            posto=postos_a[1],
            data_hora_inicio=amanha.replace(hour=9, minute=0, second=0, microsecond=0),
            data_hora_fim=amanha.replace(hour=18, minute=0, second=0, microsecond=0),
            status='CONFIRMADA',
        )
        Reserva.objects.create(
            usuario=ana,
            posto=postos_b[0],
            data_hora_inicio=amanha.replace(hour=14, minute=0, second=0, microsecond=0),
            data_hora_fim=amanha.replace(hour=17, minute=0, second=0, microsecond=0),
            status='CONFIRMADA',
        )

        self.stdout.write(self.style.SUCCESS('Seed concluído.'))
        self.stdout.write(f'  Perfis: {PerfilProfissional.objects.count()}')
        self.stdout.write(f'  Usuários: {Usuario.objects.exclude(is_superuser=True).count()}')
        self.stdout.write(f'  Equipes: {Equipe.objects.count()}')
        self.stdout.write(f'  Salas: {Sala.objects.count()}')
        self.stdout.write(f'  Posições: {PostoDeTrabalho.objects.count()}')
        self.stdout.write(f'  Reservas: {Reserva.objects.count()}')
        self.stdout.write('')
        self.stdout.write('Credenciais de teste:')
        self.stdout.write('  admin@growup.com / admin123 (ADMIN)')
        self.stdout.write('  felipe@growup.com / felipe123 (PADRAO)')
        self.stdout.write('  ana@growup.com / ana123 (PADRAO)')
        self.stdout.write('  carlos@growup.com / carlos123 (LIDER)')
        self.stdout.write('  visitante@growup.com / visitante123 (PADRAO)')