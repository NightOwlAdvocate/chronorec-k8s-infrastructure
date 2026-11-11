# Ubuntu setup

Ubuntu requires Git, Python 3, Docker Engine, `kubectl`, kind, Helm, and curl.
Install Docker, `kubectl`, kind, and Helm only from their official instructions
for your Ubuntu release. Then confirm that the current user can run
`docker info`.

From the repository root, verify the environment:

```bash
./scripts/check-environment.sh
```

After every prerequisite reports `[ok]`, the lab starts in the same way on macOS
and Ubuntu:

```bash
./scripts/bootstrap-lab.sh
```

Do not expose the Docker daemon through an unauthenticated TCP socket. Do not
commit kubeconfig files, tokens, or the contents of real Kubernetes Secrets to
this repository.
