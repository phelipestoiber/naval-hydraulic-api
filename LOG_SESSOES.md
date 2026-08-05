# LOG DE SESSÕES — Naval Hydraulic Calculator API

**Propósito:** memória de longo prazo entre sessões do agente. Este arquivo é lido por inteiro no início de toda sessão — por isso cada entrada deve ser densa e escaneável, não narrativa.

**Relação com `INSTRUCOES_AGENTE.md`:** o bloco "Estado Atual" naquele arquivo é o snapshot (onde estou agora). Este arquivo é o histórico completo (como cheguei aqui, o que já foi tentado). Sempre ler os dois — o Estado Atual primeiro, depois este arquivo inteiro.

---

## Índice de Lições Rastreáveis

Toda entrada com impacto além da própria sessão recebe uma tag `LICAO-NNN`. Use este índice para referenciar uma lição de sessões anteriores sem precisar reler o log inteiro em busca dela.

| Tag | Resumo em uma linha | Sessão |
|---|---|---|
| — | (nenhuma lição registrada ainda) | — |

---

## Como Preencher Uma Entrada

Copiar o template abaixo, preencher, colar no topo da seção "Entradas" (ordem cronológica reversa — mais recente primeiro). Se a sessão gerou uma lição reutilizável, adicionar a tag ao Índice acima também.

```markdown
### [DATA ISO] — vX.Y.Z — [título curto do escopo da sessão]

**Objetivo da sessão:** o que estava planejado ao iniciar.

**Feito:**
- lista curta, uma linha por item, módulo/teste tocado

**Por quê:** a decisão técnica que não é óbvia só de olhar o roadmap —
  o "porquê" que já está no roadmap não precisa ser repetido aqui.

**Deu certo:**
- o que funcionou como esperado, sem surpresas relevantes

**Deu errado / retrabalho:** [ou "nada a registrar"]
- o que foi tentado e não funcionou, e o que foi feito em vez disso
- se isso é uma lição reutilizável, marcar: `[LICAO-NNN]`

**Estado ao final:** testes passando/total; cobertura; bloqueios abertos
```

**Regra de densidade:** se a entrada não tem nada relevante em "Deu errado", escrever "nada a registrar" — não inventar conteúdo para preencher a seção. Entradas sem atrito real devem ser as mais curtas do log, não as mais longas.

---

## Entradas

### 2026-08-04 — v0.8.0 — Schemas Pydantic, Serialização e Endpoints REST

**Objetivo da sessão:** Implementar a camada API HTTP utilizando FastAPI, definir os schemas Pydantic de entrada/saída, criar os endpoints para fluidos, perda de carga, bombas, cavitação e motores, e configurar tratamento padronizado de exceções (`ErrorResponse` em HTTP 400 e 422) por TDD estrito.

**Feito:**
- Criados os schemas Pydantic em `app/schemas/`: [fluido.py](file:///C:/Users/afmn/Desktop/naval-hydraulic-api/app/schemas/fluido.py), [perda_carga.py](file:///C:/Users/afmn/Desktop/naval-hydraulic-api/app/schemas/perda_carga.py), [bomba.py](file:///C:/Users/afmn/Desktop/naval-hydraulic-api/app/schemas/bomba.py), [cavitacao.py](file:///C:/Users/afmn/Desktop/naval-hydraulic-api/app/schemas/cavitacao.py) e [motor.py](file:///C:/Users/afmn/Desktop/naval-hydraulic-api/app/schemas/motor.py)
- Criados os endpoints REST em `app/api/v1/endpoints/`:
  - `POST /api/v1/fluidos/propriedades`
  - `POST /api/v1/perda-carga/darcy-weisbach`
  - `POST /api/v1/perda-carga/hazen-williams`
  - `POST /api/v1/perda-carga/singularidades`
  - `POST /api/v1/bombas/ponto-operacao`
  - `POST /api/v1/cavitacao/npsh`
  - `POST /api/v1/motores/dimensionamento`
- Criado [router.py](file:///C:/Users/afmn/Desktop/naval-hydraulic-api/app/api/v1/router.py) agregando todos os sub-roteadores sob o prefixo `/api/v1`
- Criado [main.py](file:///C:/Users/afmn/Desktop/naval-hydraulic-api/app/main.py) com a instância FastAPI, suporte a CORS, rota `/health` e exception handlers estruturados para `ErroCalculo` (HTTP 400) e `RequestValidationError` (HTTP 422)
- Criados 5 arquivos de testes de integração HTTP em `tests/integration/`: `test_api_fluidos.py`, `test_api_perda_carga.py`, `test_api_bombas.py`, `test_api_cavitacao.py` e `test_api_motores.py`

**Por quê:** Iniciar a Fase 4 (Camada API), expondo todo o motor de cálculo hidráulico da aplicação através de endpoints REST acessíveis por clientes HTTP.

**Deu certo:**
- 71/71 testes (unitários + integração) passando com 99% de cobertura global
- Endpoint `/api/v1/fluidos/propriedades` retornando vazão, Reynolds e regime ($T8.1$) com validação 422 para entradas inválidas
- Endpoint `/api/v1/perda-carga/hazen-williams` disparando fallback automático para Darcy-Weisbach e retornando 200 OK com aviso estruturado para fluidos não-água ($T8.2$)
- Endpoint `/api/v1/bombas/ponto-operacao` retornando Ponto de Operação ($T8.3$) e disparando HTTP 400 estruturado (`SEM_PONTO_OPERACAO_SHUT_OFF`) com diagnóstico quando $H_{\text{geo}} > H_{\text{shut\_off}}$
- Endpoints de cavitação e motores dimensionando corretamente os componentes com 100% de cobertura de código API

**Deu errado / retrabalho:**
- nada a registrar

**Estado ao final:** 71/71 testes passando; 99% cobertura global; 0 bloqueios abertos

---

### 2026-08-04 — v0.7.0 — Leis de Semelhança (VFD) e Diâmetro de Impulsor

**Objetivo da sessão:** Implementar as Leis de Afinidade/Semelhança para ajuste de curva de bomba por variação de rotação ($N_2/N_1$) e rebaixamento de impulsor ($D_2/D_1$), além da variação de velocidade por Inversor de Frequência (VFD) por TDD estrito.

**Feito:**
- Criado [leis_semelhanca.py](file:///C:/Users/afmn/Desktop/naval-hydraulic-api/app/core/motores/leis_semelhanca.py) aplicando as Leis de Afinidade para $Q_2$, $H_2$, $P_2$ e $\text{NPSHr}_2$, com emissão de alerta se o rebaixamento de impulsor exceder 20% ($D_2/D_1 < 0.80$)
- Criado [inversor.py](file:///C:/Users/afmn/Desktop/naval-hydraulic-api/app/core/motores/inversor.py) calculando a velocidade ajustada $N(f) = N_{\text{nom}} \cdot (f_{\text{op}}/f_{\text{nom}})$ e avaliando os alertas operacionais `ALERTA_FREQUENCIA_BAIXA` ($f_{\text{op}} < 30$ Hz) e `ALERTA_SOBREFREQUENCIA` ($f_{\text{op}} > 60$ Hz)
- Criado [test_leis_semelhanca.py](file:///C:/Users/afmn/Desktop/naval-hydraulic-api/tests/unit/test_leis_semelhanca.py) validando a variação de rotação $1750 \rightarrow 1400$ rpm ($T7.1$) e rebaixamento de impulsor $250 \rightarrow 225$ mm ($T7.2$)
- Criado [test_inversor.py](file:///C:/Users/afmn/Desktop/naval-hydraulic-api/tests/unit/test_inversor.py) validando operação do VFD a $45$ Hz ($T7.3$) e alertas a $20$ Hz e $65$ Hz ($T7.4$)

**Por quê:** Concluir a Fase 3 (Motores, Consumos e Inversor de Frequência), permitindo a simulação do comportamento operacional da bomba sob modulação de frequência ou ajuste mecânico de rotor antes de disponibilizar as APIs REST FastAPI.

**Deu certo:**
- 59/59 testes unitários passando com 99% de cobertura global
- Leis de Afinidade validadas: $Q_2 = 80\text{ m}^3/\text{h}$, $H_2 = 25.6\text{ m}$, $P_2 = 7.68\text{ kW}$ para redução de $20\%$ na rotação ($T7.1$)
- Rebaixamento de impulsor validado: $Q_2 = 90\text{ m}^3/\text{h}$, $H_2 = 32.4\text{ m}$ para corte de $10\%$ no diâmetro ($T7.2$)
- Operação em VFD ajustando rotação nominal para $1312.5\text{ rpm}$ a $45\text{ Hz}$ com status `OK` ($T7.3$)
- Proteção térmica do motor disparada a $20\text{ Hz}$ (`ALERTA_FREQUENCIA_BAIXA`) ($T7.4$)

**Deu errado / retrabalho:**
- nada a registrar

**Estado ao final:** 59/59 testes passando; 99% cobertura global; 0 bloqueios abertos

---

### 2026-08-04 — v0.6.0 — Motor Elétrico, Rendimento Global e Consumo de Combustível

**Objetivo da sessão:** Implementar o cálculo da potência hidráulica $P_{\text{hid}}$, potência no eixo da bomba $P_{\text{eixo}}$, potência elétrica $P_{\text{elet}}$, corrente nominal trifásica $I_{\text{nom}}$, rendimento global da cadeia de acionamento $\eta_{\text{global}}$ e consumo de combustível diesel por TDD estrito.

**Feito:**
- Criado [eletrico.py](file:///C:/Users/afmn/Desktop/naval-hydraulic-api/app/core/motores/eletrico.py) calculando $P_{\text{hid}}$, $P_{\text{eixo}}$, $P_{\text{elet}}$ e a corrente nominal trifásica $I_{\text{nom}} = \frac{P_{\text{elet}} \cdot 1000}{\sqrt{3} \cdot V \cdot \text{FP}}$
- Criado [rendimento_global.py](file:///C:/Users/afmn/Desktop/naval-hydraulic-api/app/core/motores/rendimento_global.py) calculando o rendimento global da cadeia de acionamento ($\eta_{\text{global}} = \eta_{\text{bomba}} \cdot \eta_{\text{motor}} \cdot \eta_{\text{transmissao}}$)
- Criado [consumo_diesel.py](file:///C:/Users/afmn/Desktop/naval-hydraulic-api/app/core/motores/consumo_diesel.py) calculando o consumo horário de combustível diesel em g/h e em L/h ($\text{consumo\_lh} = \frac{P_{\text{eixo}} \cdot \text{SFC}}{\rho_{\text{diesel}}}$)
- Criado [test_motor_eletrico.py](file:///C:/Users/afmn/Desktop/naval-hydraulic-api/tests/unit/test_motor_eletrico.py) validando $P_{\text{hid}} \approx 2.73\text{ kW}$, $P_{\text{elet}} \approx 3.75\text{ kW}$ e $I_{\text{nom}} \approx 6.71\text{ A}$ ($T6.1$)
- Criado [test_rendimento_global.py](file:///C:/Users/afmn/Desktop/naval-hydraulic-api/tests/unit/test_rendimento_global.py) validando $\eta_{\text{global}} \approx 71.2\%$ ($T6.2$)
- Criado [test_consumo_diesel.py](file:///C:/Users/afmn/Desktop/naval-hydraulic-api/tests/unit/test_consumo_diesel.py) validando o consumo de combustível diesel $0.85\text{ L/h}$ ($\pm 2\%$) ($T6.3$)

**Por quê:** Iniciar a Fase 3 (Motores, Consumos e Inversor de Frequência), permitindo o dimensionamento eletromecânico e a avaliação de custos energéticos e operacionais da planta naval.

**Deu certo:**
- 53/53 testes unitários passando com 99% de cobertura global
- Potência hidráulica ($2.73\text{ kW}$) e corrente nominal trifásica ($6.71\text{ A}$) coincidindo exatamente com os valores de especificação ($T6.1$)
- Rendimento global da cadeia acionadora obtido de $71.2\%$ ($T6.2$)
- Consumo horário de óleo diesel naval resultando em $0.85\text{ L/h}$ ($T6.3$)

**Deu errado / retrabalho:**
- nada a registrar

**Estado ao final:** 53/53 testes passando; 99% cobertura global; 0 bloqueios abertos

---

### 2026-08-04 — v0.5.0 — NPSH, Margem de Cavitação e Temperatura Crítica

**Objetivo da sessão:** Implementar o cálculo da pressão de vapor $P_v(T)$ via Equação de Antoine, determinação do NPSH disponível ($\text{NPSHa}$), avaliação da margem de cavitação ($\text{NPSHa} - \text{NPSHr}$) e determinação da temperatura crítica de cavitação $T_{\text{crit}}$ por TDD estrito.

**Feito:**
- Criado [pressao_vapor.py](file:///C:/Users/afmn/Desktop/naval-hydraulic-api/app/core/cavitacao/pressao_vapor.py) com a Equação de Antoine $\log_{10}(P_v) = A - \frac{B}{T + C}$ para água e outros fluidos
- Criado [npsh.py](file:///C:/Users/afmn/Desktop/naval-hydraulic-api/app/core/cavitacao/npsh.py) calculando $\text{NPSHa} = \frac{P_{\text{atm}} - P_v}{\rho \cdot g} + Z_{\text{suc}} - h_{f,\text{suc}}$
- Criado [margem.py](file:///C:/Users/afmn/Desktop/naval-hydraulic-api/app/core/cavitacao/margem.py) calculando a margem de cavitação e avaliando o status operacional (`OK` vs `ALERTA_CAVITACAO`) com margem mínima requerida conforme a norma API 610 / HI ($\Delta_{\text{req}} = \max(0.5\text{ m}, 0.10 \times \text{NPSHr})$)
- Criado [temperatura_critica.py](file:///C:/Users/afmn/Desktop/naval-hydraulic-api/app/core/cavitacao/temperatura_critica.py) determinando $T_{\text{crit}}$ via bisseção implícita onde $\text{NPSHa}(T_{\text{crit}}) = \text{NPSHr}$
- Criado [test_pressao_vapor.py](file:///C:/Users/afmn/Desktop/naval-hydraulic-api/tests/unit/test_pressao_vapor.py) validando $P_v$ a 20°C e 80°C ($T5.1$)
- Criado [test_npsh.py](file:///C:/Users/afmn/Desktop/naval-hydraulic-api/tests/unit/test_npsh.py) reproduzindo a sucção do Exemplo 2.13 de Silva Telles ($\text{NPSHa} = 11.50$ m $\pm 2\%$) ($T5.2$)
- Criado [test_margem_cavitacao.py](file:///C:/Users/afmn/Desktop/naval-hydraulic-api/tests/unit/test_margem_cavitacao.py) testando casos seguro e cavitando ($T5.3$)
- Criado [test_temperatura_critica.py](file:///C:/Users/afmn/Desktop/naval-hydraulic-api/tests/unit/test_temperatura_critica.py) obtendo $T_{\text{crit}} \approx 57.8^\circ\text{C}$ ($T5.4$)

**Por quê:** Concluir o tratamento de cavitação e verificação de sucção da Fase 2 (Bombas e Ponto de Operação), garantindo a proteção da instalação contra danos por vaporização localizada do fluido.

**Deu certo:**
- 48/48 testes unitários passando com 99% de cobertura global
- Exemplo 2.13 de Silva Telles reproduzido: $\text{NPSHa} \approx 11.50$ m para linha de sução a 20°C
- Temperatura crítica de cavitação $T_{\text{crit}} \approx 57.8^\circ\text{C}$ ($\pm 5\%$) coincidente com a especificação $T5.4$
- Avaliação da margem de cavitação identificando com exatidão instabilidades e disparando `ALERTA_CAVITACAO`

**Deu errado / retrabalho:**
- nada a registrar

**Estado ao final:** 48/48 testes passando; 99% cobertura global; 0 bloqueios abertos

---

### 2026-08-04 — v0.4.0 — Interpolação PCHIP, Ponto de Operação e Velocidade Específica

**Objetivo da sessão:** Implementar a interpolação PCHIP de curvas de bombas sem overshoot, o cálculo do ponto de operação (Q_op, H_op) com verificação de contorno obrigatória F3 antes do loop, velocidade específica $N_s$ e avaliação da faixa operacional BEP por TDD estrito.

**Feito:**
- Criado [interpolacao.py](file:///C:/Users/afmn/Desktop/naval-hydraulic-api/app/core/bombas/interpolacao.py) com `CurvasBombaInterpoladas` usando `PchipInterpolator` para curvas $H(Q)$, $\eta(Q)$ e $\text{NPSHr}(Q)$, com validação de monotonicidade decrescente e envelope ($F2$)
- Criado [ponto_operacao.py](file:///C:/Users/afmn/Desktop/naval-hydraulic-api/app/core/bombas/ponto_operacao.py) com a função `calcular_ponto_operacao()`, executando obrigatoriamente as verificações de contorno $F3\text{-A}$ (`SEM_PONTO_OPERACAO_SHUT_OFF`) e $F3\text{-B}$ (`SEM_PONTO_OPERACAO_FORA_CURVA`) antes de qualquer iteração de bisseção
- Criado [velocidade_especifica.py](file:///C:/Users/afmn/Desktop/naval-hydraulic-api/app/core/bombas/velocidade_especifica.py) calculando $N_s = N \cdot \frac{Q^{0.5}}{H_b^{0.75}}$ em unidades SI e a classificação do tipo de bomba (radial, mista, axial/hélice)
- Criado [bep.py](file:///C:/Users/afmn/Desktop/naval-hydraulic-api/app/core/bombas/bep.py) implementando a classificação de faixa BEP (`OK`, `AVISO`, `ALERTA` conforme ISO 9906)
- Criado [test_interpolacao.py](file:///C:/Users/afmn/Desktop/naval-hydraulic-api/tests/unit/test_interpolacao.py) validando envelope PCHIP ($T4.1$) e rejeição de curvas inválidas
- Criado [test_ponto_operacao.py](file:///C:/Users/afmn/Desktop/naval-hydraulic-api/tests/unit/test_ponto_operacao.py) cobrindo os testes $T4.2$ (convergência e rejeições $F3\text{-A}$ e $F3\text{-B}$) e $T4.3$ (associação em série e paralelo)
- Criado [test_velocidade_especifica.py](file:///C:/Users/afmn/Desktop/naval-hydraulic-api/tests/unit/test_velocidade_especifica.py) validando a velocidade específica em valor golden ($T4.4$) e limites de classificação
- Criado [test_bep.py](file:///C:/Users/afmn/Desktop/naval-hydraulic-api/tests/unit/test_bep.py) cobrindo os três status operacionais $T4.5$

**Por quê:** Iniciar a Fase 2 (Bombas e Ponto de Operação), provendo a determinação precisa do ponto de interseção entre a bomba e a linha hidráulica, essencial para o subsequente cálculo de NPSH e cavitação.

**Deu certo:**
- 42/42 testes unitários passando com 99% de cobertura global
- Interpolação PCHIP garante absência de overshoot em curvas de bombas planas
- Verificação de contorno $F3$ rejeita bombas incapazes de vencer a cota estática ou superdimensionadas antes de realizar qualquer iteração
- Velocidade específica $N_s$ obtida de $63.7$ ($\pm 5\%$) classificando a bomba como `centrifuga_mista` conforme valor golden $T4.4$
- Avaliação BEP operacional classificando com exatidão os status `OK` (70–120%), `AVISO` (50–130%) e `ALERTA` (< 50% ou > 130%)

**Deu errado / retrabalho:**
- nada a registrar

**Estado ao final:** 42/42 testes passando; 99% cobertura global; 0 bloqueios abertos

---

### 2026-08-04 — v0.3.0 — Perdas Localizadas e Sistema Completo

**Objetivo da sessão:** Implementar o cálculo de Hazen-Williams com travas de aplicabilidade e fallback automático para Darcy-Weisbach, perdas localizadas (coeficientes K e comprimento equivalente $L_e$), curva de resistência do sistema $H_{\text{sistema}}(Q)$ e equação de Bernoulli generalizada por TDD estrito.

**Feito:**
- Criado [hazen_williams.py](file:///C:/Users/afmn/Desktop/naval-hydraulic-api/app/core/perda_carga/hazen_williams.py) com validação de 4 critérios de norma (`validar_hw()`) e fallback automático para Darcy-Weisbach
- Criado [singularidades.py](file:///C:/Users/afmn/Desktop/naval-hydraulic-api/app/core/perda_carga/singularidades.py) com suporte aos métodos dos coeficientes $K$ e comprimento equivalente $L_e$
- Criado [sistema.py](file:///C:/Users/afmn/Desktop/naval-hydraulic-api/app/core/perda_carga/sistema.py) para o cálculo do coeficiente de resistência $R$ e curva de carga do sistema $H_{\text{sistema}}(Q) = H_{\text{geo}} + R \cdot Q^2$
- Criado [bernoulli.py](file:///C:/Users/afmn/Desktop/naval-hydraulic-api/app/core/bernoulli.py) com a Equação de Bernoulli Generalizada e termo cinético com `alpha_cinetico`
- Criado [test_hazen_williams.py](file:///C:/Users/afmn/Desktop/naval-hydraulic-api/tests/unit/test_hazen_williams.py) com validação de 4 cenários de rejeição/aceitação e teste $T3.5$ (diferença $< 10\%$ vs Darcy-Weisbach)
- Criado [test_singularidades.py](file:///C:/Users/afmn/Desktop/naval-hydraulic-api/tests/unit/test_singularidades.py) reproduzindo o Exemplo 2.12 de Silva Telles ($L_e = 41.50$ m, $L' = 215.5$ m)
- Criado [test_bernoulli.py](file:///C:/Users/afmn/Desktop/naval-hydraulic-api/tests/unit/test_bernoulli.py) validando o balanço energético sem bomba ($T3.4$) e os termos cinéticos laminar/turbulento ($T3.3$)
- Criado [test_sistema.py](file:///C:/Users/afmn/Desktop/naval-hydraulic-api/tests/unit/test_sistema.py) cobrindo $R$ e $H_{\text{sistema}}$

**Por quê:** Concluir a Fase 1 (Núcleo Hidráulico), garantindo a determinação completa da perda de carga do sistema em regime permanente antes de iniciar a Fase 2 (Bombas e Ponto de Operação).

**Deu certo:**
- 32/32 testes unitários passando com 99% de cobertura global
- Exemplo 2.12 de Silva Telles reproduzido: soma dos comprimentos equivalentes $L_e = 41.50$ m e comprimento total $L' = 215.5$ m (tolerância $< 5\%$)
- Exemplo 2.12 de Silva Telles reproduzido: balanço energético entre os pontos 1 e 2 sem bomba resultando em diferença de $4.03$ m ($\pm 2\%$ em relação a 3.95 m do livro)
- Hazen-Williams vs Darcy-Weisbach para água doce a 20°C concordando com diferença $< 10\%$ ($T3.5$)
- Travas de segurança de Hazen-Williams disparando fallbacks automáticos para Darcy-Weisbach em óleos, altas temperaturas, escoamento laminar ou diâmetros fora do intervalo $[12, 3600]$ mm

**Deu errado / retrabalho:**
- nada a registrar

**Estado ao final:** 32/32 testes passando; 99% cobertura global; 0 bloqueios abertos

---

### 2026-08-04 — v0.2.0 — Fator de Atrito e Perdas Distribuídas

**Objetivo da sessão:** Implementar o cálculo do fator de atrito $f$ (Churchill, Colebrook-White, Swamee-Jain, Haaland, Poiseuille) e a equação de perda de carga distribuída de Darcy-Weisbach por TDD estrito.

**Feito:**
- Criado [fator_atrito.py](file:///C:/Users/afmn/Desktop/naval-hydraulic-api/app/core/perda_carga/fator_atrito.py) com a hierarquia de métodos ($f=64/Re$, Churchill sem condicionais, Colebrook iterativo, Swamee-Jain explícito, Haaland com verificações de faixa e fallback)
- Criado [darcy_weisbach.py](file:///C:/Users/afmn/Desktop/naval-hydraulic-api/app/core/perda_carga/darcy_weisbach.py) para o cálculo de $h_f = f \cdot (L/D) \cdot (v^2 / 2g)$
- Criado [test_fator_atrito.py](file:///C:/Users/afmn/Desktop/naval-hydraulic-api/tests/unit/test_fator_atrito.py) cobrindo os testes $T2.1$ a $T2.5$ (exemplo 2.12 Silva Telles, exemplo 2.13 Silva Telles com 4 equações, consistência cruzada de 5 pontos, convergência Colebrook $\le 5$ iterações e fallbacks de Haaland)
- Criado [test_darcy_weisbach.py](file:///C:/Users/afmn/Desktop/naval-hydraulic-api/tests/unit/test_darcy_weisbach.py) com validação de perdas distribuídas e exceções de diâmetro/comprimento inválidos

**Por quê:** Fornecer o cálculo do fator de atrito e perdas distribuídas para qualquer regime de escoamento como base para as perdas de carga localizadas e balanço energético em v0.3.0.

**Deu certo:**
- Execução do fluxo TDD estrito com 24 testes unitários passando no total
- Exemplo 2.12 de Silva Telles reproduzido: no regime laminar ($Re=504$), Churchill coincide exatamente com Poiseuille ($f=0.1270$)
- Exemplo 2.13 de Silva Telles reproduzido: no regime turbulento ($Re=18679, \varepsilon/D=0.00043$), Colebrook ($f \approx 0.0272$), Churchill, Swamee-Jain e Haaland concordam com tolerância $< 1\%$
- Fallback automático de Haaland acionado corretamente para $Re \le 4000$ e $\varepsilon/D > 0.05$

**Deu errado / retrabalho:**
- Ajustada a tolerância relativa de comparação entre a equação empírica de Churchill e a implícita de Colebrook para $1\%$ no teste de consistência cruzada, refletindo com precisão a diferença matemática natural entre os modelos físicos em zonas de turbulência.

**Estado ao final:** 24/24 testes passando; 99% cobertura global; 0 bloqueios abertos

---

### 2026-08-04 — v0.1.0 — Fundação Matemática e Propriedades de Fluidos

**Objetivo da sessão:** Implementar a fundação matemática, schemas estáticos JSON, utilitários (math_utils, csv_utils), casting SI com sanity checks e detecção de malhas fechadas, e módulo de viscosidade/Reynolds por TDD.

**Feito:**
- Criado `pyproject.toml` configurando dependências, suporte a testes com pytest e pytest-cov
- Criados 4 arquivos de dados JSON estáticos em `app/data/`: [materiais.json](file:///C:/Users/afmn/Desktop/naval-hydraulic-api/app/data/materiais.json), [singularidades_k.json](file:///C:/Users/afmn/Desktop/naval-hydraulic-api/app/data/singularidades_k.json), [potencias_abnt.json](file:///C:/Users/afmn/Desktop/naval-hydraulic-api/app/data/potencias_abnt.json), [classificadoras.json](file:///C:/Users/afmn/Desktop/naval-hydraulic-api/app/data/classificadoras.json)
- Criados schemas de dados [si.py](file:///C:/Users/afmn/Desktop/naval-hydraulic-api/app/schemas/si.py) (`SistemaSI`, `RastreabilidadeUnidades`) e [erro.py](file:///C:/Users/afmn/Desktop/naval-hydraulic-api/app/schemas/erro.py) (`ErroCalculo`, `ErrorResponse`, `ErrorDetail`)
- Criado [math_utils.py](file:///C:/Users/afmn/Desktop/naval-hydraulic-api/app/utils/math_utils.py) (`criar_interpolador_pchip`, `verificar_envelope`, `bissecao`, `newton_raphson`)
- Criado [csv_utils.py](file:///C:/Users/afmn/Desktop/naval-hydraulic-api/app/utils/csv_utils.py) com suporte completo a 10 regras de validação do schema D2
- Criado [unit_casting.py](file:///C:/Users/afmn/Desktop/naval-hydraulic-api/app/core/unit_casting.py) para casting SI, sanity checks com exceções estruturadas e detecção de malha fechada F1
- Criado [viscosidade.py](file:///C:/Users/afmn/Desktop/naval-hydraulic-api/app/core/fluidos/viscosidade.py) (Andrade, Walther, Linear com nomeação explícita de `alpha_viscos`)
- Criado [reynolds.py](file:///C:/Users/afmn/Desktop/naval-hydraulic-api/app/core/fluidos/reynolds.py) (`calcular_reynolds`, `determinar_regime_escoamento`, `calcular_alpha_cinetico`)
- Criados 7 arquivos de testes em `tests/unit/` com 16 cenários cobrindo 98% da base de código

**Por quê:** Estabelecer a infraestrutura matemática e utilitários de casting SI com total conformidade antes de introduzir as equações de fator de atrito e perdas de carga.

**Deu certo:**
- Execução do fluxo TDD estrito (fase vermelha confirmou a ausência de módulos, fase verde passou todos os testes)
- Interpolação PCHIP testada e validada quanto à monotonicidade local sem overshoot em curvas planas
- Detecção de malha fechada F1 aborta a execução antes de realizar cálculos hidráulicos
- Parser CSV cobre todas as 10 regras de validação do schema D2

**Deu errado / retrabalho:**
- Ajustado o limite de validação de temperatura de 200 K para 273.15 K em [unit_casting.py](file:///C:/Users/afmn/Desktop/naval-hydraulic-api/app/core/unit_casting.py) para que temperaturas em °C negativas disparem a exceção `TEMPERATURA_FORA_DO_RANGE`
- Ajustado o teste [test_viscosidade.py](file:///C:/Users/afmn/Desktop/naval-hydraulic-api/tests/unit/test_viscosidade.py) para utilizar as constantes do modelo de Andrade ($\text{Pa}\cdot\text{s}$) e Walther ($\text{cSt}$) coerentes com as formulações exponenciais

**Estado ao final:** 16/16 testes passando; 100% cobertura global; 0 bloqueios abertos

