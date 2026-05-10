## Python tooling

All Python work in this repo uses Poetry. Never use `pip`, `pip3`, or `requirements.txt`.

- **SDK track**: `poetry -C foundation-sdk run <cmd>` (e.g. `poetry -C foundation-sdk run pytest`, `poetry -C foundation-sdk run python deploy.py`)
- **Root pytest**: `poetry run pytest` from the repo root covers grafonnet dashboard tests (`grafonnet/tests/`) and integration tests (`tests/integration/`); integration tests are skipped automatically if Grafana is unreachable
- **Adding dependencies**: `poetry -C <dir> add <package>` from root, or `poetry add <package>` from within the subdirectory
- **Tests**: always write pytest tests in the appropriate `tests/` directory — never one-off `python -c` or standalone scripts

## Deployment

- **`make deploy`** — compile all Jsonnet dashboards and deploy both tracks to their Grafana instances; always run from repo root

### foundation-sdk specifics

- Install: `poetry install --no-root --with dev` from within `foundation-sdk/` — plain `poetry install` fails because `packages = [{ include = "." }]` in its pyproject.toml
- SDK builder API reference: `foundation-sdk/sdk-api-notes.md` — read this before writing SDK dashboard code to avoid needing runtime introspection
- Grafonnet builder API reference: `grafonnet/grafonnet-api-notes.md` — read this before writing Grafonnet dashboard code to avoid searching vendor files

**After implementing any new panel type or query pattern**, update both `foundation-sdk/sdk-api-notes.md` and `grafonnet/grafonnet-api-notes.md` before closing the issue.

## Agent skills

### Issue tracker

Issues live in GitHub Issues on `rpuncel/grafana-learn`. See `docs/agents/issue-tracker.md`.

### Triage labels

Five canonical labels with default strings (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`). See `docs/agents/triage-labels.md`.

### Domain docs

Single-context repo: `CONTEXT.md` + `docs/adr/` at root. See `docs/agents/domain.md`.
