"""
Application settings module.
"""

from pydantic import BaseSettings

from app.version import __version__


class ApplicationSettings(BaseSettings):
    """Define application configuration model.

    Constructor will attempt to determine the values of any fields not passed
    as keyword arguments by reading from the environment. Default values will
    still be used if the matching environment variable is not set.

    Environment variables:
        * FASTAPI_DEBUG
        * FASTAPI_PROJECT_NAME
        * FASTAPI_PROJECT_DESCRIPTION
        * FASTAPI_USE_LIMITER
        * FASTAPI_VERSION
        * FASTAPI_DOCS_URL

    Attributes:
        DEBUG (bool): FastAPI logging level. You should disable this for
            production.
        PROJECT_NAME (str): FastAPI project name.
        PROJECT_DESCRIPTION (str): FastAPI project description.
        USE_LIMITER (bool): Enable rate limiter middleware.
        MAX_REQUESTS (int): Maximum number of requests per time limit.
        REQUEST_TIME_LIMIT (int): Time limit in seconds.
        VERSION (str): Application version.
        DOCS_URL (str): Path where swagger ui will be served at.
    """

    DEBUG: bool = True
    PROJECT_NAME: str = "API Gateway Service"
    PROJECT_DESCRIPTION: str = "Fast Gateway helps manage your microservices communication. 🚀"
    USE_LIMITER: bool = False
    MAX_REQUESTS: int = 10
    REQUEST_TIME_LIMIT: int = 60
    VERSION: str = __version__
    DOCS_URL: str = "/docs"

    # All your additional application configuration should go either here or in
    # separate file in this submodule.

    class Config:
        """Config subclass needed to customize BaseSettings settings.
        Attributes:
            case_sensitive (bool): When case_sensitive is True, the environment
                variable names must match field names (optionally with a prefix)
            env_prefix (str): The prefix for environment variable.
        Resources:
            https://pydantic-docs.helpmanual.io/usage/settings/
        """

        case_sensitive = True
        env_prefix = "FASTAPI_"
