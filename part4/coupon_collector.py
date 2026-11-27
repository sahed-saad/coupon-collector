"""
Coupon Collector: math vs. simulation, rare cards, and trading.
Fahim's part (Video 4). Requires only the standard library;
matplotlib is optional (used for the convergence plot).
"""
import random
from itertools import combinations


# ---------- Core simulation (the same idea as Video 3) ----------
def collect(n=5):
    """Mohammed's Part 3 code: buy packs until the set is complete."""
    owned = set()
    packs = 0
    while len(owned) < n:
        owned.add(random.randint(1, n))
        packs += 1
    return packs


def simulate_once(n, probs=None):
    """Buy one card at a time until we own all n cards. Return purchases."""
    owned = set()
    purchases = 0
    cards = list(range(n))
    while len(owned) < n:
        card = random.choices(cards, weights=probs)[0] if probs else random.randrange(n)
        owned.add(card)
        purchases += 1
    return purchases


def simulate_average(n, trials=10_000, probs=None):
    return sum(simulate_once(n, probs) for _ in range(trials)) / trials


# ---------- Math ----------
def expected_math(n):
    """E = n * (1 + 1/2 + ... + 1/n) for equally likely cards."""
    return n * sum(1 / k for k in range(1, n + 1))


def expected_math_unequal(probs):
    """Exact answer for unequal probabilities (inclusion-exclusion).
    E = sum over non-empty subsets S of (-1)^(|S|+1) / (sum of p in S).
    Only practical for small sets (2^n subsets)."""
    n = len(probs)
    total = 0.0
    for size in range(1, n + 1):
        sign = 1 if size % 2 == 1 else -1
        for subset in combinations(probs, size):
            total += sign / sum(subset)
    return total


def std_dev_math(n):
    """Exact standard deviation of one run: Var = n^2 * sum(1/k^2) - n*H_n."""
    var = n * n * sum(1 / k ** 2 for k in range(1, n + 1)) - expected_math(n)
    return var ** 0.5


# ---------- 1. Compare math vs simulation ----------
def comparison_table(sizes=(5, 10, 100), trials=10_000):
    print(f"{'Set size':>10} {'Math':>10} {'Simulation':>12} {'Gap':>8} {'Expected wobble (SE)':>22}")
    for n in sizes:
        m = expected_math(n)
        s = sum(collect(n) for _ in range(trials)) / trials
        se = std_dev_math(n) / trials ** 0.5
        print(f"{n:>10} {m:>10.2f} {s:>12.2f} {abs(m - s):>8.2f} {se:>22.2f}")


# ---------- 2. Show the gap shrinking with more runs ----------
def convergence(n=10, checkpoints=(10, 100, 1_000, 10_000, 100_000)):
    m = expected_math(n)
    print(f"\nConvergence for n={n} (math answer {m:.2f})")
    print(f"{'Runs':>10} {'Simulation':>12} {'Gap':>8} {'Expected wobble (SE)':>22}")
    total, runs = 0, 0
    for cp in checkpoints:
        while runs < cp:
            total += collect(n)
            runs += 1
        avg = total / runs
        se = std_dev_math(n) / runs ** 0.5
        print(f"{runs:>10} {avg:>12.2f} {abs(m - avg):>8.2f} {se:>22.2f}")


def convergence_plot(n=10, runs=20_000):
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed; skipping plot")
        return
    total, running = 0, []
    for i in range(1, runs + 1):
        total += simulate_once(n)
        running.append(total / i)
    plt.plot(running, label="Simulation average")
    plt.axhline(expected_math(n), color="red", linestyle="--", label="Math answer")
    plt.xscale("log")
    plt.xlabel("Number of simulated runs")
    plt.ylabel("Average packs needed")
    plt.title(f"Simulation converges to the math answer (n={n})")
    plt.legend()
    plt.savefig("convergence.png", dpi=150, bbox_inches="tight")
    print("Saved convergence.png")


# ---------- 3. Rare cards ----------
def rare_cards(n=10, num_rare=2, rare_weight=0.2, trials=20_000):
    """num_rare cards are `rare_weight` times as likely as a common card."""
    weights = [rare_weight] * num_rare + [1.0] * (n - num_rare)
    probs = [w / sum(weights) for w in weights]
    m = expected_math_unequal(probs)
    s = simulate_average(n, trials, probs)
    print(f"\nRare cards: {n} cards, {num_rare} of them {rare_weight}x as likely")
    print(f"  Equal-odds math answer: {expected_math(n):.2f}")
    print(f"  Rare-card math answer:  {m:.2f}")
    print(f"  Rare-card simulation:   {s:.2f}")


# ---------- 4. Trading with a friend ----------
def simulate_trading(n, trials=10_000, trade=True):
    """Two collectors each buy one card per round. Any time one holds a
    duplicate the other needs, they swap 1-for-1 (repeat until no trades).
    Returns average packs bought PER PERSON until both sets are complete."""
    total = 0
    for _ in range(trials):
        a, b = {}, {}  # card -> count
        rounds = 0
        while not (len(a) == n and len(b) == n):
            for hand in (a, b):
                c = random.randrange(n)
                hand[c] = hand.get(c, 0) + 1
            rounds += 1
            # trade until nobody can help the other
            while trade:
                a_spare_for_b = [c for c, k in a.items() if k > 1 and c not in b]
                b_spare_for_a = [c for c, k in b.items() if k > 1 and c not in a]
                if not a_spare_for_b or not b_spare_for_a:
                    break
                x, y = a_spare_for_b[0], b_spare_for_a[0]
                a[x] -= 1; b[x] = b.get(x, 0) + 1
                b[y] -= 1; a[y] = a.get(y, 0) + 1
        total += rounds
    return total / trials


def trading_comparison(n=10, trials=10_000):
    solo = simulate_trading(n, trials, trade=False)  # two people, no trading
    traded = simulate_trading(n, trials, trade=True)
    print(f"\nTrading with a friend ({n} cards, 1-for-1 swaps of duplicates)")
    print("  Packs each person buys until BOTH sets are complete:")
    print(f"  No trading: {solo:.2f}")
    print(f"  Trading:    {traded:.2f}")
    print(f"  Savings from trading: {100 * (solo - traded) / solo:.1f}%")


if __name__ == "__main__":
    random.seed(42)  # remove for different results each run
    comparison_table()
    convergence()
    convergence_plot()
    rare_cards()
    trading_comparison()
