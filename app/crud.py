from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select, func, update
from .models import User, Resource, AuditLog, AuditAction, RoleEnum
from .auth import hash_password

# ---------- Utilities ----------

def log_action(db: Session, user_id: Optional[int], action: AuditAction):
    db.add(AuditLog(user_id=user_id, action=action))

# ---------- Users ----------

def count_users(db: Session) -> int:
    return db.scalar(select(func.count()).select_from(User).where(User.is_deleted == False))


def create_user(db: Session, username: str, password: str, role: str, acting_user_id: int) -> User:
    # Enforce per-tenant max users = 50
    if count_users(db) >= 50:
        raise ValueError("Tenant user capacity reached (50)")

    existing = db.scalar(select(User).where(User.username == username, User.is_deleted == False))
    if existing:
        raise ValueError("Username already exists in tenant")
    u = User(username=username, password_hash=hash_password(password), role=role)
    db.add(u)
    db.flush()
    log_action(db, acting_user_id, AuditAction.CREATED_USER)
    return u


def soft_delete_user(db: Session, user_id: int, acting_user_id: int):
    user = db.get(User, user_id)
    if not user or user.is_deleted:
        raise ValueError("User not found")
    user.is_deleted = True
    db.flush()
    log_action(db, acting_user_id, AuditAction.DELETED_USER)

# ---------- Resources ----------

def count_resources(db: Session) -> int:
    return db.scalar(select(func.count()).select_from(Resource).where(Resource.is_deleted == False))


def count_resources_by_owner(db: Session, owner_id: int) -> int:
    return db.scalar(
        select(func.count()).select_from(Resource).where(Resource.owner_id == owner_id, Resource.is_deleted == False)
    )


def create_resource(db: Session, name: str, description: Optional[str], owner_id: int, acting_user_id: int) -> Resource:
    # Enforce tenant-wide limit = 500 resources
    if count_resources(db) >= 500:
        raise ValueError("Tenant resource capacity reached (500)")

    # Per-user resource limit = 10
    if count_resources_by_owner(db, owner_id) >= 10:
        raise ValueError("Owner already has 10 resources")

    # Ensure owner exists & not deleted
    owner = db.get(User, owner_id)
    if not owner or owner.is_deleted:
        raise ValueError("Owner not found")

    r = Resource(name=name, description=description, owner_id=owner_id)
    db.add(r)
    db.flush()
    log_action(db, acting_user_id, AuditAction.CREATED_RESOURCE)
    return r


def update_resource(db: Session, resource_id: int, name: Optional[str], description: Optional[str], acting_user_id: int) -> Resource:
    r = db.get(Resource, resource_id)
    if not r or r.is_deleted:
        raise ValueError("Resource not found")
    if name is not None:
        r.name = name
    if description is not None:
        r.description = description
    db.flush()
    log_action(db, acting_user_id, AuditAction.UPDATED_RESOURCE)
    return r


def delete_resource(db: Session, resource_id: int, acting_user_id: int):
    r = db.get(Resource, resource_id)
    if not r or r.is_deleted:
        raise ValueError("Resource not found")
    r.is_deleted = True
    db.flush()
    log_action(db, acting_user_id, AuditAction.DELETED_RESOURCE)

# ---------- Search & Pagination ----------

def search_resources(db: Session, name: Optional[str], owner_id: Optional[int], page: int, size: int) -> Tuple[int, List[Resource]]:
    stmt = select(Resource).where(Resource.is_deleted == False)
    count_stmt = select(func.count()).select_from(Resource).where(Resource.is_deleted == False)

    if name:
        like = f"%{name.lower()}%"
        stmt = stmt.where(func.lower(Resource.name).like(like))
        count_stmt = count_stmt.where(func.lower(Resource.name).like(like))
    if owner_id:
        stmt = stmt.where(Resource.owner_id == owner_id)
        count_stmt = count_stmt.where(Resource.owner_id == owner_id)

    total = db.scalar(count_stmt)
    items = db.scalars(stmt.order_by(Resource.id).offset((page - 1) * size).limit(size)).all()
    return total, items
