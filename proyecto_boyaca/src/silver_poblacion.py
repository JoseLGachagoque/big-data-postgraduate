"""Bronze -> silver de población. Dueño: P1.

Dos tablas:
- silver/poblacion.parquet       municipio-año, desde poblacion_dane (fuente municipal OFICIAL).
- silver/poblacion_area.parquet  municipio-año-área-sexo-edad, desde el archivo de "centros poblados".

Por qué dos fuentes: el archivo de "centros poblados" no son centros poblados.
Son proyecciones DANE por ÁREA (Cabecera, Centros poblados y rural disperso, Total)
por edad simple y sexo. Sirve para la pirámide y para el % rural, pero:
- Cabecera + Rural = Total. Sumar las tres filas DUPLICA la población.
- Su "Total" no coincide exactamente con poblacion_dane (otra versión de la proyección),
  por eso la población municipal oficial es poblacion_dane y la diferencia se reporta.
"""
import polars as pl

from src.calidad import (Regla, clave_unica, codigo_divipola, diagnosticar, entre, no_negativo,
                         registrar, validar, verificar_cardinalidad)
from src.config import N_MUNICIPIOS, QUALITY, SILVER, bronze_csv
from src.contratos import cumplir

CONTEOS = ["poblacion_total", "hombres", "mujeres", "pob_18_44", "pob_18_64",
           "hombres_18_44", "mujeres_18_44"]

AREAS = {"Cabecera Municipal": "cabecera", "Centros Poblados y Rural Disperso": "rural",
         "Total": "total"}


# ------------------------------------------------------------------ poblacion municipal

def construir_poblacion(ruta=None) -> pl.DataFrame:
    ruta = ruta or bronze_csv("poblacion_dane")
    crudo = pl.read_csv(ruta, infer_schema_length=0)          # bronze: todo como texto
    diagnosticar(crudo, "bronze", "poblacion_dane")

    df = crudo.with_columns(
        pl.col("codigo_municipio").str.strip_chars().str.zfill(5),
        pl.col("municipio").str.strip_chars(),
        pl.col("anio").cast(pl.Int16, strict=False),
        *[pl.col(c).cast(pl.Int64, strict=False) for c in CONTEOS],
    )

    reglas = [
        Regla("codigo_divipola_valido", codigo_divipola(), "rechazar",
              "Código de 5 dígitos que inicia en 15"),
        Regla("anio_en_rango", entre("anio", 2020, 2025, nulos_validos=False), "rechazar",
              "Año entre 2020 y 2025"),
        Regla("conteos_no_nulos", pl.all_horizontal([pl.col(c).is_not_null() for c in CONTEOS]),
              "rechazar", "Ningún conteo vacío o no numérico"),
        Regla("conteos_no_negativos", pl.all_horizontal([no_negativo(c) for c in CONTEOS]),
              "rechazar", "Conteos >= 0"),
        Regla("total_positivo", pl.col("poblacion_total") > 0, "rechazar", "Población total > 0"),
        Regla("sexo_suma_total", pl.col("hombres") + pl.col("mujeres") == pl.col("poblacion_total"),
              "alertar", "hombres + mujeres = total"),
        Regla("grupos_anidados",
              (pl.col("pob_18_44") <= pl.col("pob_18_64")) & (pl.col("pob_18_64") <= pl.col("poblacion_total")),
              "rechazar", "18-44 <= 18-64 <= total"),
        Regla("sexo_18_44_suma", pl.col("hombres_18_44") + pl.col("mujeres_18_44") == pl.col("pob_18_44"),
              "alertar", "hombres 18-44 + mujeres 18-44 = 18-44"),
        Regla("clave_unica", clave_unica(["codigo_municipio", "anio"]), "detener",
              "Una fila por municipio y año"),
    ]
    df = validar(df, reglas, "silver", "poblacion")
    verificar_cardinalidad(df, ["codigo_municipio"], N_MUNICIPIOS, "silver", "poblacion", grupo="anio")

    df = cumplir(df, "silver/poblacion").sort(["codigo_municipio", "anio"])
    diagnosticar(df, "silver", "poblacion")
    df.write_parquet(SILVER / "poblacion.parquet")
    return df


# ------------------------------------------------------------------ poblacion por area

def construir_poblacion_area(ruta=None, poblacion: pl.DataFrame | None = None) -> pl.DataFrame:
    ruta = ruta or bronze_csv("centros_poblados")
    crudo = pl.read_csv(ruta, infer_schema_length=0)
    diagnosticar(crudo, "bronze", "centros_poblados")

    df = crudo.rename({"CÓDIGO DANE MUNICIPIO": "codigo_municipio", "AÑO": "anio",
                       "ÁREA GEOGRÁFICA": "area_fuente"}).with_columns(
        pl.col("codigo_municipio").str.strip_chars().str.zfill(5),
        pl.col("anio").cast(pl.Int16, strict=False),
        area=pl.col("area_fuente").replace_strict(AREAS, default=None),
    )

    reglas = [
        Regla("codigo_divipola_valido", codigo_divipola(), "rechazar", "Código de 5 dígitos que inicia en 15"),
        Regla("area_conocida", pl.col("area").is_not_null(), "rechazar",
              "Área en {Cabecera, Centros poblados y rural disperso, Total}"),
        Regla("clave_unica", clave_unica(["codigo_municipio", "anio", "area"]), "detener",
              "Una fila por municipio, año y área"),
    ]
    df = validar(df, reglas, "silver", "centros_poblados")

    # --- conciliación 1: cabecera + rural = total (dentro de la misma fuente)
    tot = df.with_columns(pl.col("Total").cast(pl.Int64, strict=False))
    piv = (tot.group_by(["codigo_municipio", "anio"])
              .agg(suma_areas=pl.col("Total").filter(pl.col("area") != "total").sum(),
                   total_fuente=pl.col("Total").filter(pl.col("area") == "total").sum()))
    dif = piv.filter(pl.col("suma_areas") != pl.col("total_fuente")).height
    registrar("silver", "centros_poblados", "cabecera_mas_rural_igual_total", piv.height, dif, "alertar",
              "Cabecera + Rural debe igualar la fila Total: por eso NO se suman las tres")

    # --- conciliación 2: total de esta fuente vs poblacion_dane (fuente oficial)
    if poblacion is not None:
        comp = (piv.join(poblacion.select("codigo_municipio", "anio", "poblacion_total"),
                         on=["codigo_municipio", "anio"], how="inner")
                   .with_columns(diferencia=pl.col("total_fuente") - pl.col("poblacion_total"),
                                 diferencia_pct=(pl.col("total_fuente") - pl.col("poblacion_total"))
                                 / pl.col("poblacion_total") * 100))
        comp.sort(["anio", "codigo_municipio"]).write_csv(QUALITY / "conciliacion_poblacion_fuentes.csv")
        registrar("silver", "centros_poblados", "total_vs_poblacion_dane", comp.height,
                  comp.filter(pl.col("diferencia") != 0).height, "alertar",
                  "Diferencias entre versiones de la proyección; se usa poblacion_dane como oficial")

    # --- formato largo: solo cabecera y rural (la fila total se descarta para no duplicar)
    cols_edad = [c for c in df.columns if c.startswith(("Hombres_", "Mujeres_"))]
    largo = (df.filter(pl.col("area") != "total")
               .select(["codigo_municipio", "anio", "area", *cols_edad])
               .unpivot(index=["codigo_municipio", "anio", "area"], on=cols_edad,
                        variable_name="variable", value_name="personas")
               .with_columns(
                   sexo=pl.when(pl.col("variable").str.starts_with("Hombres")).then(pl.lit("H")).otherwise(pl.lit("M")),
                   edad=pl.col("variable").str.split("_").list.last().cast(pl.Int16),   # 85 = 85 y más
                   personas=pl.col("personas").cast(pl.Int64, strict=False))
               .drop("variable"))

    reglas_largo = [
        Regla("personas_no_nulas", pl.col("personas").is_not_null(), "rechazar", "Conteo numérico"),
        Regla("personas_no_negativas", no_negativo("personas"), "rechazar", "Conteo >= 0"),
        Regla("edad_en_rango", entre("edad", 0, 85, nulos_validos=False), "rechazar", "Edad 0-85 (85 = 85+)"),
    ]
    largo = validar(largo, reglas_largo, "silver", "poblacion_area")
    verificar_cardinalidad(largo, ["codigo_municipio"], N_MUNICIPIOS, "silver", "poblacion_area", grupo="anio")

    largo = cumplir(largo, "silver/poblacion_area").sort(["codigo_municipio", "anio", "area", "sexo", "edad"])
    diagnosticar(largo, "silver", "poblacion_area")
    largo.write_parquet(SILVER / "poblacion_area.parquet")
    return largo


def pct_rural(poblacion_area: pl.DataFrame) -> pl.DataFrame:
    """% de la población que vive en centros poblados y rural disperso, por municipio y año."""
    return (poblacion_area.group_by(["codigo_municipio", "anio"])
            .agg(rural=pl.col("personas").filter(pl.col("area") == "rural").sum(),
                 total=pl.col("personas").sum())
            .with_columns(pct_rural=pl.when(pl.col("total") > 0)
                          .then(pl.col("rural") / pl.col("total") * 100))
            .select("codigo_municipio", "anio", "pct_rural"))


def prop_18_44_desde_areas(poblacion_area: pl.DataFrame) -> pl.DataFrame:
    """Proporción 18-44 calculada con la fuente alterna (para el análisis de sensibilidad)."""
    return (poblacion_area.group_by(["codigo_municipio", "anio"])
            .agg(p=pl.col("personas").filter(pl.col("edad").is_between(18, 44)).sum(),
                 t=pl.col("personas").sum())
            .with_columns(prop_18_44_alt_pct=pl.col("p") / pl.col("t") * 100)
            .select("codigo_municipio", "anio", "prop_18_44_alt_pct"))
