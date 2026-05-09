# Two Grafana instances sharing one observability backend

The repo has two parallel learning tracks (Grafonnet and SDK) that each deploy dashboards independently. Rather than sharing one Grafana instance with folder-based separation, we run two separate Grafana services in Docker Compose — one per track — both pointing to the same Prometheus, Loki, and Tempo backend. This keeps the deployment toolchains (`grr` vs Python API) completely isolated: no ambiguity about which tool created a given dashboard. Grafana itself is lightweight, so the overhead of a second instance is negligible compared to the clarity gained.

## Considered Options

- **One Grafana, two folders** — simpler Docker Compose, but both toolchains target the same instance, which blurs the comparison and risks accidental interference between tracks.
- **Two Grafana instances** — chosen. Minimal extra overhead, clean separation of concerns, and each instance can be configured independently if needed for future experiments.
