from typing import Any
from app.schemas.si import SistemaSI, RastreabilidadeUnidades
from app.schemas.erro import ErroCalculo

def detectar_malha_fechada(trechos: list[Any]) -> bool:
    """
    Detecta topologia em malha fechada (ciclos, loops, anéis).
    Se qualquer id_destino apontar para um trecho já visitado, há malha fechada.
    """
    ids_vistos = set()
    for trecho in trechos:
        id_atual = trecho.get('id') if isinstance(trecho, dict) else getattr(trecho, 'id', None)
        id_destino = trecho.get('id_destino') if isinstance(trecho, dict) else getattr(trecho, 'id_destino', None)

        if id_destino and id_destino in ids_vistos:
            return True
        if id_atual:
            ids_vistos.add(id_atual)
    return False

def realizar_unit_casting(payload: dict[str, Any]) -> tuple[SistemaSI, RastreabilidadeUnidades]:
    """
    Executa a conversão de unidades de engenharia para o Sistema Internacional (SI),
    aplica sanity checks e verifica limitações topológicas.
    Sporta payloads planos e estruturados em seções ('sistema', 'fluido', 'trechos', 'bomba').
    """
    sistema_dict = payload.get("sistema", {}) if isinstance(payload.get("sistema"), dict) else {}
    fluido_dict = payload.get("fluido", {}) if isinstance(payload.get("fluido"), dict) else {}
    trechos_list = payload.get("trechos", []) if isinstance(payload.get("trechos"), list) else []

    # 1. Sanity Check — Unidade de Vazão
    unidade_vazao = payload.get("unidade_vazao", sistema_dict.get("unidade_vazao", "m3h"))
    unidades_vazao_validas = ("m3h", "m3/h", "l/min", "l/s", "m3s")
    if unidade_vazao not in unidades_vazao_validas:
        raise ErroCalculo(
            codigo="UNIDADE_INVALIDA",
            mensagem=f"Unidade de vazão '{unidade_vazao}' não suportada. Use m3h, l/min ou l/s.",
            campo="unidade_vazao"
        )

    # 2. Sanity Check — Vazão
    vazao_bruta = payload.get("vazao", sistema_dict.get("vazao", 0.0))
    if vazao_bruta <= 0:
        raise ErroCalculo(
            codigo="VAZAO_NEGATIVA",
            mensagem=f"Vazão deve ser strictly positiva (fornecida: {vazao_bruta}).",
            campo="vazao"
        )

    # Fator de conversão da vazão para m3/s
    if unidade_vazao in ("m3h", "m3/h"):
        fator_vazao = "/ 3600"
        Q_m3s = vazao_bruta / 3600.0
    elif unidade_vazao == "l/min":
        fator_vazao = "/ 60000"
        Q_m3s = vazao_bruta / 60000.0
    elif unidade_vazao == "l/s":
        fator_vazao = "/ 1000"
        Q_m3s = vazao_bruta / 1000.0
    else:
        fator_vazao = "1"
        Q_m3s = vazao_bruta

    # 3. Sanity Check — Diâmetro
    diametro_default = 150.0
    if trechos_list and isinstance(trechos_list[0], dict):
        diametro_default = trechos_list[0].get("diametro_interno_mm", 150.0)

    diametro_mm = payload.get("diametro_mm", payload.get("diametro_s_mm", sistema_dict.get("diametro_mm", diametro_default)))
    if diametro_mm <= 0:
        raise ErroCalculo(
            codigo="DIAMETRO_INVALIDO",
            mensagem=f"Diâmetro deve ser positivo (fornecido: {diametro_mm}).",
            campo="diametro_mm"
        )
    D_m = diametro_mm / 1000.0

    # 4. Sanity Check — Densidade
    rho = payload.get("densidade_kg_m3", fluido_dict.get("densidade_kg_m3", 1000.0))
    if rho <= 0 or rho > 2000.0:
        raise ErroCalculo(
            codigo="DENSIDADE_INVALIDA",
            mensagem=f"Massa específica deve estar no intervalo (0, 2000] kg/m³ (fornecida: {rho}).",
            campo="densidade_kg_m3"
        )

    # 5. Sanity Check — Viscosidade dinâmica
    mu = payload.get("viscosidade_dinamica_Pa_s", fluido_dict.get("viscosidade_dinamica_Pa_s", 0.001))
    if mu <= 0:
        raise ErroCalculo(
            codigo="VISCOSIDADE_INVALIDA",
            mensagem=f"Viscosidade dinâmica deve ser positiva (fornecida: {mu}).",
            campo="viscosidade_dinamica_Pa_s"
        )
    nu_m2s = mu / rho

    # 6. Sanity Check — Pressão de vapor
    pressao_vapor = payload.get("pressao_vapor_Pa", fluido_dict.get("pressao_vapor_Pa", 0.0))
    if pressao_vapor < 0:
        raise ErroCalculo(
            codigo="PRESSAO_VAPOR_INVALIDA",
            mensagem=f"Pressão de vapor não pode ser negativa (fornecida: {pressao_vapor}).",
            campo="pressao_vapor_Pa"
        )

    # 7. Sanity Check — Temperatura
    temp_c = payload.get("temperatura_C", fluido_dict.get("temperatura_C", 20.0))
    T_k = temp_c + 273.15
    if T_k < 273.15 or T_k > 700.0:
        raise ErroCalculo(
            codigo="TEMPERATURA_FORA_DO_RANGE",
            mensagem=f"Temperatura em Kelvin deve estar entre 273.15 K (0°C) e 700 K (fornecida: {temp_c}°C = {T_k} K).",
            campo="temperatura_C"
        )

    # 8. Sanity Check — Rugosidade
    rugosidade_mm = payload.get("rugosidade_mm", 0.045)
    if rugosidade_mm < 0:
        raise ErroCalculo(
            codigo="RUGOSIDADE_INVALIDA",
            mensagem=f"Rugosidade não pode ser negativa (fornecida: {rugosidade_mm}).",
            campo="rugosidade_mm"
        )
    epsilon_m = rugosidade_mm / 1000.0

    # 9. Topologia Check (Malha Fechada — F1)
    if trechos_list and detectar_malha_fechada(trechos_list):
        raise ErroCalculo(
            codigo="TOPOLOGIA_MALHA_NAO_SUPORTADA",
            mensagem=(
                "Topologia em malha fechada detectada. "
                "Este sistema suporta apenas escoamento unidimensional em topologia aberta. "
                "Sistemas em anel requerem solver matricial (Hardy-Cross) — fora do escopo."
            )
        )

    comprimento_m = payload.get("comprimento_m", 10.0)
    pressao_atm_Pa = payload.get("pressao_atm_Pa", sistema_dict.get("pressao_atm_Pa", 101325.0))
    altitude_m = payload.get("altitude_m", sistema_dict.get("altitude_m", 0.0))
    rotacao_rpm = payload.get("rotacao_rpm", payload.get("bomba", {}).get("rotacao_rpm", 1450.0))

    sistema_si = SistemaSI(
        Q_m3s=Q_m3s,
        D_m=D_m,
        L_m=comprimento_m,
        rho_kgm3=rho,
        mu_pas=mu,
        nu_m2s=nu_m2s,
        Pv_pa=pressao_vapor,
        Patm_pa=pressao_atm_Pa,
        T_k=T_k,
        epsilon_m=epsilon_m,
        altitude_m=altitude_m,
        N_rpm=rotacao_rpm
    )

    rastreabilidade = RastreabilidadeUnidades(campos=[
        {
            "campo": "vazao",
            "valor_entrada": vazao_bruta,
            "unidade_entrada": unidade_vazao,
            "valor_si": Q_m3s,
            "unidade_si": "m3/s",
            "fator": fator_vazao
        },
        {
            "campo": "diametro",
            "valor_entrada": diametro_mm,
            "unidade_entrada": "mm",
            "valor_si": D_m,
            "unidade_si": "m",
            "fator": "/ 1000"
        },
        {
            "campo": "temperatura",
            "valor_entrada": temp_c,
            "unidade_entrada": "°C",
            "valor_si": T_k,
            "unidade_si": "K",
            "fator": "+ 273,15"
        }
    ])

    return (sistema_si, rastreabilidade)
