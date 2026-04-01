# Relatório Técnico — Estratégia Multi-Camada de Seleção de Carteira

**Disciplina:** Análise de Investimentos (GOLD7008)  
**Curso:** Mestrado — PPGOLD/UFPR  
**Professor:** Claudio Marcelo Edwards Barros  
**Competição:** Carteira de Investimentos 2026  
**Data:** 26 de março de 2026  

---

## Sumário

1. [Introdução e Objetivo](#1-introdução-e-objetivo)
2. [Visão Geral da Arquitetura](#2-visão-geral-da-arquitetura)
3. [Camada 1 — Piotroski F-Score](#3-camada-1--piotroski-f-score)
4. [Camada 2 — Score Composto EV/EBITDA + Fama-French](#4-camada-2--score-composto)
5. [Camada 3 — Momentum 12-1](#5-camada-3--momentum-12-1)
6. [Camada 4 — Deduplicação por Empresa](#6-camada-4--deduplicação-por-empresa)
7. [Camada 5 — Otimização Combinatória de Markowitz](#7-camada-5--otimização-combinatória-de-markowitz)
8. [Restrições de Peso e Garantia de Diversificação](#8-restrições-de-peso)
9. [Indicadores Exigidos pelo Edital](#9-indicadores-exigidos-pelo-edital)
10. [Fundamentação Teórica e Referências](#10-fundamentação-teórica-e-referências)

---

## 1. Introdução e Objetivo

O objetivo desta competição é montar uma carteira de **exatamente 4 ativos** listados na B3, de alta liquidez, capaz de superar o **CDI** como benchmark durante o período de avaliação.

A abordagem adotada rompe com a seleção manual e subjetiva de ações (*stock picking* com viés humano) e implementa um **framework quantitativo multi-fatorial**, replicável e auditável, fundamentado em quatro pilares consolidados da literatura acadêmica de finanças:

| Pilar | Autores | Ano |
|---|---|---|
| Otimização de Portfólios | Markowitz, H. | 1952 |
| Triagem de Qualidade Fundamentalista | Piotroski, J. | 2000 |
| Modelo de 5 Fatores (Valuation) | Fama, E. & French, K. | 2015 |
| Efeito Momentum | Jegadeesh, N. & Titman, S. | 1993 |

---

## 2. Visão Geral da Arquitetura

A estratégia é organizada em **5 camadas sequenciais**, onde cada camada reduz o universo de ativos:

```
Universo B3 (~700 papéis)
        │
        ▼
┌─────────────────────────────────────────────────────────────┐
│  CAMADA 1 — Piotroski F-Score (Qualidade Fundamentalista)   │
│  Filtro: F-Score ≥ 6 + Liq. Bimestral > R$ 5 milhões       │
│  Resultado: ~30–60 empresas saudáveis e líquidas            │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  CAMADA 2 — Score Composto EV/EBITDA + Fama-French          │
│  Fatores: EV/EBITDA (40%) + B/M (25%) + ROE (25%) + CMA    │
│  Resultado: Top 25 ações melhor-precificadas e lucrativas   │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  CAMADA 3 — Momentum 12-1 (Timing de Entrada)               │
│  Métrica: Retorno acumulado 12m excluindo 1 mês             │
│  Score Final = Score_C2 × 0.65 + Rank_Momentum × 0.35      │
│  Resultado: Top 12 com confirmação de tendência de alta     │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  CAMADA 4 — Deduplicação por Empresa                        │
│  Regra: 1 empresa = 1 ativo (elimina ON+PN da mesma firma)  │
│  Resultado: Máximo 12 empresas DISTINTAS                    │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  CAMADA 5 — Otimização Combinatória de Markowitz            │
│  C(n, 4) combinações × SciPy SLSQP → Máximo Sharpe         │
│  Constraints: 5% ≤ peso ≤ 80%, soma = 100%                 │
│  Resultado: 4 ativos + pesos otimizados                     │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Camada 1 — Piotroski F-Score

### 3.1 Fundamentação

O **Piotroski F-Score** foi proposto por Joseph D. Piotroski em *"Value Investing: The Use of Historical Financial Statement Information to Separate Winners from Losers"* (Journal of Accounting Research, 2000). O modelo avalia a **saúde financeira fundamental** de uma empresa através de 9 critérios binários distribuídos em 3 eixos.

### 3.2 Critérios e Pontuação

Cada critério gera **1 ponto** se verdadeiro, **0 pontos** se falso. O F-Score total varia de 0 a 9.

#### Eixo A — Rentabilidade (4 critérios)

| Critério | Definição | Proxy utilizada | Pontuação |
|---|---|---|---|
| **F1** | ROA > 0 | ROE > 0 (Fundamentus) | 0 ou 1 |
| **F2** | FCO > 0 | Margem Líquida > 0 | 0 ou 1 |
| **F3** | ROA crescente (melhora) | ROIC > ROE | 0 ou 1 |
| **F4** | FCO > Lucro (accruals baixos) | Mrg. EBIT > Mrg. Líquida | 0 ou 1 |

> **Accruals** medem a diferença entre o lucro contábil e o fluxo de caixa operacional. Quando FCO > Lucro, a empresa gera mais caixa real do que o lucro reportado — sinal de alta qualidade de earnings.

#### Eixo B — Alavancagem e Liquidez (3 critérios)

| Critério | Definição | Proxy utilizada | Pontuação |
|---|---|---|---|
| **F5** | Dívida/Ativos diminuindo | Dív. Bruta/PL < 1.0 | 0 ou 1 |
| **F6** | Liquidez Corrente crescendo | Liquidez Corrente > 1.0 | 0 ou 1 |
| **F7** | Sem novas emissões de ações | Cresc. Receita 5a > 0 | 0 ou 1 |

#### Eixo C — Eficiência Operacional (2 critérios)

| Critério | Definição | Proxy utilizada | Pontuação |
|---|---|---|---|
| **F8** | Margem Bruta crescente | Margem EBIT > 0 | 0 ou 1 |
| **F9** | Giro do Ativo crescente | ROIC > 10% | 0 ou 1 |

**Fórmula do F-Score Total:**

```
F_SCORE = F1 + F2 + F3 + F4 + F5 + F6 + F7 + F8 + F9
```

### 3.3 Filtros Aplicados

```
F-Score >= 6             → Empresa fundamentalmente saudável
Liq.2meses > 5.000.000  → Alta liquidez (regra do edital)
P/L > 0                 → Empresa com lucro (sem prejuízo)
```

**Interpretação dos scores:**
- **F-Score 7–9:** Empresa sólida — alta probabilidade de superar o mercado
- **F-Score 4–6:** Empresa neutra — avaliar caso a caso
- **F-Score 0–3:** Empresa fraca — evitar

### 3.4 Por que o F-Score supera o P/L + ROE isolados?

O P/L e ROE capturam apenas um *snapshot* pontual. O F-Score avalia a **trajetória e qualidade** dos fundamentos em 3 dimensões simultâneas — exatamente os 3 eixos exigidos pelo edital da competição.

---

## 4. Camada 2 — Score Composto

### 4.1 EV/EBITDA — Fundamentos

O **Enterprise Value / EBITDA** é a métrica de Valuation preferida por Damodaran (2012) para comparações cross-setor porque elimina as distorções da estrutura de capital, da política de dividendos e das diferenças contábeis.

```
EV = Market Cap + Dívida Líquida - Caixa

EBITDA = EBIT + Depreciação + Amortização

EV/EBITDA = EV / EBITDA
```

- **EV/EBITDA baixo** → empresa barata vs. geração de caixa operacional
- **EV/EBITDA alto** → empresa cara (pode ser justificado por crescimento esperado)

**Referência para o mercado brasileiro (2026):** 4x–12x para empresas maduras.

### 4.2 Proxies dos Fatores Fama-French

O **modelo Fama-French 5 Fatores** (2015) propõe que o retorno esperado de um ativo é explicado por:

```
E[Ri] - Rf = β_MKT*(Rm - Rf) + β_SMB*SMB + β_HML*HML + β_RMW*RMW + β_CMA*CMA
```

Proxies utilizadas via Fundamentus:

| Fator FF5 | Proxy utilizada | Lógica |
|---|---|---|
| **HML** (High Minus Low) | `1 / P/VP` (Book-to-Market) | Ações com B/M alto (P/VP baixo) são "value" — historicamente superam |
| **RMW** (Robust Minus Weak) | `ROE` | Empresas mais lucrativas superam (fator rentabilidade) |
| **CMA** (Conservative Minus Aggressive) | `Cresc. Receita 5a` (invertido) | Empresas conservadoras superam as agressivas no investimento |

### 4.3 Cálculo do Score Composto

Para cada ativo, calcula-se o **ranking relativo** (posição ordinal) em cada métrica:

```
rank_ev_ebitda  = rank(EV/EBITDA,  ascending=True)   # menor = rank 1
rank_book_mkt   = rank(1/P/VP,     ascending=False)   # maior B/M = rank 1
rank_roe        = rank(ROE,        ascending=False)   # maior ROE = rank 1
rank_conserv    = rank(Cresc.Rec,  ascending=True)    # menor cresc = rank 1
```

**Score Composto:**
```
Score_C2 = 0.40 * rank_EV_EBITDA
         + 0.25 * rank_B/M
         + 0.25 * rank_ROE
         + 0.10 * rank_CMA
```

> Quanto **menor** o Score_C2, mais atrativo é o ativo.

**Justificativa dos pesos:**
- EV/EBITDA (40%): mais robusta e abrangente — incorpora preço e dívida
- ROE + B/M (50%): os dois fatores FF com maior evidência empírica de persistência
- CMA (10%): evidência mais fraca para horizontes curtos

---

## 5. Camada 3 — Momentum 12-1

### 5.1 Fundamentação

O **efeito Momentum** foi documentado por Jegadeesh & Titman (1993): ações que mais subiram nos últimos 12 meses tendem a continuar superando nos próximos 3–12 meses.

**Mecanismos cognitivos que sustentam o Momentum:**
- **Subréação de investidores** (*underreaction*): boas notícias são incorporadas gradualmente
- **Comportamento de manada** (*herding*): gestores seguem o que está em alta
- **Revisões sequenciais**: empresas que surpreendem positivamente tendem a repetir

### 5.2 Fórmula do Momentum 12-1

A janela de cálculo **exclui o mês mais recente** para evitar o efeito de reversão de curtíssimo prazo (Jegadeesh, 1990):

```
Momentum_12-1 = P(t-21) / P(t-252) - 1
```

Onde:
- `P(t-21)` = preço 1 mês atrás (~21 dias úteis)
- `P(t-252)` = preço 12 meses atrás (~252 dias úteis)

### 5.3 Score Final com Momentum

O Score Final integra fundamentalismo (Camadas 1 e 2) com sinal de mercado (Momentum):

```
Score_Final = 0.65 * Score_C2 + 0.35 * rank_Momentum
```

**Justificativa da ponderação 65/35:** Preserva dominância da análise fundamentalista (qualidade estrutural) com influência significativa do Momentum (timing de entrada correto).

> **Por que combinar Value com Momentum?** A maior armadilha do Value Investing puro é o *value trap* — a empresa parece barata pelos fundamentos, mas o mercado continua vendendo. O Momentum funciona como um "gatilho de reconhecimento" — confirma que o mercado começou a valorizar o que os fundamentos já indicavam. AQR Capital baseia suas principais estratégias nesta combinação (Asness, Moskowitz & Pedersen, 2013).

---

## 6. Camada 4 — Deduplicação por Empresa

### 6.1 O Problema da Falsa Diversificação

PETR3 (ON) e PETR4 (PN) da Petrobras têm correlação histórica tipicamente **> 0.97**. Incluir ambas na carteira:

- **Não reduz volatilidade** — correlação próxima de 1 anula benefícios de diversificação
- **Concentra risco** disfarçado de diversificação
- **Viola Markowitz**: a redução de risco via diversificação só funciona com ativos *descorrelacionados*

```
Correlação esperada entre ON e PN da mesma empresa ≈ 0.97
→ diversificação efetiva ≈ 0
```

### 6.2 Implementação da Deduplicação

Extrai o **código raiz** de cada ticker removendo os sufixos numéricos:

```python
empresa_base = ticker.str.replace(r'\d+$', '', regex=True)
# PETR4 → PETR, VALE3 → VALE, BBDC4 → BBDC, ITUB4 → ITUB
```

Para cada empresa, mantém apenas o **ticker com melhor Score Final**:

```python
df_dedup = (df_final
    .sort_values('Score_Final')                          # menor Score = melhor
    .drop_duplicates(subset='empresa_base', keep='first') # 1 por empresa
    .reset_index(drop=True)
)
```

---

## 7. Camada 5 — Otimização Combinatória de Markowitz

### 7.1 Teoria Moderna do Portfólio (Markowitz, 1952)

Markowitz demonstrou que o risco do portfólio depende fundamentalmente das **covariâncias** entre os retornos — não da média dos riscos individuais.

**Retorno esperado do portfólio:**
```
E[Rp] = w1*μ1 + w2*μ2 + ... + wN*μN  =  w^T * μ
```

**Variância (Risco²) do portfólio:**
```
σp² = Σ_i Σ_j wi * wj * σij  =  w^T * Σ * w
```

**Volatilidade:**
```
σp = sqrt(w^T * Σ * w)
```

Onde:
- `w` = vetor de pesos
- `μ` = vetor de retornos esperados anualizados
- `Σ` = matriz de covariância anualizada (252 × covariância diária)

### 7.2 Índice de Sharpe — Função Objetivo

```
Sharpe = (E[Rp] - Rf) / σp
```

Onde:
- `E[Rp]` = retorno esperado anualizado do portfólio
- `Rf` = taxa livre de risco (CDI proxy = **10,75% a.a.** em 2026)
- `σp` = volatilidade anualizada do portfólio

> O Índice de Sharpe maximizado corresponde à **Carteira Tangente** — ponto na Fronteira Eficiente onde a Linha de Mercado de Capitais (CML) é tangente à fronteira, entregando o máximo prêmio de risco por unidade de risco assumido.

### 7.3 Análise Combinatória

A competição exige **exatamente 4 ativos**. Testamos todas as combinações únicas de 4 do universo de candidatos:

```
C(n, 4) = n! / (4! * (n-4)!)

C(12, 4) = 495 combinações
C(10, 4) = 210 combinações
C(8,  4) = 70  combinações
```

Para **cada** combinação, resolvemos o problema de otimização:

```
Maximizar:   Sharpe(w) = (w^T * μ - Rf) / sqrt(w^T * Σ * w)

Sujeito a:
   Σ wi = 1          (soma dos pesos = 100%)
   0.05 ≤ wi ≤ 0.80  (mínimo 5%, máximo 80% por ativo)
```

O otimizador utilizado é o **SLSQP** (Sequential Least Squares Quadratic Programming) do SciPy.

A **carteira vencedora** é a combinação que produziu o **maior Índice de Sharpe** entre todas as testadas.

### 7.4 Estimação dos Parâmetros

Base: **5 anos de dados históricos diários** (2021-03-26 a 2026-03-26)

**Retorno médio diário:**
```
μ_i_diário = média(r_it)  para t = 1 a T

Retorno anualizado: μ_i = μ_i_diário × 252
```

**Covariância anualizada:**
```
σ_ij = [252/(T-1)] × Σ_t (r_it - μ_i)(r_jt - μ_j)
```

> **Por que 252?** O ano financeiro padrão no Brasil tem 252 dias úteis. Multiplicar por 252 converte covariância e retornos diários para escala anual, compatível com o CDI (expresso em base anual).

---

## 8. Restrições de Peso

### 8.1 O problema do peso zero

Sem restrições adicionais, o otimizador pode atribuir **0% a qualquer ativo** quando uma sub-carteira de 3 maximiza melhor o Sharpe. Isso cria um "ativo fantasma" — presente na lista, mas com zero contribuição.

### 8.2 Restrições implementadas

| Restrição | Valor | Justificativa |
|---|---|---|
| Peso mínimo por ativo | **5%** | Garante contribuição real de cada papel |
| Peso máximo por ativo | **80%** | Evita concentração excessiva |
| Soma dos pesos | **100%** | Carteira long-only (sem short) |

**Implementação com dupla garantia:**

```python
# Primeira garantia: limites do otimizador
MIN_PESO, MAX_PESO = 0.05, 0.80
bounds = [(MIN_PESO, MAX_PESO)] * 4

# Segunda garantia: descarte pós-otimização
if np.any(w_opt < 0.02):
    continue  # pula esta combinação
```

---

## 9. Indicadores Exigidos pelo Edital

### 9.1 Rentabilidade / Lucratividade

| Indicador | Fórmula | Fonte | Onde aparece |
|---|---|---|---|
| **ROE** | Lucro Líquido / Patrimônio Líquido | Fundamentus | Camadas 1 e 2 |
| **ROIC** | NOPAT / Capital Investido | Fundamentus | Camada 1 (F9) |
| **Margem EBIT** | EBIT / Receita Líquida | Fundamentus | Camada 1 (F8) |

### 9.2 Valuation

| Indicador | Fórmula | Fonte | Onde aparece |
|---|---|---|---|
| **EV/EBITDA** | EV / EBITDA | Fundamentus | Camada 2 (peso 40%) |
| **P/VP** | Preço / Valor Patrimonial por Ação | Fundamentus | Camada 2 (fator HML) |
| **P/L** | Preço / Lucro por Ação | Fundamentus | Filtro qualitativo |

### 9.3 Endividamento

| Indicador | Fórmula | Fonte | Onde aparece |
|---|---|---|---|
| **Dívida Bruta / PL** | Dívida Bruta / Patrimônio Líquido | Fundamentus | Camada 1 (F5) |
| **Liquidez Corrente** | Ativo Circulante / Passivo Circulante | Fundamentus | Camada 1 (F6) |

---

## 10. Fundamentação Teórica e Referências

### 10.1 Adequação ao contexto da competição

A competição tem horizonte de **curto prazo** (meses). Este contexto favorece:

1. **Momentum sobre Value puro:** em horizontes curtos, a tendência de preços é mais preditiva do que fundamentos de longo prazo (35% do Score Final ao Momentum).
2. **Qualidade sobre crescimento:** com CDI > 10%, empresas altamente endividadas pagam caro pelos juros. O F-Score filtra esse risco exigindo Dívida/PL < 1.0.
3. **Diversificação real:** quatro empresas distintas e sem duplicidades reduz o risco idiossincrático, permitindo que Markowitz atue sobre descorrelações genuínas.

### 10.2 Referências Bibliográficas

**Artigos fundacionais:**

- MARKOWITZ, H. *Portfolio Selection*. Journal of Finance, v. 7, n. 1, p. 77–91, 1952.

- SHARPE, W. F. *Mutual Fund Performance*. Journal of Business, v. 39, n. 1, p. 119–138, 1966.

- FAMA, E. F.; FRENCH, K. R. *A Five-Factor Asset Pricing Model*. Journal of Financial Economics, v. 116, n. 1, p. 1–22, 2015.

- FAMA, E. F.; FRENCH, K. R. *Common Risk Factors in the Returns on Stocks and Bonds*. Journal of Financial Economics, v. 33, n. 1, p. 3–56, 1993.

- PIOTROSKI, J. D. *Value Investing: The Use of Historical Financial Statement Information to Separate Winners from Losers*. Journal of Accounting Research, v. 38, Supplement, p. 1–41, 2000.

- JEGADEESH, N.; TITMAN, S. *Returns to Buying Winners and Selling Losers: Implications for Stock Market Efficiency*. Journal of Finance, v. 48, n. 1, p. 65–91, 1993.

- JEGADEESH, N. *Evidence of Predictable Behavior of Security Returns*. Journal of Finance, v. 45, n. 3, p. 881–898, 1990.

- ASNESS, C. S.; MOSKOWITZ, T. J.; PEDERSEN, L. H. *Value and Momentum Everywhere*. Journal of Finance, v. 68, n. 3, p. 929–985, 2013.

**Livros — bibliografia do plano de ensino:**

- DAMODARAN, A. *Avaliação de Empresas*. 2. ed. São Paulo: Pearson, 2007.
- DAMODARAN, A. *Investment Valuation*. 3. ed. Hoboken: Wiley, 2012.
- BRIGHAM, E. F.; HOUSTON, J. F. *Fundamentals of Financial Management*. 14. ed. Mason: Cengage, 2016.
- COPELAND, T.; KOLLER, T.; MURRIN, J. *Valuation*. 5. ed. Hoboken: Wiley, 2010.
- WOOLDRIDGE, J. M. *Introductory Econometrics*. 6. ed. Mason: Cengage, 2015.

---

## Apêndice — Glossário

| Termo | Definição |
|---|---|
| **B3** | Brasil, Bolsa, Balcão — bolsa de valores brasileira |
| **CDI** | Certificado de Depósito Interbancário — benchmark de renda fixa |
| **EV** | Enterprise Value = Valor de Mercado + Dívida Líquida |
| **EBITDA** | Lucro antes de Juros, Impostos, Dep. e Amortização |
| **F-Score** | Piotroski Financial Score — score de qualidade de 0 a 9 |
| **Fronteira Eficiente** | Conjunto de portfólios com máximo retorno para cada nível de risco |
| **Índice de Sharpe** | Prêmio de retorno por unidade de risco |
| **Momentum** | Tendência de preços — ativos que sobem tendem a continuar subindo |
| **ROE** | Return on Equity — retorno sobre patrimônio líquido |
| **ROIC** | Return on Invested Capital — retorno sobre capital investido |
| **SLSQP** | Sequential Least Squares Quadratic Programming — algoritmo de otimização |
| **Value Trap** | Ação barata pelos fundamentos que continua caindo no mercado |

---

*Relatório produzido em conformidade com as exigências da disciplina GOLD7008 — Análise de Investimentos (PPGOLD/UFPR). Todos os dados e cálculos são reproduzíveis via o Jupyter Notebook `Estrategia 5 - Combinar 3 Estrategias em Camadas.ipynb`.*
