#!/usr/bin/env python3
"""
Simple script to test table creation.
Run this to create all tables in your database.
"""

import sys
import os

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.database import create_all_tables

if __name__ == "__main__":
    print("Creating all tables...")
    try:
        create_all_tables()
        print("Tables created successfully!")
    except Exception as e:
        print(f"Error creating tables: {e}")
        sys.exit(1) 

# from passlib.context import CryptContext
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# password = "tenant1admin@123"

# has_pass = pwd_context.hash(password)

# print(has_pass)