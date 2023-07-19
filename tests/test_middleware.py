from typing import Optional

from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import Response

from jwt_pydantic import JWTPydantic
# from jwt_pydantic.middleware import JWTPydanticMiddleware
from tests.fixtures import claims, MyJWT, MyMiddleware, SECRET_KEY


app = FastAPI()
app.add_middleware(
    MyMiddleware,
    header_name="jwt",
    jwt_pydantic_model=MyJWT,
    jwt_key=SECRET_KEY,
)


@app.get("/")
def homepage():
    return "Hello world"


client = TestClient(app)


def get_home_page(headers: Optional[dict] = None) -> Response:
    return client.get("/", headers=headers)


def test_jwt(claims: dict):
    headers = {"jwt": MyJWT.new_token(claims, SECRET_KEY)}
    resp = get_home_page(headers)
    assert resp.status_code == 200


def test_no_jwt():
    resp = get_home_page()
    assert resp.status_code == 403
    assert resp.json() == {
        "bad_token": "No jwt header found"
    }


def test_bad_jwt():
    resp = get_home_page(headers={"jwt": "bad_token"})
    assert resp.status_code == 403
    assert resp.json() == {
        "bad_token": "Not enough segments"
    }


def test_bad_pydantic_model():
    class WrongModel(JWTPydantic):
        a: int

    token = WrongModel.new_token({"a": 0}, SECRET_KEY)
    resp = get_home_page({"jwt": token})
    assert resp.status_code == 403
