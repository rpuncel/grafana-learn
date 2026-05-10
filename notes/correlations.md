# Correlations

Grafana **Correlations** create server-side connections between datasources. They are an **Explore-first feature**: correlation links surface in Explore's table view (next to field values), not in regular dashboard panel tooltips. For the dashboard click-to-navigate experience, use a **data link** instead (embedded in panel JSON). Both mechanisms are complementary.

This is distinct from:
- **Data links** — embedded in dashboard/panel JSON, appear in the panel tooltip on click
- **Dashboard links** — panel-level navigation tabs linking to other dashboards

## What was implemented (Issue #11)

### Correlation (Explore)

A datasource-level correlation links **Prometheus** → **Loki**:

| Field | Value |
|-------|-------|
| Label | `Go to Logs` |
| Source datasource UID | `prometheus` |
| Target datasource UID | `loki` |
| Type | `query` |
| Field | `service_name` |
| Target query | `{service_name="${service_name}"}` |

The `field` setting tells Grafana which label from the clicked series to extract. The `${service_name}` variable in the Loki expression is substituted with that extracted value.

To find it: open **Explore** → select **Prometheus** → run a query (or open the Error Rate panel via its menu → Explore) → switch results to **Table view** → the "Go to Logs" link appears on cells with a `service_name` value.

### Data link (Dashboard)

A panel-level data link on the Error Rate library panel (`red-metrics-error-rate`) provides the same navigation directly from the Service Dashboard:

- **Title**: Go to Logs
- **URL**: `/d/logs-drilldown?var-service=${__field.labels.service_name}&${__url_time_range}`

Click any data point on the Error Rate panel → "Go to Logs" link appears in the tooltip.

### Query change required

Both mechanisms require `service_name` to be present as a field in the Prometheus data frame. `sum()` without grouping strips all labels (`metric: {}`). All three RED metrics queries were updated to use `sum by (service_name)(...)` (and `sum by (le, service_name)(...)` for the histogram) to preserve the label.

## API endpoints (Grafana 13)

| Operation | Endpoint |
|-----------|----------|
| List | `GET /api/datasources/uid/{sourceUID}/correlations` |
| Create | `POST /api/datasources/uid/{sourceUID}/correlations` |
| Update | `PATCH /api/datasources/uid/{sourceUID}/correlations/{correlationUID}` |
| Delete | `DELETE /api/datasources/uid/{sourceUID}/correlations/{correlationUID}` |

**Gotcha**: `type` is a top-level field in the request body, not nested inside `config`. Putting it inside `config` returns `400 bad request data` with no further detail.

```json
{
  "label": "Go to Logs",
  "description": "View logs for this service",
  "targetUID": "loki",
  "type": "query",
  "config": {
    "field": "service_name",
    "target": { "expr": "{service_name=\"${service_name}\"}" }
  }
}
```

## Provisioning

Correlations are provisioned via the HTTP API as part of `make deploy`. The upsert logic mirrors the library-panel pattern: GET the list, match by label, POST to create or PATCH to update.

- Grafonnet track: `grafonnet/deploy.py` → targets `http://localhost:3000`
- SDK track: `foundation-sdk/src/graflearn/tools/deploy.py` → targets `http://localhost:3001`

Both instances share the same datasource UIDs, so the correlation config is identical across both.
