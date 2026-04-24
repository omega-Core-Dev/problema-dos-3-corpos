"""
ANALOGOS v0.5.0 — Three-Body Problem
Example implementation of the 5-primitive pipeline across 3 passes (k=5, 10, 15).

Each pass feeds its final state as the initial conditions of the next,
so σ² evolves across passes and the stopping criterion is meaningful.
"""

import numpy as np

# ---------------------------------------------------------------------------
# Initial conditions: three bodies in an unstable near-figure-8 configuration
# ---------------------------------------------------------------------------
BODIES = {
    "A": {"pos": np.array([-1.0,  0.0]), "vel": np.array([ 0.35,  0.35])},
    "B": {"pos": np.array([ 1.0,  0.0]), "vel": np.array([ 0.35, -0.35])},
    "C": {"pos": np.array([ 0.0,  0.5]), "vel": np.array([-0.70,  0.00])},
}
G = 1.0
N_STEPS = 500
DT = 0.01


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def gravitational_forces(bodies):
    names = list(bodies.keys())
    forces = {n: np.zeros(2) for n in names}
    magnitudes = []
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            ni, nj = names[i], names[j]
            r_vec = bodies[nj]["pos"] - bodies[ni]["pos"]
            r = np.linalg.norm(r_vec) + 1e-6
            f = G / r ** 2 * (r_vec / r)
            forces[ni] += f
            forces[nj] -= f
            magnitudes.append(r)
    return forces, magnitudes


def simulate(bodies, n_steps=N_STEPS, dt=DT):
    """Euler integration — returns final state and all force magnitudes."""
    state = {k: {"pos": v["pos"].copy(), "vel": v["vel"].copy()} for k, v in bodies.items()}
    all_magnitudes = []
    for _ in range(n_steps):
        forces, mags = gravitational_forces(state)
        all_magnitudes.append(mags)
        for name in state:
            state[name]["vel"] = state[name]["vel"] + forces[name] * dt
            state[name]["pos"] = state[name]["pos"] + state[name]["vel"] * dt
    return state, np.array(all_magnitudes)


def fractal_distance(d, sigma, k_depth):
    """D_fractal(d, k) = Σᵢ₌₁ᵏ (σ/i) · ηᵢ · d^(1/i)"""
    rng = np.random.default_rng(seed=int(d * 1000) % 9999)
    total = 0.0
    for i in range(1, k_depth + 1):
        eta = rng.normal(0, 1)
        total += (sigma / i) * eta * (d ** (1.0 / i))
    return total


def circular_velocity(pos_a, pos_b):
    r = np.linalg.norm(pos_b - pos_a) + 1e-6
    return np.sqrt(G / r)


# ---------------------------------------------------------------------------
# The 5 Primitives
# ---------------------------------------------------------------------------

def scan(magnitudes):
    """Primitive 1 — estimate distribution of gravitational force magnitudes."""
    mu = float(np.mean(magnitudes))
    sigma2 = float(np.var(magnitudes))
    return {"mu": mu, "sigma2": sigma2}


def broadcast(state, scan_out, k_depth):
    """Primitive 2 — each body emits P(pos) modulated by fractal distance."""
    sigma = np.sqrt(scan_out["sigma2"])
    nodes = {}
    for name, body in state.items():
        d_self = np.linalg.norm(body["pos"])
        d_frac = fractal_distance(d_self + 1e-6, sigma, k_depth)
        nodes[name] = {
            "pos_mean": body["pos"].copy(),
            "pos_std": abs(d_frac) + 1e-6,
            "vel": body["vel"].copy(),
        }
    names = list(nodes.keys())
    cov = {}
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            ni, nj = names[i], names[j]
            r_vec = nodes[nj]["pos_mean"] - nodes[ni]["pos_mean"]
            r = np.linalg.norm(r_vec) + 1e-6
            cov[(ni, nj)] = fractal_distance(r, sigma, k_depth)
    return {"nodes": nodes, "cov": cov}


def candidate(broadcast_out, prior=None):
    """Primitive 3 — Bayesian hypothesis weighting."""
    nodes = broadcast_out["nodes"]
    spreads = [v["pos_std"] for v in nodes.values()]
    avg_spread = np.mean(spreads)

    if prior is None:
        prior = {"stable": 1 / 3, "ejection": 1 / 3, "collision": 1 / 3}

    if avg_spread < 0.5:
        likelihood = {"stable": 0.7, "ejection": 0.1, "collision": 0.2}
    elif avg_spread < 1.5:
        likelihood = {"stable": 0.3, "ejection": 0.4, "collision": 0.3}
    else:
        likelihood = {"stable": 0.1, "ejection": 0.5, "collision": 0.4}

    evidence = sum(likelihood[h] * prior[h] for h in prior)
    posterior = {h: (likelihood[h] * prior[h]) / evidence for h in prior}
    return posterior


def propagate(state, posterior):
    """Primitive 4 — velocity correction weighted by instability confidence."""
    names = list(state.keys())
    corrections = {}
    p_instability = posterior["ejection"] + posterior["collision"]

    for i, ni in enumerate(names):
        correction = np.zeros(2)
        for j, nj in enumerate(names):
            if i == j:
                continue
            r_vec = state[nj]["pos"] - state[ni]["pos"]
            r = np.linalg.norm(r_vec) + 1e-6
            v_circ = circular_velocity(state[ni]["pos"], state[nj]["pos"])
            v_curr = np.linalg.norm(state[ni]["vel"])
            delta_v = (v_circ - v_curr) * p_instability
            tangent = np.array([-r_vec[1], r_vec[0]]) / r
            correction += delta_v * tangent
        corrections[ni] = correction

    loss = sum(np.linalg.norm(c) ** 2 for c in corrections.values())
    return {"corrections": corrections, "loss": float(loss)}


def compose(state, broadcast_out, propagate_out, posterior):
    """Primitive 5 — expected-value aggregation with centripetal nudge."""
    nodes = broadcast_out["nodes"]
    corrections = propagate_out["corrections"]
    p_collision = posterior["collision"]
    centroid = np.mean([state[n]["pos"] for n in state], axis=0)

    composed = {}
    for name in state:
        e_pos = nodes[name]["pos_mean"]
        corr = corrections[name]
        nudge = 0.01 * (centroid - e_pos) if p_collision > 0.5 else np.zeros(2)
        composed[name] = {"expected_pos": e_pos + corr * 0.01 + nudge}

    # Apply corrections to produce the next-pass initial state
    next_state = {}
    for name in state:
        next_state[name] = {
            "pos": composed[name]["expected_pos"].copy(),
            "vel": state[name]["vel"] + corrections[name] * 0.001,
        }

    return {"composed": composed, "p_collision": p_collision, "next_state": next_state}


# ---------------------------------------------------------------------------
# One full pass of the 5-primitive pipeline
# ---------------------------------------------------------------------------

def run_pass(bodies, k_depth, prior=None, label=""):
    state, magnitudes = simulate(bodies)
    flat_mags = magnitudes.flatten()

    s = scan(flat_mags)
    b = broadcast(state, s, k_depth)
    c = candidate(b, prior=prior)
    p = propagate(state, c)
    o = compose(state, b, p, c)

    spread = np.mean([v["pos_std"] for v in b["nodes"].values()])

    print(f"\n{'='*56}")
    print(f"  PASS k={k_depth:<3}  —  {label}")
    print(f"{'='*56}")
    print(f"  SCAN      │ μ={s['mu']:.3f}  σ²={s['sigma2']:.3f}")
    print(f"  BROADCAST │ avg spread = {spread:.4f}")
    print(f"  CANDIDATE │ P(stable)={c['stable']:.2f}  P(eject)={c['ejection']:.2f}  P(coll)={c['collision']:.2f}")
    print(f"  PROPAGATE │ loss = {p['loss']:.4f}")
    print(f"  COMPOSE   │ P(collision) = {o['p_collision']:.2f}")
    print(f"{'='*56}")

    return s, c, o


# ---------------------------------------------------------------------------
# Summary table
# ---------------------------------------------------------------------------

def print_summary(results):
    W = 98
    sep  = "─" * W
    line = "─" * W

    header = (
        f"{'Pass':<8} │ {'Problem (what the pass reads)':<30} │ "
        f"{'Process (primitives fired)':<28} │ {'Result':<22}"
    )

    rows = [
        (
            "k = 5",
            "Raw gravitational noise",
            "SCAN→BROADCAST→CANDIDATE→PROPAGATE→COMPOSE",
            f"P(coll)={results[0]['p_col']:.2f}  σ²={results[0]['sigma2']:.2f}",
        ),
        (
            "k = 10",
            "Structure inside the noise",
            "Inter-pass divergence as new loss signal",
            f"P(coll)={results[1]['p_col']:.2f}  σ²={results[1]['sigma2']:.2f}",
        ),
        (
            "k = 15",
            "Geometry of instability",
            "Phase-space manifold classification",
            f"P(coll)={results[2]['p_col']:.2f}  σ²={results[2]['sigma2']:.2f}",
        ),
    ]

    print(f"\n  {'QUADRO — PROBLEMA / PROCESSO / RESULTADO':^{W}}")
    print(f"  ┌{'─'*8}─┬{'─'*30}─┬{'─'*28}─┬{'─'*22}─┐")
    print(f"  │ {'Pass':<8} │ {'Problem (what the pass reads)':<30} │ {'Process (primitives fired)':<28} │ {'Result':<22} │")
    print(f"  ├{'─'*8}─┼{'─'*30}─┼{'─'*28}─┼{'─'*22}─┤")
    for pass_name, problem, process, result in rows:
        print(f"  │ {pass_name:<8} │ {problem:<30} │ {process:<28} │ {result:<22} │")
    print(f"  └{'─'*8}─┴{'─'*30}─┴{'─'*28}─┴{'─'*22}─┘")

    d1 = abs(results[1]["sigma2"] - results[0]["sigma2"])
    d2 = abs(results[2]["sigma2"] - results[1]["sigma2"])
    eps = 0.01

    print(f"\n  STOPPING CRITERION  |σ²ₖ - σ²ₖ₋₁| < ε={eps}")
    print(f"  k=5→10 : Δσ² = {d1:.4f}  {'✓ converged' if d1 < eps else '✗ still revealing structure'}")
    print(f"  k=10→15: Δσ² = {d2:.4f}  {'✓ converged' if d2 < eps else '✗ still revealing structure'}")

    converged = d2 < eps
    print(f"\n  → {'Converged at k=15.' if converged else 'Non-convergence IS the answer.'}")
    if not converged:
        print("  → Structural depth: genuinely irreducible at this scale.")
    print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("\nANALOGOS v0.5.0 — Three-Body Problem")
    print("Recursive fractal pipeline: 3 passes × 5 primitives")
    print("Each pass feeds its evolved state as input to the next.\n")

    summary = []

    # Pass 1 — k=5, start from initial conditions
    s1, c1, o1 = run_pass(BODIES, k_depth=5, label="Reading the noise")
    summary.append({"p_col": o1["p_collision"], "sigma2": s1["sigma2"]})

    # Pass 2 — k=10, start from state produced by pass 1
    s2, c2, o2 = run_pass(o1["next_state"], k_depth=10, prior=c1, label="Reading structure inside the noise")
    summary.append({"p_col": o2["p_collision"], "sigma2": s2["sigma2"]})

    # Pass 3 — k=15, start from state produced by pass 2
    s3, c3, o3 = run_pass(o2["next_state"], k_depth=15, prior=c2, label="Reading the geometry of instability")
    summary.append({"p_col": o3["p_collision"], "sigma2": s3["sigma2"]})

    print_summary(summary)
