import io
import os

import pytest

from app.utils.storage import (
    upload_file,
    delete_file,
    list_files,
    file_exists,
    get_signed_url,
)


class DummyFile:
    def __init__(self, filename, content=b"test", content_type="text/plain"):
        self.filename = filename
        self.content_type = content_type
        self._buf = io.BytesIO(content)

    def seek(self, pos, whence=0):
        self._buf.seek(pos, whence)

    def tell(self):
        return self._buf.tell()

    def save(self, filepath):
        with open(filepath, "wb") as f:
            f.write(self._buf.getvalue())


@pytest.mark.unit
def test_upload_and_list_local(tmp_path, app):
    # Forzar entorno local
    os.environ.pop("GAE_ENV", None)
    os.environ.pop("K_SERVICE", None)

    folder = "ordenes"
    filename = "prueba.txt"
    dummy = DummyFile(filename, b"contenido")

    # Subir archivo local
    url = upload_file(dummy, folder)
    assert isinstance(url, str) and url.endswith(f"/{folder}/{filename}")

    # Verificar que existe físicamente
    local_path = url.lstrip("/")
    assert os.path.exists(local_path)

    # Listar archivos
    files = list_files(folder)
    assert filename in files

    # file_exists local
    assert file_exists(url, folder) is True

    # URL firmada en local regresa la misma ruta
    signed = get_signed_url(url, folder)
    assert signed == url

    # Eliminar
    assert delete_file(local_path, folder) is True
    assert file_exists(url, folder) is False


@pytest.mark.unit
def test_upload_too_large_is_rejected(app):
    # Archivo mayor a 10MB debe ser rechazado
    big_content = b"x" * (10 * 1024 * 1024 + 1)
    dummy = DummyFile("grande.bin", big_content, "application/octet-stream")

    url = upload_file(dummy, "manuales")
    assert url is None


@pytest.mark.unit
def test_list_files_with_prefix_and_uploads_paths(tmp_path, app):
    # Entorno local
    os.environ.pop("GAE_ENV", None)
    os.environ.pop("K_SERVICE", None)

    folder = "ordenes"

    # Crear múltiples archivos con y sin prefijo
    f1 = DummyFile("log-001.txt", b"a")
    f2 = DummyFile("log-002.txt", b"b")
    f3 = DummyFile("data-001.txt", b"c")

    url1 = upload_file(f1, folder)
    url2 = upload_file(f2, folder)
    url3 = upload_file(f3, folder)

    # Prefijo 'log'
    files_pref = list_files(folder, prefix="log")
    assert "log-001.txt" in files_pref
    assert "log-002.txt" in files_pref
    assert "data-001.txt" not in files_pref

    # Verificar rutas con '/uploads/...'
    assert file_exists(url1, folder) is True
    assert delete_file(url1, folder) is True
    assert file_exists(url1, folder) is False

    # Borrar restante por ruta local
    local2 = url2.lstrip("/")
    local3 = url3.lstrip("/")
    assert delete_file(local2, folder) is True
    assert delete_file(local3, folder) is True

    # Eliminar inexistente
    assert delete_file("/uploads/ordenes/no-existe.txt", folder) is False
    assert file_exists("/uploads/ordenes/no-existe.txt", folder) is False


@pytest.mark.unit
def test_gcs_branches_with_doubles(monkeypatch, app):
    # Forzar entorno GCP
    from app.utils import storage as storage_mod

    monkeypatch.setattr(storage_mod, "is_gcp_environment", lambda: True)

    captured = {"uploaded": [], "deleted": [], "signed": None}

    class FakeBlob:
        def __init__(self, name):
            self.name = name
            self._exists = False

        def upload_from_file(self, file, content_type=None):
            self._exists = True
            captured["uploaded"].append((self.name, content_type))

        def delete(self):
            captured["deleted"].append(self.name)
            self._exists = False

        def exists(self):
            return self._exists

        def generate_signed_url(self, version, expiration, method):
            captured["signed"] = (self.name, method)
            return f"https://signed.example/{self.name}"

    class FakeBucket:
        def __init__(self):
            self._blobs = {}

        def blob(self, path):
            if path not in self._blobs:
                self._blobs[path] = FakeBlob(path)
            return self._blobs[path]

        def list_blobs(self, prefix=None):
            # Retornar algunos blobs que coincidan con el prefijo
            names = [
                f"ordenes/log-001.txt",
                f"ordenes/log-002.txt",
                f"ordenes/data-001.txt",
            ]
            for n in names:
                self._blobs.setdefault(n, FakeBlob(n))
            if prefix:
                return [b for n, b in self._blobs.items() if n.startswith(prefix)]
            return list(self._blobs.values())

    class FakeClient:
        def bucket(self, name):
            return FakeBucket()

    monkeypatch.setattr(storage_mod, "get_storage_client", lambda: FakeClient())

    folder = "ordenes"
    dummy = DummyFile("gcs-archivo.txt", b"contenido", "text/plain")

    # Subida a GCS
    url = upload_file(dummy, folder)
    assert url.startswith("gs://")

    # file_exists GCS
    assert file_exists(url, folder) is True

    # Lista en GCS con prefijo
    files = list_files(folder, prefix="log")
    assert "log-001.txt" in files and "data-001.txt" not in files

    # URL firmada
    signed = get_signed_url(url, folder)
    assert signed.startswith("https://signed.example/")

    # Eliminar
    assert delete_file(url, folder) is True
    assert file_exists(url, folder) is False


@pytest.mark.unit
def test_gcs_client_failure(monkeypatch, app):
    # Forzar entorno GCP y que el cliente falle
    from app.utils import storage as storage_mod

    monkeypatch.setattr(storage_mod, "is_gcp_environment", lambda: True)
    monkeypatch.setattr(storage_mod, "get_storage_client", lambda: None)

    dummy = DummyFile("fallo.txt", b"x", "text/plain")

    # upload debe retornar None
    assert upload_file(dummy, "ordenes") is None

    # delete con gs:// debe retornar False
    assert delete_file("gs://bucket/ordenes/fallo.txt", "ordenes") is False

    # exists debe retornar False
    assert file_exists("gs://bucket/ordenes/fallo.txt", "ordenes") is False

    # signed url debe devolver la ruta original
    original = "/uploads/ordenes/fallo.txt"
    assert get_signed_url(original, "ordenes") == original


@pytest.mark.unit
def test_gcs_blob_missing(monkeypatch, app):
    # Simular cliente y bucket, pero blob no existe
    from app.utils import storage as storage_mod

    monkeypatch.setattr(storage_mod, "is_gcp_environment", lambda: True)

    class MissingBlob:
        def __init__(self, name):
            self.name = name

        def upload_from_file(self, file, content_type=None):
            # Simular subida, pero luego exists() retorna False
            pass

        def delete(self):
            pass

        def exists(self):
            return False

        def generate_signed_url(self, version, expiration, method):
            return f"https://signed.example/{self.name}"

    class FakeBucket:
        def blob(self, path):
            return MissingBlob(path)

        def list_blobs(self, prefix=None):
            return []

    class FakeClient:
        def bucket(self, name):
            return FakeBucket()

    monkeypatch.setattr(storage_mod, "get_storage_client", lambda: FakeClient())

    # exists debe ser False si el blob no existe
    assert file_exists("gs://bucket/ordenes/missing.txt", "ordenes") is False
    # delete debe ser False
    assert delete_file("gs://bucket/ordenes/missing.txt", "ordenes") is False
    # list_files retorna vacío
    assert list_files("ordenes", prefix="log") == []