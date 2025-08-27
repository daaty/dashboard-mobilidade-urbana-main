from pydantic import BaseModel
from typing import Optional


class SignupRequest(BaseModel):
    username: str
    email: str
    password: str
    first_name: str
    last_name: str
    signup_token: str

class SignupResponse(BaseModel):
    success: bool
    message: str

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TwoFARequest(BaseModel):
    code: str
    temp_token: str

class TwoFAResponse(BaseModel):
    success: bool
    message: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    first_name: str
    last_name: str
    full_name: str
    roles: list[str]
