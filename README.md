# GrowUp API

Plataforma para gestão de espaços corporativos. Centraliza o controle de salas e postos de trabalho com mapeamento automático via IA e sugestão inteligente de posições.

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
| Frontend | React + Vite |
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

Edite o `.env` com os valores do seu ambiente. A tabela abaixo descreve cada variável:

| Variável | Descrição | Exemplo |
|---|---|---|
| `SECRET_KEY` | Chave criptográfica interna do Django. Gere com: `python -c "import secrets; print(secrets.token_urlsafe(50))"` | `3C-0DMy0...` |
| `DEBUG` | `True` em desenvolvimento, `False` em produção | `True` |
| `ALLOWED_HOSTS` | Hosts permitidos separados por vírgula | `localhost,127.0.0.1,web` |
| `DB_NAME` | Nome do banco de dados da aplicação | `room_db` |
| `DB_USER` | Usuário do PostgreSQL | `postgres` |
| `DB_PASSWORD` | Senha do PostgreSQL | `postgres` |
| `DB_HOST` | Host do banco (use `db` dentro do Docker) | `db` |
| `DB_PORT` | Porta do PostgreSQL | `5432` |
| `CORS_ALLOWED_ORIGINS` | Origens permitidas para o frontend | `http://localhost:5173` |
| `SAML_IDP_URL` | URL do realm Keycloak | `http://localhost:8080/realms/growup` |
| `SAML_ENTITY_ID` | Entity ID do cliente SAML no Keycloak | `growup` |
| `SAML_ACS_URL` | URL do ACS (Assertion Consumer Service) | `http://localhost:8000/api/v1/saml/acs/` |
| `SAML_X509_CERT` | Certificado X509 do Keycloak. Obtido em: Realm settings → Keys → RS256 → Certificate | `MIICmz...` |
| `FRONTEND_URL` | URL do frontend para redirect pós-login SAML | `http://localhost:5173` |
| `KEYCLOAK_INTERNAL_URL` | URL interna do Keycloak (usada pelo container web) | `http://keycloak:8080/realms/growup` |
| `KEYCLOAK_JWKS_URL` | URL pública dos certificados JWKS do Keycloak | `http://localhost:8080/realms/growup/protocol/openid-connect/certs` |
| `KEYCLOAK_JWKS_URL_INTERNAL` | URL interna dos certificados JWKS | `http://keycloak:8080/realms/growup/protocol/openid-connect/certs` |
| `KEYCLOAK_OIDC_CLIENT_ID` | ID do cliente OIDC no Keycloak | `growup-api` |
| `KEYCLOAK_OIDC_CLIENT_SECRET` | Client secret do cliente OIDC. Obtido em: Clients → growup-api → Credentials → Client Secret | `abc123...` |
| `KEYCLOAK_USERS_PASSWORD` | Senha padrão dos usuários criados pelo seed | `sua_senha` |
| `CELERY_BROKER_URL` | URL do Redis usado como broker do Celery | `redis://redis:6379/0` |

> **Nota sobre a IA:** o módulo de visão computacional usa OpenCV localmente — não requer chave de API externa. As únicas integrações externas são o Keycloak (autenticação) e o Redis (processamento assíncrono), ambos configurados via variáveis acima.

### 3. Subir os containers

```bash
docker compose up --build -d
```

Isso sobe 6 containers: `db`, `db_keycloak`, `keycloak`, `redis`, `web` e `celery_worker`.

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
| Frontend | http://localhost:5173 |

---

## Autenticação

### Via SAML (uso com frontend)

1. Acesse `http://localhost:8000/api/v1/saml/login/` — redireciona para o Keycloak
2. Faça login com as credenciais do usuário de teste
3. O ACS retorna um `access_token` e redireciona para o frontend
4. Use o token no header: `Authorization: Bearer <access_token>`

### Via endpoint direto (uso com Swagger/Postman)

```bash
POST /api/v1/auth/token/
Content-Type: application/json

{
  "username": "admin_growup",
  "password": "sua_senha"
}
```

A resposta retorna o `access_token`. No Swagger, clique em **Authorize** e cole o token.

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

# Limpar cache Redis
docker compose exec redis redis-cli FLUSHDB

# Arquivos estáticos (necessário antes do deploy em produção)
docker compose exec web python manage.py collectstatic --no-input
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
gestao-salas-accenture-residenciaII/
├── core/
│   ├── __init__.py       # Importa o app Celery
│   ├── asgi.py
│   ├── celery.py         # Configuração do Celery
│   ├── settings.py       # Configurações globais
│   ├── urls.py           # Roteamento principal
│   └── wsgi.py
├── logs/
│   └── growup.log        # Gerado em runtime — não versionar
├── staticfiles/          # Gerado por collectstatic — não versionar
├── workspace/
│   ├── management/
│   │   └── commands/
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
│   ├── services.py       # Lógica de negócio + algoritmo OpenCV
│   ├── tasks.py          # Tasks assíncronas (Celery)
│   ├── urls.py           # Roteamento
│   └── views.py          # Endpoints
├── conftest.py
├── factories.py
├── test_services.py
├── test_views.py
├── .env.example
├── docker-compose.yml
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
| POST | /api/v1/auth/token/ | Obter token via usuário/senha (testes) |
| GET | /api/v1/health/ | Status da API |
| GET | /api/v1/salas/ | Lista salas |
| POST | /api/v1/salas/ | Cria sala (Admin) |
| GET | /api/v1/salas/{id}/disponibilidade/ | Disponibilidade por data |
| GET | /api/v1/salas/{id}/layout-preview/ | Resultado do mapeamento IA |
| POST | /api/v1/salas/{id}/posicoes/ | Adiciona posto manualmente (Admin) |
| POST | /api/v1/ia/mapear/ | Mapeia planta baixa (assíncrono) |
| GET | /api/v1/posicoes/sugestoes/ | Sugestão por perfil |
| GET | /api/v1/posicoes/sugestoes/equipe/ | Sugestão por equipe |
| POST | /api/v1/reservas/ | Cria reserva |
| GET | /api/v1/equipes/ | Lista equipes |

Documentação completa: `http://localhost:8000/api/docs/`

---

## Repositório

[github.com/tgnariz-maker/gestao-salas-accenture-residenciaII](https://github.com/tgnariz-maker/gestao-salas-accenture-residenciaII)