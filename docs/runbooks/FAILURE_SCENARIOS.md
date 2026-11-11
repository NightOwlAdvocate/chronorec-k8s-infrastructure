# Training failure scenarios

## Safety rules

These commands are intended only for the local kind context. Before starting,
run:

```bash
kubectl config current-context
```

The expected result is `kind-chronorec-lab`. Stop if any other context is
active. The lab contains no real user data, and all failure-injection flags are
disabled by default.

## 1. Pod deletion: self-healing

**Goal:** observe how a Deployment restores its desired replica count.

```bash
kubectl -n chronorec-lab get pods -w
```

In another terminal window, run:

```bash
pod=$(kubectl -n chronorec-lab get pods \
  -l app.kubernetes.io/instance=chronorec-demo \
  -o jsonpath='{.items[0].metadata.name}')
kubectl -n chronorec-lab delete pod "$pod" --wait=false
```

**Expected result:** one Pod enters `Terminating`, the ReplicaSet creates a
replacement, and the Ready count returns to `2/2`. The root cause is artificial:
a manual deletion. The Deployment controller performs the recovery.

## 2. Failed readiness rollout and automatic rollback

**Goal:** prove that an unready release receives no traffic and cannot replace
all working replicas.

```bash
helm upgrade chronorec-demo helm/chronorec-demo \
  -n chronorec-lab \
  --reuse-values \
  --set lab.notReady=true \
  --atomic \
  --timeout 60s
```

The command should fail and perform a rollback. Verify the result:

```bash
helm history chronorec-demo -n chronorec-lab
kubectl get pods -n chronorec-lab
kubectl get endpoints chronorec-demo -n chronorec-lab
./scripts/verify-deployment.sh
```

**Root cause:** `/readyz` intentionally returns HTTP 503. **Recovery:** Helm
`--atomic` restores the previous values, after which both Pods become Ready
again. Helm 4 accepts this flag but warns that its new name is
`--rollback-on-failure`; `--atomic` remains here for Helm 3 compatibility.

## 3. CrashLoopBackOff

**Goal:** identify a startup failure through `describe` output and logs.

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

**Expected result:** the new Pod restarts while the old Ready Pods remain
available because of the rolling-update strategy. The logs contain
`Intentional lab startup failure`.

Recover the release:

```bash
helm upgrade chronorec-demo helm/chronorec-demo \
  -n chronorec-lab \
  --reuse-values \
  --set lab.crashOnStart=false \
  --wait
./scripts/verify-deployment.sh
```

## 4. OOMKilled

**Goal:** connect an exit and restart to a memory limit instead of guessing from
the symptoms.

```bash
helm upgrade chronorec-demo helm/chronorec-demo \
  -n chronorec-lab \
  --reuse-values \
  --set resources.limits.memory=64Mi \
  --set lab.allocateMemoryMb=256

kubectl get pods -n chronorec-lab -w
```

After the restart, locate the new Pod and inspect the reason:

```bash
kubectl get pods -n chronorec-lab \
  -l app.kubernetes.io/instance=chronorec-demo
kubectl describe pods -n chronorec-lab \
  -l app.kubernetes.io/instance=chronorec-demo
```

`Last State` should show `Reason: OOMKilled` and exit code 137.

Recover the release:

```bash
helm upgrade chronorec-demo helm/chronorec-demo \
  -n chronorec-lab \
  --reuse-values \
  --set resources.limits.memory=128Mi \
  --set lab.allocateMemoryMb=0 \
  --wait
./scripts/verify-deployment.sh
```

**Root cause:** the process attempted to allocate 256 MiB while its limit was
64 MiB. In a real incident, do not simply keep increasing the limit. First
inspect the memory profile, leaks, actual workload, and the correctness of the
resource requests and limits.

## Incident report template

For each exercise, record the following without including personal data:

- date and context (`kind-chronorec-lab`);
- observed symptom;
- commands and relevant output;
- root cause;
- fix or rollback;
- command that confirmed recovery;
- lesson learned and what would be different in production.
