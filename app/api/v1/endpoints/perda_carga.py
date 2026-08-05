import math
from fastapi import APIRouter
from app.schemas.perda_carga import (
    DarcyWeisbachRequest, DarcyWeisbachResponse,
    HazenWilliamsRequest, HazenWilliamsResponse,
    PerdaSingularidadesRequest, PerdaSingularidadesResponse
)
from app.core.fluidos.viscosidade import calcular_viscosidade
from app.core.fluidos.reynolds import calcular_reynolds, determinar_regime_escoamento
from app.core.perda_carga.fator_atrito import calcular_fator_atrito
from app.core.perda_carga.darcy_weisbach import calcular_perda_carga_darcy_weisbach
from app.core.perda_carga.hazen_williams import calcular_perda_carga_hazen_williams
from app.core.perda_carga.singularidades import calcular_perda_singularidades

router = APIRouter(prefix="/perda-carga", tags=["Perda de Carga"])

@router.post("/darcy-weisbach", response_model=DarcyWeisbachResponse)
def endpoint_darcy_weisbach(payload: DarcyWeisbachRequest):
    temp_k = payload.temperatura_c + 273.15
    res_visc = calcular_viscosidade(payload.fluido, temp_k)
    nu = res_visc["viscosidade_cinematica_m2s"]

    Q_m3s = payload.vazao_m3h / 3600.0
    D_m = payload.diametro_mm / 1000.0
    L_m = payload.comprimento_m
    eps_m = payload.rugosidade_mm / 1000.0

    v_ms = (4.0 * Q_m3s) / (math.pi * D_m**2) if D_m > 0 else 0.0
    Re = calcular_reynolds(v_ms, D_m, nu)
    regime = determinar_regime_escoamento(Re)

    eps_d = eps_m / D_m if D_m > 0 else 0.0
    f = calcular_fator_atrito(Re, eps_d, metodo=payload.metodo_fator_atrito)
    hf = calcular_perda_carga_darcy_weisbach(f, L_m, D_m, v_ms)

    return DarcyWeisbachResponse(
        hf_m=hf,
        fator_atrito=f,
        reynolds=Re,
        regime=regime,
        velocidade_ms=v_ms
    )

@router.post("/hazen-williams", response_model=HazenWilliamsResponse)
def endpoint_hazen_williams(payload: HazenWilliamsRequest):
    temp_k = payload.temperatura_c + 273.15
    res_visc = calcular_viscosidade(payload.fluido, temp_k)
    nu = res_visc["viscosidade_cinematica_m2s"]

    Q_m3s = payload.vazao_m3h / 3600.0
    D_m = payload.diametro_mm / 1000.0
    L_m = payload.comprimento_m

    v_ms = (4.0 * Q_m3s) / (math.pi * D_m**2) if D_m > 0 else 0.0
    Re = calcular_reynolds(v_ms, D_m, nu)
    f_darcy = calcular_fator_atrito(Re, 0.0003, metodo="churchill")

    res = calcular_perda_carga_hazen_williams(
        Q_m3s=Q_m3s,
        L_m=L_m,
        D_m=D_m,
        C=payload.coeficiente_c,
        tipo_fluido=payload.fluido,
        temp_c=payload.temperatura_c,
        Re=Re,
        f_darcy=f_darcy
    )

    return HazenWilliamsResponse(
        hf_m=res["hf_m"],
        metodo_usado=res["metodo_usado"],
        aviso=res["aviso"],
        codigo_rejeicao=res["codigo_rejeicao"]
    )

@router.post("/singularidades", response_model=PerdaSingularidadesResponse)
def endpoint_singularidades(payload: PerdaSingularidadesRequest):
    D_m = payload.diametro_mm / 1000.0
    items = [item.model_dump() for item in payload.singularidades]

    hL, Le = calcular_perda_singularidades(
        singularidades=items,
        D_m=D_m,
        v_ms=payload.velocidade_ms,
        f=payload.fator_atrito,
        metodo=payload.metodo
    )

    return PerdaSingularidadesResponse(
        hl_total_m=hL,
        le_total_m=Le
    )
