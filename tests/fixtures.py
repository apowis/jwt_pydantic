from pydantic import Field
import pytest
from starlette.responses import JSONResponse

from jwt_pydantic import JWTPydantic, JWTPydanticMiddleware

SECRET_KEY = "mykey"


class MyJWT(JWTPydantic):
    foo: int
    bar: int = Field(ge=0, le=10)


class MyMiddleware(JWTPydanticMiddleware):
    def bad_response(self, token_error: str) -> JSONResponse:
        """Overriding this to test bad_response override"""
        return JSONResponse(
            {"bad_token": token_error}, status_code=403
        )


@pytest.fixture
def claims():
    return {"foo": 1, "bar": 10}
