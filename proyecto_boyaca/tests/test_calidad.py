"""Pruebas unitarias del framework de calidad: no necesitan datos reales."""
import polars as pl
import pytest

from src import calidad
from src.calidad import Regla, ValidacionError, clave_unica, normalizar_texto, validar


@pytest.fixture(autouse=True)
def carpetas_temporales(tmp_path, monkeypatch):
    monkeypatch.setattr(calidad, "QUALITY", tmp_path / "quality")
    monkeypatch.setattr(calidad, "REJECTS", tmp_path / "rejects")
    return tmp_path


def test_rechaza_y_registra(carpetas_temporales):
    df = pl.DataFrame({"codigo_municipio": ["15001", "15002", "99999"], "v": [1, -1, 3]})
    ok = validar(df, [Regla("no_negativo", pl.col("v") >= 0), Regla("cod", calidad.codigo_divipola())],
                 "silver", "prueba")
    assert ok["codigo_municipio"].to_list() == ["15001"]
    rechazos = pl.read_parquet(carpetas_temporales / "rejects" / "silver_prueba.parquet")
    assert rechazos.height == 2 and "motivo_rechazo" in rechazos.columns
    metricas = pl.read_csv(carpetas_temporales / "quality" / "metricas_silver.csv")
    assert metricas["afectados"].to_list() == [1, 1]


def test_alertar_no_elimina():
    df = pl.DataFrame({"v": [1, -1]})
    assert validar(df, [Regla("aviso", pl.col("v") >= 0, "alertar")], "silver", "prueba").height == 2


def test_detener_lanza_error():
    df = pl.DataFrame({"k": ["a", "a"]})
    with pytest.raises(ValidacionError):
        validar(df, [Regla("unica", clave_unica(["k"]), "detener")], "silver", "prueba")


def test_nulo_no_es_cero():
    df = pl.DataFrame({"v": [None, 0]}, schema={"v": pl.Int64})
    ok = validar(df, [Regla("informado", pl.col("v").is_not_null())], "silver", "prueba")
    assert ok["v"].to_list() == [0]


def test_normalizar_texto():
    assert normalizar_texto("  Güicán de La  Sierra ") == "guican de la sierra"
