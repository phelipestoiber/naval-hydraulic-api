from typing import Any

def aplicar_leis_semelhanca(
    Q1: float,
    H1: float,
    P1: float,
    N1: float,
    N2: float,
    D1: float = 1.0,
    D2: float = 1.0,
    npshr1: float | None = None
) -> dict[str, Any]:
    """
    Aplica as Leis de Afinidade (Semelhança) para bombas centrífugas:
    - Q2 = Q1 * (N2/N1) * (D2/D1)
    - H2 = H1 * (N2/N1)^2 * (D2/D1)^2
    - P2 = P1 * (N2/N1)^3 * (D2/D1)^3
    - NPSHr2 = NPSHr1 * (N2/N1)^2
    """
    if N1 <= 0 or D1 <= 0:
        return {"Q2": Q1, "H2": H1, "P2": P1, "npshr2": npshr1, "aviso_rebaixamento": None}

    ratio_n = N2 / N1
    ratio_d = D2 / D1

    Q2 = Q1 * ratio_n * ratio_d
    H2 = H1 * (ratio_n**2) * (ratio_d**2)
    P2 = P1 * (ratio_n**3) * (ratio_d**3)

    npshr2 = None
    if npshr1 is not None:
        npshr2 = npshr1 * (ratio_n**2)

    aviso = None
    if ratio_d < 0.80:
        aviso = f"Corte de impulsor ({ratio_d*100:.1f}%) superior a 20% reduz o rendimento hidráulico da bomba."

    return {
        "Q2": Q2,
        "H2": H2,
        "P2": P2,
        "npshr2": npshr2,
        "aviso_rebaixamento": aviso
    }
