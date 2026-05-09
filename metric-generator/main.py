"""Synthetic HTTP metric generator for Grafana Learning Lab.

Each container instance simulates one service sending OpenTelemetry
http.server.request.duration metrics to the collector.

Environment variables:
  SERVICE_NAME   Name of the simulated service (required)
  OTLP_ENDPOINT  gRPC endpoint of the OTel Collector (default: http://otelcol:4317)
  ERROR_RATE     Fraction of requests that return 5xx (default: 0.05)
"""

from __future__ import annotations

import os
import random
import time

from opentelemetry import metrics as otel_metrics
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import SERVICE_NAME, Resource

SERVICE = os.environ["SERVICE_NAME"]
OTLP_ENDPOINT = os.getenv("OTLP_ENDPOINT", "http://otelcol:4317")
ERROR_RATE = float(os.getenv("ERROR_RATE", "0.05"))

resource = Resource.create({SERVICE_NAME: SERVICE})
exporter = OTLPMetricExporter(endpoint=OTLP_ENDPOINT, insecure=True)
reader = PeriodicExportingMetricReader(exporter, export_interval_millis=15_000)
provider = MeterProvider(resource=resource, metric_readers=[reader])
otel_metrics.set_meter_provider(provider)

meter = otel_metrics.get_meter(__name__)
request_duration = meter.create_histogram(
    "http.server.request.duration",
    unit="s",
    description="HTTP server request duration",
)

METHODS = ["GET", "POST"]

print(f"Generating metrics for service={SERVICE} error_rate={ERROR_RATE}", flush=True)

while True:
    status = "500" if random.random() < ERROR_RATE else "200"
    request_duration.record(
        abs(random.lognormvariate(-2.5, 0.8)),
        {
            "http.request.method": random.choice(METHODS),
            "http.response.status_code": status,
            "url.scheme": "http",
        },
    )
    time.sleep(random.uniform(0.05, 0.2))
