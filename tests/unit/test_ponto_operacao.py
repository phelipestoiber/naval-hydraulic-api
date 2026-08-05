import pytest
from app.schemas.erro import ErroCalculo
from app.core.bombas.interpolacao import criar_curvas_bomba_interpoladas
from app.core.bombas.ponto_operacao import calcular_ponto_operacao

def test_boundary_check_shut_off_f3_a():
    """T4.2 — Boundary check F3-A: H_geo > H_shut_off (SEM_PONTO_OPERACAO_SHUT_OFF)"""
    Q_m3h = [0.0, 50.0, 100.0, 150.0, 180.0]
    H_m = [42.0, 40.0, 36.0, 28.0, 18.0]
    curvas = criar_curvas_bomba_interpoladas(Q_m3h, H_m)

    fn_h_sistema = lambda q_m3h: 50.0 + 0.0001 * (q_m3h**2)

    with pytest.raises(ErroCalculo) as exc_info:
        calcular_ponto_operacao(curvas, fn_h_sistema)

    assert exc_info.value.codigo == "SEM_PONTO_OPERACAO_SHUT_OFF"
    assert exc_info.value.dados_diagnostico["deficit_m"] == pytest.approx(8.0)

def test_boundary_check_fora_curva_f3_b():
    """T4.2 — Boundary check F3-B: Q_op > Q_max (SEM_PONTO_OPERACAO_FORA_CURVA)"""
    Q_m3h = [0.0, 50.0, 100.0, 150.0, 180.0]
    H_m = [42.0, 40.0, 36.0, 28.0, 18.0]
    curvas = criar_curvas_bomba_interpoladas(Q_m3h, H_m)

    fn_h_sistema = lambda q_m3h: 1.0 + 0.0001 * (q_m3h**2)

    with pytest.raises(ErroCalculo) as exc_info:
        calcular_ponto_operacao(curvas, fn_h_sistema)

    assert exc_info.value.codigo == "SEM_PONTO_OPERACAO_FORA_CURVA"

def test_ponto_operacao_normal_convergencia():
    """T4.2 — Ponto de operação normal (convergência garantida)"""
    Q_m3h = [0.0, 50.0, 100.0, 150.0, 180.0]
    H_m = [42.0, 38.0, 28.0, 12.0, 2.0]
    curvas = criar_curvas_bomba_interpoladas(Q_m3h, H_m)

    R = 5.05 / (118.5**2)
    fn_h_sistema = lambda q_m3h: 3.40 + R * (q_m3h**2)

    res = calcular_ponto_operacao(curvas, fn_h_sistema)

    assert res["convergiu"] is True
    assert res["Q_op_m3h"] > 0
    assert abs(res["residual_m"]) < 1e-4

def test_ponto_operacao_falha_convergencia():
    """Testa exceção SEM_PONTO_OPERACAO quando max_iter é 0."""
    Q_m3h = [0.0, 50.0, 100.0, 150.0, 180.0]
    H_m = [42.0, 38.0, 28.0, 12.0, 2.0]
    curvas = criar_curvas_bomba_interpoladas(Q_m3h, H_m)
    fn_h_sistema = lambda q_m3h: 3.40 + 0.0005 * (q_m3h**2)

    with pytest.raises(ErroCalculo) as exc_info:
        calcular_ponto_operacao(curvas, fn_h_sistema, tol=1e-15, max_iter=0)

    assert exc_info.value.codigo == "SEM_PONTO_OPERACAO"

def test_ponto_operacao_serie_e_paralelo():
    """T4.3 — Série e paralelo"""
    Q_m3h = [0.0, 50.0, 100.0, 150.0, 180.0]
    H_m = [42.0, 38.0, 28.0, 12.0, 2.0]

    H_serie = [2.0 * h for h in H_m]
    curvas_serie = criar_curvas_bomba_interpoladas(Q_m3h, H_serie)

    Q_paralelo = [2.0 * q for q in Q_m3h]
    curvas_paralelo = criar_curvas_bomba_interpoladas(Q_paralelo, H_m)

    fn_h_sistema = lambda q_m3h: 5.0 + 0.001 * (q_m3h**2)

    res_serie = calcular_ponto_operacao(curvas_serie, fn_h_sistema)
    res_paralelo = calcular_ponto_operacao(curvas_paralelo, fn_h_sistema)

    # T4.3: Q_op_paralelo > Q_op_serie
    assert res_paralelo["Q_op_m3h"] > res_serie["Q_op_m3h"]
