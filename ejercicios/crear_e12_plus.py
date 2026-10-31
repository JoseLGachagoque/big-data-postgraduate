"""Genera la plantilla demostrativa E12_plus sin resultados guardados."""
import json
from pathlib import Path

cells = []
def md(s):
    cells.append({"cell_type": "markdown", "metadata": {}, "source": s.splitlines(keepends=True)})
def code(s):
    cells.append({"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": s.splitlines(keepends=True)})

md("""# E12_plus · Spark, tablas Iceberg y metadatos

**Ampliación opcional** de E12: no cambia sus criterios ni la entrega. Usaremos dos muestras reales de PQRS de la Superintendencia Nacional de Salud, de 1.000 filas cada una, para contar reportes por corte y código de municipio del afectado. Copia el notebook a `soluciones/` con otro nombre.

Las muestras son las primeras filas de cada archivo y no son aleatorias. Los conteos representan reportes, no personas únicas ni prevalencia, y no deben extrapolarse. Esta agrupación ilustrativa no sustituye la validación de E12.

Requiere Python y PySpark **4.0.1**, Java 21 y kernel del curso. Detén otras sesiones Spark y reinicia el kernel antes de iniciar: las extensiones y el catálogo se configuran al crear la sesión. La primera ejecución descarga el runtime Iceberg 1.12.0 desde Maven y requiere conexión; también puede instalarse previamente el JAR compatible. Utiliza `local[2]`. Los ejemplos crean un almacén nuevo por ejecución, sin sobrescribir productos E12. No edites ni borres archivos de metadatos a mano.
""")
code("""from pathlib import Path
from uuid import uuid4
import csv, hashlib, json, sys
from pyspark import SparkContext
from pyspark.sql import SparkSession

root = next((p for p in [Path.cwd(), *Path.cwd().parents] if (p / 'kit/requirements_spark.txt').is_file()), None)
assert root, 'Abre Jupyter desde el repositorio big-data-postgraduate.'
assert SparkContext._active_spark_context is None, 'Detén Spark y reinicia el kernel antes de continuar.'
run_id = uuid4().hex[:12]
out = root / 'kit/salidas/soluciones/E12_plus' / run_id
warehouse = out / 'warehouse'
warehouse.mkdir(parents=True, exist_ok=False)
print('Ejecución:', run_id, 'almacén:', warehouse)
""")
md("""## 1. Configurar Spark y el catálogo

Un catálogo Hadoop local administra las tablas en el almacén indicado. El paquete debe coincidir con Spark 4.0 y Scala 2.13; reinicia el kernel si cambias la configuración.
""")
code("""spark = (SparkSession.builder.master('local[2]').appName('E12-plus-Iceberg')
    .config('spark.jars.packages', 'org.apache.iceberg:iceberg-spark-runtime-4.0_2.13:1.12.0')
    .config('spark.sql.extensions', 'org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions')
    .config('spark.sql.catalog.laboratorio', 'org.apache.iceberg.spark.SparkCatalog')
    .config('spark.sql.catalog.laboratorio.type', 'hadoop')
    .config('spark.sql.catalog.laboratorio.warehouse', warehouse.as_uri())
    .config('spark.sql.shuffle.partitions', '4').getOrCreate())
assert spark.version == '4.0.1', f'Se esperaba Spark 4.0.1; encontrado {spark.version}'
print('Spark:', spark.version, 'Python:', sys.executable)
""")
md("""## 2. Crear y consultar una tabla

Lee las muestras 2023_II y 2024_I con el separador del manifiesto, verifica sus huellas y cuenta reportes por corte y código de municipio del afectado. Los códigos permanecen como texto y los vacíos se identifican como SIN_INFORMAR.
""")
code("""from pyspark.sql import functions as F

manifiesto = json.loads((root / 'kit/pqrs_fuentes.json').read_text(encoding='utf-8'))
por_corte = {x['periodo']: x for x in manifiesto}
entradas, agregados = {}, {}
for corte in ['2023_II', '2024_I']:
    ref = por_corte[corte]
    ruta = root / 'kit/data/pqrs_muestras' / f'Muestra_1000_{corte}.csv'
    assert ruta.is_file(), f'Falta la muestra: {ruta}'
    huella = hashlib.sha256(ruta.read_bytes()).hexdigest()
    assert huella == ref['sha256_muestra'], f'Huella inesperada: {ruta.name}'
    with ruta.open(encoding=ref['codificacion'], newline='') as archivo:
        lector = csv.DictReader(archivo, delimiter=ref['separador'])
        assert {'OBJECTID', 'afec_cod_mpio'} <= set(lector.fieldnames or [])
        filas = [(corte, (fila['afec_cod_mpio'] or '').strip() or 'SIN_INFORMAR') for fila in lector]
    assert len(filas) == ref['filas_muestra']
    datos = spark.createDataFrame(filas, ['corte', 'territorio'])
    agregado = datos.groupBy('corte', 'territorio').agg(F.count('*').alias('reportes'))
    assert agregado.agg(F.sum('reportes')).first()[0] == len(filas)
    entradas[corte] = {'archivo': ruta.name, 'sha256': huella, 'filas': len(filas)}
    agregados[corte] = agregado
    print(corte, 'filas:', len(filas), 'grupos:', agregado.count())

spark.sql('CREATE NAMESPACE IF NOT EXISTS laboratorio.e12')
spark.sql('''CREATE TABLE laboratorio.e12.reportes (
    corte STRING, territorio STRING, reportes BIGINT
) USING iceberg''')
agregados['2023_II'].writeTo('laboratorio.e12.reportes').append()
assert spark.table('laboratorio.e12.reportes').exceptAll(agregados['2023_II']).count() == 0
assert agregados['2023_II'].exceptAll(spark.table('laboratorio.e12.reportes')).count() == 0
spark.sql('SELECT * FROM laboratorio.e12.reportes ORDER BY corte, territorio').show()
""")
md("""## 3. Un segundo snapshot

Agrega el corte 2024_I y compara el estado actual con el primer snapshot, que contiene 2023_II. Comprueba todos los grupos y el total de reportes. La lectura histórica depende de la retención. Ejecuta esta celda una sola vez: repetirla duplicaría el corte.
""")
code("""primer_snapshot = spark.sql('SELECT snapshot_id FROM laboratorio.e12.reportes.snapshots ORDER BY committed_at').first()[0]
agregados['2024_I'].writeTo('laboratorio.e12.reportes').append()
snapshots = spark.sql('SELECT committed_at, snapshot_id, parent_id, operation FROM laboratorio.e12.reportes.snapshots ORDER BY committed_at')
snapshots.show(truncate=False)
tabla_actual = spark.table('laboratorio.e12.reportes')
tabla_anterior = spark.read.format('iceberg').option('snapshot-id', str(primer_snapshot)).load('laboratorio.e12.reportes')
esperado = agregados['2023_II'].unionByName(agregados['2024_I'])
assert tabla_anterior.exceptAll(agregados['2023_II']).count() == 0
assert agregados['2023_II'].exceptAll(tabla_anterior).count() == 0
assert tabla_actual.exceptAll(esperado).count() == 0
assert esperado.exceptAll(tabla_actual).count() == 0
anterior = tabla_anterior.agg(F.sum('reportes')).first()[0]
actual = tabla_actual.agg(F.sum('reportes')).first()[0]
print('Reportes anterior / actual:', anterior, actual)
assert (anterior, actual) == (entradas['2023_II']['filas'], sum(x['filas'] for x in entradas.values()))
""")
md("""## 4. Inspeccionar y guardar evidencia de metadatos

Iceberg mantiene metadatos de tabla, snapshots, manifiestos y referencias a archivos en el almacén. Las tablas de metadatos permiten consultarlos; el JSON siguiente es una evidencia legible de la ejecución, no reemplaza esos archivos ni constituye una copia de seguridad. Evita divulgar rutas si contienen información sensible.
""")
code("""spark.sql('SELECT committed_at, snapshot_id, is_current_ancestor FROM laboratorio.e12.reportes.history').show(truncate=False)
spark.sql('SELECT file_path, record_count, file_size_in_bytes FROM laboratorio.e12.reportes.files').show(truncate=False)
evidencia = {'ejecucion': run_id, 'spark': spark.version, 'iceberg': '1.12.0',
             'tabla': 'laboratorio.e12.reportes', 'warehouse': warehouse.as_uri(),
             'primer_snapshot': str(primer_snapshot), 'entradas': entradas,
             'reportes_anteriores': anterior, 'reportes_actuales': actual,
             'snapshots': [json.loads(row) for row in snapshots.toJSON().collect()]}
(out / 'evidencia.json').write_text(json.dumps(evidencia, ensure_ascii=False, indent=2), encoding='utf-8')
print('Evidencia:', out / 'evidencia.json')
print('Metadatos físicos:', warehouse / 'e12/reportes/metadata')
""")
md("""## 5. Actividad del equipo

1. Explica qué corte contiene cada snapshot y qué representa cada archivo consultado. Compara por territorio y total.
2. Repite con una tabla nueva a partir del agregado validado E12; registra su procedencia y compara conteos y medidas antes y después de publicar. Explica las diferencias con esta agrupación exploratoria.
3. Guarda la evidencia de ejecución y explica qué metadatos administra Iceberg, dónde quedan y por qué el JSON de auditoría no los reemplaza.
4. Describe una limitación de la muestra y qué necesitaría cambiar para un catálogo compartido en producción.

**Respuesta y evidencia del equipo:** completar.
""")
code("""# Completa aquí la adaptación y sus comprobaciones.
""")
md("""## 6. Cierre

Conserva el almacén completo si necesitas volver a consultar esta tabla local. Las salidas quedan bajo `kit/salidas/soluciones/E12_plus/` y deben poder regenerarse; no incluyen la solución principal E12. Detén Spark al terminar.

Referencias: [configuración de Spark e Iceberg](https://iceberg.apache.org/docs/latest/spark-configuration/), [consultas y tablas de metadatos](https://iceberg.apache.org/docs/latest/spark-queries/) y [versiones](https://iceberg.apache.org/releases/).
""")
code("spark.stop()\n")
notebook = {"cells": cells, "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}, "language_info": {"name": "python"}}, "nbformat": 4, "nbformat_minor": 5}
Path(__file__).with_name('E12_plus_Spark_Iceberg.ipynb').write_text(json.dumps(notebook, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
