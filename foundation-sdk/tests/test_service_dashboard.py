"""Tests for service_dashboard.build_service_dashboard()."""

from __future__ import annotations

import json

from grafana_foundation_sdk.cog.encoder import JSONEncoder

from graflearn.dashboards.service_dashboard import build_service_dashboard


def _serialise() -> dict:
    return json.loads(json.dumps(build_service_dashboard(), cls=JSONEncoder))


def test_uid():
    assert _serialise()["uid"] == "service-dashboard"


def test_title():
    assert _serialise()["title"] == "Service Dashboard"


def test_tags():
    dash = _serialise()
    assert "service-dashboard" in dash["tags"]
    assert "sdk" in dash["tags"]


def test_refresh():
    assert _serialise()["refresh"] == "30s"


def test_panel_count():
    assert len(_serialise()["panels"]) == 3


def test_panel_titles():
    titles = [p["title"] for p in _serialise()["panels"]]
    assert "Request Rate" in titles
    assert "Error Rate" in titles
    assert "Request Duration p99" in titles


def test_latency_panel_full_width():
    latency = next(p for p in _serialise()["panels"] if p["title"] == "Request Duration p99")
    assert latency["gridPos"]["w"] == 24


def test_rate_panels_half_width():
    half_width = [p for p in _serialise()["panels"] if p["gridPos"]["w"] == 12]
    titles = {p["title"] for p in half_width}
    assert titles == {"Request Rate", "Error Rate"}


def test_service_variable():
    variables = _serialise()["templating"]["list"]
    assert len(variables) == 1
    v = variables[0]
    assert v["name"] == "service"
    assert v["type"] == "query"
    assert "label_values(http_server_request_duration_seconds_count, service_name)" in v["query"]


def test_service_variable_label():
    v = _serialise()["templating"]["list"][0]
    assert v["label"] == "Service"


def test_service_variable_datasource():
    v = _serialise()["templating"]["list"][0]
    assert v["datasource"]["type"] == "prometheus"


def test_service_variable_refresh_on_time_range():
    v = _serialise()["templating"]["list"][0]
    assert v["refresh"] == 2  # VariableRefresh.ON_TIME_RANGE_CHANGED


def test_queries_use_service_variable():
    for panel in _serialise()["panels"]:
        for target in panel["targets"]:
            assert "$service" in target["expr"]


def test_dashboard_link_to_fleet_overview():
    urls = [link["url"] for link in _serialise()["links"]]
    assert "/d/fleet-overview" in urls


def test_prometheus_datasource():
    for panel in _serialise()["panels"]:
        assert panel["datasource"]["type"] == "prometheus"


def test_serialises_to_valid_json():
    payload = {"dashboard": build_service_dashboard(), "folderId": 0, "overwrite": True}
    parsed = json.loads(json.dumps(payload, cls=JSONEncoder))
    assert parsed["dashboard"]["uid"] == "service-dashboard"
