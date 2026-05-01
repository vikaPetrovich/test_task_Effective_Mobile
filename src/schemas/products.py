from pydantic import BaseModel


class ProductCreateRequest(BaseModel):
    name: str


class ProductUpdateRequest(BaseModel):
    name: str


class ProductResponse(BaseModel):
    id: int
    name: str
    owner_id: int