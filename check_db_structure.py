import sqlite3

conn = sqlite3.connect("instance/database.db")
cursor = conn.cursor()

# Verificar estructura de la tabla inventario
cursor.execute("PRAGMA table_info(inventario)")
columns = cursor.fetchall()
print("Columnas en la tabla inventario:")
for col in columns:
    print(f"  {col[1]} - {col[2]}")

conn.close()
