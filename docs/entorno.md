# Datos y ejecución del curso

[Windows/WSL](instalacion-wsl.md) · [Linux/macOS](instalacion-linux-macos.md) · [Índice](../README.md)

Como apoyo para las personas con poca experiencia en la CLI de Linux, se anexó la [guía de línea de comandos](guia-cli-linux/README.md), con ejemplos de navegación, consulta y verificación de archivos, además de un cheat sheet de 100 comandos y sus opciones habituales.

Preparar el entorno de la guía correspondiente al sistema. Los ejemplos de navegación siguientes usan la ruta Windows/WSL; en Linux/macOS sustituir la carpeta base por `"$HOME/bigdata"`. Mantener los comandos relativos, los requisitos y el `.venv` base CPU. Antes de iniciar en WSL:

```bash
cd /mnt/c/Users/TUPTC/bigdata
cd big-data-postgraduate
source .venv/bin/activate
cd kit
```

El clon no incluye los originales agroambientales ni los completos PQRS; `--verificar` requiere obtener antes todas las fuentes correspondientes.

## Polars con GPU (opcional)

La instalación NVIDIA tiene una [guía independiente](polars-gpu.md): primero se preparan el controlador y CUDA Toolkit según Linux o WSL 2, y después los paquetes Python en `.venv-gpu`. No ejecutar esa instalación como parte de la preparación CPU. En macOS se utiliza CPU.

Consultar [entornos virtuales por plataforma](entornos-virtuales.md) para crear, activar y verificar `.venv`, así como para la alternativa Windows nativa de las guías rápidas.

## Tres rutas para obtener los datos

- Ruta A, recomendada para clase: descomprimir el paquete docente, que ya contiene data/raw. Ejecutar --verificar. Permite continuar sin Internet una vez instalado el software.
- Ruta B, práctica de descarga: crear una carpeta nueva, copiar 00_datos.py y fuentes.json, y ejecutar --descargar con los IDs requeridos. No descargar todas las fuentes simultáneamente.
- Ruta C, contingencia: copiar una carpeta raw de respaldo verificada mediante --respaldo. El script comprueba el SHA-256 antes de incorporar archivos.

```
python 00_datos.py --descargar agrosavia divipola eva
python 00_datos.py --descargar igac_capacidad igac_quimica
python 00_datos.py --descargar soilgrids wosis nasa chirps
python 00_datos.py --respaldo "/ruta/kit_original/data/raw" --verificar
```

Las URLs exactas están en fuentes.json y en el [catálogo de fuentes](datasets.md). El descargador limita cada respuesta a tres veces el tamaño de referencia o 2 MB, lo que sea mayor. Rechaza páginas HTML, no sobrescribe archivos existentes y conserva una descarga que cambió como .nueva. Un SHA-256 distinto puede deberse a nuevos datos o a cambios de serialización: el docente revisa esquema, valores y conteos antes de aprobar otro corte. No se considera que un HTTP 200 por sí solo sea una descarga válida.

## Descarga manual de los shapes DANE

[Fuente](<https://geoportal.dane.gov.co/servicios/descarga-y-metadatos/datos-geoestadisticos/>)

- Abrir el catálogo vigente y buscar MGN2025-Nivel. Seleccionar los enlaces de Nivel Departamento y Nivel Municipio en formato Shapefile.
- Guardar los ZIP sin modificar como dane_departamentos.zip y dane_municipios.zip dentro de data/raw. Tamaños observados: 12,52 MB y 71,58 MB. Las etiquetas del catálogo pueden diferir del tamaño descargado.
- Verificar con 00_datos.py --verificar. GeoPandas lee los ZIP DANE con read_file y el prefijo zip://. Si se extraen, conservar .shp, .shx, .dbf y .prj juntos y comprobar el CRS antes de reproyectar.
- Si el portal responde 403 o la descarga tarda, usar la copia docente. No insistir con múltiples descargas. El enlace antiguo del MGN devolvió 404 y no debe quedar como dependencia del taller.

No descargar MGN2025_00_COLOMBIA.zip con todos los niveles: el catálogo anuncia aproximadamente 1,5 GB y contiene detalle que no requiere el curso. Los dos ZIP seleccionados incluyen exclusivamente los niveles necesarios. No se reemplazan polígonos por puntos de DIVIPOLA para evitar esa descarga.

## Verificación y organización

```
kit/
  fuentes.json
  00_datos.py
  talleres.py
  spark_taller.py
  data/raw/       # originales sin editar
  salidas/        # resultados reconstruibles
  entregas/      # informes personales
```

Leer salidas/verificacion.json: archivo presente, huella coincidente, conteo esperado, JSON sin error de API y ZIP íntegro. Los scripts reconstruyen y sobrescriben sus salidas homónimas; las conclusiones del estudiante se guardan en entregas. En nuevas descargas registrar fecha, versión, licencia, URL, tamaño y huella. Para reproducibilidad guardar también python --version y python -m pip freeze.

## Preparación del dominio PQRS

Las dependencias se instalan según la guía [WSL](instalacion-wsl.md) o [Linux/macOS](instalacion-linux-macos.md). Desde `kit/`, con `.venv` activo:

```
python pqrs_descarga.py --listar
python 00_datos.py --descargar pqrs-completos
python 00_datos.py --verificar pqrs-completos
```

Las tres muestras incluidas en `data/pqrs_muestras` se preparan desde `kit/` con `python 00_datos.py --descargar pqrs` y se comprueban con `python 00_datos.py --verificar pqrs`. El [taller P01, actividad 0](../talleres/P01.md) detalla este procedimiento. Los archivos existentes que coinciden se conservan; una versión distinta produce error sin sobrescritura. El grupo `pqrs-completos` descarga los seis cortes semestrales de 2023–2025. También puede usarse `pqrs_descarga.py` para seleccionar cortes concretos:

```
python pqrs_descarga.py --descargar 2025_I 2025_II
python pqrs_descarga.py --verificar 2025_I 2025_II
```

La verificación completa requiere los seis cortes; si solo se descargó una selección, verificar explícitamente esos periodos. Para 2025-II, el descargador conserva el ZIP original, extrae el TXT y lo presenta a los motores como `PQRD_2025_II.csv`. La descarga rechaza HTML, limita el tamaño, comprueba SHA-256 y conserva como `.nueva` una fuente cuyo contenido cambió.

Espacio: 5 GB para la ruta de muestras y datos agroambientales; reservar al menos 12 GB para los seis CSV PQRS, el ZIP de 2025-II, Parquet, temporales y salidas. Con herramientas instaladas, planificar 20–25 GB libres para la ruta completa. Son presupuestos preventivos, no tamaños de instalación medidos. Usar SSD y bloques de 25.000 filas; bajar a 5.000–10.000 si la RAM es limitada.

## Notebooks actuales

Registrar el kernel según la guía del sistema. Con el entorno de la raíz activo y situado en `kit/`:

```bash
python -m jupyter lab --no-browser --ip=127.0.0.1
```

Abrir `Notebooks/` y seleccionar el kernel BigData correspondiente al sistema. En Windows las dependencias se instalan dentro de WSL; en Linux/macOS, de forma nativa. Los anexos históricos conservan comandos originales de Colab únicamente como referencia.

## Rutas de los scripts

Los scripts vigentes resuelven sus fuentes y salidas a partir de su archivo dentro de `kit/`. En PQRS, `--config`, `--datos` y `--salidas` relativos también se interpretan desde `kit/`; las rutas absolutas se respetan. El descargador general interpreta `--respaldo` desde el directorio actual: usar una ruta absoluta para una copia externa. No escribir rutas de otra máquina dentro de los scripts.

## Ejecución geoespacial

Consultar la [guía práctica de GeoPandas](manual-geopandas.md) para mapas de Colombia, resaltado de municipios y consultas tabulares por meses y edades antes de unirlas a las geometrías.

Usar el entorno base CPU `.venv` del curso con GeoPandas, Pyogrio, Rasterio y Matplotlib. Desde `kit/`, `python talleres.py geografia` ejecuta E08, `python talleres.py suelo` prepara E09 y `python talleres.py clima` prepara E11. Los mapas se generan en Jupyter o como PNG en `salidas/`. `python talleres.py clima_suelo` reúne ambos informes para compatibilidad y requiere las cuatro fuentes SoilGrids, WoSIS, NASA y CHIRPS. Consultar el [índice de notebooks](../kit/Notebooks/README.md).
