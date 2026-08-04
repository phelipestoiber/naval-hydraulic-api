from typing import Callable
import numpy as np
from scipy.interpolate import PchipInterpolator

def criar_interpolador_pchip(x: list[float] | np.ndarray, y: list[float] | np.ndarray) -> PchipInterpolator:
    """
    Cria e retorna um interpolador PCHIP (Piecewise Cubic Hermite Interpolating Polynomial).
    Garante monotonicidade local e previne overshoot físico em curvas de bomba.
    """
    return PchipInterpolator(x, y)

def verificar_envelope(interp: PchipInterpolator, Q_min: float, Q_max: float, H_min: float, H_max: float, n: int = 1000) -> bool:
    """
    Verifica se a interpolação H(Q) permanece estritamente dentro do envelope [H_min, H_max]
    para n pontos no intervalo [Q_min, Q_max].
    """
    Q_test = np.linspace(Q_min, Q_max, n)
    H_test = interp(Q_test)
    return bool(np.all(H_test >= H_min - 1e-9) and np.all(H_test <= H_max + 1e-9))

def bissecao(f: Callable[[float], float], a: float, b: float, tol: float = 1e-4, max_iter: int = 100) -> tuple[float, int, bool]:
    """
    Busca de raiz pelo método da bisseção.
    Retorna (raiz, iteracoes, convergiu).
    """
    fa = f(a)
    fb = f(b)
    if fa * fb > 0:
        return (a, 0, False)

    c = a
    for i in range(1, max_iter + 1):
        c = (a + b) / 2.0
        fc = f(c)
        if abs(fc) < tol or (b - a) / 2.0 < tol:
            return (c, i, True)

        if fa * fc < 0:
            b = c
            fb = fc
        else:
            a = c
            fa = fc

    return (c, max_iter, False)

def newton_raphson(f: Callable[[float], float], df: Callable[[float], float], x0: float, tol: float = 1e-4, max_iter: int = 100) -> tuple[float, int, bool]:
    """
    Busca de raiz pelo método de Newton-Raphson.
    Retorna (raiz, iteracoes, convergiu).
    """
    x = x0
    for i in range(1, max_iter + 1):
        der = df(x)
        if abs(der) < 1e-12:
            return (x, i, False)
        x_next = x - f(x) / der
        if abs(x_next - x) < tol or abs(f(x_next)) < tol:
            return (x_next, i, True)
        x = x_next
    return (x, max_iter, False)
