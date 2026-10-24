"""Descarga y verifica los seis cortes completos PQRS de 2023 a 2025."""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import shutil
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parent
PARSER = argparse.ArgumentParser(description=__doc__)
PARSER.add_argument('--listar', action='store_true')
PARSER.add_argument('--descargar', nargs='+', metavar='CORTE')
PARSER.add_argument('--verificar', nargs='*', metavar='CORTE', help='Sin cortes: verifica los seis; también admite una selección')
PARSER.add_argument('--datos', type=Path, default=ROOT/'data/pqrs_completos')
ARGS = PARSER.parse_args()

ARGS.datos = ARGS.datos.expanduser()
if not ARGS.datos.is_absolute():
    ARGS.datos = ROOT/ARGS.datos

FUENTES = (
    json.loads((ROOT/'pqrs_fuentes.json').read_text(encoding='utf-8'))
    + json.loads((ROOT/'pqrs_fuentes_adicionales_2023_2025.json').read_text(encoding='utf-8'))
)
FUENTES.sort(key=lambda fuente: fuente['periodo'])
ARGS.datos.mkdir(parents=True, exist_ok=True)


def sha256_archivo(path):
    huella = hashlib.sha256()
    with path.open('rb') as stream:
        for bloque in iter(lambda: stream.read(1024*1024), b''):
            huella.update(bloque)
    return huella.hexdigest()


def destino_csv(fuente):
    return ARGS.datos/fuente['archivo']


def destino_descarga(fuente):
    if fuente.get('contenedor') == 'zip':
        return ARGS.datos/'originales'/fuente['archivo_descarga']
    return destino_csv(fuente)


def descargar(fuente):
    csv_destino = destino_csv(fuente)
    if csv_destino.exists():
        if (csv_destino.stat().st_size == fuente['bytes'] and
                sha256_archivo(csv_destino) == fuente['sha256']):
            print('Ya existe y coincide:', csv_destino.name)
            return
        raise RuntimeError(f'No se sobrescribe una versión distinta: {csv_destino}')

    descarga = destino_descarga(fuente)
    descarga.parent.mkdir(parents=True, exist_ok=True)
    bytes_descarga = fuente.get('bytes_descarga', fuente['bytes'])
    sha_descarga = fuente.get('sha256_descarga', fuente['sha256'])

    if descarga.exists():
        if descarga.stat().st_size != bytes_descarga or sha256_archivo(descarga) != sha_descarga:
            raise RuntimeError(f'La fuente descargada no coincide: {descarga}')
        print('Fuente ya descargada y verificada:', descarga.name)
    else:
        temporal = descarga.with_suffix(descarga.suffix+'.part')
        limite = max(bytes_descarga*3, 2_000_000)
        try:
            print('Descargando:', fuente['periodo'], fuente['url'], flush=True)
            solicitud = urllib.request.Request(fuente['url'], headers={'User-Agent':'Curso-BigData/1.0'})
            with urllib.request.urlopen(solicitud, timeout=60) as response, temporal.open('wb') as output:
                if 'text/html' in response.headers.get('Content-Type', '').lower():
                    raise ValueError('El servidor entregó HTML en lugar de datos')
                total = 0
                while True:
                    bloque = response.read(1024*1024)
                    if not bloque:
                        break
                    total += len(bloque)
                    if total > limite:
                        raise ValueError('La descarga supera el límite de seguridad')
                    output.write(bloque)
            if temporal.stat().st_size != bytes_descarga or sha256_archivo(temporal) != sha_descarga:
                nueva = descarga.with_suffix(descarga.suffix+'.nueva')
                temporal.replace(nueva)
                raise ValueError(f'La fuente cambió; se conserva en {nueva.name}')
            temporal.replace(descarga)
        except Exception:
            temporal.unlink(missing_ok=True)
            raise

    if fuente.get('contenedor') == 'zip':
        temporal_csv = csv_destino.with_suffix(csv_destino.suffix+'.part')
        try:
            with zipfile.ZipFile(descarga) as archive:
                info = archive.getinfo(fuente['miembro_zip'])
                if info.file_size != fuente['bytes']:
                    raise ValueError('El CSV contenido en el ZIP cambió de tamaño')
                with archive.open(info) as source, temporal_csv.open('wb') as target:
                    shutil.copyfileobj(source, target, length=1024*1024)
            if (temporal_csv.stat().st_size != fuente['bytes'] or
                    sha256_archivo(temporal_csv) != fuente['sha256']):
                nueva = csv_destino.with_suffix(csv_destino.suffix+'.nueva')
                temporal_csv.replace(nueva)
                raise ValueError(f'El CSV extraído cambió; se conserva en {nueva.name}')
            temporal_csv.replace(csv_destino)
        except Exception:
            temporal_csv.unlink(missing_ok=True)
            raise

    print('Preparado:', csv_destino.name)


def verificar(fuente):
    archivo = destino_csv(fuente)
    if not archivo.exists():
        raise RuntimeError(f'Ausente: {archivo}')
    if archivo.stat().st_size != fuente['bytes'] or sha256_archivo(archivo) != fuente['sha256']:
        raise RuntimeError(f'Huella o tamaño distinto: {archivo.name}')
    with archivo.open(encoding=fuente.get('codificacion', 'utf-8-sig'), newline='') as stream:
        lector = csv.reader(stream, delimiter=fuente['separador'])
        cabecera = next(lector, [])
        filas = 0
        anchos_incorrectos = 0
        for fila in lector:
            filas += 1
            anchos_incorrectos += len(fila) != len(cabecera)
    if cabecera != fuente['columnas'] or filas != fuente['filas'] or anchos_incorrectos:
        raise RuntimeError(f'Estructura distinta: {archivo.name}')
    if fuente.get('contenedor') == 'zip':
        descarga = destino_descarga(fuente)
        if not descarga.exists():
            raise RuntimeError(f'Falta conservar el ZIP original: {descarga}')
        if (descarga.stat().st_size != fuente['bytes_descarga'] or
                sha256_archivo(descarga) != fuente['sha256_descarga']):
            raise RuntimeError(f'ZIP original distinto: {descarga.name}')
    print(archivo.name, 'coincide', filas, 'filas')


if ARGS.listar:
    for fuente in FUENTES:
        tipo = 'ZIP→CSV' if fuente.get('contenedor') == 'zip' else 'CSV'
        print(f"{fuente['periodo']:8} {tipo:8} {fuente['bytes']/1e6:9.2f} MB "
              f"{fuente['filas']:>9,} filas  {fuente['url']}")

if ARGS.descargar:
    cortes = {fuente['periodo'] for fuente in FUENTES}
    solicitados = set(ARGS.descargar)
    if 'todos' in solicitados or 'pqrs-completos' in solicitados:
        solicitados = cortes
    desconocidos = solicitados - cortes
    if desconocidos:
        raise SystemExit(f'Cortes no admitidos: {sorted(desconocidos)}; disponibles: {sorted(cortes)}')
    for fuente in FUENTES:
        if fuente['periodo'] in solicitados:
            descargar(fuente)

if ARGS.verificar is not None:
    cortes = {fuente['periodo'] for fuente in FUENTES}
    solicitados = set(ARGS.verificar) or cortes
    desconocidos = solicitados - cortes
    if desconocidos:
        raise SystemExit(f'Cortes no admitidos: {sorted(desconocidos)}; disponibles: {sorted(cortes)}')
    for fuente in FUENTES:
        if fuente['periodo'] in solicitados:
            verificar(fuente)

if not any([ARGS.listar, ARGS.descargar, ARGS.verificar is not None]):
    PARSER.print_help()
