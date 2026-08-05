import pytest
from app.core.motores.leis_semelhanca import aplicar_leis_semelhanca

def test_leis_semelhanca_variacao_rotacao():
    """T7.1 — Leis de semelhança por variação de rotação (N2/N1 = 0.8)"""
    N1 = 1750.0
    N2 = 1400.0
    Q1 = 100.0
    H1 = 40.0
    P1 = 15.0
    npshr1 = 4.0

    res = aplicar_leis_semelhanca(Q1=Q1, H1=H1, P1=P1, N1=N1, N2=N2, npshr1=npshr1)

    assert res["Q2"] == pytest.approx(80.0)
    assert res["H2"] == pytest.approx(25.6)
    assert res["P2"] == pytest.approx(7.68)
    assert res["npshr2"] == pytest.approx(2.56)

def test_leis_semelhanca_rebaixamento_impulsor():
    """T7.2 — Leis de semelhança por diâmetro de impulsor (D2/D1 = 0.9 e aviso < 0.80)"""
    D1 = 250.0
    D2 = 225.0
    Q1 = 100.0
    H1 = 40.0
    P1 = 15.0

    res = aplicar_leis_semelhanca(Q1=Q1, H1=H1, P1=P1, N1=1750.0, N2=1750.0, D1=D1, D2=D2)

    assert res["Q2"] == pytest.approx(90.0)
    assert res["H2"] == pytest.approx(32.4)
    assert res["aviso_rebaixamento"] is None

    res_excesso = aplicar_leis_semelhanca(Q1=Q1, H1=H1, P1=P1, N1=1750.0, N2=1750.0, D1=250.0, D2=180.0)
    assert res_excesso["aviso_rebaixamento"] is not None

def test_leis_semelhanca_parametros_invalidos():
    """Testa tratamento defensivo quando N1 ou D1 é menor ou igual a zero."""
    res_inv = aplicar_leis_semelhanca(100.0, 40.0, 15.0, N1=0.0, N2=1400.0)
    assert res_inv["Q2"] == 100.0
