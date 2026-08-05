from typing import Any

def avaliar_margem_cavitacao(
    npsha_m: float,
    npshr_m: float,
    fator_seguranca: float = 0.10,
    margem_min_m: float = 0.5
) -> dict[str, Any]:
    """
    Avalia a margem de cavitação (NPSHa - NPSHr) conforme a norma API 610 / HI:
    Margem Requerida = max(0.5 m, fator_seguranca * NPSHr)
    """
    margem = npsha_m - npshr_m
    margem_req = max(margem_min_m, fator_seguranca * npshr_m)
    cavitacao_detectada = npsha_m < (npshr_m + margem_req)

    if npsha_m < npshr_m or cavitacao_detectada:
        status = "ALERTA_CAVITACAO"
    else:
        status = "OK"

    return {
        "margem_m": margem,
        "margem_requerida_m": margem_req,
        "cavitacao_detectada": cavitacao_detectada,
        "status_cavitacao": status
    }
