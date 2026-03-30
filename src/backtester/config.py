"""Backtest configuration."""

from __future__ import annotations

from dataclasses import dataclass

from .exceptions import ConfigError


@dataclass(frozen=True)
class BacktestConfig:
    """Configuration for a backtest run.

    Attributes:
        starting_bankroll: Initial bankroll in dollars.
        kelly_fraction: Fractional Kelly multiplier (0 < f <= 1).
        min_edge: Minimum edge required to place a bet.
        max_stake_pct: Maximum stake as fraction of bankroll.
        devig_method: De-vig method name (e.g. "multiplicative").
        min_bet: Minimum bet size in dollars.
        label: Descriptive label for this config.
    """

    starting_bankroll: float = 1000.0
    kelly_fraction: float = 0.25
    min_edge: float = 0.03
    max_stake_pct: float = 0.05
    devig_method: str = "multiplicative"
    min_bet: float = 1.0
    label: str = ""

    def __post_init__(self) -> None:
        if self.starting_bankroll <= 0:
            raise ConfigError("starting_bankroll must be positive")
        if not 0 < self.kelly_fraction <= 1:
            raise ConfigError("kelly_fraction must be in (0, 1]")
        if self.min_edge < 0:
            raise ConfigError("min_edge must be non-negative")
        if not 0 < self.max_stake_pct <= 1:
            raise ConfigError("max_stake_pct must be in (0, 1]")
        if self.min_bet < 0:
            raise ConfigError("min_bet must be non-negative")
