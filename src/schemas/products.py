from pydantic import BaseModel


class ProductCreateRequest(BaseModel):
    name: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Test product"
            }
        }
    }


class ProductUpdateRequest(BaseModel):
    name: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Updated product"
            }
        }
    }


class ProductResponse(BaseModel):
    id: int
    name: str
    owner_id: int