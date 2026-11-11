#!/usr/bin/env bash
set -euo pipefail

missing=0

printf 'Operating system: '
uname -srm

for tool in git python3 docker kubectl kind helm curl; do
  if command -v "${tool}" >/dev/null 2>&1; then
    printf '[ok] %-8s %s\n' "${tool}" "$(command -v "${tool}")"
  else
    printf '[missing] %s\n' "${tool}"
    missing=1
  fi
done

if command -v docker >/dev/null 2>&1; then
  if docker info >/dev/null 2>&1; then
    printf '[ok] Docker engine is running\n'
  else
    printf '[action needed] Docker is installed, but Docker Desktop is not running\n'
    missing=1
  fi
fi

if [[ "${missing}" -ne 0 ]]; then
  printf '\nRead docs/SETUP_MAC.md before creating the cluster.\n'
  exit 1
fi

printf '\nEnvironment is ready for the local Kubernetes lab.\n'
