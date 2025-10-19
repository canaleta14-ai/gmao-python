#!/usr/bin/env python3
"""
Script para exportar datos de la base de datos local a producción
Ejecutar en el entorno de DESARROLLO

Este script es compatible con Windows, Linux y Mac.
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
    NC = "\033[0m"  # No Color


def print_color(message, color=Colors.NC):
    """Imprime mensaje con color."""
    print(f"{color}{message}{Colors.NC}")


def find_pg_dump():
    """
    Busca el ejecutable pg_dump en ubicaciones comunes.
    Retorna la ruta completa o None si no se encuentra.
    """
    # Intentar encontrar en PATH primero
    try:
        result = subprocess.run(
            ["pg_dump", "--version"], capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            return "pg_dump"
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # Ubicaciones comunes en Windows
    if sys.platform == "win32":
        possible_paths = [
            r"C:\Program Files\PostgreSQL\16\bin\pg_dump.exe",
            r"C:\Program Files\PostgreSQL\15\bin\pg_dump.exe",
            r"C:\Program Files\PostgreSQL\14\bin\pg_dump.exe",
            r"C:\Program Files\PostgreSQL\13\bin\pg_dump.exe",
            r"C:\Program Files\PostgreSQL\12\bin\pg_dump.exe",
            r"C:\Program Files (x86)\PostgreSQL\16\bin\pg_dump.exe",
            r"C:\Program Files (x86)\PostgreSQL\15\bin\pg_dump.exe",
            r"C:\Program Files (x86)\PostgreSQL\14\bin\pg_dump.exe",
            r"C:\Program Files (x86)\PostgreSQL\13\bin\pg_dump.exe",
            r"C:\Program Files (x86)\PostgreSQL\12\bin\pg_dump.exe",
        ]

        for path in possible_paths:
            if os.path.exists(path):
                return path

        # Buscar en Program Files usando glob
        pg_base = Path("C:/Program Files/PostgreSQL")
        if pg_base.exists():
            for version_dir in pg_base.iterdir():
                pg_dump = version_dir / "bin" / "pg_dump.exe"
                if pg_dump.exists():
                    return str(pg_dump)

    return None


def calculate_sha256(file_path):
    """Calcula el SHA256 de un archivo."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def compress_file(input_file, output_file):
    """Comprime un archivo con gzip."""
    print_color(f"🗜️  Comprimiendo archivo...", Colors.YELLOW)
    with open(input_file, "rb") as f_in:
        with gzip.open(output_file, "wb") as f_out:
            f_out.writelines(f_in)
    print_color(f"✅ Archivo comprimido: {output_file}", Colors.GREEN)


def create_readme(export_dir, compressed_file, checksum_file):
    """Crea archivo README con instrucciones."""
    readme_path = export_dir / "README.txt"

    file_size = os.path.getsize(compressed_file)
    size_mb = file_size / (1024 * 1024)

    readme_content = f"""
========================================================================
EXPORTACIÓN DE BASE DE DATOS GMAO - MIGRACIÓN A PRODUCCIÓN
========================================================================

Fecha de exportación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Tamaño del archivo: {size_mb:.2f} MB

ARCHIVOS INCLUIDOS:
------------------
1. {os.path.basename(compressed_file)} - Base de datos comprimida
2. {os.path.basename(checksum_file)} - Checksum SHA256 para verificación
3. README.txt - Este archivo

INSTRUCCIONES DE TRANSFERENCIA:
-------------------------------

Opción 1: Transferencia segura con SCP
---------------------------------------
scp {os.path.basename(compressed_file)} usuario@servidor:/ruta/destino/
scp {os.path.basename(checksum_file)} usuario@servidor:/ruta/destino/

Opción 2: Transferencia con SFTP
---------------------------------
sftp usuario@servidor
put {os.path.basename(compressed_file)}
put {os.path.basename(checksum_file)}
exit

Opción 3: Transferencia con rsync (más robusto)
------------------------------------------------
rsync -avz --progress {os.path.basename(compressed_file)} usuario@servidor:/ruta/destino/
rsync -avz --progress {os.path.basename(checksum_file)} usuario@servidor:/ruta/destino/

INSTRUCCIONES DE IMPORTACIÓN EN EL SERVIDOR:
--------------------------------------------

1. Conectarse al servidor:
   ssh usuario@servidor

2. Verificar integridad del archivo:
   cd /ruta/destino/
   sha256sum -c {os.path.basename(checksum_file)}
   
   Debe mostrar: {os.path.basename(compressed_file)}: OK

3. Ejecutar script de importación:
   ./import_production_data.sh {os.path.basename(compressed_file)}

4. Seguir las instrucciones interactivas del script

NOTAS IMPORTANTES:
-----------------
- El proceso de importación detendrá temporalmente la aplicación
- Se creará un backup automático antes de la importación
- El tiempo estimado de importación es 5-15 minutos
- Mantener este archivo y el backup por al menos 7 días

SOPORTE:
--------
En caso de problemas durante la importación, consultar:
- DEPLOYMENT.md sección "Migración de Datos"
- Logs del servidor: /home/gmao/gmao-python/gmao-sistema/logs/

========================================================================
"""

    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme_content)

    print_color(f"📝 README generado: {readme_path}", Colors.GREEN)


def main():
    """Función principal."""
    print_color("=" * 64, Colors.BLUE)
    print_color("📦 Exportación de Base de Datos GMAO - Producción", Colors.BLUE)
    print_color("=" * 64, Colors.BLUE)
    print_color(
        f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", Colors.YELLOW
    )
    print_color(f"🖥️  Sistema: {sys.platform}", Colors.YELLOW)
    print_color("=" * 64, Colors.BLUE)
    print()

    # Configuración
    export_dir = Path("./db_export")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    export_file = export_dir / f"gmao_data_export_{timestamp}.sql"
    compressed_file = Path(f"{export_file}.gz")
    checksum_file = Path(f"{compressed_file}.sha256")

    # Crear directorio de exportación
    export_dir.mkdir(exist_ok=True)
    print_color(f"✅ Directorio de exportación creado: {export_dir}/", Colors.GREEN)

    # Buscar pg_dump
    print_color("🔍 Buscando PostgreSQL (pg_dump)...", Colors.YELLOW)
    pg_dump = find_pg_dump()

    if not pg_dump:
        print_color("❌ Error: No se encontró pg_dump", Colors.RED)
        print_color(
            "\nPor favor, instala PostgreSQL o agrega pg_dump al PATH:", Colors.YELLOW
        )

        if sys.platform == "win32":
            print_color("\nOpciones para Windows:", Colors.YELLOW)
            print_color(
                "1. Instalar PostgreSQL desde: https://www.postgresql.org/download/windows/",
                Colors.YELLOW,
            )
            print_color(
                "2. Agregar al PATH: C:\\Program Files\\PostgreSQL\\[version]\\bin",
                Colors.YELLOW,
            )
            print_color("\nPara agregar al PATH:", Colors.YELLOW)
            print_color(
                "   - Panel de Control > Sistema > Configuración avanzada del sistema",
                Colors.YELLOW,
            )
            print_color(
                "   - Variables de entorno > Path > Editar > Nuevo", Colors.YELLOW
            )
            print_color(
                "   - Agregar: C:\\Program Files\\PostgreSQL\\16\\bin", Colors.YELLOW
            )
        else:
            print_color("\nPara Linux/Mac:", Colors.YELLOW)
            print_color(
                "   sudo apt install postgresql-client  # Ubuntu/Debian", Colors.YELLOW
            )
            print_color("   brew install postgresql  # Mac con Homebrew", Colors.YELLOW)

        sys.exit(1)

    print_color(f"✅ PostgreSQL encontrado: {pg_dump}", Colors.GREEN)

    # Cargar variables de entorno
    if os.path.exists(".env"):
        print_color("📄 Leyendo credenciales de .env...", Colors.YELLOW)
        load_dotenv()
    else:
        print_color(
            "⚠️  Archivo .env no encontrado, usando valores por defecto", Colors.YELLOW
        )

    # Obtener credenciales
    db_name = os.getenv("DB_NAME", "gmao_db")
    db_user = os.getenv("DB_USER", "gmao_user")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_password = os.getenv("DB_PASSWORD", "")

    print_color(f"📊 Base de datos: {db_name}@{db_host}:{db_port}", Colors.BLUE)
    print()

    # Construir comando pg_dump
    env = os.environ.copy()
    if db_password:
        env["PGPASSWORD"] = db_password

    cmd = [
        pg_dump,
        "--no-owner",
        "--no-acl",
        "--clean",
        "--if-exists",
        "--verbose",
        "--host",
        db_host,
        "--port",
        db_port,
        "--username",
        db_user,
        "--dbname",
        db_name,
        "--file",
        str(export_file),
    ]

    # Ejecutar exportación
    print_color("📊 Exportando base de datos...", Colors.YELLOW)
    print_color(
        f"Comando: pg_dump -h {db_host} -p {db_port} -U {db_user} -d {db_name}",
        Colors.BLUE,
    )
    print()

    try:
        result = subprocess.run(
            cmd, env=env, capture_output=True, text=True, timeout=300
        )

        if result.returncode != 0:
            print_color(f"❌ Error en pg_dump:", Colors.RED)
            print_color(result.stderr, Colors.RED)
            sys.exit(1)

        print_color(f"✅ Base de datos exportada: {export_file}", Colors.GREEN)

    except subprocess.TimeoutExpired:
        print_color("❌ Error: La exportación tardó demasiado (>5 minutos)", Colors.RED)
        sys.exit(1)
    except Exception as e:
        print_color(f"❌ Error durante la exportación: {str(e)}", Colors.RED)
        sys.exit(1)

    # Comprimir archivo
    compress_file(export_file, compressed_file)

    # Eliminar archivo sin comprimir
    os.remove(export_file)

    # Calcular checksum
    print_color("🔐 Generando checksum SHA256...", Colors.YELLOW)
    checksum = calculate_sha256(compressed_file)

    with open(checksum_file, "w") as f:
        f.write(f"{checksum}  {os.path.basename(compressed_file)}\n")

    print_color(f"✅ Checksum generado: {checksum_file}", Colors.GREEN)

    # Crear README
    create_readme(export_dir, compressed_file, checksum_file)

    # Resumen final
    file_size = os.path.getsize(compressed_file)
    size_mb = file_size / (1024 * 1024)

    print()
    print_color("=" * 64, Colors.BLUE)
    print_color("✅ EXPORTACIÓN COMPLETADA", Colors.GREEN)
    print_color("=" * 64, Colors.BLUE)
    print_color(f"Archivos generados en: {export_dir}/", Colors.YELLOW)
    print()
    print_color("Archivos:", Colors.BLUE)
    print_color(
        f"- {os.path.basename(compressed_file)} (archivo de datos)", Colors.YELLOW
    )
    print_color(f"- {os.path.basename(checksum_file)} (checksum)", Colors.YELLOW)
    print_color(f"- README.txt (instrucciones)", Colors.YELLOW)
    print()
    print_color(f"Tamaño: {size_mb:.2f} MB", Colors.BLUE)
    print()
    print_color("SIGUIENTE PASO:", Colors.GREEN)
    print_color(
        "1. Transferir estos archivos al servidor de producción:", Colors.YELLOW
    )
    print_color(f"   scp {export_dir}/*.* usuario@servidor:/ruta/", Colors.BLUE)
    print_color("2. En el servidor, ejecutar:", Colors.YELLOW)
    print_color("   python import_production_data.py", Colors.BLUE)
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_color("\n\n❌ Exportación cancelada por el usuario", Colors.RED)
        sys.exit(1)
    except Exception as e:
        print_color(f"\n❌ Error inesperado: {str(e)}", Colors.RED)
        import traceback

        traceback.print_exc()
        sys.exit(1)
