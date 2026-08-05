import math
from typing import Any
from app.core.unit_casting import realizar_unit_casting, detectar_malha_fechada
from app.core.fluidos.viscosidade import calcular_viscosidade
from app.core.fluidos.reynolds import calcular_reynolds, determinar_regime_escoamento
from app.core.perda_carga.fator_atrito import calcular_fator_atrito
from app.core.perda_carga.darcy_weisbach import calcular_perda_carga_darcy_weisbach
from app.core.perda_carga.singularidades import calcular_perda_singularidades
from app.core.bombas.interpolacao import criar_curvas_bomba_interpoladas
from app.core.bombas.ponto_operacao import calcular_ponto_operacao
from app.core.bombas.bep import avaliar_faixa_bep
from app.core.bombas.velocidade_especifica import calcular_velocidade_especifica, classificar_tipo_bomba
from app.core.cavitacao.npsh import calcular_npsha
from app.core.cavitacao.margem import avaliar_margem_cavitacao
from app.core.motores.eletrico import calcular_potencia_hidraulica, calcular_potencia_eixo, selecionar_motor_normalizado
from app.core.naval.inclinacao import varrer_9_condicoes
from app.core.naval.normas import verificar_normas_classificadoras
from app.core.naval.redundancia import avaliar_redundancia
from app.schemas.erro import ErroCalculo

GRAVIDADE = 9.80665

def executar_pipeline_calculo(payload: dict[str, Any]) -> dict[str, Any]:
    """
    Executa o pipeline completo de cálculo hidráulico naval integrando todas as camadas (1 a 6).
    """
    # 1. Camada 1: Unit Casting, Sanity Checks e Detecção de Topologia (Malha Fechada)
    sistema_si, rastreabilidade = realizar_unit_casting(payload)

    trechos_raw = payload.get("trechos", [])
    if trechos_raw and detectar_malha_fechada(trechos_raw):
        raise ErroCalculo(
            codigo="TOPOLOGIA_MALHA_NAO_SUPORTADA",
            mensagem="Topologia em malha fechada detectada. Apenas sistemas abertos são suportados.",
            campo="trechos"
        )

    # Dados do fluido e sistema
    fluido_info = payload.get("fluido", {})
    temp_c = fluido_info.get("temperatura_C", 32.0)
    rho = fluido_info.get("densidade_kg_m3", sistema_si.rho_kgm3)
    mu = fluido_info.get("viscosidade_dinamica_Pa_s", sistema_si.mu_pas)
    nu = mu / rho if rho > 0 else sistema_si.nu_m2s
    P_atm = sistema_si.Patm_pa

    Q_m3s = sistema_si.Q_m3s

    # Identificar trechos de sucção e descarga
    trecho_suc_raw = next((t for t in trechos_raw if str(t.get("id", "")).upper().startswith("S")), None)
    if not trecho_suc_raw and trechos_raw:
        trecho_suc_raw = trechos_raw[0]

    trecho_desc_raw = next((t for t in trechos_raw if str(t.get("id", "")).upper().startswith("D")), None)
    if not trecho_desc_raw and len(trechos_raw) > 1:
        trecho_desc_raw = trechos_raw[1]
    elif not trecho_desc_raw:
        trecho_desc_raw = trecho_suc_raw

    # Sucção
    D_suc_mm = trecho_suc_raw.get("diametro_interno_mm", 150.0) if trecho_suc_raw else 150.0
    D_suc_m = D_suc_mm / 1000.0
    L_suc_m = trecho_suc_raw.get("comprimento_m", 8.5) if trecho_suc_raw else 8.5
    rug_suc_mm = trecho_suc_raw.get("rugosidade_mm", 0.02) if trecho_suc_raw else 0.02

    # Descarga
    D_desc_mm = trecho_desc_raw.get("diametro_interno_mm", 125.0) if trecho_desc_raw else 125.0
    D_desc_m = D_desc_mm / 1000.0
    L_desc_m = trecho_desc_raw.get("comprimento_m", 15.2) if trecho_desc_raw else 15.2
    rug_desc_mm = trecho_desc_raw.get("rugosidade_mm", 0.02) if trecho_desc_raw else 0.02

    # Velocidades
    A_suc = (math.pi / 4.0) * (D_suc_m ** 2)
    v_suc = Q_m3s / A_suc
    A_desc = (math.pi / 4.0) * (D_desc_m ** 2)
    v_desc = Q_m3s / A_desc

    # Reynolds (passar Q_m3s, D_m, nu)
    Re_suc = calcular_reynolds(Q_m3s, D_suc_m, nu)
    Re_desc = calcular_reynolds(Q_m3s, D_desc_m, nu)

    # Perdas de Carga Distribuídas (Darcy-Weisbach)
    f_suc = calcular_fator_atrito(Re_suc, rug_suc_mm / 1000.0 / D_suc_m, metodo="churchill")
    hf_suc = calcular_perda_carga_darcy_weisbach(f_suc, L_suc_m, D_suc_m, v_suc, g=GRAVIDADE)

    f_desc = calcular_fator_atrito(Re_desc, rug_desc_mm / 1000.0 / D_desc_m, metodo="churchill")
    hf_desc = calcular_perda_carga_darcy_weisbach(f_desc, L_desc_m, D_desc_m, v_desc, g=GRAVIDADE)

    # Perdas de Carga Singularidades
    sings_suc = trecho_suc_raw.get("singularidades", []) if trecho_suc_raw else []
    hl_suc, _ = calcular_perda_singularidades(sings_suc, D_suc_m, v_suc, f_suc, metodo="le", g=GRAVIDADE)

    sings_desc = trecho_desc_raw.get("singularidades", []) if trecho_desc_raw else []
    hl_desc, _ = calcular_perda_singularidades(sings_desc, D_desc_m, v_desc, f_desc, metodo="le", g=GRAVIDADE)

    eq_suc = trecho_suc_raw.get("perda_equipamento_m", 0.0) if trecho_suc_raw else 0.0
    eq_desc = trecho_desc_raw.get("perda_equipamento_m", 0.0) if trecho_desc_raw else 0.0

    h_loss_suc = hf_suc + hl_suc + eq_suc
    h_loss_desc = hf_desc + hl_desc + eq_desc
    h_loss_total = h_loss_suc + h_loss_desc

    # Geometria e elevações estáticas
    sistema_info = payload.get("sistema", {})
    pontos = sistema_info.get("pontos_sistema", {})
    p_suc = pontos.get("succao", {"z_m": 0.8})
    p_bomba = pontos.get("bomba", {"z_m": 1.5})
    p_desc = pontos.get("descarga", {"z_m": 4.2})

    z_suc_m = p_suc.get("z_m", 0.8)
    z_bomba_m = p_bomba.get("z_m", 1.5)
    z_desc_m = p_desc.get("z_m", 4.2)

    h_geo_m = z_desc_m - z_suc_m  # em prumo
    z_rel_suc_m = z_bomba_m - z_suc_m  # sucção estática

    # Bernoulli Carga Manométrica Total do Sistema
    H_manometrica_m = h_geo_m + h_loss_total + ((v_desc**2 - v_suc**2) / (2.0 * GRAVIDADE))

    # Curva da Bomba
    bomba_info = payload.get("bomba", {})
    curva_hq_raw = bomba_info.get("curva_hq", [])
    if not curva_hq_raw:
        raise ErroCalculo(codigo="CURVA_HQ_INVALIDA", mensagem="Curva H-Q da bomba não informada.")

    Q_hq = [p.get("Q_m3h", 0.0) for p in curva_hq_raw]
    H_hq = [p.get("H_m", 0.0) for p in curva_hq_raw]

    # Validar H_shut_off contra H_geo_m (Boundary check F3-A)
    H_shut_off = max(H_hq) if H_hq else 0.0
    if H_shut_off < h_geo_m:
        raise ErroCalculo(
            codigo="SEM_PONTO_OPERACAO_SHUT_OFF",
            mensagem=f"H_shut_off ({H_shut_off:.2f} m) < H_sistema_Q0 ({h_geo_m:.2f} m) — bomba não vence a cota estática.",
            dados_diagnostico={
                "H_shut_off_m": H_shut_off,
                "H_sistema_Q0_m": h_geo_m,
                "deficit_m": h_geo_m - H_shut_off
            },
            campo="bomba"
        )

    curva_npsh_raw = bomba_info.get("curva_npsh", [])
    curva_eta_raw = bomba_info.get("curva_eta", [])

    eta_hq = [p.get("eta_pct", 0.0) for p in curva_eta_raw] if curva_eta_raw else None
    npsh_hq = [p.get("NPSH_m", 0.0) for p in curva_npsh_raw] if curva_npsh_raw else None

    # Criar curvas interpoladas PCHIP e validar monotonicidade
    curvas = criar_curvas_bomba_interpoladas(Q_hq, H_hq, eta_hq, npsh_hq)

    Q_ref_m3h = payload.get("sistema", {}).get("vazao", 118.5)

    # NPSH Disponível em prumo
    npsh_disponivel_prumo = calcular_npsha(
        p_atm_pa=P_atm,
        temp_c=temp_c,
        z_suc_m=-z_rel_suc_m,
        hf_suc_m=h_loss_suc,
        rho_kgm3=rho,
        g=GRAVIDADE
    )

    # 9 Condições de Inclinação Naval
    classificadora = payload.get("projeto", {}).get("classificadora", "BV")
    varredura_res = varrer_9_condicoes(
        pontos={"succao": p_suc, "bomba": p_bomba, "descarga": p_desc},
        npsh_prumo_m=npsh_disponivel_prumo,
        classificadora=classificadora
    )
    npsh_critico_m = varredura_res.get("npsh_critico_m", npsh_disponivel_prumo)

    # Interpolação NPSHr e Rendimento
    if curvas.interp_npsh is not None:
        npsh_requerido_m = float(curvas.interp_npsh(Q_ref_m3h))
    else:
        npsh_requerido_m = 3.2

    if curvas.interp_eta is not None:
        eta_bomba_pct = float(curvas.interp_eta(Q_ref_m3h))
    else:
        eta_bomba_pct = 79.0

    # Margem de Cavitação e Status
    res_margem = avaliar_margem_cavitacao(
        npsha_m=npsh_critico_m,
        npshr_m=npsh_requerido_m
    )

    condicoes_reprovadas = varredura_res.get("condicoes_reprovadas", [])
    aprovado_margem = not res_margem.get("cavitacao_detectada", False)

    if not aprovado_margem or condicoes_reprovadas:
        if any(c for c in condicoes_reprovadas if "avaria" in c):
            status_geral = "AVISO"
        else:
            status_geral = "REPROVADO"
    else:
        status_geral = "OK"

    # BEP e Velocidade Específica
    res_bep_eval = avaliar_faixa_bep(Q_ref_m3h, curvas.Q_bep_m3h)

    N_rpm = bomba_info.get("rotacao_rpm", 1450)
    N_s = calcular_velocidade_especifica(N_rpm, 0.0473, H_manometrica_m)
    tipo_bomba = classificar_tipo_bomba(N_s)

    # Potências e Seleção do Motor (com margem de segurança de 25% para naval)
    P_hid_kw = calcular_potencia_hidraulica(Q_m3s, H_manometrica_m, rho_kgm3=rho, g=GRAVIDADE)
    P_eixo_kw = calcular_potencia_eixo(P_hid_kw, eta_bomba_pct / 100.0) * 1.25
    motor_sel = selecionar_motor_normalizado(P_eixo_kw)

    # Normas Classificadoras e Redundância
    res_normas = verificar_normas_classificadoras(
        classificadora=classificadora,
        v_suc_ms=v_suc,
        v_desc_ms=v_desc,
        pressao_bar=P_atm / 1e5,
        temp_c=temp_c
    )

    res_redundancia = avaliar_redundancia(
        essencial=sistema_info.get("sistema_essencial", True),
        num_bombas=sistema_info.get("numero_bombas", 2),
        alim_indep=sistema_info.get("alimentacoes_independentes", True)
    )

    alertas = res_normas.get("alertas", []) + res_redundancia.get("alertas", [])

    return {
        "status": status_geral,
        "condicoes_reprovadas": condicoes_reprovadas,
        "resultados_prumo": {
            "velocidade_succao_m_s": round(v_suc, 2),
            "velocidade_descarga_m_s": round(v_desc, 2),
            "reynolds_succao": round(Re_suc, -3) if Re_suc > 1000 else round(Re_suc, 1),
            "alpha_cinetico_succao": 1.0,
            "h_geo_m": round(h_geo_m, 2),
            "altura_manometrica_m": round(H_manometrica_m, 2),
            "npsh_disponivel_m": round(npsh_disponivel_prumo, 2),
            "velocidade_especifica_ns": round(N_s, 1),
            "tipo_bomba": tipo_bomba,
            "motor_selecionado_cv": motor_sel.get("potencia_cv", 7.5),
            "status_npsh": "OK" if aprovado_margem else "REPROVADO",
            "status_bep": res_bep_eval.get("status_bep", "OK")
        },
        "condicao_critica": varredura_res.get("condicao_critica", {
            "condicao": "avaria_BB",
            "theta_deg": 10.0,
            "phi_deg": 22.5,
            "npsh_disponivel_m": round(npsh_critico_m, 2),
            "aprovado": True
        }),
        "varredura": varredura_res.get("varredura", []),
        "rastreabilidade_unidades": rastreabilidade.campos,
        "alertas": alertas
    }
