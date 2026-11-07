"""Bronze -> silver de las Evaluaciones Agropecuarias Municipales (EVA). Dueño: P2.

Características del archivo:
- Solo vigencia 2023. Cultivos transitorios en 2023A y 2023B; permanentes en "2023" (anual).
- 96 cultivos y 6 estados físicos (en fresco, grano seco, grano, caña, pergamino, fibra).
  Por eso las toneladas de cultivos distintos NO son comparables entre sí.
- Hay filas con área cosechada mayor que la sembrada: se marcan, no se borran.
"""
import polars as pl

from src.calidad import (Regla, clave_unica, codigo_divipola, diagnosticar, entre, no_negativo,
                         registrar, validar, verificar_cardinalidad)
from src.config import COD_DEPARTAMENTO, N_MUNICIPIOS, SILVER, bronze_csv
from src.contratos import cumplir

RENOMBRAR = {
    "Ciclo del cultivo": "ciclo", "Municipio": "municipio", "Cultivo": "cultivo", "Periodo": "periodo",
    "Área sembrada (ha)": "area_sembrada_ha", "Área cosechada (ha)": "area_cosechada_ha",
    "Producción (t)": "produccion_t", "Rendimiento (t/ha)": "rendimiento_fuente_t_ha",
    "Código Dane departamento": "codigo_departamento", "Código Dane municipio": "codigo_municipio",
    "Provincia": "provincia", "Desagregación cultivo": "desagregacion_cultivo",
    "Grupo cultivo": "grupo_cultivo", "Subgrupo": "subgrupo", "Código del cultivo": "codigo_cultivo",
    "Estado físico del cultivo": "estado_fisico", "Nombre científico del cultivo": "nombre_cientifico",
}
NUMERICAS = ["area_sembrada_ha", "area_cosechada_ha", "produccion_t", "rendimiento_fuente_t_ha"]


def _numero(col: str) -> pl.Expr:
    """Acepta '1234.5' y '1.234,5'; lo que no sea número queda null (y se cuenta)."""
    s = pl.col(col).str.strip_chars()
    s = pl.when(s.str.contains(r",\d+$")).then(s.str.replace_all(r"\.", "").str.replace(",", ".")).otherwise(s)
    return s.cast(pl.Float64, strict=False).alias(col)


def construir_agricola(ruta=None) -> pl.DataFrame:
    ruta = ruta or bronze_csv("evaluaciones_agropecuarias")
    crudo = pl.read_csv(ruta, infer_schema_length=0)
    diagnosticar(crudo, "bronze", "evaluaciones_agropecuarias")

    faltan = [c for c in RENOMBRAR if c not in crudo.columns]
    if faltan:
        raise ValueError(f"La EVA cambió: faltan columnas {faltan}")
    extra = [c for c in crudo.columns if c not in RENOMBRAR]   # Cultivo2, Periodo2, Departamento...
    df = crudo.rename(RENOMBRAR).drop(extra)

    # valores no numéricos ANTES de convertir (para no confundir "texto raro" con "vacío")
    for c in NUMERICAS:
        no_num = df.filter(pl.col(c).is_not_null() & _numero(c).is_null()).height
        registrar("silver", "agricola", f"{c}_no_numerico", df.height, no_num, "alertar",
                  f"Valores de {c} que no se pudieron leer como número")

    df = df.with_columns(
        pl.col("codigo_municipio").str.strip_chars().str.zfill(5),
        pl.col("codigo_departamento").str.strip_chars(),
        pl.col("periodo").str.strip_chars(),
        pl.col("cultivo").str.strip_chars(),
        pl.col("estado_fisico").str.strip_chars(),
        *[_numero(c) for c in NUMERICAS],
    ).with_columns(
        anio=pl.col("periodo").str.slice(0, 4).cast(pl.Int16, strict=False),
        alerta_cosechada_mayor=pl.col("area_cosechada_ha") > pl.col("area_sembrada_ha"),
        alerta_produccion_sin_area=(pl.col("produccion_t") > 0) & (pl.col("area_cosechada_ha") == 0),
    )

    reglas = [
        Regla("departamento_boyaca", pl.col("codigo_departamento") == COD_DEPARTAMENTO, "rechazar",
              "Solo filas de Boyacá (15)"),
        Regla("codigo_divipola_valido", codigo_divipola(), "rechazar", "Código de 5 dígitos que inicia en 15"),
        Regla("periodo_valido", pl.col("periodo").str.contains(r"^\d{4}[AB]?$"), "rechazar",
              "Periodo AAAA, AAAAA o AAAAB"),
        Regla("cultivo_informado", pl.col("cultivo").is_not_null() & pl.col("codigo_cultivo").is_not_null(),
              "rechazar", "Cultivo y código de cultivo presentes"),
        Regla("produccion_y_area_informadas",
              pl.col("produccion_t").is_not_null() & pl.col("area_cosechada_ha").is_not_null(), "rechazar",
              "Producción y área cosechada numéricas (faltante no es cero)"),
        Regla("valores_no_negativos", pl.all_horizontal([no_negativo(c) for c in NUMERICAS]), "rechazar",
              "Áreas, producción y rendimiento >= 0"),
        Regla("cosechada_no_mayor_sembrada", ~pl.col("alerta_cosechada_mayor").fill_null(False), "alertar",
              "Área cosechada <= sembrada (en permanentes puede cosecharse área sembrada en años previos)"),
        Regla("produccion_con_area", ~pl.col("alerta_produccion_sin_area").fill_null(False), "alertar",
              "Si hay producción, hay área cosechada"),
        Regla("rendimiento_fuente_razonable", entre("rendimiento_fuente_t_ha", 0, 500), "alertar",
              "Rendimiento reportado entre 0 y 500 t/ha (revisar extremos, no se eliminan)"),
        Regla("clave_unica", clave_unica(["codigo_municipio", "codigo_cultivo", "periodo", "estado_fisico"]),
              "rechazar", "Una fila por municipio, cultivo, periodo y estado físico; repetidas -> rejects"),
    ]
    df = validar(df, reglas, "silver", "agricola")
    verificar_cardinalidad(df, ["codigo_municipio"], N_MUNICIPIOS, "silver", "agricola")

    df = cumplir(df, "silver/agricola").sort(["codigo_municipio", "cultivo", "periodo"])
    diagnosticar(df, "silver", "agricola")
    df.write_parquet(SILVER / "agricola.parquet")
    return df
