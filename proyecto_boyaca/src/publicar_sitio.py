"""Genera el sitio estático de resultados para GitHub Pages. Dueño: P6.

    python -m src.publicar_sitio        # después de ./run_pipeline.sh

Escribe site/index.html, site/img/*.png y site/.nojekyll. Todas las cifras salen de
src/resumen.py, las mismas que usa docs/informe_final.md. No ejecuta ningún análisis.
"""
from __future__ import annotations

import html
import shutil
from datetime import datetime

import polars as pl

from src.config import ANIO_EVA, ANIO_MDM, FIGURES, MAPS, ROOT
from src.resumen import cargar, conclusion_principal, ic, n0, n1, pv, respuestas

SITE = ROOT / "site"

TITULOS = {
    "p1_piramide": ("Población por edad y sexo", "P1"),
    "p1_distribucion_rural": ("Población rural por municipio", "P1"),
    "p2_produccion_rendimiento_cultivos": ("Producción y rendimiento por cultivo", "P2"),
    "p2_produccion_por_1000": ("Producción por 1.000 habitantes de 18–64 años", "P2"),
    "p4_distribucion_clases": ("Clases de capacidad de uso de las tierras", "P4"),
    "p5_dispersion_joven_mdm": ("Población joven vs desempeño municipal", "P5"),
    "p5_dispersion_produccion_poblacion": ("Producción vs población de 18–64 años", "P5"),
    "m1_poblacion_joven": ("Población de 18–44 años", "P3"),
    "m2_desempeno": ("Desempeño municipal (MDM)", "P3"),
    "m3_rendimiento_papa": ("Rendimiento de papa", "P3"),
    "m4_produccion_por_1000": ("Producción por 1.000 habitantes", "P3"),
    "m5_clase_predominante": ("Clase de suelo predominante", "P3"),
    "m6_bivariado_joven_mdm": ("Bivariado: joven × desempeño", "P3"),
    "m7_lado_a_lado": ("Lado a lado: joven y desempeño", "P3"),
}


def _e(x) -> str:
    return html.escape("" if x is None else str(x))


def _tabla(df: pl.DataFrame, cols: list[str], enc: list[str], fmt: dict | None = None, num: set | None = None) -> str:
    fmt, num = fmt or {}, num or set()
    cab = "".join(f'<th{" class=n" if c in num else ""}>{_e(h)}</th>' for c, h in zip(cols, enc))
    filas = []
    for row in df.select(cols).iter_rows(named=True):
        celdas = "".join(f'<td{" class=n" if c in num else ""}>{_e(fmt[c](row[c]) if c in fmt else row[c])}</td>' for c in cols)
        filas.append(f"<tr>{celdas}</tr>")
    return f'<div class="tabla"><table><thead><tr>{cab}</tr></thead><tbody>{"".join(filas)}</tbody></table></div>'


# ------------------------------------------------------------------ diagrama de arquitectura (SVG)

def _caja(x, y, w, h, clase, titulo, lineas=(), quien=""):
    t = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" class="{clase}"/>',
         f'<text x="{x + 12}" y="{y + 22}" class="t-tit">{_e(titulo)}</text>']
    if quien:
        t.append(f'<text x="{x + w - 10}" y="{y + 22}" class="t-quien" text-anchor="end">{_e(quien)}</text>')
    for i, l in enumerate(lineas):
        t.append(f'<text x="{x + 12}" y="{y + 42 + i * 17}" class="t-lin">{_e(l)}</text>')
    return "".join(t)


def _flecha(x1, y1, x2, y2):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="flecha" marker-end="url(#punta)"/>'


def arquitectura_svg(f: dict) -> str:
    p = []
    cols = [(20, "FUENTES", "c-src"), (232, "BRONZE", "c-bro"), (444, "SILVER", "c-sil"),
            (716, "GOLD", "c-gol"), (938, "SALIDAS", "c-out")]
    for x, nombre, cl in cols:
        p.append(f'<text x="{x}" y="26" class="t-capa {cl}-t">{nombre}</text>')

    fuentes = [("EVA · UPRA", f"{ANIO_EVA} · 2.613 filas"), ("MDM · DNP", f"{ANIO_MDM} · 246 filas"),
               ("Población · DANE", "2020–2025 · 738"), ("Población por área", "2020–2024 · 1.845"),
               ("MGN · DANE", "2025 · 123 polígonos"), ("Suelo · IGAC", "2004 · 958 polígonos")]
    for i, (a, b) in enumerate(fuentes):
        p.append(_caja(20, 44 + i * 56, 176, 48, "b-src", a, [b]))

    p.append(_caja(232, 44, 176, 328, "b-bro", "01 Ingesta", [
        "", "6 CSV sin modificar", "GeoJSON → CSV con WKT", "", "manifiesto por fuente:", "URL, SHA-256, filas,", "columnas, CRS", "",
        "diagnóstico por columna", "(antes de limpiar)"], "P6"))

    silver = [("02 Población", "P1", ["poblacion · 738", "poblacion_area · 211.560"]),
              ("03 Desempeño", "P1", ["2 bloques A / B", "código vs nombre DANE"]),
              ("04 Agrícola", "P2", ["agricola · 2.613", "373 alertas conservadas"]),
              ("05 Geo y suelo", "P3·P4", ["municipios · 123", "capacidad_uso · 958"])]
    for i, (t, q, l) in enumerate(silver):
        p.append(_caja(444, 44 + i * 84, 236, 74, "b-sil", t, l, q))

    p.append(_caja(716, 44, 186, 160, "b-gol", "06 Integración", [
        "LEFT JOIN código + año", "municipio_anio · 738", "maestro (geo) · 123", "", "detiene si duplica filas", "o cambia la población"], "P6"))
    p.append(_caja(716, 214, 186, 158, "b-gol", "Tablas analíticas", [
        "cultivo_municipio", "suelo_municipio (overlay", "  en EPSG:9377)", "", "indicadores: % 18–44,", "% 18–64, prod./1.000 hab."], ""))

    salidas = [("07 Estadística", "P5", [f"r = {n1(f['h_sp']['r'], 2)}, p = {pv(f['h_sp']['p'])}"]),
               ("08 Mapas", "P3", ["7 mapas municipales"]),
               ("Informe", "P6", ["docs/informe_final.md"]),
               ("Este sitio", "P6", ["GitHub Pages"])]
    for i, (t, q, l) in enumerate(salidas):
        p.append(_caja(938, 44 + i * 84, 176, 74, "b-out", t, l, q))

    for y in (68, 124, 180, 236, 292, 348):
        p.append(_flecha(196, y, 230, min(max(y, 120), 300)))
    for y in (81, 165, 249, 333):
        p.append(_flecha(408, 208, 442, y))
    for y in (81, 165, 249, 333):
        p.append(_flecha(680, y, 714, 124 if y < 200 else 293))
    for y in (81, 165):
        p.append(_flecha(902, 124, 936, y))
    for y in (249, 333):
        p.append(_flecha(902, 293, 936, y))

    p.append('<rect x="20" y="396" width="1094" height="64" rx="8" class="b-trans"/>')
    trans = [("calidad.py", "rechazar · alertar · detener"),
             ("contratos.py", "esquema y clave por tabla"),
             ("tests/", "26 pruebas pytest"),
             ("run_pipeline.sh", "01 → 08 en orden + pruebas")]
    for i, (a, b) in enumerate(trans):
        x = 36 + i * 272
        p.append(f'<text x="{x}" y="421" class="t-tit">{_e(a)}</text><text x="{x}" y="442" class="t-lin">{_e(b)}</text>')

    return ('<svg viewBox="0 0 1134 472" role="img" aria-label="Arquitectura medallón del pipeline" class="arq">'
            '<defs><marker id="punta" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto">'
            '<path d="M0,0 L10,5 L0,10 z" class="punta"/></marker></defs>' + "".join(p) + "</svg>")


# ------------------------------------------------------------------ galería

def _galeria(carpeta, prefijo: str) -> str:
    imgs = sorted(carpeta.glob("*.png")) if carpeta.exists() else []
    if not imgs:
        return '<p class="pendiente">Sin imágenes: ejecute <code>bash run_pipeline.sh</code>.</p>'
    destino = SITE / "img"
    destino.mkdir(parents=True, exist_ok=True)
    tarjetas = []
    for img in imgs:
        nombre = f"{prefijo}_{img.name}"
        shutil.copy2(img, destino / nombre)
        clave = next((k for k in TITULOS if img.stem.startswith(k)), None)
        titulo, quien = TITULOS.get(clave, (img.stem.replace("_", " "), ""))
        tarjetas.append(f'<figure><a href="img/{_e(nombre)}" target="_blank" rel="noopener">'
                        f'<img src="img/{_e(nombre)}" alt="{_e(titulo)}" loading="lazy"></a>'
                        f'<figcaption><span>{_e(titulo)}</span><span class="quien">{_e(quien)}</span></figcaption></figure>')
    return f'<div class="galeria">{"".join(tarjetas)}</div>'


# ------------------------------------------------------------------ estilos

CSS = """
/* Layout: columna de lectura de 1120px; bandas por sección; diagrama SVG con scroll propio en pantallas chicas */
:root{
  --bg:#f5f4ee; --surface:#ffffff; --ink:#1c2620; --muted:#5a665e; --line:#dcdcd2;
  --accent:#2d6a4f; --accent-soft:#e3efe7;
  --src:#eef0f3; --src-s:#8a94a3;
  --bro:#f4e3d2; --bro-s:#a0612b; --sil:#e6e9ef; --sil-s:#5f6f86; --gol:#f6ecc9; --gol-s:#9c7a14;
  --out:#e3efe7; --out-s:#2d6a4f; --trans:#f0eee6;
  --ok:#2d6a4f; --warn:#9a5b13;
  --f-ui:"IBM Plex Sans",system-ui,-apple-system,"Segoe UI",sans-serif;
  --f-mono:"IBM Plex Mono",ui-monospace,Menlo,Consolas,monospace;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --bg:#121815; --surface:#19211d; --ink:#e4ebe6; --muted:#9fb0a6; --line:#2b3631;
  --accent:#7cc39d; --accent-soft:#1d2e25;
  --src:#1f252b; --src-s:#7d8794; --bro:#2e2218; --bro-s:#d39a63; --sil:#20252e; --sil-s:#93a3ba; --gol:#2c2715; --gol-s:#d6b54a;
  --out:#1d2e25; --out-s:#7cc39d; --trans:#1b211e; --ok:#7cc39d; --warn:#e0a85a; color-scheme:dark}}
:root[data-theme="dark"]{
  --bg:#121815; --surface:#19211d; --ink:#e4ebe6; --muted:#9fb0a6; --line:#2b3631;
  --accent:#7cc39d; --accent-soft:#1d2e25;
  --src:#1f252b; --src-s:#7d8794; --bro:#2e2218; --bro-s:#d39a63; --sil:#20252e; --sil-s:#93a3ba; --gol:#2c2715; --gol-s:#d6b54a;
  --out:#1d2e25; --out-s:#7cc39d; --trans:#1b211e; --ok:#7cc39d; --warn:#e0a85a; color-scheme:dark}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.55 var(--f-ui)}
.envoltura{max-width:1120px;margin:0 auto;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}
header{padding-block:44px 28px;border-bottom:1px solid var(--line)}
.eyebrow{font:600 .78rem/1 var(--f-mono);letter-spacing:.08em;text-transform:uppercase;color:var(--accent);margin:0 0 12px}
h1{font-size:clamp(1.7rem,4vw,2.4rem);line-height:1.15;margin:0 0 14px;text-wrap:balance;max-width:24ch}
.tesis{font-size:1.06rem;max-width:72ch;margin:0;color:var(--ink)}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin-top:24px}
.kpi{background:var(--surface);border:1px solid var(--line);border-radius:8px;padding:12px 14px}
.kpi b{display:block;font:600 1.45rem/1.2 var(--f-mono);font-variant-numeric:tabular-nums}
.kpi span{font-size:.84rem;color:var(--muted)}
.kpi.alerta b{color:var(--warn)}
nav{display:flex;flex-wrap:wrap;gap:6px 16px;margin-top:22px;font-size:.92rem}
nav a{color:var(--accent);text-decoration:none}nav a:hover{text-decoration:underline}
section{padding-block:36px;border-bottom:1px solid var(--line)}
h2{font-size:1.4rem;margin:0 0 6px;text-wrap:balance}
.lead{color:var(--muted);margin:0 0 20px;max-width:75ch}
h3{font-size:1.02rem;margin:26px 0 10px}
.diagrama{overflow-x:auto;background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:14px}
.arq{display:block;min-width:900px;width:100%;height:auto}
.arq .t-capa{font:600 12px var(--f-mono);letter-spacing:.1em}
.arq .t-tit{font:600 14px var(--f-ui);fill:var(--ink)}
.arq .t-lin{font:12.5px var(--f-ui);fill:var(--muted)}
.arq .t-quien{font:600 11px var(--f-mono);fill:var(--muted)}
.arq .b-src{fill:var(--src);stroke:var(--src-s)} .arq .c-src-t{fill:var(--src-s)}
.arq .b-bro{fill:var(--bro);stroke:var(--bro-s)} .arq .c-bro-t{fill:var(--bro-s)}
.arq .b-sil{fill:var(--sil);stroke:var(--sil-s)} .arq .c-sil-t{fill:var(--sil-s)}
.arq .b-gol{fill:var(--gol);stroke:var(--gol-s)} .arq .c-gol-t{fill:var(--gol-s)}
.arq .b-out{fill:var(--out);stroke:var(--out-s)} .arq .c-out-t{fill:var(--out-s)}
.arq .b-trans{fill:var(--trans);stroke:var(--line);stroke-dasharray:5 4}
.arq rect{stroke-width:1.4}
.arq .flecha{stroke:var(--muted);stroke-width:1.4}.arq .punta{fill:var(--muted)}
.respuestas{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:14px}
.resp{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:16px 18px;min-width:0}
.resp .num{font:600 .78rem var(--f-mono);color:var(--accent)}
.resp h3{margin:4px 0 8px;font-size:1rem}
.resp p{margin:0 0 10px;font-size:.95rem}
.resp .ev{font-size:.82rem;color:var(--muted);margin:0}
.conclusion{background:var(--accent-soft);border-left:4px solid var(--accent);padding:14px 18px;border-radius:0 8px 8px 0;max-width:85ch}
.tabla{overflow-x:auto;border:1px solid var(--line);border-radius:8px;background:var(--surface)}
table{border-collapse:collapse;width:100%;font-size:.88rem}
th,td{padding:8px 11px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}
th{font-weight:600;background:color-mix(in srgb,var(--line) 40%,transparent)}
td.n,th.n{text-align:right;font-variant-numeric:tabular-nums;font-family:var(--f-mono);font-size:.84rem;white-space:nowrap}
tbody tr:last-child td{border-bottom:0}
.galeria{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:16px}
figure{margin:0;background:var(--surface);border:1px solid var(--line);border-radius:8px;padding:10px;min-width:0}
figure img{width:100%;height:auto;display:block;border-radius:4px;background:#fff}
figcaption{display:flex;justify-content:space-between;gap:8px;font-size:.88rem;color:var(--muted);margin-top:8px}
.quien{font:600 .75rem var(--f-mono)}
ul.lim{max-width:80ch;padding-left:20px}ul.lim li{margin-bottom:6px}
pre{background:var(--surface);border:1px solid var(--line);border-radius:8px;padding:12px 14px;overflow-x:auto;font:.85rem/1.5 var(--f-mono)}
.pendiente{color:var(--warn)}
code{font-family:var(--f-mono);font-size:.9em}
footer{color:var(--muted);font-size:.85rem;padding-block:24px 48px}
a:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
"""


# ------------------------------------------------------------------ página

def generar() -> None:
    r = cargar()
    f = r.f
    if SITE.exists():
        shutil.rmtree(SITE)
    SITE.mkdir(parents=True)
    (SITE / ".nojekyll").write_text("", encoding="utf-8")
    sp, rc = f["h_sp"], f["reg_ctrl"]

    kpis = [(n0(f["n_municipios"]), "municipios integrados"), ("6", "fuentes públicas"),
            (n0(f["rechazados"]), "filas rechazadas"), (n1(sp["r"], 2), f"Spearman, p = {pv(sp['p'])}"),
            (pv(rc["p"]), "p con controles", "alerta" if rc["p"] >= 0.05 else "")]
    kpi_html = "".join(f'<div class="kpi {k[2] if len(k) > 2 else ""}"><b>{_e(k[0])}</b><span>{_e(k[1])}</span></div>' for k in kpis)

    resp_html = "".join(
        f'<article class="resp"><div class="num">PREGUNTA {q["n"]}</div><h3>{_e(q["pregunta"])}</h3>'
        f'<p>{_e(q["respuesta"])}</p><p class="ev">Evidencia: {_e(q["evidencia"])}</p></article>' for q in respuestas(f))

    hip = r.tablas["hipotesis"]
    t_hip = _tabla(hip, ["tipo", "analisis", "metodo", "n", "r", "ic95_inf", "ic95_sup", "p", "p_holm", "conclusion"],
                   ["Tipo", "Análisis", "Método", "n", "r", "IC 95 % inf.", "IC 95 % sup.", "p", "p (Holm)", "Conclusión"],
                   {"r": lambda x: n1(x, 3), "ic95_inf": lambda x: n1(x, 3), "ic95_sup": lambda x: n1(x, 3),
                    "p": pv, "p_holm": lambda x: pv(x) if x is not None else "—"},
                   {"n", "r", "ic95_inf", "ic95_sup", "p", "p_holm"})
    t_ctrl = _tabla(r.tablas["reg_ctrl"], ["termino", "coef", "ic95_inf", "ic95_sup", "p"],
                    ["Término", "Coeficiente", "IC 95 % inf.", "IC 95 % sup.", "p"],
                    {"coef": lambda x: n1(x, 3), "ic95_inf": lambda x: n1(x, 3), "ic95_sup": lambda x: n1(x, 3), "p": pv},
                    {"coef", "ic95_inf", "ic95_sup", "p"})
    t_grupos = _tabla(r.tablas["grupos"], ["grupo_capacidad", "municipios", "mdm_medio", "joven_medio"],
                      ["Grupo de capacidades", "Municipios", "MDM medio", "% 18–44 medio"],
                      {"mdm_medio": n1, "joven_medio": n1}, {"municipios", "mdm_medio", "joven_medio"})

    cal = r.tablas["calidad"]
    t_cal_res = _tabla(pl.DataFrame([{"capa": c, "reglas": v["reglas"], "ok": v["ok"], "fallas": v["fallas"].height} for c, v in cal.items()]),
                       ["capa", "reglas", "ok", "fallas"], ["Capa", "Reglas evaluadas", "OK", "Con hallazgos"], num={"reglas", "ok", "fallas"})
    hall = pl.concat([v["fallas"].with_columns(capa=pl.lit(c)) for c, v in cal.items() if v["fallas"].height])
    t_hall = _tabla(hall, ["capa", "fuente", "regla", "descripcion", "revisados", "afectados", "accion_si_falla"],
                    ["Capa", "Fuente", "Regla", "Qué revisa", "Revisados", "Afectados", "Acción si falla"],
                    num={"revisados", "afectados"})

    secciones = [
        ("arquitectura", "Arquitectura del pipeline",
         "<p class=\"lead\">Arquitectura medallón: cada capa es más confiable que la anterior y todo se regenera desde bronze con un comando. "
         "Los recuadros son los notebooks que orquestan cada paso; la banda inferior son los componentes que atraviesan todas las capas.</p>"
         f'<div class="diagrama">{arquitectura_svg(f)}</div>'),
        ("respuestas", "Respuestas a las preguntas de investigación",
         f'<p class="conclusion">{_e(conclusion_principal(f))}</p><h3>Las seis preguntas</h3><div class="respuestas">{resp_html}</div>'),
        ("hipotesis", "Hipótesis, sensibilidad y controles",
         f"<p class=\"lead\">Hipótesis principal en {ANIO_MDM}, unilateral, α = 0,05 fijado antes de ver los datos. "
         f"Las complementarias ({ANIO_EVA}) son exploratorias y su p se ajusta por Holm.</p>{t_hip}"
         f"<h3>Regresión con controles (n = {f['reg_ctrl_meta']['n']}, R² ajustado = {n1(f['reg_ctrl_meta']['r2_ajustado'], 3)})</h3>"
         f"<p class=\"lead\">El coeficiente de la población joven pasa de {n1(f['reg_simple']['coef'], 2)} (p = {pv(f['reg_simple']['p'])}) "
         f"a {n1(rc['coef'], 2)} (IC {ic(rc['ic95_inf'], rc['ic95_sup'])}, p = {pv(rc['p'])}). El grupo base es G1.</p>{t_ctrl}"
         f"<h3>Grupos de capacidades iniciales del DNP</h3><p class=\"lead\">Los municipios G1 tienen a la vez más población joven y mejor desempeño: "
         f"por eso el efecto se diluye al controlar por grupo.</p>{t_grupos}"),
        ("calidad", "Calidad de datos por capa",
         f"<p class=\"lead\">Cada regla tiene una acción si falla: <b>rechazar</b> (la fila va a la zona de rechazos), <b>alertar</b> "
         f"(se conserva y se anota) o <b>detener</b> (el pipeline se para). Filas rechazadas en total: <b>{n0(f['rechazados'])}</b>. "
         f"Todos los hallazgos son anomalías documentadas, no datos perdidos.</p>{t_cal_res}<h3>Hallazgos</h3>{t_hall}"),
        ("figuras", "Gráficos", _galeria(FIGURES, "fig")),
        ("mapas", "Mapas municipales", "<p class=\"lead\">Cortes por cuantiles; municipios sin dato en gris con trama; proyección EPSG:9377.</p>"
         + _galeria(MAPS, "map")),
        ("limitaciones", "Limitaciones",
         "<ul class=\"lim\">"
         "<li>Asociaciones entre municipios en un solo año: no demuestran causalidad ni miden disposición al cambio.</li>"
         "<li>Con controles, el efecto de la población joven deja de ser significativo.</li>"
         f"<li>No hay año común: desempeño {ANIO_MDM}, producción {ANIO_EVA}.</li>"
         "<li>La población es una proyección del DANE y las dos fuentes difieren.</li>"
         f"<li>El MDM publica dos bloques para la misma vigencia (correlación {n1(f['bloques_corr'], 2)} entre ellos); el resultado se mantiene con ambos.</li>"
         "<li>El mapa del IGAC es de 2004 a escala 1:100.000: capacidad de uso, no fertilidad actual.</li>"
         "<li>La producción total suma toneladas no comparables; en municipios cañeros domina el indicador por habitante.</li></ul>"),
        ("reproducir", "Cómo reproducirlo",
         "<pre>python -m venv .venv &amp;&amp; source .venv/bin/activate\npip install -r requirements.txt\n"
         "bash run_pipeline.sh            # notebooks 01-08 + 26 pruebas\npython -m src.generar_informe    # docs/informe_final.md\n"
         "python -m src.publicar_sitio     # este sitio</pre>"),
    ]
    nav = "".join(f'<a href="#{i}">{_e(t)}</a>' for i, t, _ in secciones)
    cuerpo = "".join(f'<section id="{i}"><div class="envoltura"><h2>{_e(t)}</h2>{c}</div></section>' for i, t, c in secciones)

    pagina = f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Proyecto Boyacá · Resultados</title>
<meta name="description" content="Población, producción agrícola, suelo y desempeño de los 123 municipios de Boyacá">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@400;600&display=swap">
<style>{CSS}</style></head><body>
<header><div class="envoltura">
<p class="eyebrow">Proyecto final · Electiva Big Data · Boyacá</p>
<h1>¿Más población joven, mejor desempeño municipal?</h1>
<p class="tesis">{_e(conclusion_principal(f))}</p>
<div class="kpis">{kpi_html}</div>
<nav>{nav}</nav></div></header>
<main>{cuerpo}</main>
<footer><div class="envoltura">Fuentes: DANE, DNP, UPRA e IGAC vía datos.gov.co. Generado el {datetime.now().strftime('%Y-%m-%d %H:%M')}
con <code>python -m src.publicar_sitio</code> a partir de las salidas del pipeline.</div></footer>
</body></html>"""
    (SITE / "index.html").write_text(pagina, encoding="utf-8")
    print(f"Sitio generado en {SITE / 'index.html'}")


if __name__ == "__main__":
    generar()
