"""Bronze: los CSV no se alteraron después de la ingesta (hash del manifiesto)."""
import hashlib
import json

from conftest import requiere
from src.config import BRONZE, FUENTES, ROOT


def test_manifiesto_sin_errores():
    m = json.loads(requiere(BRONZE / "manifest_bronze.json").read_text(encoding="utf-8"))
    assert m["errores"] == []
    assert {f["fuente"] for f in m["fuentes"]} == set(FUENTES)


def test_bronze_integro():
    m = json.loads(requiere(BRONZE / "manifest_bronze.json").read_text(encoding="utf-8"))
    for f in m["fuentes"]:
        p = ROOT / f["archivo_bronze"]
        assert hashlib.sha256(p.read_bytes()).hexdigest() == f["sha256_bronze"], f["fuente"]


def test_geometrias_en_wkt():
    for fuente in ("municipios_mgn", "capacidad_uso_igac"):
        cab = requiere(BRONZE / fuente / f"{fuente}.csv").open(encoding="utf-8").readline()
        assert "geometry_wkt" in cab
