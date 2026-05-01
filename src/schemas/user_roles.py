from pydantic import BaseModel, EmailStr


class AssignRoleRequest(BaseModel):
    role_name: str


class AssignRoleResponse(BaseModel):
    user_id: int
    email: EmailStr
    first_name: str | None
    last_name: str | None
    middle_name: str | None
    role_id: int
    role_name: str