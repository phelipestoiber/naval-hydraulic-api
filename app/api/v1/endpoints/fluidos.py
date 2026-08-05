from fastapi import APIRouter
from app.schemas.fluido import PropriedadesFluidoRequest, PropriedadesFluidoResponse
from app.core.fluidos.viscosidade import calcular_viscosidade
from app.core.fluidos.reynolds import calcular_reynolds, determinar_regime_escoamento, calcular_alpha_cinetico

router = APIRouter(prefix="/fluidos", tags=["Fluidos"])

@router.post("/propriedades", response_model=PropriedadesFluidoResponse)
def calcular_propriedades_fluido(payload: PropriedadesFluidoRequest):
    temp_k = payload.temperatura_c + 273.15
    res_visc = calcular_viscosidade(payload.fluido, temp_k)

    rho = res_visc["massa_especifica_kgm3"]
    mu = res_visc["viscosidade_dinamica_pas"]
    nu = res_visc["viscosidade_cinematica_m2s"]

    Q_m3s = payload.vazao_m3h / 3600.0
    D_m = payload.diametro_mm / 1000.0
    area = 3.141592653589793 * (D_m**2) / 4.0
    v_ms = Q_m3s / area if area > 0 else 0.0

    Re = calcular_reynolds(v_ms, D_m, nu)
    regime = determinar_regime_escoamento(Re)
    alpha = calcular_alpha_cinetico(Re)

    return PropriedadesFluidoResponse(
        fluido=payload.fluido,
        temperatura_c=payload.temperatura_c,
        massa_especifica_kgm3=rho,
        viscosidade_dinamica_pas=mu,
        viscosidade_cinematica_m2s=nu,
        velocidade_ms=v_ms,
        reynolds=Re,
        regime=regime,
        alpha_cinetico=alpha
    )
