import math

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

    Atenção: 'alpha_viscos' é o coeficiente térmico de viscosidade — não confundir com
    'alpha_cinetico' (coeficiente de Coriolis da equação de Bernoulli).
    """
    return mu_ref * (1.0 + alpha_viscos * (T_k - T_ref_k))
