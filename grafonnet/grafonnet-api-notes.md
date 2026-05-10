# Grafonnet API Notes

Grafonnet version: `grafonnet-v11.4.0`

## Standard import

```jsonnet
local g = import 'github.com/grafana/grafonnet/gen/grafonnet-v11.4.0/main.libsonnet';
```

## Panel builders

All panels use the same chainable pattern: `p.new(title) + p.queryOptions.* + p.panelOptions.*`

### Time series

```jsonnet
local ts = g.panel.timeSeries;

ts.new('My Panel')
+ ts.queryOptions.withDatasource('prometheus', 'prometheus')
+ ts.queryOptions.withTargets([...])
+ ts.standardOptions.withUnit('reqps')          // unit string
+ ts.standardOptions.withLinks([dataLink])      // panel-level data links
+ ts.panelOptions.withGridPos(h=8, w=24, x=0, y=0)
```

### Node Graph

```jsonnet
local ng = g.panel.nodeGraph;

ng.new('Service Topology')
+ ng.queryOptions.withDatasource('tempo', 'tempo')
+ ng.queryOptions.withTargets([
    g.query.tempo.new('tempo', '', [])
    + g.query.tempo.withQueryType('serviceMap'),  // nodes+edges from Tempo service graph
    + { refId: 'A' },
  ])
+ ng.panelOptions.withGridPos(h=12, w=24, x=0, y=16)
```

### Table (raw object — builder doesn't set type correctly for search results)

Use a raw Jsonnet object when the panel needs an explicit `type` that the builder doesn't expose cleanly (e.g. Tempo trace search results, which must be `type: "table"` not `type: "traces"`):

```jsonnet
local tracesPanel = {
  type: 'table',
  title: 'Traces',
  datasource: { type: 'tempo', uid: 'tempo' },
  targets: [
    g.query.tempo.new('tempo', '{resource.service.name="${service}"}', [])
    + g.query.tempo.withQueryType('traceql')
    + { refId: 'A' },
  ],
  gridPos: { h: 16, w: 24, x: 0, y: 0 },
  options: {},
  fieldConfig: { defaults: {}, overrides: [] },
};
```

### Logs (raw object)

```jsonnet
local logsPanel = {
  type: 'logs',
  title: 'Logs',
  datasource: { type: 'loki', uid: 'loki' },
  targets: [{ ... }],
  gridPos: { h: 16, w: 24, x: 0, y: 0 },
  options: {},
  fieldConfig: { defaults: {}, overrides: [] },
};
```

## Panel options DSL

```jsonnet
p.queryOptions.withDatasource(type, uid)   // sets panel-level datasource
p.queryOptions.withTargets([...])          // array of query objects
p.standardOptions.withUnit(unit)           // unit string (reqps, percentunit, s, ...)
p.standardOptions.withLinks([link])        // panel-level data links (field-level)
p.panelOptions.withGridPos(h, w, x, y)    // grid position (all optional args)
```

## Data link object (panel-level)

```jsonnet
{
  title: 'Open Service Dashboard',
  url: '/d/service-dashboard?var-service=${__field.labels.service_name}',
  targetBlank: false,
}
```

## Query builders

### Prometheus

```jsonnet
local promQuery = g.query.prometheus;

promQuery.new('prometheus', 'sum(rate(metric[$__rate_interval])) by (label)')
+ promQuery.withLegendFormat('{{label}}')
```

### Tempo — TraceQL search

```jsonnet
g.query.tempo.new('tempo', '{resource.service.name="${service}"}', [])
+ g.query.tempo.withQueryType('traceql')
+ { refId: 'A' }
```

### Tempo — service map (Node Graph)

```jsonnet
g.query.tempo.new('tempo', '', [])
+ g.query.tempo.withQueryType('serviceMap')
+ { refId: 'A' }
```

### Loki

```jsonnet
{
  datasource: { type: 'loki', uid: 'loki' },
  expr: '{service_name="${service}"}',
  refId: 'A',
}
```

## Dashboard builder

```jsonnet
g.dashboard.new('My Dashboard')
+ g.dashboard.withUid('my-dashboard')
+ g.dashboard.withDescription('...')
+ g.dashboard.withTags(['tag1', 'tag2'])
+ g.dashboard.withTimezone('browser')
+ g.dashboard.withRefresh('30s')
+ g.dashboard.withVariables([serviceVar])
+ g.dashboard.withLinks([dashLink])
+ g.dashboard.withPanels([panel1, panel2])
```

## Variables

```jsonnet
local var = g.dashboard.variable;

// Query variable (Prometheus label values)
var.query.new('service')
+ var.query.withDatasource('prometheus', 'prometheus')
+ var.query.queryTypes.withLabelValues('service_name', 'http_server_request_duration_seconds_count')
+ var.query.generalOptions.withLabel('Service')
+ var.query.refresh.onTime()
+ var.query.selectionOptions.withIncludeAll(false)
```

## Dashboard links

```jsonnet
// Named link to another dashboard
g.dashboard.link.link.new('Fleet Overview', '/d/fleet-overview')
+ { keepTime: true, targetBlank: false }
```
