# Prontuario Service no Kubernetes

Manifests da parte do `prontuario-service` para o Trabalho Pratico 3.

## Arquivos

| Arquivo | Funcao |
| --- | --- |
| `deployment.yaml` | Executa o `prontuario-service` com 2 replicas |
| `service.yaml` | Cria o Service interno `prontuario-service` |
| `configmap.yaml` | Variaveis nao sensiveis (ambiente, algoritmo JWT) |
| `secret.yaml` | Dados sensiveis (DATABASE_URL, JWT_SECRET) |
| `ingress.yaml` | Expoe o servico pelo host `prontuario.local` |

## Dependencias

- `postgres-service` com o banco `prontuario_db` (ver `k8s/infra/`)
- Ingress Controller do Minikube habilitado

O `prontuario-service` nao usa RabbitMQ. As metricas saem no `/metrics`
(via prometheus-fastapi-instrumentator) e sao coletadas pelo Prometheus em
`k8s/observability/`.

## Como Executar

Na raiz do repositorio (depois de `k8s/infra/`):

```bash
minikube image build -t prontuario-service:local ./prontuario-service
kubectl apply -f k8s/prontuario-service/
```

## Como Validar

```bash
kubectl -n medsync get pods -l app.kubernetes.io/name=prontuario-service
kubectl -n medsync port-forward svc/prontuario-service 8080:8000
```

- `http://localhost:8080/health`
- `http://localhost:8080/metrics`
- `http://localhost:8080/docs`
