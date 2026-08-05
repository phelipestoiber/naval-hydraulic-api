import math

def calcular_fator_atrito_poiseuille(Re: float) -> float:
    """
    Calcula o fator de atrito para escoamento laminar (Poiseuille):
    f = 64 / Re
    """
    if Re <= 0:
        raise ValueError("Número de Reynolds deve ser estritamente positivo.")
    return 64.0 / Re

def calcular_fator_atrito_churchill(Re: float, epsilon_sobre_d: float) -> float:
    """
    Calcula o fator de atrito pela equação de Churchill (1977).
    Válido para todos os regimes sem necessidade de condicionais de regime.
    f = 8 * [ (8/Re)^12 + (A + B)^(-1.5) ]^(1/12)
    """
    if Re <= 0:
        raise ValueError("Número de Reynolds deve ser estritamente positivo.")

    # A = { -2.457 * ln[ (7/Re)^0.9 + 0.27 * (epsilon/D) ] }^16
    termo_a_inner = (7.0 / Re)**0.9 + 0.27 * epsilon_sobre_d
    if termo_a_inner <= 0:
        termo_a_inner = 1e-15
    A = (-2.457 * math.log(termo_a_inner))**16

    # B = (37530 / Re)^16
    B = (37530.0 / Re)**16

    f = 8.0 * ((8.0 / Re)**12 + (A + B)**(-1.5))**(1.0 / 12.0)
    return f

def calcular_fator_atrito_colebrook(Re: float, epsilon_sobre_d: float, f0: float = 0.02, tol: float = 1e-6, max_iter: int = 50) -> tuple[float, int]:
    """
    Calcula o fator de atrito pela equação de Colebrook-White iterativa.
    1/sqrt(f) = -2 * log10( (epsilon/D)/3.71 + 2.51/(Re * sqrt(f)) )
    Retorna (f, iteracoes).
    """
    if Re < 2300:
        return (calcular_fator_atrito_poiseuille(Re), 1)

    f = f0
    for i in range(1, max_iter + 1):
        if f <= 0:
            f = 1e-6
        sqrt_f = math.sqrt(f)
        arg = (epsilon_sobre_d / 3.71) + (2.51 / (Re * sqrt_f))
        if arg <= 0:
            arg = 1e-15
        inv_sqrt_f = -2.0 * math.log10(arg)
        f_next = 1.0 / (inv_sqrt_f**2)

        if abs(f_next - f) < tol:
            return (f_next, i)
        f = f_next

    return (f, max_iter)

def calcular_fator_atrito_swamee_jain(Re: float, epsilon_sobre_d: float) -> float:
    """
    Calcula o fator de atrito pela equação explícita de Swamee-Jain (1976).
    f = 0.25 / [ log10( (epsilon/D)/3.71 + 5.74 / Re^0.9 ) ]^2
    """
    if Re < 2300:
        return calcular_fator_atrito_poiseuille(Re)

    arg = (epsilon_sobre_d / 3.71) + (5.74 / (Re**0.9))
    f = 0.25 / (math.log10(arg)**2)
    return f

def calcular_fator_atrito_haaland(Re: float, epsilon_sobre_d: float) -> tuple[float, str | None]:
    """
    Calcula o fator de atrito pela equação explícita de Haaland (1983).
    1/sqrt(f) = -1.8 * log10[ ((epsilon/D)/3.7)^1.11 + 6.9/Re ]
    Validade: 4.000 < Re < 10^8; 0 <= epsilon/D <= 0.05.
    Se fora da faixa, retorna (f_fallback, mensagem_aviso).
    """
    aviso = None

    if Re <= 4000:
        aviso = f"Haaland fora da faixa de validade (Re={Re} <= 4000). Usando fallback Poiseuille/Colebrook."
        if Re < 2300:
            return (calcular_fator_atrito_poiseuille(Re), aviso)

    if epsilon_sobre_d > 0.05 or Re > 1e8:
        aviso = f"Haaland fora da faixa de validade (ed={epsilon_sobre_d}, Re={Re}). Usando fallback Colebrook."
        f_col, _ = calcular_fator_atrito_colebrook(Re, epsilon_sobre_d)
        return (f_col, aviso)

    arg = ((epsilon_sobre_d / 3.7)**1.11) + (6.9 / Re)
    if arg <= 0:
        arg = 1e-15
    inv_sqrt_f = -1.8 * math.log10(arg)
    f = 1.0 / (inv_sqrt_f**2)
    return (f, aviso)

def calcular_fator_atrito(Re: float, epsilon_sobre_d: float, metodo: str = "churchill") -> float:
    """
    Função genérica de entrada para cálculo do fator de atrito f.
    Suporta os métodos: 'churchill' (padrão), 'colebrook', 'swamee_jain', 'haaland', 'poiseuille'.
    """
    if Re < 2300:
        return calcular_fator_atrito_poiseuille(Re)

    metodo_norm = metodo.lower()
    if metodo_norm == "churchill":
        return calcular_fator_atrito_churchill(Re, epsilon_sobre_d)
    elif metodo_norm == "colebrook":
        f, _ = calcular_fator_atrito_colebrook(Re, epsilon_sobre_d)
        return f
    elif metodo_norm == "swamee_jain":
        return calcular_fator_atrito_swamee_jain(Re, epsilon_sobre_d)
    elif metodo_norm == "haaland":
        f, _ = calcular_fator_atrito_haaland(Re, epsilon_sobre_d)
        return f
    elif metodo_norm == "poiseuille":
        return calcular_fator_atrito_poiseuille(Re)
    else:
        return calcular_fator_atrito_churchill(Re, epsilon_sobre_d)
