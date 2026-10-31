# Programa académico de 64 horas

Curso de Postgrado: BigData, Especialización en Bases de datos. Preparado por el PhD Esteban Hernández, CyberColombia. El programa desarrolla competencias de ingeniería de datos sobre dos dominios abiertos: reportes administrativos de salud (PQRS/PQRD de Supersalud) y datos agroambientales de suelo, territorio, producción agrícola y clima. Cada dominio conserva su unidad y significado. El vínculo común es el diseño de ingesta, contratos, calidad, formatos, ejecución y evidencia reproducible.

La organización vigente integra los datasets descargados, las presentaciones institucionales y los ejercicios reproducibles. Las prácticas se ejecutan en un portátil, comienzan con cortes manejables y avanzan a 2.444.766 reportes PQRS, sin fabricar filas para simular volumen. Los escenarios de 2 GB, 20 GB y 2 TB son cálculos de capacidad, claramente separados de los archivos observados.

## Propósito y resultados de aprendizaje

Diseñar, ejecutar y evaluar un sistema local de ingesta, calidad, integración y análisis que conserve la procedencia y el significado de los datos. El estudiante debe justificar cuándo un portátil es suficiente y qué cambiaría al crecer el volumen, la concurrencia o las exigencias de actualización.

- RA1. Formular una pregunta verificable, identificar la unidad de análisis y evaluar cobertura, licencias y límites de las fuentes.
- RA2. Descargar y verificar archivos, conservar el corte original, tipar variables y reportar datos aptos y pendientes de revisión.
- RA3. Integrar códigos territoriales, tablas y geometrías sin multiplicar observaciones ni confundir escalas espaciales.
- RA4. Comparar DuckDB y Spark local, medir formatos y explicar particiones, joins, ventanas y eventos tardíos.
- RA5. Integrar y verificar un pipeline local con controles, publicación de detalle y agregado, consultas SQL y reejecución estable; defender sus decisiones y límites.

## Horario y carga académica

| Componente | Tiempo efectivo |
|---|---|
| Viernes 2 y 9 de octubre, 18:00–22:00 | 3 h 45 min cada uno |
| Viernes 16, 23 y 30 de octubre y 6 de noviembre, 18:00–21:15 | 3 h cada uno |
| Sábados 3, 10, 17, 24 y 31 de octubre, 08:00–17:00 | 7 h 30 min cada uno |
| Sábado 7 de noviembre, 08:00–16:30 | 7 h |
| Total de clase en línea, excluidas pausas | 64 h |

Doce sesiones online en seis fines de semana, del 2 de octubre al 7 de noviembre de 2026. Las 64 horas corresponden íntegramente a docencia en línea. El trabajo autónomo opcional no se descuenta de esta obligación. La instalación y la comprobación inicial disponen de un bloque durante la sesión 2.

Viernes: explicación y demostraciones guiadas por el profesor, sin entregas ni calificación. El profesor ejecuta, explica y comparte sus archivos de referencia; los estudiantes observan, preguntan y pueden seguir voluntariamente. Sábado: ejecución por los estudiantes, revisión y entrega durante la clase. La evidencia evaluable debe corresponder a su propia ejecución. No se exige una entrega ni trabajo autónomo obligatorio entre ambos encuentros.

E = ejercicio general del curso (E01–E13). P = práctica con datos PQRS (P01–P04); PQRS significa peticiones, quejas, reclamos y sugerencias. El número identifica la actividad, no la sesión. T01 = taller teórico de capacidad; I01 = introducción a eventos NASA.

## Estructura curricular

| Fechas | Núcleo y ejercicios | Clase efectiva |
|---|---|---|
| 02/10 y 03/10 | Fundamentos y escala / Ingesta y perfilado | 11 h 15 min |
| 09/10 y 10/10 | Arquitecturas, formatos y pipelines / Calidad e integración | 11 h 15 min |
| 16/10 y 17/10 | Procesamiento con Spark / Consultas e integración distribuida | 10 h 30 min |
| 23/10 y 24/10 | Rendimiento y escalabilidad / Streaming de eventos | 10 h 30 min |
| 30/10 y 31/10 | Integración del pipeline y publicación de datos / Ejecución y auditoría del pipeline | 10 h 30 min |
| 06/11 y 07/11 | Clínica de proyectos y ensayo de defensa / Sustentación y cierre contractual | 10 h |

## Fundamentos que se conservan

Volumen, velocidad, variedad y veracidad; escalamiento vertical y horizontal; ley de Amdahl; latencia y throughput; ciclo de vida del dato; sistemas distribuidos y tolerancia a fallos. Warehouse, lake y lakehouse, papel de Hadoop/HDFS y modelos NoSQL se estudian mediante decisiones de arquitectura. La implementación se concentra en Python, DuckDB, Parquet, Spark local y herramientas geográficas de escritorio.

Las sesiones 9 y 10 explican primero el propósito de los pipelines y las prácticas DataOps: dependencias, orquestación, responsables, versiones, pruebas, monitoreo y tratamiento de fallos. Comparan ETL, ELT, capas Medallion y captura de cambios como esquemas que pueden combinarse. Después desarrollan un ejemplo y ejercicios guiados antes de integrar E12. La [guía de pipelines y DataOps](pipelines-dataops.md) contiene ese desarrollo, sin exigir plataformas adicionales.

Los archivos tabulares de esta cohorte caben en un portátil. Su tamaño no demuestra una necesidad de cómputo distribuido. La complejidad surge también de esquemas heterogéneos, profundidades, fechas, escalas, geometrías y versiones territoriales. Spark local permite estudiar ejecución y planes; sus tiempos no predicen el rendimiento de un clúster.

## Evaluación

| Evidencia | Peso |
|---|---|
| E01–E03: procedencia, descarga y perfilado | 10 % |
| E04–E06: calidad, formatos y SQL | 10 % |
| E07–E09: Spark e integración geográfica | 10 % |
| E10–E11: experimento y eventos | 20 % |
| E12–E13: proyecto e informe técnico | 35 % |
| Sustentación individual | 15 % |

La rúbrica valora corrección y conservación de unidades (30 %), reproducibilidad y trazabilidad (25 %), justificación técnica (25 %) y comunicación de limitaciones (20 %), aplicada dentro de cada entrega. Se penaliza afirmar cobertura nacional a partir de muestras, sumar rendimientos, convertir ausencias a cero, introducir fuga temporal o presentar asociaciones como causalidad. La nota mínima y las reglas de asistencia corresponden al programa institucional.

## Producto integrador

Cada equipo elige dominio agroambiental o PQRS y presenta un pipeline local ejecutable con entradas identificadas, validación, detalle y agregado Parquet, consultas SQL conciliadas y registros de dos ejecuciones. Las prácticas previas de motores, rendimiento, mapas y eventos se adjuntan como evidencias pertinentes, sin exigir integrarlas todas en el pipeline. La actualización de un período es una ampliación posterior a los cuatro criterios mínimos de E12. La evaluación predictiva EVA queda como referencia opcional. El informe de 8 a 12 páginas debe separar resultados observados, estimaciones, limitaciones y propuesta de escalamiento. La sustentación final se realiza el 7 de noviembre. La sesión del 6 permite ensayar, corregir y validar el producto dentro de las horas contratadas. Planificar 15 minutos por equipo incluyendo preguntas y transición; ajustar el número de turnos al grupo real.

El [temario desarrollado del 30 y 31 de octubre](temario-30-31-octubre.md) establece la progresión y los criterios de E12. Iceberg se presenta en una demostración docente preparada; su instalación y uso estudiantil no son requisitos del proyecto.

## Dos dominios y una secuencia común

| Dominio | Uso central | Límites |
|---|---|---|
| PQRS de salud | Perfil, lectura por bloques, Parquet, contratos y comparación de motores | Reportes administrativos; no equivalen a personas únicas ni prevalencia. |
| Agroambiental | DIVIPOLA, shapes, propiedades del suelo, EVA, clima y análisis temporal | Escalas y unidades distintas; muestra municipal no representa automáticamente toda la superficie. |

La introducción usa las cinco V, costos de movimiento, escalamiento y Amdahl. Después se construye un producto: conservar originales, definir contrato, tipar, controlar calidad, publicar Parquet, consultar, medir y defender el resultado. Polars y DuckDB trabajan localmente; Spark permite estudiar planes y shuffle. Dask, Zarr, GPU y plataformas gestionadas se presentan como alternativas de arquitectura, sin añadir instalaciones obligatorias ni laboratorios extra.

## Prerrequisitos operativos y progresión

- Saber usar una terminal, tipos básicos de Python y SELECT/GROUP BY en SQL. El diagnóstico inicial orienta la ayuda docente.
- Iniciar con las tres muestras reales de 1.000 filas PQRS y los CSV agroambientales. Las muestras son las primeras filas y sirven para probar código; no tienen representatividad estadística.
- El profesor demuestra datos completos PQRS en la sesión 7 después de validar la consulta con muestras. Descargar un corte por vez o acceder a la copia docente.
- E01–E13 y P01–P04 comparten los bloques del programa. P01–P03 complementan los talleres de las sesiones 2–4; P04 se demuestra en la sesión 7 y se ejecuta y entrega en la sesión 8. No se añaden horas.

## Fechas de entrega y calificación

| Sábado / cierre | Evidencia | Peso |
|---|---|---|
| 10-03 · 16:45–17:00 | Ficha de problema, presupuesto de recursos, manifiesto, perfil y claves territoriales | 10 % |
| 10-10 · 16:30–16:45 | Contrato propio, Parquet, prueba de reejecución, controles de calidad, consultas equivalentes y cobertura | 10 % |
| 10-17 · 16:30–17:00 | Plan y equivalencia Spark/DuckDB, consulta de ventanas, mapa y alcance espacial | 10 % |
| 10-24 · 16:30–17:00 | Informe de benchmark propio, traza de eventos y análisis de recuperación | 20 % |
| 10-31 · 16:30–17:00 | Pipeline candidato, detalle y agregado Parquet, consultas conciliadas, registros de reejecución y ficha de auditoría | Hito formativo del bloque de proyecto (35 %) |
| 11-07 · 16:00–16:30 | Paquete final corregido, informe de 8–12 páginas y registro de defensa individual | 35 % proyecto + 15 % sustentación |

El candidato del 31 de octubre recibe retroalimentación y no añade otra ponderación. El bloque E12–E13 se califica con 35 % sobre la versión final del 7 de noviembre, que incorpora E12 y las correcciones. La sustentación individual vale 15 %. Total del curso: 100 %. Los archivos parciales del sábado forman una entrega única por fin de semana.
