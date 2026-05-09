// Placeholder dashboard for the Grafonnet track.
// This is a minimal scaffold — feature dashboards are implemented in separate issues.
local grafonnet = import 'github.com/grafana/grafonnet/gen/grafonnet-v11.4.0/main.libsonnet';

local dashboard = grafonnet.dashboard;
local panel = grafonnet.panel;
local text = grafonnet.panel.text;

dashboard.new('Placeholder — Grafonnet Track')
+ dashboard.withUid('grafonnet-placeholder')
+ dashboard.withDescription('Scaffold placeholder. Feature dashboards are coming in subsequent issues.')
+ dashboard.withTags(['placeholder', 'grafonnet'])
+ dashboard.withTimezone('browser')
+ dashboard.withRefresh('30s')
+ dashboard.withPanels([
  text.new('Welcome')
  + text.panelOptions.withDescription('Placeholder panel')
  + text.options.withMode('markdown')
  + text.options.withContent(|||
    ## Grafonnet Track — Placeholder

    This dashboard is a scaffold confirming that the Grafonnet toolchain is wired up correctly.

    Feature dashboards (Fleet Overview, Service Dashboard, Drill-downs) are implemented in subsequent issues.
  |||)
  + text.gridPos.withX(0)
  + text.gridPos.withY(0)
  + text.gridPos.withW(24)
  + text.gridPos.withH(8),
])
