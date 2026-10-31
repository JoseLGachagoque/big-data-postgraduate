# Curso de Postgrado: BigData, Especialización en Bases de datos

Preparado por el PhD Esteban Hernández, CyberColombia.

**64 horas efectivas de clase en línea**, del **2 de octubre al 7 de noviembre de 2026**. Doce encuentros en seis fines de semana. Los recesos y almuerzos se excluyen; el trabajo autónomo no integra el cómputo.

[Programa](docs/programa.md) · [Calendario contractual](docs/calendario.md) · [Guía por sesiones](docs/agenda.md) · [Metodología](docs/metodologia.md) · [Datasets](docs/datasets.md) · [Entorno y descargas](docs/entorno.md) · [Controles docentes](docs/controles-docente.md) · [Guías complementarias](#guías-complementarias)

El curso emplea dos dominios abiertos: PQRS/PQRD de Supersalud y datos agroambientales de suelo, territorio, rendimiento agrícola y clima. Los dominios conservan sus unidades; no se unen filas de reportes de salud con muestras de suelo.

## Preparar el equipo

Antes de los talleres, preparar el ambiente siguiendo la guía del sistema operativo. Ambas preparan Git, Python 3.12, un `.venv` base CPU, JDK Java 21, Spark, Jupyter y las bibliotecas fijadas del curso:

- [Windows: WSL 2 con Ubuntu-26.04](docs/instalacion-wsl.md).
- [Linux: instalación nativa](docs/instalacion-linux-macos.md#linux), con paquetes para Ubuntu/Debian y Fedora.
- [macOS: Apple Silicon M1, M2, M3, M4 e Intel](docs/instalacion-linux-macos.md#macos), con Homebrew y `brew install --cask temurin@21` para instalar el JDK 21 en ambas arquitecturas.

- [Entornos virtuales por plataforma](docs/entornos-virtuales.md): creación, activación, kernels y alternativa Windows nativa para las guías rápidas.
- [Polars con GPU NVIDIA, instalación opcional independiente](docs/polars-gpu.md): prerrequisitos del sistema, CUDA y entorno GPU. No forma parte de la instalación base.

### Instrucciones generales de preparación

1. **Revisar el equipo:** identificar sistema operativo y arquitectura, disponer de conexión a Internet y permisos de administrador para instalar herramientas. Planificar 16 GB de RAM y 20 GB libres; con 8 GB, comenzar con muestras y Spark `local[2]`.
2. **Elegir dónde ejecutar:** en Windows, instalar WSL 2 y trabajar dentro de Ubuntu; en Linux y macOS, usar la terminal nativa. Los comandos PowerShell de la guía WSL se ejecutan en Windows y los bloques Bash, dentro de Ubuntu.
3. **Instalar herramientas y clonar el curso:** seguir la guía elegida para instalar Git y JDK 21, clonar `main` y preparar Python 3.12 mediante `uv`, sin reemplazar el Python del sistema.
4. **Crear el entorno base CPU:** mantener `.venv` en la raíz del repositorio e instalar allí los requisitos base, PQRS y notebooks; Spark se añade en su etapa. La ampliación GPU usa `.venv-gpu` según su guía independiente. No compartir ese entorno entre Windows, WSL, Linux, macOS o arquitecturas distintas.
5. **Configurar Java y Jupyter:** establecer `JAVA_HOME`, comprobar `java -version` y `javac -version` (ambos 21), registrar el kernel y seleccionarlo en los notebooks. En macOS, verificar además que Java corresponda a ARM64 o Intel según el equipo.
6. **Verificar antes del taller:** comprobar Python 3.12, ejecutar `python -m pip check`, realizar la prueba de Spark de la guía y abrir un notebook con el kernel del curso. Adaptar las rutas y preparar los datos según [datos y ejecución](docs/entorno.md).

Al retomar el trabajo, activar `.venv` y cargar `~/.config/bigdata/entorno.sh` antes de iniciar Jupyter. Las guías incluyen los comandos completos y la solución de problemas frecuentes.

## Encuentros

| Fecha | Clase | Horario | Horas efectivas |
|---|---|---|---|
| Viernes 02/10/2026 | [Fundamentos y escala](clases/01-fundamentos-y-problema/README.md) | 18:00–22:00 | 3 h 45 min |
| Sábado 03/10/2026 | [Ingesta y perfilado](clases/02-entorno-y-exploracion/README.md) | 08:00–17:00 | 7 h 30 min |
| Viernes 09/10/2026 | [Arquitecturas, formatos y pipelines](clases/03-arquitecturas-y-formatos/README.md) | 18:00–22:00 | 3 h 45 min |
| Sábado 10/10/2026 | [Calidad e integración](clases/04-calidad-y-duckdb/README.md) | 08:00–17:00 | 7 h 30 min |
| Viernes 16/10/2026 | [Procesamiento con Spark](clases/05-ejecucion-spark/README.md) | 18:00–21:15 | 3 h |
| Sábado 17/10/2026 | [Consultas e integración distribuida](clases/06-consultas-joins-y-ventanas/README.md) | 08:00–17:00 | 7 h 30 min |
| Viernes 23/10/2026 | [Rendimiento y escalabilidad](clases/07-rendimiento/README.md) | 18:00–21:15 | 3 h |
| Sábado 24/10/2026 | [Streaming de eventos](clases/08-streaming/README.md) | 08:00–17:00 | 7 h 30 min |
| Viernes 30/10/2026 | [Integración del pipeline y publicación de datos](clases/09-analitica-y-gobernanza/README.md) | 18:00–21:15 | 3 h |
| Sábado 31/10/2026 | [Ejecución y auditoría del pipeline](clases/10-integracion-y-defensa/README.md) | 08:00–17:00 | 7 h 30 min |
| Viernes 06/11/2026 | [Clínica de proyectos y ensayo de defensa](clases/11-clinica-de-proyectos/README.md) | 18:00–21:15 | 3 h |
| Sábado 07/11/2026 | [Sustentación y cierre contractual](clases/12-sustentacion-y-cierre/README.md) | 08:00–16:30 | 7 h |

## Guías complementarias

Material de consulta y práctica para acompañar los ejercicios del curso.

- [Guía de línea de comandos de Linux](docs/guia-cli-linux/README.md): se anexó como apoyo para personas con poca experiencia en la CLI de Linux. Incluye navegación, manejo de archivos, `grep`, `wc`, AWK, verificaciones rápidas y un cheat sheet de 100 comandos con sus opciones habituales. Disponible en [PDF](docs/guia-cli-linux/Guia_Linea_de_Comandos.pdf) y [HTML](docs/guia-cli-linux/index.html).

- [Git y GitHub: flujo de trabajo de los ejercicios](docs/guia-git/README.md): guía ilustrada sobre clones, forks, ramas, commits, PR, trabajo compartido y resolución de conflictos. Incluye seis escenarios y un desafío integrador. La [versión HTML](docs/guia-git/index.html) puede abrirse en el navegador después de clonar o descargar el repositorio; sus imágenes están incluidas en la misma carpeta.
- [Panorama OpenSource 2026](docs/panorama-opensource-2026.md): mapa en alta resolución de las capas de una plataforma moderna de Big Data y Lakehouse, desde gobernanza hasta formatos físicos. Incluye una explicación breve y el enlace oficial de cada producto representado.
- [Guía práctica de pandas](docs/manual-pandas.md): inspección, filtros, consultas y operaciones sobre los CSV del curso.
- [Guía rápida de Polars](docs/manual-polars.md): ejemplos mínimos, equivalencias con pandas y ventajas de las expresiones y la ejecución diferida.
- [Polars con GPU NVIDIA: instalación y ejecución CPU/GPU](docs/polars-gpu.md): **solo para equipos con GPU NVIDIA compatible en Linux o WSL 2**; requiere controlador y CUDA Toolkit compatibles. Incluye entorno GPU independiente, selección del motor y regreso a CPU. Es opcional; los talleres funcionan en CPU.
- [Guía rápida de DuckDB](docs/manual-duckdb.md): ejemplos mínimos de SQL, comparaciones con pandas y consultas sobre archivos Parquet.
- [Guía práctica de GeoPandas y mapas de Colombia](docs/manual-geopandas.md): departamentos, ciudades, municipios y territorios especiales; resaltado de regiones y consultas de quejas por meses y edades representadas en mapas.
- Preparación del entorno: [Windows/WSL](docs/instalacion-wsl.md) o [Linux/macOS](docs/instalacion-linux-macos.md).

## Recursos actuales

- [Ejercicios de pandas y Polars](ejercicios/README.md): PD01–PD03 (cuatro horas) y PD04–PD05 (ocho horas), con enunciados y plantillas en `ejercicios/` y entrega de los notebooks resueltos en `soluciones/`.
- [Soluciones comentadas en Jupyter de P01, P02, P03 y E12](soluciones/README.md).
- [Índice completo de talleres](talleres/README.md), con descargas, tamaños y criterios.
- [Kit base](kit/README.md), [manifiesto agroambiental](kit/fuentes.json), [manifiesto PQRS base](kit/pqrs_fuentes.json) y [cortes adicionales 2023–2025](kit/pqrs_fuentes_adicionales_2023_2025.json).
- [Descargador PQRS](kit/pqrs_descarga.py) y [prácticas reproducibles PQRS](kit/pqrs_talleres.py).
- [Proyecto y evaluación por dominio](proyecto/README.md) y [mapa de ejercicios y prerrequisitos](docs/mapa-ejercicios.md).
- [Notebooks actuales](kit/Notebooks/README.md) y [notebooks históricos Supersalud](supersalud/README.md), preservados como referencia.

Los originales agroambientales suman 136,4 MB. P04 utiliza seis cortes completos PQRS de 2023–2025: 5.327.501 registros y aproximadamente 3,830 GB descomprimidos. Las tres muestras reales incluidas suman 2,235 MB. Los originales voluminosos y salidas se excluyen de Git. La instalación se comprueba durante la clase 2 y el docente ofrece una copia validada para continuidad de los talleres.

## Temario del 30 y 31 de octubre

[Temario desarrollado](docs/temario-30-31-octubre.md) y [guía de pipelines y DataOps](docs/pipelines-dataops.md): primero propósito y conceptos, después esquemas industriales (ETL, ELT, Medallion y CDC), ejemplo PQRS y ejercicios guiados. La aplicación integra validación, publicación Parquet, SQL y reejecución. E12 se incorpora al candidato del proyecto; la predicción EVA queda como referencia opcional. La [solución integrada E12](soluciones/E12_solucion.ipynb) ejecuta el recorrido completo con las tres muestras PQRS.

## Cierre del proyecto

31 de octubre: candidato y auditoría. 6 de noviembre: clínica, correcciones y ensayo. 7 de noviembre: sustentación, entrega final y cierre contractual.

## Ruta y rama del curso

El clon se realiza siempre desde `main`: en Windows/WSL se usa `/mnt/c/Users/TUPTC/bigdata/big-data-postgraduate` y en Linux/macOS `~/bigdata/big-data-postgraduate`. El entorno está en `.venv` de la raíz; los scripts se ejecutan desde `kit/` en el sistema elegido. Para actualizar, situarse en `main` y ejecutar `git pull --ff-only origin main` después de revisar los cambios locales.

La [revisión de rutas](docs/revision-rutas.md) detalla las ubicaciones de trabajo y el alcance de la validación.

## Entregas y actividades

Viernes: explicación y demostraciones guiadas por el profesor, sin entregas ni calificación. El profesor ejecuta, explica y comparte sus archivos de referencia; los estudiantes observan, preguntan y pueden seguir voluntariamente. Sábado: ejecución por los estudiantes, revisión y entrega durante la clase. La evidencia evaluable debe corresponder a su propia ejecución. No se exige una entrega ni trabajo autónomo obligatorio entre ambos encuentros.

E = ejercicio general del curso (E01–E13). P = práctica con datos PQRS (P01–P04); PQRS significa peticiones, quejas, reclamos y sugerencias. El número identifica la actividad, no la sesión. T01 = taller teórico de capacidad; I01 = introducción a eventos NASA.

[Fechas y cambios de las entregas](docs/entregas-sabados.md).

Las actividades geoespaciales E08, E09 y E11 se desarrollan con GeoPandas, Rasterio y Matplotlib en Jupyter. Consultar los [notebooks y sus requisitos](kit/Notebooks/README.md#ejercicios-geoespaciales).
