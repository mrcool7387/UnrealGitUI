class ConfigError(Exception):
    """Exception raised for errors in the configuration."""
    pass

class PyProjectError(Exception):
    """Custom exception for pyproject.toml validation errors."""
    pass