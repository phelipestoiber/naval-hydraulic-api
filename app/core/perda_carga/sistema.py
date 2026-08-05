def calcular_resistencia_sistema(Hf_total_m: float, Q_projeto_m3s: float) -> float:
    """
    Calcula o coeficiente de resistência do sistema R [s²/m⁵]:
    R = Hf_total / Q_projeto^2
    """
    if Q_projeto_m3s <= 0:
        raise ValueError("Vazão de projeto deve ser estritamente positiva.")
    return Hf_total_m / (Q_projeto_m3s**2)

def calcular_curva_sistema(H_geo_m: float, R: float, Q_m3s: float) -> float:
    """
    Calcula a altura manométrica requerida pelo sistema H_sistema(Q):
    H_sistema = H_geo + R * Q^2
    """
    return H_geo_m + R * (Q_m3s**2)
