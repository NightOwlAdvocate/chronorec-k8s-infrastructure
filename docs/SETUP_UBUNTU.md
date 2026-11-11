# Подготовка Ubuntu

На Ubuntu нужны Git, Python 3, Docker Engine, `kubectl`, kind, Helm и curl.
Устанавливайте Docker, `kubectl`, kind и Helm только по официальным инструкциям
для вашей версии Ubuntu; затем убедитесь, что текущий пользователь может
выполнять `docker info`.

Проверка из корня репозитория:

```bash
./scripts/check-environment.sh
```

После всех строк `[ok]` лаборатория запускается одинаково на Mac и Ubuntu:

```bash
./scripts/bootstrap-lab.sh
```

Не запускайте Docker daemon с открытым TCP-сокетом без аутентификации. Не
добавляйте в этот репозиторий kubeconfig, токены и содержимое реальных Secret.
