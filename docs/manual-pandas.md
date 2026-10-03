# Guía práctica de pandas para los talleres de Big Data

Funciones más usadas de **pandas 2.2.3** para leer, inspeccionar, limpiar, transformar, combinar y guardar los datos de **DIVIPOLA, EVA y AGROSAVIA** descargados con `kit/00_datos.py`.

| Símbolo | Significado |
|:---:|---|
| 📘 | Concepto necesario para entender la operación. |
| ✅ | Control para comprobar el resultado. |
| ⚠️ | Error frecuente o límite de interpretación. |

```mermaid
flowchart LR
    A[Leer] --> B[Inspeccionar]
    B --> C[Convertir y limpiar]
    C --> D[Filtrar, agrupar o unir]
    D --> E[Comprobar totales]
    E --> F[Guardar]
```

> **📘 Idea central:** que una operación termine sin errores no significa que el resultado sea correcto. Después de cada paso se revisan las columnas, los tipos, la cantidad de filas y qué representa cada fila.

## Contenido

1. [Preparación y datos de ejemplo](#1-preparación-y-datos-de-ejemplo)
2. [Leer datos](#2-leer-datos)
3. [Inspeccionar](#3-inspeccionar)
4. [Convertir tipos y tratar ausencias](#4-convertir-tipos-y-tratar-ausencias)
5. [Seleccionar y filtrar](#5-seleccionar-y-filtrar)
6. [Crear y transformar columnas](#6-crear-y-transformar-columnas)
7. [Claves y duplicados](#7-claves-y-duplicados)
8. [Ordenar, agrupar y resumir](#8-ordenar-agrupar-y-resumir)
9. [Combinar tablas](#9-combinar-tablas)
10. [Guardar y procesar archivos grandes](#10-guardar-y-procesar-archivos-grandes)
11. [Recetas para problemas comunes](#11-recetas-para-problemas-comunes)
12. [Errores frecuentes](#12-errores-frecuentes)
13. [Resumen de funciones](#13-resumen-de-funciones)
14. [Referencias](#14-referencias)

## 1. Preparación y datos de ejemplo

```python
import sys
from pathlib import Path

import numpy as np
import pandas as pd

print("Python:", sys.version.split()[0])
print("Intérprete:", sys.executable)
print("pandas:", pd.__version__)
print("Directorio actual:", Path.cwd())
```

Los ejemplos utilizan únicamente estos tres CSV, ubicados en `kit/data/raw/`. Cada fuente cumple un propósito distinto:

| Archivo | Contenido | Uso en la guía |
|---|---|---|
| `eva.csv` | Registros de evaluación agrícola por territorio, cultivo y periodo. | Tabla principal para inspeccionar, filtrar, agrupar y calcular indicadores. |
| `agrosavia.csv` | Resultados de análisis de suelo. | Conversión de medidas, fechas, ausencias y resúmenes mensuales. |
| `divipola.csv` | Catálogo de entidades territoriales. | Validación de códigos y unión con nombres y tipos de entidad. |

Los bloques Python se ejecutan en orden en un notebook del repositorio, por ejemplo dentro de `kit/Notebooks/` o `soluciones/`. Las variables creadas en una sección se utilizan en las siguientes.

El siguiente bloque localiza la raíz del repositorio aunque el notebook se abra desde `kit/Notebooks/`:

```python
actual = Path.cwd().resolve()
REPO = next(
    (ruta for ruta in [actual, *actual.parents]
     if (ruta / "kit/fuentes.json").is_file()
     and (ruta / "kit/00_datos.py").is_file()),
    None,
)
if REPO is None:
    raise FileNotFoundError("Jupyter debe iniciarse dentro de big-data-postgraduate")

KIT = REPO / "kit"
RAW = KIT / "data/raw"
SALIDAS = KIT / "salidas/manual_pandas"
SALIDAS.mkdir(parents=True, exist_ok=True)
```

> **📘 DataFrame y Series:** un DataFrame es una tabla con filas, columnas e índice. Una Series es una sola columna etiquetada. El índice sirve para localizar filas, pero no es una clave de negocio.

Si todavía falta alguno de los archivos, el siguiente comando se ejecuta en la **terminal, desde la raíz del repositorio y con el entorno del curso activo**. El script guarda las descargas en `kit/data/raw/` y comprueba su correspondencia con el manifiesto. Si los tres CSV ya están descargados, se continúa con el bloque Python.

```bash
python kit/00_datos.py --descargar divipola eva agrosavia
```

Se comprueba la presencia de los tres archivos antes de cargarlos. `eva_original` conserva la lectura inicial; `df` es una copia de trabajo a la que se añadirán columnas. La columna `fila_fuente` permite localizar cada registro en el CSV, contando la cabecera como la primera fila.

```python
archivos = ["eva.csv", "agrosavia.csv", "divipola.csv"]
faltantes = [nombre for nombre in archivos if not (RAW / nombre).is_file()]
if faltantes:
    raise FileNotFoundError(f"Faltan archivos en {RAW}: {faltantes}")

opciones = dict(sep=",", encoding="utf-8-sig", dtype=str, keep_default_na=False)
eva_original = pd.read_csv(RAW / "eva.csv", **opciones)
suelo = pd.read_csv(RAW / "agrosavia.csv", **opciones)
divipola = pd.read_csv(RAW / "divipola.csv", **opciones)

df = eva_original.copy()
df["fila_fuente"] = range(2, len(df) + 2)

print("EVA:", eva_original.shape)
print("AGROSAVIA:", suelo.shape)
print("DIVIPOLA:", divipola.shape)
```

> **✅ Comprobación:** en el corte del manifiesto, EVA contiene 166.732 filas y 18 columnas; AGROSAVIA, 92.738 filas y 32 columnas; DIVIPOLA, 1.122 filas y 7 columnas. `df` añade una columna de procedencia a EVA. Estos tamaños describen la entrada, no la cantidad de registros que superarán los controles de calidad.

## 2. Leer datos

```python
tabla = pd.read_csv(
    RAW / "eva.csv",
    sep=",",
    encoding="utf-8-sig",
    dtype=str,                 # conserva los códigos con ceros iniciales
    keep_default_na=False,     # los vacíos quedan como "" y no como NaN
    usecols=["Código Dane municipio", "Año", "Cultivo", "Área cosechada"],
    nrows=1000,                # vista inicial; no representa todo el archivo
)
```

| Parámetro | Para qué sirve |
|---|---|
| `sep` | Separador de columnas (`,`, `;`, `\t`, `\|`). |
| `encoding` | Codificación del archivo (`utf-8-sig` en los CSV del kit). |
| `dtype` | Tipo de cada columna; `str` evita conversiones automáticas. |
| `usecols` | Leer solo algunas columnas. |
| `nrows` | Leer solo las primeras filas para explorar. |
| `na_values` | Textos que deben tratarse como ausencia (`"ND"`, `"N/A"`). |
| `chunksize` | Leer por bloques (sección 10). |

> **⚠️ Códigos como texto:** si un código (`05`, `001`) se lee como número pierde los ceros iniciales y luego no cruza con otras tablas. Leer como texto y convertir después solo las columnas que realmente son numéricas es la opción más segura.

> **✅ Comprobación:** después de leer, revisar `tabla.shape` y `tabla.columns.tolist()`. Este ejemplo devuelve 1.000 filas y cuatro columnas. Si aparece una sola columna al leer un archivo completo, se debe revisar el separador; los tres CSV de esta guía utilizan coma.

## 3. Inspeccionar

| Operación | Uso principal |
|---|---|
| `shape`, `len`, `empty` | Cantidad de filas y columnas. |
| `columns`, `dtypes` | Nombres y tipos. |
| `head`, `tail`, `sample` | Ver algunos registros. |
| `info` | Tipos, no nulos y memoria. |
| `nunique` | Valores distintos. |
| `value_counts` | Frecuencias. |
| `describe` | Estadísticas descriptivas. |

```python
print("Dimensiones:", df.shape)
print("Columnas:", df.columns.tolist())
print(df.dtypes)
print(df.head(3))
print(df.sample(3, random_state=42))
df.info(memory_usage="deep")
print("Memoria MiB:", df.memory_usage(deep=True).sum() / 1024**2)
print(df["Cultivo"].value_counts(dropna=False).head(10))
print(df["Año"].value_counts(dropna=False).sort_index())
```

`info()` e `isna()` cuentan una cadena vacía como valor presente. Este perfil separa los nulos de pandas de los textos vacíos:

```python
texto = df.select_dtypes(include=["object", "string"])
perfil = pd.DataFrame({
    "tipo": df.dtypes.astype(str),
    "nulos": df.isna().sum(),
    "distintos": df.nunique(dropna=False),
})
perfil["vacios_texto"] = texto.apply(lambda col: col.str.strip().eq("").sum())
print(perfil)
```

## 4. Convertir tipos y tratar ausencias

Se crea una columna nueva y se conserva la original, para poder identificar lo que no se pudo convertir.

```python
df["cultivo_limpio"] = df["Cultivo"].str.strip()
df["anio"] = pd.to_numeric(df["Año"], errors="coerce").astype("Int64")
df["area_ha"] = pd.to_numeric(df["Área cosechada"], errors="coerce")
df["produccion_t"] = pd.to_numeric(df["Producción"], errors="coerce")
df["codigo_departamento"] = df["Código Dane departamento"].str.strip().str.zfill(2)

codigo = df["Código Dane municipio"].str.strip()
df["codigo_municipio"] = (
    codigo.where(codigo.str.fullmatch(r"[0-9]{1,5}"), pd.NA).str.zfill(5)
)
print(df[["area_ha", "produccion_t"]].describe())
```

`errors="coerce"` convierte lo que no se puede interpretar en ausencia (`NaN` o `NaT`). `Int64`, con mayúscula, admite enteros y ausencias a la vez. Para el código municipal, `where` conserva solo textos numéricos de una a cinco cifras antes de completar los ceros; un vacío no se transforma en `"00000"`. El campo original permite revisar lo que se descartó.

AGROSAVIA permite practicar la conversión de coma decimal y fechas con formato explícito:

```python
suelo["ph"] = pd.to_numeric(
    suelo["pH agua:suelo"].str.strip().str.replace(",", ".", regex=False),
    errors="coerce",
)
suelo["fecha_dt"] = pd.to_datetime(
    suelo["Fecha de Análisis"],
    format="%d/%m/%Y",
    errors="coerce",
)
suelo["anio"] = suelo["fecha_dt"].dt.year.astype("Int64")
```

La sustitución de coma por punto responde a la representación de esta fuente. El formato `%d/%m/%Y` evita confundir el día con el mes. Un marcador como `ND` queda ausente y no se convierte en cero.

> **✅ Contar los fallos de conversión:** distinguir lo que venía vacío de lo que tenía un texto no válido.

```python
vacia = suelo["pH agua:suelo"].str.strip().eq("")
no_numerica = ~vacia & suelo["ph"].isna()

print("Vacías:", int(vacia.sum()))
print("No numéricas:", int(no_numerica.sum()))
print(suelo.loc[no_numerica, ["Secuencial", "pH agua:suelo"]].head())
```

### Ausencias

| Operación | Uso |
|---|---|
| `isna()`, `notna()` | Detectar ausencias. |
| `isna().sum()` | Contar ausencias por columna. |
| `fillna(valor)` | Reemplazar ausencias. |
| `dropna(subset=[...])` | Eliminar filas con ausencias en ciertas columnas. |

```python
con_ph_numerico = suelo.dropna(subset=["ph"])
print("Filas sin pH numérico:", len(suelo) - len(con_ph_numerico))

cultivo_para_tabla = (
    df["cultivo_limpio"].replace("", pd.NA).fillna("SIN INFORMAR")
)
```

> **⚠️ Ausencia no significa cero:** `fillna(0)` solo es válido cuando la regla del dato lo justifica. Una categoría ausente puede mostrarse como `"SIN INFORMAR"`; una medida desconocida no debe convertirse en cero porque altera sumas y promedios. Antes de usar `dropna`, contar cuántas filas se excluyen.

## 5. Seleccionar y filtrar

`loc` selecciona por etiquetas o condiciones; `iloc`, por posición.

```python
columnas = [
    "fila_fuente", "codigo_departamento", "codigo_municipio",
    "anio", "Cultivo", "area_ha", "produccion_t",
]

una_columna = df["area_ha"]               # Series
varias = df[columnas]                     # DataFrame
primeras = df.iloc[:3, :4]                # posiciones 0 a 2
por_etiqueta = df.loc[0:2, columnas]      # etiquetas 0 a 2, inclusivas
```

Filtros con condiciones:

```python
solo_2024 = df.loc[df["anio"].eq(2024)].copy()

con_cosecha_2024 = df.loc[
    (df["anio"] == 2024) & (df["area_ha"] > 0),
    columnas,
].copy()

algunos_departamentos = df.loc[df["codigo_departamento"].isin(["15", "25"])]
areas_entre_10_y_100 = df.loc[df["area_ha"].between(10, 100)]
cultivos_de_papa = df.loc[
    df["Cultivo"].str.contains("PAPA", case=False, na=False, regex=False)
]
sin_area = df.loc[df["area_ha"].isna()]
```

Las condiciones se combinan con `&` (y), `|` (o) y `~` (no). Cada comparación con `==`, `>` o `<` va entre paréntesis.

| Método | Equivale a |
|---|---|
| `.eq(x)`, `.ne(x)` | `== x`, `!= x` |
| `.gt(x)`, `.ge(x)`, `.lt(x)`, `.le(x)` | `>`, `>=`, `<`, `<=` |
| `.between(a, b)` | `a <= valor <= b` |
| `.isin([...])` | Pertenece a la lista |
| `.str.contains("txt")` | El texto contiene |

### Filtrar con `query`

```python
anio_objetivo = 2024
consulta = df.query(
    "anio == @anio_objetivo and area_ha > 0",
    engine="python",
)
```

`query` filtra un DataFrame ya cargado con una expresión de texto; `@` permite usar variables de Python.

> **⚠️ `.copy()`:** al guardar un filtro en una variable que luego se va a modificar, añadir `.copy()` evita la advertencia `SettingWithCopyWarning` y resultados inesperados.

## 6. Crear y transformar columnas

```python
# Condición simple
df["estado_area"] = np.where(
    df["area_ha"].isna() | df["area_ha"].le(0),
    "REVISAR",
    "SIN ALERTA",
)

# Asignar solo a algunas filas
df["apto_rendimiento"] = False
mascara_apta = df["area_ha"].gt(0) & df["produccion_t"].ge(0) & df["anio"].notna()
df.loc[mascara_apta, "apto_rendimiento"] = True

# Reemplazar valores con un diccionario
df["ciclo_abreviado"] = df["Ciclo del cultivo"].map({
    "Transitorio": "T", "Permanente": "P",
})

# Rangos
df["rango_area"] = pd.cut(
    df["area_ha"],
    bins=[0, 10, 100, float("inf")],
    labels=["(0, 10] ha", "(10, 100] ha", "Más de 100 ha"],
)

# Renombrar y eliminar columnas
df = df.rename(columns={"cultivo_limpio": "cultivo"})
sin_columnas_auxiliares = df.drop(columns=["ciclo_abreviado"])
```

Los intervalos de área son una agrupación para practicar `cut`, no una clasificación oficial de predios. `map` devuelve ausencias para las categorías que no aparecen en el diccionario. `apto_rendimiento` identifica filas que cumplen el dominio numérico del cociente; no certifica todos los aspectos de calidad del registro.

Operaciones de texto más usadas (todas bajo `.str`):

| Método | Uso |
|---|---|
| `strip`, `lower`, `upper`, `title` | Limpiar espacios y normalizar mayúsculas. |
| `replace(a, b, regex=False)` | Reemplazar texto. |
| `zfill(n)` | Rellenar con ceros a la izquierda (`"5"` → `"05"`). |
| `len`, `slice(0, 2)` | Longitud y subcadena. |
| `contains`, `startswith`, `fullmatch` | Buscar patrones. |
| `split(",", expand=True)` | Dividir en varias columnas. |

> **📘 `apply`:** `df.apply(funcion, axis=1)` ejecuta una función fila por fila. Es flexible pero lento; cuando existe una operación vectorizada (`+`, `np.where`, `.str`, `.map`) esta es preferible.

## 7. Claves y duplicados

Una **clave repetida** y una **fila repetida** son situaciones distintas. Antes de eliminar hay que definir qué identifica a un registro.

```python
clave_grupo = ["codigo_municipio", "cultivo", "Estado físico del cultivo", "anio"]

# Varias observaciones pueden pertenecer al mismo grupo de análisis
grupos_repetidos = df.loc[
    df.duplicated(clave_grupo, keep=False)
].sort_values(clave_grupo)

# Repeticiones exactas en las 18 columnas originales de EVA
columnas_originales = eva_original.columns.tolist()
repetidas = df.duplicated(columnas_originales, keep="first")
sin_repetidas = df.drop_duplicates(columnas_originales)

assert len(df) == len(sin_repetidas) + int(repetidas.sum())
print("Filas que comparten grupo de análisis:", len(grupos_repetidos))
print("Repeticiones exactas:", int(repetidas.sum()))
print("¿Código único en DIVIPOLA?", divipola["Código Municipio"].is_unique)
```

`keep=False` marca todas las apariciones; `keep="first"` deja sin marcar la primera y marca las demás.

En EVA, municipio, cultivo, estado físico y año definen un grupo de análisis, pero no necesariamente una fila única: pueden existir periodos o desagregaciones diferentes. `sin_repetidas` permite estudiar el efecto de eliminar filas idénticas; `df` conserva todos los registros para decidir con evidencia.

> **⚠️ Deduplicar sobre un subconjunto de columnas:** dos filas pueden coincidir en las columnas seleccionadas y diferir en las demás. Eliminar duplicados sobre una selección parcial puede borrar registros legítimos.

## 8. Ordenar, agrupar y resumir

```python
ordenada = df.sort_values(
    ["anio", "codigo_departamento", "codigo_municipio"],
    ascending=[True, True, True],
)
areas_mayores = df.nlargest(10, "area_ha")
```

`groupby` forma grupos y calcula una medida para cada uno. Después de agrupar, cada fila deja de ser un registro y pasa a ser un grupo.

```python
conteo = (
    df.groupby(["anio", "codigo_departamento"], dropna=False)
    .size()
    .reset_index(name="registros")
)
assert conteo["registros"].sum() == len(df)

resumen = df.groupby("anio", dropna=False).agg(
    registros=("fila_fuente", "size"),
    con_area_numerica=("area_ha", "count"),
    area_mediana=("area_ha", "median"),
    cultivos=("cultivo", "nunique"),
    municipios=("codigo_municipio", "nunique"),
).reset_index()
print(resumen)
```

| Función | Qué calcula |
|---|---|
| `size` | Filas del grupo, incluidas las ausencias. |
| `count` | Valores no nulos de una columna. |
| `sum`, `mean`, `median`, `min`, `max` | Estadísticas. |
| `nunique` | Valores distintos. |
| `first`, `last` | Primer y último valor. |

> **✅ Conciliar:** la suma de los conteos por grupo debe coincidir con el total de filas. `dropna=False` conserva los grupos con clave ausente; sin él, esas filas desaparecen del resultado.

### Tablas dinámicas y cambio de forma

```python
matriz = df.pivot_table(
    index="codigo_departamento",
    columns="anio",
    values="fila_fuente",
    aggfunc="count",
    fill_value=0,
)

# De ancho a largo
largo = matriz.reset_index().melt(
    id_vars="codigo_departamento",
    var_name="anio",
    value_name="registros",
)
```

> **⚠️ Interpretación:** un cero con `fill_value=0` indica que no hay filas para esa combinación en los datos cargados; no es una medición de cero.

## 9. Combinar tablas

`concat` apila tablas con las mismas columnas. `merge` relaciona tablas por una clave, como un `JOIN` de SQL.

El siguiente ejemplo apila dos subconjuntos del mismo CSV. Así se practica `concat` sin necesitar archivos adicionales:

```python
eva_2023 = df.loc[df["anio"].eq(2023)].copy()
eva_2024 = df.loc[df["anio"].eq(2024)].copy()
dos_anios = pd.concat([eva_2023, eva_2024], ignore_index=True)
assert len(dos_anios) == len(eva_2023) + len(eva_2024)
```

DIVIPOLA añade los nombres oficiales y el tipo de entidad a cada registro EVA. Primero se comprueba que el código de la tabla territorial tiene cinco cifras y aparece una sola vez.

```python
TIPO_ENTIDAD = "Tipo: Municipio / Isla / Área no municipalizada"
divipola["codigo_municipio"] = (
    divipola["Código Municipio"].str.strip()
)
divipola["tipo_entidad"] = divipola[TIPO_ENTIDAD].str.strip()
dimension = divipola[[
    "codigo_municipio", "Nombre Departamento", "Nombre Municipio", "tipo_entidad"
]].copy()

assert dimension["codigo_municipio"].is_unique
assert dimension["codigo_municipio"].str.fullmatch(r"[0-9]{5}").all()

unida = df.merge(
    dimension,
    on="codigo_municipio",
    how="left",
    validate="many_to_one",
    indicator=True,
)
assert len(unida) == len(df)

sin_correspondencia = unida.loc[unida["_merge"].eq("left_only")]
print(sin_correspondencia[["fila_fuente", "codigo_municipio", "anio"]].head())
```

| `how` | Filas que conserva |
|---|---|
| `inner` | Solo las que tienen correspondencia en ambas tablas. |
| `left` | Todas las de la izquierda. |
| `right` | Todas las de la derecha. |
| `outer` | Todas las de ambas. |

| `validate` | Relación esperada |
|---|---|
| `one_to_one` | Una fila por clave en ambas tablas. |
| `one_to_many` | Una a la izquierda, varias a la derecha. |
| `many_to_one` | Varias a la izquierda, una a la derecha. |
| `many_to_many` | Repeticiones en ambos lados; requiere justificación. |

> **📘 Anti-join:** `indicator=True` añade la columna `_merge`. Filtrar `left_only` devuelve las filas de la izquierda que no encontraron correspondencia.

> **⚠️ Antes de unir:** las claves deben tener el mismo tipo y formato en ambas tablas (texto con texto, sin espacios, con la misma cantidad de ceros iniciales). Si las claves tienen nombres distintos, usar `left_on` y `right_on`.

### Caso E03: códigos EVA y clasificación DIVIPOLA

La clasificación de DIVIPOLA se conserva y se comprueba antes de utilizar la tabla como dimensión:

```python
tipos = divipola["tipo_entidad"].value_counts()
assert len(divipola) == 1122
assert divipola["codigo_municipio"].str.fullmatch(r"[0-9]{5}").all()
assert tipos.to_dict() == {
    "Municipio": 1103,
    "Área no municipalizada": 18,
    "Isla": 1,
}
print(tipos)
```

EVA se compara con DIVIPOLA mediante un anti-join. El año se conserva para localizar temporalmente cualquier código ausente, pero no se compara directamente con el corte único 2024 de DIVIPOLA.

```python
eva_codigo_anio = df[["codigo_municipio", "anio"]].drop_duplicates()
comparacion_eva = eva_codigo_anio.merge(
    dimension[["codigo_municipio"]],
    on="codigo_municipio",
    how="left",
    validate="many_to_one",
    indicator=True,
)
eva_sin_divipola = comparacion_eva.loc[
    comparacion_eva["_merge"].eq("left_only"),
    ["codigo_municipio", "anio"],
]
print(eva_sin_divipola)
assert eva_sin_divipola.empty
```

> **✅ Resultado esperado:** 1.103 municipios, 18 áreas no municipalizadas, una isla y cero combinaciones código–año de EVA sin correspondencia en el corte suministrado. DIVIPOLA declara corte 2024 y EVA contiene registros de 2019 a 2025. La coincidencia de códigos no demuestra que los límites territoriales hayan sido iguales durante todo ese periodo.

## 10. Guardar y procesar archivos grandes

Los archivos de salida se crean durante esta guía a partir de EVA. No se requiere haber ejecutado otros talleres ni disponer de productos Parquet previos.

```python
df.to_csv(SALIDAS / "eva_preparada.csv", index=False, encoding="utf-8-sig")
df.to_parquet(SALIDAS / "eva_preparada.parquet", index=False)

recuperado = pd.read_parquet(SALIDAS / "eva_preparada.parquet")
pd.testing.assert_frame_equal(df, recuperado)

columnas_parquet = pd.read_parquet(
    SALIDAS / "eva_preparada.parquet",
    columns=["codigo_municipio", "anio", "area_ha", "produccion_t"],
)
```

| Formato | Característica |
|---|---|
| CSV | Texto plano; no guarda los tipos. Al releer, declarar `dtype=str` para los códigos. |
| Parquet | Guarda los tipos, ocupa menos y permite leer solo algunas columnas. |
| Excel | Útil para compartir; lento con tablas grandes. |

`index=False` evita guardar el índice como una columna adicional.

### Lectura por bloques

`chunksize` procesa un CSV sin cargarlo completo. Cada bloque se reduce a un resultado parcial que se combina al final.

```python
parciales = []
filas = 0

for bloque in pd.read_csv(
    RAW / "eva.csv",
    sep=",",
    encoding="utf-8-sig",
    dtype=str,
    keep_default_na=False,
    usecols=["Año", "Código Dane departamento"],
    chunksize=10000,
):
    filas += len(bloque)
    parciales.append(
        bloque.groupby(["Año", "Código Dane departamento"], dropna=False).size()
    )

conteo_total = pd.concat(parciales).groupby(level=[0, 1]).sum()
assert int(conteo_total.sum()) == filas
assert filas == len(eva_original)

conteo_completo = eva_original.groupby(
    ["Año", "Código Dane departamento"], dropna=False
).size()
pd.testing.assert_series_equal(conteo_total.sort_index(), conteo_completo.sort_index())
```

> **⚠️ Cálculos parciales:** sumas y conteos se pueden combinar entre bloques. Una mediana global no se obtiene promediando medianas parciales, ni un promedio global promediando promedios. Guardar los bloques originales en una lista elimina el ahorro de memoria.

Otras formas de reducir memoria: leer solo las columnas necesarias con `usecols`, convertir columnas repetitivas con `astype("category")` y usar Parquet en lugar de CSV.

## 11. Recetas para problemas comunes

### Porcentaje sobre el total del grupo

`transform` devuelve un valor por cada fila original, no por grupo.

```python
por_departamento = (
    df.groupby(["anio", "codigo_departamento"], dropna=False)
    .size()
    .reset_index(name="registros")
)
por_departamento["total_anio"] = (
    por_departamento.groupby("anio", dropna=False)["registros"].transform("sum")
)
por_departamento["pct_anio"] = (
    por_departamento["registros"] / por_departamento["total_anio"] * 100
)
```

El porcentaje describe la distribución de los registros EVA dentro de cada año. No representa la proporción de área agrícola del departamento.

### Los N mayores de cada grupo

```python
por_cultivo = (
    df.groupby(["anio", "cultivo"], dropna=False)
    .size()
    .reset_index(name="registros")
)
top2 = (
    por_cultivo.sort_values(["registros", "cultivo"], ascending=[False, True])
    .groupby("anio", dropna=False, group_keys=False)
    .head(2)
)
```

### Razón agregada: dividir sumas, no promediar razones

```python
eva_apta = df.loc[df["apto_rendimiento"]].copy()
print("Filas incluidas:", len(eva_apta))
print("Filas fuera del dominio del cociente:", len(df) - len(eva_apta))

rendimiento = eva_apta.groupby(
    ["codigo_municipio", "cultivo", "Estado físico del cultivo", "anio"],
    as_index=False,
    dropna=False,
).agg(
    registros=("fila_fuente", "size"),
    produccion_t=("produccion_t", "sum"),
    area_ha=("area_ha", "sum"),
)
rendimiento["rendimiento_t_ha"] = (
    rendimiento["produccion_t"] / rendimiento["area_ha"]
)
assert rendimiento["registros"].sum() == len(eva_apta)
```

Un promedio simple de razones individuales da el mismo peso a registros de tamaños distintos.

### Valor anterior, diferencias y acumulados

```python
claves_serie = ["codigo_municipio", "cultivo", "Estado físico del cultivo"]
serie = rendimiento.sort_values(claves_serie + ["anio"]).copy()
grupo = serie.groupby(claves_serie, dropna=False)

serie["rendimiento_anterior"] = grupo["rendimiento_t_ha"].shift(1)
serie["anio_anterior"] = grupo["anio"].shift(1)
serie["variacion"] = serie["rendimiento_t_ha"] - serie["rendimiento_anterior"]
serie["produccion_acumulada"] = grupo["produccion_t"].cumsum()
serie["posicion"] = grupo["rendimiento_t_ha"].rank(
    ascending=False, method="dense"
)
serie["anios_consecutivos"] = serie["anio"].eq(serie["anio_anterior"] + 1)
serie["variacion_anual"] = serie["variacion"].where(serie["anios_consecutivos"])
```

> **⚠️** `shift` toma la fila anterior dentro del grupo, no necesariamente el periodo anterior. Si faltan periodos, comprobar que sean consecutivos antes de comparar.

### Resumir por mes

AGROSAVIA dispone de una fecha de análisis. Se cuentan las filas con fecha interpretable por mes y se contabilizan aparte las fechas ausentes o inválidas.

```python
suelo_con_fecha = suelo.dropna(subset=["fecha_dt"]).copy()
suelo_con_fecha["mes_analisis"] = suelo_con_fecha["fecha_dt"].dt.to_period("M")
mensual = (
    suelo_con_fecha.groupby("mes_analisis")
    .size()
    .rename("registros")
)
sin_fecha = int(suelo["fecha_dt"].isna().sum())
assert int(mensual.sum()) + sin_fecha == len(suelo)
print("Filas sin fecha interpretable:", sin_fecha)
```

### Marcar registros para revisión en lugar de eliminarlos

```python
suelo["en_revision"] = (
    suelo["ph"].isna()
    | ~suelo["ph"].between(0, 14)
    | suelo["fecha_dt"].isna()
    | suelo["Secuencial"].duplicated(keep=False)
)
print(suelo["en_revision"].value_counts())
```

La marca reúne controles de pH, fecha e identificador para localizar filas que requieren revisión. No equivale a una recomendación agronómica ni elimina observaciones del DataFrame.

### Comprobar que dos resultados son iguales

```python
a = df.query("anio == 2024 and area_ha > 0", engine="python")
b = df.loc[df["anio"].eq(2024) & df["area_ha"].gt(0)]
pd.testing.assert_frame_equal(a, b)
```

## 12. Errores frecuentes

| Síntoma | Revisión recomendada |
|---|---|
| `ModuleNotFoundError: pandas` | Revisar `sys.executable`; activar el entorno correcto o seleccionar el kernel. |
| `FileNotFoundError` | Mostrar `Path.cwd()` y comprobar la ruta del archivo. |
| El CSV aparece como una sola columna | Indicar el separador correcto con `sep`. |
| Caracteres extraños (`Ã±`, `�`) o `UnicodeDecodeError` | Probar `encoding="utf-8-sig"` o `"latin-1"`. |
| `KeyError` | Consultar `df.columns.tolist()`; respetar espacios, acentos y mayúsculas. |
| Los códigos perdieron los ceros iniciales | Leer con `dtype=str` y normalizar con `.str.zfill(n)`. |
| No aparecen faltantes, pero hay vacíos | Contar `.str.strip().eq("")` además de `isna()`. |
| Comparaciones numéricas incorrectas (`"10" < "9"`) | Convertir con `pd.to_numeric` y contar los fallos. |
| `The truth value of a Series is ambiguous` | Usar `&`, `\|`, `~` y paréntesis en lugar de `and`, `or`, `not`. |
| `SettingWithCopyWarning` | Asignar con `.loc[mascara, columna]` y usar `.copy()` al filtrar. |
| `MergeError` | Revisar claves repetidas y la cardinalidad declarada en `validate`. |
| El `merge` aumenta las filas | La clave no es única en la tabla de la derecha. |
| El `merge` no encuentra coincidencias | Igualar tipo y formato de las claves en ambas tablas. |
| Los totales del `groupby` no cuadran | Añadir `dropna=False` y revisar las claves ausentes. |
| Falta memoria | Leer solo las columnas necesarias y procesar por bloques. |

## 13. Resumen de funciones

| Tarea | Funciones |
|---|---|
| Leer | `read_csv`, `read_excel`, `read_parquet` |
| Inspeccionar | `shape`, `dtypes`, `head`, `info`, `describe`, `nunique`, `value_counts` |
| Convertir | `to_numeric`, `to_datetime`, `astype`, `.str`, `.dt` |
| Ausencias | `isna`, `notna`, `fillna`, `dropna` |
| Seleccionar | `loc`, `iloc`, `query`, `isin`, `between` |
| Transformar | `np.where`, `map`, `replace`, `cut`, `rename`, `drop`, `apply` |
| Duplicados | `duplicated`, `drop_duplicates`, `is_unique` |
| Resumir | `sort_values`, `nlargest`, `groupby`, `agg`, `transform`, `pivot_table`, `melt` |
| Combinar | `concat`, `merge` |
| Series ordenadas | `shift`, `cumsum`, `rank`, `dt.to_period` |
| Guardar | `to_csv`, `to_parquet`, `to_excel` |
| Comprobar | `assert`, `pd.testing.assert_frame_equal` |

## 14. Referencias

- [Introducción a pandas en 10 minutos](https://pandas.pydata.org/docs/user_guide/10min.html)
- [Lectura de archivos CSV](https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html)
- [Selección: `loc`, `iloc` y `query`](https://pandas.pydata.org/docs/user_guide/indexing.html)
- [Datos ausentes](https://pandas.pydata.org/docs/user_guide/missing_data.html)
- [Texto con `.str`](https://pandas.pydata.org/docs/user_guide/text.html)
- [Combinación de tablas](https://pandas.pydata.org/docs/user_guide/merging.html)
- [Agrupaciones](https://pandas.pydata.org/docs/user_guide/groupby.html)
- [Cambio de forma y tablas dinámicas](https://pandas.pydata.org/docs/user_guide/reshaping.html)
- [Escalamiento a conjuntos grandes](https://pandas.pydata.org/docs/user_guide/scale.html)
