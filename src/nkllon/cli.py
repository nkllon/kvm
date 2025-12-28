"""Command-line interface for NKLLON topology tools."""

import argparse
import sys

from nkllon import validate, query


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="NKLLON Hardware Topology Validation System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Validate command
    subparsers.add_parser(
        "validate",
        help="Run SHACL validation on deployment data",
    )

    # Query command
    subparsers.add_parser(
        "query",
        help="Run example SPARQL queries",
    )

    # Info command
    info_parser = subparsers.add_parser(
        "info",
        help="Display system information",
    )

    args = parser.parse_args()

    if args.command == "validate":
        validate.main()
    elif args.command == "query":
        query.main()
    elif args.command == "info":
        print_info()
    else:
        parser.print_help()
        sys.exit(1)


def print_info() -> None:
    """Print system information."""
    from nkllon import __version__

    print("=" * 80)
    print("NKLLON Hardware Topology System")
    print("=" * 80)
    print(f"\nVersion: {__version__}")
    print("\nDescription:")
    print("  Semantic web validation system for KVM hardware topologies")
    print("  using RDF/OWL ontologies and SHACL constraints.")
    print("\nCommands:")
    print("  nkllon validate  - Run SHACL validation")
    print("  nkllon query     - Run example SPARQL queries")
    print("  nkllon info      - Display this information")
    print("\nMakefile shortcuts:")
    print("  make validate    - Run validation")
    print("  make query       - Run queries")
    print("  make test        - Run test suite")
    print("=" * 80)


if __name__ == "__main__":
    main()
