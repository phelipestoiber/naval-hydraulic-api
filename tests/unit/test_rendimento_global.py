import pytest
from app.core.motores.rendimento_global import calcular_rendimento_global

def test_rendimento_global_cadeia():
    """T6.2 — Rendimento global eta_global"""
    eta_bomba = 0.79
    eta_motor = 0.92
    eta_transmissao = 0.98

    eta_global = calcular_rendimento_global(eta_bomba, eta_motor, eta_transmissao)
    # 0.79 * 0.92 * 0.98 = 0.71226 (71.2% +- 1%)
    assert eta_global == pytest.approx(0.71226, rel=0.01)
