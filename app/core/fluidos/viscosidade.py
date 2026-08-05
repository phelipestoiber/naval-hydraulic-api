import math
from typing import Any

def calcular_viscosidade_andrade(T_k: float, A: float, B: float) -> float:
    """
    Calcula a viscosidade dinâmica mu em Pa·s usando o Modelo de Andrade:
    ln(mu) = A + B/T     [mu em Pa·s, T em Kelvin]
    """
    return math.exp(A + B / T_k)

def calcular_viscosidade_walther(T_k: float, A: float, B: float) -> float:
    """
    Calcula a viscosidade cinemática nu em cSt usando o Modelo de Walther (ASTM D341):
    log10(log10(nu + 0.7)) = A - B * log10(T)     [nu em cSt, T em Kelvin]
    Retorna nu em cSt.
    """
    val = A - B * math.log10(T_k)
    nu_cst = 10.0**(10.0**val) - 0.7
    return nu_cst

def calcular_viscosidade_linear(T_k: float, mu_ref: float, T_ref_k: float, alpha_viscos: float) -> float:
    """
    Calcula a viscosidade dinâmica mu em Pa·s usando o Modelo Linear:
    mu(T) = mu_ref * [1 + alpha_viscos * (T - T_ref)]
    """
    return mu_ref * (1.0 + alpha_viscos * (T_k - T_ref_k))

def calcular_viscosidade(nome_fluido: str, T_k: float) -> dict[str, float]:
    """
    Obtém as propriedades físicas do fluido (massa específica, viscosidade dinâmica e cinemática)
    para uma dada temperatura em Kelvin.
    """
    nome_norm = nome_fluido.lower()
    if "oleo_lubrificante" in nome_norm or "lubrificante" in nome_norm:
        rho = 890.0
        mu = calcular_viscosidade_andrade(T_k, -14.0, 3500.0)
    elif "oleo" in nome_norm or "diesel" in nome_norm:
        rho = 850.0
        mu = calcular_viscosidade_andrade(T_k, -11.0, 2000.0)
    else:
        # Padrão: Água doce
        temp_c = T_k - 273.15
        rho = 1000.0 - 0.015 * (temp_c - 4.0)**2
        if rho <= 0:
            rho = 1000.0
        mu = calcular_viscosidade_andrade(T_k, -11.64, 1680.0)

    nu = mu / rho if rho > 0 else 1e-6
    return {
        "massa_especifica_kgm3": rho,
        "viscosidade_dinamica_pas": mu,
        "viscosidade_cinematica_m2s": nu
    }
