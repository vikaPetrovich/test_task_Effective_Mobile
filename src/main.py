from fastapi import FastAPI
import uvicorn

from src.routers.auth import router as auth_router
from src.routers.users import router as users_router
from src.routers.products import router as products_router
from src.routers.user_role_management import router as user_role_management_router


app = FastAPI(title="Auth and Access Control API")

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(products_router)
app.include_router(user_role_management_router)

if __name__ == "__main__":
    uvicorn.run("src.main:app")