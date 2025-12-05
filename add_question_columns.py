from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    with db.engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE question ADD COLUMN alt_e TEXT"))
            print("Added alt_e column")
        except Exception as e:
            print(f"Error adding alt_e: {e}")
            
        try:
            conn.execute(text("ALTER TABLE question ADD COLUMN num_alternatives INTEGER NOT NULL DEFAULT 4"))
            print("Added num_alternatives column")
        except Exception as e:
            print(f"Error adding num_alternatives: {e}")
            
        try:
            conn.execute(text("ALTER TABLE question ADD COLUMN comment TEXT"))
            print("Added comment column")
        except Exception as e:
            print(f"Error adding comment: {e}")
            
        conn.commit()
        print("Database schema update complete.")
