"""RED metrics row — library panel definitions for the SDK track.

Provides:
- LIBRARY_PANELS: list of dicts to POST/PATCH to /api/library-elements
- build_*_ref(): Panel builders with libraryPanel refs for use in dashboards
"""

from __future__ import annotations

import json
from typing import Any

from grafana_foundation_sdk.builders.dashboard import Panel
from grafana_foundation_sdk.builders.prometheus import Dataquery as PrometheusQuery
from grafana_foundation_sdk.builders.timeseries import Panel as TimeseriesPanel
from grafana_foundation_sdk.cog.encoder import JSONEncoder
from grafana_foundation_sdk.models.dashboard import (
    DataSourceRef,
    GridPos,
    LibraryPanelRef,
)

_PROMETHEUS = DataSourceRef(type_val="prometheus", uid="prometheus")

RATE_UID = "red-metrics-rate"
ERROR_RATE_UID = "red-metrics-error-rate"
LATENCY_UID = "red-metrics-latency"

def _serialise(panel: TimeseriesPanel) -> dict[str, Any]:
    return json.loads(json.dumps(panel.build(), cls=JSONEncoder))


def _build_rate_model() -> TimeseriesPanel:
    return (
        TimeseriesPanel()
        .title("Request Rate")
        .datasource(_PROMETHEUS)
        .with_target(
            PrometheusQuery()
            .datasource(_PROMETHEUS)
            .expr(
                "sum by (service_name)(rate(http_server_request_duration_seconds_count"
                '{service_name="$service"}[$__rate_interval]))'
            )
            .legend_format("req/s")
        )
        .unit("reqps")
    )


def _build_error_rate_model() -> TimeseriesPanel:
    return (
        TimeseriesPanel()
        .title("Error Rate")
        .datasource(_PROMETHEUS)
        .with_target(
            PrometheusQuery()
            .datasource(_PROMETHEUS)
            .expr(
                "sum by (service_name)(rate(http_server_request_duration_seconds_count"
                '{service_name="$service", http_response_status_code=~"5.."}[$__rate_interval]))\n'
                "/ sum by (service_name)(rate(http_server_request_duration_seconds_count"
                '{service_name="$service"}[$__rate_interval]))'
            )
            .legend_format("error rate")
        )
        .unit("percentunit")
    )


def _build_latency_model() -> TimeseriesPanel:
    return (
        TimeseriesPanel()
        .title("Request Duration p99")
        .datasource(_PROMETHEUS)
        .with_target(
            PrometheusQuery()
            .datasource(_PROMETHEUS)
            .expr(
                "histogram_quantile(0.99, sum by (le, service_name)(rate(http_server_request_duration_seconds_bucket"
                '{service_name="$service"}[$__rate_interval])))'
            )
            .legend_format("p99")
        )
        .unit("s")
    )


LIBRARY_PANELS: list[dict[str, Any]] = [
    {"uid": RATE_UID, "name": "Request Rate", "kind": 1, "model": _serialise(_build_rate_model())},
    {"uid": ERROR_RATE_UID, "name": "Error Rate", "kind": 1, "model": _serialise(_build_error_rate_model())},
    {"uid": LATENCY_UID, "name": "Request Duration p99", "kind": 1, "model": _serialise(_build_latency_model())},
]


def build_rate_ref(grid_pos: GridPos) -> Panel:
    return (
        Panel()
        .grid_pos(grid_pos)
        .library_panel(LibraryPanelRef(name="Request Rate", uid=RATE_UID))
    )


def build_error_rate_ref(grid_pos: GridPos) -> Panel:
    return (
        Panel()
        .grid_pos(grid_pos)
        .library_panel(LibraryPanelRef(name="Error Rate", uid=ERROR_RATE_UID))
    )


def build_latency_ref(grid_pos: GridPos) -> Panel:
    return (
        Panel()
        .grid_pos(grid_pos)
        .library_panel(LibraryPanelRef(name="Request Duration p99", uid=LATENCY_UID))
    )
