from typing import List, Optional
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class UserPublic(BaseModel):
    id: int
    username: str
    full_name: str
    role: str
    permissions: List[str]
    is_active: bool


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserPublic


class ForgotPasswordRequest(BaseModel):
    username: str = Field(..., min_length=1)


class ForgotPasswordResponse(BaseModel):
    message: str


class ResetPasswordRequest(BaseModel):
    token: str = Field(..., min_length=6)
    new_password: str = Field(..., min_length=6)
    confirm_password: str = Field(..., min_length=6)


class ResetPasswordResponse(BaseModel):
    message: str
