.PHONY: up down deploy deploy-grafonnet deploy-sdk

# ── Infrastructure ─────────────────────────────────────────────────────────

up:
	docker compose up -d

down:
	docker compose down

# ── Deploy ─────────────────────────────────────────────────────────────────

deploy-grafonnet:
	jsonnet grafonnet/dashboards/placeholder.jsonnet
	grr validate grafonnet/
	grr apply grafonnet/

deploy-sdk:
	poetry run pyright foundation-sdk/
	poetry run python foundation-sdk/deploy.py

deploy: deploy-grafonnet deploy-sdk
