"""Utilidades geográficas compartidas. Dueño: P3 (cambios por PR con revisión de P4)."""
import geopandas as gpd
import pandas as pd
from shapely.geometry import GeometryCollection, MultiPolygon, Polygon
from shapely.validation import make_valid

from src.calidad import registrar


def leer_csv_wkt(ruta, crs: str, columna_wkt: str = "geometry_wkt") -> gpd.GeoDataFrame:
    """Reconstruye un GeoDataFrame desde el CSV de bronze (geometría en WKT)."""
    df = pd.read_csv(ruta, dtype=str, keep_default_na=False, na_values=[""])
    geom = gpd.GeoSeries.from_wkt(df.pop(columna_wkt), crs=crs)
    return gpd.GeoDataFrame(df, geometry=geom, crs=crs)


def _solo_poligonos(g):
    """make_valid puede devolver colecciones con líneas o puntos: se conservan solo las áreas."""
    if g is None or g.is_empty:
        return g
    if isinstance(g, (Polygon, MultiPolygon)):
        return g
    if isinstance(g, GeometryCollection):
        partes = [p for p in g.geoms if isinstance(p, (Polygon, MultiPolygon))]
        polys = []
        for p in partes:
            polys.extend(p.geoms if isinstance(p, MultiPolygon) else [p])
        return MultiPolygon(polys) if polys else None
    return None


def reparar_geometrias(gdf: gpd.GeoDataFrame, capa: str, fuente: str) -> gpd.GeoDataFrame:
    """Cuenta nulas/vacías/inválidas, repara con make_valid y registra cada paso."""
    n = len(gdf)
    nulas = int((gdf.geometry.isna() | gdf.geometry.is_empty).sum())
    registrar(capa, fuente, "geometrias_nulas_o_vacias", n, nulas, "rechazar",
              "Sin geometría no hay polígono que dibujar ni intersectar")
    gdf = gdf[~(gdf.geometry.isna() | gdf.geometry.is_empty)].copy()

    invalidas = ~gdf.geometry.is_valid
    registrar(capa, fuente, "geometrias_invalidas_reparadas", n, int(invalidas.sum()), "alertar",
              "Autointersecciones u otros errores topológicos reparados con make_valid")
    if invalidas.any():
        gdf.loc[invalidas, "geometry"] = gdf.loc[invalidas, "geometry"].apply(
            lambda g: _solo_poligonos(make_valid(g)))
        perdidas = int(gdf.geometry.isna().sum())
        registrar(capa, fuente, "geometrias_irreparables", n, perdidas, "rechazar",
                  "Tras reparar no quedó un polígono")
        gdf = gdf[gdf.geometry.notna()].copy()

    tipos = gdf.geometry.geom_type.value_counts().to_dict()
    no_area = sum(v for k, v in tipos.items() if k not in ("Polygon", "MultiPolygon"))
    registrar(capa, fuente, "tipo_geometria_poligonal", n, no_area, "alertar", f"Tipos: {tipos}")
    return gdf


def area_ha(gdf: gpd.GeoDataFrame, crs_areas: str) -> pd.Series:
    """Área en hectáreas calculada en un CRS proyectado (metros)."""
    return gdf.to_crs(crs_areas).geometry.area / 10_000
