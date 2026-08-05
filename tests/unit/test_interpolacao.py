import pytest
from app.schemas.erro import ErroCalculo
from app.core.bombas.interpolacao import criar_curvas_bomba_interpoladas

def test_pchip_envelope_e_monotonicidade_f2():
    """T4.1 — PCHIP: envelope e monotonicidade (F2)"""
    Q_m3h = [0.0, 50.0, 100.0, 150.0, 180.0]
    H_m = [42.0, 40.0, 36.0, 28.0, 18.0]
    eta_pct = [0.0, 50.0, 79.0, 75.0, 60.0]
    npsh_m = [1.5, 2.0, 3.2, 4.8, 6.5]

    curvas = criar_curvas_bomba_interpoladas(Q_m3h, H_m, eta_pct, npsh_m)

    assert curvas.interp_hq(0.0) == pytest.approx(42.0)
    assert curvas.interp_hq(180.0) == pytest.approx(18.0)
    assert curvas.envelope_valido is True

    # Teste com curva plana (onde CubicSpline geraria overshoot)
    H_flat = [42.0, 41.8, 36.0, 28.0, 18.0]
    curvas_flat = criar_curvas_bomba_interpoladas(Q_m3h, H_flat)
    assert curvas_flat.envelope_valido is True
    # Q=25 deve ser entre 41.8 e 42.0 sem overshoot
    assert 41.8 <= curvas_flat.interp_hq(25.0) <= 42.0

def test_interpolacao_validacao_curva_invalida():
    """Testa validação de curva HxQ com < 3 pontos ou H não decrescente."""
    # < 3 pontos -> CURVA_HQ_INVALIDA
    with pytest.raises(ErroCalculo) as exc1:
        criar_curvas_bomba_interpoladas([0.0, 50.0], [42.0, 40.0])
    assert exc1.value.codigo == "CURVA_HQ_INVALIDA"

    # H crescente -> CURVA_HQ_H_INVALIDO
    with pytest.raises(ErroCalculo) as exc2:
        criar_curvas_bomba_interpoladas([0.0, 50.0, 100.0], [42.0, 45.0, 36.0])
    assert exc2.value.codigo == "CURVA_HQ_H_INVALIDO"
