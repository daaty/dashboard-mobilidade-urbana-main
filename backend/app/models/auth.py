from pydantic import BaseModel
from typing import Optional

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
    roles: list[str]
