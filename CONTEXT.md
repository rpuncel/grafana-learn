# Grafana Learning Lab

A learning repository for exploring advanced Grafana 13 features through two parallel implementation tracks, both monitoring the OpenTelemetry Demo distributed system.

## Language

### Dashboard Hierarchy

**Fleet Overview**:
A single dashboard showing the health of all services at a glance, with SLI summary and system-wide traffic, error rate, and latency.
_Avoid_: Home dashboard, top-level dashboard, main dashboard

**Service Dashboard**:
A dashboard scoped to a single service, selected via the `$service` template variable, showing RED metrics for that service.
_Avoid_: Per-service dashboard, service view

**Drill-down**:
A signal-specific detail dashboard (Traces, Logs, or Infrastructure) reached from a Service Dashboard via a data link or dashboard link.
_Avoid_: Detail dashboard, deep-dive

**RED metrics**:
The three standard service-level indicators: Request rate, Error rate, and Duration (latency).
_Avoid_: Golden signals (which also includes saturation)

### Navigation Features

**Dashboard link**:
A link from one dashboard to another, optionally passing template variable values as URL parameters.
_Avoid_: Cross-dashboard link, inter-dashboard link

**Data link**:
A link embedded in a panel's data points, activated by clicking a specific value (e.g., a latency spike), typically used to open a related Trace or Log query.
_Avoid_: Panel link, drill-through link

**Library panel**:
A panel definition stored in Grafana's database by UID, referenced across multiple dashboards so changes propagate everywhere.
_Avoid_: Shared panel, reusable panel, template panel

**Template variable**:
A dashboard-scoped variable (e.g., `$service`) that filters panel queries and is passed between dashboards via dashboard links.
_Avoid_: Dashboard variable, filter variable

**Correlation**:
A Grafana-native connection between two signals (e.g., metrics → traces) that surfaces as a clickable link within a panel, without leaving Grafana.
_Avoid_: Signal correlation, cross-signal link

**Annotation**:
A time-stamped marker overlaid on time series panels, used to mark external events such as deployments.
_Avoid_: Event marker, deployment marker

### Learning Tracks

**Grafonnet track**:
The implementation track that uses Grafonnet (Jsonnet library) and Grizzly to define and deploy dashboards. Toolchain: `jb`, `go-jsonnet`, `grr`.
_Avoid_: Jsonnet track

**SDK track**:
The implementation track that uses the Grafana Foundation SDK (Python) and Poetry to define and deploy dashboards.
_Avoid_: Python track, Foundation track

## Relationships

- A **Fleet Overview** links to one or more **Service Dashboards** via **dashboard links**, passing `$service`
- A **Service Dashboard** links to one or more **Drill-downs** via **data links**
- A **Library panel** is defined once and referenced by UID across multiple **Service Dashboards**
- The **Grafonnet track** and **SDK track** implement the same dashboard hierarchy independently, enabling direct comparison
- Both tracks deploy to separate Grafana instances that share the same Prometheus, Loki, and Tempo backend

## Example dialogue

> **Dev:** "The Fleet Overview is too noisy — can we move the latency histogram to the Service Dashboard?"
> **Reviewer:** "Sure, but that's a Library panel — update the definition once and it'll propagate to all Service Dashboards automatically."

> **Dev:** "How does a user get from the Fleet Overview to a specific service's traces?"
> **Reviewer:** "They click the error rate spike — that's a data link that opens the Traces Drill-down with the service and time range pre-filled."
