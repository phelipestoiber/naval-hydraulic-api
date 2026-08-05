def calcular_rendimento_global(
    eta_bomba: float,
    eta_motor: float,
    eta_transmissao: float = 1.0
) -> float:
    """
    Calcula o rendimento global da cadeia de acionamento:
    eta_global = eta_bomba * eta_motor * eta_transmissao
    """
    return eta_bomba * eta_motor * eta_transmissao
