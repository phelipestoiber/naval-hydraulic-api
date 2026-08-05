from typing import Any

def calcular_rotacao_inversor(N_nom: float, f_op: float, f_nom: float = 60.0) -> float:
    """
    Calcula a rotação ajustada pelo inversor de frequência (VFD):
    N(f_op) = N_nom * (f_op / f_nom)
    """
    if f_nom <= 0:
        return N_nom
    return N_nom * (f_op / f_nom)

def avaliar_status_inversor(f_op: float, f_nom: float = 60.0) -> dict[str, Any]:
    """
    Avalia a faixa de operação do inversor de frequência (VFD):
    - f_op < 30 Hz  -> ALERTA_FREQUENCIA_BAIXA (risco de superaquecimento)
    - 30 <= f_op <= 60 Hz -> OK
    - f_op > 60 Hz  -> ALERTA_SOBREFREQUENCIA
    """
    if f_op < 30.0:
        status = "ALERTA_FREQUENCIA_BAIXA"
        aviso = f"Frequência ({f_op} Hz) < 30 Hz — risco de superaquecimento por falta de ventilação no motor."
    elif f_op > 60.0:
        status = "ALERTA_SOBREFREQUENCIA"
        aviso = f"Frequência ({f_op} Hz) > 60 Hz — sobrecarga mecânica e térmica."
    else:
        status = "OK"
        aviso = None

    return {
        "frequencia_hz": f_op,
        "status_vfd": status,
        "aviso": aviso
    }
