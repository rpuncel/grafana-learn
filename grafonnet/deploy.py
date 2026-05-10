"""Push compiled grafonnet resources to Grafana via the HTTP API.

Deploy order:
  1. Library panels from grafonnet/resources/lib/ (upsert via /api/library-elements)
  2. Dashboards from grafonnet/resources/*.json (POST to /api/dashboards/db)

Targets http://localhost:3000 (grafana-grafonnet container, anonymous admin auth).
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import requests

GRAFANA_URL = "http://localhost:3000"
ANNOTATIONS_ENDPOINT = f"{GRAFANA_URL}/api/annotations"
CORRELATIONS_ENDPOINT = f"{GRAFANA_URL}/api/datasources/uid/prometheus/correlations"
DASHBOARDS_ENDPOINT = f"{GRAFANA_URL}/api/dashboards/db"
LIBRARY_ELEMENTS_ENDPOINT = f"{GRAFANA_URL}/api/library-elements"
RESOURCES_DIR = Path(__file__).parent / "resources"
LIB_DIR = RESOURCES_DIR / "lib"

LOGS_CORRELATION = {
    "label": "Go to Logs",
    "description": "View logs for this service",
    "targetUID": "loki",
    "type": "query",
    "config": {
        "field": "service_name",
        "target": {"expr": '{service_name="${service_name}"}'},
    },
}


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


def deploy_correlations() -> None:
    print(f"Deploying correlations to {GRAFANA_URL}...")
    resp = requests.get(CORRELATIONS_ENDPOINT, timeout=10)
    resp.raise_for_status()
    body = resp.json()
    existing_list = body.get("correlations", body) if isinstance(body, dict) else body
    existing = next((c for c in existing_list if c.get("label") == LOGS_CORRELATION["label"]), None)

    if existing is None:
        r = requests.post(
            CORRELATIONS_ENDPOINT,
            headers={"Content-Type": "application/json"},
            data=json.dumps(LOGS_CORRELATION),
            timeout=10,
        )
        r.raise_for_status()
        print("  created correlation: Go to Logs (prometheus → loki)")
    else:
        uid = existing["uid"]
        r = requests.patch(
            f"{CORRELATIONS_ENDPOINT}/{uid}",
            headers={"Content-Type": "application/json"},
            data=json.dumps(LOGS_CORRELATION),
            timeout=10,
        )
        r.raise_for_status()
        print("  updated correlation: Go to Logs (prometheus → loki)")


def main() -> None:
    deploy_library_panels()

    dashboards = sorted(RESOURCES_DIR.glob("*.json"))
    if not dashboards:
        print("No JSON files found in grafonnet/resources/", file=sys.stderr)
        sys.exit(1)

    print(f"Deploying {len(dashboards)} dashboard(s) to {GRAFANA_URL}...")
    for path in dashboards:
        deploy_dashboard(path)

    print(f"Seeding sample annotations to {GRAFANA_URL}...")
    seed_deployment_annotation()

    deploy_correlations()


if __name__ == "__main__":
    main()
