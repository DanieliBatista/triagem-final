# Evidências de Execução — MedSync no Kubernetes (TP3)

Saídas capturadas ao vivo do cluster Minikube em 2026-06-27. Cada seção mapeia
um requisito do trabalho.

---

## 1. Múltiplas réplicas (Req. 4.1 e 4.2)

```bash
kubectl -n medsync get pods
```

```text
NAME                                     READY   STATUS    RESTARTS      AGE
auth-service-55b49db8bb-hpnql            1/1     Running   1 (36m ago)   36m
auth-service-55b49db8bb-xr4ph            1/1     Running   0             36m
classificacao-service-66f9565ff9-h8sxc   1/1     Running   0             36m
classificacao-service-66f9565ff9-szq4h   1/1     Running   1 (36m ago)   36m
postgres-88748668-lrnqf                  1/1     Running   0             39m
prontuario-service-5c8fdf4fb7-g2mjt      1/1     Running   0             36m
prontuario-service-5c8fdf4fb7-pcpbj      1/1     Running   1 (36m ago)   36m
rabbitmq-58fb46d5f5-5npz5                1/1     Running   0             39m
triagem-service-5df94597f9-54lnk         1/1     Running   0             36m
triagem-service-5df94597f9-7z6pp         1/1     Running   0             10m
triagem-service-5df94597f9-lqgkr         1/1     Running   1 (36m ago)   36m
triagem-service-5df94597f9-mwn67         1/1     Running   0             10m
```

```bash
kubectl -n medsync get deploy
```

```text
NAME                    READY   UP-TO-DATE   AVAILABLE   AGE
auth-service            2/2     2            2           36m
classificacao-service   2/2     2            2           36m
postgres                1/1     1            1           39m
prontuario-service      2/2     2            2           36m
rabbitmq                1/1     1            1           39m
triagem-service         4/4     4            4           36m
```
---

## 2. Objetos obrigatórios: Service, ConfigMap, Secret, Ingress (Req. 3)

```bash
kubectl -n medsync get svc,configmap,secret,ingress
```

```text
NAME                            TYPE        CLUSTER-IP       PORT(S)              AGE
service/auth-service            ClusterIP   10.104.109.135   8000/TCP             36m
service/classificacao-service   ClusterIP   10.101.204.203   8000/TCP             36m
service/postgres-service        ClusterIP   10.111.147.139   5432/TCP             39m
service/prontuario-service      ClusterIP   10.103.128.77    8000/TCP             36m
service/rabbitmq-service        ClusterIP   10.96.122.58     5672/TCP,15672/TCP   39m
service/triagem-service         ClusterIP   10.108.181.62    8000/TCP             36m

NAME                                     DATA   AGE
configmap/auth-service-config            3      36m
configmap/classificacao-service-config   9      36m
configmap/postgres-init                  1      39m
configmap/prontuario-service-config      2      36m
configmap/triagem-service-config         6      36m

NAME                                  TYPE     DATA   AGE
secret/auth-service-secret            Opaque   2      36m
secret/classificacao-service-secret   Opaque   3      36m
secret/postgres-secret                Opaque   2      39m
secret/prontuario-service-secret      Opaque   2      36m
secret/triagem-service-secret         Opaque   2      36m

NAME                                              CLASS   HOSTS                 ADDRESS        PORTS   AGE
ingress.networking.k8s.io/auth-service            nginx   auth.local            192.168.49.2   80      36m
ingress.networking.k8s.io/classificacao-service   nginx   classificacao.local   192.168.49.2   80      36m
ingress.networking.k8s.io/prontuario-service      nginx   prontuario.local      192.168.49.2   80      36m
ingress.networking.k8s.io/triagem-service         nginx   triagem.local         192.168.49.2   80      36m
```

---

## 3. Observabilidade: Prometheus + Grafana no cluster (Req. 5)

```bash
kubectl -n monitoring get pods
```

```text
NAME                          READY   STATUS    RESTARTS   AGE
grafana-5bdd87c74c-5fn6d      1/1     Running   0          36m
prometheus-6d9f58896d-mf4jm   1/1     Running   0          36m
```

Alvos coletados pelo Prometheus (auto-descoberta por annotations; label `job`
reescrito com o nome do serviço):

```text
prontuario-service-5c8fdf4fb7-g2mjt      job=prontuario-service     health=up
prontuario-service-5c8fdf4fb7-pcpbj      job=prontuario-service     health=up
triagem-service-5df94597f9-54lnk         job=triagem-service        health=up
triagem-service-5df94597f9-mwn67         job=triagem-service        health=up
triagem-service-5df94597f9-7z6pp         job=triagem-service        health=up
triagem-service-5df94597f9-lqgkr         job=triagem-service        health=up
classificacao-service-66f9565ff9-h8sxc   job=classificacao-service  health=up
classificacao-service-66f9565ff9-szq4h   job=classificacao-service  health=up
```

> Todos os pods dos três serviços com métricas estão `health=up`. Os dashboards
> (pasta "MedSync" no Grafana, admin/admin) leem essas métricas.

---

## 4. Aplicação funcionando por completo — teste E2E (Req. 1)

Fluxo real exercitando os 4 serviços de uma vez (cadastro/login no auth → token
→ triagem que chama a classificação → prontuário criar/consultar), rodado de
dentro do cluster via DNS interno:

```text
============================================================
TESTE E2E NO CLUSTER  -  paciente PAC-1782591604
============================================================
[1] AUTH  cadastro      -> HTTP 201  {'status': 'Sucesso', 'usuario_id': 2}
[2] AUTH  login         -> HTTP 200  token_recebido=True
[3] TRIAGEM->CLASSIF.   -> HTTP 201  cor_risco=VERMELHO
[4] PRONTUARIO criar    -> HTTP 201  {'status': 'Sucesso', ...}
[5] PRONTUARIO historico-> HTTP 200  total_atendimentos=1
============================================================
RESULTADO: TODOS OS PASSOS OK
============================================================
```

---

## 5. Escalabilidade e resiliência (suporte a escalabilidade)

Escalar um serviço em tempo real:

```bash
kubectl -n medsync scale deploy/triagem-service --replicas=4
kubectl -n medsync get pods -l app.kubernetes.io/name=triagem-service
```

Resiliência (self-healing) — apagar um pod e ver o Kubernetes recriar:

```bash
kubectl -n medsync delete pod <nome-do-pod>
kubectl -n medsync get pods -w
```

Voltar à configuração declarada (2 réplicas):

```bash
kubectl -n medsync scale deploy/triagem-service --replicas=2
```
