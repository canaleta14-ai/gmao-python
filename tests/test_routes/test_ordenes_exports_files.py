import io


def crear_orden_minima(client):
    payload = {
        "tipo": "Correctivo",
        "prioridad": "Media",
        "descripcion": "Orden para pruebas de exportación/archivos",
    }
    resp = client.post("/ordenes/", json=payload)
    assert resp.status_code in [200, 201]
    data = resp.get_json() or {}
    assert data.get("id") is not None
    return data.get("id")


def test_exportar_csv(authenticated_client):
    # Asegurar al menos una orden en el sistema
    crear_orden_minima(authenticated_client)

    resp = authenticated_client.get("/ordenes/exportar-csv")
    assert resp.status_code == 200
    # Validar cabeceras de archivo Excel
    assert (
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        in resp.headers.get("Content-Type", "")
    )
    cd = resp.headers.get("Content-Disposition", "")
    assert "attachment" in cd and "ordenes_trabajo.xlsx" in cd
    # Validar que hay contenido (no vacío)
    assert resp.data is not None and len(resp.data) > 100


def test_estadisticas_ordenes(authenticated_client):
    resp = authenticated_client.get("/ordenes/estadisticas")
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, dict)
    # Estructura mínima esperada
    for key in ["total", "por_estado"]:
        assert key in data


def test_listar_archivos_orden_vacio(authenticated_client):
    orden_id = crear_orden_minima(authenticated_client)
    resp = authenticated_client.get(f"/ordenes/api/{orden_id}/archivos")
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)


def test_agregar_enlace_sin_url(authenticated_client):
    orden_id = crear_orden_minima(authenticated_client)
    # Falta 'url' -> la ruta debe responder 400
    resp = authenticated_client.post(
        f"/ordenes/api/{orden_id}/enlaces", json={}
    )
    assert resp.status_code == 400
    data = resp.get_json() or {}
    assert "error" in data