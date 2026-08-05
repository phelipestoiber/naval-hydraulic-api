import pytest
from app.core.motores.inversor import calcular_rotacao_inversor, avaliar_status_inversor

def test_inversor_frequencia_operacao_ok():
    """T7.3 — Inversor VFD: f_op = 45 Hz (N = 1312.5 rpm, status OK)"""
    N_nom = 1750.0
    f_nom = 60.0
    f_op = 45.0

    N_adj = calcular_rotacao_inversor(N_nom, f_op, f_nom)
    assert N_adj == pytest.approx(1312.5)

    res_status = avaliar_status_inversor(f_op, f_nom)
    assert res_status["status_vfd"] == "OK"

def test_inversor_frequencia_alertas():
    """T7.4 — Inversor VFD: frequências baixas (<30Hz) e altas (>60Hz)"""
    res_baixa = avaliar_status_inversor(20.0, 60.0)
    assert res_baixa["status_vfd"] == "ALERTA_FREQUENCIA_BAIXA"

    res_alta = avaliar_status_inversor(65.0, 60.0)
    assert res_alta["status_vfd"] == "ALERTA_SOBREFREQUENCIA"

def test_inversor_frequencia_nominal_zero():
    """Testa tratamento defensivo quando frequência nominal é zero."""
    assert calcular_rotacao_inversor(1750.0, 45.0, 0.0) == 1750.0
