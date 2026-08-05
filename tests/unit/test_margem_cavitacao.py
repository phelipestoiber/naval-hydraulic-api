import pytest
from app.core.cavitacao.margem import avaliar_margem_cavitacao

def test_margem_cavitacao_ok_e_alerta():
    """T5.3 — Margem de cavitação e alerta"""
    # 1. Caso com risco de cavitação (NPSHa = 3.2 m, NPSHr = 4.8 m)
    res_cavitando = avaliar_margem_cavitacao(npsha_m=3.2, npshr_m=4.8)
    assert res_cavitando["margem_m"] == pytest.approx(-1.6)
    assert res_cavitando["status_cavitacao"] == "ALERTA_CAVITACAO"
    assert res_cavitando["cavitacao_detectada"] is True

    # 2. Caso seguro (NPSHa = 11.5 m, NPSHr = 3.2 m)
    res_seguro = avaliar_margem_cavitacao(npsha_m=11.5, npshr_m=3.2)
    assert res_seguro["margem_m"] == pytest.approx(8.3)
    assert res_seguro["status_cavitacao"] == "OK"
    assert res_seguro["cavitacao_detectada"] is False
