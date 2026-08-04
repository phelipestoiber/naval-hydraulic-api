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

**Estado ao final:** 16/16 testes passando; 98% cobertura global; 0 bloqueios abertos

