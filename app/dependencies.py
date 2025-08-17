from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session
from .database import db_session, set_search_path
from .config import settings
from .auth import get_current_claims

# Header name for tenant id
TENANT_HEADER = "X-Tenant-ID"


def get_db_for_public():
    # For public schema operations (tenants registry)
    with db_session() as s:
        # ensure we're in public
        set_search_path(s, settings.PUBLIC_SCHEMA)
        yield s


def get_db_for_tenant(tenant_id: str = Header(..., alias=TENANT_HEADER)):
    # Ensure tenant header present; search_path is set to that schema
    with db_session() as s:
        # Validate schema name format quickly (alphanumeric and underscore)
        print("tenant id:",tenant_id)
        if not tenant_id or not tenant_id.replace("_", "").isalnum():
            raise HTTPException(status_code=400, detail="Invalid tenant id")
        set_search_path(s, tenant_id)
        yield s


def get_current_user_info(claims=Depends(get_current_claims)):
    return {
        "user_id": claims.get("uid"),
        "username": claims.get("sub"),
        "role": claims.get("role"),
        "tenant_id": claims.get("tenant_id"),
    }
