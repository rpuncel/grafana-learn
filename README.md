# Grafana Learning Lab

A hands-on exploration of Grafana 13 features — dashboard composition, data links, TraceQL drill-downs, and more — implemented across two parallel tracks against a simulated observability stack.

## What's here

The stack monitors six synthetic services (frontend, checkout, cart, payment, shipping, recommendation) that emit HTTP request metrics and traces via OpenTelemetry. The dashboards follow a three-level hierarchy:

- **Fleet Overview** — all services at a glance, with data links into the Service Dashboard
- **Service Dashboard** — RED metrics (rate, errors, duration) for a selected service, with a data link into the Traces Drill-down
- **Traces Drill-down** — TraceQL search results for the selected service

The same dashboard hierarchy is implemented independently in two tracks, enabling direct comparison of the toolchains.

## Quick start

**Requirements:** Docker, Docker Compose, Python 3.11+, Poetry, jsonnet, jb

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
