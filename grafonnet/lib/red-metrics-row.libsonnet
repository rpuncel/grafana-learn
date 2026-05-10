// RED metrics library panels for the Service Dashboard.
// Compiles to an array of Grafana library-element request bodies (kind=1).
// Deployed by deploy.py via POST/PATCH /api/library-elements before dashboards.

local g = import 'github.com/grafana/grafonnet/gen/grafonnet-v11.4.0/main.libsonnet';

local ts = g.panel.timeSeries;
local promQuery = g.query.prometheus;

local ratePanel =
  ts.new('Request Rate')
  + ts.queryOptions.withDatasource('prometheus', 'prometheus')
  + ts.queryOptions.withTargets([
    promQuery.new(
      'prometheus',
      'sum by (service_name)(rate(http_server_request_duration_seconds_count{service_name="$service"}[$__rate_interval]))',
    )
    + promQuery.withLegendFormat('req/s'),
  ])
  + ts.standardOptions.withUnit('reqps');

local errorRatePanel =
  ts.new('Error Rate')
  + ts.queryOptions.withDatasource('prometheus', 'prometheus')
  + ts.queryOptions.withTargets([
    promQuery.new(
      'prometheus',
      |||
        sum by (service_name)(rate(http_server_request_duration_seconds_count{service_name="$service", http_response_status_code=~"5.."}[$__rate_interval]))
        /
        sum by (service_name)(rate(http_server_request_duration_seconds_count{service_name="$service"}[$__rate_interval]))
      |||,
    )
    + promQuery.withLegendFormat('error rate'),
  ])
  + ts.standardOptions.withUnit('percentunit');

local latencyPanel =
  ts.new('Request Duration p99')
  + ts.queryOptions.withDatasource('prometheus', 'prometheus')
  + ts.queryOptions.withTargets([
    promQuery.new(
      'prometheus',
      'histogram_quantile(0.99, sum by (le, service_name)(rate(http_server_request_duration_seconds_bucket{service_name="$service"}[$__rate_interval])))',
    )
    + promQuery.withLegendFormat('p99'),
  ])
  + ts.standardOptions.withUnit('s')
  + ts.standardOptions.withLinks([{
    title: 'View Traces',
    url: '/d/traces-drilldown?var-service=${service}&${__url_time_range}',
    targetBlank: false,
  }]);

[
  { uid: 'red-metrics-rate', name: 'Request Rate', kind: 1, model: ratePanel },
  { uid: 'red-metrics-error-rate', name: 'Error Rate', kind: 1, model: errorRatePanel },
  { uid: 'red-metrics-latency', name: 'Request Duration p99', kind: 1, model: latencyPanel },
]
