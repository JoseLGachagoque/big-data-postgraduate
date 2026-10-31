# Soluciones

Esta carpeta es el destino de las soluciones desarrolladas por cada estudiante. También contiene las soluciones comentadas de referencia P01–P03 sobre PQRS.

## Entregas de los ejercicios de pandas

Los enunciados y las plantillas de PD01–PD05 están en [`ejercicios/`](../ejercicios/README.md), junto con la distribución del primer bloque de cuatro horas y la ampliación de ocho horas. Cada plantilla debe copiarse a esta carpeta antes de comenzar el desarrollo en el repositorio del estudiante.

| Ejercicio | Nombre obligatorio del notebook resuelto en esta carpeta |
|---|---|
| [PD01 · Explorar y preparar AGROSAVIA](../ejercicios/PD01_exploracion_agrosavia.ipynb) | `PD01_exploracion_agrosavia.ipynb` |
| [PD02 · Consultar y resumir EVA](../ejercicios/PD02_consultas_eva.ipynb) | `PD02_consultas_eva.ipynb` |
| [PD03 · Integrar EVA con DIVIPOLA](../ejercicios/PD03_integracion_territorial.ipynb) | `PD03_integracion_territorial.ipynb` |

PD04 y PD05 continúan los temas de limpieza, integración, formatos y particionamiento:

| Ejercicio | Nombre del notebook resuelto |
|---|---|
| [PD04 · Limpieza e integración territorial](../ejercicios/PD04_limpieza_integracion_territorial.ipynb) | `PD04_limpieza_integracion_territorial.ipynb` |
| [PD05 · Particionamiento y comparación pandas–Polars](../ejercicios/PD05_particionamiento_pandas_polars.ipynb) | `PD05_particionamiento_pandas_polars.ipynb` |

Ejecuta PD04 antes de PD05. Sus resultados se guardan en `kit/salidas/soluciones/PD04/` y `PD05/`. PD04 añade mapas e intersecciones con GeoPandas y exporta un GeoPackage; PD05 compara los resultados tabulares de ambos motores sobre la misma cartografía. El particionamiento usa grupos, archivos individuales e inventarios CSV. Todas las lecturas y transformaciones se desarrollan con las API visibles en las celdas, sin scripts que oculten el procedimiento.

Cada solución debe incluir el código completado, las comprobaciones y la interpretación de los resultados. Antes de entregar, se reinicia el kernel y se ejecutan todas las celdas en orden.

Las tablas CSV se generan en `kit/salidas/soluciones/PD01/`, `PD02/` y `PD03/`. Esas carpetas están excluidas de Git: las tablas deben poder regenerarse al ejecutar el notebook. Las entradas originales se conservan en `kit/data/raw/`.

## Soluciones comentadas de referencia PQRS

Las soluciones P01, P02, P03 y E12 relacionan sus secciones con las tareas de cada taller e incluyen código, verificaciones e interpretación.

| Taller | Solución | Evidencias |
|---|---|---|
| [P01](../talleres/P01.md) | [Perfil y lectura por bloques](P01_solucion.ipynb) | Manifiesto, perfiles con bloques 100/500/1000, diccionario y límites |
| [P02](../talleres/P02.md) | [Parquet, contrato y reejecución](P02_solucion.ipynb) | 16 columnas, conciliación de particiones, dos ejecuciones y fallo de contrato |
| [P03](../talleres/P03.md) | [Calidad y consulta diferida](P03_solucion.ipynb) | Controles, política de decisión y equivalencia Polars/SQL |
| [E12](../talleres/E12.md) | [Pipeline local integrado](E12_solucion.ipynb) | Entradas verificadas, detalle y rechazados, agregado Parquet, conciliación DuckDB, dos ejecuciones estables, publicación identificada y auditoría |

## Abrir en WSL

Preparar primero el entorno según la [guía de instalación](../docs/instalacion-wsl.md). No instalar paquetes desde los notebooks.

```bash
cd /mnt/c/Users/TUPTC/bigdata
cd big-data-postgraduate
source .venv/bin/activate
jupyter lab soluciones/
```

Seleccionar el kernel del entorno `.venv` del curso y ejecutar las celdas en orden. Los notebooks de referencia usan las tres muestras PQRS incluidas; no descargan los completos. P03 requiere ejecutar P02 y disponer de DIVIPOLA. P01 declara una ruta WSL editable, desarrolla las operaciones directamente con pandas y guarda sus controles en `kit/salidas/clase2/P01`. P02 y P03 declaran rutas WSL editables y muestran las operaciones con pandas. Guardan sus salidas en `kit/salidas/pandas/P02` o `P03`. Una reejecución reemplaza las salidas de esa solución.

P03 requiere `kit/data/raw/divipola.csv` para completar el control territorial. Si no existe, se detiene con una indicación para preparar el catálogo antes de ejecutar los joins. Para prepararlo:

```bash
cd /mnt/c/Users/TUPTC/bigdata
cd big-data-postgraduate
source .venv/bin/activate
cd kit
python 00_datos.py --descargar divipola
```

## Validación

La validación de las plantillas PD01–PD03 se documenta en el [índice de ejercicios](../ejercicios/README.md#validación-de-las-plantillas). Cada estudiante debe comprobar la ejecución completa de sus soluciones antes de entregar.

Se validó el formato de las soluciones P01, P02 y P03 y se ejecutaron todas sus celdas con las muestras locales: 3.000 filas y 38 columnas originales, proyección de 16 columnas, 8 archivos particionados, estabilidad de la reejecución, rechazo de una columna ausente y equivalencia de consultas de 2024 sobre 2.000 filas. E12 se ejecutó de principio a fin con las mismas tres muestras: 3.000 filas conciliadas, 687 grupos, igualdad por grupo y total en DuckDB y firmas de contenido idénticas entre dos ejecuciones. E12 conserva sus resultados de referencia en el notebook; las salidas regenerables permanecen excluidas de Git. Esta comprobación no equivale a una instalación real en Windows/WSL.
