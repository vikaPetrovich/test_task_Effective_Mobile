from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserUpdateRequest(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    middle_name: str | None = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "first_name": "Иван",
                "last_name": "Иванов",
                "middle_name": "Иванович"
            }
        }
    }

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