"""Fleet Overview dashboard — Foundation SDK track.

Two time series panels (request rate + error rate) grouped by service_name.
Panel-level data links navigate to the Service Dashboard for the clicked service.
"""

from __future__ import annotations

from typing import Any

from grafana_foundation_sdk.builders.dashboard import Dashboard, DashboardLink
from grafana_foundation_sdk.builders.nodegraph import Panel as NodeGraphPanel
from grafana_foundation_sdk.builders.prometheus import Dataquery as PrometheusQuery
from grafana_foundation_sdk.builders.table import Panel as TablePanel
from grafana_foundation_sdk.builders.tempo import TempoQuery
from grafana_foundation_sdk.builders.timeseries import Panel as TimeseriesPanel
from grafana_foundation_sdk.models.dashboard import DataSourceRef, DataTransformerConfig, DashboardLinkType, GridPos

_PROMETHEUS = DataSourceRef(type_val="prometheus", uid="prometheus")
_TEMPO = DataSourceRef(type_val="tempo", uid="tempo")

_SERVICE_DASHBOARD_DATA_LINK = (
    DashboardLink("Open Service Dashboard")
    .url("/d/service-dashboard?var-service=${__field.labels.service_name}")
    .type(DashboardLinkType.LINK)
    .target_blank(False)
)


def build_fleet_overview_dashboard() -> Any:
    rate_panel = (
        TimeseriesPanel()
        .title("Request Rate by Service")
        .datasource(_PROMETHEUS)
        .with_target(
            PrometheusQuery()
            .datasource(_PROMETHEUS)
            .expr("sum(rate(http_server_request_duration_seconds_count[$__rate_interval])) by (service_name)")
            .legend_format("{{service_name}}")
        )
        .unit("reqps")
        .data_links([_SERVICE_DASHBOARD_DATA_LINK])
        .grid_pos(GridPos(h=8, w=24, x=0, y=0))
    )

    error_rate_panel = (
        TimeseriesPanel()
        .title("Error Rate by Service")
        .datasource(_PROMETHEUS)
        .with_target(
            PrometheusQuery()
            .datasource(_PROMETHEUS)
            .expr(
                "sum(rate(http_server_request_duration_seconds_count"
                '{http_response_status_code=~"5.."}[$__rate_interval])) by (service_name)\n'
                "/ sum(rate(http_server_request_duration_seconds_count[$__rate_interval])) by (service_name)"
            )
            .legend_format("{{service_name}}")
        )
        .unit("percentunit")
        .data_links([_SERVICE_DASHBOARD_DATA_LINK])
        .grid_pos(GridPos(h=8, w=24, x=0, y=8))
    )

    node_graph_panel = (
        NodeGraphPanel()
        .title("Service Topology")
        .datasource(_TEMPO)
        .with_target(
            TempoQuery()
            .datasource(_TEMPO)
            .query_type("serviceMap")
            .query("")
            .ref_id("A")
        )
        .grid_pos(GridPos(h=12, w=24, x=0, y=16))
    )

    error_rate_summary_panel = (
        TablePanel()
        .title("Current Error Rate by Service")
        .datasource(_PROMETHEUS)
        .with_target(
            PrometheusQuery()
            .datasource(_PROMETHEUS)
            .expr(
                "sum(rate(http_server_request_duration_seconds_count"
                '{http_response_status_code=~"5.."}[$__rate_interval])) by (service_name)\n'
                "/ sum(rate(http_server_request_duration_seconds_count[$__rate_interval])) by (service_name)"
            )
            .legend_format("{{service_name}}")
        )
        .with_transformation(
            DataTransformerConfig(
                id_val="reduce",
                options={"reducers": ["lastNotNull"], "mode": "seriesToRows"},
            )
        )
        .unit("percentunit")
        .grid_pos(GridPos(h=6, w=24, x=0, y=28))
    )

    return (
        Dashboard("Fleet Overview")
        .uid("fleet-overview")
        .description(
            "All services at a glance — request rate and error rate. "
            "Click a series to open the Service Dashboard for that service."
        )
        .tags(["fleet-overview", "sdk"])
        .timezone("browser")
        .refresh("30s")
        .with_panel(rate_panel)
        .with_panel(error_rate_panel)
        .with_panel(node_graph_panel)
        .with_panel(error_rate_summary_panel)
        .link(
            DashboardLink("Service Dashboard")
            .url("/d/service-dashboard")
            .type(DashboardLinkType.LINK)
            .keep_time(True)
            .target_blank(False)
        )
        .build()
    )
