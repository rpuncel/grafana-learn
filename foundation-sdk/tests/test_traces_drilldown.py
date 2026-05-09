"""Tests for traces_drilldown.build_traces_drilldown_dashboard()."""

from __future__ import annotations

import json

from grafana_foundation_sdk.cog.encoder import JSONEncoder

from graflearn.dashboards.traces_drilldown import build_traces_drilldown_dashboard


def _serialise() -> dict:
    return json.loads(json.dumps(build_traces_drilldown_dashboard(), cls=JSONEncoder))


def test_uid():
    assert _serialise()["uid"] == "traces-drilldown"


def test_title():
    assert _serialise()["title"] == "Traces Drill-down"


def test_tags():
    dash = _serialise()
    assert "traces-drilldown" in dash["tags"]
    assert "sdk" in dash["tags"]


def test_refresh():
    assert _serialise()["refresh"] == "30s"


def test_panel_count():
    assert len(_serialise()["panels"]) == 1


def test_panel_type_traces():
    panel = _serialise()["panels"][0]
    assert panel["type"] == "traces"


def test_panel_title():
    panel = _serialise()["panels"][0]
    assert panel["title"] == "Traces"


def test_panel_full_width():
    panel = _serialise()["panels"][0]
    assert panel["gridPos"]["w"] == 24


def test_panel_datasource_tempo():
    panel = _serialise()["panels"][0]
    assert panel["datasource"]["type"] == "tempo"
    assert panel["datasource"]["uid"] == "tempo"


def test_panel_query_uses_service_variable():
    target = _serialise()["panels"][0]["targets"][0]
    assert "${service}" in target["query"]


def test_panel_query_type_traceql():
    target = _serialise()["panels"][0]["targets"][0]
    assert target.get("queryType") == "traceql"


def test_service_variable():
    variables = _serialise()["templating"]["list"]
    assert len(variables) == 1
    v = variables[0]
    assert v["name"] == "service"
    assert v["type"] == "query"
    assert "label_values(http_server_request_duration_seconds_count, service_name)" in v["query"]


def test_service_variable_datasource():
    v = _serialise()["templating"]["list"][0]
    assert v["datasource"]["type"] == "prometheus"


def test_service_variable_refresh_on_time_range():
    v = _serialise()["templating"]["list"][0]
    assert v["refresh"] == 2


def test_dashboard_links():
    urls = [link["url"] for link in _serialise()["links"]]
    assert "/d/fleet-overview" in urls
    assert "/d/service-dashboard" in urls


def test_serialises_to_valid_json():
    payload = {"dashboard": build_traces_drilldown_dashboard(), "folderId": 0, "overwrite": True}
    parsed = json.loads(json.dumps(payload, cls=JSONEncoder))
    assert parsed["dashboard"]["uid"] == "traces-drilldown"
