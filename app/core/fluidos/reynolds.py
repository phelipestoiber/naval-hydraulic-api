import math

def calcular_reynolds(Q_m3s: float, D_m: float, nu_m2s: float) -> float:
    """
    Calcula o Número de Reynolds:
    Re = v * D / nu = (4 * Q) / (pi * D * nu)
    """
    v = (4.0 * Q_m3s) / (math.pi * D_m**2)
    return (v * D_m) / nu_m2s

def determinar_regime_escoamento(Re: float) -> str:
    """
    Determina o regime de escoamento com base no número de Reynolds:
    - Re < 2.300          -> laminar
    - 2.300 <= Re <= 4.000 -> transicao
    - Re > 4.000          -> turbulento
    """
    if Re < 2300.0:
        return "laminar"
    elif Re <= 4000.0:
        return "transicao"
    else:
        return "turbulento"

def calcular_alpha_cinetico(Re: float) -> float:
    """
    Calcula o coeficiente de energia cinética (alpha_cinetico) de Coriolis:
    - Laminar (Re < 2.300): alpha_cinetico = 2.0
    - Turbulento (Re >= 2.300): alpha_cinetico = 1.0
    """
    if Re < 2300.0:
        return 2.0
    else:
        return 1.0
