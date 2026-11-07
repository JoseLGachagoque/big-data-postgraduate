"""Integración de silver/gold parciales en las tablas analíticas. Dueño: P6.

- gold/municipio_anio.parquet      grano municipio-año (123 x 6 años = 738 filas).
- gold/maestro_boyaca.geoparquet   una fila por municipio, variables de análisis + geometría (mapas).

Principios (sección 7.3 del enunciado):
- Cada fuente se agrega a su grano ANTES de unir: así no se duplica producción ni población.
- Todas las uniones son LEFT sobre la población (la base de 123 municipios) y se reporta
  cuántas claves cruzaron y cuáles quedaron sin vincular en cada lado.
- Cada variable vive solo en su año: puntaje_mdm solo en 2020, producción solo en 2023.
  En los demás años queda null (no hay dato), nunca 0.
"""
import geopandas as gpd
import polars as pl

from src.calidad import Regla, entre, registrar, validar, verificar_cardinalidad
from src.config import ANIO_EVA, ANIO_MDM, GOLD, N_MUNICIPIOS, QUALITY
from src.contratos import cumplir


def reporte_union(izq: pl.DataFrame, der: pl.DataFrame, clave: list[str], nombre: str) -> None:
    """Registra coincidencias y no vinculados de una unión; guarda la lista para revisión."""
    a, b = izq.select(clave).unique(), der.select(clave).unique()
    solo_izq = a.join(b, on=clave, how="anti").with_columns(lado=pl.lit("solo_izquierda"))
    solo_der = b.join(a, on=clave, how="anti").with_columns(lado=pl.lit("solo_derecha"))
    coinciden = a.join(b, on=clave, how="semi").height
    registrar("gold", "integracion", f"union_{nombre}_sin_vincular_izq", a.height, solo_izq.height, "alertar",
              f"{coinciden} claves coinciden; {solo_izq.height} de la base sin dato en {nombre}")
    registrar("gold", "integracion", f"union_{nombre}_sin_vincular_der", b.height, solo_der.height, "alertar",
              f"{solo_der.height} claves de {nombre} que no existen en la base")
    pl.concat([solo_izq, solo_der]).write_csv(QUALITY / f"no_vinculados_{nombre}.csv")


def _pct(num: str, den: str) -> pl.Expr:
    return pl.when(pl.col(den) > 0).then(pl.col(num) / pl.col(den) * 100)


def construir_municipio_anio(poblacion: pl.DataFrame, desempeno: pl.DataFrame,
                             agricola_municipal: pl.DataFrame, pct_rural: pl.DataFrame,
                             suelo_resumen: pl.DataFrame) -> pl.DataFrame:
    clave = ["codigo_municipio", "anio"]
    base = poblacion.with_columns(
        prop_18_44_pct=_pct("pob_18_44", "poblacion_total"),
        prop_18_64_pct=_pct("pob_18_64", "poblacion_total"),
        prop_mujeres_18_44_pct=_pct("mujeres_18_44", "poblacion_total"),
        prop_hombres_18_44_pct=_pct("hombres_18_44", "poblacion_total"),
    )

    mdm = (desempeno.filter(pl.col("es_bloque_oficial"))
                    .select("codigo_municipio", "anio", "grupo_capacidad", "puntaje_mdm"))
    reporte_union(base.filter(pl.col("anio") == ANIO_MDM), mdm, clave, "desempeno")
    reporte_union(base.filter(pl.col("anio") == ANIO_EVA), agricola_municipal, clave, "agricola")
    reporte_union(base, pct_rural, clave, "pct_rural")
    reporte_union(base.select("codigo_municipio").unique(), suelo_resumen.select("codigo_municipio"),
                  ["codigo_municipio"], "suelo")

    df = (base.join(mdm, on=clave, how="left")
              .join(agricola_municipal, on=clave, how="left")
              .join(pct_rural, on=clave, how="left")
              .join(suelo_resumen.select("codigo_municipio", "clase_predominante", "pct_sin_clasificar",
                                         "pct_clases_iii_iv"), on="codigo_municipio", how="left")
              .with_columns(produccion_1k_18_64=pl.when(pl.col("pob_18_64") > 0)
                            .then(pl.col("produccion_total_t") / pl.col("pob_18_64") * 1000)))

    # ---------------- controles de gold
    registrar("gold", "municipio_anio", "conciliacion_poblacion_silver", poblacion.height,
              int(df["poblacion_total"].sum() != poblacion["poblacion_total"].sum()), "detener",
              "La población total no cambia al integrar (sin duplicados por las uniones)")
    if df.height != poblacion.height:
        raise ValueError(f"Las uniones multiplicaron filas: {poblacion.height} -> {df.height}")

    pcts = ["prop_18_44_pct", "prop_18_64_pct", "prop_mujeres_18_44_pct", "prop_hombres_18_44_pct",
            "pct_rural", "pct_sin_clasificar", "pct_clases_iii_iv"]
    reglas = [
        Regla("porcentajes_0_100", pl.all_horizontal([entre(c, 0, 100) for c in pcts]), "detener",
              "Todas las proporciones entre 0 y 100"),
        Regla("mdm_solo_en_su_anio", (pl.col("anio") == ANIO_MDM) | pl.col("puntaje_mdm").is_null(), "detener",
              f"puntaje_mdm solo en {ANIO_MDM}"),
        Regla("produccion_solo_en_su_anio", (pl.col("anio") == ANIO_EVA) | pl.col("produccion_total_t").is_null(),
              "detener", f"Producción solo en {ANIO_EVA}"),
        Regla("indicadores_finitos",
              pl.all_horizontal([pl.col(c).is_null() | pl.col(c).is_finite()
                                 for c in ["produccion_1k_18_64", "rendimiento_papa_t_ha"]]),
              "detener", "Sin infinitos: no hubo división entre cero"),
        Regla("mdm_disponible_en_2020", (pl.col("anio") != ANIO_MDM) | pl.col("puntaje_mdm").is_not_null(),
              "alertar", "Municipios de 2020 sin puntaje (quedan fuera de la hipótesis principal)"),
        Regla("produccion_disponible_en_2023",
              (pl.col("anio") != ANIO_EVA) | pl.col("produccion_total_t").is_not_null(),
              "alertar", "Municipios de 2023 sin producción reportada"),
    ]
    df = validar(df, reglas, "gold", "municipio_anio")
    verificar_cardinalidad(df, ["codigo_municipio"], N_MUNICIPIOS, "gold", "municipio_anio", grupo="anio")

    df = cumplir(df, "gold/municipio_anio").sort(["codigo_municipio", "anio"])
    df.write_parquet(GOLD / "municipio_anio.parquet")
    return df


def construir_maestro(municipio_anio: pl.DataFrame, municipios: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Formato ancho para mapas: variables de 2020 y de 2023 en la misma fila del municipio."""
    v2020 = (municipio_anio.filter(pl.col("anio") == ANIO_MDM)
             .select("codigo_municipio", "prop_18_44_pct", "prop_mujeres_18_44_pct", "prop_hombres_18_44_pct",
                     "pct_rural", "grupo_capacidad", "puntaje_mdm", "poblacion_total")
             .rename(lambda c: c if c == "codigo_municipio" else f"{c}_{ANIO_MDM}"))
    v2023 = (municipio_anio.filter(pl.col("anio") == ANIO_EVA)
             .select("codigo_municipio", "pob_18_64", "prop_18_64_pct", "produccion_total_t",
                     "produccion_papa_t", "rendimiento_papa_t_ha", "produccion_1k_18_64")
             .rename(lambda c: c if c == "codigo_municipio" else f"{c}_{ANIO_EVA}"))
    suelo = municipio_anio.select("codigo_municipio", "clase_predominante", "pct_sin_clasificar",
                                  "pct_clases_iii_iv").unique("codigo_municipio")
    ancho = v2020.join(v2023, on="codigo_municipio", how="full", coalesce=True) \
                 .join(suelo, on="codigo_municipio", how="left")

    gdf = municipios[["codigo_municipio", "municipio", "geometry"]].merge(
        ancho.to_pandas(), on="codigo_municipio", how="left")
    registrar("gold", "maestro", "municipios_con_geometria", len(ancho), len(ancho) - len(gdf), "alertar",
              "Municipios de la tabla analítica que tienen polígono")
    gdf.to_parquet(GOLD / "maestro_boyaca.geoparquet")
    return gdf
