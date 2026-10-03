# Curso de Postgrado: BigData, Especialización en Bases de datos

Preparado por el PhD Esteban Hernández, CyberColombia.

**64 horas efectivas de clase en línea**, del **2 de octubre al 7 de noviembre de 2026**. Doce encuentros en seis fines de semana. Los recesos y almuerzos se excluyen; el trabajo autónomo no integra el cómputo.

[Programa](docs/programa.md) · [Calendario contractual](docs/calendario.md) · [Guía por sesiones](docs/agenda.md) · [Metodología](docs/metodologia.md) · [Datasets](docs/datasets.md) · [Entorno y descargas](docs/entorno.md) · [Controles docentes](docs/controles-docente.md)

El curso emplea dos dominios abiertos: PQRS/PQRD de Supersalud y datos agroambientales de suelo, territorio, rendimiento agrícola y clima. Los dominios conservan sus unidades; no se unen filas de reportes de salud con muestras de suelo.

## Preparar el equipo

Seguir la [guía Windows → WSL 2 → Ubuntu-26.04](docs/instalacion-wsl.md): listar distribuciones, instalar Ubuntu-26.04, entrar a `/mnt/c/Users/TUPTC/bigdata`, clonar el repositorio y preparar Python 3.12, Java, Jupyter y las bibliotecas dentro de Ubuntu. Esta es la base de todas las instrucciones vigentes de instalación.

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
| Viernes 30/10/2026 | [Analítica y gobernanza](clases/09-analitica-y-gobernanza/README.md) | 18:00–21:15 | 3 h |
| Sábado 31/10/2026 | [Integración y auditoría del proyecto](clases/10-integracion-y-defensa/README.md) | 08:00–17:00 | 7 h 30 min |
| Viernes 06/11/2026 | [Clínica de proyectos y ensayo de defensa](clases/11-clinica-de-proyectos/README.md) | 18:00–21:15 | 3 h |
| Sábado 07/11/2026 | [Sustentación y cierre contractual](clases/12-sustentacion-y-cierre/README.md) | 08:00–16:30 | 7 h |

## Recursos actuales

- [Soluciones comentadas en Jupyter de P01, P02 y P03](soluciones/README.md).
- [Índice completo de talleres](talleres/README.md), con descargas, tamaños y criterios.
- [Kit base](kit/LEEME.txt), [manifesto agroambiental](kit/fuentes.json) y [manifiesto PQRS](kit/pqrs_fuentes.json).
- [Descargador PQRS](kit/pqrs_descarga.py) y [prácticas reproducibles PQRS](kit/pqrs_talleres.py).
- [Proyecto y evaluación por dominio](proyecto/README.md) y [mapa de ejercicios y prerrequisitos](docs/mapa-ejercicios.md).
- [Notebooks actuales](kit/Notebooks/README.md) y [notebooks históricos Supersalud](supersalud/README.md), preservados como referencia.

Los originales agroambientales suman 136,4 MB; los tres completos PQRS, 1,816 GB. Las tres muestras reales incluidas suman 2,235 MB. Los originales voluminosos y salidas se excluyen de Git. La instalación se comprueba durante la clase 2 y el docente ofrece una copia validada para continuidad de los talleres.

## Cierre del proyecto

31 de octubre: candidato y auditoría. 6 de noviembre: clínica, correcciones y ensayo. 7 de noviembre: sustentación, entrega final y cierre contractual.

## Ruta y rama del curso

El clon se realiza siempre desde `main` en `/mnt/c/Users/TUPTC/bigdata/big-data-postgraduate`. El entorno está en `.venv` de la raíz; los ejercicios se ejecutan desde `kit/`, dentro de Ubuntu-26.04 sobre WSL. Para actualizar, situarse en `main` y ejecutar `git pull --ff-only origin main` después de revisar los cambios locales.

La [revisión de rutas](docs/revision-rutas.md) detalla las ubicaciones de trabajo y el alcance de la validación.
