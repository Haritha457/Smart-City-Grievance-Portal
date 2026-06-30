import os
import psycopg2
conn = psycopg2.connect(os.environ.get("DATABASE_URL"))
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS complaints (
        id SERIAL PRIMARY KEY,
        tracking_id TEXT UNIQUE,       
        text TEXT NOT NULL,
        category TEXT,
        priority TEXT,
        status TEXT DEFAULT 'Pending',       
        is_anomaly INTEGER DEFAULT 0,
        timestamp TEXT DEFAULT CURRENT_TIMESTAMP
    )
''')
cursor.execute('''
CREATE TABLE IF NOT EXISTS admins (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
''')

cursor.execute("""
INSERT INTO admins (username, password)
VALUES (%s, %s)
ON CONFLICT (username) DO NOTHING
""", ("admin", "admin123"))

conn.commit()
conn.close()

print("Database and table created successfully.")