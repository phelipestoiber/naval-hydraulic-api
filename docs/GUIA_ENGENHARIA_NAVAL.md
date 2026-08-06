# ⚓ Guia Técnico de Engenharia Hidráulica e Naval

**Naval Hydraulic Calculator API** — Manual de Engenharia, Fundamentação Física e Guia de Aplicação de Bordo.

---

## 📄 Apresentação e Propósito

Este manual foi escrito especificamente para **Engenheiros Navais, Engenheiros Mecânicos, Projetistas de Tubulações, Chefes de Máquinas e Inspetores de Sociedades Classificadoras**. Não é necessário ter conhecimento em programação para compreender ou utilizar os conceitos e resultados descritos aqui.

### Por que esta ferramenta foi criada?
No projeto de tubulações e plantas de bombeamento de embarcações (como rebocadores, navios mercantes, embarcações de apoio offshore PSV e embarcações militares), o cálculo manual ou via planilhas eletrônicas convencionais apresenta sérias limitações:
1. **Negligência da Inclinação 3D**: Planilhas comuns calculam o sistema apenas em condição estática ("em prumo"). No mar, a embarcação sofre Trim (arfagem/pitch), balanço (rolamento/roll) e condições de avaria (alagamento assimétrico), alterando a altura estática do fluido e podendo causar **cavitação severa e perda de sucção da bomba**.
2. **Erros em Curvas de Bombas**: O uso de interpolação polinomial simples (spline cúbica) em curvas planas de bombas pode criar oscilações numéricas falsas (*overshoot*), prevendo pontos de operação inexistentes ou irreais.
3. **Não-Conformidade Normativa**: O não cumprimento automático dos limites de velocidade de água do mar impostos por Sociedades Classificadoras (Bureau Veritas, Lloyd's Register, DNV, ABS) pode gerar corrosão-erosão precoce em tubulações de cuproníquel ou sedimentação na sucção.

A **Naval Hydraulic Calculator API** resolve esses problemas ao integrar um **motor matemático rigoroso**, varredura espacial tridimensional das **9 condições de inclinação naval** e validação direta contra regras de classe e normas SOLAS/NORMAM.

---

## 📋 Sumário

1. [O Que o Sistema Calcula (Visão Geral das Capacidades)](#1-o-que-o-sistema-calcula-visão-geral-das-capacidades)
2. [Exemplos Práticos e Casos de Estudo de Bordo](#2-exemplos-práticos-e-casos-de-estudo-de-bordo)
   - [Caso 1: Resfriamento de Água do Mar do Motor Principal](#caso-1-resfriamento-de-água-do-mar-do-motor-principal-me)
   - [Caso 2: Transferência de Óleo Combustível MDO/HFO](#caso-2-transferência-de-óleo-combustível-mdo-hfo)
   - [Caso 3: Esgoto de Porão e Lastro sob Avaria Extrema](#caso-3-esgoto-de-porão-e-lastro-sob-avaria-extrema)
   - [Caso 4: Sistema de Combate a Incêndio de Bordo](#caso-4-sistema-de-combate-a-incêndio-de-bordo)
3. [Como Estruturar os Dados de Entrada do Seu Projeto](#3-como-estruturar-os-dados-de-entrada-do-seu-projeto)
4. [Como Interpretar os Resultados e Tomar Decisões](#4-como-interpretar-os-resultados-e-tomar-decisões)
5. [Fundamentação Teórica, Fórmulas e Normas](#5-fundamentação-teórica-fórmulas-e-normas)

---

## 1. O Que o Sistema Calcula (Visão Geral das Capacidades)

O sistema analisa uma instalação de tubulação completa (da tomada de água no casco até o ponto de descarga final) e realiza as seguintes etapas encadeadas de cálculo:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          FLUXO INTEGRADO DE CÁLCULO                             │
└─────────────────────────────────────────────────────────────────────────────────┘
  1. CONVERSÃO E VALIDAÇÃO DA TOPOLOGIA
     ↳ Converte unidades (m³/h, bar, mm, °C) para o SI.
     ↳ Rejeita sistemas inválidos (ex: malhas fechadas/anéis).
                                    │
                                    ▼
  2. PROPRIEDADES DO FLUIDO E REGIME DE ESCOAMENTO
     ↳ Calcula densidade (ρ), viscosidade (μ, ν) e Número de Reynolds (Re).
     ↳ Identifica regime: Laminar (Re < 2000), Transição ou Turbulento (Re > 4000).
                                    │
                                    ▼
  3. PERDAS DE CARGA (DISTRIBUÍDAS E LOCALIZADAS)
     ↳ Calcula o fator de atrito (f) via Churchill (contínuo) ou Colebrook.
     ↳ Avalia perda em tubos retos (Darcy-Weisbach) e conexões/válvulas (K ou Le/D).
     ↳ Aplica trava de segurança para Hazen-Williams (com fallback automático).
                                    │
                                    ▼
  4. INTERPOLAÇÃO DA BOMBA E PONTO DE OPERAÇÃO
     ↳ Interpola curvas H×Q, η×Q e NPSHr×Q usando PCHIP (sem overshoot).
     ↳ Cruzamento quadrático H_sistema(Q) = H_geo + k_sys·Q².
     ↳ Executa os Checks F3: Rejeita se H_shutoff < H_geo ou se Q_op > Q_max.
                                    │
                                    ▼
  5. VARREDURA 3D DE INCLINAÇÃO NAVAL (9 CONDIÇÕES)
     ↳ Aplica rotação espacial R(θ, φ) para Trim (pitch) e Banda (roll).
     ↳ Calcula o NPSH Disponível (NPSHa) em cada uma das 9 posições navais.
     ↳ Identifica a Condição Crítica de Avaria (ex: +10° Trim, +22.5° banda).
                                    │
                                    ▼
  6. VERIFICAÇÃO NORMATIVA E DIMENSIONAMENTO ELETROMECÂNICO
     ↳ Compara velocidades na sucção e descarga contra limites BV / LR / ABS.
     ↳ Avalia redundância (N ≥ 2 bombas essenciais) e fontes de energia.
     ↳ Calcula potências (Hidráulica, Eixo com 25% margem naval, Elétrica).
     ↳ Seleciona a carcaça comercial do motor elétrico ABNT em CV.
     ↳ Emite o Status Final: "OK", "AVISO" ou "REPROVADO".
```

---

## 2. Exemplos Práticos e Casos de Estudo de Bordo

### Caso 1: Resfriamento de Água do Mar do Motor Principal (ME)

#### ⚓ Cenário Real:
Um navio mercante necessita dimensionar o sistema de resfriamento central de água do mar para o Motor Principal. A água do mar é captada na caixa de mar (*sea chest* / kingston) localizada no fundo do casco, bombeada até os trocadores de calor de placas e descartada na bordada acima da linha d'água.

```
 [Caixa de Mar] ──> [Válvula Kingston] ──> [Tubulação Sucção] ──> [BOMBA CENTRÍFUGA]
                                                                        │
 [Bordada (Descarte)] <── [Resfriador Placas] <── [Tubulação Descarga] <┘
```

#### 📥 Dados de Entrada do Projeto:
- **Fluido**: Água do mar a $32^\circ\text{C}$ ($\rho = 1025 \text{ kg/m}^3$, $\mu = 0.001 \text{ Pa}\cdot\text{s}$, $P_v = 4800 \text{ Pa}$).
- **Vazão requerida**: $118.5 \text{ m}^3/\text{h}$ ($0.0329 \text{ m}^3/\text{s}$).
- **Geometria dos Pontos (Coordenadas em relação ao centro de rotação da embarcação)**:
  - Tomada de Sucção (Kingston): $z = 0.8 \text{ m}$
  - Flange de Entrada da Bomba: $z = 1.5 \text{ m}$ (Sucção estática $= -0.7 \text{ m}$)
  - Ponto de Descarga (Resfriador): $z = 4.2 \text{ m}$ (Altura geométrica total $H_{\text{geo}} = 3.4 \text{ m}$)
- **Tubulação de Sucção**: Diâmetro $150 \text{ mm}$ ($6''$), comprimento $8.5 \text{ m}$, Aço Inox 304, com 1 Válvula Gaveta, 2 Curvas 90° RL, 1 Válvula de Retenção e filtro de sucção ($h_{\text{equip}} = 3.62 \text{ m}$).
- **Tubulação de Descarga**: Diâmetro $125 \text{ mm}$ ($5''$), comprimento $15.2 \text{ m}$, Aço Inox 304, com 3 Curvas 90° RL, 1 Tê passagem direta.
- **Bomba Fornecida (Grundfos NK 100-315, 1450 rpm)**: Curva H×Q ($0\text{ m}^3/\text{h} \rightarrow 42\text{ m}$; $118.5\text{ m}^3/\text{h} \rightarrow 36\text{ m}$; $180\text{ m}^3/\text{h} \rightarrow 18\text{ m}$).

#### 📤 Resultados Obtidos pelo Sistema:

| Grandeza Calculada | Valor Obtido | Avaliação de Engenharia |
|---|---|---|
| **Velocidade na Sucção** | $1.87 \text{ m/s}$ | ⚠️ **Aviso de Classe**: Acima do ideal ($1.2 \text{ m/s}$) para linhas de água salgada em uso contínuo (recomenda-se elevar o diâmetro para $200 \text{ mm}$). |
| **Velocidade na Descarga** | $2.69 \text{ m/s}$ | ✅ **Conforme**: Dentro da faixa permitida ($1.5 \text{ a } 3.0 \text{ m/s}$). |
| **Número de Reynolds (Sucção)** | $287.000$ | Regime Plenamente Turbulento ($Re > 4000$). |
| **Altura Manométrica Total** | $8.45 \text{ m}$ | Carga estática ($3.40\text{m}$) + Perdas distribuídas/localizadas ($5.05\text{m}$). |
| **NPSH Disponível (Prumo)** | $4.85 \text{ m}$ | ✅ **Seguro**: Maior que o $\text{NPSHr}$ da bomba ($3.20 \text{ m}$) + margem de $0.5 \text{ m}$. |
| **NPSH Disponível (Avaria BB)** | $4.43 \text{ m}$ | ✅ **Seguro em Avaria**: Mesmo com Trim de $10^\circ$ e banda de $22.5^\circ$, o $\text{NPSHa}$ permanece acima de $3.70 \text{ m}$. |
| **Velocidade Específica ($N_s$)** | $63.7$ | Classificação física: **Bomba Centrífuga Mista**. |
| **Motor Elétrico Requerido** | **7.5 CV** (ABNT) | Potência hidráulica $= 2.80 \text{ kW} \implies P_{\text{eixo}} = 3.54 \text{ kW}$. Com $25\%$ de margem naval $\implies 4.43 \text{ kW} = 6.02 \text{ CV} \implies$ Comercial **7.5 CV**. |
| **STATUS GERAL** | **`OK`** | Instalação aprovada operacionalmente. |

---

### Caso 2: Transferência de Óleo Combustível MDO/HFO

#### ⚓ Cenário Real:
Transferência de óleo combustível pesado (HFO) aquecido ou óleo diesel marinho (MDO) a $40^\circ\text{C}$ de um tanque de fundo duplo para o tanque diário de serviço.

#### 📥 Dados de Entrada:
- **Fluido**: Óleo Combustível Pesado ($\rho = 890 \text{ kg/m}^3$, viscosidade cinemática $\nu = 110 \text{ cSt} = 1.1 \times 10^{-4} \text{ m}^2/\text{s}$).
- **Vazão**: $25 \text{ m}^3/\text{h}$, Tubulação de $80 \text{ mm}$ ($3''$).

#### 📤 Comportamento Físico Calculado pelo Sistema:
1. **Número de Reynolds**: $Re \approx 805$ ($Re < 2000$).
2. **Regime de Escoamento**: **Laminar**.
3. **Fator de Atrito**: O sistema automaticamente utiliza Poiseuille / Churchill ($f = 64 / 805 = 0.0795$), que é cerca de $4 \times$ maior que o fator de atrito da água!
4. **Tratamento de Hazen-Williams**: Se o usuário solicitar o uso de Hazen-Williams para esta linha de óleo, o sistema **rejeita automaticamente o método HW** por violação da norma (fluido não-água e regime laminar) e executa o cálculo correto via **Darcy-Weisbach**, emitindo o seguinte aviso:
   > *"Método Hazen-Williams incompatível para o fluido óleo. Fallback automático executado para Darcy-Weisbach."*

---

### Caso 3: Esgoto de Porão e Lastro sob Avaria Extrema

#### ⚓ Cenário Real:
Dimensionamento da bomba de esgoto da praça de máquinas. Em uma situação de emergência (colisão ou rasgo no casco), a embarcação adquire uma inclinação permanente de **$10^\circ$ de Trim (posição embicada) e $22.5^\circ$ de adernamento para o bordo de bombordo (BB)**.

```
 CONDIÇÃO DE PRUMO (0°, 0°)              CONDIÇÃO DE AVARIA EXTREMA (+10°, +22.5°)
      ┌───────────┐                           ┌───────────┐
      │   Bomba   │                           │   Bomba   │\
      └─────┬─────┘                           └─────┬─────┘ \
            │                                       │        \  Linha d'água inclinada
   ~~~~~~~~~┴~~~~~~~~~ Lâmina d'água       ~~~~~~~~~┴~~~~~~~~~\
```

#### 📤 Análise de Inclinação 3D Executada pelo Sistema:
O sistema calcula a cota estática efetiva do ponto de captação para cada uma das 9 condições navais:

```
  [1] Prumo (0°, 0°)                   ──> NPSHa = 4.85 m (Status: OK)
  [2] Trim a Vante (+5°, 0°)        ──> NPSHa = 4.75 m (Status: OK)
  [3] Trim a Ré (-5°, 0°)           ──> NPSHa = 4.90 m (Status: OK)
  [4] Banda BE (0°, +15°)              ──> NPSHa = 4.65 m (Status: OK)
  [5] Banda BB (0°, -15°)              ──> NPSHa = 4.60 m (Status: OK)
  [6] Combinado BE/Vante (+5°, +15°)   ──> NPSHa = 4.57 m (Status: OK)
  [7] Combinado BB/Ré (-5°, -15°)      ──> NPSHa = 4.55 m (Status: OK)
  [8] Avaria BE (+5°, +22.5°)          ──> NPSHa = 4.47 m (Status: OK)
  [9] Avaria BB (+10°, +22.5°) [CRÍTICA] ─> NPSHa = 4.43 m (Status: OK)
```

#### 💡 O que aconteceria se a bomba estivesse em uma cota elevada?
Se o flange da bomba estivesse posicionado a $z = 3.0 \text{ m}$ em relação ao fundo, o $\text{NPSHa}$ em avaria cairia para $2.90 \text{ m}$ (abaixo do $\text{NPSHr} + \text{margem} = 3.70 \text{ m}$). 
O sistema emitiria imediatamente o status **`AVISO`** ou **`REPROVADO`**, indicando o risco iminente de a bomba entrar em cavitação e parar de esgotar o porão justamente no momento da emergência.

---

### Caso 4: Sistema de Combate a Incêndio de Bordo

#### ⚓ Cenário Real:
Dimensionamento da bomba principal de incêndio conforme exigências SOLAS (Safety of Life at Sea). O sistema deve alimentar os hidrantes do convés principal e da superestrutura com pressão mínima nos esguichos.

#### 📤 Regras de Redundância e Proteção Avaliadas pelo Sistema:
1. **Pressão Manométrica Mínima**: O sistema calcula a altura manométrica necessária ($H \ge 45 \text{ m}$) para vencer a altura do passadiço e a perda nos mangotes.
2. **Redundância SOLAS**: Se o usuário marcar o sistema como `"sistema_essencial": true` e informar apenas 1 bomba (`"numero_bombas": 1`), o sistema reprova o projeto emitindo o alerta:
   > *"`REPROVADO`: Sistemas essenciais de combate a incêndio exigem no mínimo 2 bombas com fontes de energia independentes (uma acionada pelo gerador principal e outra por motor diesel dedicado ou gerador de emergência)."*

---

## 3. Como Estruturar os Dados de Entrada do Seu Projeto

Para enviar o seu projeto para a API (ou preencher o arquivo de entrada), você precisa organizar as informações em **5 Blocos Principais**. Não se preocupe com termos de programação; veja abaixo o significado simples de cada campo:

### 1. Bloco `projeto` (Identificação)
- `nome`: Nome do projeto (ex: `"Sistema de Resfriamento — Rebocador 80t BP"`).
- `navio`: Nome ou casco da embarcação (ex: `"Hull 124"`).
- `classificadora`: Sigla da sociedade classificadora (`"BV"`, `"LR"`, `"ABS"`, `"DNV"`).

### 2. Bloco `fluido` (Características do Líquido)
- `tipo`: `"agua_doce"`, `"agua_salgada"`, `"oleo_lubrificante"`, `"oleo_combustivel"`.
- `temperatura_C`: Temperatura de operação em ${^\circ}\text{C}$ (ex: `32`).
- `densidade_kg_m3`: Densidade do fluido (ex: `1025` para água do mar, `1000` para água doce).
- `viscosidade_dinamica_Pa_s`: Viscosidade (ex: `0.001` para água a $20^\circ\text{C}$).

### 3. Bloco `sistema` (Parâmetros da Linha)
- `vazao`: Vazão desejada do sistema (ex: `118.5`).
- `unidade_vazao`: Unidade em que você informou a vazão (`"m3h"` para $\text{m}^3/\text{h}$, `"l/min"` para Litros/min, `"l/s"` para Litros/seg).
- `pontos_sistema`: Elevação em metros de cada ponto:
  - `succao`: Altura da captação (ex: `z_m: 0.8`).
  - `bomba`: Altura do eixo da bomba (ex: `z_m: 1.5`).
  - `descarga`: Altura do ponto final de descarte (ex: `z_m: 4.2`).
- `sistema_essencial`: `true` se o sistema for vital para a navegação (incêndio, esgoto, resfriamento ME) ou `false` se for serviço geral.
- `numero_bombas`: Quantidade de bombas instaladas na praça de máquinas (ex: `2`).
- `alimentacoes_independentes`: `true` se as bombas tiverem quadros elétricos/motores separados.

### 4. Bloco `trechos` (Tubulações e Conexões)
Uma lista contendo o trecho de **Sucção** (do mar à bomba) e o trecho de **Descarga** (da bomba ao destino):
- `id`: Identificador (`"S1"` para sucção, `"D1"` para descarga).
- `diametro_interno_mm`: Diâmetro interno do tubo em milímetros (ex: `150` para $6''$).
- `comprimento_m`: Comprimento total reto em metros (ex: `8.5`).
- `rugosidade_mm`: Rugosidade do tubo em mm (ex: `0.02` para Aço Inox, `0.046` para Aço Carbono).
- `perda_equipamento_m`: Perda de carga fixa em metros causada por equipamentos especiais no trecho (ex: trocador de calor de placas $= 3.62 \text{ m}$).
- `singularidades`: Lista de válvulas e curvas presentes no trecho (ex: `{"tipo": "valvula_gaveta", "quantidade": 1}`).

### 5. Bloco `bomba` (Curva do Fabricante)
- `rotacao_rpm`: Rotação nominal da bomba (ex: `1450` rpm).
- `curva_hq`: Lista de pontos da curva de vazão × altura manométrica do catálogo do fabricante:
  - Ex: `[{"Q_m3h": 0, "H_m": 42}, {"Q_m3h": 118.5, "H_m": 36}, {"Q_m3h": 180, "H_m": 18}]`
- `curva_npsh`: Lista de pontos da curva de $\text{NPSHr}$ do catálogo.
- `curva_eta`: Lista de pontos da curva de rendimento $\eta\%$ do catálogo.

---

## 4. Como Interpretar os Resultados e Tomar Decisões

Ao processar o seu projeto, o sistema retorna um relatório completo. Veja abaixo como interpretar cada campo e qual ação de engenharia tomar:

### 🚦 Significado dos Status Globais:

```
 🟢 STATUS: "OK"
    Meaning: O projeto está totalmente aprovado!
    - O NPSHd é suficiente em todas as 9 condições navais (prumo e avaria).
    - As velocidades estão dentro dos limites da Sociedade Classificadora.
    - A bomba opera perto do ponto BEP de máxima eficiência.
    - As regras de redundância SOLAS/NORMAM foram cumpridas.

 🟡 STATUS: "AVISO"
    Meaning: O projeto funciona, mas requer atenção operacional ou pequenos ajustes!
    - Exemplos: O NPSH passa em prumo, mas fica apertado em condição de avaria extrema;
      ou a bomba está operando um pouco fora da faixa ideal de rendimento (BEP);
      ou a velocidade na tubulação está ligeiramente acima da recomendação da classe.
    - Ação: Avaliar os alertas emitidos no relatório antes de fechar o projeto executivo.

 🔴 STATUS: "REPROVADO"
    Meaning: O projeto possui não-conformidade grave ou risco de falha!
    - Causa 1: A bomba entra em cavitação severa na condição de prumo (NPSHa < NPSHr).
    - Causa 2: A bomba escolhida não tem pressão suficiente para vencer a cota estática (H_shutoff < H_geo).
    - Causa 3: Um sistema essencial de bordo possui apenas 1 bomba sem reserva.
    - Ação: Redimensionar o sistema obrigatoriamente antes da aprovação de classe.
```

---

### 🔧 O que fazer quando o resultado der "AVISO" ou "REPROVADO"?

| Problema Identificado no Relatório | Causa Física | Ação de Engenharia Recomendada |
|---|---|---|
| `NPSHa < NPSHr` (Cavitação) | Pressão na entrada da bomba menor que a pressão de vapor do fluido. | 1. **Aumentar o diâmetro** da tubulação de sucção (ex: de $125\text{mm}$ para $150\text{mm}$).<br>2. **Rebaixar a bomba** na praça de máquinas (aproximá-la da linha de base).<br>3. Reduzir o comprimento ou quantidade de curvas na sucção.<br>4. Selecionar uma bomba com menor $\text{NPSHr}$. |
| `SEM_PONTO_OPERACAO_SHUT_OFF` | A altura manométrica de corte da bomba é menor que a altura do prédio/embarcação ($H_{\text{shut-off}} < H_{\text{geo}}$). | 1. Selecionar uma bomba com **maior diâmetro de impulsor** ou maior rotação.<br>2. Associar duas bombas em **série**. |
| Velocidade de Sucção $> 1.2 \text{ m/s}$ | Tubulação de sucção subdimensionada para o fluxo exigido. | Aumentar o diâmetro comercial do tubo de sucção para evitar erosão acelerada. |
| Status BEP `= ALERTA` | A bomba está operando muito estrangulada ou muito aberta ($\frac{Q_{\text{op}}}{Q_{\text{BEP}}} < 50\%$ ou $> 130\%$). | Escolher um modelo de bomba cujo ponto de maior eficiência ($Q_{\text{BEP}}$) seja mais próximo da vazão de projeto. |

---

## 5. Fundamentação Teórica, Fórmulas e Normas

Para fins de memória de cálculo técnica e auditoria de classe, esta seção apresenta a síntese de todas as equações empregadas no motor de cálculo.

### 5.1 Fator de Atrito de Darcy ($f$) — Fórmula de Churchill

Adotada por ser **rigorosamente contínua** em todas as regiões de Reynolds (sem descontinuidade na transição $2000 \le Re \le 4000$):

$$f = 8 \cdot \left[ \left( \frac{8}{Re} \right)^{12} + \frac{1}{(A + B)^{1.5}} \right]^{1/12}$$

$$\text{onde: } A = \left[ 2.457 \cdot \ln \left( \frac{1}{\left( \frac{7}{Re} \right)^{0.9} + 0.27 \cdot \frac{\varepsilon}{D}} \right) \right]^{16} \quad \text{e} \quad B = \left( \frac{37530}{Re} \right)^{16}$$

---

### 5.2 Rotação 3D da Cota Estática — Matriz de Inclinação

Dado o vetor posição $\vec{P} = (x, y, z)$ de um ponto de tubulação em prumo, sua nova cota $z'$ sob Trim $\theta$ (pitch) e banda $\phi$ (roll) é calculada por:

$$z'(\theta, \phi) = -x \cdot \sin\theta \cdot \cos\phi + y \cdot \sin\phi + z \cdot \cos\theta \cdot \cos\phi$$

A variação de altura estática relativa na sucção $\Delta Z_{\text{efetivo}}$ altera o $\text{NPSHa}$ pela relação:

$$\text{NPSHa}(\theta, \phi) = \frac{P_{\text{atm}} - P_v(T)}{\rho \cdot g} + z'_{\text{suc}}(\theta, \phi) - h_{\text{perda, suc}} - \frac{v_{\text{suc}}^2}{2g}$$

---

### 5.3 Leis de Afinidade (Variação de Rotação $N$ e Diâmetro do Impulsor $D$)

Utilizadas para simulação de Inversores de Frequência (VFD) ou rebaixamento mecânico de rotor:

- **Variação de Rotação ($N_1 \rightarrow N_2$)**:
  $$Q_2 = Q_1 \cdot \left(\frac{N_2}{N_1}\right), \quad H_2 = H_1 \cdot \left(\frac{N_2}{N_1}\right)^2, \quad P_2 = P_1 \cdot \left(\frac{N_2}{N_1}\right)^3$$

- **Rebaixamento de Impulsor ($D_1 \rightarrow D_2$)** (Válido para $D_2/D_1 \ge 0.80$):
  $$Q_2 = Q_1 \cdot \left(\frac{D_2}{D_1}\right), \quad H_2 = H_1 \cdot \left(\frac{D_2}{D_1}\right)^2, \quad P_2 = P_1 \cdot \left(\frac{D_2}{D_1}\right)^3$$

---

### 5.4 Referências Normativas Adotadas

1. **Bureau Veritas (BV) Rules for the Classification of Steel Ships**: Part C, Chap 1, Sec 10 (Piping Systems).
2. **American Bureau of Shipping (ABS)**: Rules for Building and Classing Marine Vessels (Part 4 - Vessel Systems and Machinery).
3. **Lloyd's Register (LR)**: Rules and Regulations for the Classification of Ships (Part 5 - Main and Auxiliary Machinery).
4. **SOLAS (Safety of Life at Sea)**: Chapter II-1, Regulation 35-1 (Bilge pumping arrangements) & Regulation 10 (Fire pumps).
5. **NORMAM 01/DTM**: Normas da Autoridade Marítima para Embarcações Empregadas na Navegação em Mar Aberto.
6. **Hydraulic Institute (HI) / API 610**: Centrifugal Pumps for Petroleum, Petrochemical and Natural Gas Industries (NPSH margin standards).
7. **ISO 9906**: Rotodynamic pumps — Hydraulic performance acceptance tests — Grades 1, 2 and 3.
