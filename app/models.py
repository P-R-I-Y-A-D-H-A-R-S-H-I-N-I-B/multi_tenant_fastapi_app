from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, relationship, Mapped, mapped_column
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, Index, Enum as SAEnum
from enum import Enum

class Base(DeclarativeBase):
    pass

# ----------------------------
# PUBLIC schema models
# ----------------------------
class Tenant(Base):
    __tablename__ = "tenants"
    # NOTE: This table is always created/queried in PUBLIC schema.
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    schema_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

# ----------------------------
# TENANT schema models (search_path driven)
# ----------------------------
class RoleEnum(str, Enum):
    ADMIN = "ADMIN"
    MANAGER = "MANAGER"
    EMPLOYEE = "EMPLOYEE"
    SUPERADMIN = "SUPERADMIN"  # only used in JWT, not stored in tenant schemas

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(100), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Unique username within a tenant achieved via unique index on username (per schema)

Index("ix_users_username_unique", User.username, unique=True)

class Resource(Base):
    __tablename__ = "resources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

Index("ix_resources_name", Resource.name)
Index("ix_resources_owner_id", Resource.owner_id)

class AuditAction(str, Enum):
    CREATED_RESOURCE = "CREATED_RESOURCE"
    UPDATED_RESOURCE = "UPDATED_RESOURCE"
    DELETED_RESOURCE = "DELETED_RESOURCE"
    CREATED_USER = "CREATED_USER"
    DELETED_USER = "DELETED_USER"

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

Index("ix_audit_logs_timestamp", AuditLog.timestamp)
