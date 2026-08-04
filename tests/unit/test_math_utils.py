import pytest
import numpy as np
from app.utils.math_utils import (
    criar_interpolador_pchip,
    verificar_envelope,
    bissecao,
    newton_raphson
)

def test_pchip_monotonicidade_e_envelope():
    """T1.11 — PCHIP: monotonicidade e envelope"""
    Q_points = [0, 50, 100, 150, 180]
    H_points = [42, 40, 36, 28, 18]

    interp = criar_interpolador_pchip(Q_points, H_points)

    assert interp(0) == pytest.approx(42, abs=1e-5)
    assert interp(180) == pytest.approx(18, abs=1e-5)
    assert verificar_envelope(interp, 0, 180, 18, 42, n=1000) is True

    Q_flat = [0, 50, 100, 150, 180]
    H_flat = [42, 41.8, 36, 28, 18]
    interp_flat = criar_interpolador_pchip(Q_flat, H_flat)
    assert verificar_envelope(interp_flat, 0, 180, 18, 42, n=1000) is True

    H_25 = interp_flat(25)
    assert 41.8 <= H_25 <= 42.0

def test_bissecao_raiz():
    """Testa busca de raiz via bisseção para função simples."""
    f = lambda x: x**2 - 4
    raiz, iteracoes, convergiu = bissecao(f, 0, 5, tol=1e-6, max_iter=100)
    assert convergiu is True
    assert raiz == pytest.approx(2.0, abs=1e-5)

    # Teste f(a)*f(b) > 0
    _, _, convergiu_fa_fb = bissecao(f, 3, 5)
    assert convergiu_fa_fb is False

    # Teste não convergência (max_iter pequeno)
    _, _, convergiu_limite = bissecao(f, 0, 5, tol=1e-15, max_iter=1)
    assert convergiu_limite is False

def test_newton_raphson():
    """Testa busca de raiz via Newton-Raphson."""
    f = lambda x: x**2 - 4
    df = lambda x: 2 * x
    raiz, iteracoes, convergiu = newton_raphson(f, df, x0=3.0, tol=1e-6, max_iter=100)
    assert convergiu is True
    assert raiz == pytest.approx(2.0, abs=1e-5)

    # Derivada nula
    _, _, convergiu_der_zero = newton_raphson(f, lambda x: 0.0, x0=3.0)
    assert convergiu_der_zero is False

    # Não convergiu em max_iter
    _, _, convergiu_max_iter = newton_raphson(f, df, x0=3.0, tol=1e-15, max_iter=1)
    assert convergiu_max_iter is False
