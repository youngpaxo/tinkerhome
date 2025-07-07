import sqlite3
from werkzeug.security import generate_password_hash

conn = sqlite3.connect("finanzas.db")
cursor = conn.cursor()

hashed_password = generate_password_hash("Diegocalderon01")
cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", ("Diego", hashed_password))
conn.commit()
conn.close()

print("Usuario creado!")