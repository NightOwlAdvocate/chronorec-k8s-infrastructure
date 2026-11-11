# Подготовка Mac

## Что показала проверка

Первичная проверка обнаружила macOS 27.0.1 (Apple Silicon), Git, Python 3.14,
Docker CLI и `kubectl`. Docker Desktop был выключен, а `kind` и Helm отсутствовали.
После этого Docker Desktop был запущен, а Homebrew установил kind 0.33.0 и Helm
4.3.1. Раздел ниже остаётся инструкцией для чистой машины.

## 1. Запустить Docker Desktop

Откройте Docker Desktop как обычное приложение и дождитесь статуса Engine
running. Проверка:

```bash
docker info
```

Если команда выводит сведения о Server без ошибки подключения, Docker готов.

## 2. Установить kind и Helm

Если Homebrew уже установлен:

```bash
brew install kind helm
```

Проверка:

```bash
kind version
helm version
kubectl version --client
```

Локально лаборатория проверена с kind 0.33.0 и Helm 4.3.1. CI дополнительно
проверяет chart с Helm 3.18.4, чтобы сохранить совместимость Helm 3.

## 3. Проверить всю среду одной командой

Из корня репозитория:

```bash
./scripts/check-environment.sh
```

Каждая строка `[ok]` означает выполненную предпосылку. Строка `[missing]` или
`[action needed]` объясняет, что ещё требуется.

## Почему выбран kind

kind запускает Kubernetes-ноды как Docker-контейнеры. Он лёгкий, легко удаляется
и подходит для локального обучения и CI. Это не production-платформа и не
заменяет managed Kubernetes или многосерверный кластер.
