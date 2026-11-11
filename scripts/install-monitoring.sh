#!/usr/bin/env bash
set -euo pipefail

helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

helm upgrade --install monitoring prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  --values monitoring/kube-prometheus-stack-values.yaml \
  --wait \
  --timeout 10m

helm upgrade --install chronorec-demo helm/chronorec-demo \
  --namespace chronorec-lab \
  --values helm/chronorec-demo/values-monitoring.yaml \
  --wait \
  --timeout 3m

printf '\nMonitoring is ready. See docs/MONITORING.md for access commands.\n'
