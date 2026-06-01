# Prontuario Service - Trabalho Pratico 2 DevOps

Microsservico responsavel por registrar atendimentos, consultar historico
medico do paciente e gerar sumario de alta. A autenticacao e feita por token
JWT emitido pelo `auth-service`.

## Requisitos atendidos

| Requisito da especificacao | Implementacao |
| --- | --- |
| Git Flow | Fluxo com `main` (HOMOL), `develop` (DEV) e `feature/*` |
| CI: build, testes e SonarCloud | `.github/workflows/ci-prontuario.yml` |
| CD: `develop` para DEV e `main` para HOMOL | Auto-Deploy do Render conectado as branches |
| Swagger por ambiente | `APP_ENV=DEV` habilita; `APP_ENV=HOMOL` desabilita |
| Containerizacao e publicacao | `Dockerfile` e imagem publicada no GHCR |
| Versionamento semantico | `VERSION` e tags `prontuario-vX.Y.Z` |
| Seguranca | Dependabot e GitHub Secrets |
| Observabilidade | `/metrics`, Prometheus e dashboard provisionado no Grafana |

## Execucao local

Na raiz do repositorio:

```bash
docker compose --profile observability up --build
```

Servicos relevantes:

| Recurso | URL local |
| --- | --- |
| Prontuario Swagger (DEV) | `http://localhost:8080/docs` |
| Health check | `http://localhost:8080/health` |
| Metricas Prometheus da API | `http://localhost:8080/metrics` |
| Prometheus | `http://localhost:9090` |
| Grafana | `http://localhost:3001` |

## Ambientes publicados

| Ambiente | Branch | URL | Swagger |
| --- | --- | --- | --- |
| DEV | `develop` | `<URL_RENDER_PRONTUARIO_DEV>` | Habilitado |
| HOMOL | `main` | `<URL_RENDER_PRONTUARIO_HOMOL>` | Desabilitado |

Validacao de DEV:

```text
GET <URL_RENDER_PRONTUARIO_DEV>/health -> 200 healthy
GET <URL_RENDER_PRONTUARIO_DEV>/docs   -> 200
```

Validacao de HOMOL:

```text
GET <URL_RENDER_PRONTUARIO_HOMOL>/health -> 200 healthy
GET <URL_RENDER_PRONTUARIO_HOMOL>/docs   -> 404
```

## Variaveis de ambiente

| Variavel | Descricao |
| --- | --- |
| `APP_ENV` | `DEV` habilita Swagger; `HOMOL` desabilita |
| `DATABASE_URL` | URL interna do PostgreSQL do prontuario |
| `JWT_SECRET` | Mesmo segredo usado no `auth-service` do ambiente |
| `JWT_ALGORITHM` | Algoritmo do JWT, normalmente `HS256` |
| `PYTHON_VERSION` | Versao usada no Render, por exemplo `3.10.20` |

## Endpoints

| Metodo | Endpoint | Uso |
| --- | --- | --- |
| `GET` | `/` | Mensagem de disponibilidade |
| `GET` | `/health` | Health check |
| `GET` | `/metrics` | Coleta Prometheus |
| `POST` | `/prontuarios` | Registra atendimento |
| `GET` | `/prontuarios/{paciente_id}` | Consulta historico |
| `GET` | `/prontuarios/{paciente_id}/alta` | Gera sumario de alta |

## CI/CD

O pipeline executa testes com cobertura, analise SonarCloud, build Docker e
publicacao da imagem no GitHub Container Registry.

Secret necessario:

| Secret | Uso |
| --- | --- |
| `SONAR_TOKEN_PRONTUARIO` | Analise SonarCloud |

Para publicar uma versao:

```bash
git tag prontuario-v1.0.0
git push origin prontuario-v1.0.0
```
