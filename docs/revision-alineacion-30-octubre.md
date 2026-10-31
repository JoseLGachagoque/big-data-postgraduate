# Revisión de alineación del repositorio

Fecha: 30 de octubre de 2026. Alcance: acuerdos de las clases 09 y 10 sobre pipelines, DataOps, esquemas industriales y E12/E13. Se revisó el árbol de trabajo local; no se realizó commit ni push.

## Resultado

La documentación revisada queda alineada con la progresión problema y propósito, conceptos, ejemplo desarrollado y ejercicios. La alineación documental original no acreditaba una ejecución; posteriormente se añadió y ejecutó la solución integrada de E12.

| Acuerdo | Material alineado | Estado |
|---|---|---|
| Explicar el porqué antes del cómo | Programa, metodología, clase 09 y guía conceptual | Documentado |
| Tareas, dependencias, DAG y orquestación | Guía conceptual y temario del viernes | Documentado con esquema |
| DataOps: ciclo, responsables, versiones, pruebas y fallos | Guía, E12, E13, proyecto y clase 10 | Integrado en evidencias existentes |
| ETL, ELT, Medallion y CDC | Guía conceptual, clase 09 y temario | Comparación conceptual, sin nuevas instalaciones |
| Ejemplo PQRS y tres ejercicios guiados | Guía conceptual y E12 | Disponible en el repositorio |
| Cuatro criterios mínimos | E12, E13 y proyecto | Conservados |
| Predicción EVA opcional | Índice, kit, mapa, fuente integrada y registro histórico | Diferenciada del E12 vigente |
| Notebook de referencia E12 | [Solución integrada](../soluciones/E12_solucion.ipynb), índice y enunciado | Completado y ejecutado con las tres muestras PQRS |
| Iceberg docente | Temario y guía conceptual | Requiere entorno y demostración comprobados |
| Presentaciones PPTX | Distribución docente externa al árbol Git | No acompañan al clon; la guía conserva el contenido conceptual |

## Inconsistencias corregidas

- Las clases 09 y 10 y el programa omitían el desarrollo explícito de DataOps y de esquemas industriales.
- El archivo estructurado `curso_integrado.json` conservaba el E12 predictivo y bloques antiguos del calendario, metodología y proyecto. Se sincronizaron con sus documentos vigentes y se incorporaron la guía conceptual y el temario.
- El calendario estructurado del viernes mantenía la distribución anterior de bloques. Se ajustó al temario conceptual sin cambiar horarios, duración o descanso.
- El registro histórico presentaba métricas predictivas bajo el nombre E12 sin distinguir que pertenecían al ejercicio anterior.
- Los enlaces a PPTX salían del árbol del repositorio. Se identificó su distribución externa y se proporcionó una guía interna utilizable desde el clon.

## Verificación y límites

Se comprobaron 164 enlaces locales en los Markdown modificados y las nuevas guías, sin destinos ausentes. Se analizaron los JSON modificados y se verificaron doce sesiones y 3.840 minutos efectivos; el viernes 30 conserva 180 minutos efectivos. `git diff --check` no encontró errores de espacios.

No se ejecutaron notebooks, descargas, Spark ni Iceberg en esta revisión documental. Los cambios previos del notebook de streaming se conservaron y no se modificaron como parte de esta revisión.

## Cierre del pendiente práctico

La [solución integrada E12](../soluciones/E12_solucion.ipynb) sigue la ruta prevista: propósito y entradas, reglas con caso pequeño, lectura y validación, detalle y agregado candidatos, relectura y conciliación, decisión de publicación, segunda ejecución y comparación del contenido. Se ejecutó con tres muestras identificadas y conserva ambos registros, la publicación válida y la ficha de auditoría. Los notebooks 02 y 03 permanecen como antecedentes parciales.

Referencias: [guía conceptual](pipelines-dataops.md), [temario](temario-30-31-octubre.md), [E12](../talleres/E12.md), [índice de notebooks](../kit/Notebooks/README.md).
