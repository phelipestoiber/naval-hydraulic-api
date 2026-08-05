from dataclasses import dataclass
from typing import Sequence
import numpy as np
from scipy.interpolate import PchipInterpolator
from app.utils.math_utils import verificar_envelope
from app.schemas.erro import ErroCalculo

@dataclass
class CurvasBombaInterpoladas:
    Q_min_m3h: float
    Q_max_m3h: float
    H_min_m: float
    H_max_m: float
    interp_hq: PchipInterpolator
    interp_eta: PchipInterpolator | None
    interp_npsh: PchipInterpolator | None
    envelope_valido: bool
    Q_bep_m3h: float

def criar_curvas_bomba_interpoladas(
    Q_m3h: Sequence[float],
    H_m: Sequence[float],
    eta_pct: Sequence[float] | None = None,
    npsh_m: Sequence[float] | None = None
) -> CurvasBombaInterpoladas:
    """
    Cria os interpoladores PCHIP para a curva de bomba e valida o envelope de operação.
    Rejeita com ErroCalculo se a curva tiver < 3 pontos ou se H for crescente.
    """
    if len(Q_m3h) < 3 or len(H_m) < 3:
        raise ErroCalculo(
            codigo="CURVA_HQ_INVALIDA",
            mensagem=f"Curva HxQ da bomba deve conter no mínimo 3 pontos (fornecidos: {len(Q_m3h)}).",
            campo="curva_hq"
        )

    # Validação de monotonicidade decrescente em H
    for i in range(1, len(H_m)):
        if H_m[i] >= H_m[i - 1]:
            raise ErroCalculo(
                codigo="CURVA_HQ_H_INVALIDO",
                mensagem="Altura manométrica H da curva de bomba deve ser monotonicamente decrescente com a vazão Q.",
                campo="curva_hq"
            )

    Q_arr = np.array(Q_m3h, dtype=float)
    H_arr = np.array(H_m, dtype=float)

    Q_min = float(np.min(Q_arr))
    Q_max = float(np.max(Q_arr))
    H_min = float(np.min(H_arr))
    H_max = float(np.max(H_arr))

    interp_hq = PchipInterpolator(Q_arr, H_arr)

    interp_eta = None
    Q_bep = (Q_min + Q_max) / 2.0
    if eta_pct is not None and len(eta_pct) == len(Q_m3h):
        eta_arr = np.array(eta_pct, dtype=float)
        interp_eta = PchipInterpolator(Q_arr, eta_arr)
        # BEP é o ponto de maior eficiência
        idx_bep = int(np.argmax(eta_arr))
        Q_bep = float(Q_arr[idx_bep])

    interp_npsh = None
    if npsh_m is not None and len(npsh_m) == len(Q_m3h):
        npsh_arr = np.array(npsh_m, dtype=float)
        interp_npsh = PchipInterpolator(Q_arr, npsh_arr)

    env_valido = verificar_envelope(interp_hq, Q_min, Q_max, H_min, H_max)

    return CurvasBombaInterpoladas(
        Q_min_m3h=Q_min,
        Q_max_m3h=Q_max,
        H_min_m=H_min,
        H_max_m=H_max,
        interp_hq=interp_hq,
        interp_eta=interp_eta,
        interp_npsh=interp_npsh,
        envelope_valido=env_valido,
        Q_bep_m3h=Q_bep
    )
