"""Ejercicios locales sobre datos abiertos. Ejecutar: python talleres.py --help"""
from pathlib import Path
import argparse, csv, hashlib, json, re, statistics, time, unicodedata
import duckdb
import pandas as pd
ROOT=Path(__file__).resolve().parent; RAW=ROOT/'data/raw'; OUT=ROOT/'salidas';OUT.mkdir(exist_ok=True)
def norm(x):
    x=''.join(c for c in unicodedata.normalize('NFKD',str(x)) if not unicodedata.combining(c))
    return ' '.join(re.sub(r'[^A-Z0-9 ]',' ',x.upper()).split())
def load(name):return pd.read_csv(RAW/name,dtype=str,keep_default_na=False,encoding='utf-8-sig')
def save_json(name,data):(OUT/name).write_text(json.dumps(data,ensure_ascii=False,indent=2,default=str),encoding='utf-8')
def perfil():
    results=[]
    for name in ['agrosavia.csv','eva.csv','divipola.csv']:
        df=load(name)
        for col in df:
            values=df[col].str.strip()
            results.append({'archivo':name,'columna':col,'filas':len(df),'vacios':int(values.eq('').sum()),'ND':int(values.str.upper().eq('ND').sum()),'distintos':int(values.nunique())})
    pd.DataFrame(results).to_csv(OUT/'perfil.csv',index=False)
    print('Perfil:',len(results),'columnas; no se han eliminado registros.')
def calidad():
    original=load('agrosavia.csv'); n=len(original)
    # La igualdad se comprueba en las 32 columnas, incluido el identificador.
    repeated=original.duplicated(keep='first')
    original[repeated].to_csv(OUT/'duplicados_exactos.csv',index=False)
    df=original.loc[~repeated].copy();df['fila_fuente']=df.index+2
    rename={'Secuencial':'id','Fecha de Análisis':'fecha_texto','Departamento':'departamento','Municipio':'municipio','Cultivo':'cultivo','pH agua:suelo':'ph_texto','Materia organica':'mo_texto','Fósforo Bray II':'p_texto'}
    s=df[list(rename)+['fila_fuente']].rename(columns=rename)
    for a,b in [('ph_texto','ph'),('mo_texto','mo'),('p_texto','fosforo')]:
        s[b]=pd.to_numeric(s[a].str.strip().str.replace(',','.',regex=False),errors='coerce')
    s['fecha']=pd.to_datetime(s['fecha_texto'],format='%d/%m/%Y',errors='coerce')
    s['anio']=s['fecha'].dt.year.astype('Int64')
    s['conflicto_id']=s['id'].duplicated(keep=False)
    s['estado_ph']='apto'
    s.loc[s['ph'].isna(),'estado_ph']='sin_ph_numerico'
    s.loc[s['ph'].notna() & ~s['ph'].between(0,14),'estado_ph']='fuera_dominio'
    s.loc[s['conflicto_id'],'estado_ph']='conflicto_id'
    # Son dominios analíticos, no recomendaciones de fertilización.
    s['mo_admisible']=s['mo'].between(0,100)
    s['fosforo_admisible']=s['fosforo'].ge(0)
    d=load('divipola.csv');d['codigo_municipio']=d['Código Municipio'].str.zfill(5)
    d['codigo_departamento']=d['Código Departamento'].str.zfill(2)
    d['clave']=d['Nombre Departamento'].map(norm)+'|'+d['Nombre Municipio'].map(norm)
    if d['codigo_municipio'].duplicated().any():raise ValueError('DIVIPOLA no es única por código')
    if d['clave'].duplicated().any():raise ValueError('Nombres territoriales ambiguos: revisar DIVIPOLA')
    s['clave']=s['departamento'].map(norm)+'|'+s['municipio'].map(norm)
    s=s.merge(d[['clave','codigo_municipio']],how='left',on='clave',validate='many_to_one')
    s['municipio_encontrado']=s['codigo_municipio'].notna()
    s.to_parquet(OUT/'suelos_clasificados.parquet',index=False)
    aptos=s[s['estado_ph'].eq('apto')]; cuar=s[~s['estado_ph'].eq('apto')]
    aptos.to_parquet(OUT/'suelos_ph.parquet',index=False)
    cuar.to_csv(OUT/'revision_ph.csv',index=False)
    s[~s['municipio_encontrado']][['departamento','municipio','clave']].drop_duplicates().to_csv(OUT/'territorios_por_revisar.csv',index=False)
    dim=d.rename(columns={'Nombre Departamento':'departamento','Nombre Municipio':'municipio'})[['codigo_departamento','codigo_municipio','departamento','municipio']]
    dim.to_parquet(OUT/'dim_municipio.parquet',index=False)
    e=load('eva.csv').rename(columns={'Código Dane municipio':'codigo_municipio','Código Dane departamento':'codigo_departamento','Año':'anio','Cultivo':'cultivo','Periodo':'periodo','Estado físico del cultivo':'estado_fisico','Área cosechada':'area_ha','Producción':'produccion_t','Rendimiento':'rendimiento_publicado'})
    e=e[['codigo_departamento','codigo_municipio','anio','cultivo','periodo','estado_fisico','area_ha','produccion_t','rendimiento_publicado']].copy()
    e['codigo_municipio']=e['codigo_municipio'].str.zfill(5)
    e['codigo_departamento']=e['codigo_departamento'].str.zfill(2)
    for c in ['area_ha','produccion_t','rendimiento_publicado','anio']:e[c]=pd.to_numeric(e[c],errors='coerce')
    e['apto_rendimiento']=e['area_ha'].gt(0)&e['produccion_t'].ge(0)&e['anio'].notna()
    e['municipio_encontrado']=e['codigo_municipio'].isin(dim['codigo_municipio'])
    e.to_parquet(OUT/'eva.parquet',index=False)
    stats={'raw_suelos':n,'duplicados_exactos':int(repeated.sum()),'clasificados':len(s),'aptos_ph':len(aptos),'revision_ph':len(cuar),'motivos':s['estado_ph'].value_counts().to_dict(),'territorio_no_encontrado':int((~s['municipio_encontrado']).sum()),'fecha_no_interpretable':int(s['fecha'].isna().sum()),'divipola':len(dim),'eva':len(e),'eva_apto_rendimiento':int(e['apto_rendimiento'].sum()),'eva_sin_codigo_en_divipola':int((~e['municipio_encontrado']).sum())}
    assert n==stats['duplicados_exactos']+stats['aptos_ph']+stats['revision_ph']
    save_json('controles.json',stats);print(json.dumps(stats,ensure_ascii=False,indent=2))
def consultas():
    con=duckdb.connect(str(OUT/'suelo_sabio.duckdb'));con.execute("SET threads=2")
    for name,file in [('suelos','suelos_ph.parquet'),('eva','eva.parquet'),('municipios','dim_municipio.parquet')]:
        con.execute(f"CREATE OR REPLACE TABLE {name} AS SELECT * FROM read_parquet(?)",[str(OUT/file)])
    # Cada salida tiene una unidad explícita. No se cruza cada muestra con cada cultivo.
    ph=con.execute('''SELECT codigo_municipio, anio, count(*) AS muestras,
        median(ph) AS mediana_ph FROM suelos
        WHERE codigo_municipio IS NOT NULL AND anio IS NOT NULL
        GROUP BY codigo_municipio,anio ORDER BY codigo_municipio,anio''').df()
    ph.to_parquet(OUT/'ph_municipio_anio.parquet',index=False)
    con.execute('''CREATE OR REPLACE TABLE rendimiento AS
        SELECT codigo_municipio, cultivo, estado_fisico, anio,
        sum(produccion_t) AS produccion_t, sum(area_ha) AS area_ha,
        sum(produccion_t)/sum(area_ha) AS rendimiento_t_ha
        FROM eva WHERE apto_rendimiento
        GROUP BY codigo_municipio,cultivo,estado_fisico,anio''')
    con.execute('SELECT * FROM rendimiento ORDER BY codigo_municipio,cultivo,estado_fisico,anio').df().to_parquet(OUT/'rendimiento.parquet',index=False)
    con.execute('''SELECT r.*, m.departamento,m.municipio
        FROM rendimiento r LEFT JOIN municipios m USING(codigo_municipio)
        ORDER BY codigo_municipio,cultivo,estado_fisico,anio''').df().to_csv(OUT/'rendimiento_municipal.csv',index=False)
    # Join correcto solo entre agregados y con clave explícita.
    con.register('ph_agregado',ph)
    q=con.execute('''SELECT r.*, p.muestras,p.mediana_ph
        FROM rendimiento r LEFT JOIN ph_agregado p USING(codigo_municipio,anio)
        ORDER BY codigo_municipio,cultivo,estado_fisico,anio''').df()
    assert len(q)==con.execute('SELECT count(*) FROM rendimiento').fetchone()[0]
    q.to_parquet(OUT/'integracion_exploratoria.parquet',index=False)
    save_json('cobertura_integracion.json',{'filas_rendimiento':len(q),'filas_con_ph':int(q['mediana_ph'].notna().sum()),'advertencia':'Asociación agregada exploratoria; no causal ni validación de recomendaciones agronómicas.'})
    con.close();print('Base SQL, agregados y cobertura guardados.')
def benchmark():
    con=duckdb.connect();con.execute('SET threads=2')
    src=OUT/'eva.parquet';df=pd.read_parquet(src);csvpath=OUT/'eva_normalizada.csv';df.to_csv(csvpath,index=False)
    rows=[]
    for label,expr in [('CSV',"read_csv(?, header=true, auto_detect=true)"),('Parquet',"read_parquet(?)")]:
        file=csvpath if label=='CSV' else src
        sql=f'SELECT count(*),sum(produccion_t) FROM {expr} WHERE apto_rendimiento'
        expected=con.execute(sql,[str(file)]).fetchone();times=[]
        for i in range(5):
            start=time.perf_counter();result=con.execute(sql,[str(file)]).fetchone();times.append(time.perf_counter()-start)
            assert result[0]==expected[0] and abs(result[1]-expected[1])<1e-5
        rows.append({'formato':label,'bytes':file.stat().st_size,'mediana_segundos':statistics.median(times),'repeticiones':5,'filas':expected[0],'suma_t':expected[1]})
    assert rows[0]['filas']==rows[1]['filas'] and abs(rows[0]['suma_t']-rows[1]['suma_t'])<1e-5
    pd.DataFrame(rows).to_csv(OUT/'benchmark.csv',index=False);print(rows)
def geografia():
    from geoespacial import intersecciones
    return intersecciones()
def suelo():
    import numpy as np
    import rasterio
    result={}
    with rasterio.open(RAW/'soilgrids.tif') as src:
        a=src.read(1,masked=True).astype(float)
        # pH x 10. Conservar la máscara; 0 no se supone automáticamente NoData.
        a=a/10;valid=a[(a>0)&(a<=14)]
        result['soilgrids']={'shape':src.shape,'crs':str(src.crs),'nodata':src.nodata,'min_ph':float(valid.min()),'max_ph':float(valid.max()),'media_ph_sin_ceros_por_revisar':float(valid.mean()),'pixeles_validos':int(valid.count())}
        result['soilgrids']['celdas_cero']=int(np.sum(a.filled(np.nan)==0))
        result['soilgrids']['advertencia']='Inspeccionar celdas cero y metadatos. No compararlas con muestras sin equivalencia de profundidad y ubicación.'
    w=json.loads((RAW/'wosis.json').read_text())
    result['wosis']={'registros':len(w['features']),'perfiles_distintos':len({f['properties']['profile_id'] for f in w['features']}),'paises':sorted({f['properties']['country_name'] for f in w['features']})}
    from geoespacial import mapa_suelo
    mapa_suelo()
    save_json('control_suelo.json',result);print(result);return result
def clima():
    import numpy as np
    import rasterio
    from rasterio.warp import transform_bounds
    from rasterio.windows import from_bounds
    n=json.loads((RAW/'nasa.json').read_text());params=n['properties']['parameter'];records=[]
    for date in sorted(params['T2M']):
        records.append({'fecha':pd.to_datetime(date,format='%Y%m%d'),'t2m':None if params['T2M'][date]==-999 else params['T2M'][date],'lluvia_mm':None if params['PRECTOTCORR'][date]==-999 else params['PRECTOTCORR'][date]})
    df=pd.DataFrame(records);df.to_parquet(OUT/'nasa_diario.parquet',index=False)
    result={'nasa_dias':len(df),'nasa_temperatura_media':float(df['t2m'].mean()),'nasa_precipitacion_suma':float(df['lluvia_mm'].sum())}
    with rasterio.open(RAW/'chirps.tif') as src:
        # Recorte de demostración; no corresponde a un municipio completo.
        bounds=transform_bounds('EPSG:4326',src.crs,-73.4,5.5,-73.3,5.6)
        window=from_bounds(*bounds,transform=src.transform).round_offsets().round_lengths()
        a=src.read(1,window=window,masked=True)
        a=np.ma.masked_where(a<0,a)
        result['chirps']={'crs':str(src.crs),'nodata':src.nodata,'pixeles_validos':int(a.count()),'media_lluvia_mensual_mm':float(a.mean()),'periodo':'2025-01','bbox':[-73.4,5.5,-73.3,5.6]}
    from geoespacial import mapa_clima
    mapa_clima()
    save_json('control_clima.json',result);print(result);return result
def clima_suelo():
    # Compatibilidad para informes que necesitan ambos dominios.
    result={**suelo(), **clima()}
    save_json('control_clima_suelo.json',result);return result
def modelo():
    from sklearn.metrics import mean_absolute_error
    # Pronóstico anual municipal por persistencia. No usa producción/área del año objetivo como predictores.
    df=pd.read_parquet(OUT/'rendimiento.parquet');df=df[df['anio'].between(2022,2025)].copy()
    keys=['codigo_municipio','cultivo','estado_fisico'];df=df.sort_values(keys+['anio'])
    df['prediccion']=df.groupby(keys)['rendimiento_t_ha'].shift()
    df['anio_previo']=df.groupby(keys)['anio'].shift()
    valid=df[(df['anio']==df['anio_previo']+1)&df['prediccion'].notna()]
    reports=[]
    for year in [2024,2025]:
        test=valid[valid['anio']==year]
        if test.empty:raise ValueError(f'Sin pares consecutivos para {year}')
        reports.append({'anio':year,'n':len(test),'MAE_t_ha':float(mean_absolute_error(test['rendimiento_t_ha'],test['prediccion'])),'modelo':'persistencia del año anterior'})
    # Recurso predictivo opcional del antiguo E12: conservar denominadores y escalas.
    detail=[]
    for year in [2024,2025]:
        target=df[df['anio'].eq(year)]
        evaluable=valid[valid['anio'].eq(year)]
        for (crop,state), group in target.groupby(['cultivo','estado_fisico'],dropna=False):
            test=evaluable[evaluable['cultivo'].eq(crop)&evaluable['estado_fisico'].eq(state)]
            detail.append({'anio':year,'cultivo':crop,'estado_fisico':state,
                'filas_objetivo':len(group),'pares_evaluables':len(test),
                'sin_anio_previo':len(group)-len(test),'cobertura':len(test)/len(group),
                'MAE_t_ha':float(mean_absolute_error(test['rendimiento_t_ha'],test['prediccion'])) if len(test) else None})
    pd.DataFrame(detail).to_csv(OUT/'evaluacion_por_cultivo.csv',index=False)
    for report in reports:
        total=len(df[df['anio'].eq(report['anio'])])
        report.update(filas_objetivo=total,sin_anio_previo=total-report['n'],cobertura=report['n']/total)
    valid.to_csv(OUT/'predicciones_persistencia.csv',index=False)
    save_json('evaluacion_modelo.json',reports);print(reports)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('taller',choices=['perfil','calidad','consultas','benchmark','geografia','suelo','clima','clima_suelo','modelo']);a=p.parse_args();globals()[a.taller]()
if __name__=='__main__':main()
