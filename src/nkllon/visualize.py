"""Topology visualization utilities."""

import json
from pathlib import Path

from rdflib import Graph


def extract_topology_graph(graph: Graph) -> tuple[list[dict], list[dict]]:
    """
    Extract nodes and edges from RDF graph.

    Args:
        graph: RDF graph containing topology

    Returns:
        Tuple of (nodes, edges) as lists of dictionaries
    """
    # Query for devices
    device_query = """
        PREFIX : <http://nkllon.com/sys#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT DISTINCT ?device ?type WHERE {
            ?device a ?type .
            ?type rdfs:subClassOf* :Device .
            FILTER(?type != :Device)
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
        device_id = str(row.device).split("#")[-1]  # type: ignore
        device_type = str(row.type).split("#")[-1]  # type: ignore
        nodes.append({"id": device_id, "type": device_type, "label": device_id})

    # Build edges
    for row in graph.query(connection_query):
        src_id = str(row.src).split("#")[-1]  # type: ignore
        dst_id = str(row.dst).split("#")[-1]  # type: ignore
        cable_id = str(row.cable).split("#")[-1]  # type: ignore
        edges.append({"source": src_id, "target": dst_id, "label": cable_id})

    return nodes, edges


def generate_d3_html(nodes: list[dict], edges: list[dict]) -> str:
    """
    Generate HTML with D3.js visualization.

    Args:
        nodes: List of node dictionaries
        edges: List of edge dictionaries

    Returns:
        HTML string with embedded D3.js visualization
    """
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>NKLLON Topology Visualization</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {{
            margin: 0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            overflow: hidden;
        }}
        #graph {{
            width: 100vw;
            height: 100vh;
            background: #f8f9fa;
        }}
        .node {{
            cursor: pointer;
            stroke: #fff;
            stroke-width: 2px;
        }}
        .link {{
            stroke: #999;
            stroke-opacity: 0.6;
            stroke-width: 2px;
        }}
        .node-label {{
            font-size: 12px;
            font-weight: bold;
            pointer-events: none;
            text-shadow: 0 1px 2px rgba(255,255,255,0.8);
        }}
        .link-label {{
            font-size: 10px;
            fill: #666;
            pointer-events: none;
        }}
        .legend {{
            position: absolute;
            top: 20px;
            right: 20px;
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            margin: 5px 0;
        }}
        .legend-color {{
            width: 20px;
            height: 20px;
            border-radius: 50%;
            margin-right: 10px;
        }}
        .controls {{
            position: absolute;
            top: 20px;
            left: 20px;
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        button {{
            margin: 5px;
            padding: 8px 16px;
            border: none;
            border-radius: 4px;
            background: #667eea;
            color: white;
            cursor: pointer;
            font-size: 14px;
        }}
        button:hover {{
            background: #5568d3;
        }}
    </style>
</head>
<body>
    <div id="graph"></div>

    <div class="controls">
        <h3 style="margin-top: 0;">Controls</h3>
        <button onclick="resetZoom()">Reset View</button>
        <button onclick="centerGraph()">Center</button>
    </div>

    <div class="legend">
        <h3 style="margin-top: 0;">Device Types</h3>
        <div class="legend-item">
            <div class="legend-color" style="background: #4CAF50;"></div>
            <span>Host</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background: #2196F3;"></div>
            <span>KVM</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background: #FF9800;"></div>
            <span>AudioInterface</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background: #9C27B0;"></div>
            <span>SmartDisplay</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background: #F44336;"></div>
            <span>PreAmp</span>
        </div>
    </div>

    <script>
        const nodes = {json.dumps(nodes)};
        const links = {json.dumps(edges)};

        const width = window.innerWidth;
        const height = window.innerHeight;

        const svg = d3.select("#graph")
            .append("svg")
            .attr("width", width)
            .attr("height", height);

        const g = svg.append("g");

        // Add zoom behavior
        const zoom = d3.zoom()
            .scaleExtent([0.1, 4])
            .on("zoom", (event) => {{
                g.attr("transform", event.transform);
            }});

        svg.call(zoom);

        const simulation = d3.forceSimulation(nodes)
            .force("link", d3.forceLink(links).id(d => d.id).distance(150))
            .force("charge", d3.forceManyBody().strength(-500))
            .force("center", d3.forceCenter(width / 2, height / 2))
            .force("collision", d3.forceCollide().radius(50));

        // Create arrow markers
        svg.append("defs").selectAll("marker")
            .data(["arrow"])
            .join("marker")
            .attr("id", "arrow")
            .attr("viewBox", "0 -5 10 10")
            .attr("refX", 25)
            .attr("refY", 0)
            .attr("markerWidth", 6)
            .attr("markerHeight", 6)
            .attr("orient", "auto")
            .append("path")
            .attr("d", "M0,-5L10,0L0,5")
            .attr("fill", "#999");

        const link = g.append("g")
            .selectAll("line")
            .data(links)
            .join("line")
            .attr("class", "link")
            .attr("marker-end", "url(#arrow)");

        const node = g.append("g")
            .selectAll("circle")
            .data(nodes)
            .join("circle")
            .attr("class", "node")
            .attr("r", 20)
            .attr("fill", d => getNodeColor(d.type))
            .call(drag(simulation))
            .on("mouseover", function(event, d) {{
                d3.select(this)
                    .transition()
                    .duration(200)
                    .attr("r", 25);
            }})
            .on("mouseout", function(event, d) {{
                d3.select(this)
                    .transition()
                    .duration(200)
                    .attr("r", 20);
            }});

        const label = g.append("g")
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

        function resetZoom() {{
            svg.transition()
                .duration(750)
                .call(zoom.transform, d3.zoomIdentity);
        }}

        function centerGraph() {{
            const bounds = g.node().getBBox();
            const fullWidth = bounds.width;
            const fullHeight = bounds.height;
            const midX = bounds.x + fullWidth / 2;
            const midY = bounds.y + fullHeight / 2;

            const scale = 0.8 / Math.max(fullWidth / width, fullHeight / height);
            const translate = [width / 2 - scale * midX, height / 2 - scale * midY];

            svg.transition()
                .duration(750)
                .call(
                    zoom.transform,
                    d3.zoomIdentity.translate(translate[0], translate[1]).scale(scale)
                );
        }}

        // Center on load
        setTimeout(centerGraph, 1000);
    </script>
</body>
</html>"""


def generate_visualization(ontology_path: Path, data_path: Path, output_path: Path) -> None:
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

    # Generate HTML
    html = generate_d3_html(nodes, edges)

    with open(output_path, "w") as f:
        f.write(html)

    print(f"✅ Visualization generated: {output_path}")
    print(f"   Nodes: {len(nodes)}")
    print(f"   Edges: {len(edges)}")


def main() -> None:
    """Run visualization from command line."""
    import argparse

    from nkllon.config import default_config

    parser = argparse.ArgumentParser(description="Generate interactive topology visualization")
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=Path("topology_visualization.html"),
        help="Output HTML file path",
    )
    parser.add_argument(
        "--env",
        choices=["dev", "staging", "prod"],
        default="prod",
        help="Environment to visualize",
    )

    args = parser.parse_args()

    config = default_config
    data_path = config.get_deployment_path(args.env)

    generate_visualization(config.ontology_path, data_path, args.output)


if __name__ == "__main__":
    main()
