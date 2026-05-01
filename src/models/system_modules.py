from sqlalchemy import Column, Integer, String

from src.db.session import Base


class SystemModule(Base):
    __tablename__ = "system_modules"

    id = Column(Integer, primary_key=True, index=True)

    code_name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)