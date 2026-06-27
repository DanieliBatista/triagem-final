# Classificacao Service no Kubernetes

Esta pasta contem os manifests da parte do `classificacao-service` para o
Trabalho Pratico 3.

## Arquivos

| Arquivo | Funcao |
| --- | --- |
| `deployment.yaml` | Executa o `classificacao-service` com 2 replicas |
| `service.yaml` | Cria o Service interno `classificacao-service` |
| `configmap.yaml` | Guarda variaveis nao sensiveis (ambiente, regras de negocio) |
| `secret.yaml` | Guarda dados sensiveis (DATABASE_URL, JWT_SECRET, RABBITMQ_URL) |
| `ingress.yaml` | Expoe o servico pelo host `classificacao.local` |

A observabilidade (Prometheus + Grafana) fica em `k8s/observability/`.

## Dependencias

O `postgres-service` (com o banco `classificacao_db`) e o `rabbitmq-service`
sao providos por `k8s/infra/`. Tambem e preciso o Ingress Controller do
Minikube habilitado.

O `DATABASE_URL`, o `JWT_SECRET` e o `RABBITMQ_URL` ficam em `secret.yaml`. Para
uma entrega real, troque o `JWT_SECRET` por um segredo combinado com o
`auth-service` (os tres servicos usam o mesmo valor).

## Como Executar

Veja o passo a passo completo (cluster, infra, imagens) em `k8s/README.md`.
Resumo da parte da classificacao:

```bash
kubectl apply -f k8s/infra/                # postgres + rabbitmq (uma vez)
minikube image build -t classificacao-service:local ./classificacao-service
kubectl apply -f k8s/classificacao-service/
```

## Como Validar (multiplos pods)

```bash
kubectl -n medsync get deployment classificacao-service
kubectl -n medsync get pods -l app.kubernetes.io/name=classificacao-service
```

Resultado esperado:

```text
classificacao-service-xxxxx   1/1   Running
classificacao-service-yyyyy   1/1   Running
```

Verifique os objetos obrigatorios:

```bash
kubectl -n medsync get deployment classificacao-service
kubectl -n medsync get service classificacao-service
kubectl -n medsync get configmap classificacao-service-config
kubectl -n medsync get secret classificacao-service-secret
kubectl -n medsync get ingress classificacao-service
```

## Teste Local via Port-Forward

```bash
kubectl -n medsync port-forward svc/classificacao-service 5002:8000
```

Acesse:

- `http://localhost:5002/health`
- `http://localhost:5002/metrics`
- `http://localhost:5002/docs`

## Teste Pelo Ingress

Descubra o IP do Minikube:

```bash
minikube ip
```

Adicione no arquivo `hosts` da maquina (`C:\Windows\System32\drivers\etc\hosts`
no Windows):

```text
IP_DO_MINIKUBE classificacao.local
```

Depois acesse:

- `http://classificacao.local/health`
- `http://classificacao.local/metrics`
- `http://classificacao.local/docs`

## Evidencias Para Apresentacao

```bash
kubectl -n medsync get pods -l app.kubernetes.io/name=classificacao-service
kubectl -n medsync get deployment classificacao-service
kubectl -n medsync get service classificacao-service
kubectl -n medsync get ingress classificacao-service
```

Mostre tambem o endpoint `/metrics` e o Grafana/Prometheus coletando as
metricas (`classificacao_http_requests_total`).
