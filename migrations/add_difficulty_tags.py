import sqlite3
import os

# Database path
DB_PATH = 'instance/app.db'

def migrate():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Add difficulty column
        try:
            cursor.execute("ALTER TABLE question ADD COLUMN difficulty VARCHAR(20) DEFAULT 'Médio'")
            print("Added 'difficulty' column.")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e):
                print("'difficulty' column already exists.")
            else:
                raise e

        # Add tags column
        try:
            cursor.execute("ALTER TABLE question ADD COLUMN tags TEXT DEFAULT ''")
            print("Added 'tags' column.")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e):
                print("'tags' column already exists.")
            else:
                raise e

        conn.commit()
        print("Migration successful.")

    except Exception as e:
        print(f"Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    migrate()
