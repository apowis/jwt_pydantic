"""
A Starlette middleware that can be used with a JWTPydantic model.
"""
# pylint: disable=too-few-public-methods
from typing import Dict, Optional, Union

from jose import jwt, JWTError
from jose.constants import ALGORITHMS
from pydantic import BaseModel, ValidationError  # pylint: disable=no-name-in-module
from starlette.datastructures import Headers
from starlette.responses import PlainTextResponse
from starlette.types import ASGIApp, Receive, Scope, Send


class JWTPydantic(BaseModel):
    """
    Enable easy checking of JWT claims, whilst also using
    the powerful features of Pydantic models, to verify the contents
    of the claims being used.
    Example usage:
        >>> class MyJWT(JWTPydantic):
        >>>     foo: int
        >>>     bar: str
        >>> SECRET_KEY = 'mykey'
        >>> claims = {'foo': 10, 'bar': 'hello'}
        >>> token = MyJWT.new_token(claims, SECRET_KEY)
        >>> MyJWT(token, SECRET_KEY)
        MyJWT(foo=10, bar='hello')
    """

    def __init__(
        self,
        jwt_token: Union[str, bytes],
        key: Union[str, bytes],
        algorithm: str = ALGORITHMS.HS256,
        jose_opts: Optional[Dict] = None,
    ):
        """
        Args:
            jwt_token (str | bytes): The JWT token that needs to be verified
                against the specified Pydantic model.
            key (str): The key to use for signing the claim set. Can be
                individual JWK or JWK set.
            algorithm (str): The algorithm to use for signing the
                the claims.  Defaults to HS256.
            jose_opts (dict): Provide extra keyword arguments (such as
                access_token) used by python-jose to decode the jwt_token.
        """
        jose_opts = jose_opts if jose_opts else {}
        data = jwt.decode(jwt_token, key, algorithms=[algorithm], **jose_opts)
        super().__init__(**data)

    @classmethod
    def new_token(
        cls,
        claims: dict,
        key: Union[str, bytes],
        algorithm: str = ALGORITHMS.HS256,
        jose_opts: Optional[Dict] = None,
    ) -> str:
        """
        Takes in new claims, a key and algorithm and returns a new
        JWT token. The claims key/values are checked against the
        Pydantic BaseModel.
        Args:
            claims (dict): A claims set to sign
            key (str): The key to use for signing the claim set. Can be
                individual JWK or JWK set.
            algorithm (str): The algorithm to use for signing the
                the claims.  Defaults to HS256.
            jose_opts (dict): Provide extra keyword arguments (such as
                access_token) used by python-jose to encode the JWT token.
        Returns:
            str: The string representation of the header, claims, and signature.
        """
        jose_opts = jose_opts if jose_opts else {}
        token = jwt.encode(claims, key, algorithm, **jose_opts)
        cls(token, key, algorithm, jose_opts)  # test new token passes model
        return token

    @classmethod
    def verify_token(
        cls,
        jwt_token: Union[str, bytes],
        key: Union[str, bytes],
        algorithm: str = ALGORITHMS.HS256,
        jose_opts: Optional[Dict] = None,
    ) -> None:
        """
        Args:
            jwt_token (str | bytes): The JWT token that needs to be verified
                against the specified Pydantic model.
            key (str): The key to use for signing the claim set. Can be
                individual JWK or JWK set.
            algorithm (str): The algorithm to use for signing the
                the claims.  Defaults to HS256.
            jose_opts (dict): Provide extra keyword arguments (such as
                access_token) used by python-jose to decode the jwt_token.
        """
        cls(jwt_token, key, algorithm, jose_opts)


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
            response = PlainTextResponse(check_model, 403)
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
