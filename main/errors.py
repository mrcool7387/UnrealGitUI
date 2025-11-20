class ConfigError(Exception):
    """Exception raised for errors in the configuration."""
    pass

class PyProjectError(Exception):
    """Exception for pyproject.toml validation errors."""
    pass

class MissingDotEnvFile(Exception):
    """Exception for Missing `.env` File"""
    pass

class MissingGithubToken(Exception):
    """Exception if Github Token is Missing"""
    pass