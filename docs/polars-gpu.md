# Polars con GPU NVIDIA

[Índice](../README.md) · [Entornos virtuales](entornos-virtuales.md) · [Guía de Polars](manual-polars.md)

Esta instalación es **opcional e independiente del entorno CPU del curso**. Completar primero la instalación básica. Tener una GPU NVIDIA o instalar `cudf-polars-cu12` no basta: se necesitan hardware compatible, controlador, CUDA Toolkit y paquetes Python compatibles entre sí. Los talleres funcionan en CPU.

## 1. Elegir una plataforma compatible

| Plataforma | Ruta para Polars GPU |
|---|---|
| Linux con NVIDIA | Controlador Linux y CUDA Toolkit compatibles, más el backend RAPIDS. |
| Windows con NVIDIA | WSL 2; controlador en Windows, Toolkit y paquetes Python dentro de Linux. |
| Windows nativo | No instalar el backend RAPIDS de esta guía en PowerShell; usar WSL 2. |
| macOS Intel o Apple Silicon | Polars en CPU; este backend no utiliza Metal ni la GPU de Apple. |
| GPU AMD o Intel | Este backend requiere NVIDIA; continuar en CPU. |

Antes de instalar, elegir una versión de RAPIDS y comprobar **su** [matriz de instalación](https://docs.rapids.ai/install/): modelo y capacidad de cómputo de la GPU, arquitectura del equipo, distribución Linux, Python, controlador y versión de CUDA admitidos. No confundir que una distribución ejecute Python con que esa combinación esté admitida por RAPIDS/CUDA.

El curso fija Python **3.12** y Polars **1.35.2**. Su archivo GPU usa la familia **CUDA 12** (`-cu12`), no CUDA 13. Debe existir una versión del backend compatible con esas restricciones. La versión menor del Toolkit y el controlador mínimo dependen de la versión RAPIDS elegida; no basta con que el nombre empiece por 12. Si la combinación no está soportada, mantener CPU o preparar una instalación GPU aparte sobre una distribución admitida. Esto también aplica a Ubuntu 26.04 de la guía base: comprobar su soporte para la versión GPU elegida antes de añadir repositorios.

## 2. Preparar NVIDIA en Linux nativo

Estos son prerrequisitos del **sistema operativo**, fuera del virtualenv:

1. Identificar la distribución con `cat /etc/os-release` y la arquitectura con `uname -m`.
2. Instalar un controlador NVIDIA compatible mediante el procedimiento oficial de la distribución/NVIDIA. Reiniciar si el instalador lo pide y comprobar que el controlador carga correctamente.
3. Instalar la versión **CUDA Toolkit 12.x** elegida en la matriz RAPIDS. Usar el [selector de descargas CUDA](https://developer.nvidia.com/cuda-toolkit-archive) y seguir las instrucciones de esa versión para la distribución y arquitectura exactas. No copiar repositorios de otra versión de Ubuntu.
4. Completar el PATH y los ajustes de bibliotecas indicados por el instalador; si ya hay varios Toolkits, comprobar cuál se selecciona.

No hay un único `apt install` válido para Ubuntu, Debian y Fedora. Los pasos concretos del controlador y del Toolkit deben corresponder al sistema detectado. [Guía oficial de instalación CUDA para Linux](https://docs.nvidia.com/cuda/cuda-installation-guide-linux/).

Comprobar en una terminal Linux:

```bash
nvidia-smi
nvcc --version
```

`nvidia-smi` debe mostrar la GPU y el controlador; `nvcc --version`, la versión del CUDA Toolkit seleccionado. Comparar esa versión con la combinación CUDA/RAPIDS elegida. Si `nvcc` no se encuentra, revisar la instalación del Toolkit y su PATH.

## 3. Preparar NVIDIA en Windows con WSL 2

1. Instalar en **Windows** el controlador NVIDIA con soporte CUDA/WSL para la GPU del equipo desde [NVIDIA](https://www.nvidia.com/Download/index.aspx). Reiniciar si se solicita.
2. En **PowerShell**, actualizar WSL y verificar que la distribución usa versión 2:

```powershell
wsl --update
wsl --list --verbose
```

3. Entrar en la distribución Linux elegida. Instalar allí el **CUDA Toolkit 12.x para WSL-Ubuntu, sin controlador Linux**, siguiendo la guía de la versión seleccionada. El Toolkit instalado en Windows no sustituye al Toolkit dentro de WSL.
4. En **Bash dentro de WSL**, comprobar:

```bash
nvidia-smi
nvcc --version
```

Si `nvidia-smi` responde «command not found», probar su ubicación habitual en WSL:

```bash
/usr/lib/wsl/lib/nvidia-smi
```

Si tampoco existe esa ruta o no se detecta la GPU, revisar el controlador de Windows y la configuración de WSL antes de continuar. Si `nvcc` no se encuentra, revisar la instalación del Toolkit y su PATH **dentro de WSL**.

**No instalar un controlador NVIDIA Linux dentro de WSL.** Windows proporciona el controlador a WSL. Para la ruta CUDA 12, elegir el paquete Toolkit de la versión seleccionada, con nombre del tipo `cuda-toolkit-12-x`; `x` representa la versión menor real. Evitar los metapaquetes `cuda`, `cuda-12-x` y `cuda-drivers` que intentan instalar el controlador Linux. [Instrucciones oficiales CUDA en WSL](https://docs.nvidia.com/cuda/wsl-user-guide/index.html).

## 4. Distinguir controlador, Toolkit y backend Python

| Comprobación | Qué demuestra | Qué no demuestra |
|---|---|---|
| `nvidia-smi` | La GPU es visible para el controlador. | No confirma que el Toolkit esté instalado. |
| `nvcc --version` | Versión del Toolkit seleccionado en PATH. | No prueba que Polars ejecute en GPU. |
| `python -m pip check` | Compatibilidad declarada de paquetes Python instalados. | No prueba el controlador, CUDA ni el hardware. |
| Consulta con `raise_on_fail=True` | El motor GPU ejecuta esa consulta o produce un error visible. | No garantiza soporte de todas las operaciones ni mayor velocidad. |

El campo **CUDA Version** de `nvidia-smi` es la versión máxima de CUDA que admite el controlador, no la versión del Toolkit instalado. Un controlador que anuncia CUDA 13 puede ejecutar una instalación compatible de CUDA 12; verificar la matriz y el Toolkit real. [Referencia de NVIDIA](https://docs.nvidia.com/deploy/nvidia-smi/index.html).

## 5. Crear el entorno GPU separado

Usar `.venv-gpu` únicamente en Linux o dentro de WSL 2, desde la **raíz del repositorio**, con `uv` ya instalado. Este entorno es la excepción opcional al `.venv` base: evita que la resolución de RAPIDS cambie las dependencias de las clases.

```bash
# Si había otro entorno activo, salir de él primero.
if [ -n "${VIRTUAL_ENV:-}" ]; then deactivate; fi
uv python install 3.12
if [ ! -e .venv-gpu ]; then
    uv venv --python 3.12 --seed .venv-gpu
fi
source .venv-gpu/bin/activate
python -c 'import sys, platform; assert sys.version_info[:2] == (3, 12); assert sys.prefix != sys.base_prefix; print(sys.executable, platform.machine())'
python -m pip --version
```

Si `.venv-gpu` ya existe, se reutiliza; no copiarlo desde otro equipo, distribución o arquitectura. Si pertenece a otra instalación, abrir una terminal nueva y conservarlo con otro nombre antes de crear uno nuevo. El intérprete debe estar dentro de `.venv-gpu/bin/`.

## 6. Resolver e instalar los paquetes GPU

Ejecutar esta etapa **solo después** de preparar y verificar NVIDIA y CUDA. El archivo `kit/requirements_gpu.txt` incluye Polars, el backend CUDA 12 y Jupyter. Mantiene las restricciones de versiones del curso; no instala controladores ni CUDA Toolkit.

Primero comprobar que el resolvedor encuentra una combinación y guardar el informe:

```bash
mkdir -p kit/salidas/entorno_gpu
python -m pip install --dry-run --report kit/salidas/entorno_gpu/resolucion.json -r kit/requirements_gpu.txt
```

Continuar únicamente si la resolución termina sin error y las versiones propuestas corresponden a la matriz elegida. El backend todavía no tiene una versión fijada y certificada para el curso: el resolvedor puede retroceder a una versión anterior. Una resolución satisfactoria no valida compatibilidad con la GPU real. Si RAPIDS indica un índice NVIDIA adicional para la versión elegida, usar exclusivamente la URL indicada por su selector oficial en ambos comandos, no un espejo desconocido.

```bash
python -m pip install --report kit/salidas/entorno_gpu/instalacion.json -r kit/requirements_gpu.txt
python -m pip check
python -c 'import polars, cudf_polars; print("Polars:", polars.__version__)'
python -m ipykernel install --sys-prefix --name bigdata-gpu --display-name "BigData · NVIDIA GPU · Python 3.12"
```

Si aparece `ResolutionImpossible` o no hay una rueda compatible, revisar Python, arquitectura, CUDA y la pareja Polars/cuDF-Polars. No retirar las restricciones, usar `--no-deps` ni actualizar el entorno base para forzar la instalación. Si no existe una combinación admitida, continuar con CPU hasta validar otra versión en este entorno opcional.

## 7. Verificar que Polars ejecuta en GPU

Con `.venv-gpu` activo, ejecutar en la terminal o en el kernel **BigData · NVIDIA GPU · Python 3.12**:

```python
import polars as pl
from polars.testing import assert_frame_equal

consulta = pl.LazyFrame({"valor": [1, 2, 3]}).select(pl.col("valor").sum())
cpu = consulta.collect(engine="in-memory")
gpu = consulta.collect(engine=pl.GPUEngine(raise_on_fail=True))
assert gpu.item() == 6
assert_frame_equal(cpu, gpu)
print("Consulta GPU correcta:", gpu)
```

Instalar el paquete no activa GPU en todos los scripts. Hay que solicitar el motor al ejecutar un **LazyFrame**. `raise_on_fail=True` impide que una operación no soportada vuelva silenciosamente a CPU, lo cual es esencial para verificar y medir el uso de GPU. [Uso y limitaciones del motor GPU de Polars](https://docs.pola.rs/user-guide/gpu-support/).

Las transferencias entre RAM y GPU tienen coste. Esta suma verifica funcionamiento, no velocidad; comparar consultas representativas y resultados equivalentes antes de afirmar una mejora respecto a Polars CPU o pandas.

## 8. Jupyter, registro y regreso a CPU

Iniciar Jupyter desde el entorno GPU, en la raíz del repositorio:

```bash
source .venv-gpu/bin/activate
python -m jupyter lab --no-browser --ip=127.0.0.1
```

Elegir el kernel GPU y comprobar `sys.executable` dentro del notebook. El registro con `--sys-prefix` pertenece a este entorno; el servidor Jupyter del entorno CPU no tiene por qué listar ese kernel.

Después de pasar la prueba GPU, registrar la combinación instalada:

```bash
python -m pip freeze > kit/salidas/entorno_gpu/requirements-validado.txt
python --version > kit/salidas/entorno_gpu/python.txt
nvidia-smi > kit/salidas/entorno_gpu/nvidia-smi.txt
nvcc --version > kit/salidas/entorno_gpu/cuda-toolkit.txt
```

Añadir al informe de la prueba la distribución, arquitectura y consulta ejecutada. El archivo congelado reproduce paquetes para un sistema compatible; no instala el controlador ni el Toolkit.

Para volver al trabajo ordinario, detener Jupyter, cerrar sus kernels y ejecutar:

```bash
deactivate
source .venv/bin/activate
python -m jupyter lab --no-browser --ip=127.0.0.1
```

Seleccionar el kernel CPU del curso. Activar otro entorno en una terminal no cambia un kernel que ya estaba abierto.

## 9. Problemas frecuentes y alcance de validación

### Aplicación a PQRS: P04

Después de verificar la suma GPU de esta guía, abrir
[04_Rendimiento_y_eventos_update1.ipynb](../kit/Notebooks/04_Rendimiento_y_eventos_update1.ipynb).
La práctica compara la misma agrupación PQRS en Polars CPU y GPU con muestras
o completos ya preparados. Revisar [P04](../talleres/P04.md) para rutas,
preparación y alcance de los tiempos. El notebook permite CPU sin NVIDIA,
no instala dependencias y exige `raise_on_fail=True` cuando se solicita GPU.
Registrar la combinación instalada con los comandos de la sección 8.

| Síntoma | Acción |
|---|---|
| `nvidia-smi` falla | Revisar controlador y visibilidad de la GPU; en WSL, empezar por Windows y WSL 2. |
| `nvcc` no existe | Instalar el Toolkit seleccionado o corregir el PATH. |
| Error al cargar bibliotecas CUDA | Revisar Toolkit y bibliotecas de la versión elegida; no confundirlos con el controlador. |
| No existe un paquete compatible | Revisar Python 3.12, plataforma y matriz RAPIDS. |
| Funciona en terminal, falla en notebook | Comprobar `sys.executable` y reiniciar con el kernel GPU. |
| La consulta falla con `raise_on_fail=True` | Revisar soporte de tipos y operaciones; ejecutar en CPU si no está soportada. |
| GPU más lenta que CPU | Medir tamaño, transferencias y consulta completa; no usar tablas mínimas como benchmark. |

La documentación y los comandos se revisaron con fuentes oficiales. **La instalación y la ejecución real GPU quedan pendientes de validación en un equipo NVIDIA compatible**; una revisión en macOS no las certifica.
