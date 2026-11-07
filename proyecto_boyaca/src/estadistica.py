"""Librería estadística del proyecto. Dueño: P5.

P5 escribe las funciones y la hipótesis principal; P2 y P4 las usan para sus hipótesis
complementarias. Todas reciben pandas.DataFrame (statsmodels trabaja con pandas).

Plan de análisis fijado ANTES de ver los datos reales (no se cambia según el resultado):
- alfa = 0,05 (config.ALFA). Hipótesis principal unilateral (asociación positiva).
- Pearson y Spearman, cada uno con IC 95 % (transformación z de Fisher) y valor p.
  Spearman es la medida principal si Shapiro-Wilk rechaza normalidad o hay influyentes.
- Regresión simple y regresión con controles; Breusch-Pagan -> errores HC3 si hay
  heterocedasticidad; distancia de Cook (> 4/n) para influyentes; VIF para colinealidad.
- Sensibilidad: sin influyentes, bloque alterno del MDM, proporción con la fuente alterna.
- Complementarias = exploratorias, con valor p ajustado por Holm.
"""
from __future__ import annotations

import json
import re

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats
from statsmodels.stats.diagnostic import het_breuschpagan
from statsmodels.stats.multitest import multipletests
from statsmodels.stats.outliers_influence import variance_inflation_factor

from src.config import ALFA, STATS


# ------------------------------------------------------------------ correlaciones

def _ic_fisher(r: float, n: int, metodo: str, nivel: float = 0.95) -> tuple[float, float]:
    """IC por transformación z de Fisher. Para Spearman se usa el error de Bonett-Wright."""
    if n <= 3 or abs(r) >= 1:
        return (np.nan, np.nan)
    se = np.sqrt((1 + r ** 2 / 2) / (n - 3)) if metodo == "spearman" else 1 / np.sqrt(n - 3)
    z = np.arctanh(r)
    q = stats.norm.ppf(1 - (1 - nivel) / 2)
    return (float(np.tanh(z - q * se)), float(np.tanh(z + q * se)))


def correlacion(df: pd.DataFrame, x: str, y: str, metodo: str = "spearman",
                alternativa: str = "two-sided") -> dict:
    """alternativa: 'two-sided', 'greater' (asociación positiva) o 'less'."""
    d = df[[x, y]].dropna()
    n = len(d)
    if n < 5:
        return {"x": x, "y": y, "metodo": metodo, "n": n, "r": np.nan, "p": np.nan,
                "ic95_inf": np.nan, "ic95_sup": np.nan, "alternativa": alternativa,
                "nota": "datos insuficientes"}
    if metodo == "pearson":
        res = stats.pearsonr(d[x], d[y], alternative=alternativa)
    else:
        res = stats.spearmanr(d[x], d[y], alternative=alternativa)
    r, p = float(res.statistic), float(res.pvalue)
    lo, hi = _ic_fisher(r, n, metodo)
    return {"x": x, "y": y, "metodo": metodo, "n": n, "r": r, "p": p, "ic95_inf": lo, "ic95_sup": hi,
            "alternativa": alternativa, "nota": ""}


def normalidad(serie: pd.Series) -> dict:
    s = serie.dropna()
    w, p = stats.shapiro(s)
    return {"variable": serie.name, "n": len(s), "shapiro_w": float(w), "p": float(p),
            "normal_al_5pct": bool(p >= ALFA), "asimetria": float(stats.skew(s)),
            "curtosis": float(stats.kurtosis(s))}


def describir(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """Media, mediana, desviación, mínimo, máximo y cobertura de cada variable."""
    filas = []
    for c in cols:
        s = df[c]
        filas.append({"variable": c, "n": int(s.notna().sum()), "faltantes": int(s.isna().sum()),
                      "media": s.mean(), "mediana": s.median(), "desv_est": s.std(),
                      "min": s.min(), "max": s.max()})
    return pd.DataFrame(filas)


# ------------------------------------------------------------------ regresión

def regresion(df: pd.DataFrame, formula: str) -> dict:
    """OLS con diagnósticos. Si Breusch-Pagan rechaza, se reajusta con errores robustos HC3."""
    tokens = set(re.findall(r"[A-Za-z_][A-Za-z0-9_]*", formula))
    vars_modelo = [v for v in df.columns if v in tokens]
    d = df[vars_modelo].dropna()
    modelo = smf.ols(formula, data=d).fit()
    bp_stat, bp_p, _, _ = het_breuschpagan(modelo.resid, modelo.model.exog)
    robusto = bp_p < ALFA
    final = modelo.get_robustcov_results(cov_type="HC3") if robusto else modelo

    cook = modelo.get_influence().cooks_distance[0]
    umbral = 4 / len(d)
    influyentes = d.index[cook > umbral].tolist()

    exog = modelo.model.exog
    nombres = modelo.model.exog_names
    vif = {nombres[i]: float(variance_inflation_factor(exog, i))
           for i in range(exog.shape[1]) if nombres[i] != "Intercept"} if exog.shape[1] > 2 else {}

    params = pd.Series(np.asarray(final.params), index=nombres)
    bse = pd.Series(np.asarray(final.bse), index=nombres)
    pvals = pd.Series(np.asarray(final.pvalues), index=nombres)
    ci = pd.DataFrame(np.asarray(final.conf_int()), index=nombres, columns=["ic95_inf", "ic95_sup"])
    coef = pd.concat([params.rename("coef"), bse.rename("error_est"), pvals.rename("p"), ci], axis=1)

    return {"formula": formula, "n": int(modelo.nobs), "r2": float(modelo.rsquared),
            "r2_ajustado": float(modelo.rsquared_adj), "breusch_pagan_p": float(bp_p),
            "errores": "HC3" if robusto else "clasicos", "shapiro_residuos_p": float(stats.shapiro(modelo.resid)[1]),
            "influyentes_cook": influyentes, "umbral_cook": umbral, "vif": vif,
            "coeficientes": coef, "resumen_texto": str(final.summary())}


# ------------------------------------------------------------------ comparaciones múltiples

def ajustar_holm(pvalores: list[float]) -> list[float]:
    p = np.asarray(pvalores, dtype=float)
    ok = ~np.isnan(p)
    out = np.full_like(p, np.nan)
    if ok.any():
        out[ok] = multipletests(p[ok], method="holm")[1]
    return out.tolist()


def conclusion(p: float, r: float, alternativa: str = "greater") -> str:
    if np.isnan(p):
        return "Datos insuficientes"
    if p < ALFA and (alternativa != "greater" or r > 0):
        return "Hay evidencia de asociación" + (" positiva" if alternativa == "greater" else "")
    return "No se rechaza H0"


# ------------------------------------------------------------------ guardado

def guardar_regresion(res: dict, nombre: str) -> None:
    STATS.mkdir(parents=True, exist_ok=True)
    res["coeficientes"].to_csv(STATS / f"regresion_{nombre}_coeficientes.csv")
    (STATS / f"regresion_{nombre}_resumen.txt").write_text(res["resumen_texto"], encoding="utf-8")
    meta = {k: v for k, v in res.items() if k not in ("coeficientes", "resumen_texto")}
    (STATS / f"regresion_{nombre}.json").write_text(json.dumps(meta, indent=2, default=str), encoding="utf-8")


# ------------------------------------------------------------------ hipótesis principal (P5)

def hipotesis_principal(d2020: pd.DataFrame, alterno: pd.DataFrame | None = None) -> pd.DataFrame:
    """H0: no hay asociación positiva entre prop_18_44_pct y puntaje_mdm (2020).

    d2020: municipio_anio filtrado a 2020 (pandas), con prop_18_44_pct, puntaje_mdm,
           poblacion_total, pct_rural, grupo_capacidad.
    alterno: columnas codigo_municipio, puntaje_mdm_alt, prop_18_44_alt_pct (sensibilidad).
    """
    STATS.mkdir(parents=True, exist_ok=True)
    d = d2020.copy()
    d["log_poblacion"] = np.log(d["poblacion_total"])
    filas = []

    # 1. normalidad -> decide la medida principal
    norm = pd.DataFrame([normalidad(d["prop_18_44_pct"]), normalidad(d["puntaje_mdm"])])
    norm.to_csv(STATS / "h_principal_normalidad.csv", index=False)
    describir(d, ["prop_18_44_pct", "puntaje_mdm", "poblacion_total", "pct_rural"]) \
        .to_csv(STATS / "h_principal_descriptivos.csv", index=False)

    # 2. correlaciones (unilaterales: H1 es asociación positiva)
    for metodo in ("pearson", "spearman"):
        filas.append({"analisis": "principal", **correlacion(d, "prop_18_44_pct", "puntaje_mdm", metodo, "greater")})

    # 3. regresiones
    simple = regresion(d, "puntaje_mdm ~ prop_18_44_pct")
    guardar_regresion(simple, "h_principal_simple")
    controles = regresion(d, "puntaje_mdm ~ prop_18_44_pct + log_poblacion + pct_rural + C(grupo_capacidad)")
    guardar_regresion(controles, "h_principal_controles")

    # 4. sensibilidad (a): sin observaciones influyentes del modelo simple
    sin_inf = d.drop(index=simple["influyentes_cook"])
    for metodo in ("pearson", "spearman"):
        filas.append({"analisis": "sensibilidad_sin_influyentes",
                      **correlacion(sin_inf, "prop_18_44_pct", "puntaje_mdm", metodo, "greater")})

    # 4. sensibilidad (b) y (c): bloque alterno del MDM y proporción desde la fuente alterna
    if alterno is not None:
        m = d.merge(alterno, on="codigo_municipio", how="left")
        if "puntaje_mdm_alt" in m:
            filas.append({"analisis": "sensibilidad_bloque_alterno_mdm",
                          **correlacion(m, "prop_18_44_pct", "puntaje_mdm_alt", "spearman", "greater")})
        if "prop_18_44_alt_pct" in m:
            filas.append({"analisis": "sensibilidad_poblacion_fuente_alterna",
                          **correlacion(m, "prop_18_44_alt_pct", "puntaje_mdm", "spearman", "greater")})

    res = pd.DataFrame(filas)
    res["conclusion"] = [conclusion(p, r) for p, r in zip(res["p"], res["r"])]
    res.to_csv(STATS / "h_principal_correlaciones.csv", index=False)
    return res


# ------------------------------------------------------------------ complementarias (P2, P4)

def hipotesis_produccion_poblacion(d2023: pd.DataFrame) -> pd.DataFrame:
    """A (P2): asociación entre producción agrícola total y población 18-64 (2023)."""
    d = d2023.copy()
    d["log_produccion"] = np.log1p(d["produccion_total_t"])
    d["log_pob_18_64"] = np.log(d["pob_18_64"])
    filas = [{"analisis": "A_produccion_vs_pob_18_64",
              **correlacion(d, "pob_18_64", "produccion_total_t", "spearman")},
             {"analisis": "A_log_produccion_vs_log_pob",
              **correlacion(d, "log_pob_18_64", "log_produccion", "pearson")}]
    guardar_regresion(regresion(d, "log_produccion ~ log_pob_18_64"), "h_a_log_log")
    return pd.DataFrame(filas)


def hipotesis_suelo_rendimiento(d2023: pd.DataFrame) -> pd.DataFrame:
    """B (P4): asociación entre % de clases III-IV y rendimiento de papa (municipios con papa)."""
    d = d2023[d2023["rendimiento_papa_t_ha"].notna()].copy()
    filas = [{"analisis": "B_suelo_iii_iv_vs_rendimiento_papa",
              **correlacion(d, "pct_clases_iii_iv", "rendimiento_papa_t_ha", "spearman")}]
    guardar_regresion(regresion(d, "rendimiento_papa_t_ha ~ pct_clases_iii_iv"), "h_b_suelo")
    return pd.DataFrame(filas)


def hipotesis_sexo(d2020: pd.DataFrame) -> pd.DataFrame:
    """Opcional: patrones de mujeres y hombres 18-44 frente al desempeño."""
    return pd.DataFrame([
        {"analisis": "D_mujeres_18_44_vs_mdm", **correlacion(d2020, "prop_mujeres_18_44_pct", "puntaje_mdm")},
        {"analisis": "D_hombres_18_44_vs_mdm", **correlacion(d2020, "prop_hombres_18_44_pct", "puntaje_mdm")},
    ])


def consolidar(principal: pd.DataFrame, complementarias: list[pd.DataFrame]) -> pd.DataFrame:
    """Tabla única de resultados. Holm solo sobre las complementarias (exploratorias)."""
    comp = pd.concat(complementarias, ignore_index=True)
    comp["p_holm"] = ajustar_holm(comp["p"].tolist())
    comp["conclusion"] = [conclusion(p, r, a) for p, r, a in zip(comp["p_holm"], comp["r"], comp["alternativa"])]
    comp["tipo"] = "exploratoria"
    principal = principal.assign(p_holm=np.nan, tipo="principal")
    todo = pd.concat([principal, comp], ignore_index=True)
    todo.to_csv(STATS / "resultados_hipotesis.csv", index=False)
    return todo
