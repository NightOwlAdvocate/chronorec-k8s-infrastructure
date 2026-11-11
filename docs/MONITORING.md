# Prometheus and Grafana

## Installation

After the application is running, execute:

```bash
./scripts/install-monitoring.sh
```

The script installs `kube-prometheus-stack`, enables the ServiceMonitor API, and
loads the dashboard from the Helm chart. Alertmanager is intentionally disabled
to reduce resource consumption in the local lab.

## Access Grafana

Retrieve the automatically generated administrator password:

```bash
kubectl -n monitoring get secret monitoring-grafana \
  -o go-template='{{index .data "admin-password" | base64decode}}{{"\n"}}'
```

Start a port-forward:

```bash
kubectl -n monitoring port-forward service/monitoring-grafana 3000:80
```

Open <http://localhost:3000> and sign in as `admin`. Open the
`ChronoRec Infrastructure Demo` dashboard.

## Generate safe test traffic

In a separate terminal window, expose the API:

```bash
kubectl -n chronorec-lab port-forward service/chronorec-demo 8000:80
```

Then send several read-only requests:

```bash
for i in {1..30}; do curl -s http://localhost:8000/api/v1/summary >/dev/null; done
```

The request-rate panel should change within 15–60 seconds. This verifies the
complete path: API → `/metrics` → ServiceMonitor → Prometheus → Grafana.

## Troubleshooting

```bash
kubectl -n chronorec-lab get servicemonitor
kubectl -n monitoring get pods
kubectl -n chronorec-lab get endpoints chronorec-demo
```

The Grafana password is not stored in Git and must not appear in portfolio
screenshots.

During verification on the local Mac, Grafana 13 performed a long initial scan
of its built-in plugins. The default liveness probe restarted the container
before that scan completed. The local values therefore provide more CPU and
memory and allow 300 seconds for the first startup. After this change, the Pod
reached `3/3 Running` with no restarts.
