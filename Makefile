SHELL := /bin/bash

IMAGE ?= chronorec-demo-api:dev
NAMESPACE ?= chronorec-lab
RELEASE ?= chronorec-demo
CHART ?= helm/chronorec-demo

.PHONY: check install-dev test lint run build cluster deploy verify monitoring status clean

check:
	./scripts/check-environment.sh

install-dev:
	python3 -m venv .venv
	.venv/bin/python -m pip install --upgrade pip
	.venv/bin/python -m pip install --requirement app/requirements-dev.txt

test:
	.venv/bin/python -m pytest

lint:
	.venv/bin/python -m ruff check app tests

run:
	PYTHONPATH=app .venv/bin/python -m uvicorn chronorec_demo.main:app --reload

build:
	docker build --tag $(IMAGE) app

cluster:
	kind create cluster --config kind/cluster.yaml

deploy: build
	kind load docker-image $(IMAGE) --name chronorec-lab
	helm upgrade --install $(RELEASE) $(CHART) --namespace $(NAMESPACE) --create-namespace --wait

verify:
	./scripts/verify-deployment.sh

monitoring:
	./scripts/install-monitoring.sh

status:
	kubectl get pods,service,deployment --namespace $(NAMESPACE) -o wide

clean:
	kind delete cluster --name chronorec-lab
