"""Rutas, parámetros y catálogo de fuentes. Todo el pipeline lee de aquí.

Dueño: P6. Cambiar este archivo solo por PR aprobado por el equipo.
"""
from pathlib import Path

# ---------------------------------------------------------------- rutas
ROOT = Path(__file__).resolve().parents[1]
STAGING = ROOT / "staging"            # originales del proveedor (fuera del data lake)
BRONZE = ROOT / "data_lake" / "bronze"
SILVER = ROOT / "data_lake" / "silver"
GOLD = ROOT / "data_lake" / "gold"
REJECTS = ROOT / "data_lake" / "rejects"
OUTPUTS = ROOT / "outputs"
QUALITY = OUTPUTS / "quality"
STATS = OUTPUTS / "stats"
FIGURES = OUTPUTS / "figures"
MAPS = OUTPUTS / "maps"
FIXTURES = ROOT / "tests" / "fixtures"

# ---------------------------------------------------------------- parámetros de análisis
# Las fuentes NO comparten un año común (ver docs/informe_final.md, sección Fuentes).
ANIO_MDM = 2020          # único año del archivo de Desempeño Municipal
ANIO_EVA = 2023          # único año del archivo de Evaluaciones Agropecuarias
ANIO_PIRAMIDE = 2023     # año para la pirámide poblacional (coincide con la EVA)

# El archivo MDM trae dos bloques de 123 filas, ambos rotulados 2020.
# A = filas 1-123, B = filas 124-246. El bloque B coincide 123/123 con los nombres DANE;
# el bloque A tiene los códigos 15022/15047 cruzados. VERIFICAR en el portal antes de entregar.
MDM_BLOQUE_OFICIAL = "B"

CULTIVO_SELECCIONADO = "Papa"   # cultivo de la hipótesis de suelo
ALFA = 0.05                      # nivel de significancia fijado antes del análisis
N_MUNICIPIOS = 123
COD_DEPARTAMENTO = "15"

CRS_ORIGEN = "EPSG:4326"   # coordenadas geográficas (grados)
CRS_AREAS = "EPSG:9377"    # MAGNA-SIRGAS Origen Nacional: para áreas en metros

# ---------------------------------------------------------------- catálogo de fuentes
# nombre_fuente: (archivo original en staging, tipo, entidad, url, crs)
FUENTES = {
    "evaluaciones_agropecuarias": (
        "EVALUACIONES_AGROPECUARIAS_MUNICIPALES_-_DEPARTAMENTO_DE_BOYAC_.csv", "csv",
        "UPRA / MADR",
        "https://www.datos.gov.co/api/views/sn28-aa8q/rows.csv?accessType=DOWNLOAD", None),
    "centros_poblados": (
        "POBLACI_N_DE_LOS_DIFERENTES_CENTROS_POBLADOS_EN_LOS_MUNICIPIOS_DE_BOYAC__-_DEPARTAMENTO_DE_BOYAC_.csv", "csv",
        "Gobernación de Boyacá (con base en proyecciones DANE)",
        "https://www.datos.gov.co/api/views/seua-4ze8/rows.csv?accessType=DOWNLOAD", None),
    "desempeno_municipal": (
        "Medici_n_del_Desempe_o_Municipal_por_Municipio_-_DEPARTAMENTO_DE_BOYAC_.csv", "csv",
        "DNP",
        "https://www.datos.gov.co/api/views/665j-iwk5/rows.csv?accessType=DOWNLOAD", None),
    "poblacion_dane": (
        "poblacion_boyaca_dane_2020_2025.csv", "csv",
        "DANE (recorte del curso desde PPED-AreaSexoEdadMun-2018-2042_VP.xlsx)",
        "https://www.dane.gov.co/files/censo2018/proyecciones-de-poblacion/Municipal/PPED-AreaSexoEdadMun-2018-2042_VP.xlsx", None),
    "municipios_mgn": (
        "municipios_boyaca_mgn_2025.geojson", "geojson",
        "DANE - MGN 2025 (simplificado 75 m por el curso)",
        "https://geoportal.dane.gov.co/descargas/mgn_2025/MGN2025_MPIO_GRAFICO.zip", CRS_ORIGEN),
    "capacidad_uso_igac": (
        "capacidad_uso_tierras_boyaca.geojson", "geojson",
        "IGAC - Capacidad de uso de las tierras 1:100.000 (2004)",
        "https://mapas.igac.gov.co/server/rest/services/agrologia/mapageneraldecapacidaddeusodelastierrasdepartamentodeboyaca/MapServer",
        CRS_ORIGEN),  # el GeoJSON no declara CRS; coordenadas en grados -> se asume 4326 y se documenta
}


def bronze_csv(fuente: str) -> Path:
    """Ruta del CSV de una fuente en bronze."""
    return BRONZE / fuente / f"{fuente}.csv"


def asegurar_carpetas() -> None:
    for p in (BRONZE, SILVER, GOLD, REJECTS, QUALITY, STATS, FIGURES, MAPS, FIXTURES):
        p.mkdir(parents=True, exist_ok=True)
