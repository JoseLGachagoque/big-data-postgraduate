# Notebooks vigentes

Preparado por el PhD Esteban Hernández, CyberColombia.

P01: 3 de octubre. P02: 9 de octubre. P03: 10 de octubre. P04: 23 de octubre. I01: 24 de octubre. Los notebooks acompañan los talleres y comparten las horas de clase; no añaden entregas obligatorias.

Preparar WSL, Ubuntu-26.04 y el único entorno `.venv` de la raíz según [la guía de instalación](../../docs/instalacion-wsl.md). Abrir desde `kit/` o `kit/Notebooks/`, usar el mismo entorno Python y ejecutar en orden. Cada notebook prepara sus dependencias de datos para permitir ejecución independiente.

Los notebooks históricos se conservan en `supersalud/`, con su procedencia y limitaciones, y no son la guía de ejecución actual.

## Índice y propósito

Como referencia durante las prácticas, consultar la [guía práctica de pandas](../../docs/manual-pandas.md), con ejemplos sobre las muestras PQRS y las fuentes agroambientales del kit.

| Notebook | Talleres y clases | Evidencia |
|---|---|---|
| [01 Perfil PQRS](01_Perfil_PQRS.ipynb) | P01 · clase 2 | Conteos, esquema, hashes y memoria por tamaño de bloque |
| [02 Parquet y contratos](02_Parquet_y_contratos.ipynb) | P02 · clase 3 | Proyección de 16 columnas, particiones, reejecución y fallo de contrato |
| [03 Calidad y consulta](03_Calidad_y_consulta.ipynb) | P03 · clase 4 | Calidad sin exclusiones arbitrarias y consulta diferida de 2024 |
| [04 Rendimiento y eventos](04_Rendimiento_y_eventos.ipynb) | P04 · clase 7; I01 · clase 8 | Equivalencia entre motores y traza finita NASA |

El notebook 04 se usa en dos momentos: detenerse tras el benchmark en clase 7 y ejecutar la sección de eventos en clase 8. Los eventos requieren `data/raw/nasa.json`, que se descarga desde el manifiesto agroambiental. Los notebooks no incorporan descargas de 1,816 GB como paso automático.

Seleccionar el kernel **BigData · WSL Ubuntu 26.04 · Python 3.12**. Todas las dependencias se instalan en Ubuntu mediante el procedimiento de esa guía.

## Ruta y rama del curso

El clon se realiza siempre desde `main` en `/mnt/c/Users/TUPTC/bigdata/big-data-postgraduate`. El entorno está en `.venv` de la raíz; los ejercicios se ejecutan desde `kit/`, dentro de Ubuntu-26.04 sobre WSL. Para actualizar, situarse en `main` y ejecutar `git pull --ff-only origin main` después de revisar los cambios locales.
