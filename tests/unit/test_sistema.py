import pytest
from app.core.perda_carga.sistema import calcular_resistencia_sistema, calcular_curva_sistema

def test_sistema_resistencia_e_curva():
    """Testa cálculo do coeficiente R e H_sistema(Q)."""
    Hf_total_m = 5.0
    Q_proj_m3s = 0.032917

    R = calcular_resistencia_sistema(Hf_total_m, Q_proj_m3s)
    assert R == pytest.approx(5.0 / (0.032917**2))

    H_sys = calcular_curva_sistema(3.40, R, Q_proj_m3s)
    assert H_sys == pytest.approx(3.40 + 5.0)

    with pytest.raises(ValueError):
        calcular_resistencia_sistema(5.0, 0.0)
