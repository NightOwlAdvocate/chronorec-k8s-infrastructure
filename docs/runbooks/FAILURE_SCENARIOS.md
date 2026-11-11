# Учебные сценарии отказов

## Правила безопасности

Эти команды предназначены только для локального контекста kind. Перед началом:

```bash
kubectl config current-context
```

Ожидаемый ответ: `kind-chronorec-lab`. Если ответ другой — остановиться. Здесь
нет реальных данных, а все failure flags по умолчанию выключены.

## 1. Удаление Pod: self-healing

**Цель:** увидеть, как Deployment возвращает желаемое число реплик.

```bash
kubectl -n chronorec-lab get pods -w
```

В другом окне:

```bash
pod=$(kubectl -n chronorec-lab get pods \
  -l app.kubernetes.io/instance=chronorec-demo \
  -o jsonpath='{.items[0].metadata.name}')
kubectl -n chronorec-lab delete pod "$pod" --wait=false
```

**Ожидается:** один Pod перейдёт в `Terminating`, ReplicaSet создаст замену,
а число Ready снова станет `2/2`. Root cause здесь искусственный: ручное
удаление. Восстановление выполняет controller Deployment.

## 2. Неудачный readiness rollout и автоматический rollback

**Цель:** доказать, что неготовая версия не получает трафик и не заменяет все
рабочие реплики.

```bash
helm upgrade chronorec-demo helm/chronorec-demo \
  -n chronorec-lab \
  --reuse-values \
  --set lab.notReady=true \
  --atomic \
  --timeout 60s
```

Команда должна завершиться ошибкой и выполнить rollback. Проверка:

```bash
helm history chronorec-demo -n chronorec-lab
kubectl get pods -n chronorec-lab
kubectl get endpoints chronorec-demo -n chronorec-lab
./scripts/verify-deployment.sh
```

**Root cause:** `/readyz` намеренно отвечает HTTP 503. **Исправление:** Helm
`--atomic` возвращает предыдущие values; после rollback оба Pod снова Ready.
В Helm 4 этот флаг работает, но выводит предупреждение о новом имени
`--rollback-on-failure`; `--atomic` оставлен для совместимости с Helm 3.

## 3. CrashLoopBackOff

**Цель:** найти startup failure через describe и logs.

```bash
helm upgrade chronorec-demo helm/chronorec-demo \
  -n chronorec-lab \
  --reuse-values \
  --set lab.crashOnStart=true

kubectl get pods -n chronorec-lab
kubectl describe pods -n chronorec-lab \
  -l app.kubernetes.io/instance=chronorec-demo
kubectl logs -n chronorec-lab \
  -l app.kubernetes.io/instance=chronorec-demo \
  --all-containers --prefix --tail=50
```

**Ожидается:** новый Pod перезапускается, а старые готовые Pod остаются благодаря
rolling update. В логах виден `Intentional lab startup failure`.

Восстановление:

```bash
helm upgrade chronorec-demo helm/chronorec-demo \
  -n chronorec-lab \
  --reuse-values \
  --set lab.crashOnStart=false \
  --wait
./scripts/verify-deployment.sh
```

## 4. OOMKilled

**Цель:** связать exit/restart с memory limit, а не гадать по симптомам.

```bash
helm upgrade chronorec-demo helm/chronorec-demo \
  -n chronorec-lab \
  --reuse-values \
  --set resources.limits.memory=64Mi \
  --set lab.allocateMemoryMb=256

kubectl get pods -n chronorec-lab -w
```

После перезапуска найти новый Pod и проверить причину:

```bash
kubectl get pods -n chronorec-lab \
  -l app.kubernetes.io/instance=chronorec-demo
kubectl describe pods -n chronorec-lab \
  -l app.kubernetes.io/instance=chronorec-demo
```

В `Last State` ожидается `Reason: OOMKilled` и exit code 137.

Восстановление:

```bash
helm upgrade chronorec-demo helm/chronorec-demo \
  -n chronorec-lab \
  --reuse-values \
  --set resources.limits.memory=128Mi \
  --set lab.allocateMemoryMb=0 \
  --wait
./scripts/verify-deployment.sh
```

**Root cause:** процесс попытался выделить 256 MiB при лимите 64 MiB. В реальном
инциденте нельзя просто бесконечно увеличивать limit: сначала проверяются профиль
памяти, утечки, реальная нагрузка и корректные requests/limits.

## Шаблон отчёта об инциденте

Для каждого запуска сохранить без персональных данных:

- дата и контекст `kind-chronorec-lab`;
- наблюдаемый симптом;
- команды и ключевые строки вывода;
- root cause;
- исправление/rollback;
- команда, подтвердившая восстановление;
- чему научил сценарий и что изменилось бы в production.
