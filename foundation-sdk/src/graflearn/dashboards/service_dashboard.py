"""Service Dashboard — Foundation SDK track.

$service query variable; three panels: request rate, error rate, latency p99.
"""

from __future__ import annotations

from typing import Any

from grafana_foundation_sdk.builders.dashboard import Dashboard, DashboardLink, QueryVariable
from grafana_foundation_sdk.builders.prometheus import Dataquery as PrometheusQuery
from grafana_foundation_sdk.builders.timeseries import Panel as TimeseriesPanel
from grafana_foundation_sdk.models.dashboard import (
    DataSourceRef,
    DashboardLinkType,
    GridPos,
    VariableRefresh,
)

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

    rate_panel = (
        TimeseriesPanel()
        .title("Request Rate")
        .datasource(_PROMETHEUS)
        .with_target(
            PrometheusQuery()
            .datasource(_PROMETHEUS)
            .expr(
                "sum(rate(http_server_request_duration_seconds_count"
                '{service_name="$service"}[$__rate_interval]))'
            )
            .legend_format("req/s")
        )
        .unit("reqps")
        .grid_pos(GridPos(h=8, w=12, x=0, y=0))
    )

    error_rate_panel = (
        TimeseriesPanel()
        .title("Error Rate")
        .datasource(_PROMETHEUS)
        .with_target(
            PrometheusQuery()
            .datasource(_PROMETHEUS)
            .expr(
                "sum(rate(http_server_request_duration_seconds_count"
                '{service_name="$service", http_response_status_code=~"5.."}[$__rate_interval]))\n'
                "/ sum(rate(http_server_request_duration_seconds_count"
                '{service_name="$service"}[$__rate_interval]))'
            )
            .legend_format("error rate")
        )
        .unit("percentunit")
        .grid_pos(GridPos(h=8, w=12, x=12, y=0))
    )

    latency_panel = (
        TimeseriesPanel()
        .title("Request Duration p99")
        .datasource(_PROMETHEUS)
        .with_target(
            PrometheusQuery()
            .datasource(_PROMETHEUS)
            .expr(
                "histogram_quantile(0.99, sum(rate(http_server_request_duration_seconds_bucket"
                '{service_name="$service"}[$__rate_interval])) by (le))'
            )
            .legend_format("p99")
        )
        .unit("s")
        .grid_pos(GridPos(h=8, w=24, x=0, y=8))
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
        .with_panel(rate_panel)
        .with_panel(error_rate_panel)
        .with_panel(latency_panel)
        .link(
            DashboardLink("Fleet Overview")
            .url("/d/fleet-overview")
            .type(DashboardLinkType.LINK)
            .keep_time(True)
            .target_blank(False)
        )
        .build()
    )
