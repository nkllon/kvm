# Contributing to NKLLON Hardware Topology System

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Code Style](#code-style)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Adding Features](#adding-features)

## Getting Started

### Prerequisites

- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) package manager
- Git

### Setup

1. **Fork the repository**

   ```bash
   # Click "Fork" on GitHub, then clone your fork
   git clone https://github.com/YOUR_USERNAME/kvm.git
   cd kvm
   ```

2. **Install dependencies**

   ```bash
   # Using make
   make install

   # Or using uv directly
   uv pip install -e ".[dev]"
   ```

3. **Install pre-commit hooks**

   ```bash
   uv run pre-commit install
   ```

4. **Run tests to verify setup**

   ```bash
   make test
   ```

## Development Workflow

### Creating a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### Making Changes

1. Make your changes
2. Add tests for new functionality
3. Update documentation as needed
4. Run tests and linting

```bash
make test
make lint
```

### Committing Changes

We follow conventional commits format:

```bash
git commit -m "feat: add new device type support"
git commit -m "fix: correct SHACL constraint for audio purity"
git commit -m "docs: update README with new examples"
```

Types:

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Test additions or changes
- `refactor`: Code refactoring
- `chore`: Maintenance tasks

## Code Style

### Python Style Guide

- Follow PEP 8
- Use type hints for all functions
- Write docstrings for all public functions and classes
- Maximum line length: 100 characters

### Linting & Formatting Strategy ("Smart & Safe")

We prioritize **functional correctness** and **automated consistency** over manual style enforcement. For a full explanation of the design and requirements, see [ADR 0001: Smart & Safe Linting Strategy](../docs/adr/0001-smart-and-safe-linting.md).

- **Auto-formatting (ON)**: We use `ruff format` and pre-commit hooks to automatically format code (spacing, quotes, etc.) **and sort imports**. You should never have to manually format code or organize imports.
- **Strict Typing (ON)**: We use `mypy` with strict settings to catch type errors before runtime. This is for safety.
- **Style Linting (OFF)**: We explicitly **disable** stylistic linting rules (like "line too long" or "unsorted imports"). The Linter (`ruff check`) is configured to only report **logical errors** (undefined variables, syntax errors) via the `F` (Pyflakes) selector.

Command reference:

```bash
# Check for logic errors and type safety (will NOT complain about style)
make lint

# Auto-format your code (fixing style issues automatically)
make format
```

### Docstring Format

Use Google-style docstrings:

```python
def validate_topology(
    ontology_path: Path,
    shacl_path: Path,
    data_path: Path,
) -> Tuple[bool, str]:
    """
    Validate hardware topology against SHACL constraints.

    Args:
        ontology_path: Path to hardware ontology TTL file
        shacl_path: Path to SHACL constraints TTL file
        data_path: Path to physical deployment data TTL file

    Returns:
        Tuple of (conforms: bool, report: str)

    Raises:
        ValidationError: If validation cannot be performed
    """
```

## Testing

### Running Tests

```bash
# Run all tests
make test

# Run specific test file
uv run pytest tests/test_validation.py -v

# Run specific test
uv run pytest tests/test_validation.py::test_validation_passes -v

# Run with coverage
uv run pytest tests/ --cov=src/nkllon --cov-report=html
```

### Writing Tests

- Place tests in `tests/` directory
- Name test files `test_*.py`
- Name test functions `test_*`
- Use fixtures for common setup
- Aim for >80% code coverage

Example test:

```python
def test_new_feature(project_root):
    """Test that new feature works correctly."""
    # Arrange
    config = Config(project_root)

    # Act
    result = new_feature(config)

    # Assert
    assert result is not None
    assert result.status == "success"
```

## Pull Request Process

### Before Submitting

1. ✅ All tests pass
2. ✅ Code is formatted (`make format`)
3. ✅ No linting errors (`make lint`)
4. ✅ Documentation is updated
5. ✅ Commit messages follow conventions
6. ✅ Branch is up to date with main

### Submitting

1. Push your branch to your fork
2. Create a pull request on GitHub
3. Fill out the PR template
4. Wait for CI to pass
5. Request review

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests added/updated
- [ ] All tests pass
- [ ] Manual testing performed

## Checklist
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] No new warnings
```

## Adding Features

### Adding New Device Types

1. **Update ontology** (`ontology/hardware_ontology.ttl`):

   ```turtle
   :NewDeviceType a owl:Class ; rdfs:subClassOf :Device .
   ```

2. **Add validation rules** (if needed) in `ontology/system_constraints.shacl.ttl`:

   ```turtle
   :NewDeviceShape a sh:NodeShape ;
       sh:targetClass :NewDeviceType ;
       sh:property [
           sh:path :requiredProperty ;
           sh:minCount 1 ;
       ] .
   ```

3. **Add test cases** in `tests/test_validation.py`:

   ```python
   def test_new_device_type_exists(data_path, ontology_path):
       """Test that NewDeviceType exists."""
       graph = load_graph(data_path)
       graph += load_graph(ontology_path)

       query = """
           PREFIX : <http://nkllon.com/sys#>
           SELECT ?device WHERE {
               ?device a :NewDeviceType .
           }
       """

       results = list(graph.query(query))
       assert len(results) > 0
   ```

4. **Update documentation** in `README.md`

5. **Add example data** in `data/physical_deployment.ttl`:

   ```turtle
   :MyNewDevice a :NewDeviceType ;
       :hasPort :MyNewDevice_Port1 .
   ```

### Adding New SHACL Constraints

1. **Define SHACL shape** in `ontology/system_constraints.shacl.ttl`:

   ```turtle
   :NewConstraintShape a sh:NodeShape ;
       sh:targetClass :TargetClass ;
       sh:sparql [
           sh:message "ERROR: Constraint violation message" ;
           sh:select """
               PREFIX : <http://nkllon.com/sys#>
               SELECT $this
               WHERE {
                   # SPARQL query that returns violating nodes
               }
           """ ;
       ] .
   ```

2. **Add passing test**:

   ```python
   def test_new_constraint_passes(ontology_path, shacl_path, data_path):
       """Test that new constraint passes with valid data."""
       conforms, report = validate_topology(
           ontology_path, shacl_path, data_path
       )
       assert conforms
   ```

3. **Add failing test**:

   ```python
   def test_new_constraint_fails_invalid_data():
       """Test that new constraint fails with invalid data."""
       # Create invalid test data
       # Validate and assert it fails
   ```

4. **Document the constraint** in `README.md`

### Adding New Queries

1. **Add query function** in `src/nkllon/query.py`:

   ```python
   def query_new_feature() -> List[ResultRow]:
       """Find things for new feature."""
       graph = load_merged_graph()

       query = """
           PREFIX : <http://nkllon.com/sys#>
           SELECT ?result WHERE {
               # Your SPARQL query
           }
       """

       return list(graph.query(query))
   ```

2. **Add to main()** in `query.py`:

   ```python
   # In main()
   print("\n🔍 Query N: New Feature")
   print("-" * 80)
   results = query_new_feature()
   for row in results:
       print(f"  {format_uri(str(row.result))}")
   ```

3. **Add test**:

   ```python
   def test_new_query_returns_results():
       """Test that new query returns expected results."""
       results = query_new_feature()
       assert len(results) > 0
   ```

## Project Structure

```
nkllon-topology/
├── src/nkllon/              # Python package
│   ├── __init__.py          # Package initialization
│   ├── cli.py               # Command-line interface
│   ├── config.py            # Configuration management
│   ├── diff.py              # Topology comparison
│   ├── exceptions.py        # Custom exceptions
│   ├── query.py             # SPARQL queries
│   ├── reporters.py         # Report exporters
│   ├── validate.py          # SHACL validation
│   └── visualize.py         # Visualization generation
├── ontology/                # RDF/OWL definitions
│   ├── hardware_ontology.ttl           # Device classes
│   └── system_constraints.shacl.ttl    # Validation rules
├── data/                    # Deployment data
│   └── physical_deployment.ttl         # Hardware topology
├── tests/                   # Test suite
│   ├── __init__.py
│   └── test_validation.py
├── .github/workflows/       # CI/CD
│   └── ci.yml
├── pyproject.toml           # Project configuration
├── Makefile                 # Development commands
└── README.md                # Project documentation
```

## Questions?

- Open an issue for bugs or feature requests
- Start a discussion for questions
- Check existing issues before creating new ones

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing! 🎉
