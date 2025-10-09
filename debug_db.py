#!/usr/bin/env python3
"""
Debug script to test database table creation
"""

import sys
import traceback

print("=== Debug Database Creation ===")

try:
    print("1. Testing basic imports...")
    from app.factory import create_app
    from app.extensions import db
    print("   ✓ Basic imports successful")
    
    print("2. Testing model imports...")
    from app.models.plan_mantenimiento import PlanMantenimiento
    print("   ✓ PlanMantenimiento imported")
    
    from app.models.usuario import Usuario
    print("   ✓ Usuario imported")
    
    print("3. Testing app creation...")
    app = create_app()
    print("   ✓ App created")
    
    print("4. Testing database context...")
    with app.app_context():
        print("   ✓ App context active")
        
        print("5. Testing table creation...")
        # Create tables explicitly
        db.create_all()
        print("   ✓ db.create_all() executed")
        
        print("6. Checking table existence...")
        # Check if tables exist
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"   Tables found: {tables}")
        
        if 'plan_mantenimiento' in tables:
            print("   ✓ plan_mantenimiento table exists!")
            columns = inspector.get_columns('plan_mantenimiento')
            print("   Columns:")
            for col in columns:
                print(f"     - {col['name']} ({col['type']})")
        else:
            print("   ✗ plan_mantenimiento table NOT found")
            
        print("7. Testing model metadata...")
        print(f"   PlanMantenimiento.__tablename__: {getattr(PlanMantenimiento, '__tablename__', 'NOT SET')}")
        print(f"   PlanMantenimiento.__table__.name: {PlanMantenimiento.__table__.name}")
        print(f"   PlanMantenimiento columns: {list(PlanMantenimiento.__table__.columns.keys())}")

except Exception as e:
    print(f"ERROR: {e}")
    traceback.print_exc()