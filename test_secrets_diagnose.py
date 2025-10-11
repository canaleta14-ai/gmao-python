#!/usr/bin/env python3
"""
Script de diagnóstico para Secret Manager
Imprime exactamente qué valores está obteniendo la aplicación
"""

import os
import sys

# Simular entorno de producción
os.environ["GOOGLE_CLOUD_PROJECT"] = "mantenimiento-470311"
os.environ["GAE_ENV"] = "standard"
os.environ["DB_TYPE"] = "postgresql"

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    print("=== DIAGNÓSTICO SECRET MANAGER ===")
    print(f"GOOGLE_CLOUD_PROJECT: {os.getenv('GOOGLE_CLOUD_PROJECT')}")
    print(f"GAE_ENV: {os.getenv('GAE_ENV')}")
    print(f"DB_TYPE: {os.getenv('DB_TYPE')}")

    try:
        from app.utils.secrets import get_secret_or_env

        print("\n=== TESTEO DE SECRETOS ===")

        # Test 1: DB Password
        print("1. Testeando DB Password...")
        db_password = get_secret_or_env(
            secret_id="gmao-db-password",
            env_var="DB_PASSWORD",
            default="DEFAULT_PASSWORD",
        )
        print(
            f"   Resultado: {'[OBTENIDO]' if db_password != 'DEFAULT_PASSWORD' else '[FALLBACK]'}"
        )
        print(f"   Valor: {db_password[:8]}*** (primeros 8 chars)")

        # Test 2: DB User
        print("\n2. Testeando DB User...")
        db_user = get_secret_or_env(
            secret_id="gmao-db-user", env_var="DB_USER", default="DEFAULT_USER"
        )
        print(
            f"   Resultado: {'[OBTENIDO]' if db_user != 'DEFAULT_USER' else '[FALLBACK]'}"
        )
        print(f"   Valor: {db_user}")

        # Test 3: DB Host
        print("\n3. Testeando DB Host...")
        db_host = get_secret_or_env(
            secret_id="gmao-db-host", env_var="DB_HOST", default="DEFAULT_HOST"
        )
        print(
            f"   Resultado: {'[OBTENIDO]' if db_host != 'DEFAULT_HOST' else '[FALLBACK]'}"
        )
        print(f"   Valor: {db_host}")

        # Test 4: DB Name
        print("\n4. Testeando DB Name...")
        db_name = get_secret_or_env(
            secret_id="gmao-db-name", env_var="DB_NAME", default="DEFAULT_NAME"
        )
        print(
            f"   Resultado: {'[OBTENIDO]' if db_name != 'DEFAULT_NAME' else '[FALLBACK]'}"
        )
        print(f"   Valor: {db_name}")

        print("\n=== CONSTRUCCIÓN DE URI ===")
        uri = f"postgresql://{db_user}:{db_password[:8]}***@{db_host}/{db_name}"
        print(f"URI construida: {uri}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
