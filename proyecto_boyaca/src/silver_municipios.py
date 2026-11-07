"""Bronze -> silver de límites municipales (DANE MGN 2025). Dueño: P3.

El GeoJSON del curso viene simplificado a 75 m: sirve para mapas, no para delimitar.
El área oficial es `area_km2` (calculada por el docente sobre la geometría original en EPSG:9377);
aquí se recalcula sobre la geometría simplificada solo para medir la diferencia.
"""
import geopandas as gpd
import polars as pl

from src.calidad import diagnosticar, registrar
from src.config import CRS_AREAS, CRS_ORIGEN, N_MUNICIPIOS, SILVER, bronze_csv
from src.geo import area_ha, leer_csv_wkt, reparar_geometrias


def construir_municipios(poblacion: pl.DataFrame | None = None, ruta=None) -> gpd.GeoDataFrame:
    ruta = ruta or bronze_csv("municipios_mgn")
    gdf = leer_csv_wkt(ruta, CRS_ORIGEN)
    diagnosticar(pl.from_pandas(gdf.drop(columns="geometry")), "bronze", "municipios_mgn")

    gdf["codigo_municipio"] = gdf["codigo_municipio"].str.strip().str.zfill(5)
    gdf["area_km2"] = gdf["area_km2"].astype(float)
    n = len(gdf)

    ok_cod = gdf["codigo_municipio"].str.fullmatch(r"15\d{3}")
    registrar("silver", "municipios", "codigo_divipola_valido", n, int((~ok_cod).sum()), "rechazar",
              "Código de 5 dígitos que inicia en 15")
    gdf = gdf[ok_cod]

    dup = gdf["codigo_municipio"].duplicated()
    registrar("silver", "municipios", "clave_unica", n, int(dup.sum()), "detener", "Un polígono por municipio")
    if dup.any():
        raise ValueError("Municipios repetidos en el MGN")

    registrar("silver", "municipios", "cardinalidad", N_MUNICIPIOS, abs(N_MUNICIPIOS - len(gdf)), "alertar",
              f"Se esperaban {N_MUNICIPIOS} municipios; hay {len(gdf)}")

    gdf = reparar_geometrias(gdf, "silver", "municipios")

    # diferencia de área por la simplificación
    gdf["area_simplificada_km2"] = area_ha(gdf, CRS_AREAS) / 100
    dif_pct = (gdf["area_simplificada_km2"] - gdf["area_km2"]).abs() / gdf["area_km2"] * 100
    registrar("silver", "municipios", "area_simplificada_vs_oficial_mayor_2pct", len(gdf),
              int((dif_pct > 2).sum()), "alertar",
              f"Diferencia media {dif_pct.mean():.2f}% por la simplificación a 75 m")

    # nombre oficial DANE (el MGN viene en mayúsculas)
    if poblacion is not None:
        nombres = poblacion.select("codigo_municipio", "municipio").unique("codigo_municipio").to_pandas()
        gdf = gdf.merge(nombres, on="codigo_municipio", how="left")
        sin = int(gdf["municipio"].isna().sum())
        registrar("silver", "municipios", "codigo_existe_en_poblacion", len(gdf), sin, "alertar",
                  "Cada polígono tiene población DANE")
        gdf["municipio"] = gdf["municipio"].fillna(gdf["municipio_mgn"].str.title())
    else:
        gdf["municipio"] = gdf["municipio_mgn"].str.title()

    gdf = gdf[["codigo_municipio", "municipio", "area_km2", "area_simplificada_km2", "geometry"]]
    gdf = gdf.sort_values("codigo_municipio").reset_index(drop=True)
    gdf.to_parquet(SILVER / "municipios.geoparquet")
    return gdf
