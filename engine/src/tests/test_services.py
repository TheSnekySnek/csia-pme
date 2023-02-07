import pytest
from fastapi.testclient import TestClient
from main import app
from database import get_session
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from pytest_httpserver import HTTPServer


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )

    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
@pytest.mark.anyio
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="service_instance")
def service_instance_fixture(httpserver: HTTPServer):
    httpserver.expect_request("/status").respond_with_json({}, status=200)
    httpserver.expect_request("/compute").respond_with_json({}, status=200)

    yield httpserver

    httpserver.clear()


service_1 = {
    "name": "Service 1",
    "slug": "service-1",
    "url": "http://test-service-1.local",
    "summary": "string",
    "description": "string",
    "data_in_fields": [
        {
            "name": "string",
            "type": [
                "image/jpeg"
            ]
        }
    ],
    "data_out_fields": [
        {
            "name": "string",
            "type": [
                "image/jpeg"
            ]
        }
    ]
}

service_2 = {
    "name": "Service 2",
    "slug": "service-2",
    "url": "http://test-service-2.local",
    "summary": "string",
    "description": "string",
    "data_in_fields": [
        {
            "name": "string",
            "type": [
                "image/jpeg"
            ]
        }
    ],
    "data_out_fields": [
        {
            "name": "string",
            "type": [
                "image/jpeg"
            ]
        }
    ]
}


def test_create_service(client: TestClient, service_instance: HTTPServer):
    # Change the URL of the service to match the mocked service
    service_copy = service_1.copy()
    service_copy["url"] = service_instance.url_for("")

    service_response = client.post("/services", json=service_copy)

    assert service_response.status_code == 200


def test_get_service(client: TestClient, service_instance: HTTPServer):
    # Change the URL of the service to match the mocked service
    service_copy = service_1.copy()
    service_copy["url"] = service_instance.url_for("")

    service_response = client.post("/services", json=service_copy)
    service_response_data = service_response.json()

    service_response = client.get(f"/services/{service_response_data['id']}")

    assert service_response.status_code == 200


def test_get_services(
    client: TestClient,
    service_instance: HTTPServer,
):
    # Change the URL of the services to match the mocked services
    service_1_copy = service_1.copy()
    service_1_copy["url"] = service_instance.url_for("")

    service_2_copy = service_2.copy()
    service_2_copy["url"] = service_instance.url_for("")

    # Create the services
    client.post("/services/", json=service_1_copy)
    client.post("/services/", json=service_2_copy)

    services_response = client.get("/services")
    services_response_data = services_response.json()

    assert services_response.status_code == 200
    assert len(services_response_data) == 2


def test_delete_service(client: TestClient, service_instance: HTTPServer):
    # Change the URL of the service to match the mocked service
    service_copy = service_1.copy()
    service_copy["url"] = service_instance.url_for("")

    service_response = client.post("/services", json=service_copy)
    service_response_data = service_response.json()

    service_response = client.delete(f"/services/{service_response_data['id']}")

    assert service_response.status_code == 204


def test_update_service(client: TestClient, service_instance: HTTPServer):
    # Change the URL of the service to match the mocked service
    service_copy = service_1.copy()
    service_copy["url"] = service_instance.url_for("")

    service_response = client.post("/services", json=service_copy)
    service_response_data = service_response.json()

    service_response = client.patch(
        f"/services/{service_response_data['id']}",
        json={
            "summary": "new summary"
        }
    )
    service_response_data = service_response.json()

    assert service_response.status_code == 200
    assert service_response_data["updated_at"] != "null"
    assert service_response_data["summary"] == "new summary"


def test_create_service_no_body(client: TestClient):
    response = client.post("/services")

    assert response.status_code == 422


def test_create_service_bad_slug(client: TestClient):
    service_copy = service_1.copy()
    service_copy["slug"] = "Bad Slug"

    service_response = client.post("/services", json=service_copy)

    assert service_response.status_code == 422


def test_read_service_non_existent(client: TestClient):
    response = client.get("/services/00000000-0000-0000-0000-000000000000")

    assert response.status_code == 404
    assert response.json() == {"detail": "Service Not Found"}


def test_delete_service_non_existent(client: TestClient):
    response = client.delete("/services/00000000-0000-0000-0000-000000000000")

    assert response.status_code == 404
    assert response.json() == {"detail": "Service Not Found"}


def test_patch_service_non_existent(client: TestClient):
    response = client.patch("/services/00000000-0000-0000-0000-000000000000", json={"status": "available"})

    assert response.status_code == 404
    assert response.json() == {"detail": "Service Not Found"}


def test_read_service_non_processable(client: TestClient):
    response = client.get("/services/bad_id")

    assert response.status_code == 422
    assert response.json()["detail"][0]["type"] == "type_error.uuid"


def test_delete_service_non_processable(client: TestClient):
    response = client.delete("/services/bad_id")

    assert response.status_code == 422
    assert response.json()["detail"][0]["type"] == "type_error.uuid"


def test_patch_service_non_processable(client: TestClient):
    response = client.patch("/services/bad_id", json={"status": "available"})

    assert response.status_code == 422
    assert response.json()["detail"][0]["type"] == "type_error.uuid"


def test_create_service_same_slug(client: TestClient, service_instance: HTTPServer):
    # Change the URL of the service to match the mocked service
    service_copy = service_1.copy()
    service_copy["url"] = service_instance.url_for("")

    service_response = client.post("/services", json=service_copy)
    assert service_response.status_code == 200

    service_response = client.post("/services", json=service_copy)
    assert service_response.status_code == 409


def test_service_status_not_ok(client: TestClient, service_instance: HTTPServer):
    # Clear the default endpoints
    service_instance.clear()

    # Set the status endpoint to return an error
    service_instance.expect_request("/status").respond_with_json({}, status=500)

    # Change the URL of the service to match the mocked service
    service_copy = service_1.copy()
    service_copy["url"] = service_instance.url_for("")

    # Create the service on the Engine
    service_response = client.post("/services", json=service_copy)

    # Check the output
    assert service_response.status_code == 500


def test_service_unreachable(client: TestClient):
    # Create the service on the Engine
    service_response = client.post("/services", json=service_1)

    # Check the output
    assert service_response.status_code == 503


def test_service_compute(client: TestClient, service_instance: HTTPServer):
    """
    If the following test fails, try to replace the following lines in the `client_fixture` function

    ```
    with TestClient(app) as client:
        yield client
    ```

    instead of

    ```
    client = TestClient(app)
    yield client
    ```

    This makes the tests much slower but it makes the tests pass.

    I do not know why this happens. The order of the execution seems to matter,
    but all tests are isolated.
    """

    # Change the URL of the service to match the mocked service
    service_copy = service_1.copy()
    service_copy["url"] = service_instance.url_for("")

    # Create the service on the Engine
    service_response = client.post("/services", json=service_copy)

    # Send a request to the mocked service through the Engine
    file_to_upload = open("tests/smallest-jpeg-possible.jpg", "rb")
    service_task_response = client.post(f"/{service_copy['slug']}", files={"string": file_to_upload})

    # Check the output
    assert service_task_response.status_code == 200

    service_data = service_response.json()
    service_task_data = service_task_response.json()

    service_task_service_data = service_task_data["service"]

    assert service_data == service_task_service_data
    assert len(service_task_data["data_in"]) == 1