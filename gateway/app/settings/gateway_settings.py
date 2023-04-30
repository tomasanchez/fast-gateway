"""
Gateway settings module.
"""
from pydantic import BaseSettings


class GatewaySettings(BaseSettings):
    """Define application configuration model.

    Constructor will attempt to determine the values of any fields not passed
    as keyword arguments by reading from the environment. Default values will
    still be used if the matching environment variable is not set.

    Environment variables:
        * API_GATEWAY_AUTH_SERVICE_URL
        * API_GATEWAY_BOOKING_SERVICE_URL
        * API_GATEWAY_TIMEOUT

    Attributes:
        AUTH_SERVICE_URL (str): Auth service url.
        BOOKING_SERVICE_URL (str): Allocation service url.
        TIMEOUT (int): Timeout for requests.
    """

    AUTH_SERVICE_URL: str = "http://localhost:8000"
    BOOKING_SERVICE_URL: str = "http://localhost:8001"
    TIMEOUT: int = 59

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
        env_prefix = "API_GATEWAY_"
