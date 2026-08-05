from typing import Any

def verificar_normas_classificadoras(
    classificadora: str,
    v_suc_ms: float,
    v_desc_ms: float,
    pressao_bar: float,
    temp_c: float
) -> dict[str, Any]:
    """
    Valida os limites operacionais estipulados pelas normas das sociedades classificadoras (BV, LR, ABS):
    - Velocidade de sucção em água do mar: 0,5 m/s <= v_suc <= 1,2 m/s
    - Velocidade de descarga em água do mar: 1,5 m/s <= v_desc <= 3,0 m/s
    """
    alertas = []
    classificadora_upper = classificadora.upper()

    if v_suc_ms > 1.2:
        alertas.append(f"Velocidade de sucção ({v_suc_ms:.2f} m/s) acima do limite recomendado pela {classificadora_upper} (1.2 m/s).")
    elif v_suc_ms < 0.5:
        alertas.append(f"Velocidade de sucção ({v_suc_ms:.2f} m/s) abaixo do limite recomendado pela {classificadora_upper} (0.5 m/s).")

    if v_desc_ms > 3.0:
        alertas.append(f"Velocidade de descarga ({v_desc_ms:.2f} m/s) acima do limite recomendado pela {classificadora_upper} (3.0 m/s).")

    return {
        "classificadora": classificadora_upper,
        "conforme": len(alertas) == 0,
        "alertas": alertas
    }
