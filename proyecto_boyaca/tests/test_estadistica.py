"""Pruebas de la librería estadística con datos sintéticos de relación conocida."""
import numpy as np
import pandas as pd

from src import estadistica as est


def _datos(r_real: float, n: int = 120, semilla: int = 1):
    rng = np.random.default_rng(semilla)
    x = rng.normal(size=n)
    y = r_real * x + np.sqrt(1 - r_real ** 2) * rng.normal(size=n)
    return pd.DataFrame({"x": x, "y": y})


def test_detecta_asociacion_positiva():
    r = est.correlacion(_datos(0.6), "x", "y", "pearson", "greater")
    assert r["r"] > 0.4 and r["p"] < 0.05 and r["ic95_inf"] < r["r"] < r["ic95_sup"]


def test_no_inventa_asociacion():
    r = est.correlacion(_datos(0.0), "x", "y", "spearman", "greater")
    assert r["p"] > 0.05 or abs(r["r"]) < 0.2


def test_regresion_y_diagnosticos():
    res = est.regresion(_datos(0.5), "y ~ x")
    assert res["n"] == 120 and "x" in res["coeficientes"].index
    assert res["errores"] in ("HC3", "clasicos")


def test_holm_no_reduce_p():
    p = [0.01, 0.04, 0.03]
    assert all(a >= b for a, b in zip(est.ajustar_holm(p), p))


def test_datos_insuficientes():
    assert est.correlacion(pd.DataFrame({"x": [1, 2], "y": [1, 2]}), "x", "y")["nota"] == "datos insuficientes"
