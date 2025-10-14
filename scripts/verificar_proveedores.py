import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "../instance/database.db")
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

for row in c.execute("SELECT * FROM proveedor LIMIT 10"):
    print(row)

conn.close()