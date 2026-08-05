import pytest
from app.core.perda_carga.singularidades import (
    calcular_perda_localizada_k,
    calcular_comprimento_equivalente,
    calcular_perda_singularidades
)

def test_comprimento_equivalente_exemplo_2_12_silva_telles():
    """T3.1 — Comprimento equivalente (Exemplo 2.12 — Silva Telles)"""
    D_m = 0.255
    f = 0.1270

    singularidades = [
        {"id": "valvula_gaveta", "quantidade": 2, "Le_sobre_D": 7},
        {"id": "valvula_retencao", "quantidade": 1, "Le_sobre_D": 82.35},
        {"id": "curva_90_rl", "quantidade": 4, "Le_sobre_D": 6.86},
        {"id": "entrada_borda_viva", "quantidade": 1, "Le_sobre_D": 39.2}
    ]

    hL_total, Le_total = calcular_perda_singularidades(
        singularidades=singularidades,
        D_m=D_m,
        v_ms=1.0878,
        f=f,
        metodo="le"
    )

    assert Le_total == pytest.approx(41.50, rel=0.05)
    L_total_linha = 174.0 + Le_total
    assert L_total_linha == pytest.approx(215.5, rel=0.05)

def test_perda_localizada_metodo_k():
    """Testa o cálculo de perda por coeficientes K: hL = K * v^2 / 2g."""
    K = 2.5
    v_ms = 2.0
    hL = calcular_perda_localizada_k(K, v_ms)
    assert hL == pytest.approx(0.50968, abs=1e-3)

def test_singularidades_metodo_k_e_comprimento_equivalente():
    """Testa função calcular_comprimento_equivalente e método 'k' em calcular_perda_singularidades."""
    le = calcular_comprimento_equivalente(0.6, 0.150, 0.02)
    assert le == pytest.approx(4.5)
    assert calcular_comprimento_equivalente(0.6, 0.150, 0.0) == 0.0

    singularidades = [
        {"id": "curva_90_rl", "quantidade": 2, "K": 0.6, "Le_sobre_D": 0},
        {"id": "valvula_gaveta", "quantidade": 1, "K": 0.15, "Le_sobre_D": 7.0}
    ]
    hL, Le = calcular_perda_singularidades(singularidades, D_m=0.150, v_ms=2.0, f=0.02, metodo="k")
    assert hL > 0
    assert Le > 0

    # Método K com D_m = 0
    hL_zero, _ = calcular_perda_singularidades(singularidades, D_m=0.0, v_ms=2.0, f=0.02, metodo="le")
    assert hL_zero == 0.0
