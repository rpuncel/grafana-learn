"""Logs Drill-down — Foundation SDK track.

$service variable; one logs panel querying Loki with LogQL.
"""

from __future__ import annotations

from typing import Any

from grafana_foundation_sdk.builders.dashboard import Dashboard, DashboardLink, QueryVariable
from grafana_foundation_sdk.builders.loki import Dataquery as LokiQuery
from grafana_foundation_sdk.builders.logs import Panel as LogsPanel
from grafana_foundation_sdk.models.dashboard import (
    DataSourceRef,
    DashboardLinkType,
    GridPos,
    VariableRefresh,
)

_PROMETHEUS = DataSourceRef(type_val="prometheus", uid="prometheus")
_LOKI = DataSourceRef(type_val="loki", uid="loki")


def build_logs_drilldown_dashboard() -> Any:
    service_var = (
        QueryVariable("service")
        .label("Service")
        .datasource(_PROMETHEUS)
        .query("label_values(http_server_request_duration_seconds_count, service_name)")
        .refresh(VariableRefresh.ON_TIME_RANGE_CHANGED)
        .include_all(False)
    )

    logs_panel = (
        LogsPanel()
        .title("Logs")
        .datasource(_LOKI)
        .with_target(
            LokiQuery()
            .datasource(_LOKI)
            .expr('{service_name="${service}"}')
            .query_type("range")
            .ref_id("A")
        )
        .grid_pos(GridPos(h=16, w=24, x=0, y=0))
    )

    return (
        Dashboard("Logs Drill-down")
        .uid("logs-drilldown")
        .description("Logs for the selected service, queried from Loki.")
        .tags(["logs-drilldown", "sdk"])
        .timezone("browser")
        .refresh("30s")
        .with_variable(service_var)
        .with_panel(logs_panel)
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
