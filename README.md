# backtester

[![CI](https://github.com/bene-art/backtester/actions/workflows/ci.yml/badge.svg)](https://github.com/bene-art/backtester/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Walk-forward sports betting backtester. Synthetic data, strategy comparison, zero lookahead bias. Pure Python.

## Where this fits

[props-scorer](https://github.com/bene-art/props-scorer) tells you *what's going to happen*. [betting-math-kit](https://github.com/bene-art/betting-math-kit) tells you *what to do about it*. [bet-tracker](https://github.com/bene-art/bet-tracker) answers *did it work?* This repo answers the question before all of that: **would this strategy have worked?**

```
props-scorer              betting-math-kit              bet-tracker
┌──────────────┐  prob   ┌────────────────────┐  bet   ┌──────────────────────┐
│ player stats │ ──────→ │ de-vig → edge →    │ ─────→ │ log bet              │
│ → XGBoost    │         │ Kelly → stake size  │        │ capture closing line │
│ → probability│         │                    │        │ settle → evaluate    │
└──────────────┘         └────────────────────┘        └──────────────────────┘
       ▲                        ▲                              │
       │                        │                              │
       │                 ┌──────┴──────────┐                   │
       │                 │   backtester    │◄──────────────────┘
       │                 │ synthetic data  │
       │                 │ walk-forward    │
       │                 │ strategy compare│
       │                 └─────────────────┘
       │                        │
       └──── tune model ◄──────┘
```

You have a model. You have the math. Before you risk real money, you want to know: does this strategy survive 500 games? What happens if I use quarter-Kelly instead of half? Does tightening the edge filter help or just reduce volume?

This backtester answers those questions with synthetic data that mimics real market structure — vig, noise, and all.

## Install

```bash
pip install backtester
```

With [bet-tracker](https://github.com/bene-art/bet-tracker) integration:

```bash
pip install backtester[tracker]
```

Or from source:

```bash
git clone https://github.com/bene-art/backtester.git
cd backtester
pip install -e ".[dev]"
```

---

## Quick start

```python
from backtester import generate_games, run_backtest, format_summary

# Generate 500 synthetic games with 3% model edge
games = generate_games(n=500, edge=0.03, seed=42)

# Run the backtest with default config
result = run_backtest(games)

print(format_summary(result))
# === Backtest ===
# Games: 500  |  Bets: 312  |  Pass rate: 38%
# Win rate: 54.2% (169W / 143L)
# P&L: +$142.35  |  ROI: 4.2%
# Bankroll: $1,000.00 -> $1,142.35
# Max drawdown: 8.3%
# Brier score: 0.2418
# Avg edge: 5.1%
```

## How it works

For each game, the engine:

1. **De-vigs** the market odds → fair probabilities (via betting-math-kit)
2. **Computes edge** → model probability minus fair probability, both sides
3. **Filters** → only bets where edge exceeds your minimum
4. **Sizes** → fractional Kelly with bankroll caps
5. **Settles** → updates bankroll, records everything

No future information is used. Each decision sees only the current game and the current bankroll. This is walk-forward — the same way you'd actually bet.

## Strategy comparison

The whole point of backtesting is comparing strategies. Same games, different configs:

```python
from backtester import BacktestConfig, compare, format_comparison, generate_games

games = generate_games(n=500, edge=0.03, seed=42)

configs = [
    BacktestConfig(kelly_fraction=0.10, label="10% Kelly"),
    BacktestConfig(kelly_fraction=0.25, label="25% Kelly"),
    BacktestConfig(kelly_fraction=0.50, label="50% Kelly"),
    BacktestConfig(min_edge=0.01, label="Low filter"),
    BacktestConfig(min_edge=0.05, label="Tight filter"),
]

results = compare(games, configs)
print(format_comparison(results))
```

Because the games are identical across runs, differences in results come entirely from your strategy choices.

## Configuration

```python
from backtester import BacktestConfig

config = BacktestConfig(
    starting_bankroll=1000.0,   # initial bankroll ($)
    kelly_fraction=0.25,        # fraction of full Kelly (0-1]
    min_edge=0.03,              # minimum edge to bet (3%)
    max_stake_pct=0.05,         # max 5% of bankroll per bet
    devig_method="multiplicative",  # de-vig algorithm
    min_bet=1.0,                # minimum bet size ($)
    label="quarter kelly",      # label for comparison
)
```

All constraints are enforced per-bet: if Kelly says bet $200 but `max_stake_pct` caps at $50, you bet $50. If the sized bet is below `min_bet`, you pass.

## Synthetic data

```python
from backtester import generate_games

games = generate_games(
    n=500,          # number of games
    edge=0.03,      # average model edge over market
    sport="NFL",    # sport label
    seed=42,        # reproducible results
)
```

Each game has:
- **True probability** drawn from Beta(2.5, 2.5) — centered, realistic spread
- **Market odds** with ~4.5% total vig baked in
- **Model probability** = true prob + edge + noise (Gaussian, σ=0.04)
- **Outcome** determined by the true probability

The edge parameter controls how much better your model is than the market. `edge=0` means your model is as good as the market. `edge=0.03` means you're 3% better on average.

## bet-tracker bridge

Replay backtest results into a [bet-tracker](https://github.com/bene-art/bet-tracker) database for persistent storage and model evaluation:

```python
from backtester import generate_games, run_backtest
from backtester.tracker_bridge import replay_to_tracker

games = generate_games(n=200, seed=42)
result = run_backtest(games)

# Replay into a tracker database
tracker = replay_to_tracker(result, db_path="backtest_bets.db")

# Now use bet-tracker's full evaluation suite
eval_result = tracker.evaluate()
print(f"Brier: {eval_result.brier_score:.4f}")
print(f"CLV: {eval_result.mean_clv}")
```

## API reference

| Function | What it does |
|----------|-------------|
| `generate_games(n, edge, sport, seed)` | Create synthetic game data |
| `run_backtest(games, config)` | Run walk-forward backtest |
| `compare(games, configs)` | Run same games through multiple strategies |
| `format_summary(result)` | Human-readable single-run summary |
| `format_comparison(results)` | Side-by-side strategy comparison |
| `replay_to_tracker(result, db_path)` | Bridge to bet-tracker (optional) |

| Type | What it is |
|------|-----------|
| `Game` | Single game with odds, outcome, model probability |
| `BetRecord` | Engine's decision on one game (bet or pass) |
| `BacktestResult` | Aggregate results + full record list |
| `BacktestConfig` | Strategy configuration (frozen dataclass) |

## Testing

```bash
pip install -e ".[dev]"
pip install bet-tracker   # for bridge tests
pytest
```

```bash
ruff check src/ tests/
ruff format src/ tests/
mypy src/backtester/
```

CI runs on Python 3.10 - 3.13.

---

## Where this fits in the system

Four repos, four concerns:

| Repo | Question it answers |
|------|-------------------|
| [**props-scorer**](https://github.com/bene-art/props-scorer) | What's going to happen? |
| [**betting-math-kit**](https://github.com/bene-art/betting-math-kit) | What should I do about it? |
| [**bet-tracker**](https://github.com/bene-art/bet-tracker) | Did it work? |
| [**backtester**](https://github.com/bene-art/backtester) | Would it have worked? |

They work independently or together. The backtester uses betting-math-kit for all its math (de-vig, Kelly sizing) and can replay results into bet-tracker for persistent evaluation. props-scorer provides the probabilities that feed into everything else.

## License

MIT

## Author

Benjamin Easington — [GitHub](https://github.com/bene-art)
