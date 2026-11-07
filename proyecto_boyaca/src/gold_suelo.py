"""Overlay municipios x capacidad de uso -> composición de suelo por municipio. Dueño: P4.

Estrategia del cruce (sección 7.4 del enunciado):
1. Ambas capas ya validadas y reparadas en silver.
2. Se reproyectan a EPSG:9377 (metros) ANTES de intersectar: las áreas en grados no sirven.
3. Se disuelven los polígonos IGAC por clase: de ~958 polígonos a ~8 multipolígonos. El overlay
   es mucho más rápido y el resultado es el mismo para la composición por clase.
4. geopandas.overlay(how="intersection", keep_geom_type=True) descarta líneas y puntos
   que aparecen en los bordes compartidos.
5. % por clase = área de la clase en el municipio / área municipal cubierta por la capa x 100.
   % sin clasificar = (área municipal - área cubierta) / área municipal x 100.
"""
import geopandas as gpd
import polars as pl

from src.calidad import registrar
from src.config import CRS_AREAS, GOLD
from src.contratos import cumplir
from src.silver_suelo import CLASES_AGROLOGICAS


def composicion_suelo(municipios: gpd.GeoDataFrame, capacidad: gpd.GeoDataFrame):
    mun = municipios[["codigo_municipio", "geometry"]].to_crs(CRS_AREAS)
    mun["area_municipio_ha"] = mun.geometry.area / 10_000

    suelo = capacidad[["clase", "geometry"]].to_crs(CRS_AREAS).dissolve(by="clase").reset_index()
    inter = gpd.overlay(mun, suelo, how="intersection", keep_geom_type=True)
    inter["area_ha"] = inter.geometry.area / 10_000

    largo = (pl.from_pandas(inter.drop(columns="geometry"))
               .group_by(["codigo_municipio", "clase"]).agg(pl.col("area_ha").sum()))
    areas = pl.from_pandas(mun.drop(columns="geometry"))
    cubierta = largo.group_by("codigo_municipio").agg(area_clasificada_ha=pl.col("area_ha").sum())

    largo = (largo.join(cubierta, on="codigo_municipio")
                  .with_columns(pct_area=pl.col("area_ha") / pl.col("area_clasificada_ha") * 100))

    resumen = (areas.join(cubierta, on="codigo_municipio", how="left")
                    .with_columns(pl.col("area_clasificada_ha").fill_null(0.0))
                    .with_columns(pct_sin_clasificar=((pl.col("area_municipio_ha") - pl.col("area_clasificada_ha"))
                                                      / pl.col("area_municipio_ha") * 100).clip(0, 100)))

    # clase predominante: solo entre clases agrológicas (ZU y CA no son "suelo")
    agro = largo.filter(pl.col("clase").is_in(CLASES_AGROLOGICAS))
    pred = (agro.sort("area_ha", descending=True).group_by("codigo_municipio")
                .agg(clase_predominante=pl.col("clase").first(),
                     pct_clase_predominante=pl.col("pct_area").first()))
    iii_iv = (largo.group_by("codigo_municipio")
                   .agg(pct_clases_iii_iv=pl.col("pct_area").filter(pl.col("clase").is_in(["III", "IV"])).sum()))
    resumen = resumen.join(pred, on="codigo_municipio", how="left").join(iii_iv, on="codigo_municipio", how="left")

    # ---------------- controles de gold
    n = resumen.height
    registrar("gold", "suelo", "municipios_sin_cobertura", n,
              resumen.filter(pl.col("area_clasificada_ha") == 0).height, "alertar",
              "Municipios que la capa IGAC no cubre")
    suma = largo.group_by("codigo_municipio").agg(s=pl.col("pct_area").sum())
    registrar("gold", "suelo", "composicion_suma_100", suma.height,
              suma.filter((pl.col("s") - 100).abs() > 0.01).height, "detener",
              "La composición de cada municipio suma 100 %")
    sobre = resumen.filter(pl.col("area_clasificada_ha") > pl.col("area_municipio_ha") * 1.01).height
    registrar("gold", "suelo", "area_clasificada_no_supera_municipio", n, sobre, "alertar",
              "Área IGAC dentro del municipio <= área municipal (+1 % de tolerancia por bordes)")
    registrar("gold", "suelo", "pct_sin_clasificar_mayor_5", n,
              resumen.filter(pl.col("pct_sin_clasificar") > 5).height, "alertar",
              "Municipios con más de 5 % de su área sin clase (bordes simplificados o vacíos de la capa)")

    largo = cumplir(largo.select("codigo_municipio", "clase", "area_ha", "pct_area"), "gold/suelo_municipio")
    resumen = cumplir(resumen, "gold/suelo_resumen")
    largo.sort(["codigo_municipio", "clase"]).write_parquet(GOLD / "suelo_municipio.parquet")
    resumen.sort("codigo_municipio").write_parquet(GOLD / "suelo_resumen.parquet")
    return largo, resumen


def distribucion_departamental(suelo_municipio: pl.DataFrame) -> pl.DataFrame:
    """% del área de Boyacá en cada clase (para la gráfica de distribución de clases)."""
    return (suelo_municipio.group_by("clase").agg(pl.col("area_ha").sum())
            .with_columns(pct_area=pl.col("area_ha") / pl.col("area_ha").sum() * 100)
            .sort("clase"))
