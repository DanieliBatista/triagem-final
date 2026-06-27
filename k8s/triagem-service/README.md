# Triagem Service no Kubernetes

## Arquivos

| Arquivo | Funcao |
| --- | --- |
| `deployment.yaml` | Executa o `triagem-service` com 2 replicas |
| `service.yaml` | Cria o Service interno `triagem-service` |
| `configmap.yaml` | Guarda variaveis nao sensiveis |
| `secret.yaml` | Guarda dados sensiveis usados pela aplicacao |
| `ingress.yaml` | Expoe o servico pelo host `triagem.local` |

## Dependencias Compartilhadas

Antes de aplicar a triagem, o grupo precisa ter no cluster:

- `postgres-service`, com o banco `triagem_db`
- `classificacao-service`, na porta `8000`
- `auth-service`, usando o mesmo `JWT_SECRET`
- Prometheus e Grafana para observabilidade
- Ingress Controller do Minikube habilitado

O `DATABASE_URL` e o `JWT_SECRET` ficam em `secret.yaml`. Para uma entrega
real, troque o valor de `JWT_SECRET` por um segredo combinado com o
`auth-service`.

## Como Executar

Na raiz do repositorio:

```bash
minikube start
minikube addons enable ingress
kubectl apply -f k8s/namespace.yaml
minikube image build -t triagem-service:local ./triagem-service
kubectl apply -f k8s/triagem-service/
```

## Como Validar

Verifique se existem 2 replicas da triagem:

```bash
kubectl -n medsync get deployment triagem-service
kubectl -n medsync get pods -l app.kubernetes.io/name=triagem-service
```

Resultado esperado:

```text
triagem-service-xxxxx   1/1   Running
triagem-service-yyyyy   1/1   Running
```

Verifique os objetos obrigatorios:

```bash
kubectl -n medsync get deployment triagem-service
kubectl -n medsync get service triagem-service
kubectl -n medsync get configmap triagem-service-config
kubectl -n medsync get secret triagem-service-secret
kubectl -n medsync get ingress triagem-service
```

Teste local via port-forward:

```bash
kubectl -n medsync port-forward svc/triagem-service 5000:8000
```

Acesse:

- `http://localhost:5000/health`
- `http://localhost:5000/metrics`
- `http://localhost:5000/docs`

## Teste Pelo Ingress

Descubra o IP do Minikube:

```bash
minikube ip
```

Adicione no arquivo `hosts` da maquina:

```text
IP_DO_MINIKUBE triagem.local
```

Depois acesse:

- `http://triagem.local/health`
- `http://triagem.local/metrics`
- `http://triagem.local/docs`

## Evidencias Para Apresentacao

Mostre:

```bash
kubectl -n medsync get pods -l app.kubernetes.io/name=triagem-service
kubectl -n medsync get deployment triagem-service
kubectl -n medsync get service triagem-service
kubectl -n medsync get ingress triagem-service
```

Tambem mostre o endpoint `/metrics` e o Prometheus/Grafana coletando as
metricas do `triagem-service`.
