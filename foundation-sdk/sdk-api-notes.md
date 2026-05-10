# Foundation SDK API Notes

SDK version: `grafana_foundation_sdk 1769699998!10.1.0`

## Key imports

```python
from grafana_foundation_sdk.builders.dashboard import Dashboard, QueryVariable, DashboardLink
from grafana_foundation_sdk.builders.timeseries import Panel as TimeseriesPanel
from grafana_foundation_sdk.builders.prometheus import Dataquery as PrometheusQuery
from grafana_foundation_sdk.models.dashboard import (
    DataSourceRef, VariableRefresh, DashboardLinkType, GridPos
)
from grafana_foundation_sdk.cog.encoder import JSONEncoder
```

## TimeseriesPanel builder

```python
TimeseriesPanel()
  .title(title: str)
  .description(description: str)
  .datasource(datasource: DataSourceRef)            # DataSourceRef(type_val='prometheus', uid='prometheus')
  .with_target(target: Builder[...])                # add a Prometheus query
  .unit(unit: str)                                  # e.g. 'reqps', 'percentunit', 's'
  .grid_pos(grid_pos: GridPos)                      # GridPos(h=8, w=24, x=0, y=0)
  .data_links(links: list[Builder[DashboardLink]])  # panel-level data links
  .links(links: list[Builder[DashboardLink]])       # alias — same as data_links
```

## DashboardLink builder (panel-level AND dashboard-level)

```python
DashboardLink('My Title')
  .url(url: str)
  .type(type_val: DashboardLinkType)   # DashboardLinkType.LINK or DashboardLinkType.DASHBOARDS
  .keep_time(keep_time: bool)
  .include_vars(include_vars: bool)
  .target_blank(target_blank: bool)
  .as_dropdown(as_dropdown: bool)
  .tooltip(tooltip: str)
  .icon(icon: str)
  .tags(tags: list[str])
```

## QueryVariable builder

```python
QueryVariable('service')
  .label(label: str)                      # display label
  .datasource(datasource: DataSourceRef)
  .query(query: str)                      # e.g. 'label_values(metric, label)'
  .refresh(refresh: VariableRefresh)      # VariableRefresh.ON_TIME_RANGE_CHANGED = 2
  .include_all(include_all: bool)
  .multi(multi: bool)
  .sort(sort: VariableSort)
```

## VariableRefresh enum

| Name                   | Value |
|------------------------|-------|
| NEVER                  | 0     |
| ON_DASHBOARD_LOAD      | 1     |
| ON_TIME_RANGE_CHANGED  | 2     |

## DashboardLinkType enum

| Name       | Value         |
|------------|---------------|
| LINK       | `'link'`      |
| DASHBOARDS | `'dashboards'`|

## DataSourceRef

```python
DataSourceRef(type_val='prometheus', uid='prometheus')
```

## NodeGraphPanel builder

```python
from grafana_foundation_sdk.builders.nodegraph import Panel as NodeGraphPanel
from grafana_foundation_sdk.builders.tempo import TempoQuery

NodeGraphPanel()
  .title(title: str)
  .datasource(datasource: DataSourceRef)
  .with_target(target: Builder[...])   # TempoQuery().query_type("serviceMap").query("").ref_id("A")
  .grid_pos(grid_pos: GridPos)
```

Service map query (Tempo service graph → Node Graph panel):
```python
TempoQuery()
  .datasource(DataSourceRef(type_val="tempo", uid="tempo"))
  .query_type("serviceMap")   # returns nodes+edges for Node Graph panel
  .query("")
  .ref_id("A")
```

## Dashboard builder

```python
Dashboard('Title')
  .uid(uid: str)
  .description(description: str)
  .tags(tags: list[str])
  .timezone(timezone: str)
  .refresh(refresh: str)
  .with_variable(variable: Builder[VariableModel])
  .variables(variables: list[Builder[VariableModel]])
  .annotation(annotation: Builder[AnnotationQuery])    # add one annotation
  .annotations(annotations: list[Builder[AnnotationQuery]])  # set all annotations
  .with_panel(panel: Builder[Panel])
  .link(link: Builder[DashboardLink])       # singular — add one link
  .links(links: list[Builder[DashboardLink]])  # plural — set all links at once
  .build()
```

## Transformations

Transformations reshape panel data before rendering. Use `.with_transformation()` or `.transformations()` on any panel builder.

```python
from grafana_foundation_sdk.builders.stat import Panel as StatPanel
from grafana_foundation_sdk.models.dashboard import DataTransformerConfig

from grafana_foundation_sdk.builders.table import Panel as TablePanel

# Use mode "seriesToRows" for Prometheus output (one frame per series).
# Use mode "reduceFields" only for wide-format frames (multiple value columns in one frame).
TablePanel()
    .with_transformation(
        DataTransformerConfig(
            id_val="reduce",
            options={"reducers": ["lastNotNull"], "mode": "seriesToRows"},  # lastNotNull skips NaN edge values from rate()
        )
    )
```

`DataTransformerConfig` fields:
- `id_val` (str, required) — transformer ID (e.g. `"reduce"`, `"renameByRegex"`, `"joinByField"`)
- `options` (dict, required) — transformer-specific config
- `disabled` (bool, optional) — skip this transformation if True

Common transformation IDs:
- `reduce` — collapse time series to a single value; `options: {"reducers": ["last"], "mode": "reduceFields"}`
- `renameByRegex` — rename fields by regex; `options: {"regex": "(.*)", "renamePattern": "$1"}`
- `joinByField` — join multiple queries by a shared field

Panel builder methods:
- `.with_transformation(DataTransformerConfig)` — append one transformation
- `.transformations(list[DataTransformerConfig])` — set all transformations at once

## AnnotationQuery builder

```python
from grafana_foundation_sdk.builders.dashboard import AnnotationQuery, AnnotationTarget

# Deployment event annotation using Grafana native store (queries by tag)
AnnotationQuery()
  .name(name: str)
  .datasource(datasource: DataSourceRef)   # DataSourceRef(type_val="grafana", uid="-- Grafana --")
  .icon_color(icon_color: str)             # e.g. "blue"
  .enable(enable: bool)                    # True = query runs on every refresh
  .hide(hide: bool)                        # False = toggle visible in dashboard header
  .target(target: Builder[AnnotationTarget])
```

## AnnotationTarget builder

```python
AnnotationTarget()
  .type(type_val: str)     # "tags" = query by tag; "dashboard" = this dashboard's annotations only
  .tags(tags: list[str])   # e.g. ["deployment"]
  .limit(limit: int)       # max annotations to return, e.g. 100
  .match_any(match_any: bool)  # True = OR logic across tags; False = AND (default)
```

Example wiring (Grafana native store, deployment events):
```python
deployment_annotation = (
    AnnotationQuery()
    .name("Deployments")
    .datasource(DataSourceRef(type_val="grafana", uid="-- Grafana --"))
    .icon_color("blue")
    .enable(True)
    .hide(False)
    .target(AnnotationTarget().type("tags").tags(["deployment"]).limit(100))
)

Dashboard("My Dashboard").annotation(deployment_annotation)
```
