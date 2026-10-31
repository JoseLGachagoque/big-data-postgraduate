# Trabajo en casa: procesamiento con Spark e integración geoespacial

**Temas de las clases del 16 y 17 de octubre de 2026 · E07, E08 y E09**

Preparado por el PhD Esteban Hernández, CyberColombia.

**Propuesta para revisión docente.** Modalidad propuesta: individual. Fecha límite y medio de entrega: por definir. La ponderación de esta actividad dentro del curso queda por definir; no se añade un porcentaje a la evaluación vigente. Esta guía plantea trabajo en casa sobre los temas del fin de semana. Su adopción requiere actualizar la modalidad y la entrega de E07–E09, actualmente previstas durante la clase del sábado; no supone entregar dos veces el mismo trabajo.

## Orientaciones para el estudiante

El propósito es que puedas leer datos, revisar sus tipos, transformarlos, verificar resultados y explicar las decisiones tomadas. Utiliza los notebooks de clase como punto de partida, pero desarrolla y comenta las modificaciones solicitadas. No basta con ejecutar todas las celdas y entregar las mismas salidas del ejemplo.

Conserva los archivos originales. Utiliza operaciones visibles de pandas, Spark, DuckDB, GeoPandas y Rasterio. No reemplaces el desarrollo por una llamada a `talleres.py`, `spark_taller.py` o funciones que realicen el ejercicio completo. Los comandos de descarga y verificación sí se utilizan para preparar las fuentes.

Antes de una transformación importante, escribe qué esperas obtener. Después de ejecutarla, explica si el resultado coincide con lo esperado y cómo lo comprobaste. Documenta los errores encontrados y su solución. Si una comprobación falla, conserva la evidencia y explica el problema; no cambies el valor esperado solo para que la celda termine sin error.

Tiempo de dedicación orientativo: entre 6 y 8 horas, con el ambiente instalado y los datos disponibles. No es un límite de ejecución ni un criterio de calificación.

## Preparación del ambiente y de los datos

Utiliza el único `.venv` del repositorio y JDK 21, siguiendo la guía de [Windows/WSL](../docs/instalacion-wsl.md) o [Linux/macOS](../docs/instalacion-linux-macos.md). Selecciona en Jupyter el kernel de ese entorno. Spark debe ejecutarse con `local[2]`.

En WSL, la carpeta base es `/mnt/c/Users/TUPTC/bigdata` y el repositorio está en `/mnt/c/Users/TUPTC/bigdata/big-data-postgraduate`. En Linux/macOS, usa la ruta real de tu clon, por ejemplo `~/bigdata/big-data-postgraduate`. Ajusta la variable `repositorio` en cada notebook. Si necesitas clonar, sigue la guía de instalación y utiliza la rama `main`.

Desde `kit/`, con el entorno activo, prepara las fuentes:

```bash
python 00_datos.py --descargar eva divipola agrosavia
python 00_datos.py --descargar igac_capacidad igac_quimica igac_correlacion soilgrids wosis
python 00_datos.py --verificar eva divipola agrosavia igac_capacidad igac_quimica igac_correlacion soilgrids wosis
```

Para los ZIP DANE, sigue la descarga o copia docente indicada en [E08](E08.md). Deben quedar en `kit/data/raw/dane_departamentos.zip` y `kit/data/raw/dane_municipios.zip`. Después verifica:

```bash
python 00_datos.py --verificar dane_departamentos dane_municipios
```

Registra las versiones de Python, Java, Spark y las bibliotecas utilizadas. No se requiere GPU ni un servicio de nube. No se necesitan los CSV PQRS completos para esta actividad.

## Ejercicio 1. ¿Spark y DuckDB calculan el mismo rendimiento?

**Apoyo:** [05 Spark: lectura y agregación](../kit/Notebooks/05_Spark_lectura_y_agregacion.ipynb).

1. Lee EVA y DIVIPOLA como texto. Presenta cinco filas, los tipos de datos y el número de registros. Explica por qué los códigos municipales deben conservarse como texto.
2. Convierte año, área cosechada, producción y rendimiento publicado. Conserva el valor original de cada campo convertido y la fila de procedencia. Separa en una tabla las filas fuera del dominio del cálculo: área no positiva, producción negativa o valores requeridos ausentes/no convertibles. Explica qué significa cada condición; no clasifiques una fila como errónea solo porque queda fuera de esta pregunta analítica.
3. Escribe EVA y la dimensión municipal en Parquet. Vuelve a leer ambos archivos y comprueba igualdad de contenido, tipos y cantidad de filas.
4. Ejecuta la agregación Spark por municipio, cultivo, estado físico y año. Calcula `suma de producción / suma de área cosechada`. Ejecuta la misma consulta en DuckDB y compara todas las claves y medidas, con tolerancia absoluta de `0.000001` y tolerancia relativa cero.
5. **Modificación propia:** elige un cultivo, un estado físico y un año presentes en los datos. Anota la selección y aplica exactamente los mismos filtros en ambos motores. Repite la comparación y guarda el resultado como `rendimiento_seleccion.csv`. Si la selección queda vacía, explica el motivo y elige otra combinación existente.
6. En un grupo de la selección con varias filas, compara el cociente de sumas con el promedio del rendimiento publicado. Presenta los numeradores, denominadores y resultados. Si no existe tal grupo, usa otro del conjunto completo y documenta el cambio. Explica por qué no se puede asumir que ambos cálculos sean iguales.
7. Mide por separado una acción materializada de cada motor con `%%time`. Escribe exactamente qué incluye cada tiempo y deja la visualización y las comprobaciones fuera de la celda medida. Identifica lectura, filtro, agregación y redistribución en el plan Spark.

**Preguntas para responder:** ¿Por qué construir un DataFrame Spark no equivale a ejecutar toda la consulta? ¿Qué trabajo provoca la acción que mediste? ¿Por qué una ejecución local no demuestra cuál motor será más rápido en un clúster?

**Evidencias:** notebook ejecutado, `control_spark.json`, `rendimiento_seleccion.csv`, tabla de comparación de indicadores y explicación del plan. Para el corte docente completo se esperan 159.616 filas aptas y 107.620 grupos; esos controles no se aplican a tu selección filtrada.

## Ejercicio 2. Unir municipios y construir un ranking reproducible

**Apoyo:** [06 Spark: joins y ventanas](../kit/Notebooks/06_Spark_joins_y_ventanas.ipynb). Requiere los productos del ejercicio 1.

1. Verifica que DIVIPOLA tenga un único registro por código municipal y que no haya códigos nulos. Implementa las comprobaciones antes de unir; no presupongas la cardinalidad.
2. Ejecuta un `LEFT JOIN` entre los grupos de rendimiento y la dimensión municipal. Compara las filas antes y después. Obtén además los grupos sin correspondencia mediante `left_anti`; si no hay casos, registra el resultado cero.
3. **Experimento controlado:** en una copia de la dimensión, duplica un municipio presente en los resultados. Filtra el rendimiento a ese municipio y muestra cómo el join aumenta las filas. Explica qué comprobación habría impedido el problema. No guardes la dimensión alterada sobre el original ni la uses en los pasos siguientes.
4. Compara el plan del join normal con el de `broadcast`. Identifica la estrategia observada y explica cuándo tendría sentido distribuir una dimensión pequeña a los ejecutores. Si ambos planes usan broadcast, explica por qué Spark pudo elegirlo automáticamente.
5. Obtén los tres municipios con mayor rendimiento por cultivo, estado físico y año mediante `row_number`. Desempata por código municipal ascendente. Verifica el resultado con DuckDB usando el mismo agregado de entrada, como hace el notebook.
6. **Modificación propia:** cambia el ranking a cinco municipios para la selección del ejercicio 1. Comprueba que haya como máximo cinco filas y que las posiciones sean consecutivas desde 1. Si existen menos de cinco municipios, conserva los disponibles y explícalo; no completes con filas inventadas.
7. Repite la agregación con cuatro y dos particiones de shuffle. Compara planes, archivos generados y contenido. Explica por qué la ejecución adaptativa puede producir un número de archivos distinto al configurado.

**Evidencias:** notebook ejecutado, `control_joins_ventanas.json`, `top5_seleccion.csv` y tabla del experimento de duplicación con filas antes/después. No interpretes el ranking como una recomendación agronómica.

## Ejercicio 3. Integración territorial sin multiplicar registros

**Apoyo:** [E08 Geoespacial](../kit/Notebooks/E08_Geoespacial.ipynb).

1. Lee los límites DANE y las muestras IGAC con GeoPandas. Informa CRS, número de geometrías y cantidad de geometrías ausentes, vacías o inválidas. Si reparas geometrías, registra cuántas y conserva las fuentes originales.
2. **Selección propia:** elige un año presente en AGROSAVIA y justifica la elección. Normaliza departamento y municipio, enlaza con DIVIPOLA y reporta las filas sin código territorial. No asignes códigos por similitud de nombres sin evidencia.
3. Para el año seleccionado, cuenta registros por código municipal. Verifica que la tabla agregada sea única por municipio y únela a las geometrías con `validate="one_to_one"`. Separa municipios sin conteos y códigos de la tabla sin geometría. Explica por qué un valor faltante en el mapa no equivale automáticamente a cero análisis.
4. Genera un mapa con título, año, leyenda y una nota sobre el significado del conteo. No presentes los registros AGROSAVIA como cobertura completa o muestra representativa de todos los suelos del municipio.
5. Intersecta las muestras IGAC con los municipios. Transforma a EPSG:9377 para calcular hectáreas y conserva únicamente áreas positivas. Explica la diferencia entre `set_crs` y `to_crs` y por qué no se calculan hectáreas directamente en grados.
6. Exporta a GeoPackage, vuelve a leer y verifica cantidad de filas, CRS y columnas. Elige una intersección y presenta su área calculada junto con los atributos de área originales, si existen. Revisa sus unidades antes de compararlos; no supongas que el atributo original fue recalculado al recortar.

**Evidencias:** notebook ejecutado, mapa PNG, `control_geografico.json`, CSV de la unión municipal y GeoPackage de las intersecciones. Para la copia docente se esperan 1.122 geometrías municipales y 15 intersecciones de área positiva. Las muestras IGAC no permiten calcular cobertura temática del municipio completo.

## Ejercicio 4. ¿Es válido comparar un píxel con una medición de suelo?

**Apoyo:** [E09 Suelo y profundidad](../kit/Notebooks/E09_Geoespacial.ipynb).

1. Abre SoilGrids con Rasterio y registra dimensiones, CRS, extensión, transformación y NoData. Lee respetando la máscara del archivo y aplica el factor `pH = valor / 10`.
2. Cuenta los ceros antes de excluirlos provisionalmente del resumen. Reporta cuántos píxeles tienen valores positivos dentro del dominio de pH y explica por qué no debes modificar el archivo para declarar esos ceros como NoData sin revisar los metadatos.
3. **Análisis propio:** calcula mínimo, máximo, media y mediana de los píxeles admitidos. Calcula además la media incluyendo los ceros no enmascarados, manteniendo el mismo límite superior de pH. Presenta la diferencia y explica cómo cambia la interpretación. Esta segunda media es un análisis de sensibilidad, no una corrección de la fuente.
4. Lee WoSIS y construye una tabla por perfil y profundidad con método y precisión de ubicación. Distingue registros, horizontes y perfiles; comprueba cuáles intersectan la extensión del ráster.
5. Presenta el mapa del recorte y la tabla de perfiles. Describe las diferencias entre la predicción SoilGrids, las mediciones WoSIS y los atributos cartográficos IGAC.
6. Propón un protocolo breve para validar la predicción: coincidencia espacial, profundidad, método de laboratorio, unidades, tratamiento de faltantes y separación entre datos de ajuste y evaluación. Si las fuentes disponibles no permiten una comparación válida, explica qué falta. No inventes mediciones ni calcules un error de predicción con observaciones incompatibles.

**Evidencias:** notebook ejecutado, `control_suelo.json`, mapa PNG, tabla de perfiles y `sensibilidad_ceros_ph.csv`. Controles de la copia docente: 42 filas × 44 columnas, 188 ceros por revisar, 1.660 píxeles admitidos, 10 registros WoSIS y 3 perfiles distintos.

## Organización de la entrega

Entrega una carpeta comprimida con tu apellido y nombre. Incluye:

- Los cuatro notebooks ejecutados, con código, salidas relevantes y respuestas en celdas Markdown. Conserva el orden 05, 06, E08 y E09.
- Una carpeta `evidencias/` con los controles JSON, los CSV solicitados, los mapas PNG y el GeoPackage. Los productos base se generan en `kit/salidas/E07`, `kit/salidas/E08` y `kit/salidas/E09`; copia a la entrega únicamente las evidencias requeridas.
- Un informe breve, de dos a tres páginas, con decisiones, resultados principales, errores encontrados y límites de interpretación. Incluye tus selecciones de cultivo/estado/año y del año AGROSAVIA.
- Un archivo `LEEME.txt` con versiones, rutas que deben adaptarse, orden de ejecución y fuentes utilizadas. Identifica el commit del repositorio con `git rev-parse HEAD` desde su raíz y adjunta el resultado de la verificación de datos.

No incluyas `.venv`, cachés, archivos originales ni todos los datasets intermedios de Spark. Deben poder reconstruirse con las celdas del notebook. No copies los archivos DANE originales dentro de la entrega.

Reinicia el kernel y ejecuta cada notebook en orden antes de entregar. Detén Spark al finalizar 05 y 06. Si una limitación del equipo impide completar un paso, adjunta el mensaje de error, la configuración y lo que sí verificaste; no presentes ese paso como exitoso.

## Criterios de revisión

| Criterio | Evidencia esperada |
|---|---|
| Reproducibilidad | Fuentes verificadas, entorno identificado, rutas editables y ejecución ordenada |
| Control de los datos | Tipos, valores no convertibles, faltantes y registros fuera del dominio conservados y explicados |
| Corrección del cálculo | Cociente de sumas, claves y filtros coherentes; equivalencia por grupo, no solo por total |
| Integración y ventanas | Cardinalidad verificada, experimento de duplicación, anti-join y ranking con desempate |
| Interpretación de tiempos | Acción materializada y alcance de la medición explícito; sin conclusiones de escalabilidad injustificadas |
| Rigor geoespacial | CRS, unidades, geometrías, máscaras y profundidad revisados; límites de cobertura declarados |
| Análisis propio | Selecciones justificadas, modificaciones solicitadas y conclusiones apoyadas en resultados |

Los valores de referencia ayudan a detectar diferencias de entrada o de procedimiento. Obtener el mismo número sin explicar cómo se calculó no demuestra comprensión del ejercicio.
