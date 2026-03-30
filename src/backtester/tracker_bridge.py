"""Optional bet-tracker integration.

Replays backtest results into a bet-tracker database for
persistent storage and model evaluation via betting-math-kit.

Requires: pip install bet-tracker
"""

from __future__ import annotations

from .types import BacktestResult

try:
    from bet_tracker import BetStatus, BetTracker

    _HAS_TRACKER = True
except ImportError:
    _HAS_TRACKER = False


def replay_to_tracker(
    result: BacktestResult,
    db_path: str = ":memory:",
) -> object:
    """Replay backtest bets into a BetTracker database.

    Each non-pass bet record is logged as a placed bet, then
    immediately settled. The tracker's bankroll starts with a
    deposit matching the backtest's starting bankroll.

    Args:
        result: A completed BacktestResult.
        db_path: Path to SQLite database (":memory:" for in-memory).

    Returns:
        BetTracker instance with all bets logged.

    Raises:
        ImportError: If bet-tracker is not installed.
    """
    if not _HAS_TRACKER:
        raise ImportError(
            "Tracker bridge requires bet-tracker. "
            "Install it with: pip install bet-tracker"
        )

    tracker = BetTracker(db_path)
    tracker.deposit(result.starting_bankroll)

    for record in result.records:
        if record.side == "pass":
            continue

        bet_id = tracker.place_bet(
            sport="backtest",
            event=record.game_id,
            market="moneyline",
            selection=record.side,
            odds=record.odds,
            stake=record.stake,
            model_prob=record.model_prob,
            fair_prob=record.fair_prob,
            edge=record.edge,
        )

        if record.won is True:
            tracker.settle(bet_id, BetStatus.WON)
        elif record.won is False:
            tracker.settle(bet_id, BetStatus.LOST)

    return tracker
