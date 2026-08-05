import math

def calcular_pressao_vapor(temp_c: float, A: float = 5.20389, B: float = 1733.926, C: float = 233.626) -> float:
    """
    Calcula a pressão de vapor Pv [Pa] de um fluido (padrão água) usando a Equação de Antoine:
    log10(Pv_bar) = A - (B / (T_C + C))
    Pv_pa = 10^(log10_pv_bar) * 1e5
    """
    if temp_c < -10.0 or temp_c > 370.0:
        raise ValueError(f"Temperatura {temp_c}°C fora da faixa de validade da Equação de Antoine.")

    log10_pv_bar = A - (B / (temp_c + C))
    pv_bar = 10.0**log10_pv_bar
    return pv_bar * 1e5
