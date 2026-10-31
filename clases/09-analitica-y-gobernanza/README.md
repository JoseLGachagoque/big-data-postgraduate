# Clase 9: Integración del pipeline y publicación de datos

Preparado por el PhD Esteban Hernández, CyberColombia.

Viernes 30 de octubre de 2026. Tres horas efectivas de explicación y demostración docente. Participación guiada, sin entrega ni calificación el viernes.

## Propósito

Comprender por qué necesitamos un pipeline repetible y cómo DataOps organiza sus cambios y operación. Después, aplicar los conceptos a un caso conocido que publique detalle y agregado Parquet consultables mediante SQL.

## Temario

1. Problema: reportes diferentes, decisiones implícitas y dificultad para explicar cambios.
2. Pipeline: entradas, tareas, dependencias, productos y controles. Flujo de datos, DAG y orquestación.
3. DataOps: propósito, ciclo de trabajo, responsables, versiones, pruebas, monitoreo y tratamiento de fallos.
4. Esquemas industriales: ETL, ELT, capas Medallion y captura de cambios (CDC). Criterios de uso y combinaciones.
5. Ejemplo PQRS: originales, reglas, rechazados, detalle, agregado y conciliación por grupo y total.
6. Publicación candidata, registro y reejecución estable. Diferenciar reintento y corrección de la fuente.
7. Formatos de tabla: snapshots Iceberg y comparación conceptual con Hudi.
8. Tres ejercicios guiados: diseñar el flujo, atender incidentes y definir pruebas. Conexión con E12.

La [guía de pipelines y DataOps](../../docs/pipelines-dataops.md) conserva en el repositorio los conceptos, esquemas y ejercicios. La secuencia es problema y propósito, explicación conceptual, ejemplo desarrollado y ejercicio. Cada paso del ejemplo debe explicar su razón, operación y comprobación. Airflow y Great Expectations son referencias conceptuales, sin instalación obligatoria.

El [temario desarrollado](../../docs/temario-30-31-octubre.md) contiene preguntas, explicación, demostraciones y comprobaciones. Se utiliza una entrada manejable y validada. La instalación estudiantil de Iceberg no forma parte de la sesión.

## Descanso

20:00–20:15.

## Continuidad

El sábado se ejecuta [E12: integración y verificación del pipeline](../../talleres/E12.md), que aporta evidencia al [proyecto E13](../../talleres/E13.md). Se retira la evaluación predictiva EVA como requisito de estas sesiones. Las prácticas anteriores permanecen como referencia.
