# Classificacao Service — MedSync

Microsserviço responsável pela **classificação de risco de pacientes** segundo o Protocolo de Manchester. Recebe sinais vitais, aplica regras de negócio e retorna a cor de risco com o tempo de espera estimado. Faz parte do sistema MedSync, desenvolvido no Trabalho Prático 2 da disciplina de DevOps (UDESC Alto Vale).

---

## Requisitos atendidos

| Requisito da especificação | Implementação |
|---|---|
| Git Flow | Fluxo com `main` (HOMOL), `develop` (DEV) e `feature/*` |
| CI: build, testes e SonarCloud | `.github/workflows/ci-classificacao.yml` |
| CD: `develop` → DEV e `main` → HOMOL | Jobs `deploy-dev` e `deploy-homol` no workflow |
| Swagger por ambiente | `APP_ENV=DEV` habilita; `APP_ENV=HOMOL` desabilita |
| Containerização e publicação | `Dockerfile` e imagem publicada no GHCR |
| Versionamento semântico | Arquivo `VERSION` e tags `classificacao-vX.Y.Z` |
| Dependabot | `.github/dependabot.yml` (pip + docker) |
| Secrets | `SONAR_TOKEN_CLASSIFICACAO`, `RENDER_*` e `GITHUB_TOKEN` via GitHub Secrets |
| Observabilidade | `/metrics` (Prometheus), dashboard provisionado no Grafana |

---

## Arquitetura

O serviço adota o padrão **CQRS** (Command Query Responsibility Segregation):

- **Commands** — `CriarClassificacao`, `ReclassificarManualmente`, `GerarRelatorio`
- **Queries** — `ObterClassificacao`, `ObterHistorico`, `ObterRelatorio`
- **Domain** — entidades, value objects, enums e exceções de domínio
- **Infrastructure** — repositório SQLAlchemy, event store de auditoria, despachador de eventos (RabbitMQ ou mock)

```
classificacao-service/
├── app/
│   ├── api/            # Rotas FastAPI, schemas Pydantic, auth JWT
│   ├── application/
│   │   ├── commands/   # CriarClassificacao, Reclassificar, GerarRelatorio
│   │   ├── queries/    # ObterClassificacao, ObterHistorico, ObterRelatorio
│   │   └── events/     # ClassificacaoEscalada
│   ├── domain/         # Entidades, value objects, enums, exceções
│   ├── infrastructure/ # DB, repositório, event store, despachador
│   └── shared/         # Barramentos CQRS
├── tests/
├── Dockerfile
├── requirements.txt
├── sonar-project.properties
└── VERSION
```

---

## Protocolo de Manchester — regras de classificação

| Cor | Condição | Tempo de espera |
|---|---|---|
| 🔴 VERMELHO | Dor no peito ou PAS > 180 mmHg | Imediato (0 min) |
| 🟠 LARANJA | Temperatura > 38,5 °C | 10 min |
| 🟡 AMARELO | FC > 120 bpm ou PAS > 160 mmHg | 30 min |
| 🟢 VERDE | Temperatura > 37,5 °C ou FC > 100 bpm | 60 min |
| 🔵 AZUL | Sinais vitais dentro da normalidade | 120 min |

> Saturação de oxigênio < 92% escala a cor automaticamente para o nível acima.

---

## Ambientes publicados

| Ambiente | Branch | URL | Swagger |
|---|---|---|---|
| DEV | `develop` | *(URL Render DEV)* | Habilitado `/docs` |
| HOMOL | `main` | *(URL Render HOMOL)* | Desabilitado |

Validação de DEV:
```
GET <https://classificacao-dev-36y9.onrender.com/health>/health  → 200 {"status": "ok"}
GET <https://classificacao-dev-36y9.onrender.com/docs#/>/docs    → 200
```

Validação de HOMOL:
```
GET <https://classificacao-homol.onrender.com/health>/health → 200 {"status": "ok"}
GET <https://classificacao-homol.onrender.com/docs>   → 404
```

---

## Execução local

### Pré-requisitos

- Docker e Docker Compose

### Subir todos os serviços

```bash
cp .env.example .env
docker compose --profile observability up --build
```

### Serviços disponíveis

| Recurso | URL local |
|---|---|
| Classificacao Swagger (DEV) | http://localhost:5002/docs |
| Métricas Prometheus | http://localhost:5002/metrics |
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3001 |

> Login padrão do Grafana: `admin` / valor de `GRAFANA_ADMIN_PASSWORD` no `.env`

---

## Endpoints

### Health

```
GET /health
```

Resposta:
```json
{"status": "ok", "servico": "classificacao-service", "versao": "1.0.0"}
```

### Criar classificação

```
POST /v1/classificacoes
Authorization: Bearer <token>
```

Body:
```json
{
  "paciente_id": "PAC-001",
  "vital_signs": {
    "temperatura": 37.0,
    "pressao_sistolica": 120,
    "pressao_diastolica": 80,
    "saturacao_oxigenio": 98.0,
    "frequencia_cardiaca": 72,
    "dor_peito": false
  }
}
```

Resposta `201`:
```json
{
  "id": "uuid",
  "paciente_id": "PAC-001",
  "cor_risco": "AZUL",
  "tempo_espera_minutos": 120,
  "status": "ATIVO",
  "tipo_mudanca": "AUTOMATICA",
  "usuario_id": "medico@hospital.com",
  "data_criacao": "2026-01-01T10:00:00+00:00",
  "data_atualizacao": "2026-01-01T10:00:00+00:00",
  "requer_retriage": false
}
```

### Obter classificação

```
GET /v1/classificacoes/{classificacao_id}
Authorization: Bearer <token>
```

### Reclassificar manualmente

```
POST /v1/classificacoes/{classificacao_id}/reclassificar
Authorization: Bearer <token>
```

Body:
```json
{
  "nova_cor": "VERMELHO",
  "justificativa": "Piora clínica observada pelo médico"
}
```

> Apenas usuários com `role=MEDICO` podem reclassificar. Justificativa mínima de 5 caracteres.

### Status dos pacientes ativos

```
GET /v1/classificacoes/status
Authorization: Bearer <token>
```

### Status de capacidade

```
GET /v1/classificacoes/capacity/status
Authorization: Bearer <token>
```

### Métricas Prometheus

```
GET /metrics
```

---

## Autenticação

O token JWT é emitido pelo `auth-service`. Para testar:

1. Cadastre um usuário médico via `POST /v1/auth/cadastro` no auth-service:
```json
{
  "email": "medico@hospital.com",
  "senha": "senha_segura123",
  "nome": "Dr. Teste",
  "idade": 40,
  "role": "MEDICO",
  "crm": "12345-SC"
}
```

2. Faça login via `POST /v1/auth/login` e copie o `access_token`.

3. No Swagger do classificacao-service, clique em **Authorize** e informe o token.

Para que o token do auth-service seja aceito, configure as mesmas variáveis em ambos os serviços:

| Auth Service | Classificacao Service |
|---|---|
| `JWT_SECRET` | `JWT_SECRET` |
| `JWT_ALGORITHM=HS256` | `JWT_ALGORITHM=HS256` |

---

## Variáveis de ambiente

| Variável | Padrão | Descrição |
|---|---|---|
| `APP_ENV` | `DEV` | `DEV` habilita Swagger; `HOMOL` desabilita |
| `DATABASE_URL` | `sqlite:///./classificacao.db` | URL de conexão com o banco |
| `JWT_SECRET` | `dev-secret-key` | Chave de validação do JWT |
| `JWT_ALGORITHM` | `HS256` | Algoritmo do JWT |
| `CRITICAL_CAPACITY_LIMIT` | `10` | Limite de pacientes críticos para alerta |
| `TRIAGE_VALIDITY_HOURS` | `4` | Horas até a classificação expirar |
| `RABBITMQ_URL` | `amqp://guest:guest@localhost:5672/` | URL do RabbitMQ |
| `LOG_LEVEL` | `INFO` | Nível de log |

---

## Testes

```bash
cd classificacao-service
pip install -r requirements.txt
pytest tests/ --cov=app --cov-report=term-missing
```

### Cobertura por módulo

| Módulo | O que é testado |
|---|---|
| `test_value_objects.py` | Validação de sinais vitais, lógica de classificação, escalação por saturação, tempos de espera |
| `test_entities.py` | Criação, expiração, reclassificação manual e escalação automática da entidade `Classificacao` |
| `test_commands.py` | Manipuladores CQRS: criar classificação, reclassificar, permissões e eventos |
| `test_queries.py` | Obtenção de classificação, verificação de expiração, erro para ID inexistente |
| `test_events.py` | Serialização dos eventos de domínio para dict |
| `test_escalacao.py` | Escalação automática por tempo para cada cor do protocolo |
| `test_integracao.py` | Schemas Pydantic, validações de payload, imports e enums |
| `test_main_environment.py` | Swagger habilitado em DEV e desabilitado em HOMOL |

---

## CI/CD

O pipeline `.github/workflows/ci-classificacao.yml` executa em pushes para `main` e `develop`:

```
push/PR
   │
   ├─► build-and-test   → instala deps, roda pytest + coverage, faz docker build
   │
   ├─► sonarcloud        → análise estática com cobertura (após build-and-test)
   │
   ├─► publish-image     → publica imagem no GHCR com tags SHA, branch e versão
   │
   ├─► deploy-dev        → aciona webhook Render DEV  (somente branch develop)
   │
   └─► deploy-homol      → aciona webhook Render HOMOL (somente branch main)
```

### Publicar uma nova versão

```bash
git tag classificacao-v1.2.0
git push origin classificacao-v1.2.0
```

O pipeline publica a imagem com a tag `1.2.0` no GHCR automaticamente.

### Secrets necessários no GitHub

| Secret | Uso |
|---|---|
| `SONAR_TOKEN_CLASSIFICACAO` | Análise SonarCloud |
| `RENDER_API_KEY` | Autenticação na API do Render |
| `RENDER_DEPLOY_URL_CLASSIFICACAO_DEV` | Webhook de deploy do ambiente DEV |
| `RENDER_DEPLOY_URL_CLASSIFICACAO_HOMOL` | Webhook de deploy do ambiente HOMOL |

---

## Observabilidade

### Prometheus

O endpoint `/metrics` expõe:

| Métrica | Tipo | Descrição |
|---|---|---|
| `classificacao_http_requests_total` | Counter | Total de requisições por método, rota e status HTTP |
| `classificacao_http_request_duration_seconds` | Histogram | Duração das requisições por método e rota |

O Prometheus é configurado em `observability/prometheus.yml` para scrape a cada 15 segundos.

### Grafana

O dashboard **Classificacao Service** é provisionado automaticamente em `observability/grafana/dashboards/classificacao-service.json` e exibe:

- Taxa de requisições por segundo
- Latência p95
- Erros HTTP 4xx/5xx

---

## Deploy no Render

1. Crie dois serviços Web no Render: um conectado à branch `develop` (DEV) e outro à `main` (HOMOL).
2. Configure **Auto-Deploy** em ambos.
3. Defina as variáveis de ambiente em cada serviço conforme a tabela acima. No serviço HOMOL, use `APP_ENV=HOMOL`.
4. Copie o **Deploy Hook URL** de cada serviço e salve nos secrets do GitHub como `RENDER_DEPLOY_URL_CLASSIFICACAO_DEV` e `RENDER_DEPLOY_URL_CLASSIFICACAO_HOMOL`.