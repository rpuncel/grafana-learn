"""Deploy a placeholder dashboard to the Foundation SDK Grafana instance.

Targets http://localhost:3001 (grafana-sdk container, anonymous admin auth).
"""

from __future__ import annotations

import json
import sys
from typing import Any

import requests


GRAFANA_URL = "http://localhost:3001"
DASHBOARDS_ENDPOINT = f"{GRAFANA_URL}/api/dashboards/db"


def build_placeholder_dashboard() -> dict[str, Any]:
    """Return a minimal Grafana dashboard definition."""
    return {
        "id": None,
        "uid": "sdk-placeholder",
        "title": "Placeholder — Foundation SDK Track",
        "description": (
            "Scaffold placeholder confirming the Foundation SDK toolchain "
            "is wired up correctly. Feature dashboards are implemented in "
            "subsequent issues."
        ),
        "tags": ["placeholder", "sdk"],
        "timezone": "browser",
        "refresh": "30s",
        "schemaVersion": 39,
        "panels": [
            {
                "id": 1,
                "type": "text",
                "title": "Welcome",
                "gridPos": {"x": 0, "y": 0, "w": 24, "h": 8},
                "options": {
                    "mode": "markdown",
                    "content": (
                        "## Foundation SDK Track — Placeholder\n\n"
                        "This dashboard is a scaffold confirming that the "
                        "Grafana Foundation SDK toolchain is wired up correctly.\n\n"
                        "Feature dashboards (Fleet Overview, Service Dashboard, "
                        "Drill-downs) are implemented in subsequent issues."
                    ),
                },
            }
        ],
    }


def deploy_dashboard(dashboard: dict[str, Any]) -> None:
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
        data=json.dumps(payload),
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
    dashboard = build_placeholder_dashboard()
    deploy_dashboard(dashboard)


if __name__ == "__main__":
    main()
