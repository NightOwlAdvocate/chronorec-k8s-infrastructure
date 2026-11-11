# Prometheus и Grafana

## Установка

После работающего приложения:

```bash
./scripts/install-monitoring.sh
```

Скрипт устанавливает `kube-prometheus-stack`, включает ServiceMonitor API и
добавляет dashboard из Helm chart. Alertmanager намеренно выключен, чтобы
уменьшить локальное потребление ресурсов.

## Открыть Grafana

Получить автоматически созданный пароль администратора:

```bash
kubectl -n monitoring get secret monitoring-grafana \
  -o go-template='{{index .data "admin-password" | base64decode}}{{"\n"}}'
```

Запустить port-forward:

```bash
kubectl -n monitoring port-forward service/monitoring-grafana 3000:80
```

Открыть <http://localhost:3000>, пользователь `admin`. Найти dashboard
`ChronoRec Infrastructure Demo`.

## Создать безопасную тестовую нагрузку

В отдельном окне открыть API:

```bash
kubectl -n chronorec-lab port-forward service/chronorec-demo 8000:80
```

Затем выполнить несколько read-only запросов:

```bash
for i in {1..30}; do curl -s http://localhost:8000/api/v1/summary >/dev/null; done
```

Через 15–60 секунд график request rate должен измениться. Это проверяет путь
API → `/metrics` → ServiceMonitor → Prometheus → Grafana.

## Диагностика

```bash
kubectl -n chronorec-lab get servicemonitor
kubectl -n monitoring get pods
kubectl -n chronorec-lab get endpoints chronorec-demo
```

Пароль Grafana не записывается в Git и не должен попадать в скриншоты портфолио.

На проверенном Mac Grafana 13 выполняла долгий первый scan встроенных plugins.
Стандартная liveness probe успела перезапустить контейнер. Поэтому локальные
values дают Grafana больше CPU/памяти и 300 секунд на первый старт. После
изменения Pod стал `3/3 Running`, без рестартов.
