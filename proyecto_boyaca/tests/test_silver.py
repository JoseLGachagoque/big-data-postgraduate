"""Silver: claves, cardinalidad y rangos de las tablas reales."""
import geopandas as gpd
import polars as pl

from conftest import requiere
from src.config import MDM_BLOQUE_OFICIAL, N_MUNICIPIOS, SILVER
from src.contratos import CONTRATOS


def _leer(nombre):
    return pl.read_parquet(requiere(SILVER / f"{nombre}.parquet"))


def test_poblacion():
    df = _leer("poblacion")
    assert df.height == N_MUNICIPIOS * 6
    assert df.select(pl.struct(CONTRATOS["silver/poblacion"]["clave"]).is_duplicated().sum()).item() == 0
    assert df["codigo_municipio"].str.contains(r"^15\d{3}$").all()
    assert (df["pob_18_44"] <= df["pob_18_64"]).all() and (df["pob_18_64"] <= df["poblacion_total"]).all()


def test_poblacion_area_sin_total():
    df = _leer("poblacion_area")
    assert set(df["area"].unique()) == {"cabecera", "rural"}   # la fila Total no se carga: no hay doble conteo
    assert (df["personas"] >= 0).all()


def test_desempeno_bloque_oficial():
    df = _leer("desempeno")
    of = df.filter(pl.col("es_bloque_oficial"))
    assert of["bloque"].unique().to_list() == [MDM_BLOQUE_OFICIAL]
    assert of["codigo_municipio"].n_unique() == of.height <= N_MUNICIPIOS
    assert of["nombre_coherente"].all()
    assert of["puntaje_mdm"].is_between(0, 100).all()


def test_agricola():
    df = _leer("agricola")
    assert (df["produccion_t"] >= 0).all() and (df["area_cosechada_ha"] >= 0).all()
    assert df.select(pl.struct(CONTRATOS["silver/agricola"]["clave"]).is_duplicated().sum()).item() == 0


def test_geometrias():
    mun = gpd.read_parquet(requiere(SILVER / "municipios.geoparquet"))
    suelo = gpd.read_parquet(requiere(SILVER / "capacidad_uso.geoparquet"))
    assert len(mun) == N_MUNICIPIOS and mun["codigo_municipio"].is_unique
    assert mun.is_valid.all() and suelo.is_valid.all()
    assert mun.crs.to_epsg() == 4326 and suelo.crs.to_epsg() == 4326
