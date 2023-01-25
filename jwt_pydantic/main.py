"""
A Starlette middleware that can be used with a JWTPydantic model.
"""
from typing import Dict, Optional, Union

from jose import jwt
from jose.constants import ALGORITHMS
from pydantic import BaseModel  # pylint: disable=no-name-in-module


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
