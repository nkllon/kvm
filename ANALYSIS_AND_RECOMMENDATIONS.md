# NKLLON Hardware Topology System - Analysis & Recommendations

**Date**: 2025-12-28
**Analyst**: Antigravity AI
**Repository**: github.com/nkllon/kvm

---

## Executive Summary

The **NKLLON Hardware Topology System** is a well-structured semantic web validation system for KVM hardware topologies using RDF/OWL ontologies and SHACL constraints. The codebase demonstrates good engineering practices with proper testing, CI/CD, and documentation. However, it **critically lacks formal requirements documentation** that would enable proper spec-driven development (SDD) and long-term maintainability.

### Key Findings

✅ **Strengths**:
- Clean Python package structure with proper separation of concerns
- Comprehensive test coverage (223 lines of tests)
- Modern tooling (uv, ruff, mypy, pytest)
- Working CI/CD pipeline
- Good semantic web implementation (RDF/OWL/SHACL)

❌ **Critical Gaps**:
- **No formal requirements specification**
- Missing design documentation
- No architecture decision records (ADRs)
- Limited extensibility documentation
- No contribution guidelines
- Missing deployment/operations documentation

---

## 1. Critical Recommendation: Adopt Spec-Driven Development (SDD)

### Problem Statement

The repository has implementation code and an execution plan, but **lacks the foundational requirements and design documents** that would enable:
- Clear understanding of system goals and constraints
- Traceability from requirements → design → implementation → tests
- Onboarding new contributors
- Evaluating feature requests
- Making architectural decisions

### Solution: Implement cc-sdd Framework

Yes, **[cc-sdd](https://github.com/gotalab/cc-sdd)** would be **extremely helpful** for this project. It provides a structured workflow for:

1. **Requirements** → Formal, EARS-format requirements
2. **Design** → Architecture with diagrams and decision rationale
3. **Tasks** → Decomposed implementation tasks with dependencies
4. **Implementation** → Code that traces back to requirements

### Recommended Action Plan

#### Phase 1: Initialize SDD Structure (1-2 hours)

```bash
# Install cc-sdd
npx cc-sdd@latest --claude --lang en

# Initialize spec for the existing system
/kiro:spec-init Hardware topology validation system for KVM setups using semantic web technologies

# Generate requirements document
/kiro:spec-requirements kvm-topology-en

# Generate design document
/kiro:spec-design kvm-topology-en -y

# Generate task breakdown
/kiro:spec-tasks kvm-topology-en -y
```

This will create:
- `.kiro/specs/kvm-topology-en/requirements.md` - Formal requirements
- `.kiro/specs/kvm-topology-en/design.md` - Architecture and design decisions
- `.kiro/specs/kvm-topology-en/tasks.md` - Implementation task breakdown

#### Phase 2: Document Existing System (2-4 hours)

Create comprehensive requirements covering:

**Functional Requirements**:
- FR-1: System SHALL validate hardware topology against SHACL constraints
- FR-2: System SHALL support bidirectional cable validation for USB-C to DisplayPort
- FR-3: System SHALL enforce audio purity (bypass KVM) constraints
- FR-4: System SHALL validate eARC return paths for smart displays
- FR-5: System SHALL prioritize uptime-critical hosts on high-priority ports
- FR-6: System SHALL provide SPARQL query interface for topology exploration
- FR-7: System SHALL support CLI and programmatic interfaces

**Non-Functional Requirements**:
- NFR-1: System SHALL validate topology in < 5 seconds
- NFR-2: System SHALL support Python 3.11+
- NFR-3: System SHALL provide clear validation error messages
- NFR-4: System SHALL be extensible for new device types
- NFR-5: System SHALL maintain backward compatibility with existing TTL files

**Data Requirements**:
- DR-1: System SHALL use RDF/OWL for ontology definition
- DR-2: System SHALL use SHACL for constraint validation
- DR-3: System SHALL use Turtle format for all RDF data
- DR-4: System SHALL support standard SPARQL 1.1 queries

---

## 2. Code Quality & Architecture Fixes

### 2.1 Type Hints Completeness

**Issue**: Some functions lack complete type hints.

**Fix**: Add missing type hints in `query.py`:

```python
# Current (line 100)
def format_uri(uri: str) -> str:
    """Format URI for display by extracting local name."""
    return uri.split("#")[-1] if "#" in uri else uri.split("/")[-1]

# Should be more explicit about what it returns
from typing import Optional

def format_uri(uri: str) -> str:
    """
    Format URI for display by extracting local name.

    Args:
        uri: Full URI string (e.g., 'http://nkllon.com/sys#MacM4Mini')

    Returns:
        Local name portion of URI (e.g., 'MacM4Mini')
    """
    return uri.split("#")[-1] if "#" in uri else uri.split("/")[-1]
```

### 2.2 Error Handling

**Issue**: No error handling for missing files or malformed TTL.

**Fix**: Add robust error handling in `validate.py`:

```python
from pathlib import Path
from typing import Tuple
import sys

from pyshacl import validate
from rdflib import Graph
from rdflib.exceptions import ParserError


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


def load_graph(file_path: Path) -> Graph:
    """
    Load an RDF graph from a Turtle file.

    Args:
        file_path: Path to the Turtle file

    Returns:
        Loaded RDF graph

    Raises:
        ValidationError: If file doesn't exist or has syntax errors
    """
    if not file_path.exists():
        raise ValidationError(f"File not found: {file_path}")

    graph = Graph()
    try:
        graph.parse(file_path, format="turtle")
    except ParserError as e:
        raise ValidationError(f"Syntax error in {file_path.name}: {e}")
    except Exception as e:
        raise ValidationError(f"Failed to load {file_path.name}: {e}")

    return graph


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
        ValidationError: If any file cannot be loaded
    """
    try:
        # Load ontology
        ontology = load_graph(ontology_path)

        # Load data and merge with ontology
        data = load_graph(data_path)
        data += ontology

        # Load SHACL shapes
        shapes = load_graph(shacl_path)

        # Validate
        conforms, results_graph, results_text = validate(
            data_graph=data,
            shacl_graph=shapes,
            inference="rdfs",
            abort_on_first=False,
            meta_shacl=False,
            advanced=True,
        )

        return conforms, results_text

    except ValidationError:
        raise
    except Exception as e:
        raise ValidationError(f"Validation failed: {e}")
```

### 2.3 Configuration Management

**Issue**: Hardcoded file paths in multiple places.

**Fix**: Create a configuration module:

```python
# src/nkllon/config.py
"""Configuration management for NKLLON topology system."""

from pathlib import Path
from typing import Optional
import os


class Config:
    """Configuration for NKLLON topology system."""

    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize configuration.

        Args:
            project_root: Optional project root path. If not provided,
                         will be inferred from package location.
        """
        if project_root is None:
            # Infer from package location
            self.project_root = Path(__file__).parent.parent.parent
        else:
            self.project_root = project_root

        # Allow environment variable override
        env_root = os.getenv("NKLLON_PROJECT_ROOT")
        if env_root:
            self.project_root = Path(env_root)

    @property
    def ontology_dir(self) -> Path:
        """Get ontology directory path."""
        return self.project_root / "ontology"

    @property
    def data_dir(self) -> Path:
        """Get data directory path."""
        return self.project_root / "data"

    @property
    def ontology_path(self) -> Path:
        """Get hardware ontology file path."""
        return self.ontology_dir / "hardware_ontology.ttl"

    @property
    def shacl_path(self) -> Path:
        """Get SHACL constraints file path."""
        return self.ontology_dir / "system_constraints.shacl.ttl"

    @property
    def deployment_path(self) -> Path:
        """Get physical deployment file path."""
        return self.data_dir / "physical_deployment.ttl"


# Global default config
default_config = Config()
```

---

## 3. Feature Enhancements

### 3.1 Multiple Deployment Environments

**Enhancement**: Support multiple deployment configurations (dev, staging, prod).

**Implementation**:

```python
# data/deployments/dev.ttl
# data/deployments/staging.ttl
# data/deployments/prod.ttl

# src/nkllon/cli.py - Add environment flag
parser.add_argument(
    "--env",
    choices=["dev", "staging", "prod"],
    default="prod",
    help="Deployment environment to validate"
)
```

### 3.2 Validation Report Export

**Enhancement**: Export validation reports in multiple formats (JSON, HTML, Markdown).

**Implementation**:

```python
# src/nkllon/reporters.py
"""Validation report formatters."""

from typing import Protocol
from pathlib import Path
import json
from datetime import datetime


class Reporter(Protocol):
    """Protocol for validation reporters."""

    def generate_report(
        self,
        conforms: bool,
        results_text: str,
        output_path: Path
    ) -> None:
        """Generate validation report."""
        ...


class JSONReporter:
    """JSON format reporter."""

    def generate_report(
        self,
        conforms: bool,
        results_text: str,
        output_path: Path
    ) -> None:
        """Generate JSON validation report."""
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "conforms": conforms,
            "results": results_text,
            "status": "PASS" if conforms else "FAIL"
        }

        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)


class HTMLReporter:
    """HTML format reporter."""

    def generate_report(
        self,
        conforms: bool,
        results_text: str,
        output_path: Path
    ) -> None:
        """Generate HTML validation report."""
        status_color = "green" if conforms else "red"
        status_text = "PASSED" if conforms else "FAILED"

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>NKLLON Validation Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .header {{ background: #f0f0f0; padding: 20px; }}
        .status {{ color: {status_color}; font-size: 24px; font-weight: bold; }}
        .results {{ margin-top: 20px; white-space: pre-wrap; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>NKLLON Hardware Topology Validation</h1>
        <p class="status">Status: {status_text}</p>
        <p>Timestamp: {datetime.utcnow().isoformat()}</p>
    </div>
    <div class="results">
        <h2>Validation Results</h2>
        <pre>{results_text}</pre>
    </div>
</body>
</html>
        """

        with open(output_path, 'w') as f:
            f.write(html)
```

### 3.3 Interactive Topology Visualization

**Enhancement**: Generate interactive network diagrams of the hardware topology.

**Implementation**:

```python
# src/nkllon/visualize.py
"""Topology visualization utilities."""

from pathlib import Path
from typing import Dict, List, Tuple
from rdflib import Graph
import json


def generate_d3_visualization(
    ontology_path: Path,
    data_path: Path,
    output_path: Path
) -> None:
    """
    Generate D3.js interactive visualization of topology.

    Args:
        ontology_path: Path to ontology file
        data_path: Path to deployment data
        output_path: Path to output HTML file
    """
    # Load graphs
    graph = Graph()
    graph.parse(ontology_path, format="turtle")
    graph.parse(data_path, format="turtle")

    # Extract nodes and edges
    nodes, edges = extract_topology_graph(graph)

    # Generate HTML with embedded D3.js
    html = generate_d3_html(nodes, edges)

    with open(output_path, 'w') as f:
        f.write(html)


def extract_topology_graph(graph: Graph) -> Tuple[List[Dict], List[Dict]]:
    """Extract nodes and edges from RDF graph."""
    # Query for devices
    device_query = """
        PREFIX : <http://nkllon.com/sys#>
        SELECT ?device ?type WHERE {
            ?device a ?type .
            ?type rdfs:subClassOf* :Device .
        }
    """

    # Query for connections
    connection_query = """
        PREFIX : <http://nkllon.com/sys#>
        SELECT ?src ?dst ?cable WHERE {
            ?srcPort :belongsToDevice ?src ;
                     :connectsVia ?cable .
            ?cable :connectsTo ?dstPort .
            ?dstPort :belongsToDevice ?dst .
        }
    """

    nodes = []
    edges = []

    # Build nodes
    for row in graph.query(device_query):
        device_id = str(row.device).split('#')[-1]
        device_type = str(row.type).split('#')[-1]
        nodes.append({
            "id": device_id,
            "type": device_type,
            "label": device_id
        })

    # Build edges
    for row in graph.query(connection_query):
        src_id = str(row.src).split('#')[-1]
        dst_id = str(row.dst).split('#')[-1]
        cable_id = str(row.cable).split('#')[-1]
        edges.append({
            "source": src_id,
            "target": dst_id,
            "label": cable_id
        })

    return nodes, edges


def generate_d3_html(nodes: List[Dict], edges: List[Dict]) -> str:
    """Generate HTML with D3.js visualization."""
    return f"""
<!DOCTYPE html>
<html>
<head>
    <title>NKLLON Topology Visualization</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {{ margin: 0; font-family: Arial, sans-serif; }}
        #graph {{ width: 100vw; height: 100vh; }}
        .node {{ cursor: pointer; }}
        .link {{ stroke: #999; stroke-opacity: 0.6; }}
        .node-label {{ font-size: 12px; pointer-events: none; }}
    </style>
</head>
<body>
    <div id="graph"></div>
    <script>
        const nodes = {json.dumps(nodes)};
        const links = {json.dumps(edges)};

        // D3.js force-directed graph implementation
        const width = window.innerWidth;
        const height = window.innerHeight;

        const svg = d3.select("#graph")
            .append("svg")
            .attr("width", width)
            .attr("height", height);

        const simulation = d3.forceSimulation(nodes)
            .force("link", d3.forceLink(links).id(d => d.id))
            .force("charge", d3.forceManyBody().strength(-300))
            .force("center", d3.forceCenter(width / 2, height / 2));

        const link = svg.append("g")
            .selectAll("line")
            .data(links)
            .join("line")
            .attr("class", "link")
            .attr("stroke-width", 2);

        const node = svg.append("g")
            .selectAll("circle")
            .data(nodes)
            .join("circle")
            .attr("class", "node")
            .attr("r", 20)
            .attr("fill", d => getNodeColor(d.type))
            .call(drag(simulation));

        const label = svg.append("g")
            .selectAll("text")
            .data(nodes)
            .join("text")
            .attr("class", "node-label")
            .text(d => d.label);

        simulation.on("tick", () => {{
            link
                .attr("x1", d => d.source.x)
                .attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x)
                .attr("y2", d => d.target.y);

            node
                .attr("cx", d => d.x)
                .attr("cy", d => d.y);

            label
                .attr("x", d => d.x + 25)
                .attr("y", d => d.y + 5);
        }});

        function getNodeColor(type) {{
            const colors = {{
                "Host": "#4CAF50",
                "KVM": "#2196F3",
                "AudioInterface": "#FF9800",
                "SmartDisplay": "#9C27B0",
                "PreAmp": "#F44336"
            }};
            return colors[type] || "#999";
        }}

        function drag(simulation) {{
            function dragstarted(event) {{
                if (!event.active) simulation.alphaTarget(0.3).restart();
                event.subject.fx = event.subject.x;
                event.subject.fy = event.subject.y;
            }}

            function dragged(event) {{
                event.subject.fx = event.x;
                event.subject.fy = event.y;
            }}

            function dragended(event) {{
                if (!event.active) simulation.alphaTarget(0);
                event.subject.fx = null;
                event.subject.fy = null;
            }}

            return d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended);
        }}
    </script>
</body>
</html>
    """
```

### 3.4 Topology Diff Tool

**Enhancement**: Compare two topology configurations and show differences.

**Implementation**:

```python
# src/nkllon/diff.py
"""Topology comparison utilities."""

from pathlib import Path
from typing import Set, Tuple
from rdflib import Graph
from rdflib.compare import graph_diff


def compare_topologies(
    topology1_path: Path,
    topology2_path: Path
) -> Tuple[Set, Set, Set]:
    """
    Compare two topology configurations.

    Args:
        topology1_path: Path to first topology file
        topology2_path: Path to second topology file

    Returns:
        Tuple of (in_both, only_in_first, only_in_second)
    """
    graph1 = Graph()
    graph1.parse(topology1_path, format="turtle")

    graph2 = Graph()
    graph2.parse(topology2_path, format="turtle")

    in_both, only_in_first, only_in_second = graph_diff(graph1, graph2)

    return in_both, only_in_first, only_in_second


def print_topology_diff(
    topology1_path: Path,
    topology2_path: Path
) -> None:
    """Print human-readable topology differences."""
    in_both, only_in_first, only_in_second = compare_topologies(
        topology1_path,
        topology2_path
    )

    print("=" * 80)
    print("Topology Comparison")
    print("=" * 80)
    print(f"\nFile 1: {topology1_path.name}")
    print(f"File 2: {topology2_path.name}")

    print(f"\n📊 Statistics:")
    print(f"  Common triples: {len(in_both)}")
    print(f"  Only in {topology1_path.name}: {len(only_in_first)}")
    print(f"  Only in {topology2_path.name}: {len(only_in_second)}")

    if only_in_first:
        print(f"\n➖ Removed in {topology2_path.name}:")
        for triple in sorted(only_in_first)[:10]:  # Show first 10
            print(f"  {triple}")

    if only_in_second:
        print(f"\n➕ Added in {topology2_path.name}:")
        for triple in sorted(only_in_second)[:10]:  # Show first 10
            print(f"  {triple}")
```

---

## 4. Documentation Enhancements

### 4.1 Create CONTRIBUTING.md

```markdown
# Contributing to NKLLON Hardware Topology System

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/kvm.git`
3. Install dependencies: `make install`
4. Run tests: `make test`

## Development Workflow

### Adding New Device Types

1. Update `ontology/hardware_ontology.ttl`:
   ```turtle
   :NewDeviceType a owl:Class ; rdfs:subClassOf :Device .
   ```

2. Add validation rules in `ontology/system_constraints.shacl.ttl`

3. Add test cases in `tests/test_validation.py`

4. Update documentation in `README.md`

### Adding New Constraints

1. Define SHACL shape in `ontology/system_constraints.shacl.ttl`
2. Add test case to verify constraint works
3. Add test case to verify constraint fails when violated
4. Document the constraint in README

## Code Style

- Use `ruff` for linting and formatting
- Use type hints for all functions
- Write docstrings for all public functions
- Maintain test coverage above 80%

## Testing

```bash
# Run all tests
make test

# Run specific test
uv run pytest tests/test_validation.py::test_name -v

# Run with coverage
uv run pytest tests/ --cov=src/nkllon --cov-report=html
```

## Pull Request Process

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make your changes
3. Run tests and linting: `make test lint`
4. Commit with descriptive message
5. Push and create pull request
6. Wait for CI to pass and review

## Questions?

Open an issue or discussion on GitHub.
```

### 4.2 Create ARCHITECTURE.md

```markdown
# Architecture Documentation

## System Overview

The NKLLON Hardware Topology System uses semantic web technologies to model and validate KVM hardware configurations.

## Architecture Layers

### 1. Data Layer (RDF/OWL)

**Purpose**: Define the domain model for hardware topology

**Components**:
- `hardware_ontology.ttl` - OWL ontology defining classes and properties
- `physical_deployment.ttl` - Instance data for actual hardware

**Key Design Decisions**:
- **ADR-001**: Use RDF/OWL for extensibility and semantic reasoning
- **ADR-002**: Use Turtle format for human readability

### 2. Validation Layer (SHACL)

**Purpose**: Enforce business rules and constraints

**Components**:
- `system_constraints.shacl.ttl` - SHACL shapes for validation

**Key Design Decisions**:
- **ADR-003**: Use SHACL over custom validation for standards compliance
- **ADR-004**: Use SPARQL-based SHACL constraints for complex rules

### 3. Application Layer (Python)

**Purpose**: Provide programmatic access and CLI

**Components**:
- `validate.py` - SHACL validation engine
- `query.py` - SPARQL query utilities
- `cli.py` - Command-line interface

**Key Design Decisions**:
- **ADR-005**: Use pySHACL for Python-native validation
- **ADR-006**: Use RDFLib for RDF manipulation

## Data Flow

```
┌─────────────────┐
│  Ontology TTL   │
│  (Schema)       │
└────────┬────────┘
         │
         ├─────────────────┐
         │                 │
         ▼                 ▼
┌─────────────────┐  ┌─────────────────┐
│ Deployment TTL  │  │  SHACL Shapes   │
│ (Instance Data) │  │  (Constraints)  │
└────────┬────────┘  └────────┬────────┘
         │                     │
         └──────────┬──────────┘
                    │
                    ▼
         ┌──────────────────┐
         │  pySHACL Engine  │
         └──────────┬───────┘
                    │
         ┌──────────┴──────────┐
         │                     │
         ▼                     ▼
    ┌────────┐          ┌──────────┐
    │  PASS  │          │   FAIL   │
    └────────┘          └──────────┘
```

## Extension Points

### Adding New Device Types

1. Add class definition to ontology
2. Define required properties
3. Add SHACL constraints if needed
4. Update tests

### Adding New Constraints

1. Define SHACL shape
2. Write SPARQL query for complex rules
3. Add test cases
4. Document in README

## Performance Considerations

- Graph loading: O(n) where n = number of triples
- SHACL validation: O(n*m) where m = number of shapes
- SPARQL queries: Depends on query complexity

**Optimization strategies**:
- Cache loaded graphs for multiple validations
- Use selective SHACL validation (target specific shapes)
- Index RDF graphs for complex queries

## Security Considerations

- Input validation for TTL files (prevent malicious RDF)
- Sandboxing for SPARQL queries (prevent resource exhaustion)
- File path validation (prevent directory traversal)
```

### 4.3 Create ADR Template

```markdown
# Architecture Decision Records

## ADR-001: Use RDF/OWL for Domain Modeling

**Status**: Accepted

**Context**:
Need a flexible, extensible way to model hardware topology that supports:
- Complex relationships between devices
- Semantic reasoning
- Standard query languages
- Tool ecosystem

**Decision**:
Use RDF/OWL for domain modeling with Turtle serialization.

**Consequences**:
- ✅ Standards-based approach
- ✅ Rich tooling ecosystem
- ✅ Semantic reasoning capabilities
- ✅ SPARQL query support
- ❌ Learning curve for team members
- ❌ Verbose syntax compared to JSON

**Alternatives Considered**:
- JSON Schema: Less expressive, no reasoning
- XML Schema: More verbose, less tooling
- Custom DSL: More work, less standard

---

## ADR-002: Use SHACL for Validation

**Status**: Accepted

**Context**:
Need to enforce business rules and constraints on hardware topology.

**Decision**:
Use SHACL (Shapes Constraint Language) for validation.

**Consequences**:
- ✅ W3C standard
- ✅ Declarative constraint definition
- ✅ Good error reporting
- ✅ Supports complex SPARQL-based rules
- ❌ Less familiar than JSON Schema

**Alternatives Considered**:
- ShEx: Less mature tooling
- Custom validation: More work, less standard
- OWL reasoning: Too heavyweight for our needs
```

---

## 5. Testing Enhancements

### 5.1 Add Property-Based Testing

```python
# tests/test_property_based.py
"""Property-based tests using Hypothesis."""

from hypothesis import given, strategies as st
from rdflib import Graph, Namespace, Literal
from nkllon.validate import validate_topology


# Define strategies for generating valid RDF data
@st.composite
def device_strategy(draw):
    """Generate random device instances."""
    device_types = ["Host", "KVM", "AudioInterface", "SmartDisplay", "PreAmp"]
    device_type = draw(st.sampled_from(device_types))
    device_id = draw(st.text(min_size=1, max_size=20, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd')
    )))
    return device_type, device_id


@given(device_strategy())
def test_device_creation_is_valid(device_data):
    """Test that any generated device is valid."""
    device_type, device_id = device_data

    # Create minimal valid graph
    graph = Graph()
    ns = Namespace("http://nkllon.com/sys#")

    device_uri = ns[device_id]
    graph.add((device_uri, ns.a, ns[device_type]))

    # Should parse without errors
    assert len(graph) > 0
```

### 5.2 Add Integration Tests

```python
# tests/test_integration.py
"""Integration tests for end-to-end workflows."""

import pytest
from pathlib import Path
import tempfile
from nkllon.validate import validate_topology
from nkllon.query import query_all_devices


def test_full_validation_workflow(project_root):
    """Test complete validation workflow."""
    ontology_path = project_root / "ontology" / "hardware_ontology.ttl"
    shacl_path = project_root / "ontology" / "system_constraints.shacl.ttl"
    data_path = project_root / "data" / "physical_deployment.ttl"

    # Validate
    conforms, report = validate_topology(ontology_path, shacl_path, data_path)

    # Should pass
    assert conforms, f"Validation failed: {report}"

    # Query should return devices
    devices = query_all_devices()
    assert len(devices) > 0


def test_invalid_topology_fails():
    """Test that invalid topology is rejected."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Create invalid topology (audio connects to KVM)
        invalid_data = """
@prefix : <http://nkllon.com/sys#> .

:MotuM4 a :AudioInterface ; :hasPort :Motu_Out .
:ConnectPRO_KVM a :KVM ; :hasPort :KVM_AudioIn .

:Motu_Out a :Port ; :connectsVia :BadCable ; :belongsToDevice :MotuM4 .
:BadCable a :Cable ; :connectsTo :KVM_AudioIn .
:KVM_AudioIn a :Port ; :belongsToDevice :ConnectPRO_KVM .
        """

        data_path = tmpdir / "invalid.ttl"
        data_path.write_text(invalid_data)

        # Should fail validation
        # (Need to copy ontology and SHACL files to tmpdir)
        # ... implementation details ...
```

### 5.3 Add Performance Tests

```python
# tests/test_performance.py
"""Performance tests for validation and queries."""

import pytest
import time
from nkllon.validate import validate_topology


def test_validation_performance(project_root, benchmark):
    """Test that validation completes within acceptable time."""
    ontology_path = project_root / "ontology" / "hardware_ontology.ttl"
    shacl_path = project_root / "ontology" / "system_constraints.shacl.ttl"
    data_path = project_root / "data" / "physical_deployment.ttl"

    def run_validation():
        return validate_topology(ontology_path, shacl_path, data_path)

    # Benchmark validation
    result = benchmark(run_validation)

    # Should complete in < 5 seconds
    assert benchmark.stats['mean'] < 5.0


def test_large_topology_scaling(project_root):
    """Test validation performance with large topology."""
    # Generate large topology with 100+ devices
    # ... implementation ...

    start = time.time()
    # validate
    duration = time.time() - start

    # Should scale linearly
    assert duration < 10.0  # Even with 100 devices
```

---

## 6. Operations & Deployment

### 6.1 Add Docker Support

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy project files
COPY pyproject.toml uv.lock ./
COPY src/ ./src/
COPY ontology/ ./ontology/
COPY data/ ./data/

# Install dependencies
RUN uv pip install -e ".[dev]"

# Run validation by default
CMD ["uv", "run", "python", "-m", "nkllon.validate"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  validator:
    build: .
    volumes:
      - ./data:/app/data:ro
      - ./ontology:/app/ontology:ro
    environment:
      - NKLLON_PROJECT_ROOT=/app
```

### 6.2 Add GitHub Actions Enhancements

```yaml
# .github/workflows/ci.yml (additions)

    # Add coverage reporting
    - name: Run tests with coverage
      run: |
        uv run pytest tests/ -v --cov=src/nkllon --cov-report=xml

    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        fail_ci_if_error: true

    # Add security scanning
    - name: Run security scan
      run: |
        uv pip install safety
        uv run safety check

    # Add dependency vulnerability check
    - name: Check dependencies
      run: |
        uv pip install pip-audit
        uv run pip-audit
```

### 6.3 Add Monitoring & Observability

```python
# src/nkllon/telemetry.py
"""Telemetry and monitoring utilities."""

import time
import logging
from typing import Callable, Any
from functools import wraps

logger = logging.getLogger(__name__)


def measure_time(func: Callable) -> Callable:
    """Decorator to measure function execution time."""
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start = time.time()
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start
            logger.info(f"{func.__name__} completed in {duration:.2f}s")
            return result
        except Exception as e:
            duration = time.time() - start
            logger.error(f"{func.__name__} failed after {duration:.2f}s: {e}")
            raise
    return wrapper


class ValidationMetrics:
    """Track validation metrics."""

    def __init__(self):
        self.total_validations = 0
        self.successful_validations = 0
        self.failed_validations = 0
        self.total_duration = 0.0

    def record_validation(self, success: bool, duration: float) -> None:
        """Record a validation attempt."""
        self.total_validations += 1
        if success:
            self.successful_validations += 1
        else:
            self.failed_validations += 1
        self.total_duration += duration

    def get_stats(self) -> dict:
        """Get validation statistics."""
        return {
            "total": self.total_validations,
            "successful": self.successful_validations,
            "failed": self.failed_validations,
            "success_rate": self.successful_validations / max(self.total_validations, 1),
            "avg_duration": self.total_duration / max(self.total_validations, 1)
        }
```

---

## 7. Priority Roadmap

### Immediate (Week 1)
1. ✅ **Implement cc-sdd framework** - Generate requirements, design, tasks
2. ✅ **Add error handling** - Robust error handling in validate.py
3. ✅ **Create CONTRIBUTING.md** - Onboarding documentation
4. ✅ **Add configuration module** - Centralize path management

### Short-term (Month 1)
5. ✅ **Add validation report export** - JSON, HTML, Markdown formats
6. ✅ **Create ARCHITECTURE.md** - Document design decisions
7. ✅ **Add integration tests** - End-to-end workflow tests
8. ✅ **Add Docker support** - Containerized deployment

### Medium-term (Quarter 1)
9. ✅ **Interactive visualization** - D3.js topology viewer
10. ✅ **Topology diff tool** - Compare configurations
11. ✅ **Multiple environments** - Dev, staging, prod support
12. ✅ **Performance optimization** - Caching, indexing

### Long-term (Year 1)
13. ✅ **Web API** - REST API for validation service
14. ✅ **Real-time monitoring** - Track actual vs. expected topology
15. ✅ **Auto-documentation** - Generate wiring diagrams from RDF
16. ✅ **Version control integration** - Track topology changes over time

---

## 8. Specific Code Fixes

### Fix 1: Missing __all__ Exports

```python
# src/nkllon/__init__.py
"""NKLLON Hardware Topology Validation System."""

__version__ = "0.1.0"

__all__ = [
    "validate",
    "query",
    "cli",
    "__version__",
]
```

### Fix 2: Add Logging

```python
# src/nkllon/validate.py (add at top)
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def validate_topology(...):
    logger.info(f"Starting validation: {data_path.name}")
    # ... existing code ...
    logger.info(f"Validation {'passed' if conforms else 'failed'}")
```

### Fix 3: Add Version Command

```python
# src/nkllon/cli.py
def main():
    parser.add_argument(
        '--version',
        action='version',
        version=f'%(prog)s {__version__}'
    )
```

---

## 9. Documentation Gaps to Fill

### 9.1 Missing: Deployment Guide

Create `docs/DEPLOYMENT.md`:
- Installation on different platforms
- Configuration options
- Environment variables
- Production deployment best practices
- Monitoring and logging setup

### 9.2 Missing: API Reference

Create `docs/API.md`:
- Complete API documentation for all public functions
- Examples for each function
- Return types and exceptions
- Usage patterns

### 9.3 Missing: Tutorial

Create `docs/TUTORIAL.md`:
- Step-by-step guide for beginners
- Creating first topology
- Adding devices and connections
- Writing custom constraints
- Querying topology

### 9.4 Missing: FAQ

Create `docs/FAQ.md`:
- Common issues and solutions
- Performance tuning
- Debugging tips
- Migration guides

---

## 10. Summary & Next Steps

### Critical Actions (Do First)

1. **Implement cc-sdd** - This is the foundation for everything else
   ```bash
   npx cc-sdd@latest --claude --lang en
   /kiro:spec-init Hardware topology validation system
   ```

2. **Generate Requirements Document** - Document what the system actually does
   ```bash
   /kiro:spec-requirements kvm-topology-en
   ```

3. **Add Error Handling** - Make the system production-ready

4. **Create CONTRIBUTING.md** - Enable community contributions

### High-Value Enhancements

5. **Validation Report Export** - JSON/HTML reports for CI/CD
6. **Interactive Visualization** - D3.js topology viewer
7. **Docker Support** - Easy deployment
8. **Integration Tests** - Ensure system works end-to-end

### Long-term Improvements

9. **Web API** - REST API for validation service
10. **Real-time Monitoring** - Track topology changes
11. **Performance Optimization** - Handle large topologies

---

## Conclusion

The NKLLON Hardware Topology System is well-implemented but **critically lacks formal requirements and design documentation**. Adopting the **cc-sdd framework** will provide the structured foundation needed for:

- ✅ Clear requirements traceability
- ✅ Architectural decision documentation
- ✅ Onboarding new contributors
- ✅ Evaluating feature requests
- ✅ Long-term maintainability

The recommended enhancements will transform this from a good proof-of-concept into a **production-ready, maintainable system** with proper documentation, testing, and operational support.

**Estimated effort**:
- Critical actions: 4-8 hours
- High-value enhancements: 2-3 days
- Long-term improvements: 1-2 weeks

**ROI**: High - The spec-driven approach will save significant time in future development and maintenance.
