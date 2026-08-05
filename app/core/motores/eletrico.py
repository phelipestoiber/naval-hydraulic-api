import math

def calcular_potencia_hidraulica(
    Q_m3s: float,
    H_m: float,
    rho_kgm3: float = 1000.0,
    g: float = 9.81
) -> float:
    """
    Calcula a potência hidráulica útil P_hid em kW:
    P_hid = (rho * g * Q * H) / 1000
    """
    return (rho_kgm3 * g * Q_m3s * H_m) / 1000.0

def calcular_potencia_eixo(p_hid_kw: float, eta_bomba: float) -> float:
    """
    Calcula a potência mecânica no eixo da bomba P_eixo em kW:
    P_eixo = P_hid / eta_bomba
    """
    if eta_bomba <= 0:
        return 0.0
    return p_hid_kw / eta_bomba

def calcular_potencia_eletrica(
    p_eixo_kw: float,
    eta_motor: float,
    eta_transmissao: float = 1.0
) -> float:
    """
    Calcula a potência elétrica total consumida da rede P_elet em kW:
    P_elet = P_eixo / (eta_motor * eta_transmissao)
    """
    denom = eta_motor * eta_transmissao
    if denom <= 0:
        return 0.0
    return p_eixo_kw / denom

def calcular_corrente_nominal_trifasica(
    p_elet_kw: float,
    V_volts: float,
    fp: float = 0.85
) -> float:
    """
    Calcula a corrente nominal trifásica I_nom [A]:
    I_nom = (P_elet_kw * 1000) / (sqrt(3) * V_volts * fp)
    """
    denom = math.sqrt(3.0) * V_volts * fp
    if denom <= 0:
        return 0.0
    return (p_elet_kw * 1000.0) / denom
