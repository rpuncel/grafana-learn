"""Synthetic HTTP metric + trace generator for Grafana Learning Lab.

Each container instance simulates one service sending OpenTelemetry
http.server.request.duration metrics and HTTP server spans to the collector.

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
from opentelemetry import trace as otel_trace
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import SpanKind, StatusCode

SERVICE = os.environ["SERVICE_NAME"]
OTLP_ENDPOINT = os.getenv("OTLP_ENDPOINT", "http://otelcol:4317")
ERROR_RATE = float(os.getenv("ERROR_RATE", "0.05"))

resource = Resource.create({SERVICE_NAME: SERVICE})

# Metrics
metric_exporter = OTLPMetricExporter(endpoint=OTLP_ENDPOINT, insecure=True)
reader = PeriodicExportingMetricReader(metric_exporter, export_interval_millis=15_000)
meter_provider = MeterProvider(resource=resource, metric_readers=[reader])
otel_metrics.set_meter_provider(meter_provider)

# Traces
span_exporter = OTLPSpanExporter(endpoint=OTLP_ENDPOINT, insecure=True)
tracer_provider = TracerProvider(resource=resource)
tracer_provider.add_span_processor(BatchSpanProcessor(span_exporter))
otel_trace.set_tracer_provider(tracer_provider)

meter = otel_metrics.get_meter(__name__)
tracer = otel_trace.get_tracer(__name__)

request_duration = meter.create_histogram(
    "http.server.request.duration",
    unit="s",
    description="HTTP server request duration",
)

METHODS = ["GET", "POST"]

print(f"Generating metrics and traces for service={SERVICE} error_rate={ERROR_RATE}", flush=True)

while True:
    method = random.choice(METHODS)
    status = "500" if random.random() < ERROR_RATE else "200"
    duration_s = abs(random.lognormvariate(-2.5, 0.8))

    # Metric — same as before
    request_duration.record(
        duration_s,
        {
            "http.request.method": method,
            "http.response.status_code": status,
            "url.scheme": "http",
        },
    )

    # Span — backdated so its duration matches the sampled request duration
    now_ns = time.time_ns()
    start_ns = now_ns - int(duration_s * 1e9)
    span = tracer.start_span(
        f"{method} /",
        kind=SpanKind.SERVER,
        start_time=start_ns,
        attributes={
            "http.request.method": method,
            "http.response.status_code": int(status),
            "url.scheme": "http",
        },
    )
    if status.startswith("5"):
        span.set_status(StatusCode.ERROR)
    span.end(end_time=now_ns)

    time.sleep(random.uniform(1, 5))
