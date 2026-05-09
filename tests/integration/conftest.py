import pytest
import requests


@pytest.fixture(
    params=[
        pytest.param("http://localhost:3000", id="grafonnet"),
        pytest.param("http://localhost:3001", id="sdk"),
    ],
    scope="module",
)
def grafana_url(request):
    url = request.param
    try:
        requests.get(f"{url}/api/health", timeout=3).raise_for_status()
    except Exception:
        pytest.skip(f"Grafana not reachable at {url}")
    return url
