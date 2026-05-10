# Grafana Learning Lab

A hands-on exploration of Grafana 13 features — dashboard composition, data links, TraceQL drill-downs, and more — implemented across two parallel tracks against a simulated observability stack.

## What's here

The stack monitors six synthetic services (frontend, checkout, cart, payment, shipping, recommendation) that emit HTTP request metrics and traces via OpenTelemetry. The dashboards follow a three-level hierarchy:

- **Fleet Overview** — all services at a glance, with data links into the Service Dashboard
- **Service Dashboard** — RED metrics (rate, errors, duration) for a selected service, with a data link into the Traces Drill-down
- **Traces Drill-down** — TraceQL search results for the selected service

The same dashboard hierarchy is implemented independently in two tracks, enabling direct comparison of the toolchains.

## Prerequisites

| Tool | Version | Install |
|---|---|---|
| Docker + Docker Compose | latest | [docs.docker.com/get-docker](https://docs.docker.com/get-docker/) |
| Python | 3.11+ | [python.org/downloads](https://www.python.org/downloads/) |
| Poetry | latest | [python-poetry.org/docs](https://python-poetry.org/docs/) |
| jsonnet | latest | [github.com/google/go-jsonnet](https://github.com/google/go-jsonnet) |
| jb (Jsonnet Bundler) | latest | [github.com/jsonnet-bundler/jsonnet-bundler](https://github.com/jsonnet-bundler/jsonnet-bundler) |
| gh (GitHub CLI) | latest | [cli.github.com](https://cli.github.com/) |

## Quick start

```bash
# Start the observability stack and metric generators
docker-compose up -d

# Compile and deploy dashboards to both Grafana instances
make deploy
```

Grafana is available at:
- **http://localhost:3000** — Grafonnet track
- **http://localhost:3001** — Foundation SDK track

No login required (anonymous admin access).

## Tour

Once the stack is up and dashboards are deployed, open either Grafana instance and follow the stops below in order. Each stop demonstrates one or more features; the narrative is the same on both instances.

### 1. Fleet Overview

Open http://localhost:3000 (Grafonnet) or http://localhost:3001 (SDK).

The landing dashboard shows all six synthetic services at a glance. The stat panels at the top collapse each service's time-series error rate into a single current value using a **Reduce transformation** — scroll down to see the full request-rate and error-rate time series for all services.

At the top of the dashboard is a **dashboard link** labelled "Open Service Dashboard". Click it to jump to the Service Dashboard; Grafana passes the current time range automatically.

Scroll further down to find the **Node Graph panel**, which renders the service dependency topology as a connected graph.

### 2. Service Dashboard — RED metrics, template variable, library panels, annotations

The Service Dashboard is scoped to a single service selected by the **`$service` template variable** in the header. Use the dropdown to switch between the six services — all panels update instantly.

The three panels (Request Rate, Error Rate, Request Duration p99) are **library panels**: they are defined once in Grafana's library and referenced by UID on this dashboard (and any other dashboard that uses them). To observe propagation, open any panel's menu → *Edit library panel*, change the title, and save. The updated title appears everywhere the panel is referenced without touching the dashboard JSON.

Look for the thin blue vertical lines crossing the time series panels — those are **annotations** marking synthetic deployment events. Hover a marker to see its text. They are stored in Grafana's built-in annotation store, tagged `deployment`.

### 3. Traces Drill-down — data links

On the Service Dashboard, hover your cursor over a data point on the **Request Duration p99** panel. A tooltip appears; at the bottom is a **data link** labelled "Go to Traces". Click it.

The Traces Drill-down opens with `$service` and the selected time range pre-filled. The TraceQL query `{resource.service.name="<service>"}` runs automatically. Click any trace in the results to open the waterfall view and inspect individual spans.

### 4. Logs Drill-down — data links continued

Navigate back to the Service Dashboard (browser back button or the breadcrumb). Hover over a data point on the **Error Rate** panel — a "Go to Logs" **data link** appears in the tooltip. Click it.

The Logs Drill-down opens with a Loki query `{service_name="<service>"}` pre-filled from the panel's series labels. You can refine the query or explore log lines directly.

### 5. Correlations — signal connections in Explore

Open **Explore** from the left sidebar (compass icon). Select **Prometheus** as the datasource and run a query that preserves the `service_name` label, for example:

```
sum by (service_name)(rate(http_server_duration_milliseconds_count[5m]))
```

Switch the result view to **Table**. Each cell in the `service_name` column has a "Go to Logs" link next to it. This is a Grafana **Correlation** — a server-side connection between the Prometheus and Loki datasources that surfaces in Explore's table view. Click the link to open Loki Explore with `{service_name="<service>"}` pre-filled.

## The two tracks

### Grafonnet track (`grafonnet/`)

Dashboards are defined in Jsonnet using the [Grafonnet](https://github.com/grafana/grafonnet) library and compiled to JSON with `jsonnet`. Dependencies are managed with `jb` (Jsonnet Bundler).

```bash
# Run dashboard structure tests
poetry run pytest grafonnet/tests/

# Run integration tests (requires the stack to be up)
poetry run pytest tests/integration/

# Run both
poetry run pytest
```

### Foundation SDK track (`foundation-sdk/`)

Dashboards are defined in Python using the [Grafana Foundation SDK](https://github.com/grafana/grafana-foundation-sdk). Each dashboard is a Python module that builds and serialises a dashboard object.

```bash
# Run tests
poetry -C foundation-sdk run pytest

# Type-check
poetry -C foundation-sdk run pyright
```

`make deploy` handles both tracks: it compiles the Grafonnet dashboards from Jsonnet, then runs both deploy scripts in sequence.

## Backend stack

Both Grafana instances share the same backends:

| Service | Port | Purpose |
|---|---|---|
| Prometheus | 9090 | Metrics storage |
| Tempo | 3200 | Trace storage |
| Loki | 3100 | Log storage |
| OTel Collector | 4317/4318 | Telemetry ingestion |

## Further reading

- [`CONTEXT.md`](CONTEXT.md) — domain glossary (dashboard hierarchy, navigation features, track terminology)
- [`CLAUDE.md`](CLAUDE.md) — instructions for AI agents working in this repo
- [`docs/adr/`](docs/adr/) — architecture decision records
