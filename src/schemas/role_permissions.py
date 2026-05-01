from pydantic import BaseModel


class RolePermissionResponse(BaseModel):
    id: int

    role_id: int
    role_name: str

    module_id: int
    module_code: str

    read_own_permission: bool
    read_all_permission: bool

    create_permission: bool

    update_own_permission: bool
    update_all_permission: bool

    delete_own_permission: bool
    delete_all_permission: bool


class RolePermissionUpdateRequest(BaseModel):
    read_own_permission: bool | None = None
    read_all_permission: bool | None = None

    create_permission: bool | None = None

    update_own_permission: bool | None = None
    update_all_permission: bool | None = None

    delete_own_permission: bool | None = None
    delete_all_permission: bool | None = None


class RolePermissionUpdateByNamesRequest(RolePermissionUpdateRequest):
    role_name: str
    module_code: str