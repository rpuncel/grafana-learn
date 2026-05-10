local g = import 'github.com/grafana/grafonnet/gen/grafonnet-v11.4.0/main.libsonnet';

local logs = g.panel.logs;
local lokiQuery = g.query.loki;
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

local logsPanel =
  logs.new('Logs')
  + logs.queryOptions.withDatasource('loki', 'loki')
  + logs.queryOptions.withTargets([
    lokiQuery.new('loki', '{service_name="${service}"}')
    + lokiQuery.withRefId('A')
    + lokiQuery.withQueryType('range'),
  ])
  + logs.panelOptions.withGridPos(h=16, w=24, x=0, y=0);

g.dashboard.new('Logs Drill-down')
+ g.dashboard.withUid('logs-drilldown')
+ g.dashboard.withDescription('Logs for the selected service, queried from Loki.')
+ g.dashboard.withTags(['logs-drilldown', 'grafonnet'])
+ g.dashboard.withTimezone('browser')
+ g.dashboard.withRefresh('30s')
+ g.dashboard.withVariables([serviceVar])
+ g.dashboard.withLinks([
  g.dashboard.link.link.new('Fleet Overview', '/d/fleet-overview')
  + { keepTime: true, targetBlank: false },
  g.dashboard.link.link.new('Service Dashboard', '/d/service-dashboard')
  + { keepTime: true, targetBlank: false },
])
+ g.dashboard.withPanels([logsPanel])
