local g = import 'github.com/grafana/grafonnet/gen/grafonnet-v11.4.0/main.libsonnet';

local var = g.dashboard.variable;
local tempoQuery = g.query.tempo;

local serviceVar =
  var.query.new('service')
  + var.query.withDatasource('prometheus', 'prometheus')
  + var.query.queryTypes.withLabelValues(
    'service_name',
    'http_server_request_duration_seconds_count',
  )
  + var.query.generalOptions.withLabel('Service')
  + var.query.refresh.onTime()
  + var.query.selectionOptions.withIncludeAll(false);

// The Tempo datasource returns trace search results with preferredVisualisationType: "table".
// The "traces" panel type only handles single-trace waterfall views; use "table" for search results.
local tracesPanel = {
  type: 'table',
  title: 'Traces',
  datasource: { type: 'tempo', uid: 'tempo' },
  targets: [
    tempoQuery.new('tempo', '{resource.service.name="${service}"}', [])
    + { queryType: 'traceql', refId: 'A' },
  ],
  gridPos: { h: 16, w: 24, x: 0, y: 0 },
  options: {},
  fieldConfig: { defaults: {}, overrides: [] },
};

g.dashboard.new('Traces Drill-down')
+ g.dashboard.withUid('traces-drilldown')
+ g.dashboard.withDescription('Traces for the selected service, queried from Tempo. Opened from the Service Dashboard latency panel.')
+ g.dashboard.withTags(['traces-drilldown', 'grafonnet'])
+ g.dashboard.withTimezone('browser')
+ g.dashboard.withRefresh('30s')
+ g.dashboard.withVariables([serviceVar])
+ g.dashboard.withLinks([
  g.dashboard.link.link.new('Fleet Overview', '/d/fleet-overview')
  + { keepTime: true, targetBlank: false },
  g.dashboard.link.link.new('Service Dashboard', '/d/service-dashboard')
  + { keepTime: true, targetBlank: false },
])
+ g.dashboard.withPanels([tracesPanel])
