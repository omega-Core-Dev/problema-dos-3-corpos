# ANALOGOS v0.5.0 — Complexity Processing by Decomposition
## How to measure structural depth when classical approaches give no traction

---

There is a class of problems that resists solution not because we lack data
or computing power, but because the solution space itself is structurally
complex.

For these problems, asking *"what is the answer?"* is the wrong move.

The right question is:

> *How deep is this problem?*

That is the question ANALOGOS is built to answer.

---

## The Wrong Question vs The Right Question

Most approaches to a hard problem ask:

> *What is the output?*

That is a prediction problem. It fails when the system is chaotic, nonlinear,
or fundamentally underdetermined.

Some ask:

> *Why does the system behave this way?*

That is a comprehension problem. Partially alive — but the geometry is rarely
fully mapped.

Almost nobody asks:

> *What is the structural depth of this problem?*

That is the question ANALOGOS answers.

---

## What is ANALOGOS?

ANALOGOS is a recursive fractal framework composed of 5 primitives applied
in sequence — a pipeline where each primitive is derived from the previous one.

It is not an algorithm.
It is not a model.

It is an **algebra of process** — a structure general enough to map any complex
system that processes information under uncertainty.

The key insight:

> Any complex problem can be decomposed by applying the 5-primitive block
> recursively, in multiples of 5. Each application is a *passada* (pass).
> Each pass reveals one more layer of the problem's internal structure.
> The number of passes required is the **structural depth** of the problem.

Available on PyPI: **analogos v0.5.0**
→ pypi.org/project/analogos/

---

## The 5 Primitives

Each primitive is a function. Each one receives the output of the previous.
Together they form a single recursive block F(k×5).

---

**1. SCAN → Distribution Estimation**

SCAN does not collect facts.
SCAN estimates the *shape of the noise*.

```
Input:  raw signals from the system
Output: μ (mean), σ² (variance), empirical distribution

SCAN sees: structured noise + trend + dispersion
SCAN does NOT see: facts, certainties, fixed values
```

SCAN estimates μ and σ² of the signal magnitudes across the system.
Not values — the *distribution* of influences.

---

**2. BROADCAST → Uncertainty Propagation**

Each node does not transmit a value.
Each node transmits a **distribution**.

```
Input:  (μ, σ², fractal_distance d_fractal)
Output: P(X|d), covariance cov(i,j)

Transforms the system into:
a stochastic network — not deterministic
```

The fractal distance d_fractal is the key mechanism: each distance d between
two elements is expanded into k octaves of self-similar noise:

```
D_fractal(d, k) = Σᵢ₌₁ᵏ (σ/i) · ηᵢ · d^(1/i)
```

This is NOT normalization. It is the distance each primitive *actually sees*
— modulated by the fractal depth k.

Each element broadcasts P(X_i) — its probable state distribution — and the
covariance cov(i,j) between pairs. The system becomes a stochastic influence
network.

---

**3. CANDIDATE → Probabilistic Hypothesis Generation**

Hypotheses are not true or false.
They carry weight.

```
Input:  [P(X)₁, P(X)₂, ...] from other nodes' broadcasts
Output: P(H|evidence) via implicit Bayesian inference

Mechanism:
likelihood × prior
─────────────────── = posterior
     evidence
```

Selection criteria: likelihood, prior, evidence.
The prior updates across passes — the block has memory.

All competing hypotheses coexist with Bayesian weights.
None is declared true yet.

---

**4. PROPAGATE → Selection by Statistical Cost Function**

This is where the system becomes explicitly machine learning.

```
Input:  P(H), current state, expected stable state
Output: Δ correction vector

Loss = |state - expected_stable|²
∇Loss → correction weighted by P(H)

PROPAGATE = optimization
feedback   = statistical gradient
```

The confidence P(H) from CANDIDATE weights the correction strength.
High confidence in instability → stronger correction applied.

Loss measures deviation from expected structural energy. The gradient corrects
each element's trajectory — not by forcing a solution, but by reading the
structural signal.

---

**5. COMPOSE → Decision by Expectation**

The output is not certainty.
The output is an expected value.

```
Input:  all broadcast objects + PROPAGATE correction
Output: E[X] (expected value) or MAP (maximum a posteriori)

COMPOSE =
  aggregation of uncertainty
  decision by expected value
  or maximum probability selection
```

When confidence P(H) is low (diverging system), COMPOSE applies a gentle
correction toward the system centroid. It does not force stability — it nudges
toward it proportionally to how far from stability the system is.

---

## The Passes

The framework is applied recursively. Each pass operates on the output of the
previous one.

---

**PASS k=5 — Reading the noise**

```
SCAN:      μ, σ² of signal magnitudes across the system
BROADCAST: P(state_i) + cov(i,j) between pairs
CANDIDATE: competing hypotheses — all weighted
PROPAGATE: Loss = structural energy deviation → ∇Loss corrects trajectories
COMPOSE:   weighted probability distribution across hypotheses
```

We see chaos. We do not yet see structure inside the chaos.

---

**PASS k=10 — Reading structure inside the noise**

Applied over the output of pass k=5.

```
SCAN:      μ₂, σ²₂ of hypothesis distribution over time
           Is σ²₂ growing or stable?

BROADCAST: Nodes now transmit hypothesis confidence
           P(H₁|k=10), P(H₂|k=10), P(H₃|k=10)
           Are hypotheses excluding each other or coexisting?

CANDIDATE: Second-level hypotheses:
           H_A: fundamentally unpredictable (pure chaos)
           H_B: hidden stable configuration not yet detected
           H_C: instability has identifiable geometry

PROPAGATE: Loss₂ = divergence between passes 1 and 2
           If growing → more structure remains to be revealed

COMPOSE:   MAP → H_C
           The problem has identifiable geometry
```

We see structure inside the chaos. The system is not random — it has shape.

---

**PASS k=15 — Reading the geometry of instability**

```
SCAN:      σ²₃ < σ²₂ — approaching the bottom of this layer

BROADCAST: Nodes now transmit:
           P(manifold | current trajectory)
           Not states anymore — regions of solution space

CANDIDATE: H_α: trajectory inside stable manifold
           H_β: trajectory crossed the separatrix — collapse inevitable
           H_γ: system on the edge — sensitive to noise

PROPAGATE: Loss₃ = distance to structural separatrix
           λ = local divergence exponent
           λ > 0 → unstable
           λ < 0 → stable

COMPOSE:   MAP → H_γ
           The system is on the edge.
           Small noise determines the outcome.
```

---

## The Stopping Criterion

The problem "surrenders" when:

```
|σ²ₖ - σ²ₖ₋₁| < ε
```

When the variance between consecutive passes stops growing, the problem has
no more structure to reveal at this scale.

```
k=5  → we read chaos
k=10 → we read structure inside chaos
k=15 → we read geometry of instability
k=20 → the system does not converge

The non-convergence IS the answer.
```

This is the key result:

**ANALOGOS does not solve the problem.
It measures HOW MUCH it has no solution.**

The structural depth k at which σ² fails to converge is a new kind of
measurement — not a prediction, not a proof, but a **depth signature** of the
problem's irreducibility.

---

## On the Ontological Nature of This Result

Classical approaches produce **epistemological** limits: *we cannot know*
the answer. They describe a ceiling on prediction — a limit of the observer.

ANALOGOS produces something different: an **ontological** statement.

The structural depth k at which σ² fails to converge is not a property of our
measurement tools or computational power. It is a property of the problem
itself — of what the system *is*, independent of any observer.

When ANALOGOS returns non-convergence, it is not saying *"we ran out of
precision"*. It is saying *"irreducibility is baked into the structure of
this system"*.

| | Epistemological | Ontological |
|---|---|---|
| Question | What can we know? | What is the structure? |
| Classical limit | We cannot predict | — |
| ANALOGOS | — | The system IS irreducible at depth k |
| Limit belongs to | The observer | The problem itself |

> Depth is not ignorance measured.
> Depth is structure revealed.

---

## Why This Matters

This framework operates at the level of structural topology — not solving
equations but **mapping the structure of the problem space** recursively,
until the map either converges or reveals that no convergence is possible.

Non-convergence is not failure.
It is the most precise answer the system can give.

A problem that surrenders at k=5 is structurally simple.
A problem that surrenders at k=25 has rich internal structure.
A problem that never converges is genuinely irreducible.

That is now a measurable statement, not just a philosophical one.

---

## Applications

The same 5-primitive structure appears everywhere a system must process
information under uncertainty without access to ground truth:

- Complex decision-making under uncertainty
- Multi-agent coordination with incomplete information
- Recursive pattern detection in dynamic systems
- Any domain where classical prediction fails but structure remains

That is: almost everywhere that matters.

---

## The Framework

**ANALOGOS v0.5.0**
Available on PyPI: pypi.org/project/analogos/

```python
pip install analogos
```

The framework formalizes:
- The 5 primitives as composable operators
- The fractal depth k as a structural measurement
- The stopping criterion as a convergence test
- Non-convergence as information, not failure

---

*Classical methods ask what the answer is.*
*ANALOGOS measures how deep the question goes.*

*That is a different kind of answer.*
*And sometimes it's the only honest one available.*

---

*Copyright 2026 Zaqueu Ribeiro da Costa — Ω core*

#ANALOGOS #ComplexSystems #MachineLearning #BayesianInference #FractalMath #OpenSource
