# Architecture and design decisions

## Purpose

This project demonstrates the infrastructure lifecycle of an application:
testing, container builds, local deployment, health checks, observability, and
recovery from controlled failures.

## Boundary with the real ChronoRec/MinFri MVP

The training API was created from scratch and does not import code from the real
MVP. It does not accept user-generated records and returns only three static,
synthetic entries. This design makes it possible to demonstrate the
infrastructure publicly without exposing personal data, private product logic,
or future production secrets.

## Components

| Component | Role | Why it is included |
|---|---|---|
| FastAPI | Small HTTP workload | Provides probes, metrics, and a testable API |
| Docker | Reproducible runtime | Runs the same application locally and in CI |
| kind | Local Kubernetes | Creates and removes a disposable cluster quickly |
| Helm | Parameterised release | Demonstrates upgrades, rollbacks, and configuration values |
| Prometheus | Metrics collection | Observes requests and workload state |
| Grafana | Visualisation | Displays request rate, p95 latency, and available replicas |
| GitHub Actions | Automated validation | Tests the code and performs a real deployment to kind |

## Reliability and security

- Two replicas and a rolling update with `maxUnavailable: 0` preserve the old,
  ready version during a failed update.
- The readiness probe removes an unready Pod from Service endpoints.
- The liveness probe restarts an unhealthy process without replacing readiness
  semantics.
- Resource requests and limits make scheduling explicit and support the
  OOMKilled exercise.
- The container and Pod run without root privileges. Linux capabilities are
  dropped, the root filesystem is read-only, and the service-account token is
  not mounted.
- The NetworkPolicy permits access to the API from namespaces in the cluster.
  This is a basic training policy; the kind CNI is not evidence of production
  network segmentation.
- The PodDisruptionBudget preserves one available replica during voluntary
  disruptions. It cannot protect against node failure or insufficient cluster
  resources.

## Deliberate exclusions

The lab has no database, authentication, ingress, TLS, cloud registry,
persistent volumes, backups, or real user data. These capabilities must not be
implied in the project description. They are separate future stages that should
only be added when they solve a demonstrated requirement.
