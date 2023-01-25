# jwt-pydantic

JWT claim sets are becoming more complex and harder to manage. Writing validators for these claims checks is time consuming.

This package uses the power of Pydantic models, to make life a bit easier.

We have also included a Starlette middleware, which can be easily used in FastAPI, as shown [here](#fastapi-middleware).

## Example

Let's say our JWT token has the claims set below:
```python
claims = {
    "firstname": "David",
    "surname": "Bowie",
    "best_album": "Hunky Dory"
}
```

We can use `jwt-pydantic` to simplify the generation and verification of such tokens. First we declare the Pydantic model, by subclassing `JWTPydantic`:

```python
from jwt_pydantic import JWTPydantic

class MyJWT(JWTPydantic):
    firstname: str
    surname: str
    best_album: str
```

To generate a new JWT token, using the claims above, we do the following:

```python
token = MyJWT.new_token(claims=claims, key="SECRET_KEY")
```

We can then verify this token easily as follows
```python
MyJWT.verify_token(token, key="SECRET_KEY")
```

We can also return the decoded JWT token as our Pydantic model, to be used elsewhere:
```python
decoded_jwt = MyJWT(token, key="SECRET_KEY")
print(decoded_jwt.firstname)  # David
```

## FastAPI Middleware

It is also easy to declare a new JWTPydantic model and use this in middleware, as shown below.

```python
# main.py
from fastapi import FastAPI
from jwt_pydantic import JWTPydantic, JWTPydanticMiddleware

SECRET_KEY = "mykey"

class MyJWT(JWTPydantic):
    foo: int

app = FastAPI()
app.add_middleware(
    JWTPydanticMiddleware,
    header_name="jwt",
    jwt_pydantic_model=MyJWT,
    jwt_key=SECRET_KEY,
)

@app.get("/")
def homepage():
    return "Hello world"
```

We can run this code easily using uvicorn (`uvicorn main:app --reload`), and then using python on a different shell, we can test this to show it in action:
```python
import requests
requests.get('http://127.0.0.1:8000/', headers={'jwt': MyJWT.new_token({'foo': 1}, 'mykey')})  # b'Hello World'
```

If we want to change the response when the JWT token is bad, you can override the method in `bad_response` in `JWTPydanticMiddleware`, such as below:

```python
class MyMiddleware(JWTPydanticMiddleware):
    def bad_response(self, token_error: str) -> JSONResponse:
        """Changing standard response to be a JSONResponse"""
        return JSONResponse(
            {"bad_token": token_error}, status_code=403
        )
```

## python-jose keyword arguments

`JWTPydantic` uses [python-jose](https://pypi.org/project/python-jose/) to manage the JWT tokens. The extra features that are provided using this package can be easily used through the keyword argument `jose_opts`. For instance, we can add the 'at_hash' claim to our JWT token by specifying the keyword argument `access_token`.

```python
MyJWT.new_token(
    claims,
    SECRET_KEY,
    jose_opts={"access_token": "1234"},
)
```

