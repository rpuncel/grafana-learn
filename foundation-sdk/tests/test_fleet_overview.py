"""Tests for fleet_overview.build_fleet_overview_dashboard()."""

from __future__ import annotations

import json

from grafana_foundation_sdk.cog.encoder import JSONEncoder

from graflearn.dashboards.fleet_overview import build_fleet_overview_dashboard


def _serialise() -> dict:
    return json.loads(json.dumps(build_fleet_overview_dashboard(), cls=JSONEncoder))


def test_uid():
    assert _serialise()["uid"] == "fleet-overview"


def test_title():
    assert _serialise()["title"] == "Fleet Overview"


def test_tags():
    dash = _serialise()
    assert "fleet-overview" in dash["tags"]
    assert "sdk" in dash["tags"]


def test_refresh():
    assert _serialise()["refresh"] == "30s"


def test_panel_count():
    assert len(_serialise()["panels"]) == 2


def test_panel_titles():
    titles = [p["title"] for p in _serialise()["panels"]]
    assert "Request Rate by Service" in titles
    assert "Error Rate by Service" in titles


def test_panels_full_width():
    for panel in _serialise()["panels"]:
        assert panel["gridPos"]["w"] == 24


def test_panel_data_links():
    expected_url = "/d/service-dashboard?var-service=${__field.labels.service_name}"
    for panel in _serialise()["panels"]:
        links = panel["fieldConfig"]["defaults"]["links"]
        assert any(link["url"] == expected_url for link in links)


def test_dashboard_link_to_service_dashboard():
    urls = [link["url"] for link in _serialise()["links"]]
    assert "/d/service-dashboard" in urls


def test_prometheus_datasource():
    for panel in _serialise()["panels"]:
        assert panel["datasource"]["type"] == "prometheus"


def test_serialises_to_valid_json():
    payload = {"dashboard": build_fleet_overview_dashboard(), "folderId": 0, "overwrite": True}
    parsed = json.loads(json.dumps(payload, cls=JSONEncoder))
    assert parsed["dashboard"]["uid"] == "fleet-overview"
