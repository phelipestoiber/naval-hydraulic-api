from typing import Any

def calcular_termo_cinetico(v_ms: float, alpha_cinetico: float = 1.0, g: float = 9.81) -> float:
    """
    Calcula o termo de energia cinética de Coriolis:
    termo = alpha_cinetico * v^2 / (2 * g)

    Atenção: A variável deve se chamar 'alpha_cinetico' — nunca 'alpha' sozinho.
    """
    return alpha_cinetico * (v_ms**2) / (2.0 * g)

def calcular_energia_ponto(
    z_m: float,
    p_pa: float,
    v_ms: float,
    alpha_cinetico: float = 1.0,
    rho_kgm3: float = 1000.0,
    g: float = 9.81
) -> float:
    """
    Calcula a energia total (carga hidráulica) em um ponto do escoamento em metros:
    E = Z + P/(rho*g) + alpha_cinetico * v^2 / (2*g)
    """
    termo_pressao = p_pa / (rho_kgm3 * g) if rho_kgm3 > 0 and g > 0 else 0.0
    termo_cinetico = calcular_termo_cinetico(v_ms, alpha_cinetico=alpha_cinetico, g=g)
    return z_m + termo_pressao + termo_cinetico

def calcular_balanco_bernoulli(
    z1: float, p1_pa: float, v1_ms: float, alpha_cinetico1: float,
    z2: float, p2_pa: float, v2_ms: float, alpha_cinetico2: float,
    rho_kgm3: float = 1000.0, g: float = 9.81, Hb_m: float = 0.0
) -> dict[str, Any]:
    """
    Calcula o balanço energético da Equação de Bernoulli Generalizada entre o ponto 1 e ponto 2:
    Z1 + P1/(rho*g) + alpha_cinetico1*v1^2/(2g) = Z2 + P2/(rho*g) + alpha_cinetico2*v2^2/(2g) + Hf_total - Hb
    """
    E1 = calcular_energia_ponto(z1, p1_pa, v1_ms, alpha_cinetico=alpha_cinetico1, rho_kgm3=rho_kgm3, g=g)
    E2 = calcular_energia_ponto(z2, p2_pa, v2_ms, alpha_cinetico=alpha_cinetico2, rho_kgm3=rho_kgm3, g=g)

    diferenca = (E1 + Hb_m) - E2

    return {
        "energia_ponto1_m": E1,
        "energia_ponto2_m": E2,
        "diferenca_energia_m": diferenca,
        "hf_total_m": diferenca
    }
