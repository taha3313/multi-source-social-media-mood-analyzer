.DEFAULT_GOAL := help
.PHONY: help setup backend-install backend-dev backend-run backend-test backend-lint frontend-install frontend-dev frontend-build frontend-lint check docker-build docker-up docker-down docker-logs
HOST ?= 0.0.0.0
PORT ?= 8000
help: ## Show commands
	@awk 'BEGIN {FS=":.*## "} /^[a-z-]+:.*## / {printf "  %-22s %s\n", $$1, $$2}' $(MAKEFILE_LIST)
setup: ## Create local env files without overwriting existing ones
	@test -f backend/.env || cp backend/.env.example backend/.env
	@test -f frontend/.env || cp frontend/.env.example frontend/.env
backend-install: ## Install locked Python dependencies using uv
	cd backend && uv sync --frozen
backend-dev: ## Run API with reload on :8000
	cd backend && uv run --frozen uvicorn app.main:app --reload --host $(HOST) --port $(PORT)
backend-run: ## Run API with one model-owning worker
	cd backend && uv run --frozen uvicorn app.main:app --host $(HOST) --port $(PORT) --workers 1
backend-test: ## Test API without downloading ML models or calling providers
	cd backend && uv run --frozen pytest -q
backend-lint: ## Check Python correctness
	cd backend && uv run --frozen ruff check app tests
frontend-install: ## Install locked frontend dependencies
	cd frontend && npm ci
frontend-dev: ## Run Vite on :5173 with API proxy
	cd frontend && npm run dev
frontend-build: ## Build production frontend
	cd frontend && npm run build
frontend-lint: ## Lint frontend
	cd frontend && npm run lint
check: backend-lint backend-test frontend-lint frontend-build ## Run CI checks locally
docker-build: ## Build both containers
	docker compose build
docker-up: setup ## Start frontend :8080 and API :8000
	docker compose up --build -d
docker-down: ## Stop containers, preserving model cache
	docker compose down
docker-logs: ## Follow container logs
	docker compose logs -f
