import pytest
from app.core.fluidos.reynolds import (
    calcular_reynolds,
    determinar_regime_escoamento,
    calcular_alpha_cinetico
)

def test_reynolds_laminar_silva_telles():
    """T1.3 — Reynolds laminar (Exemplo 2.12 — Silva Telles)"""
    Q_m3s = 200.0 / 3600.0
    D_m = 0.255
    nu_m2s = 550.0 * 1e-6

    reynolds = calcular_reynolds(Q_m3s, D_m, nu_m2s)
    assert reynolds == pytest.approx(504.0, rel=0.02)

    regime = determinar_regime_escoamento(reynolds)
    assert regime == "laminar"

    alpha_cinetico = calcular_alpha_cinetico(reynolds)
    assert alpha_cinetico == pytest.approx(2.0, abs=1e-5)

def test_reynolds_transicao():
    """Testa regime de transição para 2300 <= Re <= 4000."""
    regime = determinar_regime_escoamento(3000.0)
    assert regime == "transicao"
    assert calcular_alpha_cinetico(3000.0) == 1.0

def test_reynolds_turbulento_silva_telles():
    """T1.4 — Reynolds turbulento (Exemplo 2.13 — Silva Telles)"""
    Q_m3s = 0.009
    D_m = 0.1022
    nu_m2s = 6.0 * 1e-6

    reynolds = calcular_reynolds(Q_m3s, D_m, nu_m2s)
    assert reynolds == pytest.approx(18679.0, rel=0.02)

    regime = determinar_regime_escoamento(reynolds)
    assert regime == "turbulento"

    alpha_cinetico = calcular_alpha_cinetico(reynolds)
    assert alpha_cinetico == pytest.approx(1.0, abs=1e-5)
