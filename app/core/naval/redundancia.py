from typing import Any

def avaliar_redundancia(
    essencial: bool,
    num_bombas: int,
    alim_indep: bool
) -> dict[str, Any]:
    """
    Avalia os requisitos de redundância funcional e alimentação elétrica independente
    para sistemas essenciais de bordo conforme regras SOLAS / NORMAM / Sociedades Classificadoras:
    - Sistemas essenciais exigem N >= 2 bombas com alimentações elétricas/mecânicas independentes.
    """
    alertas = []
    conforme = True

    if essencial:
        if num_bombas < 2:
            conforme = False
            alertas.append("Sistemas essenciais exigem no mínimo 2 bombas instaladas em paralelo (redundância 100%).")
        if not alim_indep:
            conforme = False
            alertas.append("Sistemas essenciais exigem fontes de alimentação de energia independentes para cada bomba.")

    return {
        "essencial": essencial,
        "num_bombas": num_bombas,
        "alimentacao_independente": alim_indep,
        "conforme": conforme,
        "alertas": alertas
    }
