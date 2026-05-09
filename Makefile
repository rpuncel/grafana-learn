.PHONY: up down deploy deploy-grafonnet deploy-sdk

GCX := gcx --config grafonnet/.gcx.yaml

# ── Infrastructure ─────────────────────────────────────────────────────────

up:
	docker compose up -d

down:
	docker compose down

# ── Deploy ─────────────────────────────────────────────────────────────────

deploy-grafonnet:
	mkdir -p grafonnet/resources
	for f in grafonnet/dashboards/*.jsonnet; do \
		jsonnet -J grafonnet/vendor "$$f" > grafonnet/resources/$$(basename "$$f" .jsonnet).json; \
	done
	poetry run python grafonnet/deploy.py

deploy-sdk:
	poetry run pyright foundation-sdk/
	poetry run python foundation-sdk/deploy.py

deploy: deploy-grafonnet deploy-sdk
