from typing import Any

def calcular_consumo_diesel(
    p_eixo_kw: float,
    sfc_g_kwh: float = 210.0,
    rho_diesel_gl: float = 850.0
) -> dict[str, Any]:
    """
    Calcula o consumo de combustível de motor diesel acionador:
    consumo_gh = P_eixo_kw * SFC
    consumo_lh = consumo_gh / rho_diesel [g/L]
    """
    if rho_diesel_gl <= 0:
        return {"consumo_gh": 0.0, "consumo_lh": 0.0}

    consumo_gh = p_eixo_kw * sfc_g_kwh
    consumo_lh = consumo_gh / rho_diesel_gl

    return {
        "consumo_gh": consumo_gh,
        "consumo_lh": consumo_lh
    }
