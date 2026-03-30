"""Compare backtest runs across different configurations."""

from __future__ import annotations

from .config import BacktestConfig
from .engine import run_backtest
from .types import BacktestResult, Game


def compare(
    games: list[Game],
    configs: list[BacktestConfig],
) -> list[BacktestResult]:
    """Run the same games through multiple configurations.

    This is the core of walk-forward comparison: same data,
    different strategies. Because the games are identical,
    differences in results are entirely due to config choices.

    Args:
        games: Games to backtest (same for all configs).
        configs: List of configurations to compare.

    Returns:
        List of BacktestResults, one per config.
    """
    return [run_backtest(games, config) for config in configs]
