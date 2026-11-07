"""Fase 1: staging -> bronze.

- CSV: se copian byte a byte (sin modificar).
- GeoJSON: se exportan a CSV con columna `geometry_wkt` (requisito del enunciado).
- Se escribe un manifiesto por fuente y uno general con URL, fecha, hash, tamaño,
  codificación, filas, columnas y CRS.
Uso:  python -m src.ingesta_bronze
"""
import hashlib, json, shutil, sys
from datetime import datetime, timezone

import geopandas as gpd
import polars as pl

from src.config import BRONZE, STAGING, FUENTES


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def encoding(path):
    raw = path.read_bytes()[:200_000]
    try:
        raw.decode("utf-8")
        return "utf-8-sig" if raw.startswith(b"\xef\xbb\xbf") else "utf-8"
    except UnicodeDecodeError:
        return "latin-1 (verificar)"


def ingerir(nombre, archivo, tipo, entidad, url, crs):
    origen = STAGING / archivo
    if not origen.exists():
        raise FileNotFoundError(f"[{nombre}] falta {origen}")
    destino_dir = BRONZE / nombre
    destino_dir.mkdir(parents=True, exist_ok=True)
    destino = destino_dir / f"{nombre}.csv"

    pasos = []
    if tipo == "csv":
        shutil.copyfile(origen, destino)
        pasos.append("copia sin modificar")
    else:
        g = gpd.read_file(origen)
        if g.crs is None:
            g = g.set_crs(crs)
            pasos.append(f"CRS no declarado en el original; se asigna {crs} (coordenadas en grados)")
        df = g.drop(columns="geometry").assign(geometry_wkt=g.geometry.to_wkt())
        df.to_csv(destino, index=False, encoding="utf-8")
        pasos.append("GeoJSON -> CSV con geometría en WKT (columna geometry_wkt)")

    df = pl.read_csv(destino, infer_schema_length=0)  # todo como texto: bronze no tipa
    m = {
        "fuente": nombre,
        "entidad": entidad,
        "url": url,
        "archivo_original": archivo,
        "sha256_original": sha256(origen),
        "archivo_bronze": str(destino.relative_to(BRONZE.parents[1])),
        "sha256_bronze": sha256(destino),
        "tamano_bytes": destino.stat().st_size,
        "codificacion": encoding(destino),
        "filas": df.height,
        "columnas": df.width,
        "esquema_observado": df.columns,
        "filas_duplicadas_exactas": int(df.is_duplicated().sum()),
        "celdas_vacias": int(sum(df[c].null_count() for c in df.columns)),
        "crs": crs,
        "pasos_conversion": pasos,
        "fecha_ingesta_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "fecha_descarga": "COMPLETAR (fecha en que se descargó del portal)",
    }
    (destino_dir / "manifest.json").write_text(json.dumps(m, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[ok] {nombre}: {m['filas']} filas, {m['columnas']} columnas")
    return m


def main():
    manifiestos, errores = [], []
    for nombre, args in FUENTES.items():
        try:
            manifiestos.append(ingerir(nombre, *args))
        except Exception as e:  # se registra y se sigue; el resumen lo reporta
            errores.append({"fuente": nombre, "error": str(e)})
            print(f"[ERROR] {nombre}: {e}", file=sys.stderr)
    (BRONZE / "manifest_bronze.json").write_text(
        json.dumps({"fuentes": manifiestos, "errores": errores}, ensure_ascii=False, indent=2), encoding="utf-8")
    if errores:
        sys.exit(1)


if __name__ == "__main__":
    main()
