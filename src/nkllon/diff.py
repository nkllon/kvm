"""Topology comparison utilities."""

from pathlib import Path

from rdflib import Graph
from rdflib.compare import graph_diff, to_isomorphic


def compare_topologies(topology1_path: Path, topology2_path: Path) -> tuple[set, set, set]:
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

    in_both, only_in_first, only_in_second = graph_diff(
        to_isomorphic(graph1), to_isomorphic(graph2)
    )

    return in_both, only_in_first, only_in_second  # type: ignore


def format_triple(triple: tuple) -> str:
    """
    Format an RDF triple for display.

    Args:
        triple: RDF triple (subject, predicate, object)

    Returns:
        Formatted string
    """
    subject, predicate, object = triple

    def format_node(node: object) -> str:  # type: ignore
        s = str(node)
        if "#" in s:
            return s.split("#")[-1]
        elif "/" in s:
            return s.split("/")[-1]
        return s

    return f"{format_node(subject)} → {format_node(predicate)} → {format_node(object)}"


def print_topology_diff(topology1_path: Path, topology2_path: Path) -> None:
    """
    Print human-readable topology differences.

    Args:
        topology1_path: Path to first topology file
        topology2_path: Path to second topology file
    """
    in_both, only_in_first, only_in_second = compare_topologies(topology1_path, topology2_path)

    print("=" * 80)
    print("Topology Comparison")
    print("=" * 80)
    print(f"\nFile 1: {topology1_path.name}")
    print(f"File 2: {topology2_path.name}")

    print("\n📊 Statistics:")
    print(f"  Common triples:     {len(in_both)}")
    print(f"  Only in {topology1_path.name:20s}: {len(only_in_first)}")
    print(f"  Only in {topology2_path.name:20s}: {len(only_in_second)}")

    if only_in_first:
        print(f"\n➖ Removed in {topology2_path.name}:")
        for triple in sorted(only_in_first)[:20]:  # Show first 20
            print(f"  - {format_triple(triple)}")
        if len(only_in_first) > 20:
            print(f"  ... and {len(only_in_first) - 20} more")

    if only_in_second:
        print(f"\n➕ Added in {topology2_path.name}:")
        for triple in sorted(only_in_second)[:20]:  # Show first 20
            print(f"  + {format_triple(triple)}")
        if len(only_in_second) > 20:
            print(f"  ... and {len(only_in_second) - 20} more")

    print("\n" + "=" * 80)


def get_device_changes(topology1_path: Path, topology2_path: Path) -> dict:
    """
    Get high-level device changes between topologies.

    Args:
        topology1_path: Path to first topology file
        topology2_path: Path to second topology file

    Returns:
        Dictionary with added, removed, and modified devices
    """
    graph1 = Graph()
    graph1.parse(topology1_path, format="turtle")

    graph2 = Graph()
    graph2.parse(topology2_path, format="turtle")

    # Query for devices in each graph
    device_query = """
        PREFIX : <http://nkllon.com/sys#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

        SELECT ?device ?type WHERE {
            ?device a ?type .
            ?type rdfs:subClassOf* :Device .
            FILTER(?type != :Device)
        }
    """

    devices1 = {(str(row.device), str(row.type)) for row in graph1.query(device_query)}  # type: ignore
    devices2 = {(str(row.device), str(row.type)) for row in graph2.query(device_query)}  # type: ignore

    added = devices2 - devices1
    removed = devices1 - devices2
    common = devices1 & devices2

    return {
        "added": [{"device": d.split("#")[-1], "type": t.split("#")[-1]} for d, t in added],
        "removed": [{"device": d.split("#")[-1], "type": t.split("#")[-1]} for d, t in removed],
        "common": [{"device": d.split("#")[-1], "type": t.split("#")[-1]} for d, t in common],
    }


def main() -> None:
    """Run diff from command line."""
    import argparse

    parser = argparse.ArgumentParser(description="Compare two topology configurations")
    parser.add_argument("file1", type=Path, help="First topology file")
    parser.add_argument("file2", type=Path, help="Second topology file")
    parser.add_argument(
        "--devices-only",
        action="store_true",
        help="Show only device-level changes",
    )

    args = parser.parse_args()

    if not args.file1.exists():
        print(f"Error: File not found: {args.file1}")
        return

    if not args.file2.exists():
        print(f"Error: File not found: {args.file2}")
        return

    if args.devices_only:
        changes = get_device_changes(args.file1, args.file2)

        print("=" * 80)
        print("Device Changes")
        print("=" * 80)

        if changes["added"]:
            print("\n➕ Added Devices:")
            for device in changes["added"]:
                print(f"  + {device['device']} ({device['type']})")

        if changes["removed"]:
            print("\n➖ Removed Devices:")
            for device in changes["removed"]:
                print(f"  - {device['device']} ({device['type']})")

        if changes["common"]:
            print(f"\n✓ Unchanged Devices: {len(changes['common'])}")

        print("\n" + "=" * 80)
    else:
        print_topology_diff(args.file1, args.file2)


if __name__ == "__main__":
    main()
