# Soluciones de talleres PQRS

Soluciones comentadas de los talleres P01, P02 y P03. Cada notebook relaciona sus secciones con las tareas del enunciado e incluye código, verificaciones e interpretación. Los demás talleres no están cubiertos por esta carpeta.

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

Seleccionar el kernel del entorno `.venv` del curso y ejecutar las celdas en orden. Cada notebook es independiente y usa las tres muestras incluidas; no descarga los completos. Las rutas se calculan desde el repositorio y las salidas se guardan en `kit/salidas/soluciones/P01`, `P02` o `P03`. Una reejecución reemplaza las salidas de esa solución.

P03 requiere `kit/data/raw/divipola.csv` para completar el control territorial. Si no existe, muestra el control como pendiente y continúa con los demás análisis. Para prepararlo:

```bash
cd /mnt/c/Users/TUPTC/bigdata
cd big-data-postgraduate
source .venv/bin/activate
cd kit
python 00_datos.py --descargar divipola
```

## Validación

Se validó el formato de los tres notebooks y se ejecutaron todas sus celdas con las muestras locales: 3.000 filas y 38 columnas originales, proyección de 16 columnas, 8 archivos particionados, estabilidad de la reejecución, rechazo de una columna ausente y equivalencia de consultas de 2024 sobre 2.000 filas. Los notebooks se distribuyen sin salidas guardadas para que cada estudiante produzca su propia evidencia. Esta comprobación no equivale a una instalación real en Windows/WSL.
