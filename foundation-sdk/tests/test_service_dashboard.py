"""Tests for service_dashboard.build_service_dashboard()."""

from __future__ import annotations

import json

from grafana_foundation_sdk.cog.encoder import JSONEncoder

from graflearn.dashboards.service_dashboard import build_service_dashboard
from graflearn.lib.red_metrics_row import ERROR_RATE_UID, LATENCY_UID, RATE_UID


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


def test_panels_are_library_panel_refs():
    for panel in _serialise()["panels"]:
        assert "libraryPanel" in panel


def test_library_panel_uids():
    uids = {p["libraryPanel"]["uid"] for p in _serialise()["panels"]}
    assert uids == {RATE_UID, ERROR_RATE_UID, LATENCY_UID}


def test_library_panel_names():
    names = {p["libraryPanel"]["name"] for p in _serialise()["panels"]}
    assert names == {"Request Rate", "Error Rate", "Request Duration p99"}


def test_latency_ref_full_width():
    latency = next(
        p for p in _serialise()["panels"]
        if p["libraryPanel"]["uid"] == LATENCY_UID
    )
    assert latency["gridPos"]["w"] == 24


def test_rate_refs_half_width():
    half_width = [p for p in _serialise()["panels"] if p["gridPos"]["w"] == 12]
    uids = {p["libraryPanel"]["uid"] for p in half_width}
    assert uids == {RATE_UID, ERROR_RATE_UID}


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


def test_dashboard_link_to_fleet_overview():
    urls = [link["url"] for link in _serialise()["links"]]
    assert "/d/fleet-overview" in urls


def test_serialises_to_valid_json():
    payload = {"dashboard": build_service_dashboard(), "folderId": 0, "overwrite": True}
    parsed = json.loads(json.dumps(payload, cls=JSONEncoder))
    assert parsed["dashboard"]["uid"] == "service-dashboard"
