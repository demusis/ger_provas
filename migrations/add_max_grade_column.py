import sys
import os
sys.path.append(os.getcwd())
from app import create_app
from models import db
from sqlalchemy import text

app = create_app()

with app.app_context():
    try:
        # Check if column exists
        with db.engine.connect() as conn:
            result = conn.execute(text("PRAGMA table_info(exam)"))
            columns = [row.name for row in result]
            
            if 'max_grade' not in columns:
                print("Adding 'max_grade' column to 'exam' table...")
                conn.execute(text("ALTER TABLE exam ADD COLUMN max_grade FLOAT DEFAULT 10.0 NOT NULL"))
                conn.commit()
                print("Column added successfully.")
            else:
                print("Column 'max_grade' already exists.")
                
    except Exception as e:
        print(f"An error occurred: {e}")
