# Mapa de ejercicios y evaluación

[Índice](../README.md) · [Programa](programa.md) · [Calendario](calendario.md)

Las doce clases suman 64 horas efectivas. Las actividades comparten los bloques existentes: no se exige repetir todas las prácticas en ambos dominios ni ejecutar los notebooks históricos completos. Cada entrega reúne la evidencia producida en clase; una ampliación sustituye una actividad equivalente.

| Clases | Ruta y prerrequisitos | Evidencia única | Peso |
|---|---|---|---|
| 1–2 | T01 y E01–E03; P01 con las tres muestras PQRS | Pregunta, presupuesto de recursos, manifiesto, perfil y claves territoriales | 10 % |
| 3–4 | E04–E06 y P02–P03; ejecutar formatos antes de calidad PQRS | Contrato, conciliación, proyección Parquet, prueba de reejecución y consulta | 10 % |
| 5–6 | E07 después de calidad/consultas agroambientales; E08–E09 con geometrías y rásteres | Equivalencia Spark/DuckDB, cardinalidad y mapa con cobertura explícita | 10 % |
| 7–8 | P04 con seis cortes completos 2023–2025; lectura Polars–DuckDB y benchmark Polars–pandas; I01/E11 con NASA y fuentes de clima | Un informe experimental y una traza de eventos | 20 % |
| 9–12 | E12 como práctica común de evaluación temporal; E13 en el dominio elegido | Producto candidato el 31/10, clínica docente sin entrega el 06/11, informe final | 35 % |
| 12 | E13 con evidencias reconstruibles | Sustentación final el 07/11 y explicación individual | 15 % |

## Política de entrega

Viernes: explicación y demostraciones guiadas por el profesor, sin entregas ni calificación. El profesor ejecuta, explica y comparte sus archivos de referencia; los estudiantes observan, preguntan y pueden seguir voluntariamente. Sábado: ejecución por los estudiantes, revisión y entrega durante la clase. La evidencia evaluable debe corresponder a su propia ejecución. No se exige una entrega ni trabajo autónomo obligatorio entre ambos encuentros.

E = ejercicio general del curso (E01–E13). P = práctica con datos PQRS (P01–P04); PQRS significa peticiones, quejas, reclamos y sugerencias. El número identifica la actividad, no la sesión. T01 = taller teórico de capacidad; I01 = introducción a eventos NASA.

Las fechas y cierres de las seis entregas están en [Entregas sabatinas](entregas-sabados.md). El candidato del 31/10 es formativo; el bloque E12–E13 se califica con 35 % sobre la versión final del 07/11.

## Orden mínimo de ejecución

En la clase 2, ejecutar [P01 paso a paso con pandas](../kit/Notebooks/01_Perfil_PQRS.ipynb): cada lectura y control queda visible. Después de esta clase, estos comandos automatizan las operaciones ya estudiadas; desde `kit/`, con el entorno activo:

```sh
python pqrs_talleres.py perfil
python pqrs_talleres.py formatos
python pqrs_talleres.py calidad
python pqrs_talleres.py benchmark --repeticiones 3
python pqrs_talleres.py eventos
```

Perfil, formatos, calidad y benchmark usan las muestras incluidas por defecto. Eventos requiere `data/raw/nasa.json`. El notebook P03 requiere DIVIPOLA para desarrollar los joins; descargarla antes de ejecutarlo. P02 y P03 muestran las operaciones pandas y no llaman al script para resolverlas. P03 requiere el Parquet de P02 y DIVIPOLA para sus joins. Las celdas se distribuyen entre las clases correspondientes, no se ejecutan todas en cada encuentro.

Para la ruta agroambiental: `talleres.py calidad` → `talleres.py consultas` → `spark_taller.py lotes` o `talleres.py modelo`. Geografía necesita DANE e IGAC; `talleres.py suelo` lee SoilGrids y WoSIS; `talleres.py clima` lee NASA y CHIRPS. E11 lee NASA para Spark.

## Uso de Supersalud histórico y actual

| Material original | Actividad vigente | Ajuste didáctico |
|---|---|---|
| Sesiones históricas 1 y 2, duplicadas | P01 y P03 | Medir perfil y faltantes sin inferir anonimato o errores por edad alta |
| Sesión histórica 3 | P02 | Validar contrato y reejecución; registrar incidencias localmente, sin correo |
| Sesión histórica 4, comparación de motores | E10/P04 | CPU, consulta equivalente, calentamiento, tres repeticiones y memoria observada |
| Sesión histórica 4, índices | E12: discusión de gobernanza | Revisar variables ausentes y supuestos; no fabricar puntuaciones clínicas |
| Sesión histórica 4, bucles de streaming | I01 y E11 | Traza finita con observaciones NASA; distinguir reintentos, atraso y semántica de Spark |

## Límites del alcance

P04 exige los seis cortes semestrales completos de 2023, 2024 y 2025. La preparación incluye localizar los archivos faltantes en el portal oficial, conservar huellas y procedencia, conciliar primero Polars con DuckDB y construir una entrada Parquet común. El benchmark posterior compara Polars con pandas mediante calentamiento y tres repeticiones; la preparación y la descarga quedan fuera del reloj. La ejecución guiada está en [04 Rendimiento Analysis](../kit/Notebooks/04_Rendimiento_Analysis.ipynb).

I01 no implementa recuperación ni toda la semántica de Spark. E11 crea un checkpoint nuevo por ejecución: el entregable básico es una traza y un análisis de recuperación, no afirmar que se probó reinicio desde el mismo estado. Un experimento de recuperación real puede sustituir una ampliación si se implementa y documenta.

E12 evalúa persistencia sobre EVA para todos los equipos. Ese resultado metodológico se identifica aparte del proyecto PQRS; no se mezcla con tasas de salud. Los proyectos PQRS pueden mostrar distribución de reportes por territorio, sin calcular tasas poblacionales si faltan denominadores compatibles y validados.

## Entorno de referencia

Todas las instalaciones de Python, entornos virtuales, bibliotecas y herramientas del curso parten de [WSL 2 con Ubuntu-26.04](instalacion-wsl.md). Los scripts y notebooks se ejecutan en el entorno de Ubuntu descrito allí.

## Ruta y rama del curso

El clon se realiza siempre desde `main` en `/mnt/c/Users/TUPTC/bigdata/big-data-postgraduate`. El entorno está en `.venv` de la raíz; los ejercicios se ejecutan desde `kit/`, dentro de Ubuntu-26.04 sobre WSL. Para actualizar, situarse en `main` y ejecutar `git pull --ff-only origin main` después de revisar los cambios locales.

Las actividades geoespaciales E08, E09 y E11 se desarrollan con GeoPandas, Rasterio y Matplotlib en Jupyter. Consultar los [notebooks y sus requisitos](../kit/Notebooks/README.md#ejercicios-geoespaciales).
