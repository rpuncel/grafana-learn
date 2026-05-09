import json
import subprocess
from pathlib import Path

GRAFONNET_DIR = Path(__file__).parent.parent
VENDOR_DIR = GRAFONNET_DIR / "vendor"
DASHBOARDS_DIR = GRAFONNET_DIR / "dashboards"


def compile_dashboard(name: str) -> dict:
    result = subprocess.run(
        ["jsonnet", "-J", str(VENDOR_DIR), str(DASHBOARDS_DIR / f"{name}.jsonnet")],
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
        assert len(self.dash["panels"]) == 2

    def test_panel_titles(self):
        titles = [p["title"] for p in self.dash["panels"]]
        assert "Request Rate by Service" in titles
        assert "Error Rate by Service" in titles

    def test_panels_full_width(self):
        for panel in self.dash["panels"]:
            assert panel["gridPos"]["w"] == 24

    def test_panel_data_links(self):
        expected_url = "/d/service-dashboard?var-service=${__field.labels.service_name}"
        for panel in self.dash["panels"]:
            links = panel["fieldConfig"]["defaults"]["links"]
            assert any(link["url"] == expected_url for link in links)

    def test_dashboard_link_to_service_dashboard(self):
        urls = [link["url"] for link in self.dash["links"]]
        assert "/d/service-dashboard" in urls

    def test_prometheus_datasource(self):
        for panel in self.dash["panels"]:
            assert panel["datasource"]["type"] == "prometheus"


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

    def test_panel_titles(self):
        titles = [p["title"] for p in self.dash["panels"]]
        assert "Request Rate" in titles
        assert "Error Rate" in titles
        assert "Request Duration p99" in titles

    def test_latency_panel_full_width(self):
        latency = next(p for p in self.dash["panels"] if p["title"] == "Request Duration p99")
        assert latency["gridPos"]["w"] == 24

    def test_rate_panels_half_width(self):
        half_width = [p for p in self.dash["panels"] if p["gridPos"]["w"] == 12]
        titles = {p["title"] for p in half_width}
        assert titles == {"Request Rate", "Error Rate"}

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

    def test_queries_use_service_variable(self):
        for panel in self.dash["panels"]:
            for target in panel["targets"]:
                assert "$service" in target["expr"]

    def test_dashboard_link_to_fleet_overview(self):
        urls = [link["url"] for link in self.dash["links"]]
        assert "/d/fleet-overview" in urls

    def test_prometheus_datasource(self):
        for panel in self.dash["panels"]:
            assert panel["datasource"]["type"] == "prometheus"
