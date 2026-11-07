"""Framework de calidad común a todas las capas. Dueño: P6.

Todas las fuentes usan las mismas tres piezas:

- `diagnosticar(df, capa, fuente)`: perfil por columna (tipo, nulos, únicos).
  Se llama en bronze (antes de limpiar) y en silver (después) para el diagnóstico
  "antes y después" que pide el enunciado (sección 7.2).
- `validar(df, reglas, capa, fuente)`: aplica reglas, devuelve los registros
  válidos, manda los rechazados a data_lake/rejects/ y registra una fila de
  métricas por regla en outputs/quality/metricas_<capa>.csv.
- `registrar(...)`: para métricas que no son una regla fila a fila
  (cardinalidad, conciliaciones, geometrías inválidas, uniones).

Acciones posibles de una regla:
- "rechazar": la fila que falla sale del dataset y va a rejects.
- "alertar":  la fila se conserva; solo se cuenta y se reporta.
- "detener":  si falla al menos una fila, el pipeline se detiene (ValidacionError).

Los datos de entrada nunca se modifican para pasar una regla.
"""
from __future__ import annotations

import csv
import unicodedata
from dataclasses import dataclass
from datetime import datetime

import polars as pl

from src.config import QUALITY, REJECTS

COLUMNAS_METRICAS = ["fecha_ejecucion", "capa", "fuente", "regla", "descripcion",
                     "revisados", "afectados", "resultado", "accion"]


class ValidacionError(Exception):
    """Una regla con accion='detener' falló."""


@dataclass
class Regla:
    nombre: str
    expr: pl.Expr            # True = la fila CUMPLE la regla
    accion: str = "rechazar"  # rechazar | alertar | detener
    descripcion: str = ""


# ---------------------------------------------------------------- métricas

def _ruta_metricas(capa: str):
    QUALITY.mkdir(parents=True, exist_ok=True)
    return QUALITY / f"metricas_{capa}.csv"


def reiniciar_metricas() -> None:
    """Borra las métricas de la corrida anterior. Se llama al inicio del pipeline (notebook 01)."""
    QUALITY.mkdir(parents=True, exist_ok=True)
    for p in QUALITY.glob("metricas_*.csv"):
        p.unlink()


def registrar(capa: str, fuente: str, regla: str, revisados: int, afectados: int,
              accion: str = "alertar", descripcion: str = "") -> None:
    """Agrega una fila al archivo de métricas de la capa."""
    ruta = _ruta_metricas(capa)
    nueva = not ruta.exists()
    with open(ruta, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if nueva:
            w.writerow(COLUMNAS_METRICAS)
        w.writerow([datetime.now().isoformat(timespec="seconds"), capa, fuente, regla, descripcion,
                    int(revisados), int(afectados), "OK" if afectados == 0 else "FALLA", accion])


# ---------------------------------------------------------------- diagnóstico

def diagnosticar(df: pl.DataFrame, capa: str, fuente: str) -> pl.DataFrame:
    """Perfil por columna. Guarda outputs/quality/diagnostico_<capa>_<fuente>.csv y lo devuelve."""
    filas = df.height
    perfil = pl.DataFrame({
        "columna": df.columns,
        "tipo": [str(t) for t in df.dtypes],
        "nulos": [df[c].null_count() for c in df.columns],
        "pct_nulos": [round(100 * df[c].null_count() / filas, 2) if filas else 0.0 for c in df.columns],
        "valores_unicos": [df[c].n_unique() for c in df.columns],
    })
    QUALITY.mkdir(parents=True, exist_ok=True)
    perfil.write_csv(QUALITY / f"diagnostico_{capa}_{fuente}.csv")
    registrar(capa, fuente, "filas_duplicadas_exactas", filas, int(df.is_duplicated().sum()),
              "alertar", "Filas idénticas en todas las columnas")
    return perfil


# ---------------------------------------------------------------- validación

def validar(df: pl.DataFrame, reglas: list[Regla], capa: str, fuente: str) -> pl.DataFrame:
    """Aplica las reglas en orden. Devuelve solo los registros válidos."""
    if df.height == 0:
        raise ValidacionError(f"[{capa}/{fuente}] el dataset llegó vacío")

    banderas = [(~r.expr.fill_null(False)).alias(f"__falla_{i}") for i, r in enumerate(reglas)]
    tmp = df.with_columns(banderas)

    rechazo = pl.lit(False)
    motivos = []
    for i, r in enumerate(reglas):
        col = f"__falla_{i}"
        afectados = int(tmp[col].sum())
        registrar(capa, fuente, r.nombre, df.height, afectados, r.accion, r.descripcion)
        if r.accion == "detener" and afectados:
            raise ValidacionError(f"[{capa}/{fuente}] regla '{r.nombre}' falló en {afectados} filas: "
                                  f"{r.descripcion}")
        if r.accion == "rechazar":
            rechazo = rechazo | pl.col(col)
            motivos.append(pl.when(pl.col(col)).then(pl.lit(r.nombre)))

    tmp = tmp.with_columns(__rechazo=rechazo)
    malos = tmp.filter(pl.col("__rechazo"))
    if malos.height:
        REJECTS.mkdir(parents=True, exist_ok=True)
        malos = malos.with_columns(
            motivo_rechazo=pl.concat_str(motivos, separator="; ", ignore_nulls=True) if motivos else pl.lit(""),
            capa=pl.lit(capa),
        )
        malos.select([c for c in malos.columns if not c.startswith("__")]) \
             .write_parquet(REJECTS / f"{capa}_{fuente}.parquet")

    buenos = tmp.filter(~pl.col("__rechazo")).select(df.columns)
    print(f"[{capa}/{fuente}] revisados={df.height} validos={buenos.height} rechazados={malos.height}")
    return buenos


def verificar_cardinalidad(df: pl.DataFrame, clave: list[str], esperado: int, capa: str, fuente: str,
                           grupo: str | None = None) -> None:
    """Cuenta municipios distintos (por grupo, p. ej. por año) frente a lo esperado (123)."""
    if grupo is None:
        n = df.select(pl.struct(clave).n_unique()).item()
        registrar(capa, fuente, "cardinalidad", esperado, abs(esperado - n), "alertar",
                  f"Se esperaban {esperado} claves distintas; hay {n}")
        return
    for g, sub in df.group_by(grupo):
        n = sub.select(pl.struct(clave).n_unique()).item()
        registrar(capa, fuente, f"cardinalidad_{grupo}_{g[0]}", esperado, abs(esperado - n), "alertar",
                  f"{grupo}={g[0]}: se esperaban {esperado} municipios; hay {n}")


# ---------------------------------------------------------------- utilidades de reglas

def clave_unica(cols: list[str]) -> pl.Expr:
    """True en la primera aparición de cada clave; las repeticiones fallan."""
    return pl.struct(cols).is_first_distinct()


def entre(col: str, minimo: float, maximo: float, nulos_validos: bool = True) -> pl.Expr:
    e = pl.col(col).is_between(minimo, maximo)
    return (pl.col(col).is_null() | e) if nulos_validos else e


def no_negativo(col: str, nulos_validos: bool = True) -> pl.Expr:
    e = pl.col(col) >= 0
    return (pl.col(col).is_null() | e) if nulos_validos else e


def codigo_divipola(col: str = "codigo_municipio") -> pl.Expr:
    """Texto de 5 dígitos que empieza por el código del departamento (15)."""
    return pl.col(col).str.contains(r"^15\d{3}$")


def normalizar_texto(s: str | None) -> str | None:
    """minúsculas, sin tildes ni diéresis, espacios simples: para comparar nombres."""
    if s is None:
        return None
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return " ".join(s.lower().split())


def a_snake(nombre: str) -> str:
    """'Área cosechada (ha)' -> 'area_cosechada_ha'."""
    s = normalizar_texto(nombre) or ""
    for ch in "()/.,-":
        s = s.replace(ch, " ")
    return "_".join(s.split())
