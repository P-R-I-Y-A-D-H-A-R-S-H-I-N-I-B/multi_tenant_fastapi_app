from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from ..schemas import AuditLogOut
from ..models import AuditLog, RoleEnum
from ..auth import require_tenant_role
from ..dependencies import get_db_for_tenant

router = APIRouter(prefix="/audit-logs", tags=["audit"]) 

@router.get("/", response_model=list[AuditLogOut], dependencies=[Depends(require_tenant_role((RoleEnum.ADMIN,)))])
def get_audit_logs(db: Session = Depends(get_db_for_tenant)):
    items = db.scalars(select(AuditLog).order_by(AuditLog.timestamp.desc())).all()
    return items
