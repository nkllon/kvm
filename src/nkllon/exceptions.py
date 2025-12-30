"""Custom exceptions for NKLLON topology system."""


class NKLLONError(Exception):
    """Base exception for NKLLON errors."""

    pass


class ValidationError(NKLLONError):
    """Exception raised during validation."""

    pass


class FileNotFoundError(NKLLONError):
    """Exception raised when required file is not found."""

    pass


class ParseError(NKLLONError):
    """Exception raised when RDF parsing fails."""

    pass


class ConfigurationError(NKLLONError):
    """Exception raised for configuration issues."""

    pass
