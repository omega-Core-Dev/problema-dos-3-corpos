# ANALOGOS v0.5.0 — Decomposição Matemática dos 5 Primitivos
## Base para formulação dos operadores ideais

*Zaqueu Ribeiro da Costa — Ω core*

---

Cada primitivo é analisado em quatro camadas:

1. **O que faz** — função semântica
2. **Espaço de operação** — onde matematicamente vive
3. **Operador atual** — o que está implementado
4. **Operador ideal** — o que precisa ser formulado

---

## PRIMITIVO 1 — SCAN

### O que faz
Estima a *forma do ruído* do sistema. Não coleta fatos — lê a distribuição
subjacente dos sinais. É o olho do framework: antes de qualquer inferência,
SCAN pergunta "como esse espaço está distribuído?"

### Espaço de operação
O espaço das medidas de probabilidade sobre ℝⁿ:

```
𝒫(ℝⁿ) = { μ : μ é medida de probabilidade sobre ℝⁿ }
```

SCAN opera em sequências de observações e produz um elemento de 𝒫(ℝⁿ).

### Operador atual
Estimador de momentos de primeira e segunda ordem:

```
SCAN(X) = ( μ̂, σ̂² )

μ̂  = (1/n) Σᵢ xᵢ              ← média empírica
σ̂² = (1/n) Σᵢ (xᵢ - μ̂)²      ← variância empírica
```

**Problema:** dois momentos não capturam a forma completa da distribuição.
Distribuições com mesmo μ e σ² podem ter caudas, multimodalidade e assimetria
radicalmente diferentes — e SCAN trata todas como iguais.

### Operador ideal a formular

**Estimador de distribuição completa via função característica:**

```
φ_X(t) = E[e^{itX}] = ∫ e^{itx} dP(x)

SCAN_ideal(X) = φ̂_X   (função característica empírica)
```

Ou, equivalentemente, via **entropia diferencial** como medida de dispersão
estrutural:

```
H(X) = -∫ p(x) log p(x) dx

SCAN_ideal(X) = ( φ̂_X, H(X) )
```

A função característica φ̂_X determina univocamente a distribuição — nenhuma
informação é perdida. H(X) substitui σ² como medida de dispersão porque
captura incerteza estrutural, não apenas variância linear.

**Operador a definir:**
```
𝒮 : ℝⁿ → 𝒫(ℝ) × ℝ
𝒮(X) = ( φ̂_X , H(X) )
```

---

## PRIMITIVO 2 — BROADCAST

### O que faz
Cada nó transmite uma *distribuição*, não um valor. Propaga incerteza pelo
sistema inteiro via distância fractal modulada por profundidade k. Transforma
o sistema de determinístico em estocástico.

### Espaço de operação
Espaço de Hilbert de núcleo reprodutor (RKHS) sobre o espaço de estados:

```
ℋ_K = { f : ℝⁿ → ℝ  |  ‖f‖_K < ∞ }
```

onde K é o núcleo (kernel) que define a geometria de propagação.

### Operador atual
Distância fractal com k oitavas de ruído auto-similar:

```
D_fractal(d, k) = Σᵢ₌₁ᵏ (σ/i) · ηᵢ · d^(1/i)

onde ηᵢ ~ 𝒩(0,1)  (ruído independente por oitava)
```

Seguido de emissão de distribuição gaussiana centrada na posição do nó com
desvio modulado por D_fractal.

**Problema:** D_fractal é aditivo e linear por oitava. A auto-similaridade
fractal real requer estrutura multiplicativa — cada escala deve *modular* a
anterior, não apenas somar. Além disso, ηᵢ independentes quebram a correlação
entre oitavas que define um fractal genuíno.

### Operador ideal a formular

**Kernel de propagação fractal com estrutura de Matérn:**

O kernel de Matérn captura correlações que decaem com a distância de forma
parametrizável pela suavidade ν:

```
K_ν(d) = (2^{1-ν} / Γ(ν)) · (√2ν · d/ℓ)^ν · K_ν(√2ν · d/ℓ)
```

onde K_ν é a função de Bessel modificada de segunda espécie e ℓ é o
comprimento de escala.

Para estrutura fractal genuína, o operador de broadcast deve ser:

```
ℬ_k : 𝒫(ℝⁿ) → 𝒫(ℝⁿ)^N

ℬ_k(P)(xᵢ) = ∫ K_k(xᵢ, xⱼ) dP(xⱼ)
```

onde K_k é um kernel composto que realiza a expansão fractal em k escalas
via produto de Hadamard (não soma):

```
K_k(x, y) = Π_{i=1}^{k} K_{ν_i}( d(x,y)^{1/i} )
```

**Operador a definir:**
```
ℬ : 𝒫(ℝⁿ) × ℕ → 𝒫(ℝⁿ)^N
ℬ(P, k)(i) = distribuição do nó i após propagação fractal de ordem k
```

---

## PRIMITIVO 3 — CANDIDATE

### O que faz
Gera hipóteses concorrentes e atribui peso probabilístico a cada uma via
inferência bayesiana implícita. Não declara verdade — mantém distribuição
sobre hipóteses. A memória entre passadas vem da atualização do prior.

### Espaço de operação
O simplex de probabilidade sobre o espaço de hipóteses H:

```
Δ^{|H|} = { p ∈ ℝ^{|H|}  |  Σᵢ pᵢ = 1,  pᵢ ≥ 0 }
```

### Operador atual
Regra de Bayes categórica com likelihoods heurísticos:

```
P(Hᵢ | e) = P(e | Hᵢ) · P(Hᵢ) / Σⱼ P(e | Hⱼ) · P(Hⱼ)
```

onde P(e | Hᵢ) é definida por thresholds manuais sobre o spread posicional.

**Problema:** os likelihoods são heurísticos — não derivados da estrutura do
sistema. A evidência `e` colapsa toda a riqueza do broadcast num único escalar
(avg_spread). O prior atualiza, mas a likelihood não aprende.

### Operador ideal a formular

**Operador de atualização bayesiana em espaço de medidas:**

A generalização correta é o operador de atualização de Bayes como mapa entre
medidas de probabilidade:

```
𝒞 : 𝒫(H) × 𝒫(X) → 𝒫(H)

𝒞(π, P_X)(H) = ∫_X P_X(x | H) dπ(H) / Z
```

Para hipóteses contínuas, isso se torna uma integral funcional. A likelihood
deve ser derivada diretamente do output de BROADCAST via divergência de
Kullback-Leibler entre a distribuição observada e a prevista por cada hipótese:

```
P(e | Hᵢ) = exp( -D_KL( P_broadcast ‖ P_{Hᵢ} ) )
```

Isso transforma CANDIDATE num **classificador por distância distribucional**
— a hipótese mais próxima da distribuição observada ganha peso, sem heurística.

**Operador a definir:**
```
𝒞 : Δ^{|H|} × 𝒫(ℝⁿ) → Δ^{|H|}
𝒞(π, P)(Hᵢ) ∝ exp( -D_KL(P ‖ P_{Hᵢ}) ) · π(Hᵢ)
```

---

## PRIMITIVO 4 — PROPAGATE

### O que faz
Seleciona e corrige trajetórias via função de custo estatística. É onde o
framework torna-se explicitamente aprendizado de máquina: o gradiente da perda
corrige o estado do sistema, ponderado pela confiança de CANDIDATE.

### Espaço de operação
Variedade Riemanniana do espaço de estados (velocidades, posições, energias):

```
(ℳ, g)

onde g é a métrica que define a geometria do espaço de estados
```

### Operador atual
Gradiente euclidiano da perda quadrática, ponderado por P(instabilidade):

```
Loss = |v - v_circular|²
∇Loss → Δv = (v_circular - v_curr) · p_instab · tangent
```

**Problema:** o gradiente euclidiano não respeita a geometria do espaço de
estados. Em espaços curvos (como espaços de distribuições, ou espaços de fase
de sistemas dinâmicos), o gradiente euclidiano aponta na direção errada. O
custo quadrático trata todos os desvios como igualmente custosos — mas desvios
próximos a instabilidades estruturais são exponencialmente mais custosos.

### Operador ideal a formular

**Gradiente natural de Amari (gradiente em geometria da informação):**

O gradiente natural corrige o gradiente euclidiano pela métrica de Fisher:

```
∇̃L = G⁻¹(θ) · ∇L

onde G(θ) é a matriz de informação de Fisher:
G_{ij}(θ) = E[ (∂ log p(x;θ)/∂θᵢ)(∂ log p(x;θ)/∂θⱼ) ]
```

Para o custo estrutural, a perda deve medir distância na geometria do espaço
de distribuições (distância de Wasserstein W₂), não distância euclidiana:

```
Loss_W = W₂( P_estado_atual , P_estado_estável )²

W₂(P, Q)² = inf_γ ∫ ‖x - y‖² dγ(x,y)
```

O fluxo de gradiente de Wasserstein gera a equação de Fokker-Planck —
conexão direta com a dinâmica de distribuições.

**Operador a definir:**
```
𝒫_op : 𝒫(ℳ) × Δ^{|H|} → T𝒫(ℳ)
𝒫_op(P, π) = -∇_W [ Σᵢ π(Hᵢ) · W₂(P, P_{Hᵢ})² ]

onde ∇_W é o gradiente no espaço de Wasserstein
```

---

## PRIMITIVO 5 — COMPOSE

### O que faz
Agrega toda a incerteza acumulada pelas passadas anteriores e produz uma
decisão. O output não é certeza — é valor esperado ou MAP. Quando a confiança
é baixa, aplica correção centrípeta proporcional ao afastamento da estabilidade.

### Espaço de operação
Espaço métrico de medidas de probabilidade com distância de Wasserstein:

```
(𝒫₂(ℝⁿ), W₂)

onde 𝒫₂ são as medidas com segundo momento finito
```

### Operador atual
Média ponderada das posições esperadas com nudge centrípeto condicional:

```
E[X] = Σᵢ wᵢ · xᵢ    (agregação linear)

if P(collision) > 0.5:
    nudge = α · (centroid - pos)   (correção centrípeta)
```

**Problema:** a média de Fréchet em espaço euclidiano não é a média correta
em espaços curvos ou em espaços de distribuições. A agregação linear de
distribuições gaussianas produz uma gaussiana — mas a média de distribuições
arbitrárias requer baricêntro de Wasserstein. O nudge centrípeto é ad hoc —
não deriva de nenhum funcional.

### Operador ideal a formular

**Baricêntro de Wasserstein como agregação de distribuições:**

A média de n distribuições {Pᵢ} no espaço de Wasserstein é o baricêntro:

```
P* = argmin_{P} Σᵢ wᵢ · W₂(P, Pᵢ)²
```

Isso generaliza a média aritmética para o espaço de distribuições. O resultado
P* captura a estrutura geométrica comum a todas as distribuições de input —
não colapsa a incerteza, a agrega corretamente.

Para a decisão final, o MAP no espaço de Wasserstein é:

```
x* = argmax_{x} P*(x)
```

e o valor esperado é a média de Fréchet de P*:

```
E_{W}[X] = argmin_{m} ∫ d(x, m)² dP*(x)
```

onde d é a distância geodésica na variedade ℳ.

**Operador a definir:**
```
𝒪 : 𝒫(ℝⁿ)^N × Δ^{|H|} → 𝒫(ℝⁿ)
𝒪({Pᵢ}, π) = argmin_{P} Σᵢ π(Hᵢ) · W₂(P, Pᵢ)²
```

---

## Quadro Geral dos Operadores

```
┌─────────────┬─────────────────────────────────┬───────────────────────────────────────────────┐
│  Primitivo  │  Espaço de operação             │  Operador ideal                               │
├─────────────┼─────────────────────────────────┼───────────────────────────────────────────────┤
│  SCAN       │  𝒫(ℝⁿ)                          │  𝒮(X) = ( φ̂_X , H(X) )                      │
│             │  medidas de probabilidade        │  função característica + entropia diferencial │
├─────────────┼─────────────────────────────────┼───────────────────────────────────────────────┤
│  BROADCAST  │  RKHS sobre espaço de estados   │  ℬ(P, k)(i) = ∫ K_k(xᵢ,xⱼ) dP(xⱼ)          │
│             │  ℋ_K                            │  kernel de Matérn composto por produto        │
├─────────────┼─────────────────────────────────┼───────────────────────────────────────────────┤
│  CANDIDATE  │  Simplex Δ^{|H|}                │  𝒞(π, P)(Hᵢ) ∝ exp(-D_KL(P‖P_{Hᵢ})) · π(Hᵢ)│
│             │  distribuição sobre hipóteses    │  divergência KL como likelihood               │
├─────────────┼─────────────────────────────────┼───────────────────────────────────────────────┤
│  PROPAGATE  │  Variedade Riemanniana (ℳ, g)   │  𝒫_op = -∇_W [ Σᵢ π(Hᵢ)·W₂(P, P_{Hᵢ})² ]  │
│             │  espaço de estados dinâmicos    │  gradiente natural + fluxo de Wasserstein     │
├─────────────┼─────────────────────────────────┼───────────────────────────────────────────────┤
│  COMPOSE    │  (𝒫₂(ℝⁿ), W₂)                  │  𝒪({Pᵢ}, π) = argmin_P Σᵢ π(Hᵢ)·W₂(P,Pᵢ)²  │
│             │  espaço de Wasserstein          │  baricêntro de Wasserstein                    │
└─────────────┴─────────────────────────────────┴───────────────────────────────────────────────┘
```

---

## Conexões Entre os Operadores

Os 5 operadores não são independentes — formam uma cadeia com invariantes:

```
𝒮 → ℬ → 𝒞 → 𝒫_op → 𝒪

𝒮  produz elemento de  𝒫(ℝ)          — medida de probabilidade
ℬ  opera sobre         𝒫(ℝ)  → ℋ_K  — levanta para RKHS
𝒞  opera sobre         ℋ_K   → Δ^n  — projeta no simplex
𝒫_op opera sobre       Δ^n   → T𝒫   — vetor tangente no espaço de Wasserstein
𝒪  opera sobre         T𝒫   → 𝒫₂   — retorna ao espaço de medidas
```

A sequência completa é um **morfismo de categorias**:

```
𝒫(ℝⁿ) →^𝒮 𝒫(ℝ) →^ℬ ℋ_K →^𝒞 Δ^n →^{𝒫_op} T𝒫₂ →^𝒪 𝒫₂(ℝⁿ)
```

O critério de parada `|σ²ₖ - σ²ₖ₋₁| < ε` é, nessa formulação, a condição
de ponto fixo do morfismo composto — quando a aplicação recursiva de F(k×5)
converge para um ponto fixo no espaço 𝒫₂(ℝⁿ).

Não-convergência significa que o morfismo não tem ponto fixo nessa escala.
Isso é uma propriedade topológica do sistema — não uma limitação computacional.

---

## Próximos Passos

Para cada operador ideal:

| Primitivo | O que falta definir |
|-----------|---------------------|
| SCAN | Estimador não-paramétrico de φ̂_X em alta dimensão |
| BROADCAST | Escolha de ν (suavidade do Matérn) por passada |
| CANDIDATE | Algoritmo eficiente para D_KL contínuo entre distribuições empíricas |
| PROPAGATE | Discretização do fluxo de gradiente de Wasserstein |
| COMPOSE | Algoritmo de baricêntro de Wasserstein iterativo (Sinkhorn) |

---

*Copyright 2026 Zaqueu Ribeiro da Costa — Ω core*
