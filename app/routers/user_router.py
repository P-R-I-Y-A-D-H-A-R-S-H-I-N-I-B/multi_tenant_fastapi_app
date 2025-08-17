from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from ..schemas import UserCreate, UserOut
from ..models import User, RoleEnum
from ..crud import create_user, soft_delete_user
from ..auth import require_tenant_role
from ..dependencies import get_db_for_tenant, get_current_user_info

router = APIRouter(prefix="/users", tags=["users"]) 

@router.post("/", response_model=UserOut, dependencies=[Depends(require_tenant_role((RoleEnum.ADMIN,)))])
def add_user(payload: UserCreate, db: Session = Depends(get_db_for_tenant), me=Depends(get_current_user_info)):
    try:
        u = create_user(db, payload.username, payload.password, payload.role, acting_user_id=me["user_id"])
        return u
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

@router.delete("/{user_id}", dependencies=[Depends(require_tenant_role((RoleEnum.ADMIN,)))])
def delete_user(user_id: int, db: Session = Depends(get_db_for_tenant), me=Depends(get_current_user_info)):
    try:
        if me["user_id"] == user_id:
            raise HTTPException(status_code=400, detail="Admins cannot delete themselves")
        soft_delete_user(db, user_id, acting_user_id=me["user_id"])
        return {"status": "deleted"}
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))