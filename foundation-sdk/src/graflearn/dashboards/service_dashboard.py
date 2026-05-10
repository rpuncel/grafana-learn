"""Service Dashboard — Foundation SDK track.

$service query variable; RED metrics panels referenced from library elements.
"""

from __future__ import annotations

from typing import Any

from grafana_foundation_sdk.builders.dashboard import Dashboard, DashboardLink, QueryVariable
from grafana_foundation_sdk.models.dashboard import (
    DataSourceRef,
    DashboardLinkType,
    GridPos,
    VariableRefresh,
)

from graflearn.lib.red_metrics_row import build_error_rate_ref, build_latency_ref, build_rate_ref

_PROMETHEUS = DataSourceRef(type_val="prometheus", uid="prometheus")


def build_service_dashboard() -> Any:
    service_var = (
        QueryVariable("service")
        .label("Service")
        .datasource(_PROMETHEUS)
        .query("label_values(http_server_request_duration_seconds_count, service_name)")
        .refresh(VariableRefresh.ON_TIME_RANGE_CHANGED)
        .include_all(False)
    )

    return (
        Dashboard("Service Dashboard")
        .uid("service-dashboard")
        .description(
            "RED metrics for the selected service. "
            "Use the $service variable to switch services."
        )
        .tags(["service-dashboard", "sdk"])
        .timezone("browser")
        .refresh("30s")
        .with_variable(service_var)
        .with_panel(build_rate_ref(GridPos(h=8, w=12, x=0, y=0)))
        .with_panel(build_error_rate_ref(GridPos(h=8, w=12, x=12, y=0)))
        .with_panel(build_latency_ref(GridPos(h=8, w=24, x=0, y=8)))
        .link(
            DashboardLink("Fleet Overview")
            .url("/d/fleet-overview")
            .type(DashboardLinkType.LINK)
            .keep_time(True)
            .target_blank(False)
        )
        .build()
    )
