"""Datos ficticios con el esquema exacto de los contratos. Dueño: P6.

Sirven para que P3, P4 y P5 programen el día 1 sin esperar a las tablas reales:
cada función del proyecto recibe DataFrames, así que con el mock se prueba igual.

    python -m src.mocks          # escribe tests/fixtures/*.parquet

Los valores son aleatorios (semilla fija): NO usar para conclusiones.
"""
import geopandas as gpd
import numpy as np
import polars as pl
from shapely.geometry import box

from src.config import CRS_ORIGEN, FIXTURES, bronze_csv
from src.contratos import CONTRATOS

rng = np.random.default_rng(42)
CLASES = ["III", "IV", "V", "VI", "VII", "VIII", "ZU", "CA"]


def _codigos() -> list[str]:
    ruta = bronze_csv("poblacion_dane")
    if ruta.exists():
        return sorted(pl.read_csv(ruta, infer_schema_length=0)["codigo_municipio"].str.zfill(5).unique())
    return [f"15{n:03d}" for n in range(1, 124)]


def _columna(nombre: str, tipo, n: int):
    if nombre == "clase" or nombre == "clase_predominante":
        return rng.choice(CLASES, n)
    if nombre == "anio":
        return rng.integers(2020, 2026, n)
    if nombre == "edad":
        return rng.integers(0, 86, n)
    if nombre in ("grupo_capacidad",):
        return rng.choice(["G1", "G2", "G3", "G4", "G5"], n)
    if tipo == pl.Utf8:
        return [f"{nombre}_{i % 7}" for i in range(n)]
    if tipo == pl.Boolean:
        return rng.random(n) < 0.5
    if tipo in (pl.Int16, pl.Int64):
        return rng.integers(100, 200_000, n)
    if "pct" in nombre or "puntaje" in nombre:
        return rng.uniform(0, 100, n)
    return rng.lognormal(3, 1.2, n)


def tabla_mock(tabla: str) -> pl.DataFrame:
    cods = _codigos()
    if tabla in ("gold/municipio_anio", "silver/poblacion"):
        base = {"codigo_municipio": np.repeat(cods, 6), "anio": np.tile(range(2020, 2026), len(cods))}
    elif tabla in ("gold/suelo_resumen",):
        base = {"codigo_municipio": cods}
    elif tabla == "gold/suelo_municipio":
        base = {"codigo_municipio": np.repeat(cods, len(CLASES)), "clase": np.tile(CLASES, len(cods))}
    else:
        base = {"codigo_municipio": np.repeat(cods, 3)}
    n = len(base["codigo_municipio"])
    datos = {k: (base[k] if k in base else _columna(k, t, n)) for k, t in CONTRATOS[tabla]["columnas"].items()}
    df = pl.DataFrame(datos).with_columns([pl.col(k).cast(t) for k, t in CONTRATOS[tabla]["columnas"].items()])
    if "anio" in df.columns and tabla == "gold/municipio_anio":
        df = df.with_columns(
            puntaje_mdm=pl.when(pl.col("anio") == 2020).then(pl.col("puntaje_mdm")),
            produccion_total_t=pl.when(pl.col("anio") == 2023).then(pl.col("produccion_total_t")))
    return df.unique(CONTRATOS[tabla]["clave"], keep="first")


def municipios_mock() -> gpd.GeoDataFrame:
    """Cuadrículas falsas sobre Boyacá para probar mapas sin el MGN."""
    cods = _codigos()
    geoms = [box(-74.5 + (i % 12) * 0.2, 4.6 + (i // 12) * 0.2, -74.3 + (i % 12) * 0.2, 4.8 + (i // 12) * 0.2)
             for i in range(len(cods))]
    return gpd.GeoDataFrame({"codigo_municipio": cods, "municipio": [f"Municipio {c}" for c in cods]},
                            geometry=geoms, crs=CRS_ORIGEN)


def generar_mocks() -> None:
    FIXTURES.mkdir(parents=True, exist_ok=True)
    for tabla in CONTRATOS:
        tabla_mock(tabla).write_parquet(FIXTURES / f"{tabla.replace('/', '__')}.parquet")
    municipios_mock().to_parquet(FIXTURES / "silver__municipios.geoparquet")
    print(f"Mocks escritos en {FIXTURES}")


if __name__ == "__main__":
    generar_mocks()
