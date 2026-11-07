# Proyecto final sobre los municipios de Boyacá

Análisis de población, producción agrícola, capacidad de uso de las tierras y desempeño municipal en Boyacá

Curso: ____________________________________    Grupo: ____________________

Docente: __________________________________    Fecha: ____________________

## Registro de integrantes

Registre el nombre completo y el código de cada integrante del grupo.

| N.º | Nombre completo | Código |
| --- | --- | --- |
| 1 |  |  |
| 2 |  |  |
| 3 |  |  |
| 4 |  |  |
| 5 |  |  |
| 6 |  |  |



## 1. Planteamiento del problema

Los municipios de Boyacá presentan diferencias en su estructura poblacional, producción agrícola, capacidad de uso de las tierras y desempeño municipal. Se propone integrar estas dimensiones para identificar patrones territoriales y estudiar si la proporción de población adulta joven se relaciona con los resultados de desempeño municipal.

Cada grupo deberá construir un proceso reproducible que abarque la ingesta, calidad, validación e integración de datos, el cálculo de indicadores, el análisis estadístico y espacial, y la generación de visualizaciones. El resultado debe permitir evaluar las hipótesis y comunicar sus hallazgos y limitaciones.

La idea de que las personas jóvenes tienen mayor disposición al cambio es una explicación posible, pero las fuentes propuestas no miden directamente esa disposición. Una asociación municipal no demuestra causalidad.

## 2. Objetivos

Objetivo general: diseñar e implementar un pipeline reproducible que integre y analice datos de los municipios de Boyacá para explorar la relación entre población, producción agrícola, capacidad de uso de las tierras y desempeño municipal.

- Identificar fuentes, variables, cobertura geográfica, vigencias y limitaciones.

- Validar la calidad de los datos y documentar su limpieza e integración.

- Construir indicadores demográficos, agrícolas y territoriales.

- Contrastar hipótesis, calcular asociaciones e interpretar sus límites.

- Generar mapas y gráficos municipales mediante un proceso reproducible.

## 3. Preguntas de investigación

- ¿Cómo se distribuyen la población y los grupos de edad entre los municipios?

- ¿Cuáles municipios presentan mayor producción y cuáles mayor rendimiento por cultivo?

- ¿Cómo se distribuyen las clases de capacidad de uso de las tierras en cada municipio?

- ¿Existe una asociación entre la proporción de población de 18 a 44 años y el desempeño municipal?

- ¿Cómo se relacionan la producción agrícola y la población de 18 a 64 años?

- ¿Cómo cambian los resultados al considerar el tamaño poblacional y otras variables disponibles?

## 4. Fuentes y localización de datos

Cada grupo debe verificar las columnas, unidades, cobertura, periodo, condiciones de uso y fecha de descarga de cada fuente antes de integrarlas.

[Evaluaciones Agropecuarias Municipales de Boyacá](https://www.datos.gov.co/Agricultura-y-Desarrollo-Rural/EVALUACIONES-AGROPECUARIAS-MUNICIPALES-DEPARTAMENT/sn28-aa8q/about_data)

Producción, cultivos y áreas, según disponibilidad. Verificar unidades, años y periodicidad.

[Población de centros poblados de Boyacá](https://www.datos.gov.co/Vivienda-Ciudad-y-Territorio/POBLACI-N-DE-LOS-DIFERENTES-CENTROS-POBLADOS-EN-LO/seua-4ze8/about_data)

Caracterización de centros poblados. Verificar si contiene edad y sexo y si cubre la totalidad municipal.

[Medición del desempeño municipal](https://www.datos.gov.co/Funci-n-p-blica/Medici-n-del-Desempe-o-Municipal-por-Municipio-DEP/665j-iwk5/about_data)

Puntajes y componentes. Verificar vigencias, metodología y comparabilidad entre años.

[Proyecciones de población del DANE](https://www.dane.gov.co/index.php/estadisticas-por-tema/demografia-y-poblacion/proyecciones-de-poblacion)

Fuente complementaria de población municipal por edad, sexo y área. Registrar la versión de la proyección.

[Capacidad de uso de las tierras de Boyacá IGAC](https://mapas.igac.gov.co/server/rest/services/agrologia/mapageneraldecapacidaddeusodelastierrasdepartamentodeboyaca/MapServer)

Servicio geográfico con clases de capacidad de uso. Verificar acceso a polígonos, atributos y cobertura.

[División político administrativa DANE](https://www.datos.gov.co/dataset/Divisi-n-Politico-Administrativa-de-Colombia-Compl/jzqe-3e54)

Límites y códigos municipales para la integración y los mapas; verificar la vigencia de la geometría.

La disponibilidad de las variables de edad y sexo en la fuente de centros poblados debe comprobarse. Si no permite estimar los grupos para todo el municipio, utilice las proyecciones del DANE para el análisis municipal y presente por separado la información de centros poblados.

El mapa del IGAC corresponde a capacidad de uso de las tierras a escala 1:100.000 y fue publicado en 2004. No equivale a una medición actual de fertilidad ni a una calificación única de la calidad del suelo; indique su escala y antigüedad.

### Descarga de datos en formato CSV para la capa Raw

La capa `Raw` es la zona inicial de recepción del data lake y corresponde a la capa **`bronze`**. Para este proyecto, los archivos de entrada que se depositan en `bronze` deben estar en formato **CSV**, con un archivo por fuente o extracción y un manifiesto de procedencia. Los siguientes enlaces descargan la representación CSV de los conjuntos publicados en Datos Abiertos Colombia:

| Fuente | Descarga CSV |
| --- | --- |
| Evaluaciones agropecuarias de Boyacá | [Descargar CSV](https://www.datos.gov.co/api/views/sn28-aa8q/rows.csv?accessType=DOWNLOAD) |
| Población de centros poblados de Boyacá | [Descargar CSV](https://www.datos.gov.co/api/views/seua-4ze8/rows.csv?accessType=DOWNLOAD) |
| Desempeño municipal | [Descargar CSV](https://www.datos.gov.co/api/views/665j-iwk5/rows.csv?accessType=DOWNLOAD) |

Por ejemplo, desde una terminal, descargue el CSV sin modificar su contenido:

```bash
mkdir -p data_lake/bronze/evaluaciones_agropecuarias
curl -L --fail -o data_lake/bronze/evaluaciones_agropecuarias/evaluaciones.csv \
  'https://www.datos.gov.co/api/views/sn28-aa8q/rows.csv?accessType=DOWNLOAD'
```

Repita el procedimiento para las demás fuentes, con el enlace y directorio correspondientes. Verifique que el resultado sea un CSV válido y no una página de error; registre URL, fecha de descarga, nombre, tamaño, hash, codificación y vigencia. Si el portal cambia o restringe el enlace, use la opción **Exportar → CSV** del conjunto y documente la descarga.

**Fuentes sin descarga CSV directa.** Las proyecciones municipales del DANE se distribuyen en libros Excel y algunas capas espaciales se ofrecen como servicios geográficos. Cuando la fuente no proporcione directamente CSV, descargue el original en un área de preparación externa a `bronze` y expórtelo a CSV antes de la ingesta. Documente la URL, archivo y versión originales, hoja o capa seleccionada, pasos de conversión, codificación y hash tanto del original como del CSV; el CSV resultante es la copia de entrada a `bronze`, no el archivo original del proveedor. Para geometrías, exporte el identificador territorial y la geometría en WKT en una columna CSV y registre el sistema de referencia de coordenadas (CRS). Al crear `silver`, reconstruya y valide las geometrías y almacénelas en GeoParquet. Si una fuente no permite exportar geometría, registre la limitación y busque una alternativa documentada; un CSV solo de atributos no permite dibujar polígonos.

## 5. Hipótesis

Hipótesis principal: H0: no existe una asociación positiva entre la proporción de población de 18 a 44 años y el puntaje de desempeño municipal. H1: existe una asociación positiva entre ambas variables.

Para unificar los criterios, el rango principal incluye las edades de 18 a 44 años. Se analizará la proporción de población, en lugar de utilizar únicamente el número de personas jóvenes.

Hipótesis complementarias: cada grupo debe evaluar al menos dos de las siguientes:

- Existe una asociación entre producción agrícola total y población de 18 a 64 años.

- La producción agrícola por persona de 18 a 64 años presenta diferencias entre municipios.

- Existe una asociación entre la composición de clases de capacidad de uso y el rendimiento de un cultivo seleccionado.

- Las asociaciones entre las proporciones de mujeres y hombres de 18 a 44 años y el desempeño municipal presentan patrones diferentes.

## 6. Indicadores mínimos

- Proporción de población joven = población de 18 a 44 años / población total × 100.

- Proporción de población de 18 a 64 años = población de 18 a 64 años / población total × 100.

- Participación de mujeres y de hombres de 18 a 44 años = población del grupo / población total × 100.

- Producción por cada 1.000 habitantes de 18 a 64 años = producción agrícola / población de 18 a 64 años × 1.000.

- Rendimiento por cultivo = producción del cultivo / área cosechada del cultivo.

- Composición de capacidad de uso = área de cada clase en el municipio / área municipal cubierta por la fuente × 100.

Documente unidades y denominadores. No divida entre cero; registre los resultados no disponibles. Para agregar rendimientos comparables use la suma de producción dividida por la suma de área cosechada. Sume producción solo cuando sus unidades y definiciones sean compatibles; un total de toneladas mezcla cultivos y no representa valor económico.

La población de 18 a 64 años es una aproximación demográfica para el ejercicio y no equivale a población económicamente activa ni a trabajadores agrícolas. La producción por habitante de ese rango tampoco mide productividad laboral.

## 7. Fases de trabajo

### 7.1 Ingesta y exploración

Descargue los CSV de las fuentes y consérvelos sin modificar en `bronze`. Si una fuente se distribuye en otro formato, prepare su exportación CSV como se indica en la sección de descarga y documente el original. Registre entidad responsable, enlace, fecha, versión, cobertura y unidad de observación. Seleccione el año común más reciente con cobertura y comparabilidad suficientes. Si no existe, justifique las vigencias utilizadas y su efecto sobre los resultados.

### 7.2 Calidad y validación

Elabore un diagnóstico antes y después de la limpieza. Evalúe completitud, duplicados según la clave de cada fuente, tipos, unidades, rangos y consistencia de códigos y nombres. Revise poblaciones y áreas no negativas, porcentajes entre 0 y 100, puntajes según su escala documentada y rendimientos extremos. Compare subtotales demográficos con totales solo si las categorías son compatibles y exhaustivas. Reporte registros afectados, decisiones y exclusiones; no elimine valores atípicos automáticamente.

### 7.3 Integración de datos

La unidad principal será municipio y año. Estandarice DIVIPOLA municipal como texto de cinco dígitos y utilícelo como clave principal. Agregue cada fuente a su nivel apropiado antes de unirla. Construya una tabla maestra y una tabla municipio-año; reporte coincidencias, registros no vinculados, duplicados y vigencias. Verifique que los registros de centros poblados no incluyan subtotales superpuestos ni doble conteo.

### 7.4 Análisis espacial

Valide geometrías, utilice un sistema apropiado para calcular áreas e intersecte las capas municipales y agrológicas. Calcule el porcentaje de área cubierta por clase y el porcentaje sin clasificación. Puede identificar la clase predominante, sin asumir que todo el municipio tiene el mismo suelo. Si no se puede acceder o procesar la capa, documente los intentos, justifique una alternativa y señale los análisis pendientes.

### 7.5 Análisis estadístico

Describa la distribución y cobertura de las variables. Grafique población joven frente a desempeño; calcule correlación de Pearson y/o Spearman con justificación, número de municipios, intervalo de confianza, valor p y nivel de significancia definido previamente; se sugiere 0,05. Estime una regresión sencilla y, si la muestra lo permite, un modelo complementario con variables de control justificadas. Revise supuestos, observaciones influyentes y sensibilidad; compare municipios incluidos y excluidos por falta de datos.

Diferencie hipótesis principal y exploratorias y discuta comparaciones múltiples. Concluya si hay evidencia de asociación positiva, si no se rechaza la hipótesis nula o si los datos son insuficientes. Informe magnitud e incertidumbre. No atribuya causalidad ni disposición al cambio a partir de correlaciones municipales.

## 8. Visualizaciones requeridas

Como referencia, consulte la [guía de visualización](../docs/guia-visualizacion-boyaca.md) y el [notebook con ejemplos de Boyacá](../kit/Notebooks/Visualizacion_Boyaca.ipynb).

Cada gráfica o mapa debe indicar título, año, fuente, unidad, leyenda e interpretación. Distinga los municipios sin datos y explique los cortes y clasificación.

- Distribución de población por edad y sexo.

- Comparación de producción y rendimiento por cultivo.

- Dispersión de proporción de población joven frente a desempeño.

- Dispersión de producción frente a población de 18 a 64 años.

- Comparación de producción por cada 1.000 habitantes de 18 a 64 años.

- Distribución de clases de capacidad de uso.

- Mapas municipales de población joven, desempeño, producción o rendimiento, producción por 1.000 habitantes y capacidad de uso.

- Mapa bivariado o mapas lado a lado que comparen población joven y desempeño, con clasificación explícita.

## 9. Requisitos de software y selección de herramientas

El proyecto debe utilizar **Python y Git**, un entorno virtual reproducible y un editor de código o entorno de notebooks. El grupo puede trabajar con scripts, con Jupyter Notebook o JupyterLab, o combinar ambos, siempre que el pipeline completo pueda ejecutarse siguiendo las instrucciones de entrega. Se recomienda el entorno Ubuntu/WSL descrito en la [guía de instalación](../docs/instalacion-wsl.md), aunque se acepta otro sistema si el grupo documenta y reproduce la ejecución.

Para el procesamiento de datos, cada grupo elegirá **pandas, Polars o Apache Spark mediante PySpark**. Puede combinar herramientas cuando explique para qué utiliza cada una. Ninguna de estas alternativas otorga una calificación adicional por sí sola. Si elige Spark, debe instalar y documentar una combinación compatible de Spark, PySpark y Java, y explicar si ejecutó en modo local o distribuido; no es obligatorio utilizar un clúster.

### Software sugerido por tarea

La siguiente lista presenta alternativas: no es necesario instalar ni usar todas. El grupo puede proponer otras herramientas justificadas que permitan cumplir y reproducir el trabajo.

| Tarea | Software o bibliotecas posibles | Uso en el proyecto |
| --- | --- | --- |
| Entorno y código | Python, venv o conda, JupyterLab, VS Code | Crear el entorno, desarrollar y ejecutar el análisis. |
| Control de versiones | Git y un repositorio Git | Registrar cambios del código, configuración y documentación. |
| Ingesta y consulta de fuentes | requests, urllib, pandas, Polars, PySpark; navegador | Descargar o leer CSV, Excel y servicios web; conservar la procedencia. |
| Calidad y validación | pandas, Polars, PySpark, Pandera o pytest | Comprobar tipos, rangos, nulos, duplicados y reglas de integración. |
| Limpieza, integración e indicadores | pandas, Polars o PySpark; SQL con DuckDB como complemento | Transformar y unir datos, agrupar y calcular indicadores municipales. |
| Análisis estadístico | SciPy, statsmodels, NumPy | Calcular correlaciones, intervalos, contrastes y regresiones. |
| Análisis geoespacial | GeoPandas, Shapely, pyproj, QGIS | Validar geometrías, transformar coordenadas e intersectar capas. |
| Gráficas | Matplotlib, Seaborn o Plotly | Crear distribuciones, comparaciones y gráficos de dispersión. |
| Mapas | GeoPandas y Matplotlib, Folium, Plotly o QGIS | Crear mapas municipales estáticos o interactivos. |
| Pipeline y ejecución | scripts de Python, Make o un notebook ejecutable | Coordinar etapas, registrar fallos y generar resultados. |
| Documentación y presentación | Markdown, Jupyter Notebook y herramientas de presentación | Describir decisiones, resultados, conclusiones y pasos para reproducirlos. |

### Justificación de la herramienta de procesamiento

En el informe y la sustentación, el grupo deberá identificar la herramienta elegida y explicar: tamaño y formato de los datos procesados; recursos disponibles; facilidad de implementación; tiempo de ejecución y uso de memoria observados cuando sea posible; compatibilidad con las tareas y limitaciones encontradas. Explique por qué esa opción es apropiada para el volumen y los requisitos del proyecto y qué ventajas o costos tendría al menos una alternativa. Una comparación experimental es opcional; si se presenta, debe usar entradas y operaciones equivalentes y describir las condiciones de medición.

Registre las versiones de Python, bibliotecas y software relevante, las dependencias de instalación y los comandos necesarios. Las herramientas de interfaz gráfica, si se usan, deben dejar un procedimiento o código que permita reproducir las operaciones y generar las salidas del pipeline.

## 10. Data lake, pipeline y reproducibilidad

### 10.1 Organización y calidad por capas

Cada grupo debe construir un **data lake** con las siguientes capas. Los nombres de directorio se escribirán en inglés: `bronze`, `silver` y `gold`. `Raw` identifica la zona de recepción, que en este proyecto corresponde a `bronze`.

| Capa | Contenido y formato | Controles y evidencia de calidad |
| --- | --- | --- |
| **Bronze (Raw)** | CSV tal como se descargaron o exportaron, sin limpieza ni sustitución de valores. Separe fuentes y extracciones y registre su procedencia. | Verifique recepción, integridad, codificación, esquema observado, filas, duplicados y valores faltantes. Conserve el diagnóstico y los errores; no modifique los archivos para ocultarlos. |
| **Silver** | Datos validados, normalizados e integrados según su grano, en **Parquet**; geometrías en **GeoParquet**. | Verifique tipos, claves DIVIPOLA, rangos, unidades, vigencias, duplicados, cardinalidad, integridad referencial, geometrías y CRS cuando apliquen. Registre correcciones, exclusiones, rechazos y cobertura. |
| **Gold** | Indicadores, agregados y tablas analíticas para correlaciones y mapas, en **Parquet**; geometrías en **GeoParquet** cuando se incluyan. | Compruebe claves municipio-año, conciliación con `silver`, denominadores, unidades, ausencia de divisiones por cero, cobertura y consistencia de los indicadores. Documente limitaciones y registros no disponibles. |

Para cada capa entregue un informe o archivo de métricas que incluya reglas, cantidad de registros revisados y afectados, resultados, decisiones y fecha de ejecución. Diferencie valores faltantes de ceros; una validación fallida debe quedar registrada y, según la regla definida, detener el proceso o enviar el registro a una zona de rechazos identificada. Los datos de entrada no deben alterarse para superar los controles.

### 10.2 Particionamiento como decisión de diseño

El particionamiento es **opcional** en `silver` y `gold`. Cada grupo decidirá si lo utiliza o no, y justificará su decisión según volumen de datos, patrones de consulta, número y tamaño de archivos y costos de mantenimiento. Si decide particionar, documentará columnas, estructura y criterios —por ejemplo, año cuando sea adecuado—, y validará que la lectura recupere todas las particiones y preserve los resultados. Si decide no particionar, explicará por qué es razonable para su caso. No se exige particionar los CSV de `bronze`.

### 10.3 Estructura sugerida

```text
data_lake/
├── bronze/       # CSV de entrada por fuente y manifiestos
├── silver/       # datos limpios e integrados en Parquet o GeoParquet
└── gold/         # indicadores y agregados en Parquet o GeoParquet
```

Los gráficos, mapas, reportes y métricas de calidad pueden almacenarse en una carpeta de salidas documentada, distinta de los datos de cada capa. La estructura interna puede variar según el diseño del grupo.

### 10.4 Ejecución reproducible

El proceso debe ejecutar recepción CSV en `bronze` → diagnóstico → limpieza y validación en `silver` → integración e indicadores en `gold` → análisis estadístico y espacial → tablas, gráficos, mapas y reporte. Puede implementarse con las herramientas del curso.

- Separar datos originales, procesados y resultados; no sobrescribir originales.

- Documentar dependencias, entorno, configuración, rutas y comando de ejecución.

- Registrar errores, cantidad de registros y progreso de cada etapa.

- Automatizar pruebas de claves, rangos, duplicados y resultados esperados.

- Generar resultados sin pasos manuales ocultos y avisar cuando fallen fuentes o validaciones.

## 11. Entregables

- Código o repositorio con configuración, versiones, dependencias, README de ejecución y justificación de las herramientas seleccionadas.

- Inventario de fuentes, diccionario de datos, manifiestos y reporte de calidad de `bronze`, `silver` y `gold`.

- Data lake con CSV en `bronze`, tablas validadas en Parquet en `silver` y tablas analíticas en Parquet en `gold`; use GeoParquet para geometrías. Documente cómo reproducir las capas y la decisión de particionar o no.

- Pipeline ejecutable, indicadores, resultados estadísticos, gráficos y mapas.

- Informe final con preguntas, hipótesis, fuentes, metodología, resultados, limitaciones, conclusiones y recomendaciones.

- Presentación y sustentación con demostración de la ejecución.

## 12. Rúbrica de evaluación

| Criterio | Porcentaje |
| --- | --- |
| Ingesta y documentación de fuentes | 10 % |
| Calidad de datos y trazabilidad | 20 % |
| Integración municipal, temporal y espacial | 15 % |
| Indicadores e interpretación | 10 % |
| Análisis estadístico e hipótesis | 20 % |
| Gráficos, mapas y comunicación visual | 10 % |
| Pipeline, pruebas y documentación | 10 % |
| Informe, conclusiones y presentación | 5 % |
| Total | 100 % |



Se valorarán las decisiones justificadas y la interpretación honesta. No encontrar una asociación es un resultado válido cuando el análisis está bien sustentado.

La rúbrica anterior califica el contenido de la entrega del proyecto. En el mapa de evaluación del curso se mantiene el 35 % para el proyecto e informe y el 15 % para la sustentación individual.

## 13. Preguntas para la sustentación

- ¿Por qué eligieron pandas, Polars o Spark y cómo se ajusta la elección a los datos y recursos disponibles?

- ¿Qué validaciones se aplicaron en cada capa y por qué decidieron particionar o no las capas `silver` y `gold`?

- ¿Por qué se eligió el periodo y cuántos municipios quedaron incluidos?

- ¿Qué diferencias existen entre población de centros poblados y población municipal?

- ¿Cómo se evitó duplicar producción o población durante la integración?

- ¿Qué significa el índice por población y qué no permite medir?

- ¿Qué representa la clase agrológica predominante y cuáles son sus limitaciones?

- ¿Cuál fue la magnitud de la asociación y qué ocurrió en el análisis de sensibilidad?

- ¿Qué información adicional se requiere para estudiar la disposición al cambio o una posible relación causal?
