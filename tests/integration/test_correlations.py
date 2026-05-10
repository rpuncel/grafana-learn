"""Integration tests: Grafana Correlations provisioning."""
import requests


def test_logs_correlation_exists(grafana_url):
    """Verify prometheus→loki 'Go to Logs' correlation is provisioned."""
    resp = requests.get(
        f"{grafana_url}/api/datasources/uid/prometheus/correlations",
        timeout=10,
    )
    resp.raise_for_status()
    body = resp.json()
    existing_list = body.get("correlations", body) if isinstance(body, dict) else body

    match = next((c for c in existing_list if c.get("label") == "Go to Logs"), None)
    assert match is not None, "Expected 'Go to Logs' correlation not found on prometheus datasource"
    assert match["targetUID"] == "loki"
    assert match["type"] == "query"
