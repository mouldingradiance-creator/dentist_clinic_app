import sqlite3

conn = sqlite3.connect('database.db')

# Create users table
conn.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT,
    role TEXT
)
""")

# Insert default users
conn.execute("INSERT INTO users (username, password, role) VALUES ('doctor', '1234', 'doctor')")
conn.execute("INSERT INTO users (username, password, role) VALUES ('reception', '1234', 'reception')")

conn.commit()
conn.close()

print("Users table created and data inserted!")