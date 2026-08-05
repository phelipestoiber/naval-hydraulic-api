import pytest
from app.core.pipeline import executar_pipeline_calculo
from app.schemas.erro import ErroCalculo

def test_pipeline_completo_golden_values(payload_referencia):
    """T9.1 — Pipeline completo: validação estrita de todos os Golden Values"""
    res = executar_pipeline_calculo(payload_referencia)

    assert res["status"] == "OK"
    assert res["condicoes_reprovadas"] == []

    prumo = res["resultados_prumo"]
    assert prumo["velocidade_succao_m_s"] == pytest.approx(1.87, rel=0.02)
    assert prumo["velocidade_descarga_m_s"] == pytest.approx(2.69, rel=0.02)
    assert prumo["reynolds_succao"] == pytest.approx(287000.0, rel=0.05)
    assert prumo["alpha_cinetico_succao"] == 1.0
    assert prumo["h_geo_m"] == pytest.approx(3.40, rel=0.02)
    assert prumo["altura_manometrica_m"] == pytest.approx(8.45, rel=0.05)
    assert prumo["npsh_disponivel_m"] == pytest.approx(4.82, rel=0.05)
    assert prumo["velocidade_especifica_ns"] == pytest.approx(63.7, rel=0.05)
    assert prumo["tipo_bomba"] == "centrifuga_mista"
    assert prumo["motor_selecionado_cv"] == 7.5
    assert prumo["status_npsh"] == "OK"
    assert prumo["status_bep"] == "OK"

    critica = res["condicao_critica"]
    assert critica["condicao"] == "avaria_BB"
    assert critica["npsh_disponivel_m"] == pytest.approx(4.40, rel=0.05)
    assert critica["aprovado"] is True

    assert len(res["varredura"]) == 9

def test_pipeline_rastreabilidade_unidades(payload_referencia):
    """T9.2 — Rastreabilidade de unidades de engenharia para SI"""
    res = executar_pipeline_calculo(payload_referencia)
    rastreabilidade = res["rastreabilidade_unidades"]

    campos_rastreados = {item["campo"]: item for item in rastreabilidade}
    assert "vazao" in campos_rastreados
    assert campos_rastreados["vazao"]["unidade_entrada"] == "m3h"
    assert campos_rastreados["vazao"]["unidade_si"] == "m3/s"

    assert "diametro" in campos_rastreados
    assert campos_rastreados["diametro"]["unidade_entrada"] == "mm"
    assert campos_rastreados["diametro"]["unidade_si"] == "m"

    assert "temperatura" in campos_rastreados
    assert campos_rastreados["temperatura"]["unidade_entrada"] == "°C"
    assert campos_rastreados["temperatura"]["unidade_si"] == "K"

def test_pipeline_alertas_acumulados(payload_referencia):
    """T9.3 — Alertas acumulados de normas e redundância"""
    res = executar_pipeline_calculo(payload_referencia)
    assert isinstance(res["alertas"], list)

def test_pipeline_erro_shut_off(payload_referencia):
    """T9.5 — ErroCalculo: H_geo excede H_shut_off"""
    payload = dict(payload_referencia)
    payload["sistema"] = dict(payload_referencia["sistema"])
    payload["sistema"]["pontos_sistema"] = {
        "succao":   {"x_m": -12.5, "y_m": 1.2, "z_m": 0.8},
        "bomba":    {"x_m": -11.0, "y_m": 1.2, "z_m": 1.5},
        "descarga": {"x_m":   5.0, "y_m": 1.2, "z_m": 50.0} # H_geo = 49.2 m > 42 m shut-off
    }

    with pytest.raises(ErroCalculo) as exc_info:
        executar_pipeline_calculo(payload)

    assert exc_info.value.codigo == "SEM_PONTO_OPERACAO_SHUT_OFF"
    assert exc_info.value.dados_diagnostico["deficit_m"] > 0

def test_pipeline_rejeicao_malha_fechada(payload_referencia):
    """T9.8 — Rejeição de malha fechada na Camada 1"""
    payload = dict(payload_referencia)
    payload["trechos"] = [
        {"id": "S1", "id_destino": "D1", "diametro_interno_mm": 150, "comprimento_m": 8.5},
        {"id": "D1", "id_destino": "S1", "diametro_interno_mm": 125, "comprimento_m": 15.2}
    ]

    with pytest.raises(ErroCalculo) as exc_info:
        executar_pipeline_calculo(payload)

    assert exc_info.value.codigo == "TOPOLOGIA_MALHA_NAO_SUPORTADA"
