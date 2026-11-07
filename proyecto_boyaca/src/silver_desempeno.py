"""Bronze -> silver del Desempeño Municipal (MDM). Dueño: P1.

Problemas conocidos del archivo (documentados en docs/informe_final.md):
1. 246 filas = dos bloques de 123 municipios con valores distintos, ambos rotulados 2020.
   Bloque A = filas 1-123, bloque B = filas 124-246. Se conservan los dos y se marca
   cuál es el oficial (config.MDM_BLOQUE_OFICIAL). El otro se usa en la sensibilidad.
2. En el bloque A los códigos 15022 y 15047 tienen los nombres cruzados (Aquitania/Almeida).
   Por eso se valida que el nombre sea coherente con el código DANE, comparando sin tildes.
3. Algunos nombres difieren solo en tildes o en el nombre largo ("Guicán" vs "Güicán de La Sierra").
"""
import polars as pl

from src.calidad import (Regla, clave_unica, codigo_divipola, diagnosticar, entre, normalizar_texto,
                         registrar, validar, verificar_cardinalidad)
from src.config import ANIO_MDM, MDM_BLOQUE_OFICIAL, N_MUNICIPIOS, QUALITY, SILVER, bronze_csv
from src.contratos import cumplir

RENOMBRAR = {
    "Código DANE": "codigo_municipio", "Municipio": "municipio_fuente", "Grupo": "grupo_capacidad",
    "Movilización de recursos": "movilizacion_recursos", "Ejecución de recursos": "ejecucion_recursos",
    "Gobierno abierto": "gobierno_abierto",
    "Ordenamiento erritorial": "ordenamiento_territorial",   # así viene (sin la "t") en la fuente
    "Gestión 2020": "gestion", "Educación": "educacion", "Salud": "salud",
    "Servicios públicos": "servicios_publicos", "Seguridad y convivencia": "seguridad_convivencia",
    "Resultados 2020": "resultados", "Ajuste por resultados": "ajuste_resultados",
    "MDM 2020": "puntaje_mdm",
}
PUNTAJES_0_100 = ["movilizacion_recursos", "ejecucion_recursos", "gobierno_abierto",
                  "ordenamiento_territorial", "gestion", "educacion", "salud", "servicios_publicos",
                  "seguridad_convivencia", "resultados", "puntaje_mdm"]


def _coherente(nombre_fuente: str | None, nombre_dane: str | None) -> bool:
    a, b = normalizar_texto(nombre_fuente), normalizar_texto(nombre_dane)
    if a is None or b is None:
        return False
    return a == b or b.startswith(a) or a.startswith(b)


def construir_desempeno(poblacion: pl.DataFrame, ruta=None) -> pl.DataFrame:
    """`poblacion` (silver) aporta los nombres oficiales DANE para validar los códigos."""
    ruta = ruta or bronze_csv("desempeno_municipal")
    crudo = pl.read_csv(ruta, infer_schema_length=0)
    diagnosticar(crudo, "bronze", "desempeno_municipal")
    faltan = [c for c in RENOMBRAR if c not in crudo.columns]
    if faltan:
        raise ValueError(f"El archivo MDM cambió: faltan columnas {faltan}")

    n_bloque = crudo.height // 2
    registrar("bronze", "desempeno_municipal", "dos_bloques_misma_vigencia", crudo.height,
              crudo.height - N_MUNICIPIOS, "alertar",
              f"{crudo.height} filas para {N_MUNICIPIOS} municipios: dos bloques rotulados 2020")

    df = (crudo.rename(RENOMBRAR)
               .with_row_index("fila")
               .with_columns(
                   pl.col("codigo_municipio").str.strip_chars().str.zfill(5),
                   pl.col("municipio_fuente").str.strip_chars(),
                   pl.col("grupo_capacidad").str.strip_chars(),
                   *[pl.col(c).str.replace(",", ".").cast(pl.Float64, strict=False)
                     for c in PUNTAJES_0_100 + ["ajuste_resultados"]],
                   anio=pl.lit(ANIO_MDM, dtype=pl.Int16),
                   bloque=pl.when(pl.col("fila") < n_bloque).then(pl.lit("A")).otherwise(pl.lit("B")),
               ))

    nombres = poblacion.select("codigo_municipio", "municipio").unique("codigo_municipio")
    df = df.join(nombres.rename({"municipio": "municipio_dane"}), on="codigo_municipio", how="left")
    df = df.with_columns(
        nombre_coherente=pl.struct(["municipio_fuente", "municipio_dane"]).map_elements(
            lambda r: _coherente(r["municipio_fuente"], r["municipio_dane"]), return_dtype=pl.Boolean),
        es_bloque_oficial=pl.col("bloque") == MDM_BLOQUE_OFICIAL,
    )

    # Evidencia de los nombres incoherentes, para el informe
    df.filter(~pl.col("nombre_coherente")).select(
        "bloque", "fila", "codigo_municipio", "municipio_fuente", "municipio_dane", "puntaje_mdm"
    ).write_csv(QUALITY / "desempeno_nombres_incoherentes.csv")

    reglas = [
        Regla("codigo_divipola_valido", codigo_divipola(), "rechazar", "Código de 5 dígitos que inicia en 15"),
        Regla("codigo_existe_en_dane", pl.col("municipio_dane").is_not_null(), "rechazar",
              "El código existe en la población DANE"),
        Regla("puntaje_mdm_no_nulo", pl.col("puntaje_mdm").is_not_null(), "rechazar", "Puntaje numérico"),
        Regla("puntajes_0_100", pl.all_horizontal([entre(c, 0, 100) for c in PUNTAJES_0_100]),
              "rechazar", "Puntajes y componentes entre 0 y 100"),
        Regla("grupo_capacidad_valido", pl.col("grupo_capacidad").str.contains(r"^(C|G[1-6])$"), "alertar",
              "Grupo de capacidades iniciales C o G1-G6"),
        # Se alerta en ambos bloques; en el bloque oficial además se rechaza (regla siguiente).
        Regla("nombre_coherente_con_codigo", pl.col("nombre_coherente"), "alertar",
              "El nombre del municipio corresponde al código DANE (sin tildes)"),
        Regla("oficial_con_nombre_coherente", ~pl.col("es_bloque_oficial") | pl.col("nombre_coherente"),
              "rechazar", "En el bloque oficial no se aceptan códigos con nombre de otro municipio"),
        Regla("clave_unica", clave_unica(["codigo_municipio", "anio", "bloque"]), "detener",
              "Una fila por municipio, año y bloque"),
    ]
    df = validar(df, reglas, "silver", "desempeno")
    verificar_cardinalidad(df.filter(pl.col("es_bloque_oficial")), ["codigo_municipio"], N_MUNICIPIOS,
                           "silver", "desempeno_oficial")

    # Cuánto difieren los dos bloques (evidencia para la sensibilidad y la sustentación)
    comp = (df.filter(pl.col("bloque") == "A").select("codigo_municipio", mdm_a="puntaje_mdm")
              .join(df.filter(pl.col("bloque") == "B").select("codigo_municipio", mdm_b="puntaje_mdm"),
                    on="codigo_municipio", how="full", coalesce=True)
              .with_columns(diferencia=pl.col("mdm_b") - pl.col("mdm_a")))
    comp.write_csv(QUALITY / "desempeno_comparacion_bloques.csv")

    df = cumplir(df, "silver/desempeno").sort(["bloque", "codigo_municipio"])
    diagnosticar(df, "silver", "desempeno")
    df.write_parquet(SILVER / "desempeno.parquet")
    return df
