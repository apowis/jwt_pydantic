"""
Example implementation of using JWTPydantic, alongside
FastAPI's feature, APIKey.
"""
from fastapi import FastAPI
from fastapi.security.api_key import APIKeyHeader, APIKey
from fastapi import Depends, Security, HTTPException
from starlette.status import HTTP_403_FORBIDDEN
from jwt_pydantic import JWTPyantic


SECRET_KEY = "mykey"


api_key_header = APIKeyHeader(name="access_token", auto_error=False)
app = FastAPI()


class MyJWT(JWTPyantic):
    foo: int


async def get_api_key(api_key_header: str = Security(api_key_header)):
    if not api_key_header:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Could not validate API KEY"
        )
    try:
        MyJWT.verify_token(api_key_header, SECRET_KEY)
    except Exception:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Could not validate API KEY"
        )
    return api_key_header


@app.get("/secure")
async def secure_page(api_key: APIKey = Depends(get_api_key)):
    return {"default variable": api_key}
