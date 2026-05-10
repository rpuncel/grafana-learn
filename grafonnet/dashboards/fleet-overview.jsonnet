local g = import 'github.com/grafana/grafonnet/gen/grafonnet-v11.4.0/main.libsonnet';

local ts = g.panel.timeSeries;
local ng = g.panel.nodeGraph;
local table = g.panel.table;
local promQuery = g.query.prometheus;
local tempoQuery = g.query.tempo;

// Data link: clicking a series navigates to the Service Dashboard for that service.
local serviceDashboardLink = {
  title: 'Open Service Dashboard',
  url: '/d/service-dashboard?var-service=${__field.labels.service_name}',
  targetBlank: false,
};

local ratePanel =
  ts.new('Request Rate by Service')
  + ts.queryOptions.withDatasource('prometheus', 'prometheus')
  + ts.queryOptions.withTargets([
    promQuery.new(
      'prometheus',
      'sum(rate(http_server_request_duration_seconds_count[$__rate_interval])) by (service_name)',
    )
    + promQuery.withLegendFormat('{{service_name}}'),
  ])
  + ts.standardOptions.withUnit('reqps')
  + ts.standardOptions.withLinks([serviceDashboardLink])
  + ts.panelOptions.withGridPos(h=8, w=24, x=0, y=0);

local errorRatePanel =
  ts.new('Error Rate by Service')
  + ts.queryOptions.withDatasource('prometheus', 'prometheus')
  + ts.queryOptions.withTargets([
    promQuery.new(
      'prometheus',
      |||
        sum(rate(http_server_request_duration_seconds_count{http_response_status_code=~"5.."}[$__rate_interval])) by (service_name)
        /
        sum(rate(http_server_request_duration_seconds_count[$__rate_interval])) by (service_name)
      |||,
    )
    + promQuery.withLegendFormat('{{service_name}}'),
  ])
  + ts.standardOptions.withUnit('percentunit')
  + ts.standardOptions.withLinks([serviceDashboardLink])
  + ts.panelOptions.withGridPos(h=8, w=24, x=0, y=8);

local nodeGraphPanel =
  ng.new('Service Topology')
  + ng.queryOptions.withDatasource('tempo', 'tempo')
  + ng.queryOptions.withTargets([
    tempoQuery.new('tempo', '', [])
    + tempoQuery.withQueryType('serviceMap')
    + { refId: 'A' },
  ])
  + ng.panelOptions.withGridPos(h=12, w=24, x=0, y=16);

local errorRateSummaryPanel =
  table.new('Current Error Rate by Service')
  + table.queryOptions.withDatasource('prometheus', 'prometheus')
  + table.queryOptions.withTargets([
    promQuery.new(
      'prometheus',
      |||
        sum(rate(http_server_request_duration_seconds_count{http_response_status_code=~"5.."}[$__rate_interval])) by (service_name)
        /
        sum(rate(http_server_request_duration_seconds_count[$__rate_interval])) by (service_name)
      |||,
    )
    + promQuery.withLegendFormat('{{service_name}}'),
  ])
  + table.queryOptions.withTransformations([
    {
      id: 'reduce',
      options: {
        reducers: ['lastNotNull'],
        mode: 'seriesToRows',
      },
    },
  ])
  + table.standardOptions.withUnit('percentunit')
  + table.panelOptions.withGridPos(h=6, w=24, x=0, y=28);

g.dashboard.new('Fleet Overview')
+ g.dashboard.withUid('fleet-overview')
+ g.dashboard.withDescription('All services at a glance — request rate and error rate. Click a series to open the Service Dashboard for that service.')
+ g.dashboard.withTags(['fleet-overview', 'grafonnet'])
+ g.dashboard.withTimezone('browser')
+ g.dashboard.withRefresh('30s')
+ g.dashboard.withLinks([
  g.dashboard.link.link.new('Service Dashboard', '/d/service-dashboard')
  + { keepTime: true, targetBlank: false },
])
+ g.dashboard.withPanels([ratePanel, errorRatePanel, nodeGraphPanel, errorRateSummaryPanel])
