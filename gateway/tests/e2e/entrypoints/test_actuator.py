"""
Actuator Entrypoint Tests
"""
import pytest
from aioresponses import aioresponses
from starlette.status import HTTP_301_MOVED_PERMANENTLY, HTTP_200_OK, HTTP_503_SERVICE_UNAVAILABLE, \
    HTTP_429_TOO_MANY_REQUESTS

from app.dependencies import get_redis
from app.domain.schemas import ReadinessChecked, ServiceReadinessStatus
from app.middleware import rate_limiter_middleware
from app.settings.gateway_settings import GatewaySettings
from tests.conftest import DependencyOverrider
from tests.mocks import no_rate_limiter_middleware, FakeRedis


class TestActuatorEntryPoint:

    @pytest.fixture
    def fake_web(self):
        with aioresponses() as mock:
            yield mock

    def test_root_redirect_to_docs_permanently(self, test_client, monkeypatch):
        """
        GIVEN a FastAPI application
        WHEN the root path is requested (GET)
        THEN it is redirected to the docs path
        """

        overrides = {
            rate_limiter_middleware: lambda: no_rate_limiter_middleware
        }

        with DependencyOverrider(overrides=overrides):
            # when
            response = test_client.get("/").history[0]

            # then
            assert response.status_code == HTTP_301_MOVED_PERMANENTLY
            assert response.headers["location"] == "/docs"

    def test_check_readiness_with_offline_services(self, test_client):
        """
        GIVEN a FastAPI application
        WHEN the readiness check path is requested (GET)
        THEN it should return SERVICE UNAVAILABLE
        """
        # given
        redis = FakeRedis(ping=False)

        overrides = {
            rate_limiter_middleware: lambda: no_rate_limiter_middleware,
            get_redis: lambda: redis
        }

        with DependencyOverrider(overrides=overrides):
            # when
            response = test_client.get("/readiness")
            # then
            assert response.status_code == HTTP_503_SERVICE_UNAVAILABLE

    def test_check_readiness_with_service_error(self, test_client, fake_web):
        """
        GIVEN a FastAPI application, and a mocked service
        WHEN the readiness check path is requested (GET)
        THEN it should return OK, with the service status as OK
        """
        # given
        settings = GatewaySettings()
        redis = FakeRedis()

        overrides = {
            rate_limiter_middleware: lambda: no_rate_limiter_middleware,
            get_redis: lambda: redis
        }

        fake_web.get(
            settings.AUTH_SERVICE_URL + "/health",
            status=HTTP_200_OK,
            payload={"fake": "response"},
        )

        with DependencyOverrider(overrides=overrides):
            # when
            response = test_client.get("/readiness")
            health_checked = ReadinessChecked(**response.json()["data"])

            # then
            services = [service.status == ServiceReadinessStatus.OK for service in health_checked.services]

            assert any(services)

    def test_rate_limiter(self, test_client, monkeypatch):
        """
        GIVEN a FastAPI application
        WHEN the rate limiter is enabled and the same IP makes too many requests
        THEN it should return TOO MANY REQUESTS
        """
        # given
        redis = FakeRedis()
        max_requests = 1
        monkeypatch.setenv("FASTAPI_MAX_REQUESTS", str(max_requests))
        monkeypatch.setenv("FASTAPI_USE_LIMITER", "True")
        overrides = {
            get_redis: lambda: redis
        }

        with DependencyOverrider(overrides=overrides):
            # when
            for _ in range(max_requests):
                test_client.get("/health")

            # then
            response = test_client.get("/health")
            assert response.status_code == HTTP_429_TOO_MANY_REQUESTS

    def test_health_endpoint(self, test_client):
        """
        GIVEN a FastAPI application
        WHEN the health check path is requested (GET)
        THEN it should return OK
        """

        # given
        overrides = {
            rate_limiter_middleware: lambda: no_rate_limiter_middleware
        }

        with DependencyOverrider(overrides=overrides):
            # when
            response = test_client.get("/health")

            # then
            assert response.status_code == HTTP_200_OK
