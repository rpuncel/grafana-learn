"""Spot-check integration tests: verify that live data is visible in Grafana.

These tests run against both Grafana instances (grafonnet track on :3000,
SDK track on :3001). Each instance is skipped automatically if unreachable.
"""

from __future__ import annotations

import time

import requests


def test_prometheus_datasource_configured(grafana_url):
    resp = requests.get(f"{grafana_url}/api/datasources/uid/prometheus", timeout=5)
    resp.raise_for_status()
    assert resp.json()["type"] == "prometheus"


def test_tempo_datasource_configured(grafana_url):
    resp = requests.get(f"{grafana_url}/api/datasources/uid/tempo", timeout=5)
    resp.raise_for_status()
    assert resp.json()["type"] == "tempo"


def test_prometheus_has_http_metrics(grafana_url):
    """At least one service is emitting HTTP request duration metrics."""
    resp = requests.get(
        f"{grafana_url}/api/datasources/proxy/uid/prometheus/api/v1/query",
        params={"query": "count(http_server_request_duration_seconds_count)"},
        timeout=5,
    )
    resp.raise_for_status()
    data = resp.json()
    assert data["status"] == "success"
    result = data["data"]["result"]
    assert result, "No http_server_request_duration_seconds_count series in Prometheus"
    assert float(result[0]["value"][1]) > 0


def test_tempo_has_traces(grafana_url):
    """Tempo has at least one trace ingested in the last hour."""
    now = int(time.time())
    resp = requests.get(
        f"{grafana_url}/api/datasources/proxy/uid/tempo/api/search",
        params={"q": "{}", "limit": 1, "start": now - 3600, "end": now},
        timeout=5,
    )
    resp.raise_for_status()
    traces = resp.json().get("traces", [])
    assert traces, "No traces found in Tempo for the last hour"


def test_loki_datasource_configured(grafana_url):
    resp = requests.get(f"{grafana_url}/api/datasources/uid/loki", timeout=5)
    resp.raise_for_status()
    assert resp.json()["type"] == "loki"


def test_loki_has_logs(grafana_url):
    """At least one service is emitting logs into Loki."""
    now = int(time.time())
    resp = requests.get(
        f"{grafana_url}/api/datasources/proxy/uid/loki/loki/api/v1/query_range",
        params={"query": '{service_name=~".+"}', "limit": 1, "start": now - 3600, "end": now},
        timeout=5,
    )
    resp.raise_for_status()
    streams = resp.json().get("data", {}).get("result", [])
    assert streams, "No log streams found in Loki for the last hour"


def test_logs_drilldown_dashboard_deployed(grafana_url):
    """Logs Drill-down dashboard exists in Grafana with the correct structure."""
    resp = requests.get(f"{grafana_url}/api/dashboards/uid/logs-drilldown", timeout=5)
    resp.raise_for_status()
    dash = resp.json()["dashboard"]
    assert dash["uid"] == "logs-drilldown"
    assert dash["title"] == "Logs Drill-down"
    panels = dash.get("panels", [])
    assert len(panels) == 1
    assert panels[0]["type"] == "logs"
