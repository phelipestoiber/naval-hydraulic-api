import pytest
from app.core.cavitacao.temperatura_critica import calcular_temperatura_critica_cavitacao

def test_temperatura_critica_cavitacao():
    """T5.4 — Temperatura crítica de cavitação"""
    p_atm_pa = 101325.0
    z_suc_m = -2.0
    hf_suc_m = 2.5
    npshr_m = 4.0
    rho_kgm3 = 1000.0
    g = 9.81

    T_crit = calcular_temperatura_critica_cavitacao(
        p_atm_pa=p_atm_pa,
        z_suc_m=z_suc_m,
        hf_suc_m=hf_suc_m,
        npshr_m=npshr_m,
        rho_kgm3=rho_kgm3,
        g=g
    )

    # T_crit ~ 57.8 °C (~55°C +- 5%)
    assert T_crit == pytest.approx(57.8, rel=0.06)

def test_temperatura_critica_nao_convergencia_fallback():
    """Testa fallback para 95.0 °C quando bisseção não converge (max_iter=0)."""
    T_fallback = calcular_temperatura_critica_cavitacao(
        p_atm_pa=101325.0,
        z_suc_m=-2.0,
        hf_suc_m=2.5,
        npshr_m=4.0,
        max_iter=0
    )
    assert T_fallback == 95.0
