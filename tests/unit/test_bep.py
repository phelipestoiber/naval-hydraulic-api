import pytest
from app.core.bombas.bep import avaliar_faixa_bep

def test_bep_tres_status():
    """T4.5 — BEP: três status"""
    Q_bep = 100.0

    # 85 m3/h (85%) -> OK (70% a 120%)
    res_ok = avaliar_faixa_bep(85.0, Q_bep)
    assert res_ok["status_bep"] == "OK"
    assert res_ok["percentual_bep"] == pytest.approx(85.0)

    # 60 m3/h (60%) -> AVISO (50% a 130%)
    res_aviso = avaliar_faixa_bep(60.0, Q_bep)
    assert res_aviso["status_bep"] == "AVISO"

    # 40 m3/h (40%) -> ALERTA (< 50%)
    res_alerta_baixo = avaliar_faixa_bep(40.0, Q_bep)
    assert res_alerta_baixo["status_bep"] == "ALERTA"

    # 140 m3/h (140%) -> ALERTA (> 130%)
    res_alerta_alto = avaliar_faixa_bep(140.0, Q_bep)
    assert res_alerta_alto["status_bep"] == "ALERTA"

    # Q_bep <= 0 -> ALERTA
    res_invalido = avaliar_faixa_bep(85.0, 0.0)
    assert res_invalido["status_bep"] == "ALERTA"
