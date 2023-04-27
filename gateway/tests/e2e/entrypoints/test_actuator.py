"""
Actuator Entrypoint Tests
"""
import pytest
from aioresponses import aioresponses
from starlette.status import HTTP_301_MOVED_PERMANENTLY, HTTP_200_OK, HTTP_500_INTERNAL_SERVER_ERROR

from app.domain.schemas import HealthChecked, ServiceHealthStatus
from app.settings.gateway_settings import GatewaySettings


class TestActuatorEntryPoint:

    @pytest.fixture
    def fake_web(self):
        with aioresponses() as mock:
            yield mock

    def test_root_redirect_to_docs_permanently(self, test_client):
        """
        GIVEN a FastAPI application
        WHEN the root path is requested (GET)
        THEN it is redirected to the docs path
        """

        # when
        response = test_client.get("/").history[0]

        # then
        assert response.status_code == HTTP_301_MOVED_PERMANENTLY
        assert response.headers["location"] == "/docs"

    def test_check_health_with_offline_services(self, test_client):
        """
        GIVEN a FastAPI application
        WHEN the health check path is requested (GET)
        THEN it should return OK, even though other services are offline
        """

        # when
        response = test_client.get("/health")

        # then
        assert response.status_code == HTTP_200_OK

        health_checked = HealthChecked(**response.json()["data"])

        assert health_checked.status == ServiceHealthStatus.OK

    def test_check_health_with_service_error(self, test_client, fake_web):
        """
        GIVEN a FastAPI application, and a mocked service
        WHEN the health check path is requested (GET)
        THEN it should return OK, with the service status as OK
        """
        # given
        settings = GatewaySettings()

        fake_web.get(
            settings.AUTH_SERVICE_URL + "/health",
            status=HTTP_200_OK,
            payload={"fake": "response"},
        )

        # when
        response = test_client.get("/health")
        health_checked = HealthChecked(**response.json()["data"])

        # then
        services = [service.status == ServiceHealthStatus.OK for service in health_checked.services]

        assert any(services)

    def test_check_health_with_service_offline(self, test_client, fake_web):
        """
        GIVEN a FastAPI application, and a mocked service
        WHEN the health check path is requested (GET)
        THEN it should return OK, with the service status as error
        """
        # given
        settings = GatewaySettings()

        fake_web.get(
            settings.AUTH_SERVICE_URL + "/health",
            status=HTTP_500_INTERNAL_SERVER_ERROR,
            payload={"fake": "response"},
        )

        # when
        response = test_client.get("/health")
        health_checked = HealthChecked(**response.json()["data"])

        # then
        services = [service.status == ServiceHealthStatus.ERROR for service in health_checked.services]

        assert any(services)
