import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_t10_4_endpoint_materiais():
    """T10.4 — GET /api/v1/materiais: lista bibliotecas de materiais"""
    res = client.get("/api/v1/materiais")
    assert res.status_code == 200
    data = res.json()

    assert len(data) >= 8
    materiais_ids = [m["id"] for m in data]
    assert "aco_inox_304" in materiais_ids

    aco_inox = next(m for m in data if m["id"] == "aco_inox_304")
    assert 0.015 <= aco_inox["rugosidade_mm"] <= 0.025

def test_t10_4_endpoint_singularidades():
    """T10.4 — GET /api/v1/singularidades/biblioteca: lista biblioteca de singularidades"""
    res = client.get("/api/v1/singularidades/biblioteca")
    assert res.status_code == 200
    data = res.json()

    assert "curva_90_rl" in data
    curva = data["curva_90_rl"]
    assert curva["K"] == 0.6
    assert curva["Le_sobre_D"] == 16
