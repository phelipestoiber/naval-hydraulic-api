# Arquitetura — Engenharia de Software e API

**Versão:** 2.1 | **Base:** ARQUITETURA_v2.1.md

---

## 1. Princípios Inegociáveis

1. **`core/` não conhece FastAPI.** Todo o motor de cálculo recebe e retorna dataclasses Python puras. Testes unitários rodam sem servidor HTTP.
2. **Uma única fronteira de unidades.** `unit_casting.py` é o único ponto de conversão de unidades de engenharia → SI. Nenhum módulo de `core/` aceita m³/h, mm ou bar.
3. **Dados estáticos em JSON, nunca hardcoded.** Rugosidades, coeficientes K, potências ABNT e limites de classificadoras ficam em `app/data/*.json`.
4. **Três contratos separados:** schemas HTTP (`app/schemas/`) ≠ modelos ORM (`app/db/models.py`) ≠ estruturas internas (`app/schemas/si.py`).
5. **Falha explícita antes de falha silenciosa.** Topologia inválida e boundary check falho devem rejeitar com mensagem diagnóstica antes de qualquer cálculo.

---

## 2. Árvore de Diretórios

```
naval-hydraulic-api/
│
├── INSTRUCOES_AGENTE.md
├── LOG_SESSOES.md                        # Memória entre sessões — leitura/escrita obrigatórias
├── docs/
│   ├── 01_REFERENCIAL_MATEMATICO.md
│   ├── 02_REFERENCIAL_NAVAL.md
│   ├── 03_ARQUITETURA.md
│   └── 04_ROADMAP.md
│
├── app/
│   ├── __init__.py
│   ├── main.py                           # Entrypoint FastAPI — routers, middleware, CORS
│   │
│   ├── api/
│   │   └── v1/
│   │       ├── router.py                 # Agrega todos os sub-routers
│   │       ├── dependencies.py           # DB session, settings
│   │       └── endpoints/
│   │           ├── fluido.py             # POST /api/v1/fluido
│   │           ├── tubulacao.py          # POST /api/v1/tubulacao
│   │           ├── singularidades.py     # POST /api/v1/singularidades
│   │           ├── bomba.py              # POST /api/v1/bomba (JSON ou CSV)
│   │           ├── calcular.py           # POST /api/v1/calcular
│   │           ├── resultado.py          # GET  /api/v1/resultado/{id}
│   │           ├── relatorio.py          # GET  /api/v1/relatorio/{id}
│   │           ├── materiais.py          # GET  /api/v1/materiais
│   │           ├── biblioteca.py         # GET  /api/v1/singularidades/biblioteca
│   │           └── comparar.py           # POST /api/v1/comparar
│   │
│   ├── schemas/
│   │   ├── fluido.py                     # FluidoInput (inclui modelo_viscosidade)
│   │   ├── tubulacao.py                  # TrechoInput, SingularidadeInput
│   │   ├── bomba.py                      # BombaInput, CurvaHQ, CurvaNPSH, CurvaEta
│   │   ├── sistema.py                    # SistemaInput, PontoSistema3D
│   │   ├── calculo.py                    # CalculoInput (payload completo)
│   │   ├── resultado.py                  # ResultadoOutput, VarreduraInclinacao (9),
│   │   │                                 # CondicaoCritica, CondicaoReprovada,
│   │   │                                 # VerificacaoRedundancia, VerificacaoNorma
│   │   ├── erro.py                       # ErrorResponse, ErrorDetail
│   │   ├── comparacao.py                 # ComparacaoInput, ComparacaoOutput
│   │   └── si.py                         # SistemaSI, RastreabilidadeUnidades
│   │
│   ├── core/                             # ZERO dependência de FastAPI/SQLAlchemy/Pydantic
│   │   ├── unit_casting.py               # Casting SI + sanity checks + detecção de malha
│   │   │
│   │   ├── fluidos/
│   │   │   ├── reynolds.py               # Re, regime, alpha_cinetico
│   │   │   └── viscosidade.py            # Andrade, Walther, Linear; alpha_viscos
│   │   │
│   │   ├── perda_carga/
│   │   │   ├── fator_atrito.py           # Churchill, Colebrook, Swamee-Jain, Haaland
│   │   │   ├── darcy_weisbach.py         # hf = f·(L/D)·(v²/2g)
│   │   │   ├── hazen_williams.py         # hf + validar_hw() interno + fallback
│   │   │   ├── singularidades.py         # hL = K·v²/2g; Le; lê singularidades_k.json
│   │   │   └── sistema.py                # Hf_total; curva H_sis = H_geo + R·Q²
│   │   │
│   │   ├── bombas/
│   │   │   ├── interpolacao.py           # PchipInterpolator H×Q, η×Q, NPSHr×Q
│   │   │   ├── ponto_operacao.py         # Boundary check + bisseção + NR
│   │   │   ├── npsh.py                   # NPSHd, NPSHr aprox., 3 métodos, altitude, Nss
│   │   │   ├── potencia.py               # P_hid→P_motor; ABNT; elétrico/diesel/gasolina
│   │   │   ├── afinidade.py              # Método A (gaveta), B (VFD), C (usinagem)
│   │   │   ├── velocidade_especifica.py  # Ns; classificação radial/mista/axial
│   │   │   ├── bep.py                    # OK/AVISO/ALERTA por faixa
│   │   │   └── pre_dimensionamento.py    # Fórmula ABNT D_R; cobertura hidráulica
│   │   │
│   │   ├── naval/
│   │   │   ├── geometria.py              # R(θ,φ); z_efetivo; docstring convenção D5
│   │   │   ├── inclinacao.py             # 9 condições; crítica; OK/AVISO/REPROVADO
│   │   │   ├── normas.py                 # Classes I/II/III por classificadora; velocidades
│   │   │   └── redundancia.py            # Standby; alimentações; 4 cenários
│   │   │
│   │   ├── bernoulli.py                  # Bernoulli com alpha_cinetico
│   │   └── pipeline.py                   # Orquestrador Camadas 1→6
│   │
│   ├── db/
│   │   ├── database.py                   # Engine SQLAlchemy, SessionLocal, get_db()
│   │   ├── models.py                     # ORM: Calculo
│   │   └── crud.py                       # create_calculo, get_resultado
│   │
│   ├── data/
│   │   ├── materiais.json
│   │   ├── singularidades_k.json
│   │   ├── potencias_abnt.json
│   │   └── classificadoras.json
│   │
│   └── utils/
│       ├── math_utils.py                 # PchipInterpolator, bisseção, NR — v0.1.0
│       ├── csv_utils.py                  # Parser e validador CSV (schema D2)
│       └── report_utils.py               # Formata RastreabilidadeUnidades; memorial
│
└── tests/
    ├── conftest.py                        # DB memória, TestClient, payload_referencia
    ├── unit/
    │   ├── test_math_utils.py
    │   ├── test_csv_utils.py
    │   ├── test_unit_casting.py
    │   ├── test_viscosidade.py
    │   ├── test_reynolds.py
    │   ├── test_fator_atrito.py
    │   ├── test_darcy_weisbach.py
    │   ├── test_hazen_williams.py
    │   ├── test_singularidades.py
    │   ├── test_bernoulli.py
    │   ├── test_interpolacao.py
    │   ├── test_ponto_operacao.py
    │   ├── test_velocidade_especifica.py
    │   ├── test_bep.py
    │   ├── test_npsh.py
    │   ├── test_potencia.py
    │   ├── test_afinidade.py
    │   ├── test_geometria_naval.py
    │   ├── test_inclinacao.py
    │   ├── test_normas.py
    │   └── test_redundancia.py
    ├── integration/
    │   ├── test_pipeline_completo.py
    │   ├── test_inclinacao_varredura.py
    │   └── test_bomba_sistema.py
    └── api/
        ├── test_endpoint_calcular.py
        ├── test_endpoint_resultado.py
        └── test_endpoint_comparar.py
```

---

## 3. Estruturas Internas em SI (`app/schemas/si.py`)

```python
from dataclasses import dataclass

@dataclass
class SistemaSI:
    """Todas as grandezas em SI — produzida por unit_casting.py."""
    Q_m3s:      float   # Vazão [m³/s]
    D_m:        float   # Diâmetro interno [m]
    L_m:        float   # Comprimento [m]
    rho_kgm3:   float   # Massa específica [kg/m³]
    mu_pas:     float   # Viscosidade dinâmica [Pa·s]
    nu_m2s:     float   # Viscosidade cinemática [m²/s]
    Pv_pa:      float   # Pressão de vapor [Pa]
    Patm_pa:    float   # Pressão atmosférica [Pa]
    T_k:        float   # Temperatura [K]
    epsilon_m:  float   # Rugosidade absoluta [m]
    altitude_m: float   # Altitude [m]
    N_rpm:      float   # Rotação da bomba [rpm]

@dataclass
class RastreabilidadeUnidades:
    """Registra cada conversão de unidade para auditoria."""
    campos: list[dict]
    # Estrutura de cada item:
    # {
    #   "campo": "vazao",
    #   "valor_entrada": 118.5,
    #   "unidade_entrada": "m3/h",
    #   "valor_si": 0.032917,
    #   "unidade_si": "m3/s",
    #   "fator": "/ 3600"
    # }
```

---

## 4. Conversão de Unidades (`unit_casting.py`)

### 4.1 Tabela de conversões

| Grandeza | Unidades aceitas | Unidade SI | Fator |
|---|---|---|---|
| Vazão | m³/h | m³/s | `/ 3600` |
| Vazão | l/min | m³/s | `/ 60000` |
| Vazão | l/s | m³/s | `/ 1000` |
| Diâmetro / comprimento | mm | m | `/ 1000` |
| Diâmetro | pol | m | `× 0,0254` |
| Pressão | kPa | Pa | `× 1000` |
| Pressão | bar | Pa | `× 1e5` |
| Pressão | kgf/cm² | Pa | `× 98066,5` |
| Pressão | mca | Pa | `× 9810` |
| Pressão | psi | Pa | `× 6894,76` |
| Temperatura | °C | K | `+ 273,15` |
| Viscosidade dinâmica | cP | Pa·s | `× 1e-3` |
| Viscosidade cinemática | cSt | m²/s | `× 1e-6` |
| Rotação | rpm | rad/s | `× 2π/60` |

### 4.2 Sanity checks (Pydantic @field_validator)

```python
# Nunca usar assert — sempre @field_validator com ErrorResponse estruturado

Q > 0                      → "VAZAO_NEGATIVA"
D > 0                      → "DIAMETRO_INVALIDO"
0 < ρ ≤ 2000 kg/m³        → "DENSIDADE_INVALIDA"
μ > 0                      → "VISCOSIDADE_INVALIDA"
Pv ≥ 0                     → "PRESSAO_VAPOR_INVALIDA"
200 K < T < 700 K          → "TEMPERATURA_FORA_DO_RANGE"
ε ≥ 0                      → "RUGOSIDADE_INVALIDA"
```

### 4.3 Detecção de malha (após sanity checks, antes de SistemaSI)

```python
if detectar_malha_fechada(payload.trechos):
    raise ErroCalculo(
        codigo="TOPOLOGIA_MALHA_NAO_SUPORTADA",
        mensagem=(
            "Topologia em malha fechada detectada. "
            "Este sistema suporta apenas escoamento unidimensional em topologia aberta. "
            "Sistemas em anel requerem solver matricial (Hardy-Cross) — fora do escopo."
        )
    )
```

---

## 5. Fluxo do Pipeline (Camadas 1→6)

```
Camada 1: unit_casting.py
  → Casting SI + sanity checks + detecção de malha
  → Produz SistemaSI + RastreabilidadeUnidades

Camada 2: validações de norma e equação
  → naval/normas.py: classe I/II/III; MAWP; velocidades limite
  → hazen_williams.py: validar_hw(); fallback automático

Camada 3: geometria e inclinação
  → naval/geometria.py: z_efetivo para prumo
  → naval/inclinacao.py: gerar lista das 9 condições nomeadas

Camada 4: loop hidráulico (para cada condição θ,φ)
  → reynolds.py: Re, regime, alpha_cinetico
  → fator_atrito.py: f via Churchill
  → darcy_weisbach.py ou hazen_williams.py: hf
  → singularidades.py: hL
  → bernoulli.py: balanço com alpha_cinetico
  → sistema.py: Hf_total, H_sistema(Q)

Camada 5: bomba
  → interpolacao.py: PchipInterpolator H×Q, η×Q, NPSHr×Q
  → ponto_operacao.py: boundary check → bisseção + NR → Q_op, H_op
  → velocidade_especifica.py: Ns, tipo_bomba
  → bep.py: status BEP
  → npsh.py: NPSHd(θ,φ), margem
  → potencia.py: P_hid, P_eixo, motor_selecionado

Camada 5b: naval
  → redundancia.py: standby + alimentações
  → inclinacao.py: status OK/AVISO/REPROVADO; condicoes_reprovadas

Camada 6: resultado
  → Montar ResultadoOutput completo
  → report_utils.py: formatar rastreabilidade_unidades
  → crud.py: persistir com UUID (apenas a partir de v1.0.0)
```

---

## 6. Contratos HTTP

### 6.1 Endpoints

```
POST /api/v1/fluido              → validar propriedades do fluido
POST /api/v1/tubulacao           → definir trechos
POST /api/v1/singularidades      → adicionar singularidades
POST /api/v1/bomba               → inserir curva H×Q (JSON ou CSV)
POST /api/v1/calcular            → executa pipeline completo
GET  /api/v1/resultado/{id}      → recupera resultado salvo
GET  /api/v1/relatorio/{id}      → memorial de cálculo estruturado
GET  /api/v1/materiais           → lista materiais e rugosidades
GET  /api/v1/singularidades/biblioteca → lista K de referência
POST /api/v1/comparar            → compara duas configurações
```

### 6.2 Schema de Erro

```python
class ErrorDetail(BaseModel):
    campo:    str | None = None   # Campo que originou o erro
    mensagem: str
    codigo:   str                 # Código de máquina

class ErrorResponse(BaseModel):
    status:     str = "ERRO"
    erros:      list[ErrorDetail]
    request_id: str | None = None
```

### 6.3 Tabela Completa de Códigos de Erro

| Situação | HTTP | Código |
|---|---|---|
| Campo obrigatório ausente | 422 | `CAMPO_OBRIGATORIO` |
| Vazão negativa | 422 | `VAZAO_NEGATIVA` |
| Diâmetro inválido | 422 | `DIAMETRO_INVALIDO` |
| Densidade fora de (0, 2000] | 422 | `DENSIDADE_INVALIDA` |
| Viscosidade negativa | 422 | `VISCOSIDADE_INVALIDA` |
| Pressão de vapor negativa | 422 | `PRESSAO_VAPOR_INVALIDA` |
| Temperatura fora de [200K, 700K] | 422 | `TEMPERATURA_FORA_DO_RANGE` |
| Rugosidade negativa | 422 | `RUGOSIDADE_INVALIDA` |
| Unidade desconhecida | 422 | `UNIDADE_INVALIDA` |
| Fluido não-Newtoniano | 422 | `FLUIDO_NAO_NEWTONIANO` |
| Fluido desconhecido | 422 | `FLUIDO_INVALIDO` |
| **Malha fechada detectada** | 422 | `TOPOLOGIA_MALHA_NAO_SUPORTADA` |
| Curva H×Q com < 3 pontos | 422 | `CURVA_HQ_INVALIDA` |
| H crescente na curva H×Q | 422 | `CURVA_HQ_H_INVALIDO` |
| **H_shut_off < H_sistema(Q=0)** | 422 | `SEM_PONTO_OPERACAO_SHUT_OFF` |
| **Q_op além da curva fornecida** | 422 | `SEM_PONTO_OPERACAO_FORA_CURVA` |
| Bisseção não convergiu | 422 | `SEM_PONTO_OPERACAO` |
| CSV — header incorreto | 422 | `CURVA_CSV_HEADER_INVALIDO` |
| CSV — Q não crescente | 422 | `CURVA_CSV_Q_NAO_CRESCENTE` |
| CSV — H crescente | 422 | `CURVA_CSV_H_INVALIDO` |
| CSV — decimal vírgula | 422 | `CURVA_CSV_FORMATO_DECIMAL` |
| CSV — < 3 pontos | 422 | `CURVA_CSV_PONTOS_INSUFICIENTES` |
| CSV — > 50 pontos | 422 | `CURVA_CSV_PONTOS_EXCEDIDOS` |
| CSV — valor ausente em coluna obrigatória | 422 | `CURVA_CSV_VALOR_AUSENTE` |
| CSV — arquivo vazio ou binário | 422 | `CURVA_CSV_ARQUIVO_INVALIDO` |
| CSV — encoding não UTF-8 | 422 | `CURVA_CSV_ENCODING_INVALIDO` |
| UUID não encontrado | 404 | `RESULTADO_NAO_ENCONTRADO` |
| Erro interno não antecipado | 500 | `ERRO_INTERNO` |
| HW rejeitada por fluido | — (aviso) | `HW_FLUIDO_INVALIDO` |
| HW rejeitada por temperatura | — (aviso) | `HW_TEMPERATURA_INVALIDA` |
| HW rejeitada por regime | — (aviso) | `HW_REGIME_INVALIDO` |
| HW rejeitada por diâmetro | — (aviso) | `HW_DIAMETRO_INVALIDO` |

### 6.3.1 Exemplo Completo de Saída — `ResultadoOutput` (caso de referência)

```json
{
  "id_calculo": "uuid-v4",
  "status": "OK",
  "alertas": ["Ponto de operação dentro da faixa preferencial de BEP (79%)."],
  "avisos_equacao": [],
  "rastreabilidade_unidades": {
    "vazao":      {"valor_entrada": 118.5, "unidade_entrada": "m3/h",
                   "valor_si": 0.032917, "unidade_si": "m3/s", "fator": "/ 3600"},
    "diametro_s": {"valor_entrada": 150.0, "unidade_entrada": "mm",
                   "valor_si": 0.150, "unidade_si": "m", "fator": "/ 1000"},
    "diametro_d": {"valor_entrada": 125.0, "unidade_entrada": "mm",
                   "valor_si": 0.125, "unidade_si": "m", "fator": "/ 1000"}
  },
  "resultados_prumo": {
    "vazao_m3h": 118.5, "vazao_m3s": 0.032917,
    "velocidade_succao_m_s": 1.87, "velocidade_descarga_m_s": 2.69,
    "reynolds_succao": 287000, "reynolds_descarga": 336000,
    "regime_succao": "turbulento",
    "alpha_cinetico_succao": 1.0, "alpha_cinetico_descarga": 1.0,
    "metodo_perda_succao": "darcy_weisbach", "metodo_perda_descarga": "darcy_weisbach",
    "fator_atrito_succao": 0.0158, "fator_atrito_descarga": 0.0165,
    "hf_distribuida_m": 3.21, "hf_localizada_m": 1.84, "hf_total_m": 5.05,
    "h_geo_m": 3.40, "altura_manometrica_m": 8.45,
    "velocidade_especifica_ns": 47.3, "tipo_bomba": "centrifuga_radial",
    "npsh_disponivel_m": 4.82, "npsh_requerido_m": 3.20, "margem_npsh_m": 0.98,
    "metodo_margem_npsh": "combinado",
    "criterio_npsh": "NPSHd >= max(NPSHr+0.6 ; 1.2*NPSHr) = max(3.80;3.84) = 3.84 m",
    "status_npsh": "OK",
    "ponto_bep_percentual": 79.0, "status_bep": "OK",
    "potencia_hidraulica_kW": 2.79, "potencia_eixo_kW": 3.50,
    "potencia_motor_kW": 3.80, "motor_selecionado_cv": 7.5,
    "eficiencia_bomba_pct": 79.9
  },
  "varredura_inclinacao": [
    {"condicao": "prumo", "theta_deg": 0.0, "phi_deg": 0.0,
     "h_geo_m": 3.40, "h_s_m": 0.70, "npsh_disponivel_m": 4.82, "aprovado": true},
    {"condicao": "operacao_BB", "theta_deg": 5.0, "phi_deg": 15.0,
     "h_geo_m": 3.17, "h_s_m": 0.93, "npsh_disponivel_m": 4.59, "aprovado": true},
    {"condicao": "operacao_EB", "theta_deg": 5.0, "phi_deg": -15.0,
     "h_geo_m": 3.63, "h_s_m": 0.47, "npsh_disponivel_m": 5.05, "aprovado": true},
    {"condicao": "operacao_BB_inv", "theta_deg": -5.0, "phi_deg": 15.0,
     "h_geo_m": 3.22, "h_s_m": 0.88, "npsh_disponivel_m": 4.64, "aprovado": true},
    {"condicao": "operacao_EB_inv", "theta_deg": -5.0, "phi_deg": -15.0,
     "h_geo_m": 3.58, "h_s_m": 0.52, "npsh_disponivel_m": 5.00, "aprovado": true},
    {"condicao": "avaria_BB", "theta_deg": 10.0, "phi_deg": 22.5,
     "h_geo_m": 2.98, "h_s_m": 1.12, "npsh_disponivel_m": 4.40, "aprovado": true},
    {"condicao": "avaria_EB", "theta_deg": 10.0, "phi_deg": -22.5,
     "h_geo_m": 3.82, "h_s_m": 0.28, "npsh_disponivel_m": 5.24, "aprovado": true},
    {"condicao": "avaria_BB_inv", "theta_deg": -10.0, "phi_deg": 22.5,
     "h_geo_m": 3.05, "h_s_m": 1.05, "npsh_disponivel_m": 4.47, "aprovado": true},
    {"condicao": "avaria_EB_inv", "theta_deg": -10.0, "phi_deg": -22.5,
     "h_geo_m": 3.75, "h_s_m": 0.35, "npsh_disponivel_m": 5.17, "aprovado": true}
  ],
  "condicoes_reprovadas": [],
  "condicao_critica": {
    "condicao": "avaria_BB",
    "descricao": "Avaria — trim +10° banda +22,5° (bombordo)",
    "theta_deg": 10.0, "phi_deg": 22.5,
    "npsh_disponivel_m": 4.40, "npsh_minimo_m": 3.84,
    "margem_m": 0.56, "deficit_m": null, "aprovado": true
  },
  "verificacao_redundancia": {
    "sistema_essencial": true, "numero_bombas": 2,
    "alimentacoes_independentes": true,
    "status": "APROVADO", "nao_conformidades": []
  },
  "verificacao_norma": {
    "classificadora": "BV", "classe_tubulacao": "III",
    "velocidade_succao_status": "OK", "velocidade_descarga_status": "OK",
    "mawp_status": "OK"
  }
}
```

**Exemplo de `condicoes_reprovadas` quando `status != "OK"`:**
```json
"condicoes_reprovadas": [
  {"condicao": "avaria_BB", "theta_deg": 10.0, "phi_deg": 22.5,
   "npsh_disponivel_m": 2.10, "npsh_minimo_m": 3.84, "deficit_m": 1.74}
]
```

### 6.4 Regra de Status para Resultados de Projeto

> Falhas de NPSH, BEP e redundância são **resultados de projeto** — sempre HTTP 200.

```
status = "OK"        → NPSHd ≥ critério em todas as 9 condições de inclinação

status = "AVISO"     → NPSHd ≥ critério nas 5 condições de operação/prumo,
                        mas < critério em 1 ou mais das 4 condições de avaria
                        (regra primária — REFERENCIAL Seção 14.3)

status = "REPROVADO" → NPSHd < critério em qualquer condição de operação
                        normal (as 5 condições de operação/prumo)

REGRAS COMPLEMENTARES (aplicadas independentemente do status de NPSH):
  - status_bep = "ALERTA" (Q/Q_BEP fora de 50–130%) → sempre eleva o
    status geral para no mínimo "AVISO", mesmo se NPSH = "OK"
  - falha em verificacao_redundancia (sistema essencial reprovado)
    → sempre eleva o status geral para "REPROVADO"

O status geral do resultado é o PIOR entre: status_npsh, status_bep
(convertido) e verificacao_redundancia.status. NPSH é a regra primária
que define AVISO/REPROVADO por inclinação; BEP e redundância são
verificações independentes que podem agravar — nunca abrandar — o status.
```

---

## 7. Schema CSV de Curva da Bomba

**Header obrigatório (case-sensitive):**
```
Q_m3h,H_m,eta_pct,NPSH_m
```

Colunas `eta_pct` e `NPSH_m` são opcionais.

| Regra | Critério | Código de erro |
|---|---|---|
| 1 | Colunas obrigatórias: `Q_m3h`, `H_m` | `CURVA_CSV_HEADER_INVALIDO` |
| 2 | Separador: vírgula | `CURVA_CSV_FORMATO_INVALIDO` |
| 3 | Decimal: ponto (não vírgula) | `CURVA_CSV_FORMATO_DECIMAL` |
| 4 | Mínimo 3 pontos | `CURVA_CSV_PONTOS_INSUFICIENTES` |
| 5 | Máximo 50 pontos | `CURVA_CSV_PONTOS_EXCEDIDOS` |
| 6 | Q monotonicamente crescente | `CURVA_CSV_Q_NAO_CRESCENTE` |
| 7 | H monotonicamente decrescente | `CURVA_CSV_H_INVALIDO` |
| 8 | Valores ausentes só em colunas opcionais | `CURVA_CSV_VALOR_AUSENTE` |
| 9 | Linhas com `#` são comentários | — |
| 10 | Encoding: UTF-8 | `CURVA_CSV_ENCODING_INVALIDO` |

---

## 8. Banco de Dados

```python
# app/db/models.py
class Calculo(Base):
    __tablename__ = "calculos"

    id             = Column(String,   primary_key=True, default=lambda: str(uuid4()))
    criado_em      = Column(DateTime, default=datetime.utcnow)
    projeto        = Column(String,   nullable=True)
    navio          = Column(String,   nullable=True)
    classificadora = Column(String,   nullable=True)
    status         = Column(String)                   # "OK"|"AVISO"|"REPROVADO"|"ERRO"
    payload_json   = Column(Text)
    resultado_json = Column(Text)
```

**Upgrade path:**
```bash
# Local (padrão)
DATABASE_URL=sqlite+aiosqlite:///./naval_hydraulic.db

# Produção / SaaS
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/naval_hydraulic
```

Versões v0.x retornam resultados **sem persistência**. Banco ativado na v0.9.0; persistência nos endpoints ativada na v1.0.0.

---

## 9. Schemas dos Arquivos JSON Estáticos

### 9.1 `materiais.json`

```json
{
  "versao_schema": "2.0",
  "materiais": [
    {
      "id": "aco_inox_304",
      "nome": "Aço inoxidável 304/316",
      "rugosidade_mm": 0.02,
      "rugosidade_mm_range": [0.015, 0.025],
      "coeficiente_hw_novo": 145,
      "coeficiente_hw_usado": 130,
      "norma_material": "ASTM A312",
      "uso_naval_tipico": "Água do mar, alimentos"
    }
  ]
}
```

### 9.2 `singularidades_k.json`

```json
{
  "versao_schema": "1.0",
  "singularidades": [
    {
      "id": "curva_90_rl",
      "nome": "Curva 90° raio longo (R/D = 1,5)",
      "K": 0.6,
      "Le_sobre_D": 16,
      "referencia": "Crane TP-410",
      "categoria": "curva",
      "suporta_metodo_A": false
    },
    {
      "id": "valvula_gaveta",
      "nome": "Válvula de gaveta (gate) — aberta",
      "K": 0.15,
      "Le_sobre_D": 7,
      "referencia": "ISA / Crane TP-410",
      "categoria": "valvula",
      "suporta_metodo_A": true
    }
  ]
}
```

> `suporta_metodo_A: true` marca válvulas que podem ser usadas no Método A de ajuste de ponto de operação.

### 9.3 `potencias_abnt.json`

```json
{
  "versao_schema": "2.0",
  "potencias_cv": [0.083, 0.125, 0.167, 0.25, 0.333, 0.5, 0.75, 1,
                   1.5, 2, 3, 4, 5, 6, 7.5, 10, 12.5, 15, 20, 25,
                   30, 40, 50, 60, 75, 100, 125, 150, 200],
  "margens_por_tipo": {
    "eletrico": [
      {"cv_max": 2.0,  "margem_pct": 50},
      {"cv_max": 5.0,  "margem_pct": 30},
      {"cv_max": 10.0, "margem_pct": 20},
      {"cv_max": 20.0, "margem_pct": 15},
      {"cv_max": null, "margem_pct": 10}
    ],
    "diesel":   [{"cv_max": null, "margem_pct": 25}],
    "gasolina": [{"cv_max": null, "margem_pct": 50}]
  }
}
```

### 9.4 `classificadoras.json`

```json
{
  "versao_schema": "2.0",
  "classificadoras": {
    "BV": {
      "classes_tubulacao": [
        {"classe": "I",   "pressao_bar_min": 16,  "temperatura_c_min": 300},
        {"classe": "II",  "pressao_bar_min": 7,   "temperatura_c_min": 170},
        {"classe": "III", "pressao_bar_min": 0,   "temperatura_c_min": 0}
      ],
      "condicoes_inclinacao": {
        "operacao": {"trim_deg": 5,  "banda_deg": 15.0},
        "avaria":   {"trim_deg": 10, "banda_deg": 22.5}
      },
      "velocidades_limite_ms": {
        "agua_salgada": {
          "succao_min": 0.5, "succao_max": 1.2,
          "recalque_min": 1.0, "recalque_max": 2.5
        }
      }
    },
    "LR": {
      "classes_tubulacao": [
        {"classe": "I",   "pressao_bar_min": 20,  "temperatura_c_min": 300},
        {"classe": "II",  "pressao_bar_min": 7,   "temperatura_c_min": 170},
        {"classe": "III", "pressao_bar_min": 0,   "temperatura_c_min": 0}
      ],
      "nota_divergencia": "Classe I LR: P>20 bar vs BV: P>16 bar."
    },
    "ABS": {
      "classes_tubulacao": [
        {"classe": "I",   "pressao_bar_min": 16,  "temperatura_c_min": 300},
        {"classe": "II",  "pressao_bar_min": 7,   "temperatura_c_min": 170},
        {"classe": "III", "pressao_bar_min": 0,   "temperatura_c_min": 0}
      ]
    }
  }
}
```

---

## 10. Dependências

```toml
# pyproject.toml

[project]
name = "naval-hydraulic-api"
version = "0.1.0"
requires-python = ">=3.11"

dependencies = [
    "fastapi>=0.111.0",           # Framework HTTP + OpenAPI automático
    "uvicorn[standard]>=0.29.0",  # ASGI server
    "pydantic>=2.7.0",            # Validação de schemas + validators declarativos
    "pydantic-settings>=2.2.0",   # Configuração via .env
    "sqlalchemy>=2.0.30",         # ORM — SQLite local / PostgreSQL futuro
    "aiosqlite>=0.20.0",          # Driver async para SQLite
    "numpy>=1.26.0",              # Operações vetoriais, matrizes de rotação 3D
    "scipy>=1.13.0",              # PchipInterpolator (F2), bisseção
    "python-multipart>=0.0.9",    # Upload de CSV da curva da bomba
    "httpx>=0.27.0",              # Cliente HTTP para testes de integração
]

[project.optional-dependencies]
dev = [
    "pytest>=8.2.0",
    "pytest-asyncio>=0.23.0",     # Testes de endpoints async
    "pytest-cov>=5.0.0",          # Cobertura de código
    "pytest-benchmark>=4.0.0",    # Benchmark do pipeline
    "ruff>=0.4.0",                # Linter + formatter
    "mypy>=1.10.0",                # Type checking estático
    "pre-commit>=3.7.0",          # Hooks de qualidade antes do commit
]
```

**Dependências descartadas deliberadamente:**

| Biblioteca | Razão da exclusão |
|---|---|
| `pandas` | Overhead desnecessário — dados são arrays simples |
| `celery` + `redis` | Cálculos completam em ms; fila é over-engineering |
| `alembic` | Adicionado pós-v1.0.0 quando o schema estabilizar |
| `sympy` | Equações implementadas diretamente |
| `reportlab` / `weasyprint` | PDF fora do escopo da API |

---

## 10.1 Docker

```dockerfile
# docker/Dockerfile

FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
RUN pip install --no-cache-dir ".[dev]"

COPY . .

EXPOSE 8000

# Produção: remover --reload do CMD abaixo
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker/docker-compose.yml

services:
  api:
    build:
      context: ..
      dockerfile: docker/Dockerfile
    ports:
      - "8000:8000"
    volumes:
      - ../app:/app/app      # Hot-reload em desenvolvimento
      - db_data:/app          # Persistência do SQLite
    env_file:
      - ../.env
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

volumes:
  db_data:
```

---

## 11. Variáveis de Ambiente (`.env.example`)

```bash
# Ambiente
APP_ENV=development
APP_DEBUG=true

# Banco
DATABASE_URL=sqlite+aiosqlite:///./naval_hydraulic.db

# API
API_V1_PREFIX=/api/v1
PROJECT_NAME="Naval Hydraulic Calculator"
VERSION=0.1.0

# Limites
MAX_TRECHOS_POR_CALCULO=50
MAX_SINGULARIDADES_POR_TRECHO=20
TIMEOUT_CALCULO_SEGUNDOS=30

# Naval
CLASSIFICADORA_PADRAO=BV

# NPSH
METODO_MARGEM_NPSH=combinado
MARGEM_NPSH_FIXA_M=0.6
MARGEM_NPSH_CRITICA_M=1.0
FATOR_MARGEM_NPSH=1.2

# Tolerâncias numéricas
TOLERANCIA_CONVERGENCIA_PONTO_OP=1e-4
TOLERANCIA_CONVERGENCIA_ATRITO=1e-6
MAX_ITERACOES_PONTO_OP=100
MAX_ITERACOES_ATRITO=50

# Interpolação
INTERPOLACAO_BOMBA=pchip

# Topologia
REJEITAR_MALHA_FECHADA=true

# Viscosidade
MODELO_VISCOSIDADE_PADRAO=andrade

# CSV
MAX_PONTOS_CURVA_HQ=50
MIN_PONTOS_CURVA_HQ=3
```

---

## 12. Limitações de Escopo

| Limitação | Código de rejeição | Motivo |
|---|---|---|
| Topologia em malha fechada | `TOPOLOGIA_MALHA_NAO_SUPORTADA` | Requer solver matricial (Hardy-Cross) |
| Fluidos não-Newtonianos | `FLUIDO_NAO_NEWTONIANO` | Requer modelos reológicos adicionais |
| Escoamento compressível | `FLUIDO_INVALIDO` | Requer equações de estado |
| Escoamento multifásico | `FLUIDO_INVALIDO` | Requer modelos de slip e fração de vazio |
| Escoamento transiente | não implementado | Requer integração temporal |
| Verificação estrutural ASME B31 | não implementado | Fora do escopo hidráulico |
| Geração de PDF | não implementado | Responsabilidade do cliente da API |

---

## 13. Ambiente de Desenvolvimento e Git

### 13.1 Pré-requisitos

| Ferramenta | Versão mínima | Verificar com |
|---|---|---|
| Python | 3.11 | `python --version` |
| pip | 23.0 | `pip --version` |
| Git | 2.40 | `git --version` |

---

### 13.2 Ambiente Virtual (Windows)

O projeto usa ambiente virtual Python padrão (`venv`). O agente **não cria nem ativa** o ambiente virtual — isso é responsabilidade do desenvolvedor antes de iniciar qualquer sessão.

**Setup inicial (executar uma única vez ao clonar o repositório):**

```bat
:: Na raiz do repositório
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
```

**Ativar em cada nova sessão de terminal:**

```bat
.venv\Scripts\activate
```

**Verificar que o ambiente está ativo:**

```bat
:: O prompt deve mostrar (.venv) no início
:: Confirmar que o Python usado é o do venv:
where python
:: Deve retornar: ...\naval-hydraulic-api\.venv\Scripts\python.exe
```

**Desativar ao encerrar:**

```bat
deactivate
```

> **Importante:** nunca instalar dependências globalmente com `pip install` fora do venv ativo. Sempre verificar `where python` antes de qualquer `pip install` ou `pytest`.

---

### 13.3 Arquivo `.gitignore`

Conteúdo completo do `.gitignore` para este projeto:

```gitignore
# Ambiente virtual
.venv/
venv/
env/

# Python
__pycache__/
*.py[cod]
*.pyo
*.pyd
.Python
*.egg-info/
dist/
build/
*.egg

# Pytest e cobertura
.pytest_cache/
.coverage
coverage.xml
htmlcov/

# Banco de dados local
*.db
*.db-journal
naval_hydraulic.db

# Variáveis de ambiente
.env
.env.local
.env.*.local

# IDEs e editores
.vscode/
.idea/
*.suo
*.user
*.userosscache
*.sln.docstates
Thumbs.db

# Logs e temporários
*.log
*.tmp
*.bak

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# ruff
.ruff_cache/

# Uploads e outputs de teste
/tmp/
```

---

### 13.4 Estratégia de Git

**Branch única: `main`**

Todo o desenvolvimento acontece direto em `main`. A estabilidade é garantida pelo critério de avanço de versão — só commitar quando os testes da versão estiverem passando e a cobertura atingida. O ponto verificado de cada versão é marcado com uma tag.

---

### 13.5 Fluxo por Sessão (comandos para copiar e colar)

O agente vai sugerir os comandos e mensagens de commit ao final de cada sessão. O fluxo esperado é:

**Durante a sessão** — o agente trabalha nos arquivos. Você não precisa fazer nada no Git.

**Ao fechar uma sessão sem completar uma versão** (trabalho parcial):

```bat
git add .
git commit -m "wip(v0.X.0): <resumo do que foi feito>"
```

**Ao fechar uma versão completa** (todos os testes passando, cobertura ok):

```bat
:: 1. Commit final da versão
git add .
git commit -m "feat(v0.X.0): <título da versão conforme 04_ROADMAP.md>"

:: 2. Tag anotada — o número de versão deve coincidir com o INSTRUCOES_AGENTE.md
git tag -a v0.X.0 -m "v0.X.0: <título da versão>"

:: 3. Push com a tag
git push origin main
git push origin v0.X.0
```

---

### 13.6 Formato de Mensagens de Commit

O agente sugerirá mensagens neste formato. Copiar e colar diretamente.

**Prefixos:**

| Prefixo | Quando usar |
|---|---|
| `feat(vX.Y.Z):` | Entrega de uma versão completa |
| `wip(vX.Y.Z):` | Trabalho parcial — versão não fechada |
| `fix(módulo):` | Correção de bug em módulo existente |
| `test(TX.Y):` | Adição ou correção de teste específico |
| `docs:` | Atualização de documentação (incluindo LOG_SESSOES.md) |
| `refactor(módulo):` | Refatoração sem mudança de comportamento |

**Exemplos reais esperados:**

```
feat(v0.1.0): fundação — unit_casting, reynolds, viscosidade, csv_utils

feat(v0.2.0): fator de atrito — Churchill, Colebrook, Haaland, Darcy-Weisbach

fix(interpolacao): substituir CubicSpline por PchipInterpolator (F2)

test(T4.2): adicionar boundary check e casos F3-A e F3-B

docs: atualizar LOG_SESSOES.md — sessão v0.3.0 concluída

wip(v0.4.0): interpolacao.py e test_interpolacao.py — ponto_operacao pendente
```

---

### 13.7 Tags Git × Versões do Software

Cada versão do `04_ROADMAP.md` que fechar deve ter uma tag Git correspondente. A tag é o único ponto no histórico do repositório que garante "o código neste commit passou em todos os testes de vX.Y.Z".

**Listar todas as tags existentes:**

```bat
git tag --list "v*" --sort=-version:refname
```

**Ver o que foi entregue em uma tag específica:**

```bat
git show v0.3.0 --stat
```

**Voltar ao estado de uma versão anterior (apenas leitura):**

```bat
git checkout v0.2.0
:: Para voltar ao estado atual:
git checkout main
```

---

### 13.8 Setup Inicial do Repositório (executar uma única vez)

```bat
:: Na pasta onde o projeto será criado
git init naval-hydraulic-api
cd naval-hydraulic-api

:: Criar o .gitignore antes do primeiro commit
:: (copiar o conteúdo da Seção 13.3 para .gitignore)

:: Criar o ambiente virtual
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"

:: Primeiro commit — só os arquivos de documentação e configuração
git add INSTRUCOES_AGENTE.md LOG_SESSOES.md docs/ pyproject.toml .gitignore
git commit -m "docs: setup inicial — documentação e configuração do projeto"
```

> **Nota:** o `LOG_SESSOES.md` e o `INSTRUCOES_AGENTE.md` entram no repositório desde o primeiro commit — eles são parte do projeto, não arquivos auxiliares externos.
