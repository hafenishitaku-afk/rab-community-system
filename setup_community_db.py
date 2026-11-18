
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def create_community_tables():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        print("✅ Connected to community_db. Creating tables...\n")
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        sys.exit(1)

    # Ordered to respect Foreign Key dependencies (users before messages/voice_notes)
    tables = [
        """CREATE TABLE IF NOT EXISTS users(
            id SERIAL PRIMARY KEY,
            full_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            location TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'staff',
            last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_read_chat TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );""",

        """CREATE TABLE IF NOT EXISTS messages(
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );""",

        """CREATE TABLE IF NOT EXISTS voice_notes(
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            file_path TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );"""
    ]

    success_count = 0
    for table_sql in tables:
        try:
            cursor.execute(table_sql)
            table_name = table_sql.split("IF NOT EXISTS")[1].split("(")[0].strip()
            print(f"✅ Created: {table_name}")
            success_count += 1
        except Exception as e:
            print(f"❌ Error creating table: {e}")
            conn.rollback()

    # Idempotent auto-migration (mirrors the ALTER logic in your database.py)
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP;")
        cursor.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS last_read_chat TIMESTAMP DEFAULT CURRENT_TIMESTAMP;")
        print("✅ Verified auto-migration columns (last_active, last_read_chat)")
    except Exception as e:
        print(f"⚠️ Auto-migration note: {e}")

    conn.commit()
    print(f"\n🎉 Done! Successfully verified/created {success_count} tables in community_db.")
    cursor.close()
    conn.close()

if __name__ == "__main__":
    create_community_tables()