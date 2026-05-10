import json
import subprocess
from pathlib import Path

GRAFONNET_DIR = Path(__file__).parent.parent
VENDOR_DIR = GRAFONNET_DIR / "vendor"
DASHBOARDS_DIR = GRAFONNET_DIR / "dashboards"
LIB_DIR = GRAFONNET_DIR / "lib"


def compile_dashboard(name: str) -> dict:
    result = subprocess.run(
        ["jsonnet", "-J", str(VENDOR_DIR), str(DASHBOARDS_DIR / f"{name}.jsonnet")],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)


def compile_lib(name: str):
    result = subprocess.run(
        ["jsonnet", "-J", str(VENDOR_DIR), str(LIB_DIR / f"{name}.libsonnet")],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)


class TestFleetOverview:
    def setup_method(self):
        self.dash = compile_dashboard("fleet-overview")

    def test_uid(self):
        assert self.dash["uid"] == "fleet-overview"

    def test_title(self):
        assert self.dash["title"] == "Fleet Overview"

    def test_tags(self):
        assert self.dash["tags"] == ["fleet-overview", "grafonnet"]

    def test_refresh(self):
        assert self.dash["refresh"] == "30s"

    def test_panel_count(self):
        assert len(self.dash["panels"]) == 3

    def test_panel_titles(self):
        titles = [p["title"] for p in self.dash["panels"]]
        assert "Request Rate by Service" in titles
        assert "Error Rate by Service" in titles
        assert "Service Topology" in titles

    def test_panels_full_width(self):
        for panel in self.dash["panels"]:
            assert panel["gridPos"]["w"] == 24

    def test_panel_data_links(self):
        expected_url = "/d/service-dashboard?var-service=${__field.labels.service_name}"
        ts_panels = [p for p in self.dash["panels"] if p["type"] == "timeseries"]
        for panel in ts_panels:
            links = panel["fieldConfig"]["defaults"]["links"]
            assert any(link["url"] == expected_url for link in links)

    def test_dashboard_link_to_service_dashboard(self):
        urls = [link["url"] for link in self.dash["links"]]
        assert "/d/service-dashboard" in urls

    def test_prometheus_datasource(self):
        ts_panels = [p for p in self.dash["panels"] if p["type"] == "timeseries"]
        for panel in ts_panels:
            assert panel["datasource"]["type"] == "prometheus"

    def test_node_graph_panel(self):
        assert any(p["type"] == "nodeGraph" for p in self.dash["panels"])

    def test_node_graph_datasource_tempo(self):
        ng = next(p for p in self.dash["panels"] if p["type"] == "nodeGraph")
        assert ng["datasource"]["type"] == "tempo"
        assert ng["datasource"]["uid"] == "tempo"

    def test_node_graph_query_type(self):
        ng = next(p for p in self.dash["panels"] if p["type"] == "nodeGraph")
        assert ng["targets"][0]["queryType"] == "serviceMap"


class TestServiceDashboard:
    def setup_method(self):
        self.dash = compile_dashboard("service-dashboard")

    def test_uid(self):
        assert self.dash["uid"] == "service-dashboard"

    def test_title(self):
        assert self.dash["title"] == "Service Dashboard"

    def test_tags(self):
        assert self.dash["tags"] == ["service-dashboard", "grafonnet"]

    def test_refresh(self):
        assert self.dash["refresh"] == "30s"

    def test_panel_count(self):
        assert len(self.dash["panels"]) == 3

    def test_panels_are_library_panel_refs(self):
        for panel in self.dash["panels"]:
            assert "libraryPanel" in panel

    def test_library_panel_uids(self):
        uids = {p["libraryPanel"]["uid"] for p in self.dash["panels"]}
        assert uids == {"red-metrics-rate", "red-metrics-error-rate", "red-metrics-latency"}

    def test_library_panel_names(self):
        names = {p["libraryPanel"]["name"] for p in self.dash["panels"]}
        assert names == {"Request Rate", "Error Rate", "Request Duration p99"}

    def test_latency_ref_full_width(self):
        latency = next(
            p for p in self.dash["panels"]
            if p["libraryPanel"]["uid"] == "red-metrics-latency"
        )
        assert latency["gridPos"]["w"] == 24

    def test_rate_refs_half_width(self):
        half_width = [p for p in self.dash["panels"] if p["gridPos"]["w"] == 12]
        uids = {p["libraryPanel"]["uid"] for p in half_width}
        assert uids == {"red-metrics-rate", "red-metrics-error-rate"}

    def test_service_variable(self):
        variables = self.dash["templating"]["list"]
        assert len(variables) == 1
        v = variables[0]
        assert v["name"] == "service"
        assert v["type"] == "query"
        assert "label_values(http_server_request_duration_seconds_count, service_name)" in v["query"]

    def test_service_variable_label(self):
        v = self.dash["templating"]["list"][0]
        assert v["label"] == "Service"

    def test_service_variable_datasource(self):
        v = self.dash["templating"]["list"][0]
        assert v["datasource"]["type"] == "prometheus"

    def test_dashboard_link_to_fleet_overview(self):
        urls = [link["url"] for link in self.dash["links"]]
        assert "/d/fleet-overview" in urls


class TestRedMetricsRow:
    def setup_method(self):
        self.panels = compile_lib("red-metrics-row")

    def test_three_library_panels(self):
        assert len(self.panels) == 3

    def test_uids(self):
        uids = {p["uid"] for p in self.panels}
        assert uids == {"red-metrics-rate", "red-metrics-error-rate", "red-metrics-latency"}

    def test_kind_is_panel(self):
        for p in self.panels:
            assert p["kind"] == 1

    def test_panel_titles(self):
        titles = {p["name"] for p in self.panels}
        assert titles == {"Request Rate", "Error Rate", "Request Duration p99"}

    def test_models_are_timeseries(self):
        for p in self.panels:
            assert p["model"]["type"] == "timeseries"

    def test_models_use_service_variable(self):
        for p in self.panels:
            targets = p["model"]["targets"]
            assert any("$service" in t["expr"] for t in targets)

    def test_rate_panel_unit(self):
        rate = next(p for p in self.panels if p["uid"] == "red-metrics-rate")
        assert rate["model"]["fieldConfig"]["defaults"]["unit"] == "reqps"

    def test_error_rate_panel_unit(self):
        error = next(p for p in self.panels if p["uid"] == "red-metrics-error-rate")
        assert error["model"]["fieldConfig"]["defaults"]["unit"] == "percentunit"

    def test_latency_panel_unit(self):
        latency = next(p for p in self.panels if p["uid"] == "red-metrics-latency")
        assert latency["model"]["fieldConfig"]["defaults"]["unit"] == "s"

    def test_latency_has_traces_drilldown_link(self):
        latency = next(p for p in self.panels if p["uid"] == "red-metrics-latency")
        links = latency["model"]["fieldConfig"]["defaults"]["links"]
        assert any("/d/traces-drilldown" in link["url"] for link in links)

    def test_prometheus_datasource(self):
        for p in self.panels:
            assert p["model"]["datasource"]["type"] == "prometheus"


class TestTracesDrilldown:
    def setup_method(self):
        self.dash = compile_dashboard("traces-drilldown")

    def test_uid(self):
        assert self.dash["uid"] == "traces-drilldown"

    def test_title(self):
        assert self.dash["title"] == "Traces Drill-down"

    def test_tags(self):
        assert self.dash["tags"] == ["traces-drilldown", "grafonnet"]

    def test_refresh(self):
        assert self.dash["refresh"] == "30s"

    def test_panel_count(self):
        assert len(self.dash["panels"]) == 1

    def test_panel_type_table(self):
        assert self.dash["panels"][0]["type"] == "table"

    def test_panel_title(self):
        assert self.dash["panels"][0]["title"] == "Traces"

    def test_panel_full_width(self):
        assert self.dash["panels"][0]["gridPos"]["w"] == 24

    def test_panel_datasource_tempo(self):
        panel = self.dash["panels"][0]
        assert panel["datasource"]["type"] == "tempo"
        assert panel["datasource"]["uid"] == "tempo"

    def test_panel_query_uses_service_variable(self):
        target = self.dash["panels"][0]["targets"][0]
        assert "${service}" in target["query"]

    def test_panel_query_type_traceql(self):
        target = self.dash["panels"][0]["targets"][0]
        assert target.get("queryType") == "traceql"

    def test_service_variable(self):
        variables = self.dash["templating"]["list"]
        assert len(variables) == 1
        v = variables[0]
        assert v["name"] == "service"
        assert v["type"] == "query"
        assert "label_values(http_server_request_duration_seconds_count, service_name)" in v["query"]

    def test_service_variable_datasource(self):
        v = self.dash["templating"]["list"][0]
        assert v["datasource"]["type"] == "prometheus"

    def test_dashboard_links(self):
        urls = [link["url"] for link in self.dash["links"]]
        assert "/d/fleet-overview" in urls
        assert "/d/service-dashboard" in urls


class TestLogsDrilldown:
    def setup_method(self):
        self.dash = compile_dashboard("logs-drilldown")

    def test_uid(self):
        assert self.dash["uid"] == "logs-drilldown"

    def test_title(self):
        assert self.dash["title"] == "Logs Drill-down"

    def test_tags(self):
        assert self.dash["tags"] == ["logs-drilldown", "grafonnet"]

    def test_refresh(self):
        assert self.dash["refresh"] == "30s"

    def test_panel_count(self):
        assert len(self.dash["panels"]) == 1

    def test_panel_type_logs(self):
        assert self.dash["panels"][0]["type"] == "logs"

    def test_panel_title(self):
        assert self.dash["panels"][0]["title"] == "Logs"

    def test_panel_full_width(self):
        assert self.dash["panels"][0]["gridPos"]["w"] == 24

    def test_panel_datasource_loki(self):
        panel = self.dash["panels"][0]
        assert panel["datasource"]["type"] == "loki"
        assert panel["datasource"]["uid"] == "loki"

    def test_panel_query_uses_service_variable(self):
        target = self.dash["panels"][0]["targets"][0]
        assert "${service}" in target["expr"]

    def test_panel_query_logql_label(self):
        target = self.dash["panels"][0]["targets"][0]
        assert "service_name" in target["expr"]

    def test_service_variable(self):
        variables = self.dash["templating"]["list"]
        assert len(variables) == 1
        v = variables[0]
        assert v["name"] == "service"
        assert v["type"] == "query"
        assert "label_values(http_server_request_duration_seconds_count, service_name)" in v["query"]

    def test_service_variable_datasource(self):
        v = self.dash["templating"]["list"][0]
        assert v["datasource"]["type"] == "prometheus"

    def test_dashboard_links(self):
        urls = [link["url"] for link in self.dash["links"]]
        assert "/d/fleet-overview" in urls
        assert "/d/service-dashboard" in urls
