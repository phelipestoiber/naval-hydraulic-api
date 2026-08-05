from typing import Any

def calcular_perda_localizada_k(K: float, v_ms: float, g: float = 9.81) -> float:
    """
    Calcula a perda de carga localizada hL pelo Método dos Coeficientes K:
    hL = K * (v^2 / (2 * g))
    """
    return K * (v_ms**2 / (2.0 * g))

def calcular_comprimento_equivalente(K: float, D_m: float, f: float) -> float:
    """
    Calcula o comprimento equivalente Le para um coeficiente K:
    Le = K * D / f
    """
    if f <= 0:
        return 0.0
    return (K * D_m) / f

def calcular_perda_singularidades(
    singularidades: list[dict[str, Any]],
    D_m: float,
    v_ms: float,
    f: float = 0.02,
    metodo: str = "k",
    g: float = 9.81
) -> tuple[float, float]:
    """
    Calcula a perda de carga total e o comprimento equivalente total para uma lista de singularidades.
    Retorna (hL_total_m, Le_total_m).
    """
    Le_total_m = 0.0
    K_total = 0.0

    for item in singularidades:
        qtd = item.get("quantidade", 1)
        K_unit = item.get("K", 0.0)
        le_sd_unit = item.get("Le_sobre_D", 0.0)

        if le_sd_unit > 0:
            le_item = qtd * le_sd_unit * D_m
            Le_total_m += le_item
            if K_unit == 0.0 and f > 0:
                K_unit = le_sd_unit * f
        elif K_unit > 0:
            if f > 0:
                le_item = (K_unit * D_m) / f
                Le_total_m += qtd * le_item

        K_total += qtd * K_unit

    if metodo.lower() == "le":
        hL_total_m = f * (Le_total_m / D_m) * (v_ms**2 / (2.0 * g)) if D_m > 0 else 0.0
    else:
        hL_total_m = calcular_perda_localizada_k(K_total, v_ms, g=g)

    return (hL_total_m, Le_total_m)
