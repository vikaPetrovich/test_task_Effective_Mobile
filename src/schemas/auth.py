from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserRegisterRequest(BaseModel):
    first_name: str
    last_name: str
    middle_name: str | None = None
    email: EmailStr
    password: str
    password_repeat: str


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    first_name: str | None
    last_name: str | None
    middle_name: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None

    class Config:
        from_attributes = True


class AuthTokenResponse(BaseModel):
    access_token: str
    token_type: str