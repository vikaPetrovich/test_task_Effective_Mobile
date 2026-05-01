from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserUpdateRequest(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    middle_name: str | None = None


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    first_name: str | None
    last_name: str | None
    middle_name: str | None
    is_active: bool
    role: str
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None

    class Config:
        from_attributes = True