# 💻 Guia Avançado de Desenvolvedores e Integração REST

**Naval Hydraulic Calculator API** — Manual Técnico de Arquitetura, Especificação OpenAPI/REST, DTOs e Guia de Integração.

---

## 📋 Sumário

1. [Visão Geral da Arquitetura e Princípios de Design](#1-visão-geral-da-arquitetura-e-princípios-de-design)
2. [Guardrails Arquiteturais Inegociáveis](#2-guardrails-arquiteturais-inegociáveis)
3. [Especificação Detalhada dos Endpoints REST](#3-especificação-detalhada-dos-endpoints-rest)
4. [Anatomia dos Payloads JSON (Entrada e Saída)](#4-anatomia-dos-payloads-json-entrada-e-saída)
5. [Sistema Integrado de Erros (`ErrorResponse`)](#5-sistema-integrado-de-erros-errorresponse)
6. [Exemplos Práticos de Integração Multilinguagem](#6-exemplos-práticos-de-integração-multilinguagem)
7. [Guia de Contribuição, Testes e Expansão](#7-guia-de-contribuição-testes-e-expansão)
8. [Deploy, Docker e Variáveis de Ambiente](#8-deploy-docker-e-variáveis-de-ambiente)

---

## 1. Visão Geral da Arquitetura e Princípios de Design

A **Naval Hydraulic Calculator API** adota uma **Arquitetura Limpa (Clean Architecture / Hexagonal Architecture)** em Python, projetada para desacoplar totalmente o motor de cálculo das camadas de framework web ou persistência.

```
                                 ┌─────────────────────────────────┐
                                 │     Cliente HTTP (Web/App)      │
                                 └────────────────┬────────────────┘
                                                  │
                                                  ▼
 ┌─────────────────────────────────────────────────────────────────────────────────┐
 │ CAMADA DE BORDA (FastAPI & Pydantic v2)                                         │
 │   app/api/v1/endpoints/  --> Routers HTTP (validação de schemas e HTTP status)│
 │   app/schemas/           --> DTOs com @field_validator                          │
 └────────────────────────────────────────┬────────────────────────────────────────┘
                                          │
                                          ▼
 ┌─────────────────────────────────────────────────────────────────────────────────┐
 │ CAMADA DE CASTEAMENTO DIMENSIONAL                                               │
 │   app/core/unit_casting.py --> ÚNICO ponto de conversão (Engenharia -> SI)     │
 └────────────────────────────────────────┬────────────────────────────────────────┘
                                          │
                                          ▼
 ┌─────────────────────────────────────────────────────────────────────────────────┐
 │ NÚCLEO HIDRÁULICO E NAVAL (PYTHON PURO)                                         │
 │   app/core/pipeline.py    --> Orquestrador integrado (Camadas 1 a 6)            │
 │   app/core/fluidos/      --> Andrade, Walther, Reynolds                         │
 │   app/core/perda_carga/  --> Churchill, Darcy-Weisbach, Singularidades          │
 │   app/core/bombas/       --> PCHIP, Ponto Operação, Ns, BEP                    │
 │   app/core/cavitacao/    --> NPSHa, Pressão Vapor Antoine                      │
 │   app/core/naval/        --> Varredura 3D R(θ,φ), Normas BV/LR/ABS, Redundância │
 │   app/core/motores/      --> Potências, ABNT, VFD, Consumo Diesel               │
 └────────────────────────────────────────┬────────────────────────────────────────┘
                                          │
                                          ▼
 ┌─────────────────────────────────────────────────────────────────────────────────┐
 │ CAMADA DE PERSISTÊNCIA                                                          │
 │   app/db/crud.py & database.py --> Armazenamento imutável em memória (UUID v4) │
 └─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Guardrails Arquiteturais Inegociáveis

Estes 5 guardrails são **estritamente verificados** e aplicados em toda a base de código:

1. **Isolamento Absoluto do `app/core/`**:
   - É **proibido** importar `fastapi`, `pydantic`, `sqlalchemy` ou `httpx` em qualquer módulo sob `app/core/`.
   - Todas as funções do `core/` consomem e retornam exclusivamente tipos primitivos de Python (`float`, `int`, `str`, `dict`, `list`) ou dataclasses puras em unidades SI.

2. **Fronteira Dimensional Única (`app/core/unit_casting.py`)**:
   - É **proibido** realizar conversão de unidades de engenharia (`m3h`, `bar`, `mm`, `°C`) dentro de módulos de cálculo hidráulico ou naval.
   - Toda conversão é realizada na entrada pelo módulo `unit_casting.py`, gerando a estrutura de rastreabilidade dimensional `RastreabilidadeUnidades`.

3. **Interpolação PCHIP Estrita (`app/utils/math_utils.py`)**:
   - É **proibido** utilizar `scipy.interpolate.CubicSpline` para curvas de bombas centrifugas ($H \times Q$, $\eta \times Q$, $\text{NPSHr} \times Q$).
   - É obrigatório o uso de `PchipInterpolator` (Piecewise Cubic Hermite Interpolating Polynomial) para evitar oscilações numéricas não físicas (*overshoot*).

4. **Tratamento de Exceções Estruturado sem Panic/Assert**:
   - Não se deve utilizar `assert` para validação de regras de negócio ou de entrada.
   - Qualquer inconformidade lança a exceção customizada `ErroCalculo` (definida em `app/schemas/erro.py`), que é capturada pelo exception handler global em `main.py` e convertida no schema `ErrorResponse`.

5. **Detecção Antecipada de Topologias em Malha Fechada**:
   - Ao varrer os trechos do payload, a detecção de topologias em malha fechada (loops, anéis) dispara imediatamente a exceção `TOPOLOGIA_MALHA_NAO_SUPORTADA` (HTTP 422) antes de executar qualquer cálculo.

---

## 3. Especificação Detalhada dos Endpoints REST

Todas as rotas públicas pertencem à versão `v1` da API e são acessíveis sob o prefixo `/api/v1`.

---

### 3.1 Endpoints de Pipeline e Resultados

#### `POST /api/v1/calcular`
* **Descrição**: Executa o pipeline de cálculo hidráulico-naval integrado de ponta a ponta (Camadas 1 a 6). Valida a entrada, realiza casting para o SI, calcula perdas, interpola a bomba, varre as 9 condições 3D, verifica normas classificadoras, seleciona o motor elétrico comercial ABNT, persiste o resultado no repositório e gera um identificador único UUID v4.
* **Headers**: `Content-Type: application/json`
* **Request Body**: `PipelineInput` (ver Anatomia na Seção 4)
* **Response Status**: `200 OK`
* **Response Body**: `ResultadoOutput`
* **Códigos de Erro Possíveis**: `422` (`TOPOLOGIA_MALHA_NAO_SUPORTADA`, `VAZAO_NEGATIVA`, `UNIDADE_INVALIDA`), `400` (`SEM_PONTO_OPERACAO_SHUT_OFF`, `SEM_PONTO_OPERACAO_FORA_CURVA`), `500` (`ERRO_INTERNO`).

#### `GET /api/v1/resultado/{id_calculo}`
* **Descrição**: Busca no banco de dados e retorna a memória de cálculo completa associada ao UUID v4 informado.
* **Path Parameter**: `id_calculo` (string UUID v4 válido, ex: `e83b48f9-467a-4c28-98e3-85f6e80b2a8d`).
* **Response Status**: `200 OK`
* **Response Body**: `ResultadoOutput`
* **Códigos de Erro Possíveis**: `404` (`RESULTADO_NAO_ENCONTRADO`).

---

### 3.2 Endpoints de Bibliotecas e Catálogos

#### `GET /api/v1/materiais`
* **Descrição**: Retorna o catálogo de materiais de tubulação navais cadastrados no sistema, acompanhados de suas rugosidades absolutas em milímetros ($\text{mm}$).
* **Response Status**: `200 OK`
* **Response Body**:
  ```json
  [
    {"id": "aco_carbono_novo", "nome": "Aço Carbono Comercial Novo", "rugosidade_mm": 0.046},
    {"id": "aco_inox_304", "nome": "Aço Inoxidável 304/316", "rugosidade_mm": 0.020},
    {"id": "cupraniquel_90_10", "nome": "Liga Cuproníquel (Cu-Ni 90/10)", "rugosidade_mm": 0.015},
    {"id": "pvc_naval", "nome": "PVC / Plástico Reforçado (PRFV)", "rugosidade_mm": 0.007}
  ]
  ```

#### `GET /api/v1/singularidades/biblioteca`
* **Descrição**: Retorna a biblioteca de conexões, acessórios e válvulas navais com seus coeficientes de perda de carga $K$ e razões de comprimento equivalente $L_e/D$.
* **Response Status**: `200 OK`
* **Response Body**:
  ```json
  {
    "valvulas": [
      {"tipo": "valvula_gaveta_aberta", "nome": "Válvula Gaveta Totalmente Aberta", "K_medio": 0.15, "Le_D": 8},
      {"tipo": "valvula_globo_aberta", "nome": "Válvula Globo Totalmente Aberta", "K_medio": 10.0, "Le_D": 340},
      {"tipo": "valvula_retencao_portinhola", "nome": "Válvula de Retenção Portinhola", "K_medio": 2.5, "Le_D": 100}
    ],
    "curvas": [
      {"tipo": "curva_90_rl", "nome": "Curva 90° Raio Longo (R/D = 1.5)", "K_medio": 0.30, "Le_D": 20},
      {"tipo": "cotovelo_90_rc", "nome": "Cotovelo 90° Raio Curto (R/D = 1.0)", "K_medio": 0.90, "Le_D": 30}
    ]
  }
  ```

---

### 3.3 Endpoints Modulares de Cálculo Hidráulico (Sub-Serviços)

- **`POST /api/v1/fluidos/propriedades`**: Calcula a viscosidade ($\mu, \nu$), densidade ($\rho$) e o Número de Reynolds ($Re$) para os parâmetros de fluido fornecidos.
- **`POST /api/v1/perda-carga/darcy-weisbach`**: Calcula o fator de atrito $f$ (via Churchill) e a perda de carga distribuída $h_f$ ($\text{m}$) para um trecho específico.
- **`POST /api/v1/perda-carga/hazen-williams`**: Calcula a perda por Hazen-Williams ou executa a conversão/fallback para Darcy-Weisbach com log estruturado.
- **`POST /api/v1/bombas/ponto-operacao`**: Executa a interpolação PCHIP da curva da bomba e encontra o cruzamento $(Q_{\text{op}}, H_{\text{op}})$.
- **`POST /api/v1/cavitacao/npsh`**: Calcula a pressão de vapor $P_v(T)$, o $\text{NPSHa}$ da sucção e a temperatura crítica $T_{\text{crit}}$ onde o fluido entraria em ebulição.
- **`POST /api/v1/motores/dimensionamento`**: Dimensiona as potências ($P_{\text{hid}}, P_{\text{eixo}}, P_{\text{elet}}$), calcula a corrente trifásica nominal e seleciona o motor comercial ABNT.

---

## 4. Anatomia dos Payloads JSON (Entrada e Saída)

### 4.1 JSON de Entrada (`PipelineInput`) Anotado

```json
{
  "projeto": {
    "nome": "string (obrigatório, ex: 'Sistema de Resfriamento ME')",
    "navio": "string (obrigatório, ex: 'Rebocador 80t BP')",
    "classificadora": "string (opcional, enum: 'BV', 'LR', 'ABS', 'DNV', default: 'BV')"
  },
  "fluido": {
    "tipo": "string (enum: 'agua_doce', 'agua_salgada', 'oleo_combustivel', 'oleo_lubrificante')",
    "temperatura_C": "float (faixa: -10 a +150 °C)",
    "densidade_kg_m3": "float (opcional, se omitido usa valor padrão da biblioteca)",
    "viscosidade_dinamica_Pa_s": "float (opcional, em Pa.s)",
    "pressao_vapor_Pa": "float (opcional, se omitido calcula por Antoine)"
  },
  "sistema": {
    "unidade_vazao": "string (enum: 'm3h', 'l/min', 'l/s', 'gpm')",
    "vazao": "float (obrigatório, Q > 0)",
    "pontos_sistema": {
      "succao":   {"x_m": "float", "y_m": "float", "z_m": "float"},
      "bomba":    {"x_m": "float", "y_m": "float", "z_m": "float"},
      "descarga": {"x_m": "float", "y_m": "float", "z_m": "float"}
    },
    "sistema_essencial": "boolean (default: false — se true ativa regras SOLAS)",
    "numero_bombas": "integer (min: 1)",
    "alimentacoes_independentes": "boolean"
  },
  "trechos": [
    {
      "id": "string (ex: 'S1')",
      "descricao": "string",
      "diametro_interno_mm": "float (> 0)",
      "comprimento_m": "float (>= 0)",
      "material": "string (id do material da biblioteca)",
      "rugosidade_mm": "float (opcional)",
      "perda_equipamento_m": "float (opcional, perda fixa adicional em metros)",
      "metodo_perda": "string (enum: 'darcy_weisbach', 'hazen_williams')",
      "singularidades": [
        {"tipo": "string (id do acessório)", "quantidade": "integer (>= 1)"}
      ]
    }
  ],
  "bomba": {
    "fabricante": "string",
    "modelo": "string",
    "rotacao_rpm": "float (> 0)",
    "curva_hq": [
      {"Q_m3h": "float", "H_m": "float"}
    ],
    "curva_npsh": [
      {"Q_m3h": "float", "NPSH_m": "float"}
    ],
    "curva_eta": [
      {"Q_m3h": "float", "eta_pct": "float"}
    ]
  }
}
```

---

### 4.2 JSON de Resposta (`ResultadoOutput`)

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
    {"condicao": "avaria_BB", "theta_deg": 10.0, "phi_deg": 22.5, "npsh_disponivel_m": 4.43, "aprovado": true}
  ],
  "rastreabilidade_unidades": [
    {"campo": "vazao", "valor_entrada": 118.5, "unidade_entrada": "m3h", "valor_si": 0.03291666666666667, "unidade_si": "m3/s", "fator": "/ 3600"}
  ],
  "alertas": []
}
```

---

## 5. Sistema Integrado de Erros (`ErrorResponse`)

A API encapsula todas as falhas de validação, erros numéricos e inconformidades navais na classe `ErrorResponse` (HTTP status `400`, `422`, `404` ou `500`).

### 5.1 Tabela Completa de Códigos de Erro

| Código (`codigo`) | Status HTTP | Origem / Causa | Exemplo de Diagnóstico |
|---|---|---|---|
| `TOPOLOGIA_MALHA_NAO_SUPORTADA` | `422` | Ciclo/anel detectado nos trechos | `{"loop_trechos": ["S1", "S2", "S1"]}` |
| `VAZAO_NEGATIVA` | `422` | Vazão informada $Q \le 0$ | `{"vazao_informada": -10}` |
| `TEMPERATURA_FORA_DO_RANGE` | `422` | Temperatura fora do limite físico | `{"temperatura_C": -50}` |
| `UNIDADE_INVALIDA` | `422` | Unidade de vazão não reconhecida | `{"unidade": "galao_desconhecido"}` |
| `CURVA_HQ_INVALIDA` | `422` | Curva de bomba tem menos de 3 pontos | `{"pontos_fornecidos": 2}` |
| `CURVA_HQ_H_INVALIDO` | `422` | Curva H×Q não é estritamente decrescente | `{"ponto_inversao_Q": 50}` |
| `SEM_PONTO_OPERACAO_SHUT_OFF` | `400` | Bomba não vence a cota estática ($H_0 < H_{\text{geo}}$) | `{"H_shut_off_m": 42.0, "deficit_m": 7.2}` |
| `SEM_PONTO_OPERACAO_FORA_CURVA` | `400` | Ponto de operação além do $Q_{\text{max}}$ da curva | `{"Q_op_requerido": 210, "Q_max_curva": 180}` |
| `RESULTADO_NAO_ENCONTRADO` | `404` | UUID v4 informado não existe no DB | `{"id_buscado": "uuid-inexistente"}` |
| `ERRO_VALIDACAO` | `422` | Erro Pydantic de tipo/formato de dados | `{"loc": ["body", "sistema", "vazao"]}` |
| `ERRO_INTERNO` | `500` | Exceção genérica interceptada no middleware | `{"mensagem": "Erro interno do servidor"}` |

### 5.2 Estrutura do JSON de Erro Estruturado

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

## 6. Exemplos Práticos de Integração Multilinguagem

### 6.1 Python (`httpx` assíncrono / síncrono com tratamento de exceção)

```python
import httpx

API_URL = "http://localhost:8000/api/v1/calcular"

payload = {
    "projeto": {"nome": "Teste Integracao", "navio": "Hull 101"},
    "fluido": {"tipo": "agua_salgada", "temperatura_C": 25},
    "sistema": {"unidade_vazao": "m3h", "vazao": 100.0},
    "bomba": {
        "rotacao_rpm": 1450,
        "curva_hq": [
            {"Q_m3h": 0, "H_m": 40.0},
            {"Q_m3h": 100, "H_m": 35.0},
            {"Q_m3h": 150, "H_m": 20.0}
        ]
    }
}

with httpx.Client() as client:
    response = client.post(API_URL, json=payload)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Sucesso! UUID: {data['id_calculo']}")
        print(f"Status Final: {data['status']}")
        print(f"Motor Recomendado: {data['resultados_prumo']['motor_selecionado_cv']} CV")
    else:
        err = response.json()
        print(f"❌ Erro HTTP {response.status_code}: [{err.get('codigo')}] {err.get('mensagem')}")
```

---

### 6.2 JavaScript / TypeScript (Node.js / React Async-Await)

```typescript
interface PipelineResponse {
  id_calculo: string;
  status: 'OK' | 'AVISO' | 'REPROVADO';
  resultados_prumo: {
    velocidade_succao_m_s: number;
    altura_manometrica_m: number;
    motor_selecionado_cv: number;
  };
}

async function executarCalculoNaval(payload: object): Promise<PipelineResponse | null> {
  try {
    const res = await fetch("http://localhost:8000/api/v1/calcular", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      const errorJson = await res.json();
      console.error(`Erro na API (${res.status}):`, errorJson.codigo, errorJson.mensagem);
      return null;
    }

    const data: PipelineResponse = await res.json();
    console.log(`Cálculo gravado com ID: ${data.id_calculo}`);
    return data;
  } catch (error) {
    console.error("Falha de rede ao conectar à API:", error);
    return null;
  }
}
```

---

### 6.3 PowerShell (Windows Native)

```powershell
$body = @{
    projeto = @{ nome = "Resfriamento ME"; navio = "PSV 4500" }
    fluido  = @{ tipo = "agua_salgada"; temperatura_C = 30 }
    sistema = @{ unidade_vazao = "m3h"; vazao = 118.5 }
    bomba   = @{
        rotacao_rpm = 1450
        curva_hq = @(
            @{ Q_m3h = 0;   H_m = 42 },
            @{ Q_m3h = 118.5; H_m = 36 },
            @{ Q_m3h = 180; H_m = 18 }
        )
    }
} | ConvertTo-Json -Depth 5

$response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/calcular" -Method Post -Body $body -ContentType "application/json"
Write-Output "UUID Gerado: $($response.id_calculo)"
Write-Output "Motor Selecionado: $($response.resultados_prumo.motor_selecionado_cv) CV"
```

---

## 7. Guia de Contribuição, Testes e Expansão

### 7.1 Executando os Testes Automatizados

A base de código possui **85 testes automatizados** divididos em unitários, integração e API HTTP:

```bash
# Executar todos os testes
pytest

# Executar com relatório de cobertura de código
pytest --cov=app --cov-report=term-missing
```

### 7.2 Regra TDD Obrigatoria para Novos Módulos
Ao criar uma nova funcionalidade (ex: modelo de viscosidade adicionado ou nova regra de classe):
1. **Escrever o teste primeiro** no repositório `tests/unit/` ou `tests/api/`.
2. Executar o `pytest` e **garantir que o teste falhe**.
3. Implementar o código em `app/core/` ou `app/api/`.
4. Executar o `pytest` e validar que **100% dos testes passem**.
5. Garantir que a cobertura global permaneça $\ge 90\%$ (com `app/core/` $\ge 95\%$).

---

## 8. Deploy, Docker e Variáveis de Ambiente

### 8.1 Dockerfile para Produção

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instala dependências de build se necessário
RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
RUN pip install --no-cache-dir .

COPY app/ ./app

EXPOSE 8000

ENV APP_ENV=production
ENV PORT=8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 8.2 Comandos Docker Compose

```yaml
version: '3.8'

services:
  naval-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - APP_ENV=production
      - APP_DEBUG=false
      - CORS_ORIGINS=*
    restart: always
```
