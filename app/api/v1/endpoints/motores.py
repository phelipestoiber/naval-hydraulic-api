from fastapi import APIRouter
from app.schemas.motor import DimensionamentoMotorRequest, DimensionamentoMotorResponse
from app.core.motores.eletrico import (
    calcular_potencia_hidraulica,
    calcular_potencia_eixo,
    calcular_potencia_eletrica,
    calcular_corrente_nominal_trifasica
)
from app.core.motores.rendimento_global import calcular_rendimento_global
from app.core.motores.consumo_diesel import calcular_consumo_diesel

router = APIRouter(prefix="/motores", tags=["Motores"])

@router.post("/dimensionamento", response_model=DimensionamentoMotorResponse)
def endpoint_dimensionamento_motor(payload: DimensionamentoMotorRequest):
    Q_m3s = payload.vazao_m3h / 3600.0
    p_hid = calcular_potencia_hidraulica(Q_m3s, payload.h_op_m)
    p_eixo = calcular_potencia_eixo(p_hid, payload.eta_bomba)
    p_elet = calcular_potencia_eletrica(p_eixo, payload.eta_motor, payload.eta_transmissao)

    i_nom = calcular_corrente_nominal_trifasica(p_elet, payload.tensao_volts, payload.fator_potencia)
    eta_global = calcular_rendimento_global(payload.eta_bomba, payload.eta_motor, payload.eta_transmissao)

    consumo_lh = None
    if payload.tipo_acionador.lower() == "diesel":
        res_c = calcular_consumo_diesel(p_eixo, payload.sfc_g_kwh)
        consumo_lh = res_c["consumo_lh"]

    return DimensionamentoMotorResponse(
        potencia_hidraulica_kw=p_hid,
        potencia_eixo_kw=p_eixo,
        potencia_eletrica_kw=p_elet,
        corrente_nominal_a=i_nom,
        rendimento_global=eta_global,
        consumo_lh=consumo_lh
    )
