from fastapi import APIRouter
from app.schemas.bomba import PontoOperacaoRequest, PontoOperacaoResponse
from app.core.bombas.interpolacao import criar_curvas_bomba_interpoladas
from app.core.bombas.ponto_operacao import calcular_ponto_operacao

router = APIRouter(prefix="/bombas", tags=["Bombas"])

@router.post("/ponto-operacao", response_model=PontoOperacaoResponse)
def endpoint_ponto_operacao(payload: PontoOperacaoRequest):
    Q_m3h = [pt.q_m3h for pt in payload.curva_hq]
    H_m = [pt.h_m for pt in payload.curva_hq]

    curvas = criar_curvas_bomba_interpoladas(Q_m3h, H_m)
    fn_h_sistema = lambda q_m3h: payload.h_geo_m + payload.resistencia_sistema_r * (q_m3h**2)

    res = calcular_ponto_operacao(curvas, fn_h_sistema)

    return PontoOperacaoResponse(
        Q_op_m3h=res["Q_op_m3h"],
        H_op_m=res["H_op_m"],
        residual_m=res["residual_m"],
        iteracoes=res["iteracoes"],
        convergiu=res["convergiu"]
    )
