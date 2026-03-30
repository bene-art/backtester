"""Synthetic game data generation for backtesting."""

from __future__ import annotations

import random

from .exceptions import DataError
from .types import Game


def generate_games(
    n: int = 500,
    edge: float = 0.03,
    sport: str = "NFL",
    seed: int | None = 42,
) -> list[Game]:
    """Generate synthetic games with controllable model edge.

    Creates games where the model's probability estimates have a known
    average edge over the true probabilities, which are themselves slightly
    better than the market-implied probabilities.

    Args:
        n: Number of games to generate.
        edge: Average model edge over market (e.g. 0.03 = 3%).
        sport: Sport label for generated games.
        seed: Random seed for reproducibility. None for random.

    Returns:
        List of Game objects sorted by timestamp.

    Raises:
        DataError: If n < 1 or edge is out of range.
    """
    if n < 1:
        raise DataError("n must be at least 1")
    if not -0.5 <= edge <= 0.5:
        raise DataError("edge must be between -0.5 and 0.5")

    rng = random.Random(seed)
    games: list[Game] = []

    for i in range(n):
        # True probability for home team (Beta-distributed, centered ~0.5)
        true_prob = _clamp(rng.betavariate(2.5, 2.5), 0.05, 0.95)

        # Market adds vig: shift true_prob slightly toward 0.5
        vig_shift = (0.5 - true_prob) * 0.08
        market_prob_home = _clamp(true_prob + vig_shift, 0.05, 0.95)

        # Model captures some of the true edge + has noise
        noise = rng.gauss(0, 0.04)
        model_prob = _clamp(true_prob + edge + noise, 0.01, 0.99)

        # Convert market probs to American odds (with ~4.5% total vig)
        vig_factor = 1.045
        home_implied = market_prob_home * vig_factor
        away_implied = (1 - market_prob_home) * vig_factor
        home_odds = _prob_to_american(home_implied)
        away_odds = _prob_to_american(away_implied)

        # Outcome determined by true probability
        outcome = 1 if rng.random() < true_prob else 0

        teams_home = f"Team{i * 2:04d}"
        teams_away = f"Team{i * 2 + 1:04d}"

        games.append(
            Game(
                game_id=f"game_{i:04d}",
                sport=sport,
                event=f"{teams_home} vs {teams_away}",
                home_odds=home_odds,
                away_odds=away_odds,
                outcome=outcome,
                model_prob_home=model_prob,
                timestamp=f"2026-01-{(i % 28) + 1:02d}T13:00:00",
            )
        )

    return games


def _clamp(value: float, lo: float, hi: float) -> float:
    """Clamp value to [lo, hi]."""
    return max(lo, min(hi, value))


def _prob_to_american(implied_prob: float) -> int:
    """Convert implied probability to American odds."""
    if implied_prob >= 0.5:
        return round(-100 * implied_prob / (1 - implied_prob))
    else:
        return round(100 * (1 - implied_prob) / implied_prob)
