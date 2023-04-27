"""
Actuator Entrypoint Tests
"""
from starlette.status import HTTP_301_MOVED_PERMANENTLY


class TestActuatorEntryPoint:

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
