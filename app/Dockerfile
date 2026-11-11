# syntax=docker/dockerfile:1
FROM python:3.13-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PATH="/opt/venv/bin:${PATH}"

RUN python -m venv /opt/venv \
    && addgroup --system --gid 10001 app \
    && adduser --system --uid 10001 --ingroup app --home /app app

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir --requirement requirements.txt

COPY --chown=10001:10001 chronorec_demo ./chronorec_demo

USER 10001:10001
EXPOSE 8000

CMD ["uvicorn", "chronorec_demo.main:app", "--host", "0.0.0.0", "--port", "8000", "--no-access-log"]
