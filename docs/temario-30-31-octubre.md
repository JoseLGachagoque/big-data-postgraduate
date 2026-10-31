# Temario del 30 y 31 de octubre de 2026

Preparado por el PhD Esteban Hernández, CyberColombia.

## Propósito y alcance

Integrar los procedimientos estudiados en un pipeline local que reciba datos, los valide, produzca tablas Parquet y publique un agregado consultable mediante SQL. El estudiante debe ejecutar el proceso completo, explicar sus controles y comprobar que una segunda ejecución con las mismas entradas conserva los resultados esperados.

El viernes dispone de 180 minutos efectivos de explicación y demostración docente; el sábado, de 450 minutos de ejecución estudiantil, revisión y entrega de un candidato formativo. No hay entrega el viernes ni trabajo autónomo obligatorio entre encuentros.

Cada equipo trabaja una sola ruta: PQRS o agroambiental. Se reutilizan datos y transformaciones anteriores. La referencia docente utiliza una selección manejable de PQRS ya disponible; el volumen completo no es requisito. El alcance de la selección debe declararse.

El entorno base utiliza Python, Parquet y DuckDB. Spark puede mantenerse si el equipo ya tiene una ejecución comprobada. No se repite la comparación entre motores como obligación. Las prácticas previas de streaming se conservan como evidencia independiente.

## Preparación docente

Antes de clase, comprobar la ejecución completa de la referencia, entradas, dependencias y rutas. Disponer de una copia validada de los archivos. La demostración Iceberg requiere una sesión de Spark y un conector preparados y probados; no se incluye instalación estudiantil.

Este documento desarrolla el temario y las consignas de [E12](../talleres/E12.md) y [E13](../talleres/E13.md). La [guía de pipelines y DataOps](pipelines-dataops.md) conserva conceptos, esquemas y ejercicios dentro del repositorio. Los PPTX se distribuyen por separado: `09_Data_pipelines_y_DataOps_pedagogica_v10.pptx` y `10_Ejecucion_y_auditoria_pipeline_v6.pptx`. Están fuera del árbol Git y no se incluyen al clonar. La [solución integrada E12](../soluciones/E12_solucion.ipynb) contiene la referencia ejecutada; las diapositivas por sí solas no acreditan la ejecución del pipeline.

## Viernes 30: integración del pipeline y publicación de datos

### 1. Conceptos de data pipelines · 35 minutos

**Pregunta:** ¿qué debe existir para que otra persona obtenga el mismo resultado?

Comenzar con dos personas que preparan el mismo reporte y aplican criterios distintos. Explicar por qué se necesitan reglas explícitas, originales conservados y controles antes de presentar la definición del pipeline. Mantener la secuencia problema, consecuencia, concepto y procedimiento.

Definir pipeline, tarea, dependencia, producto y control. Distinguir flujo de datos y flujo de control, diseño y ejecución. Leer un DAG sencillo, explicar sus ramas y diferenciar el período del dato de la fecha de ejecución. Explicar orquestación como coordinación del orden, las condiciones, los estados y la respuesta al fallo. Relacionar lotes y eventos con las prácticas anteriores.

Usar una pregunta concreta: ¿cuántos reportes contiene el corte por período y territorio? Precisar fuente, corte, unidad de observación y cobertura de los archivos seleccionados.

**Apoyo visual:** ilustración completa del pipeline, esquema de datos y control, y DAG editable. Explicar cada flecha antes de presentar herramientas.

**Comprobación oral:** explicar qué etapa no puede continuar si falta una entrada y qué debe registrar el error.

### 2. Conceptos y esquemas de DataOps · 35 minutos

**Pregunta:** ¿cómo organiza un equipo los cambios y la operación del pipeline?

Definir DataOps mediante colaboración, reproducibilidad, pruebas y retroalimentación. Recorrer el ciclo acordar, preparar, probar, publicar, observar y corregir. Distinguir este ciclo de mejora del DAG de una ejecución. Identificar responsables, versiones de datos, código, reglas y configuración. Relacionar monitoreo con diagnóstico y distinguir reintento de corrección. Explicar idempotencia con un ejemplo de anexado duplicado.

Explicar primero las razones: un programa puede terminar con datos incompletos, una fuente corregida puede cambiar legítimamente una cifra y el consumidor necesita un responsable que atienda incidentes. Cada práctica debe responder a uno de esos problemas.

Situar la solución con una diapositiva de esquemas industriales documentados actualmente: ETL, ELT, capas Medallion y captura de cambios (CDC). Mostrar sus recorridos y criterios de uso. Aclarar que corresponden a decisiones distintas y pueden combinarse. Los ejemplos de herramientas y las fuentes primarias quedan en las notas docentes. Esta comparación se integra en el bloque conceptual, sin ampliar la duración ni exigir nuevas instalaciones.

**Comprobación oral:** señalar qué evidencia permite distinguir una entrada corregida de una reejecución defectuosa. Airflow y Great Expectations se nombran como ejemplos de responsabilidades; no se instalan ni se exigen.

### 3. Ejemplo desarrollado PQRS · 45 minutos

**Pregunta:** ¿qué condiciones debe cumplir una entrada antes de incorporarla?

Explicar esquema, tipos y reglas de aceptación. Diferenciar un valor faltante de uno inválido. Identificar archivos ya recibidos y conservar los originales. Examinar posibles duplicados sin asumir que dos filas iguales representan necesariamente el mismo reporte.

**Demostración:** leer una entrada, aplicar pocas reglas visibles y separar aceptados y rechazados con sus motivos. Conciliar `filas leídas = aceptadas + rechazadas`. Contar cada fila rechazada una sola vez, aunque tenga varios motivos.

Las reglas por fila se documentan antes de ejecutar; el número de rechazos queda visible. Un fallo de esquema detiene la publicación.

**Comprobación oral:** distinguir un lote procesable con rechazos documentados de otro que debe detenerse.

**Pregunta complementaria:** ¿qué representa una fila publicada y qué consulta debe responder?

Explicar granularidad. Una fila del detalle conserva la unidad de observación; una fila agregada corresponde a una combinación de dimensiones. En PQRS, utilizar período y territorio y una medida de conteo de reportes. El período proviene de un campo documentado o del corte identificado; no se inventan fechas mensuales.

Si se incorpora DIVIPOLA, revisar claves y cardinalidad. Conservar e identificar territorios sin correspondencia y comprobar que la unión no multiplique observaciones. Agrupar categorías no informadas explícitamente para que no desaparezcan de la conciliación.

**Demostración:** reutilizar una transformación conocida, escribir detalle Parquet, producir el agregado y contrastarlo mediante SQL en DuckDB. Comparar cada grupo, además del total.

En la ruta agrícola, usar combinaciones compatibles de período, territorio, cultivo y estado físico. Si se calcula rendimiento, utilizar producción y área cosechada válidas sobre el mismo conjunto de observaciones y conservar unidades. No sumar rendimientos ni promediar cocientes sin justificación.

**Comprobación oral:** explicar qué información pierde el agregado y qué preguntas requieren el detalle.

### 4. Seguimiento operativo del ejemplo · 25 minutos

**Pregunta:** ¿cómo evitamos presentar una salida incompleta como resultado válido?

Separar salida candidata y publicación validada. Guardar candidatos en una carpeta de ejecución, verificarlos e identificar en el registro la publicación válida. Si la ejecución falla, conservar la publicación válida anterior. Este procedimiento local no demuestra transacciones distribuidas ni publicación atómica de varias tablas.

Registrar identificador, entradas y huellas, versión de reglas y configuración, etapas, conteos, controles, estado final y errores. Relacionar esas evidencias con las responsabilidades DataOps. Distinguir datos publicados de metadatos operativos: tiempos e identificadores pueden cambiar aunque el contenido de las tablas deba permanecer estable. Contrastar una reejecución con una corrección de la fuente: esta última puede cambiar legítimamente la distribución por grupo.

**Demostración:** ejecutar el recorrido completo y repetirlo con las mismas entradas. Comparar contenido, claves y medidas; la identidad binaria de los archivos Parquet no es el criterio obligatorio. Mostrar el registro producido ante una entrada inválida controlada, conservando intacto el original.

**Comprobación oral:** identificar la evidencia necesaria para afirmar que el proceso terminó correctamente.

### 5. Formatos de tabla: Iceberg y Hudi · 10 minutos

**Pregunta:** ¿qué dificultades aparecen cuando una tabla recibe correcciones y varios procesos necesitan consultarla?

Distinguir formato físico, formato de tabla, catálogo y motor. Relacionar snapshots y correcciones con los límites del ejercicio con archivos. Nombrar Hudi como alternativa relacionada con actualizaciones e ingesta incremental. El formato de tabla no sustituye la orquestación ni las pruebas del significado de los datos.

**Demostración docente preparada con Spark SQL:** consultar una tabla Iceberg pequeña, observar su snapshot, aplicar un cambio identificado como didáctico y consultar el estado anterior. La configuración y creación inicial de la tabla deben estar resueltas antes de clase.

**Comprobación oral:** justificar cuándo bastan Parquet y los controles del ejercicio y qué requisitos justificarían un formato de tabla. Iceberg no garantiza por sí solo una consulta más rápida.

### 6. Ejercicios guiados y conexión con E12 · 30 minutos

Después del ejemplo, resolver tres actividades: dibujar el pipeline y sus dependencias; decidir acciones ante incidentes; definir pruebas con las seis filas hipotéticas. Cada actividad tiene un producto explícito y respuestas orientadoras en las notas docentes. Identificar después los pasos de E12 y sus cuatro criterios mínimos. Las prácticas DataOps se evidencian en el manifiesto, las reglas, los registros y la revisión entre equipos; no añaden nuevas ponderaciones. Participación guiada, sin entrega evaluable el viernes.

**Descanso:** 20:00–20:15. Los seis bloques suman 180 minutos efectivos. El descanso interrumpe el bloque 4, después de sus primeros 5 minutos. La explicación conceptual y el ejemplo preceden a los ejercicios.

## Sábado 31: ejecución y verificación del pipeline

### 1. Preparación y alcance · 45 minutos

Comprobar kernel, bibliotecas, rutas y datos. Elegir ruta, pregunta y granularidad. Registrar corte y unidad de observación e identificar las transformaciones previas que se reutilizan.

**Producto:** ficha breve de entradas, etapas y salidas. Si una descarga falla, utilizar la copia docente validada y registrar su procedencia. No dedicar el bloque a descargar todos los cortes completos.

### 2. Recepción y validación · 90 minutos

Ejecutar lectura, tipado y reglas acordadas. Separar aceptados, rechazados y motivos. Revisar claves y cobertura territorial cuando corresponda. Explicar faltantes y conciliar conteos.

**Producto:** controles de validación revisados por el profesor antes de publicar.

### 3. Transformación y publicación candidata · 90 minutos

Integrar operaciones conocidas en un notebook con secciones consecutivas. Escribir detalle y agregado Parquet en una carpeta candidata. Releerlos y contrastar medidas por grupo y total mediante SQL, incluyendo categorías no informadas.

**Producto:** primera ejecución completa y consulta conciliada. Identificar las tablas como publicación válida cuando pasen los controles.

### 4. Reejecución y registro operativo · 75 minutos

Repetir las mismas entradas. Comparar contenido y comprobar que no aparecen filas adicionales por acumulación accidental. Conservar ambos registros. Documentar rutas, dependencias y orden para otro equipo.

**Producto:** comparación entre ejecuciones y registro final. Los equipos que aún no tengan una primera ejecución válida utilizan el bloque para completarla y registran lo pendiente.

### 5. Ejercicio de auditoría entre equipos · 90 minutos

Otro equipo utiliza las instrucciones para ejecutar o reproducir una consulta del candidato. Comprueba conciliación y registros y documenta un hallazgo verificable. El equipo autor corrige y vuelve a ejecutar el control afectado. Si no se encuentra un defecto, registrar el control satisfactorio; no inventar fallos.

**Consigna:** demostrar las cuatro comprobaciones mínimas de E12 y explicar un resultado que no puede inferirse de las entradas. Si una falla, registrar evidencia, causa investigada y corrección pendiente.

**Producto:** ficha con hallazgo o control satisfactorio, evidencia, acción y resultado posterior.

### 6. Revisión del candidato · 60 minutos

Revisar los cuatro criterios y consolidar una entrega por equipo. Identificar bloqueos para la clínica del 6 de noviembre. El candidato del 31 es formativo; la versión final y la sustentación permanecen el 7 de noviembre.

**Producto:** notebook ordenado, instrucciones, entradas identificadas, consultas, registros, ficha de auditoría y tablas o instrucciones comprobadas para regenerarlas. Las salidas voluminosas se entregan por el medio del curso y se excluyen de Git.

**Descansos:** 09:30–09:45 y 15:00–15:15; almuerzo 12:00–13:00. Los bloques suman 450 minutos efectivos y pueden interrumpirse en esos puntos sin alterar el orden.

## Criterios mínimos y ampliaciones

| Criterio obligatorio | Evidencia |
|---|---|
| Ejecución completa con instrucciones disponibles | Entradas identificadas, etapas ejecutadas y registro final |
| Conteos y reglas explicables | Leídos, aceptados y rechazados conciliados; claves y faltantes documentados |
| Agregado conciliado con el detalle | Comparación SQL por grupo y total |
| Reejecución estable | Comparación del contenido de dos ejecuciones |

Después de cumplir los cuatro criterios, un equipo puede reconstruir un período afectado y comprobar que los demás permanecen iguales. Puede completarse durante la clínica; no condiciona la aceptación mínima. Iceberg estudiantil y un tablero visual son ampliaciones posteriores al pipeline básico.

La actualización por registro, recuperación automática, operación concurrente y despliegue distribuido necesitarían diseño y pruebas adicionales. Este ejercicio no acredita esas capacidades.

## Correcciones del temario anterior

E12 sustituye la predicción temporal EVA, MAE y líneas base por integración, publicación y reejecución. La gobernanza se concreta en procedencia, reglas, responsables, versiones de entradas y estado de publicación. E13 incorpora esa evidencia y las prácticas anteriores pertinentes, sin exigir streaming ni mapas integrados en todos los productos.

Se mantienen las 64 horas totales, descansos, candidato formativo y ponderaciones vigentes. Las presentaciones anteriores de analítica y los ejercicios de modelo conservados quedan como referencia histórica u opcional y no definen la entrega de estas sesiones.
