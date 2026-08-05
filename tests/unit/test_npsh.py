import pytest
from app.core.cavitacao.npsh import calcular_npsha

def test_npsha_exemplo_2_13_silva_telles():
    """T5.2 — NPSHa (Exemplo 2.13 — Silva Telles)"""
    p_atm_pa = 101325.0
    temp_c = 20.0
    rho_kgm3 = 1000.0
    z_suc_m = 3.0
    hf_suc_m = 1.5
    g = 9.81

    npsha = calcular_npsha(
        p_atm_pa=p_atm_pa,
        temp_c=temp_c,
        z_suc_m=z_suc_m,
        hf_suc_m=hf_suc_m,
        rho_kgm3=rho_kgm3,
        g=g
    )

    # (101325 - 2338)/(1000*9.81) + 3.0 - 1.5 = 10.09 + 1.5 = 11.59 m (~11.50 m +- 2%)
    assert npsha == pytest.approx(11.50, rel=0.02)
