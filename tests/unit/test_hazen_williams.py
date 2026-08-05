import pytest
from app.core.perda_carga.hazen_williams import calcular_perda_carga_hazen_williams

def test_hazen_williams_4_casos_validacao_fallback():
    """T3.2 — HW: 4 casos rejeição/aceitação"""
    # 1. Fluido inválido (óleo diesel) -> HW_FLUIDO_INVALIDO -> fallback Darcy-Weisbach
    res_diesel = calcular_perda_carga_hazen_williams(
        Q_m3s=0.032917, L_m=10.0, D_m=0.150, C=140,
        tipo_fluido="oleo_diesel", temp_c=20.0, Re=50000.0, f_darcy=0.02
    )
    assert res_diesel["metodo_usado"] == "darcy_weisbach"
    assert res_diesel["codigo_rejeicao"] == "HW_FLUIDO_INVALIDO"
    assert res_diesel["aviso"] is not None

    # 2. Temperatura inválida (85°C > 30°C) -> HW_TEMPERATURA_INVALIDA -> fallback Darcy
    res_temp = calcular_perda_carga_hazen_williams(
        Q_m3s=0.032917, L_m=10.0, D_m=0.150, C=140,
        tipo_fluido="agua_doce", temp_c=85.0, Re=50000.0, f_darcy=0.02
    )
    assert res_temp["metodo_usado"] == "darcy_weisbach"
    assert res_temp["codigo_rejeicao"] == "HW_TEMPERATURA_INVALIDA"

    # 3. Válido (água doce, 20°C, Re=50k, D=150mm) -> aceita Hazen-Williams
    res_valido = calcular_perda_carga_hazen_williams(
        Q_m3s=0.032917, L_m=10.0, D_m=0.150, C=140,
        tipo_fluido="agua_doce", temp_c=20.0, Re=50000.0, f_darcy=0.02
    )
    assert res_valido["metodo_usado"] == "hazen_williams"
    assert res_valido["codigo_rejeicao"] is None
    assert res_valido["hf_m"] > 0

    # 4. Regime inválido (Re=1500 < 4000) -> HW_REGIME_INVALIDO -> fallback Darcy
    res_laminar = calcular_perda_carga_hazen_williams(
        Q_m3s=0.032917, L_m=10.0, D_m=0.150, C=140,
        tipo_fluido="agua_salgada", temp_c=15.0, Re=1500.0, f_darcy=0.04
    )
    assert res_laminar["metodo_usado"] == "darcy_weisbach"
    assert res_laminar["codigo_rejeicao"] == "HW_REGIME_INVALIDO"

    # 5. Diâmetro inválido (D = 5 mm = 0.005 m < 0.012 m) -> HW_DIAMETRO_INVALIDO -> fallback Darcy
    res_diametro = calcular_perda_carga_hazen_williams(
        Q_m3s=0.001, L_m=10.0, D_m=0.005, C=140,
        tipo_fluido="agua_doce", temp_c=20.0, Re=50000.0, f_darcy=0.02
    )
    assert res_diametro["metodo_usado"] == "darcy_weisbach"
    assert res_diametro["codigo_rejeicao"] == "HW_DIAMETRO_INVALIDO"

def test_hw_vs_darcy_tolerancia_10_porcento():
    """T3.5 — HW vs Darcy (< 10% diferença para água doce 20°C)"""
    Q_m3s = 0.032917
    L_m = 8.5
    D_m = 0.150
    C = 145
    f_darcy = 0.0158

    res = calcular_perda_carga_hazen_williams(
        Q_m3s=Q_m3s, L_m=L_m, D_m=D_m, C=C,
        tipo_fluido="agua_doce", temp_c=20.0, Re=287000.0, f_darcy=f_darcy
    )
    assert res["metodo_usado"] == "hazen_williams"

    hf_hw = res["hf_m"]
    v = (4.0 * Q_m3s) / (3.14159265 * D_m**2)
    hf_dw = f_darcy * (L_m / D_m) * (v**2 / (2.0 * 9.81))

    diff_relativa = abs(hf_hw - hf_dw) / hf_dw
    assert diff_relativa <= 0.10
