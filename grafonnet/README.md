# Grafonnet Track

Define Grafana dashboards as code using Jsonnet and deploy them with gcx (Grafana CLI).

## Deploy workflow

1. Compile each `.jsonnet` file in `dashboards/` to JSON in `resources/` (build artifact, not committed)
2. Validate with `gcx resources validate -p resources/`
3. Push to Grafana with `gcx resources push -p resources/`

Run `make deploy-grafonnet` to execute all three steps. gcx reads connection settings from
`GRAFANA_SERVER` and `GRAFANA_TOKEN` environment variables, or from a `gcx login` context.

## Feature parity

| Feature | Status |
|---|---|
| Fleet Overview | planned |
| Service Dashboard with `$service` | planned |
| Dashboard links with variable passing | planned |
| Data links (metrics → traces) | planned |
| Library panels | planned |
| Traces Drill-down (Tempo) | planned |
| Logs Drill-down (Loki) | planned |
| Annotations | planned |
| Correlations | planned |
| Transformations | planned |
| Node Graph panel | planned |

## Parity gaps

> *Gaps relative to the foundation-sdk track will be recorded here during implementation.*
