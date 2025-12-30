.PHONY: install validate query test lint format clean help visualize diff docker-build docker-run coverage

help:
	@echo "NKLLON Hardware Topology - Available Commands:"
	@echo "  make install      - Install dependencies using uv"
	@echo "  make validate     - Run SHACL validation on deployment data"
	@echo "  make query        - Run example SPARQL queries"
	@echo "  make visualize    - Generate interactive topology visualization"
	@echo "  make diff         - Compare two topology files"
	@echo "  make test         - Run pytest test suite"
	@echo "  make coverage     - Run tests with coverage report"
	@echo "  make lint         - Run ruff linter"
	@echo "  make format       - Format code with ruff"
	@echo "  make docker-build - Build Docker image"
	@echo "  make docker-run   - Run validation in Docker"
	@echo "  make clean        - Remove build artifacts"

install:
	uv pip install -e ".[dev]"

validate:
	@echo "Running SHACL validation..."
	uv run python -m nkllon.validate

validate-export:
	@echo "Running validation with HTML report export..."
	uv run nkllon validate --export validation_report.html --format html

query:
	@echo "Running example SPARQL queries..."
	uv run python -m nkllon.query

visualize:
	@echo "Generating topology visualization..."
	uv run nkllon visualize --output topology_visualization.html
	@echo "✅ Open topology_visualization.html in your browser"

diff:
	@echo "Usage: make diff FILE1=path/to/file1.ttl FILE2=path/to/file2.ttl"
	@if [ -z "$(FILE1)" ] || [ -z "$(FILE2)" ]; then \
		echo "Error: Please specify FILE1 and FILE2"; \
		exit 1; \
	fi
	uv run nkllon diff $(FILE1) $(FILE2)

test:
	uv run pytest tests/ -v

coverage:
	uv run pytest tests/ -v --cov=src/nkllon --cov-report=html --cov-report=term
	@echo "✅ Coverage report generated in htmlcov/index.html"

lint:
	uv run ruff check src/ tests/

format:
	uv run ruff format src/ tests/

docker-build:
	docker build -t nkllon-topology:latest .

docker-run:
	docker run --rm -v $(PWD)/reports:/app/reports nkllon-topology:latest

docker-compose-up:
	docker-compose up --build

docker-compose-down:
	docker-compose down

clean:
	rm -rf build/ dist/ *.egg-info
	rm -rf htmlcov/ .coverage
	rm -rf reports/
	rm -f topology_visualization.html validation_report.*
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
