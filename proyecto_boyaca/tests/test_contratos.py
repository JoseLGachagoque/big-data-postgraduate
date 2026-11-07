"""Los mocks cumplen el contrato: así los consumidores pueden programar contra ellos."""
from src.contratos import CONTRATOS, cumplir
from src.mocks import tabla_mock


def test_mocks_cumplen_contrato():
    for tabla in CONTRATOS:
        cumplir(tabla_mock(tabla), tabla)
