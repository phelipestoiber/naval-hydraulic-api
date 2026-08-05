import math

def calcular_velocidade_especifica(N_rpm: float, Q_m3s: float, Hb_m: float) -> float:
    """
    Calcula a velocidade específica Ns (em unidades SI):
    Ns = N * Q^0.5 / Hb^0.75
    [N em rpm; Q em m³/s; Hb em m]
    """
    if Hb_m <= 0 or Q_m3s <= 0 or N_rpm <= 0:
        return 0.0
    return N_rpm * (Q_m3s**0.5) / (Hb_m**0.75)

def classificar_tipo_bomba(Ns: float) -> str:
    """
    Classifica o tipo de bomba com base na velocidade específica Ns (SI):
    - Ns < 50          -> centrifuga_radial
    - 50 <= Ns <= 200 -> centrifuga_mista
    - Ns > 200        -> axial_helice
    """
    if Ns < 50.0:
        return "centrifuga_radial"
    elif Ns <= 200.0:
        return "centrifuga_mista"
    else:
        return "axial_helice"
