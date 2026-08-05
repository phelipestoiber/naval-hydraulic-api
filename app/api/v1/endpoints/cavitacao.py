from fastapi import APIRouter
from app.schemas.cavitacao import NPSHRequest, NPSHResponse
from app.core.cavitacao.npsh import calcular_npsha
from app.core.cavitacao.margem import avaliar_margem_cavitacao

router = APIRouter(prefix="/cavitacao", tags=["Cavitação"])

@router.post("/npsh", response_model=NPSHResponse)
def endpoint_npsh(payload: NPSHRequest):
    npsha = calcular_npsha(
        p_atm_pa=payload.p_atm_pa,
        temp_c=payload.temperatura_c,
        z_suc_m=payload.z_suc_m,
        hf_suc_m=payload.hf_suc_m
    )

    res_margem = avaliar_margem_cavitacao(npsha_m=npsha, npshr_m=payload.npshr_m)

    return NPSHResponse(
        npsha_m=npsha,
        npshr_m=payload.npshr_m,
        margem_m=res_margem["margem_m"],
        margem_requerida_m=res_margem["margem_requerida_m"],
        cavitacao_detectada=res_margem["cavitacao_detectada"],
        status_cavitacao=res_margem["status_cavitacao"]
    )
