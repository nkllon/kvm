# NKLLON Hardware Topology System - Project Context

## Project Overview

This is a semantic web validation system for KVM (Keyboard, Video, Mouse) hardware topologies using RDF/OWL ontologies and SHACL constraints.

## Core Technologies

- **Python 3.11+**: Primary language
- **RDF/OWL**: Ontology definition (Turtle format)
- **SHACL**: Constraint validation
- **SPARQL**: Query language
- **pySHACL**: Python SHACL validation library
- **RDFLib**: RDF graph manipulation

## Architecture

### Data Layer
- `ontology/hardware_ontology.ttl`: Device classes and properties (OWL)
- `data/physical_deployment.ttl`: Instance data for actual hardware

### Validation Layer
- `ontology/system_constraints.shacl.ttl`: SHACL shapes for business rules

### Application Layer
- `src/nkllon/validate.py`: SHACL validation engine
- `src/nkllon/query.py`: SPARQL query utilities
- `src/nkllon/cli.py`: Command-line interface
- `src/nkllon/visualize.py`: D3.js visualization generator
- `src/nkllon/diff.py`: Topology comparison tool
- `src/nkllon/reporters.py`: Report exporters (JSON/HTML/Markdown)
- `src/nkllon/config.py`: Configuration management
- `src/nkllon/exceptions.py`: Custom exception hierarchy

## Key Constraints

1. **eARC Return Path**: Smart displays must have HDMI-eARC path to PreAmp
2. **Audio Purity**: Audio interfaces must bypass KVMs (direct to Host or PreAmp)
3. **Bidirectional Cables**: USB-C to DisplayPort requires bidirectional cables
4. **Uptime Priority**: Production hosts must connect to high-priority KVM ports

## Development Guidelines

### Code Style
- Follow PEP 8
- Use type hints for all functions
- Write Google-style docstrings
- Maximum line length: 100 characters
- Use `ruff` for linting and formatting

### Testing
- Maintain >80% code coverage
- Write tests for all new features
- Use pytest fixtures for common setup
- Test both success and failure cases

### RDF/OWL Best Practices
- Use Turtle format for readability
- Namespace: `http://nkllon.com/sys#`
- Always define inverse properties where applicable
- Document all classes and properties with rdfs:comment

### SHACL Best Practices
- Use SPARQL-based constraints for complex rules
- Provide clear, actionable error messages
- Test constraints with both valid and invalid data
- Document constraint rationale in comments

## Common Tasks

### Adding New Device Type
1. Update `ontology/hardware_ontology.ttl` with new class
2. Add SHACL constraints if needed
3. Add test cases in `tests/test_validation.py`
4. Update README.md documentation
5. Add example data in `data/physical_deployment.ttl`

### Adding New Constraint
1. Define SHACL shape in `ontology/system_constraints.shacl.ttl`
2. Add passing test with valid data
3. Add failing test with invalid data
4. Document constraint in README.md

### Adding New Query
1. Add query function in `src/nkllon/query.py`
2. Add to main() output
3. Add test case
4. Document in README.md

## File Organization

```
nkllon-topology/
├── src/nkllon/              # Python package
├── ontology/                # RDF/OWL definitions
├── data/                    # Deployment data
├── tests/                   # Test suite
├── .github/workflows/       # CI/CD
└── docs/                    # Documentation
```

## Dependencies

### Core
- pyshacl>=0.25.0
- rdflib>=7.0.0

### Development
- pytest>=8.0.0
- ruff>=0.6.0
- mypy>=1.11.0

## Environment Variables

- `NKLLON_PROJECT_ROOT`: Override project root path

## CI/CD

GitHub Actions runs on push/PR:
- Linting (ruff)
- Type checking (mypy)
- Tests (pytest)
- Validation (actual topology validation)

## Error Handling

- Use custom exceptions from `nkllon.exceptions`
- Provide clear, actionable error messages
- Log at appropriate levels (DEBUG, INFO, ERROR)
- Exit codes: 0=success, 1=validation failed, 2+=errors

## Performance Considerations

- Graph loading: O(n) triples
- SHACL validation: O(n*m) where m = shapes
- Cache loaded graphs for multiple validations
- Use selective SHACL validation when possible
