"""SPARQL query utilities for hardware topology."""

from pathlib import Path
from typing import List

from rdflib import Graph
from rdflib.query import ResultRow


def load_merged_graph() -> Graph:
    """Load and merge ontology and deployment data."""
    project_root = Path(__file__).parent.parent.parent

    graph = Graph()
    graph.parse(project_root / "ontology" / "hardware_ontology.ttl", format="turtle")
    graph.parse(project_root / "data" / "physical_deployment.ttl", format="turtle")

    return graph


def query_bidirectional_cables() -> List[ResultRow]:
    """Find all bidirectional cables and their connections."""
    graph = load_merged_graph()

    query = """
        PREFIX : <http://nkllon.com/sys#>

        SELECT ?cable ?srcDevice ?dstDevice ?srcForm ?dstForm WHERE {
            ?cable a :Cable ;
                   :isBidirectional true .
            ?srcPort :connectsVia ?cable .
            ?cable :connectsTo ?dstPort .
            ?srcPort :belongsToDevice ?srcDevice ;
                     :physicalForm ?srcForm .
            ?dstPort :belongsToDevice ?dstDevice ;
                     :physicalForm ?dstForm .
        }
    """

    return list(graph.query(query))


def query_audio_connections() -> List[ResultRow]:
    """Find all audio interface connections."""
    graph = load_merged_graph()

    query = """
        PREFIX : <http://nkllon.com/sys#>

        SELECT ?audioDevice ?cable ?connectedDevice WHERE {
            ?audioDevice a :AudioInterface ;
                         :hasPort ?port .
            ?port :connectsVia ?cable .
            ?cable :connectsTo ?otherPort .
            ?otherPort :belongsToDevice ?connectedDevice .
        }
    """

    return list(graph.query(query))


def query_uptime_critical_hosts() -> List[ResultRow]:
    """Find uptime-critical hosts and their KVM port priorities."""
    graph = load_merged_graph()

    query = """
        PREFIX : <http://nkllon.com/sys#>

        SELECT ?host ?kvmPort ?priority WHERE {
            ?host :isUptimeCritical true ;
                  :hasPort ?hostPort .
            ?hostPort :connectsVia ?cable .
            ?cable :connectsTo ?kvmPort .
            ?kvmPort :portPriority ?priority .
        }
    """

    return list(graph.query(query))


def query_all_devices() -> List[ResultRow]:
    """List all devices in the topology."""
    graph = load_merged_graph()

    query = """
        PREFIX : <http://nkllon.com/sys#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

        SELECT ?device ?type WHERE {
            ?device a ?type .
            ?type a <http://www.w3.org/2002/07/owl#Class> .
            FILTER(?type != <http://nkllon.com/sys#Device>)
        }
        ORDER BY ?type ?device
    """

    return list(graph.query(query))


def format_uri(uri: str) -> str:
    """Format URI for display by extracting local name."""
    return uri.split("#")[-1] if "#" in uri else uri.split("/")[-1]


def main() -> None:
    """Run example queries from command line."""
    print("=" * 80)
    print("NKLLON Hardware Topology - SPARQL Queries")
    print("=" * 80)

    # Query 1: Bidirectional cables
    print("\n📊 Query 1: Bidirectional Cables")
    print("-" * 80)
    results = query_bidirectional_cables()
    if results:
        for row in results:
            cable = format_uri(str(row.cable))
            src = format_uri(str(row.srcDevice))
            dst = format_uri(str(row.dstDevice))
            src_form = str(row.srcForm)
            dst_form = str(row.dstForm)
            print(f"  {cable}: {src} ({src_form}) → {dst} ({dst_form})")
    else:
        print("  No bidirectional cables found")

    # Query 2: Audio connections
    print("\n🎵 Query 2: Audio Interface Connections")
    print("-" * 80)
    results = query_audio_connections()
    if results:
        for row in results:
            audio = format_uri(str(row.audioDevice))
            cable = format_uri(str(row.cable))
            connected = format_uri(str(row.connectedDevice))
            print(f"  {audio} → {cable} → {connected}")
    else:
        print("  No audio connections found")

    # Query 3: Uptime-critical hosts
    print("\n⚡ Query 3: Uptime-Critical Hosts")
    print("-" * 80)
    results = query_uptime_critical_hosts()
    if results:
        for row in results:
            host = format_uri(str(row.host))
            kvm_port = format_uri(str(row.kvmPort))
            priority = str(row.priority)
            print(f"  {host} → {kvm_port} (Priority: {priority})")
    else:
        print("  No uptime-critical hosts found")

    # Query 4: All devices
    print("\n🖥️  Query 4: All Devices")
    print("-" * 80)
    results = query_all_devices()
    if results:
        current_type = None
        for row in results:
            device_type = format_uri(str(row.type))
            device = format_uri(str(row.device))
            if device_type != current_type:
                print(f"\n  {device_type}:")
                current_type = device_type
            print(f"    - {device}")
    else:
        print("  No devices found")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
