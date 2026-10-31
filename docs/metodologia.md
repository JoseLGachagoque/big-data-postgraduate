# Modo de presentar y conducir el curso

Viernes: explicación y demostraciones guiadas por el profesor, sin entregas ni calificación. El profesor ejecuta, explica y comparte sus archivos de referencia; los estudiantes observan, preguntan y pueden seguir voluntariamente. Sábado: ejecución por los estudiantes, revisión y entrega durante la clase. La evidencia evaluable debe corresponder a su propia ejecución. No se exige una entrega ni trabajo autónomo obligatorio entre ambos encuentros.

E = ejercicio general del curso (E01–E13). P = práctica con datos PQRS (P01–P04); PQRS significa peticiones, quejas, reclamos y sugerencias. El número identifica la actividad, no la sesión. T01 = taller teórico de capacidad; I01 = introducción a eventos NASA.

La presentación institucional introduce la pregunta y el concepto. La guía contiene pasos, datos y criterios. El notebook permite observar y modificar el procedimiento. El cierre exige evidencia propia y una explicación del resultado. Cada recurso tiene una función y los mismos IDs de actividad.

## Ritmo de cada bloque online

- Abrir con una pregunta verificable y declarar el dato o supuesto que se usará.
- Exponer un concepto durante 10–20 min y demostrar una operación breve con el archivo real.
- Los sábados, trabajar en salas de dos o tres estudiantes con una consigna y producto concreto. Alternar quién ejecuta, quién revisa y quién documenta.
- Compartir una tabla o control agregado y discutir unidades, denominador y límite de interpretación.
- Los sábados, registrar en entregas/ el resultado y la decisión. El docente consulta los controles del corte y evita evaluar solo la cantidad de herramientas utilizadas.

## Presentaciones centrales y material de ampliación

Sesión 1: cinco V, restricciones y ficha de problema. Sesión 2: ingesta, perfil y códigos. Sesión 3: formatos, contrato y reejecución. Sesión 4: calidad, consulta e integración. La introducción a eventos se ubica en la sesión 8. Las sesiones 5, 7 y 8 trabajan Spark, rendimiento y eventos. Las sesiones 9 y 10 explican primero el problema y propósito, después conceptos de pipelines y DataOps, esquemas industriales, ejemplo y ejercicios guiados. La [guía conceptual](pipelines-dataops.md) conecta esa progresión con integración, publicación y reejecución según el [temario vigente](temario-30-31-octubre.md); las presentaciones anteriores de analítica quedan como referencia opcional. No requieren ejecutar Spark ni instalar Dask, GPU o plataformas gestionadas en el primer fin de semana.

## Datos observados y supuestos de capacidad

Los tamaños descargados y conteos del kit se identifican como observados. T01 trabaja escenarios de capacidad, no descargas de esos tamaños. Fórmulas: RAM estimada = factor de materialización × bytes; tiempo aislado = bytes/tasa efectiva; cola acumulada = (entrada − servicio) × tiempo mientras la entrada supera al servicio. Los factores son hipótesis que deben medirse para un equipo y carga de trabajo concretos.

| Tamaño hipotético | RAM si factor = 3 | Descarga a 12,5 MB/s |
|---|---|---|
| 2 GB | 6 GB | 2 min 40 s |
| 20 GB | 60 GB | 26 min 40 s |
| 2 TB | 6 TB | 44 h 26 min 40 s |

Unidades decimales. Los tiempos son estimaciones de operaciones aisladas, sin sumarlos como un pipeline universal. Streaming, filtros, caché, compresión y concurrencia pueden cambiar las medidas. T01: 25 min para calcular la tabla, comparar un portátil con 10 GB de RAM utilizable y justificar el procesamiento por bloques o remoto. Entrega: estrategia por tamaño, restricciones y dos supuestos.

## Profundidad de posgrado

Cada taller pide hipótesis, criterio de aceptación, evidencia y una crítica. Una operación correcta se acompaña de cardinalidad, procedencia, unidades y condiciones en las que el resultado deja de ser válido. La ampliación puede investigar un método o motor diferente, pero no añade otra entrega obligatoria fuera de las 64 horas.

## Matriz de coherencia

| Sesiones | Evidencia central | Recursos |
|---|---|---|
| 1–2 | Ficha, manifiestos y perfil | E01–E03, P01, T01 |
| 3–4 | Parquet, contratos y controles | E04–E06, P02–P03 |
| 5–6 | Equivalencia, consultas y mapas | E07–E09 |
| 7–8 | Rendimiento y traza de eventos | E10–E11, P04, I01 |
| 9–10 | Pipeline, publicación, conciliación y reejecución | E12–E13 |
| 11–12 | Correcciones y defensa final | E13 |
