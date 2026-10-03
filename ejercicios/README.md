# Ejercicios de pandas

Esta carpeta contiene los enunciados y las plantillas de los ejercicios PD01–PD03. Cada estudiante crea una copia de cada notebook en `soluciones/` de su propio repositorio y desarrolla allí la solución, con el nombre indicado. Las plantillas de `ejercicios/` se conservan como material de consulta.

| Enunciado y plantilla | Ruta de la solución del estudiante |
|---|---|
| [PD01 · Explorar y preparar AGROSAVIA](PD01_exploracion_agrosavia.ipynb) | `soluciones/PD01_exploracion_agrosavia.ipynb` |
| [PD02 · Consultar y resumir EVA](PD02_consultas_eva.ipynb) | `soluciones/PD02_consultas_eva.ipynb` |
| [PD03 · Integrar EVA con DIVIPOLA](PD03_integracion_territorial.ipynb) | `soluciones/PD03_integracion_territorial.ipynb` |

## Organización de las cuatro horas

Se parte del entorno del curso operativo y de los tres CSV ya descargados. La [guía práctica de pandas](../docs/manual-pandas.md) sirve como apoyo durante el desarrollo.

| Actividad | Tiempo |
|---|---:|
| Preparación, copia de plantillas y comprobación de rutas | 20 min |
| PD01 · Explorar y preparar AGROSAVIA | 60 min |
| PD02 · Consultar y resumir EVA | 70 min |
| PD03 · Integrar EVA con DIVIPOLA | 70 min |
| Reejecución y entrega | 20 min |
| **Total** | **240 min** |

## Preparación y desarrollo

1. Abrir JupyterLab desde la raíz del repositorio con el entorno `.venv` del curso activo.
2. Duplicar cada plantilla de `ejercicios/` y mover la copia a `soluciones/`, conservando el nombre de la tabla anterior. Si ya existe una solución, se continúa sobre ella.
3. Abrir la copia de `soluciones/` y seleccionar el kernel del entorno del curso.
4. Ejecutar la celda inicial de rutas y carga. Cada notebook es independiente y utiliza únicamente los CSV que necesita.
5. Completar las celdas de desarrollo e interpretación siguiendo las instrucciones. Antes de entregar, reiniciar el kernel y ejecutar todas las celdas en orden.

Los enunciados aparecen en celdas Markdown; el código se desarrolla en las celdas correspondientes. Cada actividad incluye un tiempo asignado y comprobaciones sobre los resultados.

## Archivos de entrada y resultados

Las entradas son `kit/data/raw/agrosavia.csv`, `kit/data/raw/eva.csv` y `kit/data/raw/divipola.csv`. Si falta alguna, la descarga se realiza desde la terminal, en la raíz del repositorio y con el entorno del curso activo:

```bash
python kit/00_datos.py --descargar divipola eva agrosavia
```

Los notebooks resueltos se entregan en `soluciones/`. Las tablas CSV generadas se guardan en `kit/salidas/soluciones/PD01/`, `PD02/` y `PD03/`; esas carpetas están excluidas de Git y sus archivos deben poder regenerarse al ejecutar los notebooks. Los CSV originales permanecen en `kit/data/raw/`.

## Validación de las plantillas

Se verificaron el formato de notebook, la sintaxis de las celdas, los enlaces y la suma de los tiempos. Las celdas iniciales se ejecutaron con pandas 2.2.3 desde `ejercicios/` y desde copias en `soluciones/`, utilizando únicamente los tres CSV del manifiesto. El análisis y sus conclusiones quedan pendientes del estudiante.
