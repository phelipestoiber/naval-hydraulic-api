from typing import Callable, Any
from app.core.bombas.interpolacao import CurvasBombaInterpoladas
from app.utils.math_utils import bissecao
from app.schemas.erro import ErroCalculo

def calcular_ponto_operacao(
    curvas: CurvasBombaInterpoladas,
    fn_h_sistema: Callable[[float], float],
    tol: float = 1e-4,
    max_iter: int = 100
) -> dict[str, Any]:
    """
    Calcula o ponto de operação (Q_op, H_op) do par bomba-sistema.
    Executa boundary check obrigatório (F3) antes do loop de cálculo.
    """
    Q_min = curvas.Q_min_m3h
    Q_max = curvas.Q_max_m3h

    H_bom_min = float(curvas.interp_hq(Q_min))
    H_bom_max = float(curvas.interp_hq(Q_max))

    H_sis_min = float(fn_h_sistema(Q_min))
    H_sis_max = float(fn_h_sistema(Q_max))

    g_min = H_bom_min - H_sis_min
    g_max = H_bom_max - H_sis_max

    # Boundary Check F3-A: H_shut_off < H_sistema(Q=0)
    if g_min < 0:
        raise ErroCalculo(
            codigo="SEM_PONTO_OPERACAO_SHUT_OFF",
            mensagem=f"H_shut_off ({H_bom_min:.2f} m) < H_sistema_Q0 ({H_sis_min:.2f} m) — bomba não vence a cota/pressão estática.",
            dados_diagnostico={
                "H_shut_off_m": H_bom_min,
                "H_sistema_Q0_m": H_sis_min,
                "deficit_m": H_sis_min - H_bom_min
            },
            campo="bomba"
        )

    # Boundary Check F3-B: g(Q_max) > 0
    if g_max > 0:
        raise ErroCalculo(
            codigo="SEM_PONTO_OPERACAO_FORA_CURVA",
            mensagem=f"Q_op > Q_max ({Q_max:.1f} m³/h) — bomba superdimensionada ou perda de carga muito baixa.",
            dados_diagnostico={"Q_max_curva_m3h": Q_max},
            campo="bomba"
        )

    # Função objetivo: g(Q) = H_bomba(Q) - H_sistema(Q)
    def g_obj(q_m3h: float) -> float:
        return float(curvas.interp_hq(q_m3h)) - fn_h_sistema(q_m3h)

    Q_op, iteracoes, convergiu = bissecao(g_obj, Q_min, Q_max, tol=tol, max_iter=max_iter)

    if not convergiu:
        raise ErroCalculo(
            codigo="SEM_PONTO_OPERACAO",
            mensagem="Falha de convergência ao determinar o ponto de operação da bomba.",
            campo="bomba"
        )

    H_op = float(curvas.interp_hq(Q_op))
    H_sis_op = fn_h_sistema(Q_op)
    residual = abs(H_op - H_sis_op)

    return {
        "Q_op_m3h": Q_op,
        "H_op_m": H_op,
        "residual_m": residual,
        "iteracoes": iteracoes,
        "convergiu": True
    }
