from app.core.cavitacao.pressao_vapor import calcular_pressao_vapor

def calcular_npsha(
    p_atm_pa: float,
    temp_c: float,
    z_suc_m: float,
    hf_suc_m: float,
    rho_kgm3: float = 1000.0,
    g: float = 9.81
) -> float:
    """
    Calcula o Net Positive Suction Head disponível (NPSHa) em metros:
    NPSHa = (P_atm - P_v) / (rho * g) + Z_suc - hf_suc
    """
    pv_pa = calcular_pressao_vapor(temp_c)
    termo_pressao = (p_atm_pa - pv_pa) / (rho_kgm3 * g) if rho_kgm3 > 0 and g > 0 else 0.0
    return termo_pressao + z_suc_m - hf_suc_m
