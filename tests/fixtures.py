from pydantic import Field
import pytest

from jwt_pydantic import JWTPydantic

SECRET_KEY = "mykey"


class MyJWT(JWTPydantic):
    foo: int
    bar: int = Field(ge=0, le=10)


@pytest.fixture
def claims():
    return {"foo": 1, "bar": 10}
