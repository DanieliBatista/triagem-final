# Triagem Service - Trabalho Pratico 2 DevOps

Microsservico responsavel por coletar sinais vitais e solicitar a classificacao
do paciente. A autenticacao (`auth-service`) e uma dependencia do fluxo do
trabalho anterior e fornece o JWT consumido por esta API.

## Requisitos atendidos

| Requisito da especificacao | Implementacao |
| --- | --- |
| Git Flow | Fluxo previsto com `main` (HOMOL), `develop` (DEV) e `feature/*` |
| CI: build, testes e SonarCloud | `.github/workflows/ci-triagem.yml` |
| CD: `develop` para DEV e `main` para HOMOL | Auto-Deploy do Render conectado as branches |
| Swagger por ambiente | `APP_ENV=DEV` habilita; `APP_ENV=HOMOL` desabilita |
| Containerizacao e publicacao | `triagem-service/Dockerfile` e imagem em GHCR |
| Versionamento | `VERSION` e tags `triagem-vX.Y.Z` (Semantic Versioning) |
| Seguranca | Secrets no GitHub Actions e `.github/dependabot.yml` |
| Observabilidade | `/metrics`, Prometheus e dashboard provisionado no Grafana |

## Execucao local

Crie o arquivo `.env` a partir de `.env.example` e execute:

```bash
docker compose --profile observability up --build
```

Servicos relevantes:

| Recurso | URL local |
| --- | --- |
| Triagem Swagger (DEV) | `http://localhost:5000/docs` |
| Metricas Prometheus da API | `http://localhost:5000/metrics` |
| Prometheus | `http://localhost:9090` |
| Grafana | `http://localhost:3001` |

O dashboard **Triagem Service** e carregado automaticamente no Grafana.

## Ambientes publicados

| Ambiente | Branch | URL | Swagger |
| --- | --- | --- | --- |
| DEV | `develop` | `https://triagem-dev-g1ao.onrender.com` | Habilitado |
| HOMOL | `main` | `https://triagem-homol-wn9h.onrender.com` | Desabilitado |

Validacao de DEV:

```text
GET https://triagem-dev-g1ao.onrender.com/health -> 200 healthy
GET https://triagem-dev-g1ao.onrender.com/docs   -> 200
```

Validacao de HOMOL:

```text
GET https://triagem-homol-wn9h.onrender.com/health -> 200 healthy
GET https://triagem-homol-wn9h.onrender.com/docs   -> 404
```

## Autenticacao para testar a triagem

No Swagger do `auth-service`, use primeiro `POST /v1/auth/cadastro` caso ainda
nao exista um usuario. Para login, em `POST /v1/auth/login`, o body deve ser
JSON valido, com virgula entre os campos:

```json
{
  "email": "medico@hospital.com",
  "senha": "senha_segura123"
}
```

O erro `JSON decode error: Expecting ',' delimiter` ocorre antes da validacao
das credenciais: significa que faltou uma virgula, aspas ou outro caractere no
JSON digitado.

Copie o valor de `access_token` retornado. No Swagger do `triagem-service`,
clique em **Authorize** e informe apenas o token no campo Bearer. Em seguida,
execute `POST /v1/triagem`.

Para que um token emitido pelo `auth-service` publicado seja aceito pela
triagem publicada, configure no Render o mesmo segredo e algoritmo:

| Auth (dependencia) | Triagem Service |
| --- | --- |
| `SECRET_KEY` | `JWT_SECRET` |
| `ALGORITHM=HS256` | `JWT_ALGORITHM=HS256` |

## Deploy no Render

Cadastre no GitHub o secret usado pela analise:

| Secret | Finalidade |
| --- | --- |
| `SONAR_TOKEN_TRIAGEM` | Analise SonarCloud |

No Render, conecte o servico DEV a branch `develop` e o servico HOMOL a
branch `main`, ambos com **Auto-Deploy** habilitado. No servico DEV use
`APP_ENV=DEV`. No servico HOMOL use `APP_ENV=HOMOL`, o que remove `/docs`,
`/redoc` e `/openapi.json`.

Para publicar uma versao da imagem, crie uma tag no formato
`triagem-v1.0.0`. O pipeline publica as tags de branch, commit e versao no
GitHub Container Registry.

## Endpoints

| Metodo | Endpoint | Uso |
| --- | --- | --- |
| `POST` | `/v1/triagem` | Realiza triagem autenticada |
| `GET` | `/health` | Verificacao de disponibilidade |
| `GET` | `/metrics` | Coleta Prometheus |
