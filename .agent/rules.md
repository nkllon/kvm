# Development Rules for NKLLON Hardware Topology System

## Code Quality Standards

1. **Type Safety**
   - All functions must have complete type hints
   - Use `mypy` for type checking
   - Avoid `Any` type unless absolutely necessary

2. **Documentation**
   - All public functions must have Google-style docstrings
   - Include Args, Returns, and Raises sections
   - Provide usage examples for complex functions

3. **Error Handling**
   - Use custom exceptions from `nkllon.exceptions`
   - Never use bare `except:` clauses
   - Provide context in error messages
   - Log errors at appropriate levels

4. **Testing**
   - Write tests before or alongside code (TDD encouraged)
   - Maintain >80% code coverage
   - Test both success and failure paths
   - Use descriptive test names: `test_<what>_<condition>_<expected>`

## RDF/OWL Guidelines

1. **Ontology Design**
   - Use clear, descriptive class and property names
   - Follow CamelCase for classes, camelCase for properties
   - Always provide rdfs:label and rdfs:comment
   - Define domain and range for all properties

2. **Turtle Syntax**
   - Use consistent indentation (2 spaces)
   - Group related triples together
   - Add comments to explain complex structures
   - Use prefixes to improve readability

3. **Data Integrity**
   - All instances must have explicit types
   - Use meaningful IDs (not random UUIDs)
   - Ensure all references are valid
   - Validate TTL syntax before committing

## SHACL Constraints

1. **Constraint Design**
   - One constraint per business rule
   - Use SPARQL-based constraints for complex logic
   - Provide clear, actionable error messages
   - Include rationale in comments

2. **Error Messages**
   - Start with severity: ERROR, WARNING, INFO
   - Describe what's wrong
   - Suggest how to fix it
   - Example: "ERROR: Smart Display requires HDMI-eARC path to PreAmp"

3. **Testing Constraints**
   - Test with valid data (should pass)
   - Test with invalid data (should fail)
   - Test edge cases
   - Verify error messages are helpful

## Git Workflow

1. **Commit Messages**
   - Use conventional commits format
   - Types: feat, fix, docs, test, refactor, chore
   - Example: "feat: add topology diff command"

2. **Branch Naming**
   - feature/description
   - fix/description
   - docs/description

3. **Pull Requests**
   - Fill out PR template completely
   - Ensure CI passes
   - Request review
   - Squash commits before merging

## Performance Guidelines

1. **Graph Operations**
   - Cache loaded graphs when possible
   - Use selective queries (avoid SELECT *)
   - Limit result sets appropriately
   - Profile slow operations

2. **Validation**
   - Run validation on changed files only in development
   - Use --quiet flag in CI/CD
   - Export reports for debugging

## Security Considerations

1. **Input Validation**
   - Validate all file paths
   - Sanitize SPARQL queries
   - Check file sizes before loading
   - Prevent directory traversal

2. **Dependencies**
   - Keep dependencies up to date
   - Review security advisories
   - Use `pip-audit` in CI

## CLI Design

1. **Command Structure**
   - Use subcommands for different operations
   - Provide --help for all commands
   - Use consistent flag names
   - Support both short (-v) and long (--verbose) flags

2. **Output**
   - Use colors/emojis for clarity
   - Provide progress indicators for long operations
   - Support --quiet and --verbose modes
   - Exit with appropriate codes

## When to Use Each Tool

1. **validate.py**: Checking if topology conforms to constraints
2. **query.py**: Exploring topology structure
3. **diff.py**: Comparing two topologies
4. **visualize.py**: Creating visual representations
5. **reporters.py**: Exporting validation results

## Common Patterns

### Loading Graphs
```python
from nkllon.config import default_config
from nkllon.validate import load_graph

config = default_config
graph = load_graph(config.ontology_path)
```

### Error Handling
```python
from nkllon.exceptions import ValidationError

try:
    result = validate_topology(...)
except ValidationError as e:
    logger.error(f"Validation failed: {e}")
    sys.exit(1)
```

### SPARQL Queries
```python
query = """
    PREFIX : <http://nkllon.com/sys#>
    SELECT ?device WHERE {
        ?device a :DeviceType .
    }
"""
results = list(graph.query(query))
```

## Anti-Patterns to Avoid

1. ❌ Hardcoding file paths
2. ❌ Using print() instead of logging
3. ❌ Ignoring type hints
4. ❌ Writing tests after code
5. ❌ Committing without running tests
6. ❌ Using bare except clauses
7. ❌ Modifying global state
8. ❌ Coupling unrelated components

## Code Review Checklist

- [ ] Type hints complete
- [ ] Docstrings present
- [ ] Tests added/updated
- [ ] Error handling appropriate
- [ ] Logging at correct levels
- [ ] No hardcoded values
- [ ] Documentation updated
- [ ] CI passes
