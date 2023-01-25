"""
Simple module to create and validate JWT tokens using
Pydantic models and python-jose.
"""
from jwt_pydantic.main import JWTPydantic
from jwt_pydantic.middleware import JWTPydanticMiddleware
