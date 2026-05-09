"""Push compiled grafonnet dashboard JSON to Grafana via the HTTP API.

Reads all *.json files from grafonnet/resources/ and POSTs them to
http://localhost:3000 (grafana-grafonnet container, anonymous admin auth).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import requests

GRAFANA_URL = "http://localhost:3000"
DASHBOARDS_ENDPOINT = f"{GRAFANA_URL}/api/dashboards/db"
RESOURCES_DIR = Path(__file__).parent / "resources"


def deploy_dashboard(path: Path) -> None:
    dashboard = json.loads(path.read_text())
    payload = {"dashboard": dashboard, "overwrite": True, "folderId": 0}

    response = requests.post(
        DASHBOARDS_ENDPOINT,
        headers={"Content-Type": "application/json"},
        data=json.dumps(payload),
        timeout=10,
    )

    if response.status_code == 200:
        result = response.json()
        print(f"  {path.name}: uid={result.get('uid')}, url={result.get('url')}")
    else:
        print(f"  ERROR {path.name}: HTTP {response.status_code}", file=sys.stderr)
        print(f"  {response.text}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    dashboards = sorted(RESOURCES_DIR.glob("*.json"))
    if not dashboards:
        print("No JSON files found in grafonnet/resources/", file=sys.stderr)
        sys.exit(1)

    print(f"Deploying {len(dashboards)} dashboard(s) to {GRAFANA_URL}...")
    for path in dashboards:
        deploy_dashboard(path)


if __name__ == "__main__":
    main()
