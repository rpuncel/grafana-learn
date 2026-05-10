"""Push compiled grafonnet resources to Grafana via the HTTP API.

Deploy order:
  1. Library panels from grafonnet/resources/lib/ (upsert via /api/library-elements)
  2. Dashboards from grafonnet/resources/*.json (POST to /api/dashboards/db)

Targets http://localhost:3000 (grafana-grafonnet container, anonymous admin auth).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import requests

GRAFANA_URL = "http://localhost:3000"
DASHBOARDS_ENDPOINT = f"{GRAFANA_URL}/api/dashboards/db"
LIBRARY_ELEMENTS_ENDPOINT = f"{GRAFANA_URL}/api/library-elements"
RESOURCES_DIR = Path(__file__).parent / "resources"
LIB_DIR = RESOURCES_DIR / "lib"


def upsert_library_panel(entry: dict) -> None:
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
    if not LIB_DIR.exists():
        return
    lib_files = sorted(LIB_DIR.glob("*.json"))
    if not lib_files:
        return
    print(f"Deploying library panels to {GRAFANA_URL}...")
    for path in lib_files:
        entries = json.loads(path.read_text())
        for entry in entries:
            upsert_library_panel(entry)


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
    deploy_library_panels()

    dashboards = sorted(RESOURCES_DIR.glob("*.json"))
    if not dashboards:
        print("No JSON files found in grafonnet/resources/", file=sys.stderr)
        sys.exit(1)

    print(f"Deploying {len(dashboards)} dashboard(s) to {GRAFANA_URL}...")
    for path in dashboards:
        deploy_dashboard(path)


if __name__ == "__main__":
    main()
