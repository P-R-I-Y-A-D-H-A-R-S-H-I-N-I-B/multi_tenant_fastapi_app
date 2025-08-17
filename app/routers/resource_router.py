from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..schemas import ResourceCreate, ResourceUpdate, ResourceOut, PaginatedResources
from ..models import RoleEnum
from ..crud import create_resource, update_resource, delete_resource, search_resources
from ..auth import require_tenant_role
from ..dependencies import get_db_for_tenant, get_current_user_info

router = APIRouter(prefix="/resources", tags=["resources"]) 

# Admin/Manager: create resource
@router.post("/", response_model=ResourceOut, dependencies=[Depends(require_tenant_role((RoleEnum.ADMIN, RoleEnum.MANAGER)))])
def create_res(payload: ResourceCreate, db: Session = Depends(get_db_for_tenant), me=Depends(get_current_user_info)):
    try:
        r = create_resource(db, payload.name, payload.description, payload.owner_id, acting_user_id=me["user_id"]) 
        return r
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

# Admin/Manager: update resource
@router.put("/{resource_id}", response_model=ResourceOut, dependencies=[Depends(require_tenant_role((RoleEnum.ADMIN, RoleEnum.MANAGER)))])
def update_res(resource_id: int, payload: ResourceUpdate, db: Session = Depends(get_db_for_tenant), me=Depends(get_current_user_info)):
    try:
        r = update_resource(db, resource_id, payload.name, payload.description, acting_user_id=me["user_id"]) 
        return r
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))

# Admin/Manager: delete resource
@router.delete("/{resource_id}", dependencies=[Depends(require_tenant_role((RoleEnum.ADMIN, RoleEnum.MANAGER)))])
def delete_res(resource_id: int, db: Session = Depends(get_db_for_tenant), me=Depends(get_current_user_info)):
    try:
        delete_resource(db, resource_id, acting_user_id=me["user_id"]) 
        return {"status": "deleted"}
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))

# Employee (and Admin/Manager): list/search resources
@router.get("/", response_model=PaginatedResources, dependencies=[Depends(require_tenant_role((RoleEnum.ADMIN, RoleEnum.MANAGER, RoleEnum.EMPLOYEE)))])
def list_resources(
    name: str | None = None,
    owner_id: int | None = None,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db_for_tenant),
):
    total, items = search_resources(db, name, owner_id, page, size)
    return {"total": total, "page": page, "size": size, "items": items}

# Employee (and Admin/Manager): view one
@router.get("/{resource_id}", response_model=ResourceOut, dependencies=[Depends(require_tenant_role((RoleEnum.ADMIN, RoleEnum.MANAGER, RoleEnum.EMPLOYEE)))])
def get_resource(resource_id: int, db: Session = Depends(get_db_for_tenant)):
    from sqlalchemy import select
    from ..models import Resource
    r = db.get(Resource, resource_id)
    if not r or r.is_deleted:
        raise HTTPException(status_code=404, detail="Not found")
    return r
