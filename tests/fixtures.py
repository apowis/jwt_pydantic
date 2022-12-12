from pydantic import Field
import pytest

from jwt_pydantic import JWTPyantic

SECRET_KEY = "mykey"


class MyJWT(JWTPyantic):
    foo: int
    bar: int = Field(ge=0, le=10)


@pytest.fixture
def claims():
    return {"foo": 1, "bar": 10}
