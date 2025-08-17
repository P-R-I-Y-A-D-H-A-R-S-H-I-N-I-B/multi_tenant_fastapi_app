from fastapi import FastAPI
from app.database import engine, create_all_tables
from app.models import Base, Tenant
from app.config import settings
from app.routers import tenant_router, auth_router, user_router, resource_router, audit_router

app = FastAPI(title="Multi-Tenant Resource Management System", version="1.0.0")

# Create PUBLIC schema tables (Tenants registry) on startup
@app.on_event("startup")
def on_startup():
    print("Starting Multi-Tenant Resource Management System...")
    # Create all tables in the public schema (Tenant table only) if they don't exist
    create_all_tables()
    print("Application startup completed")

# Routers
app.include_router(auth_router.router)
app.include_router(tenant_router.router)
app.include_router(user_router.router)
app.include_router(resource_router.router)
app.include_router(audit_router.router)

# Health
@app.get("/health")
def health():
    return {"status": "ok"}
