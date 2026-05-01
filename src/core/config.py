import os

from dotenv import load_dotenv


load_dotenv()


def get_required_env(name: str) -> str:
    value = os.getenv(name)

    if value is None:
        raise RuntimeError(f"Environment variable {name} is not set")

    return value


DATABASE_URL = get_required_env("DATABASE_URL")
ALEMBIC_DATABASE_URL = get_required_env("ALEMBIC_DATABASE_URL")
SECRET_KEY = get_required_env("SECRET_KEY")

ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
)

ALGORITHM = os.getenv("ALGORITHM", "HS256")