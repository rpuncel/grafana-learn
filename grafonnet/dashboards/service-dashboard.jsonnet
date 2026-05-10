local g = import 'github.com/grafana/grafonnet/gen/grafonnet-v11.4.0/main.libsonnet';

local var = g.dashboard.variable;

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

// Library panel references — panel content comes from library elements deployed by deploy.py
local rateRef = {
  libraryPanel: { uid: 'red-metrics-rate', name: 'Request Rate' },
  gridPos: { h: 8, w: 12, x: 0, y: 0 },
};

local errorRateRef = {
  libraryPanel: { uid: 'red-metrics-error-rate', name: 'Error Rate' },
  gridPos: { h: 8, w: 12, x: 12, y: 0 },
};

local latencyRef = {
  libraryPanel: { uid: 'red-metrics-latency', name: 'Request Duration p99' },
  gridPos: { h: 8, w: 24, x: 0, y: 8 },
};

g.dashboard.new('Service Dashboard')
+ g.dashboard.withUid('service-dashboard')
+ g.dashboard.withDescription('RED metrics for the selected service. Use the $service variable to switch services.')
+ g.dashboard.withTags(['service-dashboard', 'grafonnet'])
+ g.dashboard.withTimezone('browser')
+ g.dashboard.withRefresh('30s')
+ g.dashboard.withVariables([serviceVar])
+ g.dashboard.withLinks([
  g.dashboard.link.link.new('Fleet Overview', '/d/fleet-overview')
  + { keepTime: true, targetBlank: false },
])
+ g.dashboard.withPanels([rateRef, errorRateRef, latencyRef], setPanelIDs=false)
