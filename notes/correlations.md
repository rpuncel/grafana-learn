# Correlations

Grafana **Correlations** create server-side connections between datasources. When a user clicks a data point in a panel, Grafana inspects which correlations are configured for that panel's datasource and surfaces "Go to ..." navigation links. This is distinct from data links (which are embedded in dashboard JSON) and dashboard links (which are panel-level navigation tabs).

## What was implemented (Issue #11)

A single correlation links the **Prometheus** datasource (used by the error rate panel) to the **Loki** datasource (used by the Logs Drill-down):

| Field | Value |
|-------|-------|
| Label | `Go to Logs` |
| Source datasource UID | `prometheus` |
| Target datasource UID | `loki` |
| Config type | `query` |
| Field | `service_name` |
| Target query | `{service_name="${service_name}"}` |

The `field` setting tells Grafana which label from the clicked Prometheus series to extract. The `${service_name}` variable in the target Loki expression is then substituted with that extracted value.

## API endpoints (Grafana 13)

| Operation | Endpoint |
|-----------|----------|
| List | `GET /api/datasources/uid/{sourceUID}/correlations` |
| Create | `POST /api/datasources/uid/{sourceUID}/correlations` |
| Update | `PATCH /api/datasources/uid/{sourceUID}/correlations/{correlationUID}` |
| Delete | `DELETE /api/datasources/uid/{sourceUID}/correlations/{correlationUID}` |

## Provisioning

Correlations are provisioned via the HTTP API as part of `make deploy`. The upsert logic mirrors the library-panel pattern: GET the list, match by label, POST to create or PATCH to update.

- Grafonnet track: `grafonnet/deploy.py` → targets `http://localhost:3000`
- SDK track: `foundation-sdk/src/graflearn/tools/deploy.py` → targets `http://localhost:3001`

Both instances share the same datasource UIDs, so the correlation config is identical across both.
