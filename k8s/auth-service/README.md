# Auth Service no Kubernetes

Manifests da parte do `auth-service` (D2) para o Trabalho Pratico 3.

## Arquivos

| Arquivo | Funcao |
| --- | --- |
| `deployment.yaml` | Executa o `auth-service` com 2 replicas |
| `service.yaml` | Cria o Service interno `auth-service` |
| `configmap.yaml` | Variaveis nao sensiveis (ambiente, algoritmo, expiracao do token) |
| `secret.yaml` | Dados sensiveis (DATABASE_URL, JWT_SECRET) |
| `ingress.yaml` | Expoe o servico pelo host `auth.local` |

## Dependencias

- `postgres-service` com o banco `auth_db` (ver `k8s/infra/`)
- Ingress Controller do Minikube habilitado

O `auth-service` nao expoe `/metrics` (nao usa Prometheus), entao nao tem
annotations de scrape. O `JWT_SECRET` e o **mesmo** dos demais servicos, para
que os tokens emitidos aqui sejam validos no resto da aplicacao.

## Como Executar

```bash
kubectl apply -f k8s/infra/             # postgres (uma vez)
minikube image build -t auth-service:local ./auth-service
kubectl apply -f k8s/auth-service/
```

## Como Validar

```bash
kubectl -n medsync get pods -l app.kubernetes.io/name=auth-service
kubectl -n medsync port-forward svc/auth-service 3000:8000
```

- `http://localhost:3000/health`
- `http://localhost:3000/docs`
