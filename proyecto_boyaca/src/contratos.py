"""Contratos de datos: esquema de cada tabla silver y gold. Dueño: P6.

Cada productor llama `cumplir(df, "<tabla>")` justo antes de escribir su tabla.
Los consumidores pueden programar contra estos esquemas desde el día 1
usando los mocks de src/mocks.py.

Convenciones:
- codigo_municipio: texto de 5 dígitos ("15001"); siempre forma parte de la clave.
- snake_case y unidad en el nombre (_ha, _t, _km2, _pct).
- Faltante = null, nunca 0. Porcentajes entre 0 y 100.
"""
import polars as pl

S, I16, I64, F64 = pl.Utf8, pl.Int16, pl.Int64, pl.Float64

CONTRATOS: dict[str, dict] = {
    # ------------------------------------------------------------------ silver
    "silver/poblacion": {
        "clave": ["codigo_municipio", "anio"],
        "columnas": {"codigo_municipio": S, "municipio": S, "anio": I16, "poblacion_total": I64,
                     "hombres": I64, "mujeres": I64, "pob_18_44": I64, "pob_18_64": I64,
                     "hombres_18_44": I64, "mujeres_18_44": I64},
    },
    "silver/poblacion_area": {
        "clave": ["codigo_municipio", "anio", "area", "sexo", "edad"],
        "columnas": {"codigo_municipio": S, "anio": I16, "area": S, "sexo": S, "edad": I16,
                     "personas": I64},
    },
    "silver/desempeno": {
        "clave": ["codigo_municipio", "anio", "bloque"],
        "columnas": {"codigo_municipio": S, "municipio_fuente": S, "anio": I16, "bloque": S,
                     "es_bloque_oficial": pl.Boolean, "nombre_coherente": pl.Boolean,
                     "grupo_capacidad": S, "movilizacion_recursos": F64, "ejecucion_recursos": F64,
                     "gobierno_abierto": F64, "ordenamiento_territorial": F64, "gestion": F64,
                     "educacion": F64, "salud": F64, "servicios_publicos": F64,
                     "seguridad_convivencia": F64, "resultados": F64, "ajuste_resultados": F64,
                     "puntaje_mdm": F64},
    },
    "silver/agricola": {
        "clave": ["codigo_municipio", "codigo_cultivo", "periodo", "estado_fisico"],
        "columnas": {"codigo_municipio": S, "anio": I16, "periodo": S, "ciclo": S, "cultivo": S,
                     "codigo_cultivo": S, "desagregacion_cultivo": S, "grupo_cultivo": S,
                     "estado_fisico": S, "area_sembrada_ha": F64, "area_cosechada_ha": F64,
                     "produccion_t": F64, "rendimiento_fuente_t_ha": F64,
                     "alerta_cosechada_mayor": pl.Boolean, "alerta_produccion_sin_area": pl.Boolean},
    },
    # ------------------------------------------------------------------ gold
    "gold/cultivo_municipio": {
        "clave": ["codigo_municipio", "anio", "cultivo", "estado_fisico"],
        "columnas": {"codigo_municipio": S, "anio": I16, "cultivo": S, "estado_fisico": S,
                     "grupo_cultivo": S, "produccion_t": F64, "area_sembrada_ha": F64,
                     "area_cosechada_ha": F64, "rendimiento_t_ha": F64},
    },
    "gold/suelo_municipio": {
        "clave": ["codigo_municipio", "clase"],
        "columnas": {"codigo_municipio": S, "clase": S, "area_ha": F64, "pct_area": F64},
    },
    "gold/suelo_resumen": {
        "clave": ["codigo_municipio"],
        "columnas": {"codigo_municipio": S, "area_municipio_ha": F64, "area_clasificada_ha": F64,
                     "pct_sin_clasificar": F64, "clase_predominante": S, "pct_clase_predominante": F64,
                     "pct_clases_iii_iv": F64},
    },
    "gold/municipio_anio": {
        "clave": ["codigo_municipio", "anio"],
        "columnas": {"codigo_municipio": S, "municipio": S, "anio": I16, "poblacion_total": I64,
                     "pob_18_44": I64, "pob_18_64": I64, "hombres_18_44": I64, "mujeres_18_44": I64,
                     "prop_18_44_pct": F64, "prop_18_64_pct": F64, "prop_mujeres_18_44_pct": F64,
                     "prop_hombres_18_44_pct": F64, "pct_rural": F64, "grupo_capacidad": S,
                     "puntaje_mdm": F64, "produccion_total_t": F64, "produccion_papa_t": F64,
                     "area_cosechada_papa_ha": F64, "rendimiento_papa_t_ha": F64,
                     "produccion_1k_18_64": F64, "clase_predominante": S, "pct_sin_clasificar": F64,
                     "pct_clases_iii_iv": F64},
    },
}


class ContratoError(Exception):
    pass


def cumplir(df: pl.DataFrame, tabla: str) -> pl.DataFrame:
    """Ordena y castea las columnas al contrato; falla si falta alguna o la clave se repite."""
    c = CONTRATOS[tabla]
    faltan = [k for k in c["columnas"] if k not in df.columns]
    if faltan:
        raise ContratoError(f"{tabla}: faltan columnas {faltan}")
    df = df.select([pl.col(k).cast(t) for k, t in c["columnas"].items()])
    dup = df.select(pl.struct(c["clave"]).is_duplicated().sum()).item()
    if dup:
        raise ContratoError(f"{tabla}: {dup} filas con clave repetida {c['clave']}")
    return df


def esquema(tabla: str) -> dict:
    return CONTRATOS[tabla]["columnas"]
