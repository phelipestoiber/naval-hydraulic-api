# 💻 Guia dos Desenvolvedores e Integração de API

**Naval Hydraulic Calculator API** — Manual de Arquitetura, Contratos REST e Guia de Integração.

Este documento destina-se a Desenvolvedores Backend, Desenvolvedores Frontend, Engenheiros de DevOps e Integradores de Sistemas que desejam consumir ou estender a API REST.

---

## 📋 Sumário

1. [Arquitetura de Software e Guardrails](#1-arquitetura-de-software-e-guardrails)
2. [Catálogo de Endpoints REST](#2-catálogo-de-endpoints-rest)
3. [Anatomia dos Payloads JSON (Entrada e Saída)](#3-anatomia-dos-payloads-json-entrada-e-saída)
4. [Tratamento de Erros e ErrorResponse](#4-tratamento-de-erros-e-errorresponse)
5. [Exemplos Práticos de Integração (Multilinguagem)](#5-exemplos-práticos-de-integração-multilinguagem)
6. [Deployment, Docker e Configurações](#6-deployment-docker-e-configurações)

---

## 1. Arquitetura de Software e Guardrails

O sistema segue uma arquitetura em camadas rígida para garantir testabilidade, independência de frameworks e manutenibilidade.

```
naval-hydraulic-api/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/     <-- Routers FastAPI HTTP (borda)
│   │       └── router.py      <-- Agregador de rotas /api/v1
│   ├── core/                  <-- Núcleo hidráulico e naval (PURO)
│   │   ├── bombas/            <-- PCHIP, BEP, Ns, Ponto de Operação
│   │   ├── cavitacao/         <-- NPSH, Pressão de Vapor, Margem
│   │   ├── fluidos/           <-- Andrade, Walther, Reynolds
│   │   ├── motores/           <-- Potências, Consumo Diesel, VFD
│   │   ├── naval/             <-- 3D Sweep 9 Condições, Normas, Redundância
│   │   ├── perda_carga/       <-- Darcy-Weisbach, Churchill, Singularidades
│   │   ├── pipeline.py        <-- Engine Integrador de Cálculo (Camadas 1-6)
│   │   └── unit_casting.py    <-- Fronteira Dimensional Única (Eng -> SI)
│   ├── data/                  <-- JSONs estáticos (materiais, K, classificadoras)
│   ├── db/                    <-- Persistência em memória (UUID v4)
│   ├── schemas/               <-- DTOs Pydantic v2 (Input/Output validation)
│   └── main.py                <-- Instância FastAPI, Cors, Exception Handlers
└── tests/
    ├── api/                   <-- Testes de Endpoints HTTP REST (TestClient)
    ├── integration/           <-- Testes de Integração de Pipeline e DB
    └── unit/                  <-- Testes Unitários dos módulos de core/
```

### 🛡️ Guardrails Inegociáveis do Projeto:
1. **Isolamento Total do `app/core/`**: É estritamente proibido importar `fastapi`, `pydantic`, `sqlalchemy` ou `httpx` dentro de qualquer módulo em `app/core/`. As funções da camada core recebem e retornam puramente dicionários ou dataclasses nativos em unidades SI.
2. **Fronteira Dimensional Única (`unit_casting.py`)**: Nenhuma conversão de unidade de engenharia (`m3h`, `bar`, `mm`, `°C`) pode ocorrer dentro dos módulos de cálculo. Todas as conversões acontecem exclusivamente na entrada em `unit_casting.py`.
3. **Persistência Imutável em Dicionário (`app/db/`)**: Cada cálculo concluído no pipeline gera um UUID v4 de 36 caracteres e grava o resultado imutável no repositório `app/db/database.py`.

---

## 2. Catálogo de Endpoints REST

Todas as rotas estão prefixadas sob `/api/v1`.

| Método | Endpoint | Descrição | Status Sucesso |
|---|---|---|---|
| `POST` | `/api/v1/calcular` | Executa o pipeline de cálculo integrado de ponta a ponta (Camadas 1-6) e gera UUID v4 | `200 OK` |
| `GET` | `/api/v1/resultado/{id_calculo}` | Recupera o resultado completo de um cálculo gravado previamente por seu UUID | `200 OK` |
| `GET` | `/api/v1/materiais` | Retorna a biblioteca completa de materiais e suas rugosidades absolutas ($\text{mm}$) | `200 OK` |
| `GET` | `/api/v1/singularidades/biblioteca` | Retorna a biblioteca de coeficientes $K$ e $L_e/D$ para acessórios e válvulas | `200 OK` |
| `POST` | `/api/v1/fluidos/propriedades` | Cálculo isolado de densidade, viscosidade, vazão e regime de escoamento | `200 OK` |
| `POST` | `/api/v1/perda-carga/darcy-weisbach` | Cálculo isolado de perda distribuída por Darcy-Weisbach | `200 OK` |
| `POST` | `/api/v1/perda-carga/hazen-williams` | Cálculo por Hazen-Williams com verificação de travas e fallback automático | `200 OK` |
| `POST` | `/api/v1/perda-carga/singularidades` | Cálculo isolado de perdas localizadas (métodos $K$ ou $L_e/D$) | `200 OK` |
| `POST` | `/api/v1/bombas/ponto-operacao` | Interpolação PCHIP da bomba e determinação do ponto de operação | `200 OK` |
| `POST` | `/api/v1/cavitacao/npsh` | Cálculo isolado de NPSH disponível e temperatura crítica de cavitação | `200 OK` |
| `POST` | `/api/v1/motores/dimensionamento` | Dimensionamento de potências, corrente nominal trifásica e seleção ABNT | `200 OK` |
| `GET` | `/health` | Health check do serviço e versão ativa | `200 OK` |

---

## 3. Anatomia dos Payloads JSON (Entrada e Saída)

### 3.1 Payload Completo de Entrada (`POST /api/v1/calcular`)

```json
{
  "projeto": {
    "nome": "Sistema de Resfriamento — ME Principal",
    "navio": "MV Example",
    "classificadora": "BV",
    "norma": "NR467",
    "revisao": "0"
  },
  "fluido": {
    "tipo": "agua_salgada",
    "nome": "Água do mar",
    "temperatura_C": 32,
    "densidade_kg_m3": 1025,
    "viscosidade_dinamica_Pa_s": 0.001,
    "pressao_vapor_Pa": 4800,
    "modelo_viscosidade": "andrade"
  },
  "sistema": {
    "unidade_vazao": "m3h",
    "vazao": 118.5,
    "pressao_succao_Pa": 101325,
    "pressao_descarga_Pa": 101325,
    "pressao_atm_Pa": 101325,
    "altitude_m": 0,
    "pontos_sistema": {
      "succao":   {"x_m": -12.5, "y_m": 1.2, "z_m": 0.8},
      "bomba":    {"x_m": -11.0, "y_m": 1.2, "z_m": 1.5},
      "descarga": {"x_m":   5.0, "y_m": 1.2, "z_m": 4.2}
    },
    "condicoes_inclinacao": "BV_operacao_e_avaria",
    "sistema_essencial": true,
    "numero_bombas": 2,
    "alimentacoes_independentes": true
  },
  "trechos": [
    {
      "id": "S1",
      "descricao": "Sucção — kingston a bomba",
      "diametro_interno_mm": 150,
      "comprimento_m": 8.5,
      "material": "aco_inox_304",
      "rugosidade_mm": 0.02,
      "perda_equipamento_m": 3.62,
      "metodo_perda": "darcy_weisbach",
      "singularidades": [
        {"tipo": "valvula_gaveta",   "quantidade": 1},
        {"tipo": "curva_90_rl",      "quantidade": 2},
        {"tipo": "valvula_retencao", "quantidade": 1}
      ]
    },
    {
      "id": "D1",
      "descricao": "Descarga — bomba ao resfriador",
      "diametro_interno_mm": 125,
      "comprimento_m": 15.2,
      "material": "aco_inox_304",
      "rugosidade_mm": 0.02,
      "metodo_perda": "darcy_weisbach",
      "singularidades": [
        {"tipo": "curva_90_rl",         "quantidade": 3},
        {"tipo": "tee_passagem_direta", "quantidade": 1}
      ]
    }
  ],
  "bomba": {
    "fabricante": "Grundfos",
    "modelo": "NK 100-315",
    "rotacao_rpm": 1450,
    "metodo_margem_npsh": "combinado",
    "curva_hq": [
      {"Q_m3h": 0, "H_m": 42},
      {"Q_m3h": 50, "H_m": 40},
      {"Q_m3h": 118.5, "H_m": 36},
      {"Q_m3h": 150, "H_m": 28},
      {"Q_m3h": 180, "H_m": 18}
    ],
    "curva_npsh": [
      {"Q_m3h": 0, "NPSH_m": 1.5},
      {"Q_m3h": 50, "NPSH_m": 2.0},
      {"Q_m3h": 118.5, "NPSH_m": 3.2},
      {"Q_m3h": 150, "NPSH_m": 4.5},
      {"Q_m3h": 180, "NPSH_m": 6.5}
    ],
    "curva_eta": [
      {"Q_m3h": 0, "eta_pct": 0},
      {"Q_m3h": 50, "eta_pct": 55},
      {"Q_m3h": 118.5, "eta_pct": 79},
      {"Q_m3h": 150, "eta_pct": 75},
      {"Q_m3h": 180, "eta_pct": 60}
    ]
  }
}
```

---

### 3.2 Payload Completo de Resposta (`200 OK`)

```json
{
  "id_calculo": "e83b48f9-467a-4c28-98e3-85f6e80b2a8d",
  "status": "OK",
  "condicoes_reprovadas": [],
  "resultados_prumo": {
    "velocidade_succao_m_s": 1.87,
    "velocidade_descarga_m_s": 2.69,
    "reynolds_succao": 287000.0,
    "alpha_cinetico_succao": 1.0,
    "h_geo_m": 3.4,
    "altura_manometrica_m": 8.45,
    "npsh_disponivel_m": 4.85,
    "velocidade_especifica_ns": 63.7,
    "tipo_bomba": "centrifuga_mista",
    "motor_selecionado_cv": 7.5,
    "status_npsh": "OK",
    "status_bep": "OK"
  },
  "condicao_critica": {
    "condicao": "avaria_BB",
    "theta_deg": 10.0,
    "phi_deg": 22.5,
    "npsh_disponivel_m": 4.43,
    "aprovado": true
  },
  "varredura": [
    {"condicao": "prumo", "theta_deg": 0.0, "phi_deg": 0.0, "npsh_disponivel_m": 4.85, "aprovado": true},
    {"condicao": "caturro_vante", "theta_deg": 5.0, "phi_deg": 0.0, "npsh_disponivel_m": 4.75, "aprovado": true},
    {"condicao": "caturro_re", "theta_deg": -5.0, "phi_deg": 0.0, "npsh_disponivel_m": 4.90, "aprovado": true},
    {"condicao": "banda_BE", "theta_deg": 0.0, "phi_deg": 15.0, "npsh_disponivel_m": 4.65, "aprovado": true},
    {"condicao": "banda_BB", "theta_deg": 0.0, "phi_deg": -15.0, "npsh_disponivel_m": 4.60, "aprovado": true},
    {"condicao": "combinado_BE_vante", "theta_deg": 5.0, "phi_deg": 15.0, "npsh_disponivel_m": 4.57, "aprovado": true},
    {"condicao": "combinado_BB_re", "theta_deg": -5.0, "phi_deg": -15.0, "npsh_disponivel_m": 4.55, "aprovado": true},
    {"condicao": "avaria_BE", "theta_deg": 5.0, "phi_deg": 22.5, "npsh_disponivel_m": 4.47, "aprovado": true},
    {"condicao": "avaria_BB", "theta_deg": 10.0, "phi_deg": 22.5, "npsh_disponivel_m": 4.43, "aprovado": true}
  ],
  "rastreabilidade_unidades": [
    {"campo": "vazao", "valor_entrada": 118.5, "unidade_entrada": "m3h", "valor_si": 0.03291666666666667, "unidade_si": "m3/s", "fator": "/ 3600"},
    {"campo": "diametro", "valor_entrada": 150.0, "unidade_entrada": "mm", "valor_si": 0.15, "unidade_si": "m", "fator": "/ 1000"},
    {"campo": "temperatura", "valor_entrada": 32.0, "unidade_entrada": "°C", "valor_si": 305.15, "unidade_si": "K", "fator": "+ 273,15"}
  ],
  "alertas": []
}
```

---

## 4. Tratamento de Erros e ErrorResponse

Todos os erros retornados pela API utilizam o schema `ErrorResponse` com o campo estruturado `codigo`.

### 4.1 Tabela de Códigos de Erro Estruturados

| Código de Erro | HTTP Status | Causa / Descrição |
|---|---|---|
| `TOPOLOGIA_MALHA_NAO_SUPORTADA` | `422 Unprocessable Entity` | Trechos contêm ciclos/loops em malha fechada |
| `VAZAO_NEGATIVA` | `422 Unprocessable Entity` | Parâmetro de vazão $Q < 0$ |
| `TEMPERATURA_FORA_DO_RANGE` | `422 Unprocessable Entity` | Temperatura em Kelvin $< 273.15 \text{ K}$ |
| `UNIDADE_INVALIDA` | `422 Unprocessable Entity` | Unidade de engenharia não reconhecida |
| `CURVA_HQ_INVALIDA` | `422 Unprocessable Entity` | Curva H×Q fornecida possui menos de 3 pontos |
| `CURVA_HQ_H_INVALIDO` | `422 Unprocessable Entity` | Curva H×Q não é monotonicamente decrescente em H |
| `SEM_PONTO_OPERACAO_SHUT_OFF` | `400 Bad Request` | $H_{\text{shut-off}} < H_{\text{geo}}$ (Inclui `dados_diagnostico.deficit_m`) |
| `SEM_PONTO_OPERACAO_FORA_CURVA` | `400 Bad Request` | Ponto de operação excede $Q_{\text{max}}$ da curva |
| `RESULTADO_NAO_ENCONTRADO` | `404 Not Found` | UUID v4 não localizado na base em memória |
| `ERRO_VALIDACAO` | `422 Unprocessable Entity` | Falha de validação nos tipos dos campos Pydantic |
| `ERRO_INTERNO` | `500 Internal Server Error` | Exceção inesperada interceptada pelo middleware |

### 4.2 Estrutura do JSON de Erro

```json
{
  "codigo": "SEM_PONTO_OPERACAO_SHUT_OFF",
  "mensagem": "H_shut_off (42.00 m) < H_sistema_Q0 (49.20 m) — bomba não vence a cota estática.",
  "dados_diagnostico": {
    "H_shut_off_m": 42.0,
    "H_sistema_Q0_m": 49.2,
    "deficit_m": 7.2
  },
  "campo": "bomba"
}
```

---

## 5. Exemplos Práticos de Integração (Multilinguagem)

### 5.1 Python (`httpx` / `requests`)

```python
import httpx

payload = {
    "sistema": {"unidade_vazao": "m3h", "vazao": 118.5},
    "fluido": {"tipo": "agua_salgada", "temperatura_C": 32},
    "bomba": {
        "rotacao_rpm": 1450,
        "curva_hq": [
            {"Q_m3h": 0, "H_m": 42},
            {"Q_m3h": 118.5, "H_m": 36},
            {"Q_m3h": 180, "H_m": 18}
        ]
    }
}

response = httpx.post("http://localhost:8000/api/v1/calcular", json=payload)

if response.status_code == 200:
    data = response.json()
    print(f"Cálculo concluído! UUID: {data['id_calculo']}")
    print(f"Status Naval: {data['status']}")
    print(f"Motor ABNT: {data['resultados_prumo']['motor_selecionado_cv']} CV")
else:
    erro = response.json()
    print(f"Erro [{erro.get('codigo')}]: {erro.get('mensagem')}")
```

### 5.2 JavaScript / TypeScript (Node.js / Browser `fetch`)

```typescript
async function calcularHidraulicaNaval() {
  const response = await fetch("http://localhost:8000/api/v1/calcular", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      sistema: { vazao: 118.5, unidade_vazao: "m3h" },
      bomba: {
        rotacao_rpm: 1450,
        curva_hq: [
          { Q_m3h: 0, H_m: 42 },
          { Q_m3h: 118.5, H_m: 36 },
          { Q_m3h: 180, H_m: 18 }
        ]
      }
    })
  });

  if (!response.ok) {
    const errorData = await response.json();
    console.error("Erro na API:", errorData.codigo, errorData.mensagem);
    return;
  }

  const result = await response.json();
  console.log("ID do Cálculo:", result.id_calculo);
  console.log("NPSHd em Prumo:", result.resultados_prumo.npsh_disponivel_m, "m");
}
```

---

## 6. Deployment, Docker e Configurações

### 6.1 Execução com Docker Container

O projeto está pronto para empacotamento em container minimalista de produção com Python 3.11/3.13:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml .
RUN pip install --no-cache-dir .

COPY app/ ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 6.2 Variáveis de Ambiente

| Variável | Valor Padrão | Descrição |
|---|---|---|
| `APP_ENV` | `production` | Ambiente de execução (`development`, `production`) |
| `APP_DEBUG` | `false` | Se `true`, inclui a stack trace completa nos erros 500 |
| `PORT` | `8000` | Porta HTTP do servidor Uvicorn |
| `CORS_ORIGINS` | `*` | Origens permitidas para requisições cross-origin |
