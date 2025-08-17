from fastapi import APIRouter, Depends, HTTPException, Header
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session
from ..schemas import LoginRequest, Token
from ..auth import create_access_token, verify_password
from ..config import settings
from ..dependencies import get_db_for_tenant, TENANT_HEADER
from ..models import User, RoleEnum
from sqlalchemy import select
from fastapi.security import OAuth2PasswordRequestForm
from ..database import db_session, set_search_path
import logging
router = APIRouter(prefix="/auth", tags=["auth"]) 
TENANT_HEADER = "X-Tenant-ID"
api_key_header = APIKeyHeader(name=TENANT_HEADER, auto_error=False)


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    - If client_id == "SUPER" => check SUPERADMIN creds; issue SUPERADMIN token.
    - Else authenticate against tenant.users and issue tenant-scoped token.
    """
    tenant_id = form_data.client_id  # treat client_id as tenant_id
    username = form_data.username
    password = form_data.password
    print(f"DEBUG: tenant_id: {tenant_id}")
    if tenant_id == "SUPER":
        print(f"DEBUG: username: {username}")
        print(f"DEBUG: password: {'*' * len(password)}")
        print(f"DEBUG: settings.SUPERADMIN_USERNAME: {settings.SUPERADMIN_USERNAME}")
        print(f"DEBUG: settings.SUPERADMIN_PASSWORD: {'*' * len(password) if settings.SUPERADMIN_PASSWORD else 'Not set'}")
        
        logging.info("username:", username)
        logging.info("password:", password)
        logging.info("settings.SUPERADMIN_USERNAME:", settings.SUPERADMIN_USERNAME)
        logging.info("settings.SUPERADMIN_PASSWORD:", settings.SUPERADMIN_PASSWORD)
        if username == settings.SUPERADMIN_USERNAME and password == settings.SUPERADMIN_PASSWORD:
            token = create_access_token(
                user_id=None,
                username=username,
                role=RoleEnum.SUPERADMIN,
                tenant_id="SUPER"
            )
            return Token(access_token=token)
        print("sjc2")
        raise HTTPException(status_code=401, detail="Invalid superadmin credentials")

    # Tenant user flow
    with db_session() as s:  # directly open session
        # validate schema name quickly
        if not tenant_id or not tenant_id.replace("_", "").isalnum():
            raise HTTPException(status_code=400, detail="Invalid tenant id")
        set_search_path(s, tenant_id)

        user = s.scalar(select(User).where(User.username == username, User.is_deleted == False))
        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        token = create_access_token(
            user_id=user.id,
            username=user.username,
            role=user.role,
            tenant_id=tenant_id
        )
        return Token(access_token=token)
