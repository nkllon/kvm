"""SHACL validation for hardware topology."""

import logging
import sys
from pathlib import Path

from pyshacl import validate
from rdflib import Graph
from rdflib.exceptions import ParserError

from nkllon.config import Config, default_config
from nkllon.exceptions import FileNotFoundError as NKLLONFileNotFoundError
from nkllon.exceptions import ParseError, ValidationError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def load_graph(file_path: Path) -> Graph:
    """
    Load an RDF graph from a Turtle file.

    Args:
        file_path: Path to the Turtle file

    Returns:
        Loaded RDF graph

    Raises:
        NKLLONFileNotFoundError: If file doesn't exist
        ParseError: If file has syntax errors
    """
    if not file_path.exists():
        raise NKLLONFileNotFoundError(f"File not found: {file_path}")

    logger.debug(f"Loading graph from {file_path}")

    graph = Graph()
    try:
        graph.parse(file_path, format="turtle")
        logger.debug(f"Successfully loaded {len(graph)} triples from {file_path.name}")
    except ParserError as e:
        raise ParseError(f"Syntax error in {file_path.name}: {e}")
    except Exception as e:
        raise ParseError(f"Failed to load {file_path.name}: {e}")

    return graph


def validate_topology(
    ontology_path: Path,
    shacl_path: Path,
    data_path: Path,
) -> tuple[bool, str]:
    """
    Validate hardware topology against SHACL constraints.

    Args:
        ontology_path: Path to hardware ontology TTL file
        shacl_path: Path to SHACL constraints TTL file
        data_path: Path to physical deployment data TTL file

    Returns:
        Tuple of (conforms: bool, report: str)

    Raises:
        ValidationError: If validation cannot be performed
        NKLLONFileNotFoundError: If any required file is missing
        ParseError: If any file has syntax errors
    """
    logger.info(f"Starting validation for {data_path.name}")

    try:
        # Load ontology
        logger.debug("Loading ontology...")
        ontology = load_graph(ontology_path)

        # Load data and merge with ontology
        logger.debug("Loading deployment data...")
        data = load_graph(data_path)
        data += ontology
        logger.debug(f"Merged graph contains {len(data)} triples")

        # Load SHACL shapes
        logger.debug("Loading SHACL constraints...")
        shapes = load_graph(shacl_path)

        # Validate
        logger.info("Running SHACL validation...")
        conforms, results_graph, results_text = validate(
            data_graph=data,
            shacl_graph=shapes,
            inference="rdfs",
            abort_on_first=False,
            meta_shacl=False,
            advanced=True,
        )

        logger.info(f"Validation {'passed' if conforms else 'failed'}")
        return conforms, results_text

    except (NKLLONFileNotFoundError, ParseError):
        raise
    except Exception as e:
        raise ValidationError(f"Validation failed: {e}")


def validate_with_config(
    config: Config | None = None, environment: str = "prod"
) -> tuple[bool, str]:
    """
    Validate topology using configuration object.

    Args:
        config: Configuration object (uses default if not provided)
        environment: Environment to validate (dev, staging, prod)

    Returns:
        Tuple of (conforms: bool, report: str)
    """
    if config is None:
        config = default_config

    data_path = config.get_deployment_path(environment)

    return validate_topology(
        config.ontology_path,
        config.shacl_path,
        data_path,
    )


def main() -> None:
    """Run validation from command line."""
    import argparse

    parser = argparse.ArgumentParser(description="Validate hardware topology")
    parser.add_argument(
        "--env",
        choices=["dev", "staging", "prod"],
        default="prod",
        help="Environment to validate (default: prod)",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    parser.add_argument("--quiet", "-q", action="store_true", help="Suppress output except errors")

    args = parser.parse_args()

    # Configure logging level
    if args.verbose:
        logging.getLogger("nkllon").setLevel(logging.DEBUG)
    elif args.quiet:
        logging.getLogger("nkllon").setLevel(logging.ERROR)

    config = default_config
    data_path = config.get_deployment_path(args.env)

    if not args.quiet:
        print("=" * 80)
        print("NKLLON Hardware Topology Validation")
        print("=" * 80)
        print(f"\nEnvironment: {args.env}")
        print(f"Ontology:    {config.ontology_path.name}")
        print(f"SHACL:       {config.shacl_path.name}")
        print(f"Data:        {data_path.name}")
        print("\n" + "-" * 80)

    try:
        conforms, report = validate_topology(
            config.ontology_path,
            config.shacl_path,
            data_path,
        )

        if conforms:
            if not args.quiet:
                print("\n✅ VALIDATION PASSED")
                print("\nAll SHACL constraints satisfied:")
                print("  ✓ Rule 1: eARC return path (SmartDisplay to PreAmp)")
                print("  ✓ Rule 2: Audio interfaces bypass KVMs (can connect to PreAmp)")
                print("  ✓ Rule 3: Bidirectional cables (USB-C to DisplayPort)")
                print("  ✓ Rule 4: Production uptime-critical ports")
                print("\n" + "=" * 80)
            sys.exit(0)
        else:
            if not args.quiet:
                print("\n❌ VALIDATION FAILED")
                print("\nViolations found:\n")
                print(report)
                print("\n" + "=" * 80)
            sys.exit(1)

    except NKLLONFileNotFoundError as e:
        logger.error(f"File not found: {e}")
        if not args.quiet:
            print(f"\n❌ ERROR: {e}")
        sys.exit(2)

    except ParseError as e:
        logger.error(f"Parse error: {e}")
        if not args.quiet:
            print(f"\n❌ ERROR: {e}")
        sys.exit(3)

    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        if not args.quiet:
            print(f"\n❌ ERROR: {e}")
        sys.exit(4)


if __name__ == "__main__":
    main()
