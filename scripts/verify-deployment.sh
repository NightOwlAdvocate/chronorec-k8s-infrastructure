#!/usr/bin/env bash
set -euo pipefail

namespace="chronorec-lab"
local_port="18000"

kubectl --namespace "${namespace}" rollout status deployment/chronorec-demo --timeout=120s

# Port-forward a Pod that is explicitly Ready. Forwarding a Service immediately
# after a failed rollout can select a terminating or unready Pod by its selector.
ready_pod="$(
  kubectl --namespace "${namespace}" get pods \
    --selector=app.kubernetes.io/instance=chronorec-demo \
    --sort-by=.metadata.creationTimestamp \
    -o jsonpath='{range .items[?(@.status.containerStatuses[0].ready==true)]}{.metadata.name}{"\n"}{end}' \
    | tail -n 1
)"
test -n "${ready_pod}"

kubectl --namespace "${namespace}" port-forward "pod/${ready_pod}" "${local_port}:8000" >/tmp/chronorec-port-forward.log 2>&1 &
port_forward_pid=$!
trap 'kill "${port_forward_pid}" >/dev/null 2>&1 || true' EXIT

for _ in {1..20}; do
  if curl --silent --fail --connect-timeout 1 --max-time 3 \
    "http://127.0.0.1:${local_port}/healthz" >/dev/null; then
    break
  fi
  sleep 1
done

health="$(curl --silent --show-error --fail --connect-timeout 1 --max-time 5 \
  "http://127.0.0.1:${local_port}/healthz")"
readiness="$(curl --silent --show-error --fail --connect-timeout 1 --max-time 5 \
  "http://127.0.0.1:${local_port}/readyz")"
summary="$(curl --silent --show-error --fail --connect-timeout 1 --max-time 5 \
  "http://127.0.0.1:${local_port}/api/v1/summary")"

printf '[verified] rollout complete\n'
printf '[verified] health: %s\n' "${health}"
printf '[verified] readiness: %s\n' "${readiness}"
printf '[verified] synthetic summary: %s\n' "${summary}"
