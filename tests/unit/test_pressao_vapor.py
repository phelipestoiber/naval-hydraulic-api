import pytest
from app.core.cavitacao.pressao_vapor import calcular_pressao_vapor

def test_pressao_vapor_antoine_agua_20_e_80_graus():
    """T5.1 — Pressão de vapor Antoine (20°C e 80°C)"""
    # 20°C: Pv ~ 2338 Pa (+-2%)
    pv_20 = calcular_pressao_vapor(20.0)
    assert pv_20 == pytest.approx(2338.0, rel=0.02)

    # 80°C: Pv ~ 47370 Pa (+-2%)
    pv_80 = calcular_pressao_vapor(80.0)
    assert pv_80 == pytest.approx(47370.0, rel=0.02)

def test_pressao_vapor_temperatura_invalida():
    """Testa exceção ou limitação em temperatura negativa ou extrema."""
    with pytest.raises(ValueError):
        calcular_pressao_vapor(-50.0)
