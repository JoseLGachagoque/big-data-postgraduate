# Notebooks vigentes

Preparado por el PhD Esteban Hernández, CyberColombia.

P01: 3 de octubre. P02: 9 de octubre. P03: 10 de octubre. P04: 23 de octubre. I01: 24 de octubre. Los notebooks acompañan los talleres y comparten las horas de clase; no añaden entregas obligatorias.

Preparar el `.venv` base CPU de la raíz según la guía [Windows/WSL](../../docs/instalacion-wsl.md) o [Linux/macOS](../../docs/instalacion-linux-macos.md). En instalación nativa, adaptar `repositorio` o `REPO` a la ruta real como indica esa guía. Abrir desde `kit/` o `kit/Notebooks/`, usar el mismo entorno Python y ejecutar en orden. Los prerrequisitos son explícitos: P03 y el notebook 04 original leen los productos de P02; P03 requiere DIVIPOLA. El nuevo `04_Rendimiento_Analysis` sigue una ruta independiente con los seis cortes completos.

Para crear o comprobar el entorno y el kernel, consultar [entornos por plataforma](../../docs/entornos-virtuales.md). La [ampliación NVIDIA GPU](../../docs/polars-gpu.md) usa `.venv-gpu` y su propio kernel; no es necesaria para estos notebooks.

Los notebooks históricos se conservan en `supersalud/`, con su procedencia y limitaciones, y no son la guía de ejecución actual.

## Índice y propósito

Como referencia durante las prácticas, consultar la [guía práctica de pandas](../../docs/manual-pandas.md), con ejemplos sobre los CSV de DIVIPOLA, EVA y AGROSAVIA descargados con `kit/00_datos.py`.

| Notebook | Talleres y clases | Evidencia |
|---|---|---|
| [01 Perfil PQRS](01_Perfil_PQRS.ipynb) | P01 · clase 2 | Conteos, esquema, hashes y memoria por tamaño de bloque |
| [02 Parquet y contratos](02_Parquet_y_contratos.ipynb) | P02 · clase 3 | Proyección de 16 columnas, particiones, reejecución y fallo de contrato |
| [03 Calidad y consulta](03_Calidad_y_consulta.ipynb) | P03 · clase 4 | Calidad sin exclusiones arbitrarias y consulta diferida de 2024 |
| [05 Spark: lectura y agregación](05_Spark_lectura_y_agregacion.ipynb) | E07 · clase 5, 16 de octubre | CSV, conversión, Parquet, plan y equivalencia con DuckDB |
| [06 Spark: joins y ventanas](06_Spark_joins_y_ventanas.ipynb) | E07 · clase 6, 17 de octubre | Cardinalidad, broadcast, top 3 y particiones |
| [04 Rendimiento y eventos](04_Rendimiento_y_eventos.ipynb) | P04 · clase 7; I01 · clase 8 | Equivalencia entre motores y traza finita NASA |
| [04 Rendimiento Analysis](04_Rendimiento_Analysis.ipynb) | P04 actualizado · clases 7–8 | Seis cortes 2023–2025, equivalencia Polars–DuckDB y benchmark Polars–pandas |
| [08 Streaming de eventos](08_Streaming_de_Eventos.ipynb) | I01 y E11 · clase 8 | Traza finita, ventanas, watermark, estado, checkpoint, recuperación y auditoría |

El notebook 04 original se conserva sin cambios. El nuevo notebook Analysis desarrolla por separado el panorama completo de P04. Para streaming, el notebook 08 reúne I01 y la reproducción E11 en una sola progresión; usa `data/raw/nasa.json`, que se descarga desde el manifiesto agroambiental. Los notebooks anteriores no se modifican.

Seleccionar **BigData · WSL Ubuntu 26.04 · Python 3.12** en Windows/WSL o **BigData · Linux/macOS · Python 3.12** en instalación nativa. Instalar las dependencias mediante la guía correspondiente.

## Ruta y rama del curso

El clon se realiza desde `main`: `/mnt/c/Users/TUPTC/bigdata/big-data-postgraduate` en WSL o `~/bigdata/big-data-postgraduate` en Linux/macOS. El entorno está en `.venv` de la raíz; adaptar las rutas explícitas del notebook al clon local. Para actualizar, situarse en `main` y ejecutar `git pull --ff-only origin main` después de revisar los cambios locales.

## Ejercicios geoespaciales

| Notebook | Archivos requeridos | Productos |
|---|---|---|
| [E08 Geometrías e intersección](E08_Geoespacial.ipynb) | DANE departamentos y municipios; IGAC capacidad y química; AGROSAVIA y DIVIPOLA para unión tabular | Mapa, GeoPackage, CSV y controles |
| [E09 Suelo y profundidad](E09_Geoespacial.ipynb) | SoilGrids, WoSIS, IGAC química y correlación | Mapa, perfiles y control_suelo.json |
| [E11 Soporte climático](E11_Geoespacial.ipynb) | NASA y CHIRPS | Mapa, serie NASA y control_clima.json |

Los notebooks no descargan datos automáticamente. Preparar las fuentes según cada taller. Los datos originales se conservan; `kit/salidas/` se regenera. GeoPandas gestiona vectores y Rasterio los rásteres; Matplotlib produce los mapas. El notebook E11 cubre el soporte espacial: la reproducción Spark sigue en el enunciado E11.

## Enfoque de la clase 2

P01 declara una ruta WSL editable y utiliza `pd.read_csv`, inspección, filtros y comprobaciones visibles; no importa scripts del curso. Su solución de referencia conserva este desarrollo. Los bucles de lectura por bloques se introducen después de inspeccionar un bloque. P02 y P03 continúan con operaciones pandas explícitas; las funciones del kit quedan como referencia de automatización después de comprender los pasos. Las plantillas PD01–PD03 también declaran rutas explícitas y muestran cada lectura sin funciones auxiliares.

## P02 → P03: archivos y API visibles

P02 explica `read_csv`, selección y conversión, `concat`, `groupby`, `to_csv`, `to_parquet`, `read_parquet`, contrato defectuoso y comprobación de reejecución. P03 lee `kit/salidas/pandas/P02/pqrs.parquet` y muestra reglas, `merge`, cardinalidad, anti-joins y consultas equivalentes en pandas, Polars y DuckDB. Preparar DIVIPOLA antes de P03; las salidas de este notebook quedan en `kit/salidas/pandas/P03`. Las soluciones de referencia mantienen los mismos pasos.

## Desde P04: operaciones y tiempos visibles

[04 update1: laboratorio de completos](04_Rendimiento_y_eventos_update1.ipynb)
conserva las 31 celdas del notebook original y reemplaza su segunda parte con
un flujo independiente: verificar/descargar tres CSV completos PQRS,
leer y convertir todos a Parquet con Polars y analizar los mismos datos con pandas CPU,
Polars CPU y Polars GPU. Incluye equivalencia, calentamiento, tres repeticiones,
controles por periodo y fronteras de tiempo explícitas. Los ejercicios son
municipios con más quejas y sus departamentos por periodo, y municipios con
más quejas por grupo etario y género. Empezar en L1, sin P02.
GPU requiere el entorno NVIDIA verificado. Se entrega sin ejecutar y su
evidencia forma parte de P04, sin otra entrega.
Desde `kit/`, el laboratorio usa `python 00_datos.py --descargar pqrs-completos`
y `python 00_datos.py --verificar pqrs-completos`. El grupo `pqrs` conserva
su significado: solo tres muestras.

El panorama actualizado de seis cortes se desarrolla exclusivamente en
[04 Rendimiento Analysis](04_Rendimiento_Analysis.ipynb): descarga verificable,
lectura Polars–DuckDB, Parquet común y benchmark Polars–pandas. El notebook
original y `update1` permanecen como estaban y no deben mezclarse con esta ejecución.

El notebook 04 lee los productos de P02 (`kit/salidas/pandas/P02`); no ejecuta `lab.formatos` ni `lab.benchmark`. Presenta cinco celdas medidas: pandas, Polars, DuckDB sobre Parquet, sobre particiones y sobre CSV. Cada una incluye lectura, agregación y materialización del resultado en pandas; las verificaciones y visualizaciones quedan fuera. Una vuelta de calentamiento y tres vueltas alternadas generan `benchmark_notebook.csv` y su resumen en `kit/salidas/pandas/P04`. Los tiempos del kernel no se mezclan con el benchmark CLI, que además incluye procesos nuevos, exportación y sondeo RSS.

I01 muestra `json.load`, conversión a DataFrame, `merge` de entregas con observaciones, reglas explícitas de reintento y atraso, escritura y relectura de la traza. Sus evidencias quedan también en `kit/salidas/pandas/P04`.

E08, E09 y E11 declaran una ruta editable y usan directamente `read_csv`, `read_file`, `merge`, `make_valid`, `overlay`, `to_crs`, lectura de ventanas Rasterio y exportación de archivos. Las salidas se guardan respectivamente en `kit/salidas/E08`, `kit/salidas/E09` y `kit/salidas/E11`. Los scripts automatizados conservan sus rutas anteriores y se estudian después de ejecutar y explicar las celdas.

## Ruta del fin de semana: 16 y 17 de octubre

El número 04 identifica el notebook PQRS existente, que se usa el 23 y 24 de octubre; no indica que deba ejecutarse antes de Spark. Para el 16 y 17 de octubre, seguir este orden:

1. **05 Spark, lectura y agregación:** descargar/verificar EVA y DIVIPOLA, leer CSV con pandas, convertir tipos conservando errores, escribir y releer Parquet, ejecutar agregación Spark y contrastar cada grupo con DuckDB.
2. **06 Spark, joins y ventanas:** leer los productos de 05, verificar claves, ejecutar LEFT JOIN y broadcast, contrastar el ranking con DuckDB y cambiar las particiones conservando resultados.
3. **E08 Geoespacial:** geometrías, unión municipal e intersecciones.
4. **E09 Geoespacial:** ráster, pH, perfiles y profundidad.

Preparar JDK 21 y `requirements_spark.txt` en el `.venv` base CPU de la raíz según la guía WSL o Linux/macOS. Spark usa `local[2]`. Cerrar su sesión al terminar cada notebook. 05 y 06 guardan productos en `kit/salidas/E07`; 06 requiere haber completado 05. Los scripts del kit quedan como referencia posterior de automatización. La entrega del sábado integra los controles Spark, plan explicado, consulta de ventana y evidencias E08/E09; no añade una entrega el viernes.

## Guía de consulta geográfica

La [guía práctica de GeoPandas](../../docs/manual-geopandas.md) incluye ejemplos ejecutables de mapas de Colombia, ciudades, territorios especiales, municipios resaltados y consultas de quejas por meses y edades. Se ejecuta en el entorno CPU del curso, con los ZIP DANE; distingue datos ficticios de muestras reales.
