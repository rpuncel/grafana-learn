local g = import 'github.com/grafana/grafonnet/gen/grafonnet-v11.4.0/main.libsonnet';

local ts = g.panel.timeSeries;
local promQuery = g.query.prometheus;
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

local ratePanel =
  ts.new('Request Rate')
  + ts.queryOptions.withDatasource('prometheus', 'prometheus')
  + ts.queryOptions.withTargets([
    promQuery.new(
      'prometheus',
      'sum(rate(http_server_request_duration_seconds_count{service_name="$service"}[$__rate_interval]))',
    )
    + promQuery.withLegendFormat('req/s'),
  ])
  + ts.standardOptions.withUnit('reqps')
  + ts.panelOptions.withGridPos(h=8, w=12, x=0, y=0);

local errorRatePanel =
  ts.new('Error Rate')
  + ts.queryOptions.withDatasource('prometheus', 'prometheus')
  + ts.queryOptions.withTargets([
    promQuery.new(
      'prometheus',
      |||
        sum(rate(http_server_request_duration_seconds_count{service_name="$service", http_response_status_code=~"5.."}[$__rate_interval]))
        /
        sum(rate(http_server_request_duration_seconds_count{service_name="$service"}[$__rate_interval]))
      |||,
    )
    + promQuery.withLegendFormat('error rate'),
  ])
  + ts.standardOptions.withUnit('percentunit')
  + ts.panelOptions.withGridPos(h=8, w=12, x=12, y=0);

local latencyPanel =
  ts.new('Request Duration p99')
  + ts.queryOptions.withDatasource('prometheus', 'prometheus')
  + ts.queryOptions.withTargets([
    promQuery.new(
      'prometheus',
      'histogram_quantile(0.99, sum(rate(http_server_request_duration_seconds_bucket{service_name="$service"}[$__rate_interval])) by (le))',
    )
    + promQuery.withLegendFormat('p99'),
  ])
  + ts.standardOptions.withUnit('s')
  + ts.standardOptions.withLinks([{
    title: 'View Traces',
    url: '/d/traces-drilldown?var-service=${service}&${__url_time_range}',
    targetBlank: false,
  }])
  + ts.panelOptions.withGridPos(h=8, w=24, x=0, y=8);

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
+ g.dashboard.withPanels([ratePanel, errorRatePanel, latencyPanel])
