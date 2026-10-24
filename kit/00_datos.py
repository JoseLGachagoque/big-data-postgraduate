"""Descarga o verifica fuentes del curso y PQRS (muestras o completos). Solo biblioteca estándar."""
from pathlib import Path
import argparse, csv, hashlib, json, shutil, urllib.request, zipfile
ROOT = Path(__file__).resolve().parent
RAW = ROOT / 'data' / 'raw'
P = argparse.ArgumentParser(description=__doc__)
P.add_argument('--listar', action='store_true')
P.add_argument('--descargar', nargs='+', metavar='ID')
P.add_argument('--respaldo', type=Path, help='Carpeta raw de una copia del kit')
P.add_argument('--verificar', nargs='*', metavar='ID', help='Sin IDs: 12 fuentes agroambientales; pqrs: tres muestras; pqrs-completos: seis cortes CSV de 2023 a 2025')
args = P.parse_args()
fuentes = json.loads((ROOT/'fuentes.json').read_text(encoding='utf-8'))['fuentes']
muestras = []
completos = []
pqrs_base = json.loads((ROOT/'pqrs_fuentes.json').read_text(encoding='utf-8'))
pqrs_adicionales = json.loads((ROOT/'pqrs_fuentes_adicionales_2023_2025.json').read_text(encoding='utf-8'))
for f in pqrs_base:
    nombre = 'Muestra_1000_' + f['periodo'] + '.csv'
    muestras.append({'id': 'pqrs_' + f['periodo'], 'archivo': nombre,
        'url': 'https://raw.githubusercontent.com/eshernan/big-data-postgraduate/main/kit/data/pqrs_muestras/' + nombre,
        'bytes': f['bytes_muestra'], 'sha256': f['sha256_muestra'],
        'metodo': 'http', 'alcance': 'muestra', 'carpeta': 'pqrs_muestras',
        'separador': f['separador'], 'columnas': f['columnas'], 'filas': f['filas_muestra']})
for f in pqrs_base + pqrs_adicionales:
    item = {'id': 'pqrs_completo_' + f['periodo'], 'archivo': f['archivo'],
        'url': f['url'], 'bytes': f['bytes'], 'sha256': f['sha256'],
        'metodo': 'http', 'alcance': 'completo', 'carpeta': 'pqrs_completos',
        'separador': f['separador'], 'columnas': f['columnas'], 'filas': f['filas'],
        'contenedor': f.get('contenedor', 'csv')}
    for key in ['archivo_descarga', 'miembro_zip', 'bytes_descarga', 'sha256_descarga']:
        if key in f: item[key] = f[key]
    completos.append(item)
completos.sort(key=lambda fuente: fuente['id'])
catalogo = fuentes + muestras + completos

def sha256_archivo(path):
    """Calcula la huella por bloques, sin cargar CSV completos en RAM."""
    huella = hashlib.sha256()
    with path.open('rb') as stream:
        for bloque in iter(lambda: stream.read(1024 * 1024), b''):
            huella.update(bloque)
    return huella.hexdigest()

def sha256_contenido(path, fuente):
    """Normaliza metadatos volátiles cuando la fuente los incorpora."""
    if fuente.get('normalizacion') == 'nasa_power':
        contenido = json.loads(path.read_text(encoding='utf-8'))
        contenido.pop('times', None)
        contenido.get('header', {}).get('api', {}).pop('version', None)
        estable = json.dumps(
            contenido, ensure_ascii=False, sort_keys=True, separators=(',', ':')
        ).encode('utf-8')
        return hashlib.sha256(estable).hexdigest()
    return sha256_archivo(path)

def coincide_fuente(path, fuente):
    """Compara bytes exactos o contenido normalizado, según la fuente."""
    esperado = fuente.get('sha256_contenido', fuente['sha256'])
    return sha256_contenido(path, fuente) == esperado

def seleccionar(ids):
    conocidos = {f['id'] for f in catalogo} | {'pqrs', 'pqrs-completos'}
    desconocidos = set(ids) - conocidos
    if desconocidos: P.error(f'IDs desconocidos: {sorted(desconocidos)}')
    elegidos = set(ids)
    if 'pqrs' in elegidos: elegidos.update(f['id'] for f in muestras)
    if 'pqrs-completos' in elegidos: elegidos.update(f['id'] for f in completos)
    return [f for f in catalogo if f['id'] in elegidos]

def destino(f):
    return ROOT/'data'/f.get('carpeta', 'raw')/f['archivo']

def destino_descarga(f):
    if f.get('contenedor') == 'zip':
        return destino(f).parent/'originales'/f['archivo_descarga']
    return destino(f)

seleccion_descarga = seleccionar(args.descargar) if args.descargar else []
seleccion_verificacion = seleccionar(args.verificar) if args.verificar else fuentes
fallos_descarga = []
RAW.mkdir(parents=True, exist_ok=True)
if args.listar:
    print('pqrs: grupo de tres muestras (3.000 filas), destino data/pqrs_muestras; no descarga completos')
    print(f"pqrs-completos: {len(completos)} cortes completos de 2023 a 2025, "
          f"{sum(f['filas'] for f in completos):,} reportes, "
          f"{sum(f['bytes'] for f in completos)/1e9:.3f} GB descomprimidos; destino data/pqrs_completos")
    for f in catalogo:
        print(f"{f['id']:20} {f['bytes']/1e6:8.3f} MB  {f['alcance']:8} {f['metodo']}")
if args.respaldo:
    for f in fuentes:
        src = args.respaldo/f['archivo']; dst = RAW/f['archivo']
        if src.resolve() == dst.resolve(): continue
        if not src.exists(): raise SystemExit(f'Falta {src}')
        if not coincide_fuente(src, f):
            raise SystemExit(f'El respaldo no coincide con la versión docente: {src}')
        if dst.exists():
            if not coincide_fuente(dst, f):
                raise SystemExit(f'No se sobrescribe una versión diferente: {dst}')
        else: shutil.copy2(src, dst)
if args.descargar:
    for f in seleccion_descarga:
        dst = destino(f)
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.exists():
            if not coincide_fuente(dst, f):
                fallos_descarga.append(f['id'])
                print(f"Versión distinta: {dst}. No se sobrescribe; revisar o conservar aparte antes de descargar.")
            else:
                archive = destino_descarga(f)
                archive_ok = (f.get('contenedor') != 'zip' or
                              (archive.exists() and archive.stat().st_size == f['bytes_descarga'] and
                               sha256_archivo(archive) == f['sha256_descarga']))
                if archive_ok:
                    print(f"Ya existe y coincide: {dst.name}. No se descarga ni sobrescribe.")
                    continue
                print(f"El CSV coincide, pero falta recuperar su fuente comprimida: {archive}")
            if f['id'] in fallos_descarga: continue
        if f['metodo'] == 'manual':
            print(f"Descarga DANE mediante navegador; guardar como {dst}\n{f['url']}"); continue
        download = destino_descarga(f)
        download.parent.mkdir(parents=True, exist_ok=True)
        expected_bytes = f.get('bytes_descarga', f['bytes'])
        expected_sha = f.get('sha256_descarga', f['sha256'])
        temp = download.with_suffix(download.suffix+'.part')
        extracted = dst.with_suffix(dst.suffix+'.part')
        limit = max(expected_bytes*3, 2_000_000)
        try:
            if download.exists():
                if download.stat().st_size != expected_bytes or sha256_archivo(download) != expected_sha:
                    raise ValueError(f'La descarga existente no coincide: {download}')
                print('Fuente ya descargada y verificada:', download.name)
            else:
                print('Descargando:', f['archivo'], f['url'], flush=True)
                req = urllib.request.Request(f['url'], headers={'User-Agent':'Curso-BigData/1.0'})
                with urllib.request.urlopen(req, timeout=60) as response, temp.open('wb') as w:
                    ct = response.headers.get('Content-Type','').lower(); n=0
                    if 'text/html' in ct: raise ValueError('El servidor entregó HTML en lugar de datos')
                    while True:
                        chunk = response.read(1024*1024)
                        if not chunk: break
                        n += len(chunk)
                        if n > limit: raise ValueError(f'Descarga supera el límite docente de {limit/1e6:.1f} MB')
                        w.write(chunk)
                if ('sha256_contenido' not in f and temp.stat().st_size != expected_bytes) or not coincide_fuente(temp, f):
                    changed=download.with_suffix(download.suffix+'.nueva'); temp.replace(changed)
                    raise ValueError(f'La fuente cambió; se conserva en {changed.name}. Revisar esquema y controles antes de sustituir el corte docente.')
                temp.replace(download)
            if f.get('contenedor') == 'zip':
                with zipfile.ZipFile(download) as z:
                    info = z.getinfo(f['miembro_zip'])
                    if info.file_size != f['bytes']:
                        raise ValueError('El miembro comprimido cambió de tamaño')
                    with z.open(info) as source, extracted.open('wb') as target:
                        shutil.copyfileobj(source, target, length=1024*1024)
                if extracted.stat().st_size != f['bytes'] or sha256_archivo(extracted) != f['sha256']:
                    changed=dst.with_suffix(dst.suffix+'.nueva'); extracted.replace(changed)
                    raise ValueError(f'El CSV extraído cambió; se conserva en {changed.name}.')
                extracted.replace(dst)
            print('Preparado:',dst.name)
        except Exception as e:
            fallos_descarga.append(f['id'])
            temp.unlink(missing_ok=True)
            extracted.unlink(missing_ok=True)
            print(f"No se incorporó {f['id']}: {e}\nUsar el respaldo fechado; no reintentar en bucle.")
if args.verificar is not None:
    report=[]
    for f in seleccion_verificacion:
        file=destino(f); r={'id':f['id'],'archivo':f['archivo']}
        if not file.exists(): r['estado']='ausente'
        else:
            r['bytes']=file.stat().st_size
            r['sha256']=sha256_archivo(file)
            if 'sha256_contenido' in f:
                r['sha256_contenido']=sha256_contenido(file, f)
            r['estado']='coincide' if coincide_fuente(file, f) else 'version_distinta'
            if file.suffix=='.csv':
                with file.open(encoding='utf-8-sig',newline='') as stream:
                    reader=csv.reader(stream, delimiter=f.get('separador', ','))
                    cabecera=next(reader, [])
                    r['columnas']=len(cabecera); r['filas']=0; r['ancho_incorrecto']=0
                    for fila in reader:
                        r['filas'] += 1
                        r['ancho_incorrecto'] += len(fila) != len(cabecera)
                    if 'columnas' in f:
                        r['esquema_coincide'] = cabecera == f['columnas']
                        if not r['esquema_coincide'] or r['filas'] != f['filas'] or r['ancho_incorrecto']:
                            r['estado']='estructura_distinta'
            elif file.suffix=='.zip':
                with zipfile.ZipFile(file) as z:
                    r['zip_integro']=z.testzip() is None
                    r['componentes']=sorted({Path(n).suffix for n in z.namelist()})
            elif file.suffix=='.json':
                d=json.loads(file.read_text()); r['error_api']=d.get('error')
                if 'features' in d:r['elementos']=len(d['features'])
            if f.get('contenedor') == 'zip':
                archive = destino_descarga(f)
                r['archivo_fuente'] = str(archive.relative_to(ROOT))
                if not archive.exists():
                    r['estado']='archivo_fuente_ausente'
                else:
                    r['sha256_fuente']=sha256_archivo(archive)
                    r['fuente_coincide']=(archive.stat().st_size==f['bytes_descarga'] and
                                         r['sha256_fuente']==f['sha256_descarga'])
                    if not r['fuente_coincide']:r['estado']='archivo_fuente_distinto'
        report.append(r); print(r['id'],r['estado'],r.get('filas',r.get('elementos','')))
    out=ROOT/'salidas';out.mkdir(exist_ok=True)
    (out/'verificacion.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    if any(r['estado']!='coincide' or r.get('error_api') or r.get('zip_integro') is False for r in report):
        raise SystemExit('Verificación incompleta: consultar salidas/verificacion.json')
if fallos_descarga: raise SystemExit('Descarga incompleta: ' + ', '.join(fallos_descarga))
if not any([args.listar,args.descargar,args.respaldo,args.verificar is not None]): P.print_help()
