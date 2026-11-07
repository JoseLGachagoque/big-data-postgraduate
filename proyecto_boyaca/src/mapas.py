"""Mapas municipales. Dueño: P3.

Reglas de estilo comunes (sección 8 del enunciado):
- Título con año, unidad en la leyenda, fuente al pie.
- Municipios sin dato en gris con trama y con su propia entrada de leyenda.
- La clasificación (cuantiles, k clases) se declara en el pie del mapa.
Se dibuja en EPSG:9377 para no deformar las formas; se guardan en outputs/maps/.
"""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import geopandas as gpd
import mapclassify
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch

from src.config import CRS_AREAS, MAPS

SIN_DATOS = {"color": "#dddddd", "hatch": "///", "edgecolor": "#999999", "label": "Sin datos"}


def _base(titulo: str):
    fig, ax = plt.subplots(figsize=(8, 8.5))
    ax.set_axis_off()
    ax.set_title(titulo, fontsize=12)
    return fig, ax


def _pie(fig, fuente: str, clasificacion: str):
    fig.text(0.02, 0.02, f"Fuente: {fuente}.\nClasificación: {clasificacion}. Proyección EPSG:9377.",
             fontsize=8, color="#555")


def _guardar(fig, nombre: str):
    MAPS.mkdir(parents=True, exist_ok=True)
    ruta = MAPS / f"{nombre}.png"
    fig.savefig(ruta, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return ruta


def coropleta(gdf: gpd.GeoDataFrame, columna: str, titulo: str, unidad: str, fuente: str, nombre: str,
              k: int = 5, esquema: str = "Quantiles", cmap: str = "YlGnBu"):
    """Mapa coroplético con cortes por cuantiles (k clases)."""
    g = gdf.to_crs(CRS_AREAS)
    n_datos = int(g[columna].notna().sum())
    fig, ax = _base(titulo)
    g.plot(column=columna, ax=ax, scheme=esquema, k=min(k, max(n_datos - 1, 1)), cmap=cmap,
           edgecolor="white", linewidth=0.3, legend=True, missing_kwds=SIN_DATOS,
           legend_kwds={"title": unidad, "loc": "lower right", "fontsize": 8, "fmt": "{:,.1f}"})
    _pie(fig, fuente, f"{esquema} con {k} clases; {n_datos} de {len(g)} municipios con dato")
    return _guardar(fig, nombre)


def categorico(gdf: gpd.GeoDataFrame, columna: str, titulo: str, fuente: str, nombre: str,
               orden: list[str] | None = None, cmap: str = "RdYlGn_r"):
    """Mapa de categorías (p. ej. clase de suelo predominante)."""
    g = gdf.to_crs(CRS_AREAS)
    cats = orden or sorted(g[columna].dropna().unique())
    cats = [c for c in cats if c in set(g[columna].dropna())]
    colores = plt.get_cmap(cmap)(np.linspace(0.1, 0.9, max(len(cats), 1)))
    fig, ax = _base(titulo)
    for c, col in zip(cats, colores):
        g[g[columna] == c].plot(ax=ax, color=col, edgecolor="white", linewidth=0.3)
    sin = g[g[columna].isna()]
    if len(sin):
        sin.plot(ax=ax, **{k: v for k, v in SIN_DATOS.items() if k != "label"})
    handles = [Patch(color=col, label=c) for c, col in zip(cats, colores)]
    if len(sin):
        handles.append(Patch(facecolor=SIN_DATOS["color"], hatch="///", label="Sin datos"))
    ax.legend(handles=handles, title="Clase", loc="lower right", fontsize=8)
    _pie(fig, fuente, "categorías de la fuente")
    return _guardar(fig, nombre)


# ------------------------------------------------------------------ bivariado

# Paleta bivariada 3x3 (Stevens): filas = clase de Y (desempeño), columnas = clase de X (joven)
PALETA_BIV = [["#e8e8e8", "#ace4e4", "#5ac8c8"],
              ["#dfb0d6", "#a5add3", "#5698b9"],
              ["#be64ac", "#8c62aa", "#3b4994"]]


def bivariado(gdf: gpd.GeoDataFrame, x: str, y: str, titulo: str, etiqueta_x: str, etiqueta_y: str,
              fuente: str, nombre: str):
    """Mapa bivariado 3x3 por terciles de x e y."""
    g = gdf.to_crs(CRS_AREAS).copy()
    ok = g[x].notna() & g[y].notna()
    cx = mapclassify.Quantiles(g.loc[ok, x], k=3)
    cy = mapclassify.Quantiles(g.loc[ok, y], k=3)
    g.loc[ok, "_cx"], g.loc[ok, "_cy"] = cx.yb, cy.yb
    g["_color"] = None
    g.loc[ok, "_color"] = [PALETA_BIV[int(j)][int(i)] for i, j in zip(g.loc[ok, "_cx"], g.loc[ok, "_cy"])]

    fig, ax = _base(titulo)
    g[ok].plot(ax=ax, color=g.loc[ok, "_color"].tolist(), edgecolor="white", linewidth=0.3)
    if (~ok).any():
        g[~ok].plot(ax=ax, **{k: v for k, v in SIN_DATOS.items() if k != "label"})

    ley = fig.add_axes([0.70, 0.12, 0.18, 0.18])
    for j in range(3):
        for i in range(3):
            ley.add_patch(plt.Rectangle((i, j), 1, 1, color=PALETA_BIV[j][i]))
    ley.set_xlim(0, 3)
    ley.set_ylim(0, 3)
    ley.set_xticks([0.5, 1.5, 2.5], ["bajo", "medio", "alto"], fontsize=7)
    ley.set_yticks([0.5, 1.5, 2.5], ["bajo", "medio", "alto"], fontsize=7)
    ley.set_xlabel(f"{etiqueta_x} →", fontsize=8)
    ley.set_ylabel(f"{etiqueta_y} →", fontsize=8)
    ley.tick_params(length=0)
    for s in ley.spines.values():
        s.set_visible(False)

    cortes_x = ", ".join(f"{v:.1f}" for v in cx.bins[:2])
    cortes_y = ", ".join(f"{v:.1f}" for v in cy.bins[:2])
    _pie(fig, fuente, f"terciles; cortes {etiqueta_x}: {cortes_x}; {etiqueta_y}: {cortes_y}; "
                      f"{int(ok.sum())} municipios con ambos datos")
    return _guardar(fig, nombre)


def lado_a_lado(gdf: gpd.GeoDataFrame, columnas: list[tuple[str, str, str]], titulo: str, fuente: str,
                nombre: str, k: int = 5):
    """Mapas comparados en paneles: columnas = [(columna, subtítulo, unidad), ...]."""
    g = gdf.to_crs(CRS_AREAS)
    fig, axes = plt.subplots(1, len(columnas), figsize=(7 * len(columnas), 7.5))
    for ax, (col, sub, unidad) in zip(np.atleast_1d(axes), columnas):
        ax.set_axis_off()
        ax.set_title(sub)
        g.plot(column=col, ax=ax, scheme="Quantiles", k=k, cmap="YlGnBu", edgecolor="white", linewidth=0.3,
               legend=True, missing_kwds=SIN_DATOS,
               legend_kwds={"title": unidad, "loc": "lower right", "fontsize": 8, "fmt": "{:,.1f}"})
    fig.suptitle(titulo, fontsize=13)
    _pie(fig, fuente, f"cuantiles con {k} clases en cada panel")
    return _guardar(fig, nombre)
