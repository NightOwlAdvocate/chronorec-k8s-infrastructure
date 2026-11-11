# Verification record

This record contains only checks that were actually performed. Verification
date: 11 November 2026, Europe/Zurich.

| Check | Status | Observation |
|---|---|---|
| Workspace before creation | Verified | The directory was empty; no existing backend was found |
| Operating system | Verified | macOS 27.0.1, Apple Silicon arm64 |
| Git | Verified | 2.50.1 |
| Python | Verified | 3.14.3 |
| Docker CLI | Verified | 29.6.1 |
| Docker engine | Verified | Docker Desktop 29.6.1, Linux/arm64 engine |
| kubectl client | Verified | 1.36.1 |
| kind | Verified | 0.33.0; control-plane and worker, Kubernetes 1.37.0 |
| Helm | Verified | 4.3.1 locally; chart lint reported 0 failures; CI is configured for 3.18.4 |
| Python lint and tests | Verified | Ruff passed; pytest reported 6 passed |
| GitHub Actions | Configured; remote result pending review | The workflow is present; review the GitHub-hosted run before marking it verified |
| Docker image build | Verified | `chronorec-demo-api:dev`, Linux/arm64 |
| kind deployment and smoke test | Verified | 2/2 Ready; health, readiness, and synthetic summary responded successfully |
| Prometheus | Verified | Both API targets reported `health: up` with an empty `lastError` |
| Grafana | Verified | Pod reached 3/3 Ready; dashboard UID `chronorec-demo` was found through the API |
| Pod self-healing | Verified | The deleted Pod was replaced; ready=2, desired=2 |
| Failed readiness rollout | Verified | Revision 3 failed; revision 4 rolled back; the smoke test passed |
| CrashLoopBackOff | Verified | restartCount=1; the previous log showed the startup RuntimeError; recovery passed |
| OOMKilled | Verified | Reason OOMKilled, exit code 137, restartCount=1; recovery passed |

An additional edge case was found and fixed after the failed rollout:
`kubectl port-forward service/...` could select an unready Pod through the
Service selector. The verification script now selects the newest Pod with
`Ready=true` and applies request timeouts. The final rolling restart completed
with two Pods at `1/1 Running` and no restarts, followed by successful health,
readiness, and summary checks.

Update this table with a concrete result after every successful check. Do not
claim a result in the README, a CV, or an interview until the corresponding
verification has passed.
