"""Backtester exception hierarchy."""


class BacktesterError(Exception):
    """Base exception for all backtester errors."""


class ConfigError(BacktesterError, ValueError):
    """Invalid backtest configuration."""


class DataError(BacktesterError, ValueError):
    """Invalid or insufficient game data."""
