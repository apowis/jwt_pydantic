"""
"""
from pydantic import Field, ValidationError
import pytest

from jwt_pydantic import JWTPydantic
from tests.fixtures import claims, MyJWT, SECRET_KEY


def test_new_token(claims):
    token = MyJWT.new_token(claims, SECRET_KEY)
    assert (
        token
        == "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmb28iOjEsImJhciI6MTB9.evlwpdeWDTJp-emaw8J6ZGqAb77_3hQ7eQihsdA9DCA"
    )
    MyJWT.verify_token(token, SECRET_KEY)


def test_no_verify(claims):
    token = MyJWT.new_token(claims, SECRET_KEY)
    MyJWT.verify_token(
        token,
        key="222",  # change key, as no need to verify
        jose_opts={"options": {"verify_signature": False}},
    )


def test_bad_pydantic_claims(claims):
    claims["bar"] = 1000
    with pytest.raises(ValidationError):
        MyJWT.new_token(claims, SECRET_KEY)
    with pytest.raises(ValidationError):
        MyJWT.new_token({"bad_fields": "a"}, SECRET_KEY)


def test_access_token(claims):
    token = MyJWT.new_token(
        claims,
        SECRET_KEY,
        jose_opts={"access_token": "1234"},
    )
    MyJWT.verify_token(token, SECRET_KEY, jose_opts={"access_token": "1234"})
