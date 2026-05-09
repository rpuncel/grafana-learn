.PHONY: up down deploy deploy-grafonnet deploy-sdk

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
	gcx resources validate -p grafonnet/resources/
	gcx resources push -p grafonnet/resources/

deploy-sdk:
	poetry run pyright foundation-sdk/
	poetry run python foundation-sdk/deploy.py

deploy: deploy-grafonnet deploy-sdk
