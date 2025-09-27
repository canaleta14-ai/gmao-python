#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect("instance/database.db")
cursor = conn.cursor()

# Buscar conteos pendientes
cursor.execute(
    "SELECT id, estado FROM conteo_inventario WHERE estado = 'pendiente' LIMIT 5"
)
pendientes = cursor.fetchall()
print("Conteos pendientes:")
for p in pendientes:
    print(f"  ID={p[0]}, Estado={p[1]}")

conn.close()
