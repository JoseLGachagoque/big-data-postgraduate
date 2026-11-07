"""Gold: claves, conciliación con silver, denominadores e indicadores."""
import geopandas as gpd
import polars as pl

from conftest import requiere
from src.config import ANIO_EVA, ANIO_MDM, GOLD, N_MUNICIPIOS, SILVER


def _ma():
    return pl.read_parquet(requiere(GOLD / "municipio_anio.parquet"))


def test_clave_y_cardinalidad():
    df = _ma()
    assert df.select(pl.struct("codigo_municipio", "anio").is_duplicated().sum()).item() == 0
    assert (df.group_by("anio").len()["len"] == N_MUNICIPIOS).all()


def test_concilia_poblacion_con_silver():
    pob = pl.read_parquet(requiere(SILVER / "poblacion.parquet"))
    assert _ma()["poblacion_total"].sum() == pob["poblacion_total"].sum()


def test_concilia_produccion_con_silver():
    agr = pl.read_parquet(requiere(SILVER / "agricola.parquet"))
    total = _ma().filter(pl.col("anio") == ANIO_EVA)["produccion_total_t"].sum()
    assert abs(total - agr["produccion_t"].sum()) < 1e-6


def test_porcentajes_y_finitos():
    df = _ma()
    for c in ["prop_18_44_pct", "prop_18_64_pct", "pct_rural", "pct_sin_clasificar", "pct_clases_iii_iv"]:
        s = df[c].drop_nulls()
        assert s.is_between(0, 100).all(), c
    for c in ["produccion_1k_18_64", "rendimiento_papa_t_ha"]:
        assert df[c].drop_nulls().is_finite().all(), c


def test_variables_en_su_anio():
    df = _ma()
    assert df.filter(pl.col("anio") != ANIO_MDM)["puntaje_mdm"].null_count() == df.filter(pl.col("anio") != ANIO_MDM).height
    assert df.filter(pl.col("anio") != ANIO_EVA)["produccion_total_t"].null_count() == df.filter(pl.col("anio") != ANIO_EVA).height


def test_suelo_suma_100():
    s = pl.read_parquet(requiere(GOLD / "suelo_municipio.parquet"))
    sumas = s.group_by("codigo_municipio").agg(pl.col("pct_area").sum())["pct_area"]
    assert ((sumas - 100).abs() < 0.01).all()


def test_maestro_tiene_geometria():
    g = gpd.read_parquet(requiere(GOLD / "maestro_boyaca.geoparquet"))
    assert len(g) == N_MUNICIPIOS and g.geometry.notna().all()
