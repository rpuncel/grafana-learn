"""Unit tests for deploy.py — verifies that build_placeholder_dashboard()
produces the expected structure using the Grafana Foundation SDK."""

from __future__ import annotations

import json

from grafana_foundation_sdk.cog.encoder import JSONEncoder

from graflearn.tools.deploy import build_placeholder_dashboard


def _serialise(obj) -> dict:
    """Round-trip through JSON using the SDK encoder."""
    return json.loads(json.dumps(obj, cls=JSONEncoder))


def test_dashboard_title_and_uid():
    dash = _serialise(build_placeholder_dashboard())
    assert dash["title"] == "Placeholder — Foundation SDK Track"
    assert dash["uid"] == "sdk-placeholder"


def test_dashboard_tags():
    dash = _serialise(build_placeholder_dashboard())
    assert sorted(dash["tags"]) == ["placeholder", "sdk"]


def test_dashboard_timezone_and_refresh():
    dash = _serialise(build_placeholder_dashboard())
    assert dash["timezone"] == "browser"
    assert dash["refresh"] == "30s"


def test_single_text_panel():
    dash = _serialise(build_placeholder_dashboard())
    panels = dash.get("panels", [])
    assert len(panels) == 1
    panel = panels[0]
    assert panel["type"] == "text"
    assert panel["title"] == "Welcome"


def test_text_panel_grid_pos():
    dash = _serialise(build_placeholder_dashboard())
    gp = dash["panels"][0]["gridPos"]
    assert gp == {"x": 0, "y": 0, "w": 24, "h": 8}


def test_text_panel_mode_and_content():
    dash = _serialise(build_placeholder_dashboard())
    opts = dash["panels"][0]["options"]
    assert opts["mode"] == "markdown"
    assert "Foundation SDK Track" in opts["content"]


def test_dashboard_serialises_to_valid_json():
    """Ensure the full payload that deploy_dashboard would POST is serialisable."""
    dashboard = build_placeholder_dashboard()
    payload = {
        "dashboard": dashboard,
        "folderId": 0,
        "overwrite": True,
        "message": "test",
    }
    result = json.dumps(payload, cls=JSONEncoder)
    parsed = json.loads(result)
    assert parsed["dashboard"]["uid"] == "sdk-placeholder"
