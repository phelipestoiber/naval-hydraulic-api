from typing import Any

def avaliar_faixa_bep(Q_op_m3h: float, Q_bep_m3h: float) -> dict[str, Any]:
    """
    Avalia a posição do ponto de operação em relação ao Ponto de Maior Eficiência (BEP — ISO 9906):
    - 70% <= Q/Q_BEP <= 120%  -> OK
    - 50% <= Q/Q_BEP <= 130%  -> AVISO
    - Q/Q_BEP < 50% ou > 130% -> ALERTA
    """
    if Q_bep_m3h <= 0:
        return {"percentual_bep": 0.0, "status_bep": "ALERTA"}

    pct = (Q_op_m3h / Q_bep_m3h) * 100.0

    if 70.0 <= pct <= 120.0:
        status = "OK"
    elif 50.0 <= pct <= 130.0:
        status = "AVISO"
    else:
        status = "ALERTA"

    return {
        "percentual_bep": pct,
        "status_bep": status
    }
