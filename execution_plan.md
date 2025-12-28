# NKLLON Hardware Topology Execution Plan

## Overview
This plan outlines the steps to execute the hardware topology semantic web system, including improvements and validation.

## Prerequisites
- **Apache Jena** or **RDFLib** (Python) for RDF processing
- **pySHACL** (Python) or **Apache Jena SHACL** for validation
- Basic understanding of RDF/Turtle syntax

## Execution Steps

### Phase 1: Setup and File Generation
```bash
# Execute the original script
chmod +x script.sh
./script.sh
```

**Expected Output:**
- Directory: `nkllon_final_topology/`
- Files: `hardware_ontology.ttl`, `system_constraints.shacl.ttl`, `physical_deployment.ttl`
- Archive: `nkllon_final_topology.zip`

### Phase 2: Fix Ontology Issues

#### Issue 1: Add Missing Property Definition
Add to `hardware_ontology.ttl`:
```turtle
:belongsToDevice a owl:ObjectProperty ; 
    rdfs:domain :Port ; 
    rdfs:range :Device .
```

#### Issue 2: Fix Audio Chain Connection
Update in `physical_deployment.ttl`:
```turtle
# Before:
:Direct_USB a :Cable ; :connectsTo :MacM4Mini .

# After:
:Direct_USB a :Cable ; :connectsTo :M4_AudioIn .
:M4_AudioIn a :Port ; :belongsToDevice :MacM4Mini .
```

### Phase 3: Validation

#### Option A: Using Python (pySHACL)
```bash
pip install pyshacl rdflib

python3 << 'PYEOF'
from pyshacl import validate
from rdflib import Graph

# Load ontology and data
ontology = Graph()
ontology.parse("hardware_ontology.ttl", format="turtle")

data = Graph()
data.parse("physical_deployment.ttl", format="turtle")
data += ontology  # Merge ontology into data

# Load SHACL shapes
shapes = Graph()
shapes.parse("system_constraints.shacl.ttl", format="turtle")

# Validate
conforms, results_graph, results_text = validate(
    data_graph=data,
    shacl_graph=shapes,
    inference='rdfs',
    abort_on_first=False
)

print(f"Validation Result: {'PASS' if conforms else 'FAIL'}")
print(results_text)
PYEOF
```

#### Option B: Using Apache Jena
```bash
# Download Jena (if not installed)
wget https://dlcdn.apache.org/jena/binaries/apache-jena-4.10.0.tar.gz
tar -xzf apache-jena-4.10.0.tar.gz

# Merge files
apache-jena-4.10.0/bin/riot --output=turtle \
    hardware_ontology.ttl physical_deployment.ttl > merged.ttl

# Validate with SHACL
apache-jena-4.10.0/bin/shacl validate \
    --shapes=system_constraints.shacl.ttl \
    --data=merged.ttl
```

### Phase 4: Query and Exploration

#### Example SPARQL Queries

**Query 1: Find all bidirectional cables**
```sparql
PREFIX : <http://nkllon.com/sys#>

SELECT ?cable ?src ?dst WHERE {
    ?cable a :Cable ;
           :isBidirectional true .
    ?srcPort :connectsVia ?cable .
    ?cable :connectsTo ?dstPort .
    ?srcPort :belongsToDevice ?src .
    ?dstPort :belongsToDevice ?dst .
}
```

**Query 2: Verify audio isolation**
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

**Query 3: Check uptime-critical connections**
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

### Phase 5: Visualization (Optional)

#### Generate GraphViz Diagram
```python
from rdflib import Graph
from rdflib.extras.external_graph_libs import rdflib_to_networkx_graph
import networkx as nx
import matplotlib.pyplot as plt

g = Graph()
g.parse("merged.ttl", format="turtle")

# Convert to NetworkX
G = rdflib_to_networkx_graph(g)

# Draw
pos = nx.spring_layout(G)
nx.draw(G, pos, with_labels=True, node_color='lightblue', 
        node_size=500, font_size=8, arrows=True)
plt.savefig("topology_diagram.png", dpi=300, bbox_inches='tight')
```

## Validation Checklist

- [ ] All files parse without syntax errors
- [ ] Missing properties added to ontology
- [ ] Audio chain properly connects to ports
- [ ] SHACL validation passes for all 4 rules
- [ ] SPARQL queries return expected results
- [ ] No orphaned nodes in the graph

## Expected Validation Results

| Rule | Description | Status |
|------|-------------|--------|
| Rule 1 | M4 bidirectional cable | ✅ PASS |
| Rule 2 | Audio bypasses KVM | ✅ PASS (after fix) |
| Rule 3 | Legacy active adapters | ⚠️ N/A (no Mini-DP in deployment) |
| Rule 4 | Production uptime priority | ✅ PASS |

## Next Steps

1. **Extend the model**: Add more devices, ports, and cables
2. **Add monitoring**: Track actual connection states vs. topology
3. **Generate documentation**: Auto-generate wiring diagrams from RDF
4. **Version control**: Track topology changes over time
5. **Integration**: Connect to network monitoring tools

## Troubleshooting

### Common Issues

**Issue**: SHACL validation fails with "Unknown property"
- **Fix**: Ensure all properties are defined in ontology

**Issue**: SPARQL queries return empty results
- **Fix**: Check namespace prefixes match exactly

**Issue**: Turtle parsing errors
- **Fix**: Validate syntax with `riot --validate file.ttl`

## Resources

- [RDF Primer](https://www.w3.org/TR/rdf11-primer/)
- [SHACL Specification](https://www.w3.org/TR/shacl/)
- [Apache Jena Documentation](https://jena.apache.org/documentation/)
- [pySHACL Documentation](https://github.com/RDFLib/pySHACL)
