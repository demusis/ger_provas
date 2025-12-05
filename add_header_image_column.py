from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    with db.engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE student_submission ADD COLUMN header_image_path TEXT"))
            print("Added header_image_path column")
        except Exception as e:
            print(f"Error adding header_image_path: {e}")
            
        conn.commit()
        print("Database schema update complete.")
