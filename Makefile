.PHONY: install validate query test lint format clean help

help:
	@echo "NKLLON Hardware Topology - Available Commands:"
	@echo "  make install   - Install dependencies using uv"
	@echo "  make validate  - Run SHACL validation on deployment data"
	@echo "  make query     - Run example SPARQL queries"
	@echo "  make test      - Run pytest test suite"
	@echo "  make lint      - Run ruff linter"
	@echo "  make format    - Format code with ruff"
	@echo "  make clean     - Remove build artifacts"

install:
	uv pip install -e ".[dev]"

validate:
	@echo "Running SHACL validation..."
	uv run python -m nkllon.validate

query:
	@echo "Running example SPARQL queries..."
	uv run python -m nkllon.query

test:
	uv run pytest tests/ -v

lint:
	uv run ruff check src/ tests/

format:
	uv run ruff format src/ tests/

clean:
	rm -rf build/ dist/ *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
