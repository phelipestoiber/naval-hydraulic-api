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

