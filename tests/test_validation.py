"""Tests for SHACL validation."""

from pathlib import Path

import pytest
from rdflib import Graph

from nkllon.validate import load_graph, validate_topology


@pytest.fixture
def project_root() -> Path:
    """Get project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def ontology_path(project_root: Path) -> Path:
    """Get ontology file path."""
    return project_root / "ontology" / "hardware_ontology.ttl"


@pytest.fixture
def shacl_path(project_root: Path) -> Path:
    """Get SHACL constraints file path."""
    return project_root / "ontology" / "system_constraints.shacl.ttl"


@pytest.fixture
def data_path(project_root: Path) -> Path:
    """Get deployment data file path."""
    return project_root / "data" / "physical_deployment.ttl"


def test_load_ontology(ontology_path: Path) -> None:
    """Test that ontology file loads successfully."""
    graph = load_graph(ontology_path)
    assert len(graph) > 0, "Ontology should contain triples"


def test_load_shacl(shacl_path: Path) -> None:
    """Test that SHACL file loads successfully."""
    graph = load_graph(shacl_path)
    assert len(graph) > 0, "SHACL should contain triples"


def test_load_data(data_path: Path) -> None:
    """Test that deployment data loads successfully."""
    graph = load_graph(data_path)
    assert len(graph) > 0, "Data should contain triples"


def test_validation_passes(
    ontology_path: Path,
    shacl_path: Path,
    data_path: Path,
) -> None:
    """Test that current deployment passes all SHACL constraints."""
    conforms, report = validate_topology(ontology_path, shacl_path, data_path)
    assert conforms, f"Validation should pass. Report:\n{report}"


def test_ontology_has_belongs_to_device(ontology_path: Path) -> None:
    """Test that belongsToDevice property is defined in ontology."""
    graph = load_graph(ontology_path)

    query = """
        PREFIX : <http://nkllon.com/sys#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>

        ASK {
            :belongsToDevice a owl:ObjectProperty .
        }
    """

    result = graph.query(query)
    assert bool(result), "belongsToDevice property should be defined"


def test_audio_chain_connects_to_port(data_path: Path) -> None:
    """Test that audio cable connects to a port, not directly to a device."""
    graph = load_graph(data_path)

    query = """
        PREFIX : <http://nkllon.com/sys#>

        SELECT ?cable ?target WHERE {
            :MotuM4 :hasPort ?port .
            ?port :connectsVia ?cable .
            ?cable :connectsTo ?target .
            ?target a :Port .
        }
    """

    results = list(graph.query(query))
    assert len(results) > 0, "Audio cable should connect to a Port"


def test_mac_m4_has_bidirectional_cable(data_path: Path, ontology_path: Path) -> None:
    """Test that Mac M4 uses bidirectional cable."""
    graph = load_graph(data_path)
    graph += load_graph(ontology_path)

    query = """
        PREFIX : <http://nkllon.com/sys#>

        SELECT ?cable WHERE {
            :MacM4Mini :hasPort ?port .
            ?port :connectsVia ?cable .
            ?cable :isBidirectional true .
        }
    """

    results = list(graph.query(query))
    assert len(results) > 0, "Mac M4 should have bidirectional cable"


def test_ubuntu_connects_to_high_priority_port(
    data_path: Path,
    ontology_path: Path,
) -> None:
    """Test that Ubuntu production host connects to high-priority KVM port."""
    graph = load_graph(data_path)
    graph += load_graph(ontology_path)

    query = """
        PREFIX : <http://nkllon.com/sys#>

        SELECT ?kvmPort WHERE {
            :Ubuntu_Prod :hasPort ?port .
            ?port :connectsVia ?cable .
            ?cable :connectsTo ?kvmPort .
            ?kvmPort :portPriority "High-Priority" .
        }
    """

    results = list(graph.query(query))
    assert len(results) > 0, "Ubuntu should connect to high-priority port"


def test_smart_display_exists(data_path: Path, ontology_path: Path) -> None:
    """Test that SmartDisplay device class exists and is used."""
    graph = load_graph(data_path)
    graph += load_graph(ontology_path)

    query = """
        PREFIX : <http://nkllon.com/sys#>

        SELECT ?display WHERE {
            ?display a :SmartDisplay .
        }
    """

    results = list(graph.query(query))
    assert len(results) > 0, "SmartDisplay device should exist"


def test_preamp_exists(data_path: Path, ontology_path: Path) -> None:
    """Test that PreAmp device class exists and is used."""
    graph = load_graph(data_path)
    graph += load_graph(ontology_path)

    query = """
        PREFIX : <http://nkllon.com/sys#>

        SELECT ?preamp WHERE {
            ?preamp a :PreAmp .
        }
    """

    results = list(graph.query(query))
    assert len(results) > 0, "PreAmp device should exist"


def test_earc_connection_exists(
    data_path: Path,
    ontology_path: Path,
) -> None:
    """Test that eARC connection from SmartDisplay to PreAmp exists."""
    graph = load_graph(data_path)
    graph += load_graph(ontology_path)

    query = """
        PREFIX : <http://nkllon.com/sys#>

        SELECT ?display ?preamp WHERE {
            ?display a :SmartDisplay ;
                     :hasPort ?port .
            ?port :connectsVia ?cable .
            ?cable :connectsTo ?preampPort .
            ?preampPort :belongsToDevice ?preamp .
            ?preamp a :PreAmp .
        }
    """

    results = list(graph.query(query))
    assert len(results) > 0, "eARC connection from SmartDisplay to PreAmp should exist"


def test_audio_interface_connects_to_preamp(
    data_path: Path,
    ontology_path: Path,
) -> None:
    """Test that audio interface can connect to PreAmp."""
    graph = load_graph(data_path)
    graph += load_graph(ontology_path)

    query = """
        PREFIX : <http://nkllon.com/sys#>

        SELECT ?audio ?preamp WHERE {
            ?audio a :AudioInterface ;
                   :hasPort ?port .
            ?port :connectsVia ?cable .
            ?cable :connectsTo ?preampPort .
            ?preampPort :belongsToDevice ?preamp .
            ?preamp a :PreAmp .
        }
    """

    results = list(graph.query(query))
    assert len(results) > 0, "Audio interface should connect to PreAmp"
