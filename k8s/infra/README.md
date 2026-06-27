# Infraestrutura Compartilhada (Postgres + RabbitMQ)

Dependencias que os microsservicos usam dentro do cluster. Ficam no namespace
`medsync`, junto com os servicos.

## Arquivos

| Arquivo | Funcao |
| --- | --- |
| `postgres-secret.yaml` | Usuario e senha do Postgres (`postgres` / `postgres`) |
| `postgres-init.yaml` | Cria os bancos `triagem_db`, `classificacao_db`, `prontuario_db`, `auth_db` |
| `postgres.yaml` | PVC + Deployment + Service (`postgres-service:5432`) |
| `rabbitmq.yaml` | Deployment + Service (`rabbitmq-service:5672`) do RabbitMQ |

## Observacoes

- Postgres e RabbitMQ rodam com **1 replica** de proposito: sao bancos/estado,
  nao microsservicos da regra 4.1 (que pede 2 replicas para os servicos da app).
- O `postgres-init.yaml` so roda na **primeira** inicializacao (volume vazio).
  Se precisar recriar os bancos, apague o PVC: `kubectl -n medsync delete pvc postgres-data`.
- Apenas o `classificacao-service` usa RabbitMQ; os demais ignoram.

## Como Executar

Aplicar **antes** dos microsservicos:

```bash
kubectl apply -f k8s/infra/
kubectl -n medsync rollout status deployment/postgres
kubectl -n medsync rollout status deployment/rabbitmq
```
