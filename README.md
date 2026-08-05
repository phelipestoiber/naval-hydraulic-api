# ⚓ Naval Hydraulic Calculator API

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![Tests](https://img.shields.io/badge/tests-85%20passed-brightgreen.svg)]()
[![Coverage](https://img.shields.io/badge/coverage-98%25-brightgreen.svg)]()
[![License](https://img.shields.io/badge/license-MIT-blue.svg)]()

Motor de cálculo hidráulico e dimensionamento eletromecânico de plantas de bombeamento navais, com varredura espacial 3D de inclinação estática/dinâmica (prumo, caturro, banda, avaria), verificação de normas de sociedades classificadoras (BV, LR, ABS) e API REST pública baseada em FastAPI.

---

## 🗺️ Guias de Documentação Especializados

Para melhor atender às necessidades de cada área profissional, a documentação foi organizada em **dois manuais técnicos dedicados**:

```
│
├── 👷 Guia de Engenharia Naval e Hidráulica  ──> docs/GUIA_ENGENHARIA_NAVAL.md
└── 💻 Guia de Desenvolvedores e API REST     ──> docs/GUIA_DESENVOLVEDORES_API.md
```

| O que você procura? | Documento Indicado |
|---|---|
| Equações de viscosidade, Reynolds, Darcy-Weisbach, Churchill e Hazen-Williams | [Guia de Engenharia Naval](docs/GUIA_ENGENHARIA_NAVAL.md#1-fundamentação-hidráulica-e-propriedades-dos-fluidos) |
| As 9 condições de inclinação 3D, matrizes de rotação $R(\theta,\phi)$ e avaria crítica | [Guia de Engenharia Naval](docs/GUIA_ENGENHARIA_NAVAL.md#4-engenharia-naval-geometria-3d-inclinação-e-regras-de-classe) |
| Interpolação PCHIP vs CubicSpline, NPSHa, BEP, Ns e limites de classe (BV/LR/ABS) | [Guia de Engenharia Naval](docs/GUIA_ENGENHARIA_NAVAL.md#3-bombas-centrífugas-ponto-de-operação-e-cavitação) |
| Endpoints HTTP REST, Schemas JSON de Entrada/Saída e UUID v4 | [Guia de Desenvolvedores API](docs/GUIA_DESENVOLVEDORES_API.md#2-catálogo-de-endpoints-rest) |
| Tabela de Códigos de Erro Estruturados (`ErrorResponse` 400/422/500) | [Guia de Desenvolvedores API](docs/GUIA_DESENVOLVEDORES_API.md#4-tratamento-de-erros-e-errorresponse) |
| Exemplos de código em Python, JavaScript/TypeScript, cURL e Docker | [Guia de Desenvolvedores API](docs/GUIA_DESENVOLVEDORES_API.md#5-exemplos-práticos-de-integração-multilinguagem) |

---

## 🚀 Inicio Rápido (Quickstart)

### 1. Clonar e Instalar

```bash
# Clonar o repositório
git clone https://github.com/seu-usuario/naval-hydraulic-api.git
cd naval-hydraulic-api

# Criar ambiente virtual
python -m venv .venv
source .venv/bin/activate  # No Windows: .venv\Scripts\activate

# Instalar dependências
pip install -r pyproject.toml
```

### 2. Executar o Servidor de API

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Acesse a documentação interativa Swagger no navegador:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### 3. Executar a Suíte de Testes

```bash
pytest --cov=app --cov-report=term-missing
```

---

## 💡 Exemplo Rápido de Uso (cURL)

```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/calcular' \
  -H 'Content-Type: application/json' \
  -d '{
  "projeto": {
    "nome": "Sistema de Resfriamento — ME Principal",
    "navio": "MV Example",
    "classificadora": "BV"
  },
  "fluido": {
    "tipo": "agua_salgada",
    "temperatura_C": 32,
    "densidade_kg_m3": 1025,
    "viscosidade_dinamica_Pa_s": 0.001
  },
  "sistema": {
    "unidade_vazao": "m3h",
    "vazao": 118.5,
    "pontos_sistema": {
      "succao": {"z_m": 0.8},
      "bomba": {"z_m": 1.5},
      "descarga": {"z_m": 4.2}
    }
  },
  "bomba": {
    "rotacao_rpm": 1450,
    "curva_hq": [
      {"Q_m3h": 0, "H_m": 42},
      {"Q_m3h": 50, "H_m": 40},
      {"Q_m3h": 118.5, "H_m": 36},
      {"Q_m3h": 150, "H_m": 28},
      {"Q_m3h": 180, "H_m": 18}
    ]
  }
}'
```

### Resposta Resumida:

```json
{
  "id_calculo": "e83b48f9-467a-4c28-98e3-85f6e80b2a8d",
  "status": "OK",
  "resultados_prumo": {
    "velocidade_succao_m_s": 1.87,
    "velocidade_descarga_m_s": 2.69,
    "reynolds_succao": 287000.0,
    "h_geo_m": 3.4,
    "altura_manometrica_m": 8.45,
    "npsh_disponivel_m": 4.85,
    "velocidade_especifica_ns": 63.7,
    "tipo_bomba": "centrifuga_mista",
    "motor_selecionado_cv": 7.5
  }
}
```

---

## 📁 Estrutura da Base de Código

```
naval-hydraulic-api/
├── app/
│   ├── api/v1/endpoints/   # Routers de borda da API REST (FastAPI)
│   ├── core/               # Núcleo hidráulico e naval (PURO em Python/Dataclasses)
│   ├── data/               # Bibliotecas de materiais, singularidades K e normas
│   ├── db/                 # Repositório em memória com UUID v4
│   ├── schemas/            # DTOs Pydantic v2
│   └── main.py             # Instância FastAPI e exception handlers
├── docs/
│   ├── GUIA_ENGENHARIA_NAVAL.md    # Manual detalhado de equações e normas navais
│   └── GUIA_DESENVOLVEDORES_API.md # Manual detalhado de integração REST
├── tests/                  # 85 testes automatizados (unitários, integração e API)
└── README.md
```

---

## 📄 Licença

Este projeto é distribuído sob a licença **MIT**. Veja o arquivo `LICENSE` para mais detalhes.
