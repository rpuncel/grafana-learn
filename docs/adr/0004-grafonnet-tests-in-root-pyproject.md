# Root pyproject.toml owns Grafonnet output tests

Grafonnet output tests (pytest files that compile `.jsonnet` dashboards and assert on their JSON structure) live in `grafonnet/tests/` and are executed via a root-level `pyproject.toml`. The `foundation-sdk/` subdirectory keeps its own `pyproject.toml` for SDK-track deployment and tests.

## Considered Options

- **Put Grafonnet tests in `foundation-sdk/tests/`** — one virtualenv, but mixes Grafonnet concerns into the SDK track, violating the track isolation established in ADR-0001 and ADR-0003.
- **Give `grafonnet/` its own `pyproject.toml`** — symmetric with `foundation-sdk/`, but creates a third Poetry project with no deployment code, just a test runner, which is more overhead than the problem warrants.
- **Root `pyproject.toml` as test harness** — chosen. The root is the natural integration layer between the two tracks. `grafonnet/tests/` stays next to the code it tests; `testpaths = ["grafonnet/tests"]` in the root pytest config makes discovery explicit. A second virtualenv is the only cost.
