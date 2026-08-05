import pytest
from app.core.motores.eletrico import (
    calcular_potencia_hidraulica,
    calcular_potencia_eixo,
    calcular_potencia_eletrica,
    calcular_corrente_nominal_trifasica
)

def test_motor_eletrico_potencias_e_corrente():
    """T6.1 — Motor elétrico: P_hid, P_eixo, P_elet e I_nom"""
    Q_m3s = 0.032917
    H_m = 8.45
    rho_kgm3 = 1000.0
    g = 9.81
    eta_bomba = 0.79
    eta_motor = 0.92
    eta_transmissao = 1.0
    V_volts = 380.0
    fp = 0.85

    p_hid = calcular_potencia_hidraulica(Q_m3s, H_m, rho_kgm3, g)
    assert p_hid == pytest.approx(2.73, rel=0.02)

    p_eixo = calcular_potencia_eixo(p_hid, eta_bomba)
    assert p_eixo == pytest.approx(3.454, rel=0.02)

    p_elet = calcular_potencia_eletrica(p_eixo, eta_motor, eta_transmissao)
    assert p_elet == pytest.approx(3.754, rel=0.02)

    i_nom = calcular_corrente_nominal_trifasica(p_elet, V_volts, fp)
    assert i_nom == pytest.approx(6.71, rel=0.02)

def test_motor_eletrico_casos_invalidos_rendimento_zero():
    """Testa tratamento defensivo quando rendimento ou tensão é zero."""
    assert calcular_potencia_eixo(2.73, 0.0) == 0.0
    assert calcular_potencia_eletrica(3.45, 0.0, 1.0) == 0.0
    assert calcular_corrente_nominal_trifasica(3.75, 0.0, 0.85) == 0.0
