import math
from typing import Any

MOTORES_ABNT_CV = [
    0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 6.0, 7.5, 10.0, 12.5, 15.0, 20.0, 25.0, 30.0, 40.0, 50.0, 60.0, 75.0, 100.0
]

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

def selecionar_motor_normalizado(p_eixo_kw: float) -> dict[str, Any]:
    """
    Seleciona a carcaça/potência nominal normalizada comercial em CV superior a P_eixo.
    """
    p_eixo_cv = p_eixo_kw / 0.735499
    pot_cv_sel = MOTORES_ABNT_CV[-1]
    for cv in MOTORES_ABNT_CV:
        if cv >= p_eixo_cv:
            pot_cv_sel = cv
            break

    return {
        "potencia_eixo_kw": p_eixo_kw,
        "potencia_eixo_cv": p_eixo_cv,
        "potencia_cv": pot_cv_sel,
        "potencia_kw": pot_cv_sel * 0.735499
    }
