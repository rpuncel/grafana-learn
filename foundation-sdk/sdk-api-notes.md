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
  .with_panel(panel: Builder[Panel])
  .link(link: Builder[DashboardLink])       # singular — add one link
  .links(links: list[Builder[DashboardLink]])  # plural — set all links at once
  .build()
```
