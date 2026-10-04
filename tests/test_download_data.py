from pathlib import Path

import pytest
import requests

from src.download_data import (
    GeospatialDatasetImporter,
    download_file,
    formate_code_territoire,
    get_cadastre_url,
)


class DummyResponse:
    def __init__(self, payload=b"abc", status_code=200):
        self.payload = payload
        self.status_code = status_code

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP {self.status_code}")

    def iter_content(self, chunk_size=8192):
        for i in range(0, len(self.payload), chunk_size):
            yield self.payload[i : i + chunk_size]


def test_download_file_writes_content_to_disk(monkeypatch, tmp_path):
    target = tmp_path / "downloaded.bin"

    def fake_get(url, headers=None, stream=None, timeout=None):
        assert url == "https://example.com/file"
        return DummyResponse(payload=b"hello world")

    monkeypatch.setattr("requests.get", fake_get)

    result = download_file("https://example.com/file", target)

    assert result == target
    assert target.read_bytes() == b"hello world"


def test_download_file_raises_on_http_error(monkeypatch, tmp_path):
    target = tmp_path / "downloaded.bin"

    def fake_get(url, headers=None, stream=None, timeout=None):
        return DummyResponse(payload=b"", status_code=404)

    monkeypatch.setattr("requests.get", fake_get)

    with pytest.raises(requests.HTTPError):
        download_file("https://example.com/file", target)


def test_get_cadastre_url_for_department():
    assert get_cadastre_url("95", "communes") == (
        "https://cadastre.data.gouv.fr/bundler/cadastre-etalab/departements/95/shp/communes"
    )


def test_get_cadastre_url_for_commune():
    assert get_cadastre_url("75056", "parcelles") == (
        "https://cadastre.data.gouv.fr/bundler/cadastre-etalab/communes/75056/shp/parcelles"
    )


def test_get_cadastre_url_invalid_layer_raises():
    with pytest.raises(AssertionError):
        get_cadastre_url("95", "invalide")


def test_formate_code_territoire_department():
    assert formate_code_territoire("95") == ("95", None)


def test_formate_code_territoire_commune():
    assert formate_code_territoire("75056") == ("75", "75056")


def test_formate_code_territoire_invalid_raises():
    with pytest.raises(ValueError):
        formate_code_territoire("123")


def test_geospatial_dataset_importer_filename_is_sanitized():
    importer = GeospatialDatasetImporter(
        None, "https://example.com/data", "Mon Quartier", ".geojson"
    )

    assert importer.name == "mon_quartier"
    assert importer.filename == "mon_quartier.geojson"


def test_geospatial_dataset_importer_download_rejects_empty_file(monkeypatch, tmp_path):
    class FakeSession:
        def __init__(self):
            self.headers = {}

        def get(self, url, stream=True, timeout=None):
            return DummyResponse(payload=b"", status_code=200)

    importer = GeospatialDatasetImporter(
        None, "https://example.com/data", "test", ".geojson"
    )
    importer.session = FakeSession()

    with pytest.raises(ValueError, match="Downloaded file is empty"):
        importer.download(tmp_path / "test.geojson")


def test_geospatial_dataset_importer_load_geodataframe_uses_epsg_2154(monkeypatch):
    class FakeGeoDataFrame:
        def __init__(self):
            self.crs = "EPSG:4326"

        def to_crs(self, crs):
            assert crs == "EPSG:2154"
            self.crs = crs
            return self

    fake_gdf = FakeGeoDataFrame()

    monkeypatch.setattr("src.download_data.gpd.read_file", lambda path: fake_gdf)

    importer = GeospatialDatasetImporter(
        None, "https://example.com/data", "test", ".geojson"
    )
    loaded = importer.load_geodataframe(Path("fake.geojson"))

    assert loaded.crs == "EPSG:2154"
