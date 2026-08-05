import pytest
from app.core.perda_carga.darcy_weisbach import calcular_perda_carga_darcy_weisbach

def test_darcy_weisbach_perda_carga():
    """Testa o cálculo da perda de carga distribuída hf via Darcy-Weisbach."""
    f = 0.02
    L_m = 100.0
    D_m = 0.1
    v_ms = 2.0

    hf = calcular_perda_carga_darcy_weisbach(f, L_m, D_m, v_ms)
    assert hf == pytest.approx(4.07747, abs=1e-3)

def test_darcy_weisbach_excecoes():
    """Testa exceções para diâmetro <= 0 ou comprimento < 0."""
    with pytest.raises(ValueError):
        calcular_perda_carga_darcy_weisbach(0.02, 100.0, 0.0, 2.0)
    with pytest.raises(ValueError):
        calcular_perda_carga_darcy_weisbach(0.02, -10.0, 0.1, 2.0)
