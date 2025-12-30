"""Configuration management for NKLLON topology system."""

import os
from pathlib import Path


class Config:
    """Configuration for NKLLON topology system."""

    def __init__(self, project_root: Path | None = None):
        """
        Initialize configuration.

        Args:
            project_root: Optional project root path. If not provided,
                         will be inferred from package location.
        """
        if project_root is None:
            # Infer from package location
            self.project_root = Path(__file__).parent.parent.parent
        else:
            self.project_root = project_root

        # Allow environment variable override
        env_root = os.getenv("NKLLON_PROJECT_ROOT")
        if env_root:
            self.project_root = Path(env_root)

    @property
    def ontology_dir(self) -> Path:
        """Get ontology directory path."""
        return self.project_root / "ontology"

    @property
    def data_dir(self) -> Path:
        """Get data directory path."""
        return self.project_root / "data"

    @property
    def ontology_path(self) -> Path:
        """Get hardware ontology file path."""
        return self.ontology_dir / "hardware_ontology.ttl"

    @property
    def shacl_path(self) -> Path:
        """Get SHACL constraints file path."""
        return self.ontology_dir / "system_constraints.shacl.ttl"

    @property
    def deployment_path(self) -> Path:
        """Get physical deployment file path."""
        return self.data_dir / "physical_deployment.ttl"

    def get_deployment_path(self, environment: str = "prod") -> Path:
        """
        Get deployment file path for specific environment.

        Args:
            environment: Environment name (dev, staging, prod)

        Returns:
            Path to deployment file
        """
        if environment == "prod":
            return self.deployment_path

        env_file = self.data_dir / "deployments" / f"{environment}.ttl"
        if env_file.exists():
            return env_file

        return self.deployment_path


# Global default config
default_config = Config()
