# Clase 10: Ejecución y auditoría del pipeline

Preparado por el PhD Esteban Hernández, CyberColombia.

Sábado 31 de octubre de 2026. Siete horas y treinta minutos efectivos de trabajo estudiantil, revisión y entrega en clase.

## Propósito

Completar y verificar un pipeline local con componentes ya estudiados. Cada equipo trabaja una ruta y produce detalle y agregado Parquet, consultas SQL y registros de control.

Aplicar las prácticas DataOps explicadas el viernes: entradas y reglas identificadas, responsabilidades acordadas, pruebas antes de publicar y revisión de incidentes. Consultar la [guía conceptual y los ejercicios guiados](../../docs/pipelines-dataops.md). Estas prácticas se evidencian en los productos existentes de E12, sin otra ponderación ni plataformas nuevas.

## Temario y práctica

1. Comprobar entorno, entradas, alcance y granularidad.
2. Integrar recepción, validación y separación de rechazados con motivos.
3. Aplicar transformaciones conocidas y verificar claves y cardinalidad.
4. Generar detalle y agregado en una publicación candidata.
5. Releer y conciliar resultados mediante SQL por grupo y total.
6. Reejecutar con las mismas entradas y comparar el contenido publicado.
7. Auditar entre equipos, registrar evidencia y corregir hallazgos.
8. Consolidar el candidato y los pendientes para la clínica del 6 de noviembre.

El [temario desarrollado](../../docs/temario-30-31-octubre.md) establece bloques, productos y puntos de revisión. [E12](../../talleres/E12.md) define el ejercicio y sus cuatro criterios mínimos. La reconstrucción de un período es una ampliación cuando el pipeline básico funciona.

## Ejercicio de clase

Otro equipo reproduce una consulta y comprueba ejecución completa, conteos explicables, conciliación del agregado y reejecución estable. Registra un hallazgo real o un control satisfactorio y la comprobación posterior.

## Descansos

Recesos 09:30–09:45 y 15:00–15:15; almuerzo 12:00–13:00.

## Entrega

Un candidato formativo por equipo: notebook ordenado, instrucciones, entradas identificadas, tablas regenerables, consultas, registros y ficha de auditoría. Se integra a [E13](../../talleres/E13.md), sin ponderación adicional. La versión final permanece el 7 de noviembre.
