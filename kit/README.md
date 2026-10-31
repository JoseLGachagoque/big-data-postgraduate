# CURSO DE POSTGRADO: BIGDATA, ESPECIALIZACIÓN EN BASES DE DATOS
Preparado por el PhD Esteban Hernández, CyberColombia
Programa del 2 de octubre al 7 de noviembre de 2026. 64 horas efectivas de clase en línea. Recesos y almuerzos excluidos.

## Preparación del entorno

Python 3.12 y un entorno base CPU `.venv` por instalación. Seguir [Windows/WSL](../docs/instalacion-wsl.md) o [Linux/macOS](../docs/instalacion-linux-macos.md). La [referencia de entornos virtuales](../docs/entornos-virtuales.md) explica creación, activación y kernels en cada plataforma.

La [instalación opcional de Polars GPU NVIDIA](../docs/polars-gpu.md) es independiente: preparar primero controlador y CUDA Toolkit compatibles y luego instalar `requirements_gpu.txt` en `.venv-gpu`, solo Linux/WSL 2. No instalar esos requisitos en macOS ni como parte del entorno CPU.

Los comandos siguientes usan la ruta WSL; en Linux/macOS usar `$HOME/bigdata` como carpeta base. La guía WSL instala Python, JDK 21 y Jupyter dentro de Ubuntu. No compartir ese virtualenv con Windows nativo.

En cada sesión, dentro de Ubuntu:

```bash
cd /mnt/c/Users/TUPTC/bigdata
cd big-data-postgraduate
source .venv/bin/activate
source "$HOME/.config/bigdata/entorno.sh"
cd kit
python pqrs_talleres.py perfil
```


Las instalaciones de paquetes y herramientas se realizan según la guía del sistema elegido.
Después de descargar las fuentes, ejecutar la ruta del taller correspondiente.
Orden agroambiental: perfil, calidad, consultas; luego geografia, suelo, clima,
benchmark según la sesión. El comando `modelo` es una referencia opcional del enfoque anterior. E12 integra el pipeline conforme a su [enunciado vigente](../talleres/E12.md); ese comando no ejecuta E12. Spark por lotes requiere calidad y consultas.

## ARCHIVOS
fuentes.json contiene URL, tamaño y SHA-256 del corte original. data/raw debe contener 12 archivos originales (descargados o copiados del respaldo; no incluidos en Git), 136,4 MB en conjunto (ZIP de DANE sin extraer). salidas se crea al ejecutar y puede reconstruirse; conservar aparte las entregas personales. Los scripts escriben nuevamente sus salidas homónimas; no editar esas salidas como único original.
El archivo controles_referencia.json contiene resultados del corte docente, no garantías sobre futuras actualizaciones.

## DESCARGA

```bash
python 00_datos.py --listar
python 00_datos.py --descargar agrosavia divipola eva
```

El descargador conserva archivos existentes. Para practicar descarga desde cero, copiar los scripts y fuentes.json a otra carpeta sin data/raw y ejecutar allí.
Si el SHA-256 cambia, el archivo nuevo queda con extensión .nueva y NO sustituye el corte docente. El docente debe revisar esquema y recalcular controles antes de incorporarlo. WFS/WCS pueden cambiar el orden o la codificación sin cambiar valores: investigar la diferencia.
Para copiar el respaldo a un kit vacío: python 00_datos.py --respaldo "/ruta/al/kit_original/data/raw" --verificar
Para una copia almacenada en Windows, usar su ruta Ubuntu: /mnt/c/Users/TUPTC/bigdata/respaldo/data/raw.
DANE requiere navegador: usar el catálogo vigente, descargar ZIP y guardarlo con los nombres dane_departamentos.zip y dane_municipios.zip. No separar SHP/SHX/DBF/PRJ al extraer.

## TAMAÑOS Y EQUIPO
8 GB de RAM: cerrar aplicaciones y trabajar con un departamento o las muestras incluidas; Spark local[2]. Recomendado: 16 GB RAM y 5 GB libres para este kit y salidas, más espacio para Python, Java, GeoPandas y Spark. Presupuesto de instalación y entorno completo: 10–15 GB libres. Son estimaciones preventivas, no tamaños medidos de instalación.
La descompresión de shapes y los cruces geométricos pueden ocupar mucho más que los ZIP. No descargar el MGN nacional con todos los niveles (el catálogo anuncia aproximadamente 1,5 GB), ni todos los rásteres globales de SoilGrids/CHIRPS.

## ALCANCE
Las muestras IGAC son 5 polígonos por tema y 10 registros de correlación. WoSIS contiene 10 capas de 3 perfiles de Colombia. No son inventarios completos. NASA contiene 31 días de un punto demostrativo, CHIRPS un mes de Latinoamérica y SoilGrids un recorte pequeño. No hay datos inventados; la práctica de eventos cambia el orden de llegada de registros reales.
El manual explica objetivos, tiempos, pasos, criterios, unidades y advertencias de cada ejercicio. Las propiedades del suelo no se convierten automáticamente en recomendaciones de fertilización. Los códigos municipales, los años, la profundidad y la escala condicionan cualquier integración.

## PQRS Y NOTEBOOKS
Preparar las muestras: python 00_datos.py --descargar pqrs
Verificarlas: python 00_datos.py --verificar pqrs
Tres muestras reales de 1.000 filas por corte están en `data/pqrs_muestras`; total 2,235 MB. P04 descarga seis cortes completos de 2023–2025 con `python 00_datos.py --descargar pqrs-completos`: 5.327.501 registros y aproximadamente 3,830 GB de CSV. El corte 2025-II llega comprimido; el kit conserva el ZIP en `data/pqrs_completos/originales/` y genera `PQRD_2025_II.csv`. Los originales voluminosos no se incluyen en el repositorio ni en el ZIP del curso.
Instalar dependencias en el entorno WSL siguiendo ../docs/instalacion-wsl.md.

```bash
python pqrs_talleres.py perfil
python pqrs_talleres.py formatos
python pqrs_talleres.py calidad
python pqrs_talleres.py benchmark
python pqrs_talleres.py eventos
```

La calidad se ejecuta después de formatos. El benchmark usa la proyección CSV de 16 campos y sus dos versiones Parquet, con la misma consulta y universo de filas. Los originales conservan 38 campos.
Notebooks/: cuatro guías PQRS/eventos y tres guías geoespaciales E08, E09 y E11, ejecutables con los datos del kit. Seleccionar el kernel del mismo entorno.

## CALENDARIO
Fechas, temas, horas y recesos en ../docs/calendario_contractual.json y ../docs/calendario.md. Los viernes 16, 23 y 30 de octubre y 6 de noviembre cierran a las 21:15. Sustentación final el 7 de noviembre, 08:00–16:30. El trabajo autónomo es opcional y no reemplaza horas de docencia.
