# GrowUp API

Plataforma backend para gestão de espaços corporativos. Centraliza o controle de salas e postos de trabalho com mapeamento automático via IA e sugestão inteligente de posições.

**Cliente:** Accenture | **Squad:** 25 | **Residência:** II — UNIT/Porto Digital

---

## Stack

| Componente | Tecnologia |
|---|---|
| Linguagem | Python 3.12 |
| Framework | Django 6 + Django REST Framework |
| Banco de dados | PostgreSQL 17 |
| Autenticação | SAML via Keycloak |
| IA | OpenCV + Celery + Redis |
| Documentação | Swagger via drf-spectacular |
| Testes | pytest-django + factory-boy |
| Deploy | Docker |

---

## Pré-requisitos

- Docker Desktop
- Git

---

## Instalação

### 1. Clonar o repositório

```bash
git clone https://github.com/tgnariz-maker/gestao-salas-accenture-residenciaII.git
cd gestao-salas-accenture-residenciaII
```

### 2. Configurar variáveis de ambiente

```bash
cp .env.example .env
```

Preencha o `.env` com os valores do seu ambiente. Os campos obrigatórios são `SECRET_KEY`, `KEYCLOAK_OIDC_CLIENT_SECRET`, `SAML_X509_CERT` e `KEYCLOAK_USERS_PASSWORD`.

### 3. Subir os containers

```bash
docker compose up --build -d
```

Isso sobe 5 containers: `db`, `db_keycloak`, `keycloak`, `web` e `celery_worker`.

> O Keycloak leva aproximadamente 60 segundos para inicializar. O container `web` aguarda automaticamente via healthcheck.

### 4. Configurar o Keycloak

Acesse `http://localhost:8080` com `admin / admin` e configure:

**Realm:**
- Criar realm `growup`

**Cliente SAML (`growup`):**
- Client type: SAML
- Valid redirect URIs: `http://localhost:8000/*`
- Master SAML Processing URL: `http://localhost:8000/api/v1/saml/acs/`
- Client signature required: OFF

**Cliente OIDC (`growup-api`):**
- Client type: OpenID Connect
- Client authentication: ON
- Service account roles: ON
- Direct access grants: ON
- Copiar o Client secret → preencher `KEYCLOAK_OIDC_CLIENT_SECRET` no `.env`

**Usuários de teste:**
- `admin_growup` / senha definida em `KEYCLOAK_USERS_PASSWORD` — email: `admin@growup.com`
- `felipe_growup` / senha definida em `KEYCLOAK_USERS_PASSWORD` — email: `felipe@growup.com`

**Certificado X509:**
- Realm settings → Keys → RS256 → Certificate
- Copiar o valor e preencher `SAML_X509_CERT` no `.env`

> O certificado muda a cada `docker compose down -v`. Em desenvolvimento, evite usar `-v`.

### 5. Reconstruir após atualizar o .env

```bash
docker compose up --build -d
```

### 6. Popular o banco com dados de demonstração

```bash
docker compose exec web python manage.py seed
```

---

## Acesso

| Serviço | URL |
|---|---|
| Swagger | http://localhost:8000/api/docs/ |
| Keycloak | http://localhost:8080 |
| Login SAML | http://localhost:8000/api/v1/saml/login/ |

---

## Autenticação

O sistema usa SAML via Keycloak. O fluxo é:

1. Acesse `GET /api/v1/saml/login/` — redireciona para o Keycloak
2. Faça login com as credenciais do usuário de teste
3. O ACS retorna um `access_token` e redireciona para o frontend
4. Use o token no header: `Authorization: Bearer <access_token>`
5. No Swagger, clique em **Authorize** e cole o token

---

## Comandos úteis

```bash
# Subir containers
docker compose up --build -d

# Parar containers (preserva volumes)
docker compose down

# Parar containers e apagar volumes do Django (Keycloak perde configuração)
docker compose down -v

# Logs da API
docker compose logs web --tail=50

# Logs do Celery
docker compose logs celery_worker --tail=50

# Migrations
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate

# Testes
docker compose exec web pytest

# Seed
docker compose exec web python manage.py seed

# Arquivos estáticos (necessário antes do deploy em produção)
docker compose exec web python manage.py collectstatic --no-input

# Copiar migration gerada no container para o projeto local (Windows)
[System.IO.File]::WriteAllText(
    "workspace\migrations\NOME_DA_MIGRATION.py",
    (docker compose exec web cat workspace/migrations/NOME_DA_MIGRATION.py),
    [System.Text.Encoding]::UTF8
)
```

---

## Testes

74 testes automatizados cobrindo:

- Modelos e validações
- Regras de negócio (reservas, cancelamentos, soft delete)
- Endpoints (autenticação, RBAC, CRUD)
- Perfis, equipes, posições e health check

```bash
docker compose exec web pytest
```

---

## Arquitetura

```
PROJETO_RESIDENCY/
├── core/
│   ├── __init__.py       # Importa o app Celery
│   ├── asgi.py
│   ├── celery.py         # Configuração do Celery
│   ├── settings.py       # Configurações globais
│   ├── urls.py           # Roteamento principal
│   └── wsgi.py
├── logs/
│   ├── .gitkeep
│   └── growup.log        # Gerado em runtime — não versionar
├── staticfiles/          # Gerado por collectstatic — não versionar
├── tests/
│   ├── __init__.py
│   ├── conftest.py       # Fixtures de autenticação e setup
│   ├── factories.py      # Factories para criação de objetos nos testes
│   ├── test_services.py  # Testes de models e regras de negócio
│   └── test_views.py     # Testes de endpoints
├── workspace/
│   ├── management/
│   │   └── commands/
│   │       ├── __init__.py
│   │       └── seed.py       # Dados de demonstração
│   ├── migrations/
│   │   ├── 0001_initial.py
│   │   ├── 0002_computador_impressora_monitor...
│   │   ├── 0003_alter_recurso_marca...
│   │   ├── 0004_perfilprofissional_usuario_perfil...
│   │   ├── 0005_postodetrabalho_tem_maquina...
│   │   ├── 0006_alter_postodetrabalho_tipo.py
│   │   ├── 0007_alter_postodetrabalho_tipo_confi...
│   │   ├── 0008_alter_configuracaosala_dias_func...
│   │   ├── 0009_alter_configuracaosala_dias_func...
│   │   └── 0010_alter_configuracaosala_dias_func...
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── authentication.py # Validação Bearer token Keycloak
│   ├── exceptions.py     # Erros padronizados
│   ├── models.py         # Entidades do banco
│   ├── permissions.py    # RBAC
│   ├── saml_urls.py      # Roteamento SAML
│   ├── saml_utils.py     # Configuração e utilitários SAML
│   ├── saml_views.py     # Views de autenticação SAML
│   ├── selectors.py      # Queries ao banco
│   ├── serializers.py    # Validação e formatação
│   ├── services.py       # Lógica de negócio
│   ├── tasks.py          # Tasks assíncronas (Celery)
│   ├── urls.py           # Roteamento
│   └── views.py          # Endpoints
├── .dockerignore
├── .env
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── Makefile
├── manage.py
├── pyproject.toml
├── pytest.ini
├── README.md
├── requirements-dev.txt
└── requirements.txt
```

---

## Endpoints principais

| Método | Endpoint | Descrição |
|---|---|---|
| GET | /api/v1/saml/login/ | Login via SAML |
| GET | /api/v1/salas/ | Lista salas |
| POST | /api/v1/salas/ | Cria sala (Admin) |
| GET | /api/v1/salas/{id}/disponibilidade/ | Disponibilidade por data |
| GET | /api/v1/salas/{id}/layout-preview/ | Resultado do mapeamento IA |
| POST | /api/v1/ia/mapear/ | Mapeia planta baixa (assíncrono) |
| GET | /api/v1/posicoes/sugestoes/ | Sugestão por perfil |
| GET | /api/v1/posicoes/sugestoes/equipe/ | Sugestão por equipe |
| POST | /api/v1/reservas/ | Cria reserva |
| GET | /api/v1/equipes/ | Lista equipes |

Documentação completa: `http://localhost:8000/api/docs/`

---

## Repositório

[github.com/tgnariz-maker/gestao-salas-accenture-residenciaII](https://github.com/tgnariz-maker/gestao-salas-accenture-residenciaII)