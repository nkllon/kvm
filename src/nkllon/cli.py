"""Command-line interface for NKLLON topology tools."""

import argparse
import logging
import sys
from pathlib import Path

from nkllon import __version__, diff, query, reporters, validate, visualize
from nkllon.config import default_config
from nkllon.exceptions import (
    ConfigurationError,
    FileNotFoundError as NKLLONFileNotFoundError,
    ParseError,
    ValidationError,
)


EXIT_CODE_HELP = """\
Exit codes:
  0 - Success, or help displayed without running validation
  1 - Validation completed but constraints failed
  2 - Required file not found
  3 - RDF/SHACL parsing error
  4 - Validation execution error
  5 - Configuration error
  99 - Unexpected error
"""


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="NKLLON Hardware Topology Validation System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=EXIT_CODE_HELP,
    )

    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Validate command
    validate_parser = subparsers.add_parser(
        "validate",
        help="Run SHACL validation on deployment data",
    )
    validate_parser.add_argument(
        "--env",
        choices=["dev", "staging", "prod"],
        default="prod",
        help="Environment to validate (default: prod)",
    )
    validate_parser.add_argument(
        "--export",
        type=Path,
        help="Export report to file (format auto-detected from extension)",
    )
    validate_parser.add_argument(
        "--format",
        choices=["json", "html", "markdown", "md"],
        help="Report format (overrides --export extension)",
    )
    validate_parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )
    validate_parser.add_argument(
        "--quiet", "-q", action="store_true", help="Suppress output except errors"
    )

    # Query command
    query_parser = subparsers.add_parser(
        "query",
        help="Run example SPARQL queries",
    )
    query_parser.add_argument(
        "--env",
        choices=["dev", "staging", "prod"],
        default="prod",
        help="Environment to query (default: prod)",
    )

    # Diff command
    diff_parser = subparsers.add_parser(
        "diff",
        help="Compare two topology configurations",
    )
    diff_parser.add_argument("file1", type=Path, help="First topology file")
    diff_parser.add_argument("file2", type=Path, help="Second topology file")
    diff_parser.add_argument(
        "--devices-only",
        action="store_true",
        help="Show only device-level changes",
    )

    # Visualize command
    viz_parser = subparsers.add_parser(
        "visualize",
        help="Generate interactive topology visualization",
    )
    viz_parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=Path("topology_visualization.html"),
        help="Output HTML file path",
    )
    viz_parser.add_argument(
        "--env",
        choices=["dev", "staging", "prod"],
        default="prod",
        help="Environment to visualize (default: prod)",
    )

    # Info command
    subparsers.add_parser(
        "info",
        help="Display system information",
    )

    args = parser.parse_args()

    if args.command == "validate":
        handle_validate(args)
    elif args.command == "query":
        handle_query(args)
    elif args.command == "diff":
        handle_diff(args)
    elif args.command == "visualize":
        handle_visualize(args)
    elif args.command == "info":
        print_info()
    else:
        parser.print_help()
        sys.exit(0)


def handle_validate(args: argparse.Namespace) -> None:
    """Handle validate command."""
    logger = logging.getLogger("nkllon")

    # Configure logging
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    elif args.quiet:
        logger.setLevel(logging.ERROR)

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
        conforms, report = validate.validate_topology(
            config.ontology_path,
            config.shacl_path,
            data_path,
        )

        # Export report if requested
        if args.export:
            format = args.format
            if not format:
                # Auto-detect from extension
                ext = args.export.suffix.lstrip(".")
                format = ext if ext in ["json", "html", "md", "markdown"] else "json"

            reporters.export_report(conforms, report, args.export, format)
            if not args.quiet:
                print(f"\n📄 Report exported to: {args.export}")

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
        logger.error("File not found: %s", e)
        if not args.quiet:
            print(f"\n❌ ERROR: {e}")
        sys.exit(2)
    except ParseError as e:
        logger.error("Parsing error: %s", e)
        if not args.quiet:
            print(f"\n❌ ERROR: {e}")
        sys.exit(3)
    except ValidationError as e:
        logger.error("Validation execution error: %s", e)
        if not args.quiet:
            print(f"\n❌ ERROR: {e}")
        sys.exit(4)
    except ConfigurationError as e:
        logger.error("Configuration error: %s", e)
        if not args.quiet:
            print(f"\n❌ ERROR: {e}")
        sys.exit(5)
    except Exception as e:  # pragma: no cover - safety net
        logger.exception("Unexpected error during validation")
        if not args.quiet:
            print(f"\n❌ UNEXPECTED ERROR: {e}")
        sys.exit(99)


def handle_query(args: argparse.Namespace) -> None:
    """Handle query command."""
    # Set environment if needed (future enhancement)
    query.main()


def handle_diff(args: argparse.Namespace) -> None:
    """Handle diff command."""
    if not args.file1.exists():
        print(f"Error: File not found: {args.file1}")
        sys.exit(1)

    if not args.file2.exists():
        print(f"Error: File not found: {args.file2}")
        sys.exit(1)

    if args.devices_only:
        changes = diff.get_device_changes(args.file1, args.file2)

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
        diff.print_topology_diff(args.file1, args.file2)


def handle_visualize(args: argparse.Namespace) -> None:
    """Handle visualize command."""
    config = default_config
    data_path = config.get_deployment_path(args.env)

    visualize.generate_visualization(config.ontology_path, data_path, args.output)


def print_info() -> None:
    """Print system information."""
    print("=" * 80)
    print("NKLLON Hardware Topology System")
    print("=" * 80)
    print(f"\nVersion: {__version__}")
    print("\nDescription:")
    print("  Semantic web validation system for KVM hardware topologies")
    print("  using RDF/OWL ontologies and SHACL constraints.")
    print("\nCommands:")
    print("  nkllon validate     - Run SHACL validation")
    print("  nkllon query        - Run example SPARQL queries")
    print("  nkllon diff         - Compare two topologies")
    print("  nkllon visualize    - Generate interactive visualization")
    print("  nkllon info         - Display this information")
    print("\nMakefile shortcuts:")
    print("  make validate       - Run validation")
    print("  make query          - Run queries")
    print("  make test           - Run test suite")
    print("\nExamples:")
    print("  nkllon validate --env prod --export report.html")
    print("  nkllon diff data/old.ttl data/new.ttl --devices-only")
    print("  nkllon visualize --output topology.html")
    print("=" * 80)


if __name__ == "__main__":
    main()
