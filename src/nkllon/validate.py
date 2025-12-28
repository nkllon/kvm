"""SHACL validation for hardware topology."""

from pathlib import Path
from typing import Tuple

from pyshacl import validate
from rdflib import Graph


def load_graph(file_path: Path) -> Graph:
    """Load an RDF graph from a Turtle file."""
    graph = Graph()
    graph.parse(file_path, format="turtle")
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
    """
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


def main() -> None:
    """Run validation from command line."""
    # Determine project root
    project_root = Path(__file__).parent.parent.parent

    ontology_path = project_root / "ontology" / "hardware_ontology.ttl"
    shacl_path = project_root / "ontology" / "system_constraints.shacl.ttl"
    data_path = project_root / "data" / "physical_deployment.ttl"

    print("=" * 80)
    print("NKLLON Hardware Topology Validation")
    print("=" * 80)
    print(f"\nOntology: {ontology_path.name}")
    print(f"SHACL:    {shacl_path.name}")
    print(f"Data:     {data_path.name}")
    print("\n" + "-" * 80)

    conforms, report = validate_topology(ontology_path, shacl_path, data_path)

    if conforms:
        print("\n✅ VALIDATION PASSED")
        print("\nAll SHACL constraints satisfied:")
        print("  ✓ Rule 1: eARC return path (SmartDisplay to PreAmp)")
        print("  ✓ Rule 2: Audio interfaces bypass KVMs (can connect to PreAmp)")
        print("  ✓ Rule 3: Bidirectional cables (USB-C to DisplayPort)")
        print("  ✓ Rule 4: Production uptime-critical ports")
    else:
        print("\n❌ VALIDATION FAILED")
        print("\nViolations found:\n")
        print(report)

    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
