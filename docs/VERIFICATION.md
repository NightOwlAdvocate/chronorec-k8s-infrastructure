# Протокол проверок

Статус фиксирует только реально выполненные проверки. Дата: 11 ноября 2026,
Europe/Zurich.

| Проверка | Статус | Наблюдение |
|---|---|---|
| Рабочая папка до создания | Проверено | Папка была пустой; существующий backend не найден |
| Операционная система | Проверено | macOS 27.0.1, Apple Silicon arm64 |
| Git | Проверено | 2.50.1 |
| Python | Проверено | 3.14.3 |
| Docker CLI | Проверено | 29.6.1 |
| Docker engine | Проверено | Docker Desktop 29.6.1, Linux/arm64 engine |
| kubectl client | Проверено | 1.36.1 |
| kind | Проверено | 0.33.0; control-plane + worker, Kubernetes 1.37.0 |
| Helm | Проверено | Локально 4.3.1; chart lint: 0 failed; CI настроен на 3.18.4 |
| Python lint/tests | Проверено | Ruff: all checks passed; pytest: 6 passed |
| GitHub Actions | Настроено, не запущено удалённо | Workflow создан; реальный run появится только после push на GitHub |
| Docker image build | Проверено | `chronorec-demo-api:dev`, Linux/arm64 |
| kind deployment/smoke test | Проверено | 2/2 Ready; health, readiness и synthetic summary отвечают |
| Prometheus | Проверено | Оба API target `health: up`, `lastError` пустой |
| Grafana | Проверено | Pod 3/3 Ready; dashboard UID `chronorec-demo` найден через API |
| Pod self-healing | Проверено | Удалённый Pod заменён; ready=2, desired=2 |
| Failed readiness rollout | Проверено | Ревизия 3 failed; ревизия 4: rollback; smoke test зелёный |
| CrashLoopBackOff | Проверено | restartCount=1; previous log показал startup RuntimeError; восстановлено |
| OOMKilled | Проверено | Reason OOMKilled, exit 137, restartCount=1; восстановлено |

Дополнительный найденный и исправленный случай: после failed rollout
`kubectl port-forward service/...` мог выбрать ещё неготовый Pod по selector.
Проверочный скрипт теперь явно выбирает самый новый Pod с `Ready=true` и
использует timeout. Финальный rolling restart завершился двумя Pod `1/1 Running`
без рестартов, после чего health/readiness/summary снова прошли.

После каждого успешного шага обновлять эту таблицу конкретным результатом. Нельзя
указывать в CV или README «проверено», пока соответствующая команда не прошла.
