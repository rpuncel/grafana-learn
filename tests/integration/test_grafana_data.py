"""Spot-check integration tests: verify that live data is visible in Grafana.

These tests require Grafana, Prometheus, and Tempo to be running locally
(docker-compose up). They are skipped automatically if Grafana is unreachable.
"""

from __future__ import annotations

import time

import requests

GRAFANA_URL = "http://localhost:3000"
PROMETHEUS_PROXY = f"{GRAFANA_URL}/api/datasources/proxy/uid/prometheus"
TEMPO_PROXY = f"{GRAFANA_URL}/api/datasources/proxy/uid/tempo"


def test_prometheus_datasource_configured():
    resp = requests.get(f"{GRAFANA_URL}/api/datasources/uid/prometheus", timeout=5)
    resp.raise_for_status()
    assert resp.json()["type"] == "prometheus"


def test_tempo_datasource_configured():
    resp = requests.get(f"{GRAFANA_URL}/api/datasources/uid/tempo", timeout=5)
    resp.raise_for_status()
    assert resp.json()["type"] == "tempo"


def test_prometheus_has_http_metrics():
    """At least one service is emitting HTTP request duration metrics."""
    resp = requests.get(
        f"{PROMETHEUS_PROXY}/api/v1/query",
        params={"query": "count(http_server_request_duration_seconds_count)"},
        timeout=5,
    )
    resp.raise_for_status()
    data = resp.json()
    assert data["status"] == "success"
    result = data["data"]["result"]
    assert result, "No http_server_request_duration_seconds_count series in Prometheus"
    assert float(result[0]["value"][1]) > 0


def test_tempo_has_traces():
    """Tempo has at least one trace ingested in the last hour."""
    now = int(time.time())
    resp = requests.get(
        f"{TEMPO_PROXY}/api/search",
        params={"q": "{}", "limit": 1, "start": now - 3600, "end": now},
        timeout=5,
    )
    resp.raise_for_status()
    traces = resp.json().get("traces", [])
    assert traces, "No traces found in Tempo for the last hour"
