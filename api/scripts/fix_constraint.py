import sys
import os

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.db.session import SessionLocal

def fix_constraint():
    db = SessionLocal()
    try:
        # Try to drop the constraint
        print("Dropping constraint tenants_status_check...")
        db.execute(text("ALTER TABLE tenants DROP CONSTRAINT IF EXISTS tenants_status_check"))
        db.commit()
        print("Constraint dropped successfully.")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_constraint()
