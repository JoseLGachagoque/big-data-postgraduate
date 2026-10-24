# Ejercicios de pandas y Polars

Los ejercicios se organizan por fin de semana. En este índice, **sesión 1** corresponde al primer fin de semana y **sesión 2** al segundo; cada conjunto reúne las actividades asociadas a las clases del viernes y sábado.

| Sesión de ejercicios | Fin de semana | Ejercicios | Dedicación orientativa |
|---|---|---|---:|
| [Sesión 1](#sesion-1) | 2 y 3 de octubre de 2026 | PD01–PD03 | 4 horas |
| [Sesión 2](#sesion-2) | 9 y 10 de octubre de 2026 | PD04–PD05 | 8 horas |

Cada estudiante copia las plantillas de `ejercicios/` a `soluciones/` en su propio repositorio, conserva sus nombres y desarrolla allí el código y las interpretaciones. Las plantillas originales quedan como material de consulta. Los tiempos suponen el entorno instalado y los datos disponibles.

<a id="sesion-1"></a>

## Sesión 1 · Primer fin de semana: 2 y 3 de octubre

**Propósito:** explorar datos con pandas, reconocer tipos y valores ausentes, construir consultas y comprobar una integración territorial.

### Ejercicios

| Enunciado y plantilla | Trabajo del estudiante | Tiempo |
|---|---|---:|
| [PD01 · Explorar y preparar AGROSAVIA](PD01_exploracion_agrosavia.ipynb) | Inspeccionar campos, convertir pH y fechas, marcar registros para revisión y explicar los controles. | 60 min |
| [PD02 · Consultar y resumir EVA](PD02_consultas_eva.ipynb) | Filtrar datos de Boyacá, comparar consultas, calcular conteos y porcentajes y construir una tabla dinámica. | 70 min |
| [PD03 · Integrar EVA con DIVIPOLA](PD03_integracion_territorial.ipynb) | Validar códigos, revisar correspondencias y calcular rendimiento agrícola con un denominador adecuado. | 70 min |

Se destinan además **20 minutos a preparación** y **20 minutos a reejecución y entrega**: total, **240 minutos**. La [guía práctica de pandas](../docs/manual-pandas.md) sirve como apoyo.

### Entradas y orden de trabajo

- PD01: `kit/data/raw/agrosavia.csv`.
- PD02: `kit/data/raw/eva.csv`.
- PD03: `kit/data/raw/eva.csv` y `kit/data/raw/divipola.csv`.

Desarrolla PD01, PD02 y PD03 en ese orden. Cada notebook carga sus propias entradas y puede ejecutarse de manera independiente.

### Entrega de la sesión 1

| Notebook resuelto | Resultados regenerables |
|---|---|
| `soluciones/PD01_exploracion_agrosavia.ipynb` | `kit/salidas/soluciones/PD01/`: controles de AGROSAVIA. |
| `soluciones/PD02_consultas_eva.ipynb` | `kit/salidas/soluciones/PD02/`: resumen de EVA. |
| `soluciones/PD03_integracion_territorial.ipynb` | `kit/salidas/soluciones/PD03/`: rendimiento municipal y códigos sin correspondencia. |

Los notebooks deben mostrar el desarrollo, las comprobaciones y las conclusiones solicitadas. Se revisan la conservación de filas, la equivalencia de consultas, los denominadores y la interpretación de los resultados.

<a id="sesion-2"></a>

## Sesión 2 · Segundo fin de semana: 9 y 10 de octubre

**Propósito:** aplicar contratos y controles de calidad, normalizar e integrar fuentes, trabajar con CSV y Parquet, comparar pandas con Polars e integrar sus resultados con geometrías en GeoPandas.

### Ejercicios

| Enunciado y plantilla | Trabajo del estudiante | Tiempo |
|---|---|---:|
| [PD04 · Limpieza e integración territorial](PD04_limpieza_integracion_territorial.ipynb) | Limpiar y unir AGROSAVIA con DIVIPOLA; leer polígonos DANE e IGAC con GeoPandas, integrar resúmenes, crear mapas e intersectar geometrías. | 270 min |
| [PD05 · Particionamiento y comparación pandas–Polars](PD05_particionamiento_pandas_polars.ipynb) | Separar archivos con groupby, comparar lectura, escritura y procesamiento en pandas/Polars y verificar sus resultados en mapas. | 210 min |

**Total: 480 minutos (ocho horas de dedicación orientativa).** Los tiempos de cada notebook incluyen controles, publicación y reejecución. Consulta las guías de [pandas](../docs/manual-pandas.md), [Polars](../docs/manual-polars.md) y [GeoPandas](../docs/manual-geopandas.md). La duración incorpora las actividades espaciales añadidas; no representa horas adicionales en el calendario contractual.

### Entradas y orden de trabajo

1. **PD04:** lee `kit/data/raw/agrosavia.csv` y `kit/data/raw/divipola.csv` directamente con `pd.read_csv`. Lee además `dane_municipios.zip` e `igac_capacidad.json` con `gpd.read_file`. Revisa CRS y geometrías, une el resumen por código a los polígonos DANE y realiza una intersección espacial con la muestra IGAC. Las coordenadas municipales no representan la ubicación de las muestras de suelo.
2. **PD05:** requiere terminar PD04. Lee `kit/salidas/soluciones/PD04/analisis_integrados.parquet` con `pd.read_parquet` y `pl.read_parquet`. Reutiliza también la capa `municipios` de `resultados_espaciales.gpkg` con `gpd.read_file`. Compara CSV, Parquet único y dos diseños de particionamiento, separando lectura, escritura, procesamiento en memoria y consulta completa desde disco.

El particionamiento se desarrolla con `groupby`, una escritura `to_parquet` por grupo y un inventario CSV de rutas y claves. La lectura selecciona archivos por ese inventario, muestra cada llamada a `read_parquet` y concatena las partes. Las claves permanecen en los archivos.

Utiliza pandas, GeoPandas, Matplotlib, PyArrow y Polars CPU del entorno del curso, definidos en `kit/requirements.txt` y `kit/requirements_pqrs.txt`.

### Entrega de la sesión 2

| Notebook resuelto | Resultados regenerables |
|---|---|
| `soluciones/PD04_limpieza_integracion_territorial.ipynb` | `kit/salidas/soluciones/PD04/`: Parquet integrado, controles, equivalencias, resumen, registros pendientes, mapas PNG y GeoPackage de municipios e intersecciones. |
| `soluciones/PD05_particionamiento_pandas_polars.ipynb` | `kit/salidas/soluciones/PD05/`: mediciones, inventarios de particiones, controles de equivalencia y comparación de mapas PNG. |

Se revisan la conservación de originales y filas, los tipos y nulos explícitos, las correspondencias justificadas, la equivalencia de resultados, las mediciones comparables, los CRS, las áreas, la calidad geométrica y las conclusiones. No se exige que un motor gane ni que particionar siempre mejore el tiempo.

El estudiante desarrolla el código y las interpretaciones de forma autónoma. Esta organización asocia los ejercicios con el fin de semana correspondiente; no fija nuevas fechas de entrega ni modifica los porcentajes del calendario.

## Preparación y desarrollo para ambas sesiones

La **raíz del repositorio** es `big-data-postgraduate`, que contiene `README.md`, `kit/`, `ejercicios/` y `soluciones/`. En WSL se accede desde la terminal con:

```bash
cd /mnt/c/Users/TUPTC/bigdata
cd big-data-postgraduate
pwd
ls
```

Si tu copia está en otra ubicación, utiliza su ruta real. Cada notebook incluye una sección de ubicación de trabajo con una ruta editable.

1. Abre JupyterLab desde la raíz del repositorio con el entorno `.venv` activo.
2. Duplica las plantillas de la sesión en `soluciones/`, conservando los nombres indicados. Si ya existe una solución, continúa sobre ella.
3. Selecciona el kernel del curso y ajusta la ruta del repositorio.
4. Ejecuta las lecturas iniciales. Respeta la dependencia **PD04 → PD05**.
5. Completa las celdas de desarrollo e interpretación. Antes de entregar, reinicia el kernel y ejecuta todas las celdas en orden.

Los enunciados están en celdas Markdown. Las lecturas muestran rutas y opciones; las conversiones, máscaras, agrupaciones, uniones y exportaciones deben quedar visibles mediante las API de pandas, Polars y GeoPandas. No resuelvas las actividades llamando a scripts de talleres ni funciones que oculten las etapas. Los bucles de medición deben mostrar las operaciones medidas.

Si falta un CSV original, prepáralo desde la terminal, en la raíz del repositorio y con el entorno activo:

```bash
python kit/00_datos.py --descargar divipola eva agrosavia
```

Para la sesión 2 prepara también `igac_capacidad.json` con `python kit/00_datos.py --descargar igac_capacidad` y sigue la [descarga manual de cartografía DANE](../docs/entorno.md#descarga-manual-de-los-shapes-dane) para `dane_municipios.zip`. Ambos se guardan en `kit/data/raw/`.

Estos comandos solo preparan las fuentes; el análisis se desarrolla en los notebooks. Los originales permanecen en `kit/data/raw/`. Las carpetas de resultados `kit/salidas/soluciones/PD01/` a `PD05/` están excluidas de Git y deben poder regenerarse.

## Validación de las plantillas

### Sesión 1 · PD01–PD03

Para PD01–PD03 se verificaron el formato de notebook, la sintaxis de las celdas, los enlaces y la suma de los tiempos. Las celdas iniciales se ejecutaron con pandas 2.2.3 desde `ejercicios/` y desde copias en `soluciones/`, utilizando únicamente los tres CSV del manifiesto. El análisis y sus conclusiones quedan pendientes del estudiante.

### Sesión 2 · PD04–PD05

La revisión incorpora lecturas espaciales directas, unión de atributos, mapas, proyección métrica e intersección de polígonos. PD05 utiliza archivos individuales e inventarios explícitos para el particionamiento. Los tiempos de las actividades suman 270 y 210 minutos, respectivamente.

Se validaron formato de notebook, sintaxis de celdas y ejemplos, enlaces locales y tiempos. Se ejecutaron las lecturas iniciales y una comprobación técnica temporal de los flujos con pandas 2.2.3, Polars 1.35.2, GeoPandas 1.1.1 y PyArrow 19.0.1 en macOS:

- 1.122 geometrías municipales y cinco polígonos IGAC leídos en EPSG:4326; ninguna geometría ausente, vacía o inválida en estas copias.
- Nueve intersecciones poligonales de área positiva para la muestra de capacidad de uso. Capas municipales y de intersecciones exportadas y releídas en GeoPackage, conservando geometrías y CRS; mapas generados y comparación visual revisada.
- 92.738 análisis conservados al escribir y reconstruir 12 archivos por año y 373 por año/departamento. Se repitió la construcción en carpetas nuevas y se comprobó la igualdad del contenido.
- Para Boyacá en 2020, 152 análisis y 48 grupos municipales: mismos conteos y medias equivalentes en pandas y Polars, con tolerancia absoluta de 0,000001.

La comprobación temporal no se incorpora como solución del alumno y no sustituye sus controles, decisiones, conclusiones ni mediciones completas. Los conteos dependen de las copias y reglas utilizadas. Esta validación no certifica una instalación Windows/WSL ni un ganador de rendimiento.


## PD06 · PQRS completas: agregaciones en Polars CPU y GPU

[Plantilla individual PD06](PD06_PQRS_agregaciones_CPU_GPU.ipynb).
Copiar a `soluciones/` y desarrollar allí, con el kernel GPU ya verificado.
No contiene la solución de las consultas; deja celdas explícitas por completar.

1. Este ejercicio histórico conserva sus tres cortes originales. Desde la raíz, ejecutar
   `python kit/pqrs_descarga.py --descargar 2023_II 2024_I 2024_II` y
   `python kit/pqrs_descarga.py --verificar 2023_II 2024_I 2024_II`.
2. Leer y convertir CSV a Parquet con Polars; conservar las 2.444.766 filas.
3. Buscar departamentos con más quejas según edad, `patologia_1`,
   `cod_motesp`, `motivo_especifico` y `pqr_canal`, combinando todos los periodos.
4. Añadir año y mes numéricos para estudiar la evolución cronológica ascendente
   de las mismas combinaciones, sin ordenar meses como texto.
5. Ejecutar las mismas agregaciones y ordenaciones con Polars CPU y GPU,
   comprobar equivalencia y medir calentamiento más tres repeticiones por motor.

El benchmark incluye lectura Parquet, agregación, ordenamiento y resultado CPU;
excluye preparación, controles y exportación. La plantilla facilita el reloj y
el resumen; las consultas y el bucle de repeticiones los desarrolla el estudiante.
Los resultados van en `kit/salidas/soluciones/PD06/`. No exige pandas ni añade
una ponderación o fecha de entrega. La plantilla se entrega **sin ejecutar**.
