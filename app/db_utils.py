#!/usr/bin/env python3
"""
Database utility functions for managing tables and schemas.
This file can be run directly or imported for database operations.
"""

import sys
import os

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import create_all_tables, create_tenant_schema_tables, drop_tenant_schema, table_exists
from app.models import Base, Tenant, User, Resource, AuditLog
from app.config import settings

def check_table_status():
    """Check the status of all tables"""
    print("Table Status:")
    
    # Check public schema tables
    tenant_exists = table_exists("tenants", "public")
    print(f"  Public Schema:")
    print(f"    - tenants: {' Exists' if tenant_exists else 'Missing'}")
    
    # Check if any tenant schemas exist
    from app.database import engine
    from sqlalchemy import inspect
    
    inspector = inspect(engine)
    schemas = inspector.get_schema_names()
    tenant_schemas = [s for s in schemas if s not in ['information_schema', 'pg_catalog', 'public']]
    
    if tenant_schemas:
        print(f"  Tenant Schemas:")
        for schema in tenant_schemas:
            users_exist = table_exists("users", schema)
            resources_exist = table_exists("resources", schema)
            audit_logs_exist = table_exists("audit_logs", schema)
            
            print(f"    {schema}:")
            print(f"      - users: {' Exists' if users_exist else 'Missing'}")
            print(f"      - resources: {' Exists' if resources_exist else 'Missing'}")
            print(f"      - audit_logs: {' Exists' if audit_logs_exist else 'Missing'}")
    else:
        print("  Tenant Schemas: None found")

def main():
    """Main function for command-line usage"""
    if len(sys.argv) < 2:
        print("Usage: python db_utils.py [command] [schema_name]")
        print("Commands:")
        print("  create-public    - Create public schema tables (Tenant table)")
        print("  create-tenant   - Create tenant schema and tables")
        print("  drop-tenant     - Drop tenant schema and all tables")
        print("  list-tables     - List all table names")
        print("  create-all      - Create all tables in public schema")
        print("  check-status    - Check status of all tables")
        return

    command = sys.argv[1]
    
    if command == "create-public":
        print("Creating public schema tables...")
        create_all_tables()
        
    elif command == "create-tenant":
        if len(sys.argv) < 3:
            print("Error: Please provide schema name")
            print("Usage: python db_utils.py create-tenant <schema_name>")
            return
        schema_name = sys.argv[2]
        print(f"Creating tenant schema '{schema_name}' and tables...")
        create_tenant_schema_tables(schema_name)
        
    elif command == "drop-tenant":
        if len(sys.argv) < 3:
            print("Error: Please provide schema name")
            print("Usage: python db_utils.py drop-tenant <schema_name>")
            return
        schema_name = sys.argv[2]
        print(f"Dropping tenant schema '{schema_name}'...")
        drop_tenant_schema(schema_name)
        print(f"Tenant schema '{schema_name}' dropped successfully")
        
    elif command == "list-tables":
        print("Available tables:")
        print(f"  - {Tenant.__tablename__} (public schema)")
        print(f"  - {User.__tablename__} (tenant schemas)")
        print(f"  - {Resource.__tablename__} (tenant schemas)")
        print(f"  - {AuditLog.__tablename__} (tenant schemas)")
        
    elif command == "create-all":
        print("Creating all tables in public schema...")
        create_all_tables()
        
    elif command == "check-status":
        check_table_status()
        
    else:
        print(f"Unknown command: {command}")
        print("Available commands: create-public, create-tenant, drop-tenant, list-tables, create-all, check-status")

if __name__ == "__main__":
    main() 