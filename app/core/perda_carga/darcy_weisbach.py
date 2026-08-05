def calcular_perda_carga_darcy_weisbach(f: float, L_m: float, D_m: float, v_ms: float, g: float = 9.81) -> float:
    """
    Calcula a perda de carga distribuída hf (em metros) pela Equação de Darcy-Weisbach:
    hf = f * (L / D) * (v^2 / (2 * g))
    """
    if D_m <= 0:
        raise ValueError("Diâmetro D_m deve ser estritamente positivo.")
    if L_m < 0:
        raise ValueError("Comprimento L_m não pode ser negativo.")

    return f * (L_m / D_m) * (v_ms**2 / (2.0 * g))
