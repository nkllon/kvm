# NKLLON Hardware Topology System

[![CI](https://github.com/nkllon/kvm/actions/workflows/ci.yml/badge.svg)](https://github.com/nkllon/kvm/actions/workflows/ci.yml)

A semantic web validation system for KVM hardware topologies using RDF/OWL ontologies and SHACL constraints.

**Repository**: [github.com/nkllon/kvm](https://github.com/nkllon/kvm)

## Overview

This project models and validates hardware connections in a KVM (Keyboard, Video, Mouse) setup using semantic web technologies. It enforces critical constraints such as:

- **Bidirectional cable requirements** for Mac M4 Mini USB-C to DisplayPort connections
- **Audio purity** ensuring audio interfaces bypass KVMs (no digital switching)
- **Active adapter enforcement** for legacy Mini-DisplayPort connections
- **Uptime-critical port prioritization** for production Cloudflare hosts

## Project Structure

```
nkllon-topology/
├── src/nkllon/          # Python package
│   ├── validate.py      # pySHACL validation logic
│   ├── query.py         # SPARQL query utilities
│   └── cli.py           # Command-line interface
├── ontology/            # RDF/OWL definitions
│   ├── hardware_ontology.ttl           # Device classes and properties
│   └── system_constraints.shacl.ttl    # SHACL validation rules
├── data/                # Deployment data
│   └── physical_deployment.ttl         # Actual hardware topology
├── tests/               # Test suite
└── Makefile             # Common development tasks
```

## Installation

### Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) package manager

### Install Dependencies

```bash
# Using uv
uv pip install -e ".[dev]"

# Or using make
make install
```

## Usage

### Validate Hardware Topology

Run SHACL validation to ensure your hardware deployment conforms to all constraints:

```bash
# Using make
make validate

# Using CLI
uv run nkllon validate

# Using Python module
uv run python -m nkllon.validate

# With environment selection
uv run nkllon validate --env prod

# With verbose logging
uv run nkllon validate --verbose

# Export report to HTML
uv run nkllon validate --export report.html --format html

# Export report to JSON
uv run nkllon validate --export report.json --format json
```

**Example output:**
```
================================================================================
NKLLON Hardware Topology Validation
================================================================================

Environment: prod
Ontology:    hardware_ontology.ttl
SHACL:       system_constraints.shacl.ttl
Data:        physical_deployment.ttl

--------------------------------------------------------------------------------

✅ VALIDATION PASSED

All SHACL constraints satisfied:
  ✓ Rule 1: eARC return path (SmartDisplay to PreAmp)
  ✓ Rule 2: Audio interfaces bypass KVMs (can connect to PreAmp)
  ✓ Rule 3: Bidirectional cables (USB-C to DisplayPort)
  ✓ Rule 4: Production uptime-critical ports

================================================================================
```

### Query Topology

Run SPARQL queries to explore your hardware topology:

```bash
# Using make
make query

# Using CLI
uv run nkllon query

# Using Python module
uv run python -m nkllon.query
```

**Example queries:**
- Find all bidirectional cables and their connections
- List audio interface connections
- Check uptime-critical host configurations
- Display all devices by type

### Visualize Topology

Generate an interactive D3.js visualization of your hardware topology:

```bash
# Using make
make visualize

# Using CLI
uv run nkllon visualize --output topology.html

# For specific environment
uv run nkllon visualize --env staging --output staging_topology.html
```

This creates an interactive HTML file with:
- Force-directed graph layout
- Color-coded device types
- Zoom and pan controls
- Drag-and-drop nodes
- Connection labels

### Compare Topologies

Compare two topology configurations to see what changed:

```bash
# Compare two files
uv run nkllon diff data/old.ttl data/new.ttl

# Show only device-level changes
uv run nkllon diff data/old.ttl data/new.ttl --devices-only

# Using make (requires FILE1 and FILE2 variables)
make diff FILE1=data/old.ttl FILE2=data/new.ttl
```

### Run Tests

```bash
# Using make
make test

# Using pytest directly
uv run pytest tests/ -v

# With coverage report
make coverage
```

### Lint and Format

```bash
# Run linter
make lint

# Auto-format code
make format
```

### Docker Support

Run validation in a Docker container:

```bash
# Build image
make docker-build

# Run validation
make docker-run

# Use docker-compose for full stack
make docker-compose-up
```


## Ontology Structure

### Device Classes

- `Device` - Base class for all hardware
  - `Host` - Computer hosts (Mac M4 Mini, Ubuntu server)
  - `KVM` - KVM switches (ConnectPRO)
  - `AudioInterface` - Audio devices (Motu M4)

### Connection Model

```
Device → hasPort → Port → connectsVia → Cable → connectsTo → Port → belongsToDevice → Device
```

### Properties

- **Physical**: `physicalForm` (USB-C, DisplayPort, etc.)
- **Operational**: `isBidirectional`, `isActive`, `isEncrypted`
- **Priority**: `portPriority`, `isUptimeCritical`

## SHACL Validation Rules

### Rule 1: M4 Mac Mini Bidirectional Cables
Cables connecting Mac M4 (USB-C) to KVM (DisplayPort) **must** be bidirectional.

**Rationale**: USB-C to DisplayPort connections require bidirectional signal flow for proper operation.

### Rule 2: Audio Purity
Audio interfaces **must** bypass KVMs (no digital switching).

**Rationale**: Professional audio requires direct connections to avoid latency and signal degradation.

### Rule 3: Legacy Active Adapters
Legacy Mini-DisplayPort connections **must** use active adapters.

**Rationale**: Passive adapters cause signal loss on legacy ports.

### Rule 4: Production Uptime Priority
Production Cloudflare hosts **must** connect to high-priority KVM ports.

**Rationale**: Critical infrastructure requires prioritized connections for reliability.

## Example SPARQL Queries

### Find Bidirectional Cables

```sparql
PREFIX : <http://nkllon.com/sys#>

SELECT ?cable ?srcDevice ?dstDevice WHERE {
    ?cable a :Cable ;
           :isBidirectional true .
    ?srcPort :connectsVia ?cable .
    ?cable :connectsTo ?dstPort .
    ?srcPort :belongsToDevice ?srcDevice .
    ?dstPort :belongsToDevice ?dstDevice .
}
```

### Verify Audio Isolation

```sparql
PREFIX : <http://nkllon.com/sys#>

SELECT ?audioDevice ?connectedDevice WHERE {
    ?audioDevice a :AudioInterface ;
                 :hasPort ?port .
    ?port :connectsVia ?cable .
    ?cable :connectsTo ?otherPort .
    ?otherPort :belongsToDevice ?connectedDevice .
    ?connectedDevice a :KVM .
}
# Should return empty (Rule 2 compliance)
```

### Check Uptime-Critical Hosts

```sparql
PREFIX : <http://nkllon.com/sys#>

SELECT ?host ?kvmPort ?priority WHERE {
    ?host :isUptimeCritical true ;
          :hasPort ?hostPort .
    ?hostPort :connectsVia ?cable .
    ?cable :connectsTo ?kvmPort .
    ?kvmPort :portPriority ?priority .
}
```

## Development

### Adding New Devices

1. Define device in `data/physical_deployment.ttl`:
```turtle
:NewDevice a :Host ;
    :hasPort :NewDevice_Port1 .
```

2. Define connections:
```turtle
:NewDevice_Port1 a :Port ;
    :physicalForm "HDMI" ;
    :connectsVia :NewCable ;
    :belongsToDevice :NewDevice .
```

3. Run validation:
```bash
make validate
```

### Adding New Constraints

1. Add SHACL shape to `ontology/system_constraints.shacl.ttl`
2. Add corresponding test to `tests/test_validation.py`
3. Run tests: `make test`

## Technologies

- **[RDFLib](https://rdflib.readthedocs.io/)** - RDF graph manipulation
- **[pySHACL](https://github.com/RDFLib/pySHACL)** - SHACL constraint validation
- **[uv](https://github.com/astral-sh/uv)** - Fast Python package manager
- **[pytest](https://pytest.org/)** - Testing framework
- **[ruff](https://github.com/astral-sh/ruff)** - Linting and formatting

## License

MIT

## References

- [RDF Primer](https://www.w3.org/TR/rdf11-primer/)
- [SHACL Specification](https://www.w3.org/TR/shacl/)
- [SPARQL Query Language](https://www.w3.org/TR/sparql11-query/)
