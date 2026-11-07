# Datos preparados para la guía de visualización

Estos archivos son recortes reproducibles para enseñar visualización. No sustituyen la validación ni la selección de vigencias de cada proyecto. Fecha de preparación: 31 de octubre de 2026.

## Población municipal DANE

`poblacion_boyaca_dane_2020_2025.csv` contiene 123 municipios y seis años de proyecciones, 738 filas, para el área geográfica **Total**. Incluye población total, hombres, mujeres, personas de 18 a 44 años y de 18 a 64 años, y mujeres y hombres de 18 a 44 años. Se sumaron edades simples con extremos incluidos. Las cifras son proyecciones y no conteos observados.

- [Página y metodología del DANE](https://www.dane.gov.co/index.php/estadisticas-por-tema/demografia-y-poblacion/proyecciones-de-poblacion).
- [Archivo original municipal por área, sexo y edad 2018–2042](https://www.dane.gov.co/files/censo2018/proyecciones-de-poblacion/Municipal/PPED-AreaSexoEdadMun-2018-2042_VP.xlsx), versión publicada en 2025. Hoja `PobMunicipalxÁreaSexoEdad`; columnas de edad simple por sexo.
- SHA-256 del archivo descargado: `7e461635315664d44ba52cc7f951947085a0ea6f2dda72fe2efed11a76880516`.
- Preparación: `python proyecto/datos/preparar_poblacion.py RUTA_AL_XLSX proyecto/datos/poblacion_boyaca_dane_2020_2025.csv`. Requiere openpyxl. El libro original es grande y su lectura puede tardar.

## Geometrías municipales DANE

`municipios_boyaca_mgn_2025.geojson` deriva del [Marco Geoestadístico Nacional 2025](https://geoportal.dane.gov.co/descargas/mgn_2025/MGN2025_MPIO_GRAFICO.zip), filtrado al departamento 15. El área en km² se calculó a partir de la geometría original en EPSG:9377; después se simplificó la geometría con tolerancia de 75 metros y se convirtió a EPSG:4326. Las geometrías se usan para visualización, no para reemplazar la capa original en análisis espaciales o delimitaciones oficiales.

SHA-256 del ZIP original: `a3c01393059be8f2947de5e0a828faa4c7a43119819a667a8124854340bc141f`.

## Evaluaciones agropecuarias UPRA

`eva_papa_boyaca_2024.csv` contiene las filas de Boyacá, 2024, categoría **Papa todas las variedades**, estado **En fresco** y períodos disponibles A y B, derivadas de las [Evaluaciones Agropecuarias Municipales](https://www.datos.gov.co/api/views/uejq-wxrr/rows.csv?accessType=DOWNLOAD). Se conservaron código, nombre, período, área cosechada y producción. El ejemplo no mezcla otras categorías de papa. El rendimiento se calcula después de agregar la producción y el área.

SHA-256 del CSV original: `4df00a59a79f5905a5adc1d8b918af828e8e3eed9060c7793392bbad70375d73`.

Para regenerar ambos recortes, instale los requisitos de la guía y ejecute:

```bash
python proyecto/datos/preparar_capas.py RUTA_MUNICIPIOS.zip RUTA_EVA.csv proyecto/datos
```

El dataset del proyecto final puede ser una fuente o versión distinta. Compare cobertura, estado físico, unidades y metodología antes de integrar registros. Consulte las condiciones de uso de cada entidad.
