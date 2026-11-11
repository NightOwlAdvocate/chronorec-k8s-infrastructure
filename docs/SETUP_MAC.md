# macOS setup

## Verified environment

The initial check found macOS 27.0.1 on Apple Silicon, Git, Python 3.14, the
Docker CLI, and `kubectl`. Docker Desktop was stopped, while `kind` and Helm were
not installed. Docker Desktop was subsequently started, and Homebrew installed
kind 0.33.0 and Helm 4.3.1. The steps below remain the setup procedure for a
clean machine.

## 1. Start Docker Desktop

Open Docker Desktop as a normal application and wait until the engine reports
that it is running. Verify it with:

```bash
docker info
```

Docker is ready when the command prints Server information without a connection
error.

## 2. Install kind and Helm

If Homebrew is already installed, run:

```bash
brew install kind helm
```

Verify the tools:

```bash
kind version
helm version
kubectl version --client
```

The lab was verified locally with kind 0.33.0 and Helm 4.3.1. CI also validates
the chart with Helm 3.18.4 to preserve Helm 3 compatibility.

## 3. Check the complete environment

From the repository root, run:

```bash
./scripts/check-environment.sh
```

Each `[ok]` line confirms a prerequisite. A `[missing]` or `[action needed]`
line explains what still needs attention.

## Why kind was selected

kind runs Kubernetes nodes as Docker containers. It is lightweight, disposable,
and suitable for local learning and CI. It is not a production platform and
does not replace managed Kubernetes or a multi-server cluster.
