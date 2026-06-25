import sqlite3

# Connect to (or create) the database file
conn = sqlite3.connect('database.db')

# Create a cursor - this lets us run SQL commands
cursor = conn.cursor()

# Create the complaints table if it doesn't already exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS complaints (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        text TEXT NOT NULL,
        category TEXT,
        priority TEXT,
        is_anomaly INTEGER DEFAULT 0,
        timestamp TEXT DEFAULT CURRENT_TIMESTAMP
    )
''')

conn.commit()
conn.close()

print("Database and table created successfully.")