# Clase 2: Ingesta y perfilado

Preparado por el PhD Esteban Hernández, CyberColombia.

Sábado 03/10/2026. 08:00–17:00. 450 minutos efectivos.

**Modalidad:** Actividad estudiantil y entrega en clase.

Viernes: explicación y demostraciones guiadas por el profesor, sin entregas ni calificación. El profesor ejecuta, explica y comparte sus archivos de referencia; los estudiantes observan, preguntan y pueden seguir voluntariamente. Sábado: ejecución por los estudiantes, revisión y entrega durante la clase. La evidencia evaluable debe corresponder a su propia ejecución. No se exige una entrega ni trabajo autónomo obligatorio entre ambos encuentros.

E = ejercicio general del curso (E01–E13). P = práctica con datos PQRS (P01–P04); PQRS significa peticiones, quejas, reclamos y sugerencias. El número identifica la actividad, no la sesión. T01 = taller teórico de capacidad; I01 = introducción a eventos NASA.

| Horario | Tema y actividad |
|---|---|
| 08:00–08:45 | Entorno, estructura y verificación del kit |
| 08:45–09:30 | P01: manifiesto PQRS y lectura de las muestras |
| 09:30–09:45 | Receso de la mañana |
| 09:45–11:15 | E02: descarga selectiva, SHA-256 y perfil tabular |
| 11:15–12:00 | Tipos, ausencias, unidades y discusión del perfil |
| 12:00–13:00 | Almuerzo |
| 13:00–14:30 | E03: DIVIPOLA y claves territoriales |
| 14:30–15:00 | P01: lectura por bloques y presupuesto de RAM |
| 15:00–15:15 | Receso de la tarde |
| 15:15–16:00 | Revisión por pares y faltantes territoriales |
| 16:00–16:45 | Ficha propia E01/T01, contrato inicial y diccionario de variables |
| 16:45–17:00 | Entrega y preparación del siguiente encuentro |

**Entrega:** Ficha de problema, presupuesto de recursos, manifiesto, perfil y claves territoriales. Cierre 16:45–17:00.

[Calendario](../../docs/calendario.md) · [Entregas sabatinas](../../docs/entregas-sabados.md) · [Talleres y evaluación](../../docs/mapa-ejercicios.md)

## Trabajo directo con pandas

**Presentación disponible:** [Ingesta y perfilado v5](02_Ingesta_y_perfilado_v5.pptx). Versión del material docente; uso efectivo por confirmar.

Abrir [P01 paso a paso](../../kit/Notebooks/01_Perfil_PQRS.ipynb): rutas visibles, una lectura por CSV, inspección de columnas, faltantes, conversión y verificación antes de repetir por bloques. No importar scripts del curso para producir el perfil. La [solución P01](../../soluciones/P01_solucion.ipynb) mantiene los mismos pasos; las [plantillas pandas](../../ejercicios/README.md) dejan el desarrollo de cada actividad al estudiante.

Antes de leer las muestras, realizar [P01: descarga y verificación](../../talleres/P01.md) con `python 00_datos.py --descargar pqrs` y `python 00_datos.py --verificar pqrs`, desde `kit/`. Si las muestras ya existen y coinciden, se conservan.
