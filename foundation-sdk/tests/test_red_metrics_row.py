"""Tests for graflearn.lib.red_metrics_row."""

from __future__ import annotations

import json

from grafana_foundation_sdk.cog.encoder import JSONEncoder

from graflearn.lib.red_metrics_row import (
    ERROR_RATE_UID,
    LATENCY_UID,
    LIBRARY_PANELS,
    RATE_UID,
    build_error_rate_ref,
    build_latency_ref,
    build_rate_ref,
)
from grafana_foundation_sdk.models.dashboard import GridPos


def _panel_ref_json(builder) -> dict:
    return json.loads(json.dumps(builder.build(), cls=JSONEncoder))


class TestLibraryPanels:
    def test_three_panels(self):
        assert len(LIBRARY_PANELS) == 3

    def test_uids(self):
        uids = {p["uid"] for p in LIBRARY_PANELS}
        assert uids == {RATE_UID, ERROR_RATE_UID, LATENCY_UID}

    def test_kind_is_panel(self):
        for p in LIBRARY_PANELS:
            assert p["kind"] == 1

    def test_names(self):
        names = {p["name"] for p in LIBRARY_PANELS}
        assert names == {"Request Rate", "Error Rate", "Request Duration p99"}

    def test_models_are_timeseries(self):
        for p in LIBRARY_PANELS:
            assert p["model"]["type"] == "timeseries"

    def test_models_use_service_variable(self):
        for p in LIBRARY_PANELS:
            targets = p["model"]["targets"]
            assert any("$service" in t["expr"] for t in targets)

    def test_rate_panel_unit(self):
        rate = next(p for p in LIBRARY_PANELS if p["uid"] == RATE_UID)
        assert rate["model"]["fieldConfig"]["defaults"]["unit"] == "reqps"

    def test_error_rate_panel_unit(self):
        error = next(p for p in LIBRARY_PANELS if p["uid"] == ERROR_RATE_UID)
        assert error["model"]["fieldConfig"]["defaults"]["unit"] == "percentunit"

    def test_latency_panel_unit(self):
        latency = next(p for p in LIBRARY_PANELS if p["uid"] == LATENCY_UID)
        assert latency["model"]["fieldConfig"]["defaults"]["unit"] == "s"

    def test_prometheus_datasource(self):
        for p in LIBRARY_PANELS:
            assert p["model"]["datasource"]["type"] == "prometheus"


class TestRefBuilders:
    def test_rate_ref_uid(self):
        ref = _panel_ref_json(build_rate_ref(GridPos(h=8, w=12, x=0, y=0)))
        assert ref["libraryPanel"]["uid"] == RATE_UID

    def test_error_rate_ref_uid(self):
        ref = _panel_ref_json(build_error_rate_ref(GridPos(h=8, w=12, x=12, y=0)))
        assert ref["libraryPanel"]["uid"] == ERROR_RATE_UID

    def test_latency_ref_uid(self):
        ref = _panel_ref_json(build_latency_ref(GridPos(h=8, w=24, x=0, y=8)))
        assert ref["libraryPanel"]["uid"] == LATENCY_UID

    def test_rate_ref_grid_pos(self):
        ref = _panel_ref_json(build_rate_ref(GridPos(h=8, w=12, x=0, y=0)))
        assert ref["gridPos"] == {"h": 8, "w": 12, "x": 0, "y": 0}

    def test_latency_ref_grid_pos(self):
        ref = _panel_ref_json(build_latency_ref(GridPos(h=8, w=24, x=0, y=8)))
        assert ref["gridPos"] == {"h": 8, "w": 24, "x": 0, "y": 8}
