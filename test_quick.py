import requests
import time


def quick_test():
    base = "http://localhost:5000"

    print("🚀 PRUEBA RÁPIDA DE MÓDULOS GMAO")
    print("=" * 50)

    modules = [
        ("Principal", "/"),
        ("Login", "/login"),
        ("Usuarios", "/usuarios"),
        ("Activos", "/activos"),
        ("Órdenes", "/ordenes"),
        ("Planes", "/planes"),
        ("Inventario", "/inventario"),
        ("Proveedores", "/proveedores"),
        ("Solicitudes", "/solicitudes"),
        ("Reportes", "/reportes"),
    ]

    ok = 0
    total = len(modules)

    for name, url in modules:
        try:
            r = requests.get(base + url, timeout=5)
            if r.status_code in [200, 302]:
                print(f"✅ {name:12} OK ({r.status_code})")
                ok += 1
            else:
                print(f"❌ {name:12} Error {r.status_code}")
        except:
            print(f"❌ {name:12} Fallo conexión")
        time.sleep(0.2)

    print("\n" + "=" * 50)
    print(f"RESULTADO: {ok}/{total} módulos funcionando")
    print(f"Éxito: {ok/total*100:.1f}%")

    if ok == total:
        print("🎉 ¡PERFECTO! Todos los módulos funcionan")
    elif ok >= total * 0.8:
        print("✅ Sistema funcional (mayoría de módulos OK)")
    else:
        print("⚠️ Sistema con problemas")


if __name__ == "__main__":
    quick_test()
