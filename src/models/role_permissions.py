from sqlalchemy import Column, Integer, Boolean, ForeignKey, UniqueConstraint

from src.db.session import Base


class RolePermission(Base):
    __tablename__ = "role_permissions"

    __table_args__ = (
        UniqueConstraint(
            "role_id",
            "module_id",
            name="uq_role_permissions_role_module",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)

    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    module_id = Column(Integer, ForeignKey("system_modules.id"), nullable=False)

    read_own_permission = Column(Boolean, default=False)
    read_all_permission = Column(Boolean, default=False)

    create_permission = Column(Boolean, default=False)

    update_own_permission = Column(Boolean, default=False)
    update_all_permission = Column(Boolean, default=False)

    delete_own_permission = Column(Boolean, default=False)
    delete_all_permission = Column(Boolean, default=False)