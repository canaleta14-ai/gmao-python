#!/usr/bin/env python3
"""
Script de verificación completa de todos los módulos del sistema GMAO
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.factory import create_app


def verificar_modulos():
    """Verifica que todos los módulos funcionen correctamente"""
    print("🔍 VERIFICACIÓN COMPLETA DE MÓDULOS GMAO")
    print("=" * 60)

    app = create_app()

    with app.app_context():
        try:
            # 1. Verificar base de datos
            print("\n1. 🗄️ VERIFICANDO BASE DE DATOS...")
            from app.extensions import db

            db.session.execute(db.text("SELECT 1"))
            print("   ✅ Conexión a BD exitosa")

            # 2. Verificar modelos/tablas
            print("\n2. 📋 VERIFICANDO MODELOS Y TABLAS...")
            from app.models.usuario import Usuario
            from app.models.activo import Activo
            from app.models.orden_trabajo import OrdenTrabajo
            from app.models.inventario import Inventario
            from app.models.plan_mantenimiento import PlanMantenimiento
            from app.models.proveedor import Proveedor
            from app.models.categoria import Categoria

            modelos = [
                ("Usuario", Usuario),
                ("Activo", Activo),
                ("OrdenTrabajo", OrdenTrabajo),
                ("Inventario", Inventario),
                ("PlanMantenimiento", PlanMantenimiento),
                ("Proveedor", Proveedor),
                ("Categoria", Categoria),
            ]

            for nombre, modelo in modelos:
                try:
                    count = modelo.query.count()
                    print(f"   ✅ {nombre}: {count} registros")
                except Exception as e:
                    print(f"   ❌ {nombre}: Error - {e}")

            # 3. Verificar blueprints/rutas
            print("\n3. 🛣️ VERIFICANDO BLUEPRINTS Y RUTAS...")
            blueprints = [
                "web",
                "usuarios_controller",
                "activos",
                "ordenes",
                "inventario",
                "planes",
                "estadisticas",
                "proveedores",
                "categorias",
            ]

            for bp_name in blueprints:
                if bp_name in app.blueprints:
                    print(f"   ✅ Blueprint '{bp_name}' registrado")
                else:
                    print(f"   ❌ Blueprint '{bp_name}' NO registrado")

            # 4. Verificar rutas principales
            print("\n4. 🔗 VERIFICANDO RUTAS PRINCIPALES...")
            rutas_principales = [
                "/",
                "/login",
                "/dashboard",
                "/activos/",
                "/ordenes/",
                "/usuarios/",
                "/inventario/",
                "/planes/",
                "/health",
            ]

            with app.test_client() as client:
                for ruta in rutas_principales:
                    try:
                        response = client.get(ruta, follow_redirects=False)
                        status = response.status_code
                        if status in [200, 302, 401]:  # Códigos esperados
                            print(f"   ✅ {ruta}: HTTP {status}")
                        else:
                            print(f"   ⚠️ {ruta}: HTTP {status}")
                    except Exception as e:
                        print(f"   ❌ {ruta}: Error - {e}")

            # 5. Verificar controladores
            print("\n5. 🎮 VERIFICANDO CONTROLADORES...")
            try:
                from app.controllers.usuarios_controller import autenticar_usuario

                print("   ✅ usuarios_controller importado")

                from app.controllers.activos_controller import listar_activos

                print("   ✅ activos_controller importado")

                from app.controllers.ordenes_controller import listar_ordenes

                print("   ✅ ordenes_controller importado")

                from app.controllers.inventario_controller_simple import (
                    obtener_estadisticas_inventario,
                )

                print("   ✅ inventario_controller importado")

                from app.controllers.planes_controller import listar_planes

                print("   ✅ planes_controller importado")

            except Exception as e:
                print(f"   ❌ Error importando controladores: {e}")

            # 6. Verificar extensiones
            print("\n6. 🔧 VERIFICANDO EXTENSIONES...")
            try:
                from app.extensions import db, csrf, limiter

                print("   ✅ Extensions básicas (db, csrf, limiter)")

                from flask_login import LoginManager

                print("   ✅ Flask-Login")

                from flask_migrate import Migrate

                print("   ✅ Flask-Migrate")

            except Exception as e:
                print(f"   ❌ Error con extensiones: {e}")

            # 7. Verificar templates
            print("\n7. 🎨 VERIFICANDO TEMPLATES...")
            templates_principales = [
                "web/login.html",
                "web/dashboard.html",
                "base.html",
            ]

            for template in templates_principales:
                template_path = os.path.join("app", "templates", template)
                if os.path.exists(template_path):
                    print(f"   ✅ {template}")
                else:
                    print(f"   ❌ {template} NO encontrado")

            # 8. Verificar archivos estáticos
            print("\n8. 📁 VERIFICANDO ARCHIVOS ESTÁTICOS...")
            static_files = ["static/css", "static/js", "static/img"]

            for static_dir in static_files:
                if os.path.exists(static_dir):
                    files_count = (
                        len(os.listdir(static_dir)) if os.path.isdir(static_dir) else 0
                    )
                    print(f"   ✅ {static_dir}: {files_count} archivos")
                else:
                    print(f"   ❌ {static_dir} NO encontrado")

            # 9. Verificar configuración
            print("\n9. ⚙️ VERIFICANDO CONFIGURACIÓN...")
            configs = [
                ("SECRET_KEY", app.config.get("SECRET_KEY")),
                ("SQLALCHEMY_DATABASE_URI", app.config.get("SQLALCHEMY_DATABASE_URI")),
                ("CSRF_ENABLED", app.config.get("WTF_CSRF_ENABLED")),
                ("DEBUG", app.config.get("DEBUG")),
            ]

            for config_name, config_value in configs:
                if config_value is not None:
                    print(
                        f"   ✅ {config_name}: {'***' if 'SECRET' in config_name else config_value}"
                    )
                else:
                    print(f"   ❌ {config_name}: NO configurado")

            # 10. Test de login completo
            print("\n10. 🔐 TEST DE LOGIN COMPLETO...")
            try:
                # Buscar usuario admin
                admin = Usuario.query.filter_by(username="admin").first()
                if admin:
                    print(f"   ✅ Usuario admin encontrado (ID: {admin.id})")

                    # Test de autenticación
                    if admin.check_password("admin123"):
                        print("   ✅ Autenticación correcta")

                        # Test de login via controlador
                        from app.controllers.usuarios_controller import (
                            autenticar_usuario,
                        )

                        user_auth = autenticar_usuario("admin", "admin123")
                        if user_auth:
                            print("   ✅ Login via controlador exitoso")
                        else:
                            print("   ❌ Login via controlador falló")
                    else:
                        print("   ❌ Autenticación falló")
                else:
                    print("   ❌ Usuario admin no encontrado")

            except Exception as e:
                print(f"   ❌ Error en test de login: {e}")

            print("\n" + "=" * 60)
            print("🎉 VERIFICACIÓN COMPLETADA")
            print("Si todos los módulos muestran ✅, la aplicación está lista")

        except Exception as e:
            print(f"❌ Error durante verificación: {e}")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    verificar_modulos()
