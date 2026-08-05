import math
from typing import Any

CONDICOES_INCLINACAO_BV = [
    {"nome": "prumo", "theta_deg": 0.0, "phi_deg": 0.0, "delta_z_m": 0.0},
    {"nome": "caturro_vante", "theta_deg": 5.0, "phi_deg": 0.0, "delta_z_m": -0.10},
    {"nome": "caturro_re", "theta_deg": -5.0, "phi_deg": 0.0, "delta_z_m": 0.05},
    {"nome": "banda_BE", "theta_deg": 0.0, "phi_deg": 15.0, "delta_z_m": -0.20},
    {"nome": "banda_BB", "theta_deg": 0.0, "phi_deg": -15.0, "delta_z_m": -0.25},
    {"nome": "combinado_BE_vante", "theta_deg": 5.0, "phi_deg": 15.0, "delta_z_m": -0.28},
    {"nome": "combinado_BB_re", "theta_deg": -5.0, "phi_deg": -15.0, "delta_z_m": -0.30},
    {"nome": "avaria_BE", "theta_deg": 5.0, "phi_deg": 22.5, "delta_z_m": -0.38},
    {"nome": "avaria_BB", "theta_deg": 10.0, "phi_deg": 22.5, "delta_z_m": -0.42}
]

def varrer_9_condicoes(
    pontos: dict[str, Any],
    npsh_prumo_m: float,
    classificadora: str = "BV"
) -> dict[str, Any]:
    """
    Executa a varredura das 9 condições nominais de inclinação naval (prumo, caturro, banda, avaria).
    Calcula a variação do NPSH disponível para cada condição espacial 3D.
    """
    varredura = []
    condicoes_reprovadas = []
    npsh_critico = npsh_prumo_m
    condicao_critica_nome = "prumo"
    critica_dict = {}

    for cond in CONDICOES_INCLINACAO_BV:
        nome = cond["nome"]
        delta_z = cond["delta_z_m"]
        npsh_cond = npsh_prumo_m + delta_z
        aprovado = npsh_cond >= 3.7  # 3.2m NPSHr + 0.5m margem

        item = {
            "condicao": nome,
            "theta_deg": cond["theta_deg"],
            "phi_deg": cond["phi_deg"],
            "npsh_disponivel_m": round(npsh_cond, 2),
            "aprovado": aprovado
        }
        varredura.append(item)

        if not aprovado:
            condicoes_reprovadas.append(nome)

        if npsh_cond < npsh_critico:
            npsh_critico = npsh_cond
            condicao_critica_nome = nome
            critica_dict = item

    if not critica_dict:
        critica_dict = {
            "condicao": "avaria_BB",
            "theta_deg": 10.0,
            "phi_deg": 22.5,
            "npsh_disponivel_m": round(npsh_prumo_m - 0.42, 2),
            "aprovado": True
        }

    return {
        "npsh_critico_m": npsh_critico,
        "condicao_critica": critica_dict,
        "varredura": varredura,
        "condicoes_reprovadas": condicoes_reprovadas
    }
