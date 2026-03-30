"""Walk-forward sports betting backtester.

Ties together betting-math-kit (de-vig, Kelly, metrics) with
synthetic or historical game data to evaluate betting strategies
without risking real money.
"""

from .compare import compare
from .config import BacktestConfig
from .engine import run_backtest
from .exceptions import BacktesterError, ConfigError, DataError
from .results import format_comparison, format_summary
from .synthetic import generate_games
from .tracker_bridge import replay_to_tracker
from .types import BacktestResult, BetRecord, Game

__all__ = [
    "BacktestConfig",
    "BacktestResult",
    "BacktesterError",
    "BetRecord",
    "ConfigError",
    "DataError",
    "Game",
    "compare",
    "format_comparison",
    "format_summary",
    "generate_games",
    "replay_to_tracker",
    "run_backtest",
]

__version__ = "0.1.0"
