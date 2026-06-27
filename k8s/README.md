# MedSync no Kubernetes (Trabalho Pratico 3)

Deploy completo da aplicacao em Minikube, com CI/CD, multiplas replicas e
observabilidade (Prometheus + Grafana).

## Estrutura

```
k8s/
├── namespace.yaml              # namespace medsync (app)
├── infra/                      # Postgres + RabbitMQ compartilhados
├── triagem-service/            # microsservico de triagem (2 replicas)
├── classificacao-service/      # microsservico de classificacao (2 replicas)
├── prontuario-service/         # microsservico de prontuario (2 replicas)
└── observability/              # Prometheus + Grafana (namespace monitoring)
```

Cada microsservico tem seus proprios `Deployment`, `Service`, `ConfigMap`,
`Secret` e `Ingress`. Toda a configuracao vem de ConfigMap/Secret — nada fixo
no codigo.

## Pre-requisitos

- Docker em execucao
- `minikube` instalado (`winget install Kubernetes.minikube`)

## Subir Tudo (ordem importa)

```bash
# 1. Cluster + ingress
minikube start --driver=docker
minikube addons enable ingress

# 2. Namespace da aplicacao
kubectl apply -f k8s/namespace.yaml

# 3. Infra compartilhada (Postgres + RabbitMQ) e espera ficar pronta
kubectl apply -f k8s/infra/
kubectl -n medsync rollout status deployment/postgres
kubectl -n medsync rollout status deployment/rabbitmq

# 4. Build das imagens dentro do Minikube
minikube image build -t triagem-service:local ./triagem-service
minikube image build -t classificacao-service:local ./classificacao-service
minikube image build -t prontuario-service:local ./prontuario-service

# 5. Microsservicos
kubectl apply -f k8s/triagem-service/
kubectl apply -f k8s/classificacao-service/
kubectl apply -f k8s/prontuario-service/

# 6. Observabilidade (cria o namespace monitoring sozinho)
kubectl apply -f k8s/observability/
```

## Evidencia das Replicas

```bash
kubectl -n medsync get pods
kubectl -n medsync get deployments
```

Cada um dos tres servicos deve aparecer com `2/2` replicas `Running`.

## Acessar

Observabilidade:

```bash
minikube service grafana -n monitoring --url     # Grafana (admin/admin)
kubectl -n monitoring port-forward svc/prometheus 9090:9090
```

- Grafana: dashboards na pasta "MedSync" (um por servico)
- Prometheus: `http://localhost:9090/targets` deve mostrar os pods `UP`

Servicos via Ingress — descubra o IP com `minikube ip` e adicione ao
`hosts` (`C:\Windows\System32\drivers\etc\hosts` no Windows):

```text
IP_DO_MINIKUBE  triagem.local  classificacao.local  prontuario.local
```

Depois acesse `http://<host>/health`, `http://<host>/metrics`, `http://<host>/docs`.

## Observacoes

- Postgres e RabbitMQ rodam com 1 replica (sao estado, nao microsservicos).
- Os tres servicos compartilham o mesmo `JWT_SECRET` (nos Secrets). Para uma
  entrega real, troque por um segredo combinado com o `auth-service`.
- O CI ja publica as imagens no GHCR; aqui usamos build local no Minikube para
  nao depender de credenciais de registry. Para puxar do GHCR, troque o campo
  `image:` dos Deployments por `ghcr.io/<owner>/<servico>:develop`.
