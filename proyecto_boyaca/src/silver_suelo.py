"""Bronze -> silver de capacidad de uso de las tierras (IGAC 1:100.000, 2004). Dueño: P4.

- El GeoJSON original no declara CRS; las coordenadas están en grados -> se asume EPSG:4326
  (registrado en el manifiesto de bronze).
- Clases presentes: III a VIII, más ZU (zona urbana) y CA (cuerpo de agua). No hay I ni II.
  ZU y CA se conservan como categorías propias: no son clases agrológicas.
- Es capacidad de uso a escala 1:100.000 de 2004, no una medición actual de fertilidad.
"""
import geopandas as gpd
import polars as pl

from src.calidad import a_snake, diagnosticar, registrar
from src.config import CRS_AREAS, CRS_ORIGEN, SILVER, bronze_csv
from src.geo import area_ha, leer_csv_wkt, reparar_geometrias

CLASES_AGROLOGICAS = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII"]
OTRAS_CATEGORIAS = ["ZU", "CA"]   # zona urbana, cuerpo de agua


def construir_capacidad_uso(ruta=None) -> gpd.GeoDataFrame:
    ruta = ruta or bronze_csv("capacidad_uso_igac")
    gdf = leer_csv_wkt(ruta, CRS_ORIGEN)
    gdf.columns = [c if c == "geometry" else a_snake(c) for c in gdf.columns]   # 'ÁREA_HA_1' -> 'area_ha_1'
    diagnosticar(pl.from_pandas(gdf.drop(columns="geometry")), "bronze", "capacidad_uso_igac")
    n = len(gdf)

    gdf["clase"] = gdf["clase"].str.strip().str.upper()
    validas = gdf["clase"].isin(CLASES_AGROLOGICAS + OTRAS_CATEGORIAS)
    registrar("silver", "capacidad_uso", "clase_valida", n, int((~validas).sum()), "rechazar",
              "Clase en I-VIII, ZU o CA")
    gdf = gdf[validas].copy()

    presentes = sorted(gdf["clase"].unique())
    faltantes = [c for c in CLASES_AGROLOGICAS if c not in presentes]
    registrar("silver", "capacidad_uso", "clases_ausentes", len(CLASES_AGROLOGICAS), len(faltantes), "alertar",
              f"Clases sin polígonos en Boyacá: {faltantes}")

    gdf = reparar_geometrias(gdf, "silver", "capacidad_uso")

    gdf["area_ha"] = area_ha(gdf, CRS_AREAS)
    if "area_ha_1" in gdf.columns:   # área reportada por el IGAC, para contrastar
        fuente = gdf["area_ha_1"].astype(float)
        dif = (gdf["area_ha"] - fuente).abs() / fuente.where(fuente > 0) * 100
        registrar("silver", "capacidad_uso", "area_calculada_vs_igac_mayor_5pct", len(gdf),
                  int((dif > 5).sum()), "alertar",
                  f"Diferencia mediana {dif.median():.2f}% entre área en EPSG:9377 y la reportada")
    registrar("silver", "capacidad_uso", "area_positiva", len(gdf), int((gdf["area_ha"] <= 0).sum()),
              "alertar", "Polígonos con área > 0")

    cols = [c for c in ["objectid", "ucs_cp", "clase", "subclase", "grupo_manejo", "ucs",
                        "principales_caracteristicas", "principales_limitantes", "uso_actual",
                        "usos_recomendados", "area_ha"] if c in gdf.columns]
    gdf = gdf[cols + ["geometry"]].reset_index(drop=True)
    gdf.to_parquet(SILVER / "capacidad_uso.geoparquet")
    return gdf
