from app.core.cavitacao.npsh import calcular_npsha
from app.utils.math_utils import bissecao

def calcular_temperatura_critica_cavitacao(
    p_atm_pa: float,
    z_suc_m: float,
    hf_suc_m: float,
    npshr_m: float,
    rho_kgm3: float = 1000.0,
    g: float = 9.81,
    tol: float = 1e-3,
    max_iter: int = 50
) -> float:
    """
    Calcula a temperatura crítica de cavitação T_crit [°C] na qual NPSHa(T_crit) = NPSHr.
    Utiliza o método da bisseção no intervalo [0, 95] °C.
    """
    def obj_fn(temp_c: float) -> float:
        npsha = calcular_npsha(
            p_atm_pa=p_atm_pa,
            temp_c=temp_c,
            z_suc_m=z_suc_m,
            hf_suc_m=hf_suc_m,
            rho_kgm3=rho_kgm3,
            g=g
        )
        return npsha - npshr_m

    T_crit, _, convergiu = bissecao(obj_fn, a=0.0, b=95.0, tol=tol, max_iter=max_iter)
    if not convergiu:
        return 95.0
    return T_crit
