import math
from typing import Any
from app.core.perda_carga.darcy_weisbach import calcular_perda_carga_darcy_weisbach

def validar_hw(tipo_fluido: str, temp_c: float, Re: float, D_m: float) -> tuple[bool, str | None]:
    """
    Valida os 4 critérios de aplicabilidade da Equação de Hazen-Williams:
    1. Tipo de fluido: Apenas água (doce, salgada, potável, lastro, incêndio)
    2. Temperatura: 5°C <= T <= 30°C
    3. Regime: Re > 4.000 (turbulento)
    4. Diâmetro: 12 mm <= D <= 3600 mm (0.012 m <= D <= 3.6 m)

    Retorna (valido, codigo_rejeicao).
    """
    fluidos_agua_validos = ("agua_doce", "agua_salgada", "agua_potavel", "agua_lastro", "agua_incendio", "agua")
    if tipo_fluido.lower() not in fluidos_agua_validos:
        return (False, "HW_FLUIDO_INVALIDO")

    if temp_c < 5.0 or temp_c > 30.0:
        return (False, "HW_TEMPERATURA_INVALIDA")

    if Re <= 4000.0:
        return (False, "HW_REGIME_INVALIDO")

    if D_m < 0.012 or D_m > 3.6:
        return (False, "HW_DIAMETRO_INVALIDO")

    return (True, None)

def calcular_perda_carga_hazen_williams(
    Q_m3s: float,
    L_m: float,
    D_m: float,
    C: float,
    tipo_fluido: str = "agua_doce",
    temp_c: float = 20.0,
    Re: float = 50000.0,
    f_darcy: float = 0.02,
    g: float = 9.81
) -> dict[str, Any]:
    """
    Calcula a perda de carga distribuída hf via Hazen-Williams.
    Executa validar_hw() internamente e faz fallback automático para Darcy-Weisbach se rejeitada.

    Retorna dicionário:
    {
      "hf_m": float,
      "metodo_usado": "hazen_williams" | "darcy_weisbach",
      "aviso": str | None,
      "codigo_rejeicao": str | None
    }
    """
    valido, codigo_rejeicao = validar_hw(tipo_fluido, temp_c, Re, D_m)

    if not valido:
        v_ms = (4.0 * Q_m3s) / (math.pi * D_m**2) if D_m > 0 else 0.0
        hf_dw = calcular_perda_carga_darcy_weisbach(f_darcy, L_m, D_m, v_ms, g=g)
        return {
            "hf_m": hf_dw,
            "metodo_usado": "darcy_weisbach",
            "aviso": f"Hazen-Williams rejeitada ({codigo_rejeicao}). Fallback automático para Darcy-Weisbach.",
            "codigo_rejeicao": codigo_rejeicao
        }

    # Equação de Hazen-Williams: hf = 10.646 * Q^1.852 * L / (C^1.852 * D^4.87)
    hf = 10.646 * (Q_m3s**1.852) * L_m / ((C**1.852) * (D_m**4.87))
    return {
        "hf_m": hf,
        "metodo_usado": "hazen_williams",
        "aviso": None,
        "codigo_rejeicao": None
    }
