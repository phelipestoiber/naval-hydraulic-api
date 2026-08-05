import pytest
from app.core.bombas.velocidade_especifica import (
    calcular_velocidade_especifica,
    classificar_tipo_bomba
)

def test_velocidade_especifica_ns_golden_value():
    """T4.4 — Velocidade específica Ns (golden value)"""
    N_rpm = 1450.0
    Q_m3s = 0.0473
    Hb_m = 8.45

    Ns = calcular_velocidade_especifica(N_rpm, Q_m3s, Hb_m)
    assert Ns == pytest.approx(63.7, rel=0.05)

    tipo = classificar_tipo_bomba(Ns)
    assert tipo == "centrifuga_mista"

def test_classificacao_tipo_bomba_limites():
    """Testa os limites de classificação de tipo de bomba."""
    assert classificar_tipo_bomba(30.0) == "centrifuga_radial"
    assert classificar_tipo_bomba(63.7) == "centrifuga_mista"
    assert classificar_tipo_bomba(250.0) == "axial_helice"
    assert calcular_velocidade_especifica(0.0, 0.03, 8.0) == 0.0
