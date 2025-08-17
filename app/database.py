from contextlib import contextmanager
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker, scoped_session
from .config import settings

# Create a synchronous engine
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True, future=True)

# Session factory (one per request)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

@contextmanager
def db_session():
    """Context manager that yields a DB session and ensures close/rollback."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

def set_search_path(session, schema_name: str):
    """Set PostgreSQL search_path so that unqualified tables hit the tenant schema."""
    session.execute(text("SET search_path TO :schema, public").bindparams(schema=schema_name))

def table_exists(table_name: str, schema_name: str = "public") -> bool:
    """Check if a table exists in the specified schema"""
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names(schema=schema_name)
    return table_name in existing_tables

def create_all_tables():
    """Create all tables in the public schema (Tenant table only) if they don't exist"""
    from .models import Base, Tenant
    
    # Check if Tenant table already exists
    if table_exists("tenants", "public"):
        print("Public schema tables already exist")
        return
    
    print("Creating public schema tables...")
    Base.metadata.create_all(bind=engine, tables=[Tenant.__table__])
    print("Public schema tables created successfully")

def create_tenant_schema_tables(schema_name: str):
    """Create tenant-specific schema and tables if they don't exist"""
    from .models import Base, User, Resource, AuditLog
    
    # Check if schema exists and has tables
    if table_exists("users", schema_name):
        print(f"Tenant schema '{schema_name}' tables already exist")
        return
    
    print(f"Creating tenant schema '{schema_name}' and tables...")
    
    # Create the schema first
    with engine.connect() as conn:
        conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema_name}"))
        conn.commit()

    print(f"Schema '{schema_name}' created successfully!")
    # Create tables in the tenant schema
    with engine.connect() as conn:
        # Set search path to the tenant schema
        conn.execute(text(f"SET search_path TO {schema_name}, public"))
        conn.commit()
        # Create tables
        Base.metadata.create_all(
            bind=conn, 
            tables=[User.__table__, Resource.__table__, AuditLog.__table__]
        )
        conn.commit()
    
    print(f"Tenant schema '{schema_name}' and tables created successfully")

def drop_tenant_schema(schema_name: str):
    """Drop a tenant schema and all its tables"""
    with engine.connect() as conn:
        conn.execute(text(f"DROP SCHEMA IF EXISTS {schema_name} CASCADE"))
        conn.commit()
