import psycopg2
import sys

HOST = "130.211.68.78"
DB = "postgres"
USER = "gmao-user"
PASSWORD = "NbQt4EB*3gYjhu*25wemy73yr#IBXKm!"
HASH = "scrypt:32768:8:1$JQcqwdYSkaDGG0IJ$dd48c53884a5d3d3c6415b88114247f20d49502779ed35617b594655c4d9df86bc27eecbd477f05331d474ecc6dc33db58354890b203aaa054816aa430b61128"

def main():
    try:
        conn = psycopg2.connect(host=HOST, dbname=DB, user=USER, password=PASSWORD, connect_timeout=15, sslmode="require")
        conn.autocommit = False
        cur = conn.cursor()

        print("Pre-verificación:")
        cur.execute("SELECT id, username, rol, activo FROM usuario WHERE username='admin';")
        print(cur.fetchall())

        print("Aplicando UPSERT del usuario admin...")
        cur.execute(
            """
            INSERT INTO usuario (username,email,password,nombre,rol,activo,fecha_creacion)
            VALUES (%s,%s,%s,%s,%s,%s, now())
            ON CONFLICT (username) DO UPDATE SET
                password=EXCLUDED.password,
                rol=EXCLUDED.rol,
                activo=EXCLUDED.activo,
                nombre=EXCLUDED.nombre,
                email=EXCLUDED.email;
            """,
            ('admin','admin@gmao.com', HASH, 'Administrador','Administrador', True)
        )
        conn.commit()

        print("Post-verificación:")
        cur.execute("SELECT id, username, rol, activo FROM usuario WHERE username='admin';")
        print(cur.fetchall())

        cur.close()
        conn.close()
        print("Éxito")
    except Exception as e:
        print("Error:", e)
        sys.exit(1)

if __name__ == "__main__":
    main()