.PHONY: install playground run test lint clean

install:
	uv sync
	uv run agents-cli install

playground:
	uv run agents-cli playground --port 18081 --reload_agents

run:
	uv run python -m app.fast_api_app

test:
	uv run pytest tests/unit tests/integration

lint:
	uv run agents-cli lint

clean:
	rm -rf .venv __pycache__ .adk .pytest_cache .ruff_cache
