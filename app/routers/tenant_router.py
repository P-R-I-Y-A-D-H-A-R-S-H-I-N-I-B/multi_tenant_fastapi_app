from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..schemas import TenantCreate, TenantOut
from ..auth import require_superadmin
from ..dependencies import get_db_for_public, get_db_for_tenant
from ..tenant_service import create_tenant, drop_tenant

router = APIRouter(prefix="/tenants", tags=["tenants"]) 

@router.post("/", response_model=TenantOut)
def add_tenant(payload: TenantCreate, db: Session = Depends(get_db_for_tenant), claims=Depends(require_superadmin)):
    try:
        t = create_tenant(db, payload.name, payload.schema_name)
        return t
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/delete_tenant")
def remove_tenant(tenant_id: int, db: Session = Depends(get_db_for_tenant), claims=Depends(require_superadmin)):
    try:
        drop_tenant(db, tenant_id)
        return {"status": "deleted"}
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
