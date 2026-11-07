"""Cálculo único de las cifras y respuestas del proyecto. Dueño: P6.

Lo usan `generar_informe.py` (docs/informe_final.md) y `publicar_sitio.py` (site/),
para que el informe y la página muestren exactamente los mismos números.
Todo se lee de data_lake/ y outputs/: nada se escribe a mano.
"""
from __future__ import annotations

import glob
import json
from dataclasses import dataclass, field

import polars as pl

from src.config import ANIO_EVA, ANIO_MDM, GOLD, MDM_BLOQUE_OFICIAL, QUALITY, REJECTS, SILVER, STATS


# ------------------------------------------------------------------ formato (español)

def n0(x) -> str:
    """Entero con punto de miles: 1248977 -> '1.248.977'."""
    return f"{x:,.0f}".replace(",", ".") if x is not None else "—"


def n1(x, d: int = 1) -> str:
    """Decimal con coma: 38.04 -> '38,0'."""
    if x is None:
        return "—"
    return f"{x:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def pv(p) -> str:
    """Valor p legible."""
    if p is None:
        return "—"
    return "< 0,001" if p < 0.001 else n1(p, 3)


def ic(lo, hi, d: int = 2) -> str:
    return f"{n1(lo, d)} a {n1(hi, d)}"


# ------------------------------------------------------------------ carga

@dataclass
class Resumen:
    f: dict = field(default_factory=dict)        # cifras sueltas
    tablas: dict = field(default_factory=dict)   # DataFrames para mostrar


def _leer(ruta, lector=pl.read_csv):
    if not ruta.exists():
        raise FileNotFoundError(f"Falta {ruta}. Ejecute primero ./run_pipeline.sh")
    return lector(ruta)


def cargar() -> Resumen:
    r = Resumen()
    f = r.f

    # ---------------- población
    pob = _leer(SILVER / "poblacion.parquet", pl.read_parquet)
    dep = (pob.group_by("anio").agg(pl.col("poblacion_total", "pob_18_44", "pob_18_64").sum()).sort("anio")
              .with_columns(p44=pl.col("pob_18_44") / pl.col("poblacion_total") * 100,
                            p64=pl.col("pob_18_64") / pl.col("poblacion_total") * 100))
    a0, a1 = dep.row(0, named=True), dep.row(-1, named=True)
    f.update(pob_anio_ini=a0["anio"], pob_anio_fin=a1["anio"], pob_ini=a0["poblacion_total"], pob_fin=a1["poblacion_total"],
             p44_ini=a0["p44"], p44_fin=a1["p44"], p64_ini=a0["p64"], p64_fin=a1["p64"])

    ma = _leer(GOLD / "municipio_anio.parquet", pl.read_parquet)
    d20 = ma.filter(pl.col("anio") == ANIO_MDM)
    d23 = ma.filter(pl.col("anio") == ANIO_EVA)
    f["n_municipios"] = d20.height
    s = d20.sort("prop_18_44_pct")
    f.update(p44_mun_med=d20["prop_18_44_pct"].median(), p44_mun_min=s.row(0, named=True), p44_mun_max=s.row(-1, named=True),
             rural_med=d20["pct_rural"].median())
    tunja = d20.filter(pl.col("municipio") == "Tunja")
    f["tunja_pct_pob"] = (tunja["poblacion_total"][0] / d20["poblacion_total"].sum() * 100) if tunja.height else None

    # ---------------- desempeño
    s = d20.sort("puntaje_mdm")
    f.update(mdm_med=d20["puntaje_mdm"].median(), mdm_min=s.row(0, named=True), mdm_max=s.row(-1, named=True))
    r.tablas["grupos"] = (d20.group_by("grupo_capacidad")
                             .agg(municipios=pl.len(), mdm_medio=pl.col("puntaje_mdm").mean(),
                                  joven_medio=pl.col("prop_18_44_pct").mean())
                             .sort("grupo_capacidad"))
    bloques = _leer(QUALITY / "desempeno_comparacion_bloques.csv")
    f.update(bloques_dif_media=bloques["diferencia"].abs().mean(), bloques_dif_max=bloques["diferencia"].abs().max(),
             bloques_corr=bloques.select(pl.corr("mdm_a", "mdm_b")).item(), bloque_oficial=MDM_BLOQUE_OFICIAL)
    incoh = _leer(QUALITY / "desempeno_nombres_incoherentes.csv")
    r.tablas["incoherentes"] = incoh

    # ---------------- agrícola
    from src.gold_agricola import resumen_departamental_por_cultivo
    cm = _leer(GOLD / "cultivo_municipio.parquet", pl.read_parquet)
    cult = resumen_departamental_por_cultivo(cm)
    r.tablas["cultivos"] = cult
    f.update(n_cultivos=cm["cultivo"].n_unique(), prod_total=cm["produccion_t"].sum(),
             top_cultivos=cult.head(3).to_dicts())
    f.update(papa_munis=d23["produccion_papa_t"].drop_nulls().len(), papa_total=d23["produccion_papa_t"].sum(),
             papa_rend=d23["produccion_papa_t"].sum() / d23["area_cosechada_papa_ha"].sum(),
             papa_top=d23.sort("produccion_papa_t", descending=True, nulls_last=True).head(3)
                         .select("municipio", "produccion_papa_t", "rendimiento_papa_t_ha").to_dicts())
    top1k = d23.sort("produccion_1k_18_64", descending=True, nulls_last=True).head(3)
    cana = (cm.filter(pl.col("codigo_municipio").is_in(top1k["codigo_municipio"].to_list()))
              .group_by("codigo_municipio")
              .agg(pct_cana=pl.col("produccion_t").filter(pl.col("cultivo") == "Caña").sum() / pl.col("produccion_t").sum() * 100))
    f.update(p1k_med=d23["produccion_1k_18_64"].median(),
             p1k_top=top1k.select("codigo_municipio", "municipio", "produccion_1k_18_64").join(cana, on="codigo_municipio", how="left").to_dicts(),
             pob_18_64_2023=d23["pob_18_64"].sum())

    # ---------------- suelo
    from src.gold_suelo import distribucion_departamental
    sm = _leer(GOLD / "suelo_municipio.parquet", pl.read_parquet)
    sr = _leer(GOLD / "suelo_resumen.parquet", pl.read_parquet)
    dist = distribucion_departamental(sm)
    r.tablas["suelo"] = dist
    pct = dict(zip(dist["clase"], dist["pct_area"]))
    f.update(suelo_pct=pct, suelo_vii_viii=pct.get("VII", 0) + pct.get("VIII", 0), suelo_iii_iv=pct.get("III", 0) + pct.get("IV", 0),
             suelo_pred=dict(sr.group_by("clase_predominante").len().sort("len", descending=True).rows()),
             suelo_sin_clas_5=sr.filter(pl.col("pct_sin_clasificar") > 5).height)

    # ---------------- calidad
    capas = {}
    for capa in ("bronze", "silver", "gold"):
        m = _leer(QUALITY / f"metricas_{capa}.csv")
        accion = "accion_si_falla" if "accion_si_falla" in m.columns else "accion"
        fallas = m.filter(pl.col("resultado") == "FALLA").rename({accion: "accion_si_falla"})
        capas[capa] = {"reglas": m.height, "ok": m.height - fallas.height, "fallas": fallas}
    r.tablas["calidad"] = capas
    f["rechazados"] = sum(pl.read_parquet(p).height for p in glob.glob(str(REJECTS / "*.parquet")))
    conc = _leer(QUALITY / "conciliacion_poblacion_fuentes.csv")
    f.update(conc_min=conc["diferencia"].min(), conc_med=conc["diferencia"].median(), conc_max=conc["diferencia"].max(),
             conc_pct_max=conc["diferencia_pct"].abs().max())
    nv = {}
    for p in sorted(glob.glob(str(QUALITY / "no_vinculados_*.csv"))):
        nombre = p.rsplit("no_vinculados_", 1)[1][:-4]
        nv[nombre] = pl.read_csv(p).height
    f["no_vinculados"] = nv

    # ---------------- estadística
    hip = _leer(STATS / "resultados_hipotesis.csv")
    r.tablas["hipotesis"] = hip

    def fila(analisis, metodo=None):
        q = hip.filter(pl.col("analisis") == analisis)
        if metodo:
            q = q.filter(pl.col("metodo") == metodo)
        return q.row(0, named=True) if q.height else None

    f.update(h_sp=fila("principal", "spearman"), h_pe=fila("principal", "pearson"),
             s_inf=fila("sensibilidad_sin_influyentes", "spearman"), s_blo=fila("sensibilidad_bloque_alterno_mdm"),
             s_pob=fila("sensibilidad_poblacion_fuente_alterna"), h_a=fila("A_produccion_vs_pob_18_64"),
             h_a_log=fila("A_log_produccion_vs_log_pob"), h_b=fila("B_suelo_iii_iv_vs_rendimiento_papa"),
             h_dm=fila("D_mujeres_18_44_vs_mdm"), h_dh=fila("D_hombres_18_44_vs_mdm"))

    def coef(nombre_modelo, var):
        c = _leer(STATS / f"regresion_{nombre_modelo}_coeficientes.csv")
        c = c.rename({c.columns[0]: "termino"})
        row = c.filter(pl.col("termino") == var)
        meta = json.loads((STATS / f"regresion_{nombre_modelo}.json").read_text(encoding="utf-8"))
        return (row.row(0, named=True) if row.height else None), meta, c

    f["reg_simple"], f["reg_simple_meta"], _ = coef("h_principal_simple", "prop_18_44_pct")
    f["reg_ctrl"], f["reg_ctrl_meta"], r.tablas["reg_ctrl"] = coef("h_principal_controles", "prop_18_44_pct")
    norm = _leer(STATS / "h_principal_normalidad.csv")
    f["normal_ambas"] = bool(norm["normal_al_5pct"].all())
    return r


# ------------------------------------------------------------------ textos

def conclusion_principal(f: dict) -> str:
    sp, rc = f["h_sp"], f["reg_ctrl"]
    base = (f"En {ANIO_MDM}, los municipios con mayor proporción de población de 18 a 44 años tienen, en promedio, "
            f"mejor desempeño municipal: Spearman r = {n1(sp['r'], 2)} (IC 95 % {ic(sp['ic95_inf'], sp['ic95_sup'])}), "
            f"p = {pv(sp['p'])}, n = {sp['n']}. Se rechaza H0, pero la asociación es débil.")
    if rc and rc["p"] >= 0.05:
        base += (f" Al controlar por tamaño, % rural y grupo de capacidades, el efecto deja de ser significativo "
                 f"(coeficiente {n1(rc['coef'], 2)}, IC 95 % {ic(rc['ic95_inf'], rc['ic95_sup'])}, p = {pv(rc['p'])}): "
                 f"buena parte de la asociación la explica el grupo de capacidades iniciales del municipio.")
    elif rc:
        base += f" La asociación se mantiene con controles (coeficiente {n1(rc['coef'], 2)}, p = {pv(rc['p'])})."
    return base + " No demuestra causalidad ni mide disposición al cambio."


def respuestas(f: dict) -> list[dict]:
    """Las 6 preguntas de investigación (sección 3 del enunciado) con su respuesta y evidencia."""
    sp, pe, rs, rc = f["h_sp"], f["h_pe"], f["reg_simple"], f["reg_ctrl"]
    top = f["top_cultivos"]
    p1k = f["p1k_top"]
    pct = f["suelo_pct"]
    pred = f["suelo_pred"]
    return [
        {"n": 1, "pregunta": "¿Cómo se distribuyen la población y los grupos de edad entre los municipios?",
         "respuesta": (f"Boyacá pasa de {n0(f['pob_ini'])} habitantes en {f['pob_anio_ini']} a {n0(f['pob_fin'])} en {f['pob_anio_fin']}. "
                       f"La población de 18 a 44 años sube de {n1(f['p44_ini'])} % a {n1(f['p44_fin'])} % del total departamental, "
                       f"y la de 18 a 64 de {n1(f['p64_ini'])} % a {n1(f['p64_fin'])} %. Entre municipios la proporción joven varía mucho: "
                       f"mediana {n1(f['p44_mun_med'])} %, desde {n1(f['p44_mun_min']['prop_18_44_pct'])} % en {f['p44_mun_min']['municipio']} "
                       f"hasta {n1(f['p44_mun_max']['prop_18_44_pct'])} % en {f['p44_mun_max']['municipio']}. "
                       f"Es un departamento rural: la mitad de los municipios tiene más de {n1(f['rural_med'], 0)} % de su población fuera de la cabecera."),
         "evidencia": "Pirámide p1, mapa m1, distribución rural p1"},
        {"n": 2, "pregunta": "¿Cuáles municipios presentan mayor producción y cuáles mayor rendimiento por cultivo?",
         "respuesta": (f"La EVA {ANIO_EVA} registra {f['n_cultivos']} cultivos. Por toneladas dominan "
                       + ", ".join(f"{c['cultivo'].lower()} ({n0(c['produccion_t'])} t)" for c in top)
                       + f". La papa, cultivo seleccionado, se reporta en {f['papa_munis']} municipios con un rendimiento departamental de "
                       f"{n1(f['papa_rend'])} t/ha; los mayores productores son "
                       + ", ".join(f"{p['municipio']} ({n0(p['produccion_papa_t'])} t)" for p in f["papa_top"])
                       + ". En producción por 1.000 habitantes de 18–64 lideran "
                       + ", ".join(p["municipio"] for p in p1k)
                       + f", pero más del {n1(min(p['pct_cana'] or 0 for p in p1k), 0)} % de su producción es caña: "
                       f"el indicador suma toneladas no comparables (mediana departamental {n0(f['p1k_med'])} t)."),
         "evidencia": "Gráficos p2, mapas m3 y m4, gold/cultivo_municipio"},
        {"n": 3, "pregunta": "¿Cómo se distribuyen las clases de capacidad de uso de las tierras en cada municipio?",
         "respuesta": (f"El {n1(f['suelo_vii_viii'], 0)} % del área es de clases VII y VIII (VIII {n1(pct.get('VIII'))} %, "
                       f"VII {n1(pct.get('VII'))} %): tierras con fuertes limitaciones, aptas sobre todo para conservación y uso forestal. "
                       f"Solo el {n1(f['suelo_iii_iv'])} % es de clases III–IV, las de menos limitaciones presentes (no hay I ni II). "
                       f"Clase predominante por municipio: "
                       + ", ".join(f"{k} en {v}" for k, v in pred.items())
                       + f". {f['suelo_sin_clas_5']} municipios tienen más de 5 % de su área sin clasificar."),
         "evidencia": "Gráfico p4, mapa m5, gold/suelo_municipio (IGAC 1:100.000, 2004)"},
        {"n": 4, "pregunta": "¿Existe una asociación entre la proporción de población de 18 a 44 años y el desempeño municipal?",
         "respuesta": (f"Sí, positiva y débil. Spearman r = {n1(sp['r'], 2)} (IC 95 % {ic(sp['ic95_inf'], sp['ic95_sup'])}, p = {pv(sp['p'])}); "
                       f"Pearson r = {n1(pe['r'], 2)} (IC {ic(pe['ic95_inf'], pe['ic95_sup'])}, p = {pv(pe['p'])}); n = {sp['n']}. "
                       f"Cada punto porcentual más de población joven se asocia con {n1(rs['coef'], 2)} puntos más de MDM "
                       f"(IC {ic(rs['ic95_inf'], rs['ic95_sup'])}); la proporción joven explica un {n1(f['reg_simple_meta']['r2'] * 100, 0)} % "
                       f"de las diferencias. Se rechaza H0 con α = 0,05."),
         "evidencia": "Dispersión p5, mapas m6 y m7, outputs/stats/h_principal_correlaciones.csv"},
        {"n": 5, "pregunta": "¿Cómo se relacionan la producción agrícola y la población de 18 a 64 años?",
         "respuesta": (f"Asociación positiva moderada: Spearman r = {n1(f['h_a']['r'], 2)} (IC {ic(f['h_a']['ic95_inf'], f['h_a']['ic95_sup'])}), "
                       f"p ajustado por Holm {pv(f['h_a']['p_holm'])}; en escala logarítmica r = {n1(f['h_a_log']['r'], 2)}. "
                       f"Los municipios con más población en edad de trabajar producen más toneladas, en buena parte por tamaño. "
                       f"Además, en los {f['h_b']['n']} municipios con papa, más área de clases III–IV se asocia con mayor rendimiento "
                       f"(r = {n1(f['h_b']['r'], 2)}, p Holm {pv(f['h_b']['p_holm'])})."),
         "evidencia": "Dispersión p5 (producción vs población), resultados_hipotesis.csv"},
        {"n": 6, "pregunta": "¿Cómo cambian los resultados al considerar el tamaño poblacional y otras variables?",
         "respuesta": (f"La asociación se mantiene en las tres sensibilidades: sin influyentes r = {n1(f['s_inf']['r'], 2)}, con el otro bloque del MDM "
                       f"r = {n1(f['s_blo']['r'], 2)} y con la otra fuente de población r = {n1(f['s_pob']['r'], 2)} (todas p < 0,01). "
                       f"Pero con controles (log de población, % rural y grupo de capacidades G1–G5) el coeficiente baja a {n1(rc['coef'], 2)} "
                       f"(IC {ic(rc['ic95_inf'], rc['ic95_sup'])}, p = {pv(rc['p'])}) y deja de ser significativo. "
                       f"Los municipios G1, de mayores capacidades, tienen a la vez más población joven y mejor MDM. "
                       f"Por sexo: mujeres de 18–44 r = {n1(f['h_dm']['r'], 2)} (p Holm {pv(f['h_dm']['p_holm'])}); hombres r = {n1(f['h_dh']['r'], 2)} "
                       f"(p Holm {pv(f['h_dh']['p_holm'])}, no significativo)."),
         "evidencia": "outputs/stats/regresion_h_principal_controles_*, tabla de grupos de capacidad"},
    ]
