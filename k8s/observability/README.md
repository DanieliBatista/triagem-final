# Observabilidade (Prometheus + Grafana)

Stack de observabilidade que atende o requisito 5 do Trabalho Pratico 3 para os
tres microsservicos (triagem, classificacao e prontuario). Roda no namespace
proprio `monitoring`, sem alterar o namespace `medsync` da aplicacao.

## Arquivos

| Arquivo | Funcao |
| --- | --- |
| `00-namespace.yaml` | Cria o namespace `monitoring` (prefixo `00` garante que vem primeiro) |
| `prometheus-rbac.yaml` | ServiceAccount + ClusterRole para descobrir pods |
| `prometheus-config.yaml` | Config do Prometheus (auto-discovery por annotations) |
| `prometheus.yaml` | Deployment + Service do Prometheus |
| `grafana-config.yaml` | Datasource, provider, os 3 dashboards e Secret do admin |
| `grafana.yaml` | Deployment + Service (NodePort 30300) do Grafana |

## Como Funciona

O Prometheus usa `kubernetes_sd_configs` (role `pod`) e so coleta pods que tenham
as annotations `prometheus.io/scrape: "true"`, `prometheus.io/path` e
`prometheus.io/port`. Os tres servicos ja expoem essas annotations e o endpoint
`/metrics`, entao sao descobertos automaticamente — sem listar alvos na mao.

O Prometheus tambem reescreve o label `job` com o nome do servico (vindo do label
`app.kubernetes.io/name` do pod), entao os dashboards que filtram por
`job="..."` funcionam sem alteracao.

O Grafana sobe com a datasource Prometheus e os 3 dashboards (pasta "MedSync")
ja provisionados.

## Como Executar

```bash
kubectl apply -f k8s/observability/
```

O `00-namespace.yaml` cria o namespace antes dos demais objetos, entao um unico
`apply` na pasta funciona.

## Como Acessar

Grafana (usuario `admin`, senha `admin`):

```bash
minikube service grafana -n monitoring --url
```

ou via NodePort: `http://IP_DO_MINIKUBE:30300`

Prometheus (port-forward):

```bash
kubectl -n monitoring port-forward svc/prometheus 9090:9090
```

- Prometheus: `http://localhost:9090`
- Alvos coletados: `http://localhost:9090/targets`

## Evidencias Para Apresentacao

```bash
kubectl -n monitoring get pods
```

No Prometheus (`/targets`) mostre os pods dos tres servicos com estado `UP`.
No Grafana abra os dashboards da pasta "MedSync" e gere trafego (ex.: acesse
`/health` algumas vezes) para ver as metricas subindo.
