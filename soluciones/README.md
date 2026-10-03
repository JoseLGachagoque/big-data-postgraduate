# Soluciones y ejercicios de pandas

Esta carpeta contiene los ejercicios de pandas PD01–PD03 para completar en el repositorio de cada estudiante y las soluciones comentadas de referencia P01–P03 sobre PQRS.

## Ejercicios de pandas · cuatro horas

Los ejercicios utilizan únicamente `agrosavia.csv`, `eva.csv` y `divipola.csv`, descargados con `kit/00_datos.py` y ubicados en `kit/data/raw/`. Se parte del entorno del curso operativo y de los archivos ya descargados. La [guía práctica de pandas](../docs/manual-pandas.md) sirve como apoyo durante el desarrollo.

| Actividad | Notebook | Tiempo |
|---|---|---:|
| Preparación y comprobación de rutas | Selección del kernel y revisión de entradas | 20 min |
| PD01 · Explorar y preparar AGROSAVIA | [PD01_exploracion_agrosavia.ipynb](PD01_exploracion_agrosavia.ipynb) | 60 min |
| PD02 · Consultar y resumir EVA | [PD02_consultas_eva.ipynb](PD02_consultas_eva.ipynb) | 70 min |
| PD03 · Integrar EVA con DIVIPOLA | [PD03_integracion_territorial.ipynb](PD03_integracion_territorial.ipynb) | 70 min |
| Reejecución y entrega | Reinicio del kernel, ejecución en orden y revisión de evidencias | 20 min |
| **Total** | | **240 min** |

Cada notebook es independiente e incluye una celda inicial de rutas y carga, instrucciones en Markdown, celdas de código para completar y espacios para interpretar los resultados. Las actividades tienen tiempos asignados y comprobaciones explícitas. La entrega consiste en completar estos tres archivos dentro de `soluciones/` del repositorio de cada estudiante.

Las tablas CSV se generan en `kit/salidas/soluciones/PD01/`, `PD02/` y `PD03/`. Esas carpetas están excluidas de Git: las tablas deben poder regenerarse al ejecutar el notebook. Las entradas originales se conservan en `kit/data/raw/`.

Si falta alguna entrada, la descarga se realiza desde la terminal, en la raíz del repositorio y con el entorno del curso activo:

```bash
python kit/00_datos.py --descargar divipola eva agrosavia
```

## Soluciones comentadas de referencia PQRS

Las soluciones P01, P02 y P03 relacionan sus secciones con las tareas de cada taller e incluyen código, verificaciones e interpretación.

| Taller | Solución | Evidencias |
|---|---|---|
| [P01](../talleres/P01.md) | [Perfil y lectura por bloques](P01_solucion.ipynb) | Manifiesto, perfiles con bloques 100/500/1000, diccionario y límites |
| [P02](../talleres/P02.md) | [Parquet, contrato y reejecución](P02_solucion.ipynb) | 16 columnas, conciliación de particiones, dos ejecuciones y fallo de contrato |
| [P03](../talleres/P03.md) | [Calidad y consulta diferida](P03_solucion.ipynb) | Controles, política de decisión y equivalencia Polars/SQL |

## Abrir en WSL

Preparar primero el entorno según la [guía de instalación](../docs/instalacion-wsl.md). No instalar paquetes desde los notebooks.

```bash
cd /mnt/c/Users/TUPTC/bigdata
cd big-data-postgraduate
source .venv/bin/activate
jupyter lab soluciones/
```

Seleccionar el kernel del entorno `.venv` del curso y ejecutar las celdas en orden. Los notebooks de referencia P01, P02 y P03 son independientes y usan las tres muestras PQRS incluidas; no descargan los completos. Sus rutas se calculan desde el repositorio y sus salidas se guardan en `kit/salidas/soluciones/P01`, `P02` o `P03`. Una reejecución reemplaza las salidas de esa solución.

P03 requiere `kit/data/raw/divipola.csv` para completar el control territorial. Si no existe, muestra el control como pendiente y continúa con los demás análisis. Para prepararlo:

```bash
cd /mnt/c/Users/TUPTC/bigdata
cd big-data-postgraduate
source .venv/bin/activate
cd kit
python 00_datos.py --descargar divipola
```

## Validación

En PD01, PD02 y PD03 se validaron el formato de notebook, la sintaxis de las celdas, los enlaces y los tiempos asignados. Las celdas iniciales se ejecutaron con pandas 2.2.3 desde una carpeta `soluciones/` temporal con únicamente los tres CSV del manifiesto. El código de desarrollo y sus conclusiones quedan pendientes del estudiante; esta comprobación valida las plantillas y su carga de datos.

Se validó el formato de las soluciones P01, P02 y P03 y se ejecutaron todas sus celdas con las muestras locales: 3.000 filas y 38 columnas originales, proyección de 16 columnas, 8 archivos particionados, estabilidad de la reejecución, rechazo de una columna ausente y equivalencia de consultas de 2024 sobre 2.000 filas. Los notebooks se distribuyen sin salidas guardadas para que cada estudiante produzca su propia evidencia. Esta comprobación no equivale a una instalación real en Windows/WSL.
