"""Deploy all resources to the Foundation SDK Grafana instance.

Deploy order:
  1. Library panels (upsert via /api/library-elements)
  2. Dashboards (POST to /api/dashboards/db)

Targets http://localhost:3001 (grafana-sdk container, anonymous admin auth).
"""

from __future__ import annotations

import json
import sys
import time
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
from graflearn.lib.red_metrics_row import LIBRARY_PANELS


GRAFANA_URL = "http://localhost:3001"
ANNOTATIONS_ENDPOINT = f"{GRAFANA_URL}/api/annotations"
DASHBOARDS_ENDPOINT = f"{GRAFANA_URL}/api/dashboards/db"
LIBRARY_ELEMENTS_ENDPOINT = f"{GRAFANA_URL}/api/library-elements"

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


def upsert_library_panel(entry: dict[str, Any]) -> None:
    uid = entry["uid"]
    payload = {
        "uid": uid,
        "name": entry["name"],
        "kind": entry["kind"],
        "model": entry["model"],
    }

    response = requests.post(
        LIBRARY_ELEMENTS_ENDPOINT,
        headers={"Content-Type": "application/json"},
        data=json.dumps(payload),
        timeout=10,
    )

    if response.status_code == 200:
        print(f"  created library panel: uid={uid}")
        return

    if response.status_code == 400 and "already exists" in response.text.lower():
        get_resp = requests.get(f"{LIBRARY_ELEMENTS_ENDPOINT}/{uid}", timeout=10)
        get_resp.raise_for_status()
        version = get_resp.json()["result"]["version"]
        patch_payload = {**payload, "version": version}
        patch_resp = requests.patch(
            f"{LIBRARY_ELEMENTS_ENDPOINT}/{uid}",
            headers={"Content-Type": "application/json"},
            data=json.dumps(patch_payload),
            timeout=10,
        )
        patch_resp.raise_for_status()
        print(f"  updated library panel: uid={uid}")
        return

    print(
        f"  ERROR: POST {LIBRARY_ELEMENTS_ENDPOINT} returned HTTP {response.status_code}",
        file=sys.stderr,
    )
    print(response.text, file=sys.stderr)
    sys.exit(1)


def deploy_library_panels() -> None:
    print(f"Deploying library panels to {GRAFANA_URL}...")
    for entry in LIBRARY_PANELS:
        upsert_library_panel(entry)


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


def seed_deployment_annotation() -> None:
    """Create a sample deployment annotation if none exists yet."""
    resp = requests.get(ANNOTATIONS_ENDPOINT, params={"tags": "deployment", "limit": 1}, timeout=10)
    resp.raise_for_status()
    if resp.json():
        print("  sample deployment annotation already exists, skipping")
        return
    epoch_ms = int((time.time() - 1800) * 1000)  # 30 min ago — visible in default 1h range
    payload = {"tags": ["deployment"], "text": "v1.0.0 — sample deployment (seeded by deploy script)", "time": epoch_ms}
    resp = requests.post(ANNOTATIONS_ENDPOINT, headers={"Content-Type": "application/json"}, data=json.dumps(payload), timeout=10)
    resp.raise_for_status()
    print("  seeded sample deployment annotation at t-30m")


def main() -> None:
    deploy_library_panels()

    for dashboard in [
        build_placeholder_dashboard(),
        build_fleet_overview_dashboard(),
        build_service_dashboard(),
        build_traces_drilldown_dashboard(),
        build_logs_drilldown_dashboard(),
    ]:
        deploy_dashboard(dashboard)

    print(f"Seeding sample annotations to {GRAFANA_URL}...")
    seed_deployment_annotation()


if __name__ == "__main__":
    main()
