#!/usr/bin/env bash
set -euo pipefail

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${project_root}"

./scripts/check-environment.sh

if ! kind get clusters | grep -qx 'chronorec-lab'; then
  kind create cluster --config kind/cluster.yaml
else
  printf 'kind cluster chronorec-lab already exists; reusing it.\n'
fi

docker build --tag chronorec-demo-api:dev app
kind load docker-image chronorec-demo-api:dev --name chronorec-lab

helm upgrade --install chronorec-demo helm/chronorec-demo \
  --namespace chronorec-lab \
  --create-namespace \
  --wait \
  --timeout 3m

./scripts/verify-deployment.sh
