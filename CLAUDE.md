## Python tooling

All Python work in this repo uses Poetry. Never use `pip`, `pip3`, or `requirements.txt`.

- **SDK track**: `poetry -C foundation-sdk run <cmd>` (e.g. `poetry -C foundation-sdk run pytest`, `poetry -C foundation-sdk run python deploy.py`)
- **Grafonnet tests**: `poetry run pytest` from the repo root (root `pyproject.toml`, `testpaths = ["grafonnet/tests"]`)
- **Adding dependencies**: `poetry -C <dir> add <package>` from root, or `poetry add <package>` from within the subdirectory
- **Tests**: always write pytest tests in the appropriate `tests/` directory — never one-off `python -c` or standalone scripts

## Agent skills

### Issue tracker

Issues live in GitHub Issues on `rpuncel/grafana-learn`. See `docs/agents/issue-tracker.md`.

### Triage labels

Five canonical labels with default strings (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`). See `docs/agents/triage-labels.md`.

### Domain docs

Single-context repo: `CONTEXT.md` + `docs/adr/` at root. See `docs/agents/domain.md`.
