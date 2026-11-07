import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def requiere(ruta: Path):
    """Salta la prueba si la tabla aún no existe (p. ej., antes de correr el pipeline)."""
    if not ruta.exists():
        pytest.skip(f"No existe {ruta.relative_to(ROOT)}: ejecute el pipeline primero")
    return ruta
