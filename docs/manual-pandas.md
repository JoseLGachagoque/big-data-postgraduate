# Guía práctica de pandas para los talleres de Big Data

Funciones más usadas de **pandas 2.2.3** para leer, inspeccionar, limpiar, transformar, combinar y guardar los datos tabulares utilizados en los talleres del repositorio.

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
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

print("Python:", sys.version.split()[0])
print("Intérprete:", sys.executable)
print("pandas:", pd.__version__)
print("Directorio actual:", Path.cwd())
```

Los ejemplos utilizan los archivos reales del curso. Las tres muestras PQRS ya están incluidas en `kit/data/pqrs_muestras/`. DIVIPOLA, EVA y AGROSAVIA se ubican en `kit/data/raw/`; se obtienen mediante la copia docente o con los comandos de descarga indicados en los talleres.

El siguiente bloque localiza la raíz del repositorio aunque el notebook se abra desde `kit/Notebooks/`:

```python
actual = Path.cwd().resolve()
REPO = next(
    (ruta for ruta in [actual, *actual.parents]
     if (ruta / "kit/pqrs_fuentes.json").is_file()),
    None,
)
if REPO is None:
    raise FileNotFoundError("Jupyter debe iniciarse dentro de big-data-postgraduate")

KIT = REPO / "kit"
MUESTRAS = KIT / "data/pqrs_muestras"
RAW = KIT / "data/raw"
SALIDAS = KIT / "salidas/manual_pandas"
SALIDAS.mkdir(parents=True, exist_ok=True)
```

> **📘 DataFrame y Series:** un DataFrame es una tabla con filas, columnas e índice. Una Series es una sola columna etiquetada. El índice sirve para localizar filas, pero no es una clave de negocio.

Para ejecutar las secciones territoriales y agroambientales se preparan las fuentes desde `kit/`. El ZIP municipal del MGN se obtiene por navegador según la guía de entorno.

```bash
python 00_datos.py --descargar divipola eva agrosavia
python 00_datos.py --verificar
```

La tabla principal de la guía combina las tres muestras PQRS. El manifiesto proporciona el separador y el esquema de cada corte.

```python
fuentes = json.loads((KIT / "pqrs_fuentes.json").read_text(encoding="utf-8"))
tablas = []

for fuente in fuentes:
    archivo = MUESTRAS / f"Muestra_1000_{fuente['periodo']}.csv"
    tabla = pd.read_csv(
        archivo,
        sep=fuente["separador"],
        encoding=fuente["codificacion"],
        dtype=str,
        keep_default_na=False,
    )
    assert tabla.columns.tolist() == fuente["columnas"]
    assert len(tabla) == fuente["filas_muestra"]
    tabla["corte_archivo"] = fuente["periodo"]
    tabla["fila_fuente"] = range(2, len(tabla) + 2)
    tablas.append(tabla)

df = pd.concat(tablas, ignore_index=True)
assert df.shape == (3000, 40)
```

> **✅ Comprobación:** `df` contiene 3.000 reportes, 38 columnas originales y dos columnas de procedencia. Las muestras son las primeras 1.000 filas de cada corte; no son una selección aleatoria representativa.

## 2. Leer datos

```python
fuente = fuentes[0]
tabla = pd.read_csv(
    MUESTRAS / f"Muestra_1000_{fuente['periodo']}.csv",
    sep=fuente["separador"],
    encoding=fuente["codificacion"],
    dtype=str,                 # conserva los códigos con ceros iniciales
    keep_default_na=False,     # los vacíos quedan como "" y no como NaN
    usecols=["OBJECTID", "periodo", "mes", "afec_cod_mpio", "afec_edad"],
)

divipola = pd.read_csv(
    RAW / "divipola.csv",
    dtype=str,
    keep_default_na=False,
    encoding="utf-8-sig",
)

producto_pqrs = KIT / "salidas/pqrs/pqrs.parquet"
if producto_pqrs.exists():
    parquet = pd.read_parquet(
        producto_pqrs,
        columns=["corte_archivo", "OBJECTID", "anio", "mes_num"],
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

> **✅ Comprobación:** después de leer, revisar `tabla.shape` y `tabla.columns.tolist()`. Si aparece una sola columna, el separador es incorrecto. Los cortes PQRS no comparten todos el mismo separador.

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
print(df["corte_archivo"].value_counts(dropna=False))
print(df["mes"].value_counts(dropna=False).sort_index())
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
df["ent_nombre_limpio"] = df["ent_nombre"].str.strip()
df["edad_num"] = pd.to_numeric(df["afec_edad"], errors="coerce")
df["anio"] = pd.to_numeric(df["periodo"], errors="coerce").astype("Int64")
df["mes_num"] = pd.to_numeric(df["mes"], errors="coerce").astype("Int64")
```

`errors="coerce"` convierte lo que no se puede interpretar en ausencia (`NaN` o `NaT`). `Int64`, con mayúscula, admite enteros y ausencias a la vez.

AGROSAVIA permite practicar la conversión de coma decimal y fechas con formato explícito:

```python
suelo = pd.read_csv(
    RAW / "agrosavia.csv",
    dtype=str,
    keep_default_na=False,
    encoding="utf-8-sig",
)
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
vacia = df["afec_edad"].str.strip().eq("")
no_numerica = ~vacia & df["edad_num"].isna()

print("Vacías:", int(vacia.sum()))
print("No numéricas:", int(no_numerica.sum()))
print(df.loc[no_numerica, ["corte_archivo", "OBJECTID", "afec_edad"]])
```

### Ausencias

| Operación | Uso |
|---|---|
| `isna()`, `notna()` | Detectar ausencias. |
| `isna().sum()` | Contar ausencias por columna. |
| `fillna(valor)` | Reemplazar ausencias. |
| `dropna(subset=[...])` | Eliminar filas con ausencias en ciertas columnas. |

```python
con_edad_numerica = df.dropna(subset=["edad_num"])
print("Filas sin edad numérica:", len(df) - len(con_edad_numerica))

entidad_para_tabla = (
    df["ent_nombre_limpio"].replace("", pd.NA).fillna("SIN INFORMAR")
)
```

> **⚠️ Ausencia no significa cero:** `fillna(0)` solo es válido cuando la regla del dato lo justifica. Una categoría ausente puede mostrarse como `"SIN INFORMAR"`; una medida desconocida no debe convertirse en cero porque altera sumas y promedios. Antes de usar `dropna`, contar cuántas filas se excluyen.

## 5. Seleccionar y filtrar

`loc` selecciona por etiquetas o condiciones; `iloc`, por posición.

```python
columnas = [
    "corte_archivo", "OBJECTID", "anio", "mes_num",
    "afec_cod_depto", "afec_cod_mpio", "edad_num",
]

una_columna = df["edad_num"]              # Series
varias = df[columnas]                     # DataFrame
primeras = df.iloc[:3, :4]                # posiciones 0 a 2
por_etiqueta = df.loc[0:2, columnas]      # etiquetas 0 a 2, inclusivas
```

Filtros con condiciones:

```python
solo_2024 = df.loc[df["anio"].eq(2024)].copy()

primer_semestre_2024 = df.loc[
    (df["anio"] == 2024) & (df["mes_num"].between(1, 6)),
    columnas,
].copy()

algunos_departamentos = df.loc[df["afec_cod_depto"].isin(["15", "25"])]
edad_adulta = df.loc[df["edad_num"].between(18, 64)]
entidades_salud = df.loc[
    df["ent_nombre"].str.contains("SALUD", case=False, na=False, regex=False)
]
sin_edad = df.loc[df["edad_num"].isna()]
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
    "anio == @anio_objetivo and 1 <= mes_num <= 6",
    engine="python",
)
```

`query` filtra un DataFrame ya cargado con una expresión de texto; `@` permite usar variables de Python.

> **⚠️ `.copy()`:** al guardar un filtro en una variable que luego se va a modificar, añadir `.copy()` evita la advertencia `SettingWithCopyWarning` y resultados inesperados.

## 6. Crear y transformar columnas

```python
df["clave_candidata"] = df["corte_archivo"] + "|" + df["OBJECTID"]

# Condición simple
df["estado_edad"] = np.where(
    df["edad_num"].isna() | df["edad_num"].lt(0),
    "REVISAR",
    "SIN ALERTA",
)

# Asignar solo a algunas filas
df["mes_valido"] = True
df.loc[~df["mes_num"].between(1, 12).fillna(False), "mes_valido"] = False

# Reemplazar valores con un diccionario
df["genero_abreviado"] = df["afec_genero"].map({"HOMBRE": "H", "MUJER": "M"})

# Rangos
df["grupo_edad"] = pd.cut(
    df["edad_num"],
    bins=[-1, 17, 64, float("inf")],
    labels=["MENOR", "ADULTO", "MAYOR"],
)

# Renombrar y eliminar columnas
df = df.rename(columns={"ent_nombre_limpio": "entidad_limpia"})
sin_columnas_auxiliares = df.drop(columns=["genero_abreviado"])
```

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
clave = ["corte_archivo", "OBJECTID"]

# Todas las filas cuya clave aparece más de una vez
conflictos = df.loc[df.duplicated(clave, keep=False)].sort_values(clave)

# Filas idénticas en las 38 columnas originales y dentro del mismo corte
columnas_originales = fuentes[0]["columnas"]
columnas_comparacion = ["corte_archivo", *columnas_originales]
repetidas = df.duplicated(columnas_comparacion, keep="first")
sin_repetidas = df.drop_duplicates(columnas_comparacion)

assert len(df) == len(sin_repetidas) + int(repetidas.sum())
print("Filas con clave repetida:", len(conflictos))
print("Repeticiones exactas:", int(repetidas.sum()))
print("¿Clave candidata única?", df["clave_candidata"].is_unique)
```

`keep=False` marca todas las apariciones; `keep="first"` deja sin marcar la primera y marca las demás.

> **⚠️ Deduplicar sobre un subconjunto de columnas:** dos filas pueden coincidir en las columnas seleccionadas y diferir en las demás. Eliminar duplicados sobre una selección parcial puede borrar registros legítimos.

## 8. Ordenar, agrupar y resumir

```python
ordenada = df.sort_values(
    ["corte_archivo", "mes_num", "afec_cod_depto"],
    ascending=[True, True, True],
)
edades_mayores = df.nlargest(10, "edad_num")
```

`groupby` forma grupos y calcula una medida para cada uno. Después de agrupar, cada fila deja de ser un registro y pasa a ser un grupo.

```python
conteo = (
    df.groupby(["corte_archivo", "afec_cod_depto"], dropna=False)
    .size()
    .reset_index(name="reportes")
)
assert conteo["reportes"].sum() == len(df)

resumen = df.groupby("corte_archivo", dropna=False).agg(
    reportes=("OBJECTID", "size"),
    con_edad_numerica=("edad_num", "count"),
    edad_mediana=("edad_num", "median"),
    entidades=("ent_nombre", "nunique"),
    municipios_afectado=("afec_cod_mpio", "nunique"),
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
    index="afec_cod_depto",
    columns="corte_archivo",
    values="OBJECTID",
    aggfunc="count",
    fill_value=0,
)

# De ancho a largo
largo = matriz.reset_index().melt(
    id_vars="afec_cod_depto",
    var_name="corte_archivo",
    value_name="reportes",
)
```

> **⚠️ Interpretación:** un cero con `fill_value=0` indica que no hay filas para esa combinación en los datos cargados; no es una medición de cero.

## 9. Combinar tablas

`concat` apila tablas con las mismas columnas. `merge` relaciona tablas por una clave, como un `JOIN` de SQL.

```python
TIPO_ENTIDAD = "Tipo: Municipio / Isla / Área no municipalizada"
divipola["codigo_municipio"] = (
    divipola["Código Municipio"].str.strip().str.zfill(5)
)
divipola["tipo_entidad"] = divipola[TIPO_ENTIDAD].str.strip()
dimension = divipola[[
    "codigo_municipio", "Nombre Departamento", "Nombre Municipio", "tipo_entidad"
]].copy()

assert dimension["codigo_municipio"].is_unique

unida = df.merge(
    dimension,
    left_on="afec_cod_mpio",
    right_on="codigo_municipio",
    how="left",
    validate="many_to_one",
    indicator=True,
)
assert len(unida) == len(df)

sin_correspondencia = unida.loc[unida["_merge"].eq("left_only")]
print(sin_correspondencia[["corte_archivo", "OBJECTID", "afec_cod_mpio"]])
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

### Caso E03: DIVIPOLA, EVA y MGN

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

En el shape municipal, `mpio_ccdgo` contiene tres caracteres y puede repetirse entre departamentos. `mpio_cdpmp` contiene el código municipal completo de cinco caracteres.

```python
import shapefile

lector = shapefile.Reader(str(RAW / "dane_municipios.zip"), encoding="utf-8")
campos = [campo[0] for campo in lector.fields[1:]]
atributos_shape = pd.DataFrame(
    [dict(zip(campos, registro)) for registro in lector.iterRecords()]
)
atributos_shape["codigo_municipio"] = (
    atributos_shape["mpio_cdpmp"].astype("string").str.strip().str.zfill(5)
)

print(atributos_shape[["mpio_ccdgo", "mpio_cdpmp"]].head())
print("Códigos cortos distintos:", atributos_shape["mpio_ccdgo"].nunique())
print("Códigos completos distintos:", atributos_shape["codigo_municipio"].nunique())
```

EVA se compara con DIVIPOLA mediante un anti-join. El año se conserva para localizar temporalmente cualquier código ausente, pero no se compara directamente con el corte único 2024 de DIVIPOLA.

```python
eva = pd.read_csv(
    RAW / "eva.csv", dtype=str, keep_default_na=False, encoding="utf-8-sig"
).rename(columns={
    "Código Dane municipio": "codigo_municipio",
    "Año": "anio",
})
eva["codigo_municipio"] = eva["codigo_municipio"].str.strip().str.zfill(5)
eva["anio"] = pd.to_numeric(eva["anio"], errors="coerce").astype("Int64")

eva_codigo_anio = eva[["codigo_municipio", "anio"]].drop_duplicates()
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

> **✅ Resultado esperado:** 1.103 municipios, 18 áreas no municipalizadas, una isla y cero combinaciones código–año de EVA sin correspondencia. DIVIPOLA registra corte 2024 y el MGN municipal corresponde a 2025; esta diferencia debe documentarse.

## 10. Guardar y procesar archivos grandes

```python
df.to_csv(SALIDAS / "pqrs_muestras.csv", index=False, encoding="utf-8-sig")
df.to_parquet(SALIDAS / "pqrs_muestras.parquet", index=False)

recuperado = pd.read_parquet(SALIDAS / "pqrs_muestras.parquet")
pd.testing.assert_frame_equal(df, recuperado)
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
    MUESTRAS / "Muestra_1000_2023_II.csv",
    sep=";",
    encoding="utf-8-sig",
    dtype=str,
    keep_default_na=False,
    usecols=["mes", "afec_cod_depto"],
    chunksize=250,
):
    filas += len(bloque)
    parciales.append(bloque.groupby(["mes", "afec_cod_depto"]).size())

conteo_total = pd.concat(parciales).groupby(level=[0, 1]).sum()
assert int(conteo_total.sum()) == filas
```

> **⚠️ Cálculos parciales:** sumas y conteos se pueden combinar entre bloques. Una mediana global no se obtiene promediando medianas parciales, ni un promedio global promediando promedios. Guardar los bloques originales en una lista elimina el ahorro de memoria.

Otras formas de reducir memoria: leer solo las columnas necesarias con `usecols`, convertir columnas repetitivas con `astype("category")` y usar Parquet en lugar de CSV.

## 11. Recetas para problemas comunes

### Porcentaje sobre el total del grupo

`transform` devuelve un valor por cada fila original, no por grupo.

```python
por_departamento = (
    df.groupby(["corte_archivo", "afec_cod_depto"], dropna=False)
    .size()
    .reset_index(name="reportes")
)
por_departamento["total_corte"] = (
    por_departamento.groupby("corte_archivo")["reportes"].transform("sum")
)
por_departamento["pct_corte"] = (
    por_departamento["reportes"] / por_departamento["total_corte"] * 100
)
```

### Los N mayores de cada grupo

```python
por_entidad = (
    df.groupby(["corte_archivo", "entidad_limpia"], dropna=False)
    .size()
    .reset_index(name="reportes")
)
top2 = (
    por_entidad.sort_values("reportes", ascending=False)
    .groupby("corte_archivo", group_keys=False)
    .head(2)
)
```

### Razón agregada: dividir sumas, no promediar razones

```python
eva["area_ha"] = pd.to_numeric(eva["Área cosechada"], errors="coerce")
eva["produccion_t"] = pd.to_numeric(eva["Producción"], errors="coerce")

eva_apta = eva.loc[
    eva["area_ha"].gt(0) & eva["produccion_t"].ge(0) & eva["anio"].notna()
].copy()

rendimiento = eva_apta.groupby(
    ["codigo_municipio", "Cultivo", "Estado físico del cultivo", "anio"],
    as_index=False,
    dropna=False,
).agg(
    produccion_t=("produccion_t", "sum"),
    area_ha=("area_ha", "sum"),
)
rendimiento["rendimiento_t_ha"] = (
    rendimiento["produccion_t"] / rendimiento["area_ha"]
)
```

Un promedio simple de razones individuales da el mismo peso a registros de tamaños distintos.

### Valor anterior, diferencias y acumulados

```python
claves_serie = ["codigo_municipio", "Cultivo", "Estado físico del cultivo"]
serie = rendimiento.sort_values(claves_serie + ["anio"]).copy()
grupo = serie.groupby(claves_serie)

serie["rendimiento_anterior"] = grupo["rendimiento_t_ha"].shift(1)
serie["anio_anterior"] = grupo["anio"].shift(1)
serie["variacion"] = serie["rendimiento_t_ha"] - serie["rendimiento_anterior"]
serie["produccion_acumulada"] = grupo["produccion_t"].cumsum()
serie["posicion"] = grupo["rendimiento_t_ha"].rank(
    ascending=False, method="dense"
)
serie["anios_consecutivos"] = serie["anio"].eq(serie["anio_anterior"] + 1)
```

> **⚠️** `shift` toma la fila anterior dentro del grupo, no necesariamente el periodo anterior. Si faltan periodos, comprobar que sean consecutivos antes de comparar.

### Resumir por mes

```python
df["fecha_mes"] = pd.to_datetime(
    {"year": df["anio"], "month": df["mes_num"], "day": 1},
    errors="coerce",
)
mensual = (
    df.dropna(subset=["fecha_mes"])
    .groupby(df["fecha_mes"].dt.to_period("M"))
    .size()
    .rename("reportes")
)
```

### Marcar registros para revisión en lugar de eliminarlos

```python
df["en_revision"] = (
    df["edad_num"].isna()
    | df["edad_num"].lt(0)
    | ~df["mes_num"].between(1, 12).fillna(False)
    | df["afec_cod_mpio"].str.strip().eq("")
)
print(df["en_revision"].value_counts())
```

### Comprobar que dos resultados son iguales

```python
a = df.query("anio == 2024 and 1 <= mes_num <= 6", engine="python")
b = df.loc[df["anio"].eq(2024) & df["mes_num"].between(1, 6)]
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
