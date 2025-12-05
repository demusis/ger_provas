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
            result = conn.execute(text("PRAGMA table_info(question)"))
            columns = [row.name for row in result]
            
            if 'weight' not in columns:
                print("Adding 'weight' column to 'question' table...")
                conn.execute(text("ALTER TABLE question ADD COLUMN weight FLOAT DEFAULT 1.0 NOT NULL"))
                conn.commit()
                print("Column added successfully.")
            else:
                print("Column 'weight' already exists.")
                
    except Exception as e:
        print(f"An error occurred: {e}")
