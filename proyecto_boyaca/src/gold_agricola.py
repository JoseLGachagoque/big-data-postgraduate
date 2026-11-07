"""Silver -> gold agrícola. Dueño: P2.

- gold/cultivo_municipio.parquet: producción, áreas y rendimiento por municipio y cultivo
  (suma de los periodos A y B del año).
- `resumen_municipal()`: totales por municipio para la tabla municipio_anio (P6 la integra).

Regla del enunciado (sección 6): el rendimiento agregado es SUMA de producción / SUMA de área
cosechada, nunca el promedio de rendimientos. Si el área es 0, el rendimiento es null.
"""
import polars as pl

from src.calidad import Regla, registrar, validar
from src.config import CULTIVO_SELECCIONADO, GOLD
from src.contratos import cumplir


def rendimiento(prod: str = "produccion_t", area: str = "area_cosechada_ha") -> pl.Expr:
    return pl.when(pl.col(area) > 0).then(pl.col(prod) / pl.col(area)).otherwise(None)


def construir_cultivo_municipio(agricola: pl.DataFrame) -> pl.DataFrame:
    df = (agricola.group_by(["codigo_municipio", "anio", "cultivo", "estado_fisico"])
                  .agg(pl.col("grupo_cultivo").first(),
                       pl.col("produccion_t").sum(),
                       pl.col("area_sembrada_ha").sum(),
                       pl.col("area_cosechada_ha").sum())
                  .with_columns(rendimiento_t_ha=rendimiento()))

    sin_area = df.filter(pl.col("area_cosechada_ha") == 0).height
    registrar("gold", "cultivo_municipio", "rendimiento_division_por_cero", df.height, sin_area, "alertar",
              "Cultivos con área cosechada 0: rendimiento = null (no se divide entre cero)")

    reglas = [
        Regla("rendimiento_finito", pl.col("rendimiento_t_ha").is_null() | pl.col("rendimiento_t_ha").is_finite(),
              "detener", "Sin infinitos ni NaN"),
        Regla("rendimiento_no_negativo", pl.col("rendimiento_t_ha").is_null() | (pl.col("rendimiento_t_ha") >= 0),
              "detener", "Rendimiento >= 0"),
    ]
    df = validar(df, reglas, "gold", "cultivo_municipio")

    # conciliación con silver: la suma total de producción no puede cambiar al agregar
    dif = abs(df["produccion_t"].sum() - agricola["produccion_t"].sum())
    registrar("gold", "cultivo_municipio", "conciliacion_produccion_silver", agricola.height,
              int(dif > 1e-6), "detener" if dif > 1e-6 else "alertar",
              f"Producción total gold - silver = {dif:.6f} t")

    df = cumplir(df, "gold/cultivo_municipio").sort(["codigo_municipio", "cultivo"])
    df.write_parquet(GOLD / "cultivo_municipio.parquet")
    return df


def resumen_municipal(cultivo_municipio: pl.DataFrame) -> pl.DataFrame:
    """Una fila por municipio y año con los totales que usa municipio_anio.

    produccion_total_t suma toneladas de cultivos con estados físicos distintos: el enunciado lo
    pide como indicador, pero NO representa valor económico ni es comparable entre cultivos.
    """
    papa = pl.col("cultivo") == CULTIVO_SELECCIONADO
    return (cultivo_municipio.group_by(["codigo_municipio", "anio"])
            .agg(produccion_total_t=pl.col("produccion_t").sum(),
                 produccion_papa_t=pl.col("produccion_t").filter(papa).sum(),
                 area_cosechada_papa_ha=pl.col("area_cosechada_ha").filter(papa).sum(),
                 tiene_papa=papa.any())
            .with_columns(
                # sin registro de papa = null (faltante), no 0
                produccion_papa_t=pl.when(pl.col("tiene_papa")).then(pl.col("produccion_papa_t")),
                area_cosechada_papa_ha=pl.when(pl.col("tiene_papa")).then(pl.col("area_cosechada_papa_ha")))
            .with_columns(rendimiento_papa_t_ha=rendimiento("produccion_papa_t", "area_cosechada_papa_ha"))
            .drop("tiene_papa"))


def resumen_departamental_por_cultivo(cultivo_municipio: pl.DataFrame) -> pl.DataFrame:
    """Para la gráfica de producción y rendimiento por cultivo (todo Boyacá)."""
    return (cultivo_municipio.group_by(["cultivo", "estado_fisico"])
            .agg(pl.col("produccion_t").sum(), pl.col("area_cosechada_ha").sum(),
                 municipios=pl.col("codigo_municipio").n_unique())
            .with_columns(rendimiento_t_ha=rendimiento())
            .sort("produccion_t", descending=True))
