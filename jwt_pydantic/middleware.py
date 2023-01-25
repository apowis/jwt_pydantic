"""
An example Starlette middleware that can be used with a JWTPydantic model.
This can be easily modified by changing the __call__ method to return
different responses.
"""
# pylint: disable=too-few-public-methods
from typing import Optional, Union

from jose import JWTError
from pydantic import ValidationError
from starlette.datastructures import Headers
from starlette.responses import PlainTextResponse, Response
from starlette.types import ASGIApp, Receive, Scope, Send

from jwt_pydantic.main import JWTPydantic


class JWTPydanticMiddleware:
    """
    A Starlette middleware that can be used with a JWTPydantic model.
    """

    def __init__(
        self,
        app: ASGIApp,
        header_name: str,
        jwt_pydantic_model: JWTPydantic,
        jwt_key: Union[str, bytes],
    ) -> None:
        self.app = app
        self.header_name = header_name
        self.jwt_pydantic_model = jwt_pydantic_model
        self.jwt_key = jwt_key

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] not in ("http", "websocket"):  # pragma: no cover
            await self.app(scope, receive, send)
            return

        headers = Headers(scope=scope)
        check_model = self._check_pydantic_model(headers)
        if check_model:  # errror found.
            response = self.bad_response(check_model)
            await response(scope, receive, send)
            return

        await self.app(scope, receive, send)

    def _check_pydantic_model(self, headers: Headers) -> Optional[str]:
        """
        Checks the supplied model and returns the exception string if one
        is found. If no error is found, then None is returned.
        """
        jwt_token = headers.get(self.header_name)
        if not jwt_token:
            return f"No {self.header_name} header found"
        try:
            self.jwt_pydantic_model.verify_token(jwt_token, self.jwt_key)
        except JWTError as err:
            return str(err)
        except ValidationError as err:
            return str(err)

        return None

    def bad_response(self, token_error: str) -> Response:
        """
        Override this method to return different responses
        for bad tokens
        """
        return PlainTextResponse(token_error, 403)
