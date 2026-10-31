# Índice de talleres

[Mapa de evaluación y prerrequisitos](../docs/mapa-ejercicios.md).

- [E01 Pregunta y procedencia](E01.md)
- [E02 Descarga y perfil inicial](E02.md)
- [E03 Identidad territorial y vigencias](E03.md)
- [E04 Formatos y contrato de datos](E04.md)
- [E05 Calidad de análisis de suelo](E05.md)
- [E06 Rendimiento agrícola e integración SQL](E06.md)
- [E07 Spark y equivalencia de resultados](E07.md)
- [E08 Shapes y capacidad de uso](E08.md)
- [E09 Propiedades del suelo y profundidad](E09.md)
- [E10 Rendimiento del procesamiento](E10.md)
- [E11 Clima y reproducción de eventos](E11.md)
- [E12 Integración y verificación del pipeline local](E12.md)
- [E13 Proyecto integrador por dominio](E13.md)
- [I01 Introducción finita a eventos con NASA](I01.md)
- [P01 Perfil PQRS y lectura por bloques](P01.md)
- [P02 Parquet, contrato y reejecución](P02.md)
- [P03 Calidad de reportes y consulta diferida](P03.md)
- [P04 Datos completos 2023–2025 y rendimiento Polars–pandas](P04.md)

## Soluciones de referencia

Los [ejercicios de apoyo con pandas](../ejercicios/README.md) reúnen tres prácticas sobre AGROSAVIA, EVA y DIVIPOLA para cuatro horas. Sus plantillas están en `ejercicios/`; los notebooks resueltos se entregan en `soluciones/` con los nombres indicados en cada enunciado.

Las [soluciones de P01, P02 y P03](../soluciones/README.md) incluyen un notebook por taller, con desarrollo de cada tarea, controles e interpretación.

Las actividades geoespaciales E08, E09 y E11 se desarrollan con GeoPandas, Rasterio y Matplotlib en Jupyter. Consultar los [notebooks y sus requisitos](../kit/Notebooks/README.md#ejercicios-geoespaciales).

## Antes de los talleres PQRS (P01–P04)

Con `.venv` activo, desde `kit/`, preparar siempre las muestras y comprobarlas:

```bash
python 00_datos.py --descargar pqrs
python 00_datos.py --verificar pqrs
```

Continuar cuando los tres cortes de muestra indiquen `coincide`. P03 requiere además DIVIPOLA y el Parquet generado por P02. P04 sigue una ruta independiente con los seis cortes semestrales completos de 2023–2025: el kit descarga y verifica las fuentes oficiales, concilia primero la lectura Polars–DuckDB y después compara Polars con pandas.

## Propuesta de trabajo en casa

[Ejercicios sobre los temas del 16 y 17 de octubre](trabajo-casa-16-17-octubre.md): Spark, joins y ventanas, integración territorial y suelo. Borrador para revisión docente; fecha, medio de entrega y ponderación por definir.
