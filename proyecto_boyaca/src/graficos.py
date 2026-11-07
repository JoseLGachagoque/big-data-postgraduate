"""Gráficos estadísticos (no mapas). Cada función indica su dueño.

Toda figura lleva título, año, fuente, unidad, leyenda cuando aplica y una nota de lectura
(sección 8 del enunciado). Se guardan en outputs/figures/ a 200 dpi.
"""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.config import FIGURES

COLOR = "#2E6F8E"
COLOR_2 = "#C8553D"
plt.rcParams.update({"figure.dpi": 100, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.alpha": 0.3, "font.size": 10})


def pie(fig, fuente: str, nota: str = "") -> None:
    """Pie de figura común: fuente y nota de interpretación."""
    texto = f"Fuente: {fuente}." + (f"\n{nota}" if nota else "")
    fig.text(0.01, 0.005, texto, ha="left", va="bottom", fontsize=8, color="#555", wrap=True)


def guardar(fig, nombre: str):
    FIGURES.mkdir(parents=True, exist_ok=True)
    ruta = FIGURES / f"{nombre}.png"
    fig.savefig(ruta, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return ruta


# ------------------------------------------------------------------ P1

def piramide_poblacional(poblacion_area: pd.DataFrame, anio: int):
    """P1. Pirámide de Boyacá por grupos quinquenales y sexo."""
    d = poblacion_area[poblacion_area["anio"] == anio].copy()
    d["grupo"] = (d["edad"] // 5 * 5).clip(upper=85)
    g = d.groupby(["grupo", "sexo"])["personas"].sum().unstack(fill_value=0)
    total = g.values.sum()
    etiquetas = [f"{i}-{i + 4}" if i < 85 else "85+" for i in g.index]

    fig, ax = plt.subplots(figsize=(8, 6.5))
    ax.barh(etiquetas, -g["H"] / total * 100, color=COLOR, label="Hombres")
    ax.barh(etiquetas, g["M"] / total * 100, color=COLOR_2, label="Mujeres")
    lim = max(g.max()) / total * 100 * 1.1
    ax.set_xlim(-lim, lim)
    ax.set_xticks(ax.get_xticks())
    ax.set_xticklabels([f"{abs(x):.1f}" for x in ax.get_xticks()])
    ax.axhspan(etiquetas.index("20-24") - 0.5, etiquetas.index("40-44") + 0.5, color="#f0c419", alpha=0.15,
               label="Grupos 20-44 (aprox. al rango 18-44)")
    ax.set_xlabel("% de la población departamental")
    ax.set_title(f"Boyacá: población por edad y sexo, {anio}")
    ax.legend(loc="lower right")
    pie(fig, "DANE, proyecciones por área (archivo de centros poblados), cabecera + rural",
        "Cada barra es el % del total departamental en ese grupo de edad y sexo.")
    return guardar(fig, f"p1_piramide_{anio}")


def distribucion_rural(municipio_anio: pd.DataFrame, anio: int):
    """P1. Histograma del % de población rural por municipio."""
    d = municipio_anio[municipio_anio["anio"] == anio]["pct_rural"].dropna()
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.hist(d, bins=20, color=COLOR, edgecolor="white")
    ax.axvline(d.median(), color=COLOR_2, ls="--", label=f"Mediana {d.median():.1f} %")
    ax.set_xlabel("% de la población en centros poblados y rural disperso")
    ax.set_ylabel("Número de municipios")
    ax.set_title(f"Boyacá: población rural por municipio, {anio} (n = {len(d)})")
    ax.legend()
    pie(fig, "DANE, proyecciones por área")
    return guardar(fig, f"p1_distribucion_rural_{anio}")


# ------------------------------------------------------------------ P2

def produccion_rendimiento_por_cultivo(resumen_cultivos: pd.DataFrame, anio: int, top: int = 15):
    """P2. Producción total y rendimiento departamental de los cultivos con más producción."""
    d = resumen_cultivos.sort_values("produccion_t", ascending=False).head(top).iloc[::-1]
    nombres = d["cultivo"] + " (" + d["estado_fisico"].str.lower() + ")"
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 6.5), sharey=True)
    a1.barh(nombres, d["produccion_t"] / 1000, color=COLOR)
    a1.set_xlabel("Producción (miles de t)")
    a1.set_title("Producción")
    a2.barh(nombres, d["rendimiento_t_ha"], color=COLOR_2)
    a2.set_xlabel("Rendimiento (t/ha) = Σ producción / Σ área cosechada")
    a2.set_title("Rendimiento")
    fig.suptitle(f"Boyacá: {top} cultivos con mayor producción, {anio}")
    pie(fig, "UPRA - Evaluaciones Agropecuarias Municipales",
        "Las toneladas no son comparables entre cultivos con distinto estado físico.")
    return guardar(fig, f"p2_produccion_rendimiento_cultivos_{anio}")


def produccion_por_1000(municipio_anio: pd.DataFrame, anio: int, top: int = 25):
    """P2. Producción agrícola por cada 1.000 habitantes de 18 a 64 años."""
    d = (municipio_anio[municipio_anio["anio"] == anio].dropna(subset=["produccion_1k_18_64"])
         .sort_values("produccion_1k_18_64", ascending=False))
    mediana = d["produccion_1k_18_64"].median()
    d = d.head(top).iloc[::-1]
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.barh(d["municipio"], d["produccion_1k_18_64"], color=COLOR)
    ax.axvline(mediana, color=COLOR_2, ls="--", label=f"Mediana departamental {mediana:,.0f} t")
    ax.set_xlabel("t por cada 1.000 habitantes de 18 a 64 años")
    ax.set_title(f"Producción agrícola por 1.000 habitantes de 18-64 años, {anio} ({top} mayores)")
    ax.legend()
    pie(fig, "UPRA - EVA; DANE - proyecciones de población",
        "Suma toneladas de todos los cultivos: no es valor económico ni productividad laboral.")
    return guardar(fig, f"p2_produccion_por_1000_{anio}")


# ------------------------------------------------------------------ P4

def distribucion_clases(distribucion: pd.DataFrame):
    """P4. % del área departamental en cada clase de capacidad de uso."""
    orden = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "ZU", "CA"]
    d = distribucion.set_index("clase").reindex([c for c in orden if c in set(distribucion["clase"])])
    colores = [COLOR if c not in ("ZU", "CA") else "#999" for c in d.index]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar(d.index, d["pct_area"], color=colores)
    for i, v in enumerate(d["pct_area"]):
        ax.text(i, v + 0.5, f"{v:.1f}", ha="center", fontsize=8)
    ax.set_ylabel("% del área clasificada de Boyacá")
    ax.set_xlabel("Clase de capacidad de uso (ZU = zona urbana, CA = cuerpo de agua)")
    ax.set_title("Boyacá: distribución de clases de capacidad de uso de las tierras")
    pie(fig, "IGAC, mapa de capacidad de uso de las tierras, escala 1:100.000 (2004)",
        "Capacidad de uso, no fertilidad actual. Clases más bajas = menos limitaciones.")
    return guardar(fig, "p4_distribucion_clases")


# ------------------------------------------------------------------ P5

def dispersion(df: pd.DataFrame, x: str, y: str, titulo: str, xlabel: str, ylabel: str, fuente: str,
               nombre: str, res_corr: dict | None = None, etiquetar: int = 5, log: bool = False):
    """P5. Dispersión con recta de mínimos cuadrados y la correlación en el título."""
    d = df.dropna(subset=[x, y])
    if log:   # la escala log no admite ceros
        d = d[(d[x] > 0) & (d[y] > 0)]
    fig, ax = plt.subplots(figsize=(8, 5.5))
    ax.scatter(d[x], d[y], s=22, color=COLOR, alpha=0.75, edgecolor="white", linewidth=0.5)
    if len(d) > 2:
        xs, ys = (np.log10(d[x]), np.log10(d[y])) if log else (d[x], d[y])
        b, a = np.polyfit(xs, ys, 1)
        gx = np.linspace(xs.min(), xs.max(), 50)
        gy = a + b * gx
        ax.plot(10 ** gx if log else gx, 10 ** gy if log else gy, color=COLOR_2, lw=1.5, label="Recta MCO")
    if log:
        ax.set_xscale("log")
        ax.set_yscale("log")
    if etiquetar and "municipio" in d:
        extremos = pd.concat([d.nlargest(etiquetar, y), d.nsmallest(etiquetar, y)])
        for _, f in extremos.drop_duplicates().iterrows():
            ax.annotate(f["municipio"], (f[x], f[y]), fontsize=7, xytext=(3, 3), textcoords="offset points")
    sub = ""
    if res_corr:
        sub = (f"\n{res_corr['metodo'].capitalize()} r = {res_corr['r']:.2f} "
               f"(IC 95 % {res_corr['ic95_inf']:.2f} a {res_corr['ic95_sup']:.2f}), "
               f"p = {res_corr['p']:.3f}, n = {res_corr['n']}")
    ax.set_title(titulo + sub)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.legend(loc="best")
    pie(fig, fuente, "Una asociación entre municipios no demuestra causalidad.")
    return guardar(fig, nombre)
