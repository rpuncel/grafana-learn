"""Deploy all dashboards to the Foundation SDK Grafana instance.

Targets http://localhost:3001 (grafana-sdk container, anonymous admin auth).
"""

from __future__ import annotations

import json
import sys
from typing import Any

import requests
from grafana_foundation_sdk.builders.dashboard import Dashboard
from grafana_foundation_sdk.builders.text import Panel as TextPanel
from grafana_foundation_sdk.cog.encoder import JSONEncoder
from grafana_foundation_sdk.models.dashboard import GridPos
from grafana_foundation_sdk.models.text import TextMode

from graflearn.dashboards.fleet_overview import build_fleet_overview_dashboard
from graflearn.dashboards.service_dashboard import build_service_dashboard
from graflearn.dashboards.logs_drilldown import build_logs_drilldown_dashboard
from graflearn.dashboards.traces_drilldown import build_traces_drilldown_dashboard


GRAFANA_URL = "http://localhost:3001"
DASHBOARDS_ENDPOINT = f"{GRAFANA_URL}/api/dashboards/db"

_PANEL_CONTENT = (
    "## Foundation SDK Track — Placeholder\n\n"
    "This dashboard is a scaffold confirming that the "
    "Grafana Foundation SDK toolchain is wired up correctly.\n\n"
    "Feature dashboards (Fleet Overview, Service Dashboard, "
    "Drill-downs) are implemented in subsequent issues."
)


def build_placeholder_dashboard() -> Any:
    """Return a Grafana dashboard object built with the Foundation SDK."""
    panel = (
        TextPanel()
        .title("Welcome")
        .description("Placeholder panel")
        .mode(TextMode.MARKDOWN)
        .content(_PANEL_CONTENT)
        .grid_pos(GridPos(h=8, w=24, x=0, y=0))
    )

    return (
        Dashboard("Placeholder — Foundation SDK Track")
        .uid("sdk-placeholder")
        .description(
            "Scaffold placeholder confirming the Foundation SDK toolchain "
            "is wired up correctly. Feature dashboards are implemented in "
            "subsequent issues."
        )
        .tags(["placeholder", "sdk"])
        .timezone("browser")
        .refresh("30s")
        .with_panel(panel)
        .build()
    )


def deploy_dashboard(dashboard: Any) -> None:
    """POST a dashboard payload to the Grafana HTTP API."""
    payload: dict[str, Any] = {
        "dashboard": dashboard,
        "folderId": 0,
        "overwrite": True,
        "message": "Deployed by foundation-sdk/deploy.py",
    }

    response = requests.post(
        DASHBOARDS_ENDPOINT,
        headers={"Content-Type": "application/json"},
        data=json.dumps(payload, cls=JSONEncoder),
        timeout=10,
    )

    if response.status_code == 200:
        result = response.json()
        print(f"Dashboard deployed: uid={result.get('uid')}, url={result.get('url')}")
    else:
        print(
            f"ERROR: POST {DASHBOARDS_ENDPOINT} returned HTTP {response.status_code}",
            file=sys.stderr,
        )
        print(response.text, file=sys.stderr)
        sys.exit(1)


def main() -> None:
    for dashboard in [
        build_placeholder_dashboard(),
        build_fleet_overview_dashboard(),
        build_service_dashboard(),
        build_traces_drilldown_dashboard(),
        build_logs_drilldown_dashboard(),
    ]:
        deploy_dashboard(dashboard)


if __name__ == "__main__":
    main()
