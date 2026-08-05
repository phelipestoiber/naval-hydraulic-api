import pytest
from app.core.fluidos.viscosidade import (
    calcular_viscosidade_andrade,
    calcular_viscosidade_walther,
    calcular_viscosidade_linear,
    calcular_viscosidade
)

def test_andrade_agua_doce():
    """T1.5 — Andrade: água doce"""
    # Constantes ajustadas de Andrade para água doce em SI (Pa·s): ln(mu) = A + B/T
    A = -13.268
    B = 1864.1

    # T = 20°C -> 293.15 K -> mu ~ 1.002 mPa.s = 1.002e-3 Pa.s
    mu_20 = calcular_viscosidade_andrade(293.15, A, B)
    assert mu_20 == pytest.approx(1.002e-3, rel=0.02)

    # T = 60°C -> 333.15 K -> mu ~ 4.67e-4 Pa.s
    mu_60 = calcular_viscosidade_andrade(333.15, A, B)
    assert mu_60 == pytest.approx(4.67e-4, rel=0.02)

    # T = 90°C -> 363.15 K -> mu ~ 3.15e-4 Pa.s
    mu_90 = calcular_viscosidade_andrade(363.15, A, B)
    assert mu_90 == pytest.approx(3.15e-4, rel=0.07)

def test_walther_oleo_sae40():
    """T1.6 — Walther: óleo SAE 40 (ASTM D341)"""
    # Constantes ajustadas de Walther para SAE 40: log10(log10(nu + 0.7)) = A - B * log10(T)
    A = 8.110
    B = 3.125

    # T = 40°C = 313.15 K -> nu ~ 110 cSt (110 e-6 m2/s)
    nu_40_cst = calcular_viscosidade_walther(313.15, A, B)
    assert nu_40_cst == pytest.approx(110.0, rel=0.05)

    # T = 100°C = 373.15 K -> nu ~ 14.5 cSt
    nu_100_cst = calcular_viscosidade_walther(373.15, A, B)
    assert nu_100_cst == pytest.approx(14.5, rel=0.05)

def test_distincao_alpha_viscos_vs_alpha_cinetico():
    """T1.7 — Distinção alpha_viscos != alpha_cinetico"""
    # Modelo Linear: mu(T) = mu_ref * [1 + alpha_viscos * (T - T_ref)]
    mu_ref = 0.001
    T_ref_k = 293.15
    alpha_viscos = -0.02
    T_k = 313.15  # T - T_ref = +20 K

    mu_calc = calcular_viscosidade_linear(T_k, mu_ref, T_ref_k, alpha_viscos)
    # mu_calc = 0.001 * [1 + (-0.02)*20] = 0.001 * 0.6 = 0.0006 Pa.s
    assert mu_calc == pytest.approx(0.0006, rel=1e-4)

def test_calcular_viscosidade_lube_e_temperatura_extrema():
    """Testa função genérica para óleo lubrificante e trava de densidade."""
    res_lube = calcular_viscosidade("oleo_lubrificante", 293.15)
    assert res_lube["massa_especifica_kgm3"] == 890.0
    assert res_lube["viscosidade_dinamica_pas"] > 0

    # Temperatura extrema T_k = 600 K (temp_c = 326.85°C -> rho <= 0 -> fallback 1000.0)
    res_ext = calcular_viscosidade("agua_doce", 600.0)
    assert res_ext["massa_especifica_kgm3"] == 1000.0
