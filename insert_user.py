from werkzeug.security import generate_password_hash
import psycopg
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg.connect(
    dbname="company_portal_db",
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT")
)

cur = conn.cursor()

# --- ADMIN ACCOUNT ---
admin_username = "admin"
admin_password = "test123"
admin_hash = generate_password_hash(admin_password)

cur.execute("""
    INSERT INTO app_user (username, password_hash, role)
    VALUES (%s, %s, %s)
    ON CONFLICT (username) DO NOTHING;
""", (admin_username, admin_hash, "admin"))

# --- VIEWER ACCOUNT ---
viewer_username = "viewer"
viewer_password = "viewer123"
viewer_hash = generate_password_hash(viewer_password)

cur.execute("""
    INSERT INTO app_user (username, password_hash, role)
    VALUES (%s, %s, %s)
    ON CONFLICT (username) DO NOTHING;
""", (viewer_username, viewer_hash, "viewer"))

conn.commit()
cur.close()
conn.close()

print("Users created: admin, viewer")
