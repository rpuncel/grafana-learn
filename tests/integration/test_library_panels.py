"""Integration tests: verify RED metrics library panels are deployed in both Grafana instances.

Skipped automatically if the instance is unreachable.
"""

from __future__ import annotations

import requests

EXPECTED_UIDS = {"red-metrics-rate", "red-metrics-error-rate", "red-metrics-latency"}


def test_red_metrics_rate_library_panel_exists(grafana_url):
    resp = requests.get(f"{grafana_url}/api/library-elements/red-metrics-rate", timeout=5)
    resp.raise_for_status()
    result = resp.json()["result"]
    assert result["uid"] == "red-metrics-rate"
    assert result["name"] == "Request Rate"
    assert result["kind"] == 1


def test_red_metrics_error_rate_library_panel_exists(grafana_url):
    resp = requests.get(f"{grafana_url}/api/library-elements/red-metrics-error-rate", timeout=5)
    resp.raise_for_status()
    result = resp.json()["result"]
    assert result["uid"] == "red-metrics-error-rate"
    assert result["name"] == "Error Rate"
    assert result["kind"] == 1


def test_red_metrics_latency_library_panel_exists(grafana_url):
    resp = requests.get(f"{grafana_url}/api/library-elements/red-metrics-latency", timeout=5)
    resp.raise_for_status()
    result = resp.json()["result"]
    assert result["uid"] == "red-metrics-latency"
    assert result["name"] == "Request Duration p99"
    assert result["kind"] == 1


def test_library_panel_models_are_timeseries(grafana_url):
    for uid in EXPECTED_UIDS:
        resp = requests.get(f"{grafana_url}/api/library-elements/{uid}", timeout=5)
        resp.raise_for_status()
        model = resp.json()["result"]["model"]
        assert model["type"] == "timeseries", f"{uid}: expected timeseries, got {model['type']}"


def test_service_dashboard_references_library_panels(grafana_url):
    resp = requests.get(f"{grafana_url}/api/dashboards/uid/service-dashboard", timeout=5)
    resp.raise_for_status()
    panels = resp.json()["dashboard"]["panels"]
    lib_uids = {
        p["libraryPanel"]["uid"]
        for p in panels
        if "libraryPanel" in p
    }
    assert lib_uids == EXPECTED_UIDS
