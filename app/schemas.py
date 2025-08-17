from pydantic import BaseModel, Field, constr
from typing import Optional, List
from datetime import datetime
from .models import RoleEnum, AuditAction

# --------- Auth ---------
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class LoginRequest(BaseModel):
    username: constr(min_length=3, max_length=100)
    password: constr(min_length=6, max_length=128)

# --------- Tenant (public) ---------
class TenantCreate(BaseModel):
    name: constr(min_length=3, max_length=100)
    schema_name: constr(min_length=3, max_length=100)

class TenantOut(BaseModel):
    id: int
    name: str
    schema_name: str

    class Config:
        from_attributes = True

# --------- Users (tenant) ---------
class UserCreate(BaseModel):
    username: constr(min_length=3, max_length=100)
    password: constr(min_length=6, max_length=128)
    role: RoleEnum

class UserOut(BaseModel):
    id: int
    username: str
    role: RoleEnum

    class Config:
        from_attributes = True

# --------- Resources (tenant) ---------
class ResourceCreate(BaseModel):
    name: constr(min_length=1, max_length=150)
    description: Optional[constr(max_length=500)] = None
    owner_id: int

class ResourceUpdate(BaseModel):
    name: Optional[constr(min_length=1, max_length=150)] = None
    description: Optional[constr(max_length=500)] = None

class ResourceOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    owner_id: int

    class Config:
        from_attributes = True

# --------- Audits ---------
class AuditLogOut(BaseModel):
    id: int
    user_id: Optional[int]
    action: AuditAction
    timestamp: datetime

    class Config:
        from_attributes = True

# --------- Search & Pagination ---------
class ResourceSearchQuery(BaseModel):
    name: Optional[str] = Field(None, description="Case-insensitive partial match")
    owner_id: Optional[int] = None
    page: int = Field(1, ge=1)
    size: int = Field(10, ge=1, le=100)

class PaginatedResources(BaseModel):
    total: int
    page: int
    size: int
    items: List[ResourceOut]
