from sqlalchemy import text
from sqlalchemy.orm import Session
from .models import Base, Tenant, User, Resource, AuditLog
from .database import set_search_path, table_exists, create_tenant_schema_tables

TENANT_TABLES_DDL_NOTE = """
We rely on SQLAlchemy metadata to create tenant tables in the new schema by temporarily
setting the session's search_path to the target schema and calling Base.metadata.create_all().
"""

def create_tenant(session: Session, name: str, schema_name: str):
    # 1) Create schema
    session.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema_name}"'))
    session.commit()
    # 2) Check if tables already exist in this schema
    if table_exists("users", schema_name):
        print(f"Tenant schema '{schema_name}' tables already exist")
    else:
        # 3) Switch search_path for this session
        # set_search_path(session, schema_name)
        # # 4) Create tenant tables inside that schema
        # create_tenant_schema_tables(schema_name)

        # session.execute(text(f"SET search_path TO {schema_name}, public"))
        # session.commit()
        print(f"Brfore creating tables for schema")
        # Update each model’s schema dynamically
        for table in [User.__table__, Resource.__table__, AuditLog.__table__]:
            table.schema = schema_name
        # Create tables
        Base.metadata.create_all(
            bind=session.get_bind(), 
            tables=[User.__table__, Resource.__table__, AuditLog.__table__]
        )
        session.commit()
        #Base.metadata.create_all(bind=session.get_bind())
        print(f"Tenant schema '{schema_name}' tables created successfully")
        # 5) Back to public
        set_search_path(session, "public")
    
    # 6) Register tenant
    t = Tenant(name=name, schema_name=schema_name)
    session.add(t)
    session.flush()
    return t


def drop_tenant(session: Session, tenant_id: int):
    t = session.get(Tenant, tenant_id)
    if not t:
        raise ValueError("Tenant not found")
    # Drop schema cascade (will remove all tenant tables & data)
    session.execute(text(f'DROP SCHEMA IF EXISTS "{t.schema_name}" CASCADE'))
    session.delete(t)
