#user related data models, currently only for request/response validation in the auth router, not ODM/ORM mongodb models
from pydantic import BaseModel, Field

#seperate models for user registration, login, and response to ensure clear validation and response structures
class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=64)


class UserLogin(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=64)

class UserResponse(BaseModel): #expected user response, #would match /register returns
    id: str
    username: str

class TokenResponse(BaseModel): #expected token response, #would match /login returns
    access_token: str
    token_type: str