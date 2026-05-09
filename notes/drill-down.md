# Drill-down

## Traces Drill-down (issue #5)

### What was built

- `grafonnet/dashboards/traces-drilldown.jsonnet` and `foundation-sdk/src/graflearn/dashboards/traces_drilldown.py` — new dashboard querying Tempo via TraceQL (`{resource.service.name="${service}"}`) with a `$service` variable populated from Prometheus label values.
- A data link on the Service Dashboard's latency panel (`Request Duration p99`) that opens the Traces Drill-down with `var-service=${service}&${__url_time_range}` pre-filled.
- Grafana's `traces` panel type has no builder in either Grafonnet or the Foundation SDK. Grafonnet uses a raw Jsonnet object; the SDK uses a thin `_TracesPanel` builder wrapping `dashboard.Panel(type_val="traces")` directly.

### Clicking data links in time series panels

Data links on a time series panel do **not** trigger on a panel click. They appear inside the hover tooltip when the cursor is over a specific data point. Look for the link at the bottom of the tooltip.

### Infrastructure issues found and fixed

**Metric generators weren't emitting traces.** The generators only sent OTel metrics (histograms). Extended `metric-generator/main.py` to also create one HTTP server span per iteration using `TracerProvider` + `OTLPSpanExporter`. Spans are backdated so their duration matches the sampled request duration, keeping metric and trace data correlated. No new packages were needed — `opentelemetry-exporter-otlp-proto-grpc` already includes the span exporter.

**Tempo was crash-looping.** `grafana/tempo:latest` pulled v3.0.0-rc.1, which removed `ingester`, `compactor`, and `metrics_generator.traces_storage` from the config schema. Tempo had never successfully started — it silently crash-looped while Prometheus metrics continued to work (they route through the OTel Collector's Prometheus exporter, bypassing Tempo entirely). Fixed by pinning `compose.yaml` to `grafana/tempo:2.6.1`.

**After pinning, the data volume had wrong permissions.** The v3 RC container had initialized `/tmp/tempo` with a different uid. Cleared the `grafana_tempo-data` Docker volume (`docker volume rm grafana_tempo-data`) and restarted. No trace data was lost since Tempo had never ingested any.

**The OTel Collector had cached the old Tempo IP.** After Tempo restarted with a new container IP, the collector's gRPC channel kept dialing the stale IP. Restarted the collector (`docker-compose restart otelcol`) to force a fresh DNS lookup.
