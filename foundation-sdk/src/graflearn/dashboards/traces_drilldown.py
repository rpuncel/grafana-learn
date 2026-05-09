"""Traces Drill-down — Foundation SDK track.

$service variable; one traces panel querying Tempo with TraceQL.
Grafana's traces panel type has no SDK builder, so Panel is constructed directly.
"""

from __future__ import annotations

import typing
from typing import Any

from grafana_foundation_sdk.builders.dashboard import Dashboard, DashboardLink, QueryVariable
from grafana_foundation_sdk.builders.tempo import TempoQuery
from grafana_foundation_sdk.cog import builder as cogbuilder
from grafana_foundation_sdk.models.dashboard import (
    DataSourceRef,
    DashboardLinkType,
    GridPos,
    Panel,
    VariableRefresh,
)

_PROMETHEUS = DataSourceRef(type_val="prometheus", uid="prometheus")
_TEMPO = DataSourceRef(type_val="tempo", uid="tempo")


class _TracesPanel(cogbuilder.Builder[Panel]):
    """Minimal builder wrapping Grafana's native 'traces' panel type."""

    _internal: Panel

    def __init__(self) -> None:
        self._internal = Panel(type_val="traces")

    def build(self) -> Panel:
        return self._internal

    def title(self, title: str) -> typing.Self:
        self._internal.title = title
        return self

    def datasource(self, datasource: DataSourceRef) -> typing.Self:
        self._internal.datasource = datasource
        return self

    def with_target(self, target: Any) -> typing.Self:
        if self._internal.targets is None:
            self._internal.targets = []
        self._internal.targets.append(target)
        return self

    def grid_pos(self, grid_pos: GridPos) -> typing.Self:
        self._internal.grid_pos = grid_pos
        return self


def build_traces_drilldown_dashboard() -> Any:
    service_var = (
        QueryVariable("service")
        .label("Service")
        .datasource(_PROMETHEUS)
        .query("label_values(http_server_request_duration_seconds_count, service_name)")
        .refresh(VariableRefresh.ON_TIME_RANGE_CHANGED)
        .include_all(False)
    )

    traces_panel = (
        _TracesPanel()
        .title("Traces")
        .datasource(_TEMPO)
        .with_target(
            TempoQuery()
            .datasource(_TEMPO)
            .query('{resource.service.name="${service}"}')
            .query_type("traceql")
            .ref_id("A")
            .build()
        )
        .grid_pos(GridPos(h=16, w=24, x=0, y=0))
    )

    return (
        Dashboard("Traces Drill-down")
        .uid("traces-drilldown")
        .description(
            "Traces for the selected service, queried from Tempo. "
            "Opened from the Service Dashboard latency panel."
        )
        .tags(["traces-drilldown", "sdk"])
        .timezone("browser")
        .refresh("30s")
        .with_variable(service_var)
        .with_panel(traces_panel)
        .link(
            DashboardLink("Fleet Overview")
            .url("/d/fleet-overview")
            .type(DashboardLinkType.LINK)
            .keep_time(True)
            .target_blank(False)
        )
        .link(
            DashboardLink("Service Dashboard")
            .url("/d/service-dashboard")
            .type(DashboardLinkType.LINK)
            .keep_time(True)
            .target_blank(False)
        )
        .build()
    )
