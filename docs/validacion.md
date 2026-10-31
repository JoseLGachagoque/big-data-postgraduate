# Revisión del material vigente

Preparado por el PhD Esteban Hernández, CyberColombia.

## Estado del bloque pipelines y DataOps: 30 de octubre

La [revisión de alineación](revision-alineacion-30-octubre.md) registra los ajustes documentales y sus límites. El E12 vigente corresponde a integración del pipeline, no a las métricas predictivas históricas descritas más abajo. La [solución integrada E12](../soluciones/E12_solucion.ipynb) se ejecutó con las tres muestras locales: 3.000 filas, 687 grupos, conciliación exacta en DuckDB y contenido estable en dos ejecuciones. Esta comprobación no acredita una demostración Iceberg.

El calendario contractual comprende 12 clases entre el 2 de octubre y el 7 de noviembre de 2026. Se comprobaron 3.840 minutos efectivos de docencia en línea, excluyendo todos los recesos y almuerzos. El trabajo autónomo es opcional y no reemplaza horas de clase.

Las tres URL de Supersalud devolvieron HTTP 206 en una lectura Range de sus cabeceras y coincidieron con las 38 columnas del corte docente el 2 de octubre de 2026. Los CSV completos locales se verificaron por SHA-256, filas y esquema. Sumaron 2.444.766 filas y 1.816.243.049 bytes.

Se ejecutaron perfil, formatos, calidad y benchmark PQRS con muestras y archivos completos. Cinco motores conciliaron exactamente la misma agregación: pandas, Polars, DuckDB-Parquet, DuckDB-particionado y DuckDB-CSV. El lector particionado utiliza explícitamente hive_partitioning=True. Los tiempos incluyen arranque, lectura, consulta y exportación de un resultado pequeño. La RSS se sondeó cada 10 ms. Las mediciones pertenecen a esta máquina y consulta y no se extrapolan a otros equipos.

Los cuatro notebooks actuales se ejecutaron completamente con las muestras de 3.000 filas y las observaciones NASA reales. La reproducción finita obtuvo 13 entregas, 12 registros reales distintos, 11 aceptados, un reintento y un evento tardío. La regla Python no reproduce toda la semántica de Spark.

Los originales agroambientales y sus controles anteriores se conservan en el kit y su manifiesto. El script de modelo genera MAE y cobertura por año, cultivo y estado físico, además del resumen global. Las rutas originales de los notebooks históricos se preservan como referencia, fuera de la ruta de ejecución actual.

Los libros conservan el estilo del book-template y se compilaron con XeLaTeX. Las diapositivas modificadas mantienen tablas, textos y gráficos editables; se revisaron exportaciones y vistas renderizadas. No se verificó en PowerPoint la reproducción de animaciones ni se validó una instalación nueva de Windows o la interacción de QGIS en esta revisión.

## Comprobaciones de esta integración en dev

Se ejecutaron en orden todas las celdas de código de los cuatro notebooks vigentes en procesos Python locales (sin interfaz Jupyter), con las 3.000 filas de las muestras y el corte NASA. Se validó su formato con nbformat. El notebook 03 añade comparación exacta de la agregación de 2024 entre Polars y DuckDB: 2.000 reportes.

El benchmark verificó igualdad entre los cinco motores con tres repeticiones medidas y calentamiento. Se comprobó que rechaza etiquetar el producto de muestras como completo. En esta ejecución restringida no se pudo observar RSS y se obtuvo cero en ese campo: no es una medición de memoria válida. No se repitió el benchmark de 1,816 GB; sus resultados anteriores corresponden a la validación previa del material.

La versión histórica de E12, hoy referencia opcional de predicción, se volvió a ejecutar: 15.267 pares para 2024 y 15.503 para 2025. La salida `evaluacion_por_cultivo.csv` contiene 317 grupos año–cultivo–estado físico; sus conteos y MAE ponderado concilian con el resumen global. Se verificaron cobertura entre 0 y 1, grupos sin año previo y conservación de denominadores. Estos resultados no validan el E12 vigente de integración del pipeline.

Se comprobaron los enlaces locales y el calendario estructurado de doce clases y 3.840 minutos. Spark, Windows y QGIS no se volvieron a validar en esta integración. Los notebooks históricos permanecen sin ejecutar ni alterar.

## Nueva base WSL

Las instrucciones vigentes se unificaron en WSL 2 con Ubuntu-26.04, Python 3.12 gestionado por uv y JDK 21. La guía se contrastó con documentación oficial y se revisaron rutas y comandos. No se instaló ni se probó Ubuntu-26.04 en un equipo Windows durante este cambio.

## Migración geoespacial — 10 de octubre de 2026

Las referencias a QGIS de las validaciones anteriores son históricas. La ejecución vigente utiliza GeoPandas 1.1.1, Pyogrio 0.11.1, Matplotlib 3.10.3 y Rasterio 1.4.3 dentro del entorno Python del curso. Se instalaron los requisitos exactos del kit en el entorno local Python 3.12 y `pip check` no encontró incompatibilidades.

Se ejecutaron todas las celdas de E08, E09 y E11 en procesos Python locales, sin interfaz Jupyter; se validó su formato con nbformat. E08 conservó 1.122 municipios y las mismas 15 intersecciones que el script anterior, con claves iguales y áreas conciliadas con tolerancia relativa 1e-8 y absoluta 1e-6 ha. El GeoPackage se volvió a leer y conservó columnas, CRS y conteo. La segunda ejecución no duplicó filas.

Los controles de suelo y clima coinciden con los anteriores: 1.660 píxeles positivos y 188 ceros pendientes; diez horizontes WoSIS de tres perfiles; 31 días NASA, suma de 67,69 mm y cuatro píxeles del recorte CHIRPS. Ningún horizonte WoSIS del corte está dentro del recorte SoilGrids; la correlación IGAC se lee como tabla de atributos, no como capa geométrica. Se inspeccionaron los mapas PNG y se comprobaron enlaces locales, JSON y sintaxis Python.

Los comandos `suelo` y `clima` generan informes separados. `clima_suelo` permite reconstruir el informe combinado. No se ejecutó una instalación nueva de Windows/WSL ni se repitió la prueba de Spark; el notebook E11 cubre el soporte espacial y conserva la práctica Spark en su enunciado.

## Clase 2: pandas explícito

Se reescribieron P01 y su solución sin importaciones de scripts del curso, SimpleNamespace, cambios de sys.path ni búsqueda automática del repositorio. Se simplificaron también las celdas de lectura de PD01–PD03; sus actividades de desarrollo siguen abiertas para el estudiante.

Se validó nbformat y se ejecutaron todas las celdas de código de los cinco notebooks en procesos Python locales, sustituyendo únicamente la ruta WSL explícita por la del clon local durante la prueba. P01 conservó 3.000 filas, los tres hashes esperados y nueve mediciones de bloques con filas y vacíos iguales a la lectura completa. Las lecturas de las plantillas PD01–PD03 funcionaron; esto no certifica soluciones que el estudiante aún debe escribir. No se probó una instalación nueva de WSL.

## P02 y P03: operaciones visibles con pandas

Se sustituyeron las llamadas a funciones del kit por lectura, selección, conversión, escritura, partición, relectura y joins explícitos. Las soluciones de referencia contienen el mismo desarrollo. P03 requiere el Parquet de P02 y DIVIPOLA; se detiene con una indicación si falta cualquiera de esas entradas.

Se ejecutaron todas las celdas del notebook P02 dos veces y las de P03 una vez en procesos Python locales, sustituyendo únicamente la ruta WSL por la del clon local. Se conservaron 3.000 filas, 16 columnas y ocho particiones, comparando todas las columnas tras releer los productos. Se comprobaron las firmas de reejecución, el fallo de contrato y el fallo de cardinalidad del join. Los controles de P03 conservaron 41 edades mayores de 90 y tres ubicaciones de peticionario vacías, sin exclusiones. Las consultas pandas, Polars y DuckDB coincidieron en todos los grupos y en los 2.000 reportes de 2024.

Se revisaron enlaces, sintaxis y fuente JSON. Las salidas quedan separadas en kit/salidas/pandas/P02 y P03; los notebooks se distribuyen sin resultados guardados. La firma SHA-256 del CSV ordenado de P02 es propia del notebook y no sustituye la firma del script automatizado. Esta prueba no equivale a una instalación nueva de Windows/WSL.
