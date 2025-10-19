#!/usr/bin/env python3
"""
Script para importar datos de la base de datos en el servidor de producción
Ejecutar en el entorno de PRODUCCIÓN

ADVERTENCIA: Este script:
- Detendrá la aplicación temporalmente
- Creará un backup automático de la BD actual
- Reemplazará todos los datos con el archivo importado
- Requiere confirmación explícita
"""

import os
import sys
import subprocess
import gzip
import hashlib
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv


# Colores para terminal
class Colors:
    GREEN = "\033[0;32m"
    YELLOW = "\033[1;33m"
    RED = "\033[0;31m"
    BLUE = "\033[0;34m"
    CYAN = "\033[0;36m"
    NC = "\033[0m"  # No Color


def print_color(message, color=Colors.NC):
    """Imprime mensaje con color."""
    print(f"{color}{message}{Colors.NC}")


def find_psql():
    """
    Busca el ejecutable psql en ubicaciones comunes.
    Retorna la ruta completa o None si no se encuentra.
    """
    # Intentar encontrar en PATH primero
    try:
        result = subprocess.run(
            ["psql", "--version"], capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            return "psql"
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # Ubicaciones comunes en Windows
    if sys.platform == "win32":
        possible_paths = [
            r"C:\Program Files\PostgreSQL\16\bin\psql.exe",
            r"C:\Program Files\PostgreSQL\15\bin\psql.exe",
            r"C:\Program Files\PostgreSQL\14\bin\psql.exe",
            r"C:\Program Files\PostgreSQL\13\bin\psql.exe",
        ]

        for path in possible_paths:
            if os.path.exists(path):
                return path

        # Buscar en Program Files usando glob
        pg_base = Path("C:/Program Files/PostgreSQL")
        if pg_base.exists():
            for version_dir in pg_base.iterdir():
                psql = version_dir / "bin" / "psql.exe"
                if psql.exists():
                    return str(psql)

    return None


def find_pg_dump():
    """Busca pg_dump para crear backups."""
    try:
        result = subprocess.run(
            ["pg_dump", "--version"], capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            return "pg_dump"
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    if sys.platform == "win32":
        pg_base = Path("C:/Program Files/PostgreSQL")
        if pg_base.exists():
            for version_dir in pg_base.iterdir():
                pg_dump = version_dir / "bin" / "pg_dump.exe"
                if pg_dump.exists():
                    return str(pg_dump)

    return None


def verify_checksum(compressed_file, checksum_file):
    """Verifica el checksum SHA256 del archivo."""
    print_color("🔐 Verificando checksum...", Colors.YELLOW)

    # Leer checksum esperado
    with open(checksum_file, "r") as f:
        expected_checksum = f.read().strip().split()[0]

    # Calcular checksum del archivo
    sha256_hash = hashlib.sha256()
    with open(compressed_file, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    actual_checksum = sha256_hash.hexdigest()

    if expected_checksum == actual_checksum:
        print_color("✅ Checksum verificado correctamente", Colors.GREEN)
        return True
    else:
        print_color("❌ ERROR: Checksum no coincide", Colors.RED)
        print_color(f"Esperado: {expected_checksum}", Colors.RED)
        print_color(f"Obtenido: {actual_checksum}", Colors.RED)
        return False


def decompress_file(compressed_file, output_file):
    """Descomprime un archivo gzip."""
    print_color(f"📦 Descomprimiendo archivo...", Colors.YELLOW)
    with gzip.open(compressed_file, "rb") as f_in:
        with open(output_file, "wb") as f_out:
            f_out.write(f_in.read())
    print_color(f"✅ Archivo descomprimido: {output_file}", Colors.GREEN)


def create_backup(pg_dump, db_name, db_user, db_host, db_port, db_password):
    """Crea un backup de la base de datos actual."""
    print_color("💾 Creando backup de seguridad...", Colors.YELLOW)

    backup_dir = Path("./backups")
    backup_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = backup_dir / f"pre_import_backup_{timestamp}.sql"

    env = os.environ.copy()
    if db_password:
        env["PGPASSWORD"] = db_password

    cmd = [
        pg_dump,
        "--no-owner",
        "--no-acl",
        "--clean",
        "--if-exists",
        "--host",
        db_host,
        "--port",
        db_port,
        "--username",
        db_user,
        "--dbname",
        db_name,
        "--file",
        str(backup_file),
    ]

    try:
        result = subprocess.run(
            cmd, env=env, capture_output=True, text=True, timeout=300
        )

        if result.returncode != 0:
            print_color(f"❌ Error creando backup: {result.stderr}", Colors.RED)
            return None

        print_color(f"✅ Backup creado: {backup_file}", Colors.GREEN)
        return backup_file

    except Exception as e:
        print_color(f"❌ Error creando backup: {str(e)}", Colors.RED)
        return None


def stop_application():
    """Intenta detener la aplicación."""
    print_color("🛑 Intentando detener la aplicación...", Colors.YELLOW)

    # Intentar con Supervisor (Linux)
    try:
        result = subprocess.run(
            ["sudo", "supervisorctl", "stop", "gmao"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            print_color("✅ Aplicación detenida (Supervisor)", Colors.GREEN)
            return "supervisor"
    except:
        pass

    # Si no hay Supervisor, avisar que debe detenerse manualmente
    print_color("⚠️  No se pudo detener automáticamente", Colors.YELLOW)
    print_color(
        "Por favor, detén la aplicación manualmente antes de continuar", Colors.YELLOW
    )

    response = input("¿Has detenido la aplicación? (si/no): ").strip().lower()
    if response in ["si", "sí", "s", "yes", "y"]:
        return "manual"
    else:
        print_color("❌ Importación cancelada", Colors.RED)
        sys.exit(1)


def start_application(method):
    """Intenta iniciar la aplicación."""
    print_color("🚀 Intentando reiniciar la aplicación...", Colors.YELLOW)

    if method == "supervisor":
        try:
            result = subprocess.run(
                ["sudo", "supervisorctl", "start", "gmao"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                print_color("✅ Aplicación reiniciada (Supervisor)", Colors.GREEN)
                return True
        except:
            pass

    print_color("⚠️  Inicia la aplicación manualmente", Colors.YELLOW)
    return False


def import_database(psql, sql_file, db_name, db_user, db_host, db_port, db_password):
    """Importa el archivo SQL a la base de datos."""
    print_color("📥 Importando datos a PostgreSQL...", Colors.YELLOW)
    print_color("Esto puede tomar varios minutos...", Colors.CYAN)

    env = os.environ.copy()
    if db_password:
        env["PGPASSWORD"] = db_password

    cmd = [
        psql,
        "--host",
        db_host,
        "--port",
        db_port,
        "--username",
        db_user,
        "--dbname",
        db_name,
        "--file",
        str(sql_file),
    ]

    try:
        result = subprocess.run(
            cmd, env=env, capture_output=True, text=True, timeout=600
        )

        if result.returncode != 0:
            print_color(f"❌ Error importando datos:", Colors.RED)
            print_color(result.stderr, Colors.RED)
            return False

        print_color("✅ Datos importados correctamente", Colors.GREEN)
        return True

    except subprocess.TimeoutExpired:
        print_color(
            "❌ Error: La importación tardó demasiado (>10 minutos)", Colors.RED
        )
        return False
    except Exception as e:
        print_color(f"❌ Error durante la importación: {str(e)}", Colors.RED)
        return False


def run_migrations():
    """Ejecuta las migraciones de Flask."""
    print_color("🔄 Ejecutando migraciones de Flask...", Colors.YELLOW)

    try:
        # Activar entorno virtual si existe
        venv_activate = Path("./venv/bin/activate")
        if sys.platform == "win32":
            venv_activate = Path("./venv/Scripts/activate")

        # Ejecutar migraciones
        result = subprocess.run(
            ["flask", "db", "upgrade"], capture_output=True, text=True, timeout=60
        )

        if result.returncode == 0:
            print_color("✅ Migraciones completadas", Colors.GREEN)
            return True
        else:
            print_color(
                f"⚠️  Advertencia en migraciones: {result.stderr}", Colors.YELLOW
            )
            return True  # Continuar aunque haya advertencias

    except Exception as e:
        print_color(
            f"⚠️  No se pudieron ejecutar migraciones automáticamente: {str(e)}",
            Colors.YELLOW,
        )
        print_color("Ejecuta manualmente: flask db upgrade", Colors.YELLOW)
        return True


def main():
    """Función principal."""
    if len(sys.argv) < 2:
        print_color(
            "❌ Error: Debes proporcionar el archivo .sql.gz a importar", Colors.RED
        )
        print_color("\nUso:", Colors.YELLOW)
        print_color(
            "  python import_production_data.py archivo_exportado.sql.gz", Colors.CYAN
        )
        sys.exit(1)

    compressed_file = Path(sys.argv[1])

    if not compressed_file.exists():
        print_color(f"❌ Error: El archivo {compressed_file} no existe", Colors.RED)
        sys.exit(1)

    print_color("=" * 64, Colors.BLUE)
    print_color("📥 IMPORTACIÓN DE BASE DE DATOS GMAO - PRODUCCIÓN", Colors.BLUE)
    print_color("=" * 64, Colors.BLUE)
    print()

    print_color(f"📦 Archivo a importar: {compressed_file}", Colors.CYAN)

    # Verificar archivo de checksum
    checksum_file = Path(f"{compressed_file}.sha256")
    if checksum_file.exists():
        if not verify_checksum(compressed_file, checksum_file):
            print_color("\n❌ Importación cancelada por checksum inválido", Colors.RED)
            sys.exit(1)
    else:
        print_color(
            "⚠️  Archivo de checksum no encontrado, continuando sin verificar",
            Colors.YELLOW,
        )

    print()
    print_color("⚠️  ADVERTENCIA IMPORTANTE ⚠️", Colors.RED)
    print_color("=" * 64, Colors.RED)
    print_color("Este proceso:", Colors.YELLOW)
    print_color("1. Detendrá la aplicación GMAO (si está corriendo)", Colors.YELLOW)
    print_color("2. Creará un backup de la base de datos actual", Colors.YELLOW)
    print_color(
        "3. Reemplazará TODOS los datos con el archivo importado", Colors.YELLOW
    )
    print_color("4. Ejecutará las migraciones de Flask", Colors.YELLOW)
    print_color("5. Reiniciará la aplicación", Colors.YELLOW)
    print()
    print_color("Tiempo estimado: 5-15 minutos", Colors.CYAN)
    print_color("=" * 64, Colors.RED)
    print()

    # Solicitar confirmación
    print_color("Para confirmar, escribe: SI CONFIRMO", Colors.YELLOW)
    confirmation = input("Confirmación: ").strip()

    if confirmation != "SI CONFIRMO":
        print_color("\n❌ Importación cancelada. Confirmación no recibida.", Colors.RED)
        print_color(f"Se recibió: '{confirmation}'", Colors.RED)
        print_color("Se esperaba: 'SI CONFIRMO'", Colors.YELLOW)
        sys.exit(1)

    print()
    print_color("✅ Confirmación recibida", Colors.GREEN)
    print()

    # Buscar herramientas PostgreSQL
    print_color("🔍 Buscando herramientas PostgreSQL...", Colors.YELLOW)
    psql = find_psql()
    pg_dump = find_pg_dump()

    if not psql:
        print_color("❌ Error: No se encontró psql", Colors.RED)
        sys.exit(1)

    print_color(f"✅ psql encontrado: {psql}", Colors.GREEN)

    if not pg_dump:
        print_color(
            "⚠️  Advertencia: pg_dump no encontrado, no se podrá crear backup",
            Colors.YELLOW,
        )
    else:
        print_color(f"✅ pg_dump encontrado: {pg_dump}", Colors.GREEN)

    # Cargar variables de entorno
    if os.path.exists(".env"):
        print_color("📄 Leyendo credenciales de .env...", Colors.YELLOW)
        load_dotenv()

    db_name = os.getenv("DB_NAME", "gmao_db")
    db_user = os.getenv("DB_USER", "gmao_user")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_password = os.getenv("DB_PASSWORD", "")

    print_color(f"📊 Base de datos: {db_name}@{db_host}:{db_port}", Colors.BLUE)
    print()

    # Proceso de importación en 6 pasos
    print_color("🛑 Paso 1/6: Deteniendo aplicación...", Colors.CYAN)
    app_method = stop_application()
    print()

    if pg_dump:
        print_color("💾 Paso 2/6: Creando backup de seguridad...", Colors.CYAN)
        backup_file = create_backup(
            pg_dump, db_name, db_user, db_host, db_port, db_password
        )
        if not backup_file:
            print_color(
                "⚠️  No se pudo crear backup. ¿Continuar de todos modos? (si/no): ",
                Colors.YELLOW,
            )
            response = input().strip().lower()
            if response not in ["si", "sí", "s", "yes", "y"]:
                print_color("❌ Importación cancelada", Colors.RED)
                sys.exit(1)
        print()
    else:
        print_color(
            "⚠️  Paso 2/6: Saltando backup (pg_dump no disponible)", Colors.YELLOW
        )
        print()

    print_color("📦 Paso 3/6: Descomprimiendo archivo...", Colors.CYAN)
    sql_file = Path(str(compressed_file).replace(".gz", ""))
    decompress_file(compressed_file, sql_file)
    print()

    print_color("📥 Paso 4/6: Importando datos a PostgreSQL...", Colors.CYAN)
    if not import_database(
        psql, sql_file, db_name, db_user, db_host, db_port, db_password
    ):
        print()
        print_color("❌ ERROR: La importación falló", Colors.RED)
        print()
        if backup_file:
            print_color("🔙 INSTRUCCIONES DE ROLLBACK:", Colors.YELLOW)
            print_color(
                f"1. Restaurar backup: psql -U {db_user} -d {db_name} < {backup_file}",
                Colors.CYAN,
            )
            print_color(f"2. Reiniciar aplicación", Colors.CYAN)
        sys.exit(1)
    print()

    print_color("🔄 Paso 5/6: Ejecutando migraciones de Flask...", Colors.CYAN)
    run_migrations()
    print()

    print_color("🚀 Paso 6/6: Reiniciando aplicación...", Colors.CYAN)
    start_application(app_method)
    print()

    # Limpieza
    if sql_file.exists():
        sql_file.unlink()
        print_color(f"🗑️  Archivo temporal eliminado: {sql_file}", Colors.GREEN)

    # Resumen final
    print()
    print_color("=" * 64, Colors.BLUE)
    print_color("✅ IMPORTACIÓN COMPLETADA EXITOSAMENTE", Colors.GREEN)
    print_color("=" * 64, Colors.BLUE)
    print()
    print_color("📊 Verificación post-importación:", Colors.CYAN)
    if backup_file:
        print_color(f"- Backup previo: {backup_file}", Colors.YELLOW)
    print_color(f"- Base de datos actualizada: {db_name}", Colors.YELLOW)
    print_color("- Aplicación: VERIFICAR MANUALMENTE", Colors.YELLOW)
    print()
    print_color("🔍 Próximos pasos:", Colors.CYAN)
    print_color(
        "1. Verificar que la aplicación funciona: http://tu-servidor.com", Colors.YELLOW
    )
    print_color("2. Revisar logs: tail -f logs/gunicorn-access.log", Colors.YELLOW)
    print_color("3. Probar inicio de sesión y funcionalidades críticas", Colors.YELLOW)
    if backup_file:
        print_color(
            f"4. Mantener el backup por al menos 7 días: {backup_file}", Colors.YELLOW
        )
    print()

    if backup_file:
        print_color("En caso de problemas, ver sección de ROLLBACK:", Colors.CYAN)
        print_color(f"psql -U {db_user} -d {db_name} < {backup_file}", Colors.YELLOW)

    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_color("\n\n❌ Importación cancelada por el usuario", Colors.RED)
        sys.exit(1)
    except Exception as e:
        print_color(f"\n❌ Error inesperado: {str(e)}", Colors.RED)
        import traceback

        traceback.print_exc()
        sys.exit(1)
