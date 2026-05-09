import pytest
import requests

GRAFANA_URL = "http://localhost:3000"


@pytest.fixture(scope="session", autouse=True)
def grafana_live():
    try:
        requests.get(f"{GRAFANA_URL}/api/health", timeout=3).raise_for_status()
    except Exception:
        pytest.skip("Grafana not reachable at localhost:3000")
