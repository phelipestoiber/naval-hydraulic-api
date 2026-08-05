import pytest
from app.core.motores.consumo_diesel import calcular_consumo_diesel

def test_consumo_diesel_lh():
    """T6.3 — Consumo de combustível diesel em L/h"""
    p_eixo_kw = 3.45
    sfc_g_kwh = 210.0
    rho_diesel_gl = 850.0

    res = calcular_consumo_diesel(p_eixo_kw=p_eixo_kw, sfc_g_kwh=sfc_g_kwh, rho_diesel_gl=rho_diesel_gl)

    assert res["consumo_gh"] == pytest.approx(724.5, rel=0.01)
    assert res["consumo_lh"] == pytest.approx(0.852, rel=0.02)

def test_consumo_diesel_densidade_zero():
    """Testa tratamento defensivo quando densidade do diesel é menor ou igual a zero."""
    res_zero = calcular_consumo_diesel(3.45, 210.0, 0.0)
    assert res_zero["consumo_lh"] == 0.0
