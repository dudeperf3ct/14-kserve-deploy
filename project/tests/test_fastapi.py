from http import HTTPStatus

from fastapi.testclient import TestClient

from project.app import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == HTTPStatus.OK


def test_healthcheck_endpoint():
    response = client.get("/healthcheck")
    assert response.status_code == HTTPStatus.OK


# # TODO: not working as expected
# def test_classify_endpoint():
#     response = client.post(
#         "/classify", data=json.dumps({"input_text": "a"})
#     )  # min length should be 2
#     assert response.status_code == 422  # Unprocessable Entity
#     # response = client.post("/classify", data=json.dumps({"input_text": "this is positive sentence"}))  # not working as expected
#     # assert response.status_code == HTTPStatus.OK
