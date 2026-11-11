"""Minimal API for the ChronoRec Kubernetes infrastructure lab.

All records in this module are invented. This service must not be used to
collect or process real health, voice, sleep, or mood data.
"""

from __future__ import annotations

import os
import time
from contextlib import asynccontextmanager
from typing import Annotated, Literal

from fastapi import FastAPI, HTTPException, Query, Response, status
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from pydantic import BaseModel, ConfigDict, Field

REQUESTS = Counter(
    "chronorec_http_requests_total",
    "Number of HTTP requests handled by the demo API.",
    ("method", "path", "status"),
)
REQUEST_DURATION = Histogram(
    "chronorec_http_request_duration_seconds",
    "Request duration for the demo API.",
    ("path",),
)


class DemoEntry(BaseModel):
    model_config = ConfigDict(frozen=True)

    entry_id: str
    day: str
    sleep_hours: float = Field(ge=0, le=24)
    mood: Literal["calm", "energetic", "tired", "focused"]
    activity_minutes: int = Field(ge=0)
    note: str


class DemoSummary(BaseModel):
    model_config = ConfigDict(frozen=True)

    dataset: str
    privacy_notice: str
    entries: int
    average_sleep_hours: float
    average_activity_minutes: float


SYNTHETIC_ENTRIES = (
    DemoEntry(
        entry_id="demo-001",
        day="2030-01-01",
        sleep_hours=7.5,
        mood="calm",
        activity_minutes=35,
        note="Synthetic example: morning walk and quiet reading.",
    ),
    DemoEntry(
        entry_id="demo-002",
        day="2030-01-02",
        sleep_hours=6.8,
        mood="tired",
        activity_minutes=20,
        note="Synthetic example: a deliberately ordinary demo day.",
    ),
    DemoEntry(
        entry_id="demo-003",
        day="2030-01-03",
        sleep_hours=8.1,
        mood="focused",
        activity_minutes=50,
        note="Synthetic example: focused work and an evening cycle.",
    ),
)


def env_flag(name: str) -> bool:
    return os.getenv(name, "false").strip().lower() in {"1", "true", "yes", "on"}


@asynccontextmanager
async def lifespan(_: FastAPI):
    if env_flag("LAB_CRASH_ON_START"):
        raise RuntimeError("Intentional lab startup failure")

    memory_megabytes = int(os.getenv("LAB_ALLOCATE_MEMORY_MB", "0"))
    memory_block = bytearray(memory_megabytes * 1024 * 1024) if memory_megabytes else None
    yield
    del memory_block


app = FastAPI(
    title="ChronoRec Infrastructure Demo API",
    description=(
        "A synthetic, read-only API for learning containers, Kubernetes, Helm, "
        "observability, and failure recovery. It is not the ChronoRec MVP."
    ),
    version="0.1.0",
    lifespan=lifespan,
)


@app.middleware("http")
async def observe_requests(request, call_next):
    path = request.url.path
    started = time.perf_counter()
    response = await call_next(request)
    REQUESTS.labels(request.method, path, str(response.status_code)).inc()
    REQUEST_DURATION.labels(path).observe(time.perf_counter() - started)
    return response


@app.get("/healthz", tags=["operations"])
def health() -> dict[str, str]:
    """Liveness: the process can still answer HTTP requests."""
    return {"status": "alive"}


@app.get("/readyz", tags=["operations"])
def readiness() -> dict[str, str]:
    """Readiness: the pod may receive user traffic."""
    if env_flag("LAB_NOT_READY"):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Intentional lab readiness failure",
        )
    return {"status": "ready"}


@app.get("/metrics", include_in_schema=False)
def metrics() -> Response:
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/api/v1/entries", response_model=list[DemoEntry], tags=["synthetic-demo"])
def list_entries(
    limit: Annotated[int, Query(ge=1, le=50)] = 10,
) -> list[DemoEntry]:
    return list(SYNTHETIC_ENTRIES[:limit])


@app.get("/api/v1/summary", response_model=DemoSummary, tags=["synthetic-demo"])
def summary() -> DemoSummary:
    count = len(SYNTHETIC_ENTRIES)
    return DemoSummary(
        dataset="synthetic-demo-v1",
        privacy_notice="Invented training data only; no personal or medical data.",
        entries=count,
        average_sleep_hours=round(sum(item.sleep_hours for item in SYNTHETIC_ENTRIES) / count, 2),
        average_activity_minutes=round(
            sum(item.activity_minutes for item in SYNTHETIC_ENTRIES) / count, 2
        ),
    )
