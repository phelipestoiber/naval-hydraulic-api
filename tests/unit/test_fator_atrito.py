import pytest
from app.core.perda_carga.fator_atrito import (
    calcular_fator_atrito_churchill,
    calcular_fator_atrito_colebrook,
    calcular_fator_atrito_swamee_jain,
    calcular_fator_atrito_haaland,
    calcular_fator_atrito_poiseuille,
    calcular_fator_atrito
)

def test_laminar_churchill_igual_poiseuille():
    """T2.1 — Laminar: Churchill = Poiseuille (Exemplo 2.12 — Silva Telles)"""
    Re = 504.0
    f_poiseuille = calcular_fator_atrito_poiseuille(Re)
    assert f_poiseuille == pytest.approx(64.0 / 504.0, abs=1e-5)

    f_churchill = calcular_fator_atrito_churchill(Re, epsilon_sobre_d=0.001)
    assert f_churchill == pytest.approx(f_poiseuille, rel=0.001)

def test_turbulento_quatro_equacoes_vs_colebrook():
    """T2.2 — Turbulento: quatro equações vs Colebrook (Exemplo 2.13 — Silva Telles)"""
    Re = 18679.0
    ed = 0.00043

    f_colebrook, iters = calcular_fator_atrito_colebrook(Re, ed)
    assert f_colebrook == pytest.approx(0.028, rel=0.05)

    f_churchill = calcular_fator_atrito_churchill(Re, ed)
    assert f_churchill == pytest.approx(f_colebrook, rel=0.01)

    f_swamee = calcular_fator_atrito_swamee_jain(Re, ed)
    assert f_swamee == pytest.approx(f_colebrook, rel=0.03)

    f_haaland, aviso_h = calcular_fator_atrito_haaland(Re, ed)
    assert f_haaland == pytest.approx(f_colebrook, rel=0.02)
    assert aviso_h is None

def test_consistencia_cruzada_5_pontos():
    """T2.3 — Consistência cruzada 5 pontos"""
    # 1. Laminar
    f_p1 = calcular_fator_atrito_churchill(1000.0, 0.0)
    assert f_p1 == pytest.approx(0.064, rel=0.001)

    # 2. Turbulento liso
    f_col2, _ = calcular_fator_atrito_colebrook(10000.0, 0.0001)
    f_chu2 = calcular_fator_atrito_churchill(10000.0, 0.0001)
    assert f_chu2 == pytest.approx(f_col2, rel=0.01)

    # 3. Turbulento
    f_col3, _ = calcular_fator_atrito_colebrook(100000.0, 0.001)
    f_chu3 = calcular_fator_atrito_churchill(100000.0, 0.001)
    f_swa3 = calcular_fator_atrito_swamee_jain(100000.0, 0.001)
    f_haa3, _ = calcular_fator_atrito_haaland(100000.0, 0.001)
    assert f_chu3 == pytest.approx(f_col3, rel=0.01)
    assert f_swa3 == pytest.approx(f_col3, rel=0.03)
    assert f_haa3 == pytest.approx(f_col3, rel=0.02)

    # 4. Rugoso
    f_col4, _ = calcular_fator_atrito_colebrook(1e6, 0.005)
    f_chu4 = calcular_fator_atrito_churchill(1e6, 0.005)
    assert f_chu4 == pytest.approx(f_col4, rel=0.01)

    # 5. Zona totalmente rugosa
    f_col5, _ = calcular_fator_atrito_colebrook(1e8, 0.05)
    f_chu5 = calcular_fator_atrito_churchill(1e8, 0.05)
    assert f_chu5 == pytest.approx(f_col5, rel=0.01)

def test_convergencia_colebrook():
    """T2.4 — Convergência Colebrook (<= 5 iterações)"""
    f_col, iters = calcular_fator_atrito_colebrook(50000.0, 0.001, f0=0.02, tol=1e-6)
    assert iters <= 5
    assert f_col > 0

    # Max iter atingido
    _, iters_max = calcular_fator_atrito_colebrook(50000.0, 0.001, f0=-0.02, tol=1e-20, max_iter=1)
    assert iters_max == 1

def test_haaland_faixa_e_fallback():
    """T2.5 — Haaland: faixa e fallback"""
    f_haa, aviso = calcular_fator_atrito_haaland(50000.0, 0.001)
    f_ref, _ = calcular_fator_atrito_colebrook(50000.0, 0.001)
    assert abs(f_haa - f_ref) / f_ref < 0.02
    assert aviso is None

    f_haa_lam, aviso_lam = calcular_fator_atrito_haaland(1000.0, 0.001)
    assert f_haa_lam == pytest.approx(0.064, abs=1e-5)
    assert aviso_lam is not None

    f_haa_ed, aviso_ed = calcular_fator_atrito_haaland(50000.0, 0.1)
    assert aviso_ed is not None

def test_calcular_fator_atrito_generico():
    """Testa a função genérica calcular_fator_atrito para todos os métodos e exceções."""
    ed = 0.001
    assert calcular_fator_atrito(1000.0, ed) == pytest.approx(0.064)
    assert calcular_fator_atrito(50000.0, ed, "churchill") > 0
    assert calcular_fator_atrito(50000.0, ed, "colebrook") > 0
    assert calcular_fator_atrito(50000.0, ed, "swamee_jain") > 0
    assert calcular_fator_atrito(50000.0, ed, "haaland") > 0
    assert calcular_fator_atrito(50000.0, ed, "poiseuille") == pytest.approx(64.0 / 50000.0)
    assert calcular_fator_atrito(50000.0, ed, "desconhecido") > 0

    with pytest.raises(ValueError):
        calcular_fator_atrito_poiseuille(-10.0)
    with pytest.raises(ValueError):
        calcular_fator_atrito_churchill(-10.0, ed)

    f_lam_col, _ = calcular_fator_atrito_colebrook(1000.0, ed)
    assert f_lam_col == pytest.approx(0.064)
    assert calcular_fator_atrito_swamee_jain(1000.0, ed) == pytest.approx(0.064)
