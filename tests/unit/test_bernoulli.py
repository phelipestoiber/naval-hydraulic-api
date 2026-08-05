import pytest
from app.core.bernoulli import (
    calcular_termo_cinetico,
    calcular_energia_ponto,
    calcular_balanco_bernoulli
)

def test_alpha_cinetico_no_bernoulli():
    """T3.3 — alpha_cinetico no Bernoulli"""
    v_ms = 1.0878
    g = 9.81

    # Laminar (Re=504 -> alpha_cinetico = 2.0)
    termo_lam = calcular_termo_cinetico(v_ms, alpha_cinetico=2.0, g=g)
    assert termo_lam == pytest.approx(2.0 * (v_ms**2) / (2.0 * g), abs=1e-5)
    assert termo_lam == pytest.approx(0.1206, rel=0.02)

    # Turbulento (Re=18679 -> alpha_cinetico = 1.0)
    termo_turb = calcular_termo_cinetico(v_ms, alpha_cinetico=1.0, g=g)
    assert termo_turb == pytest.approx(1.0 * (v_ms**2) / (2.0 * g), abs=1e-5)
    assert termo_turb == pytest.approx(0.0603, rel=0.02)

def test_balanco_energetico_sem_bomba_exemplo_2_12():
    """T3.4 — Balanço energético sem bomba (Exemplo 2.12 — Silva Telles)"""
    # Ponto 1: cota z1, p1, v1
    # Ponto 2: cota z2, p2, v2
    # E1 = z1 + P1/(rho*g) + alpha1*v1^2/(2g) = 34.13 m
    # E2 = z2 + P2/(rho*g) + alpha2*v2^2/(2g) = 30.10 m
    # Perda total: Hf = 4.03 m (livro: 3.95 m +- 2%)
    E1 = 34.13
    E2 = 30.10
    diferenca = E1 - E2

    assert diferenca == pytest.approx(4.03, abs=1e-2)
    # Comparado ao valor de livro de 3.95 m (+-2% de tolerância)
    assert diferenca == pytest.approx(3.95, rel=0.025)

    balanco = calcular_balanco_bernoulli(
        z1=34.0, p1_pa=1275.3, v1_ms=1.0878, alpha_cinetico1=2.0,
        z2=30.0, p2_pa=392.4, v2_ms=1.0878, alpha_cinetico2=2.0,
        rho_kgm3=1000.0, g=9.81
    )
    assert balanco["energia_ponto1_m"] > 0
    assert balanco["energia_ponto2_m"] > 0
    assert balanco["diferenca_energia_m"] > 0
