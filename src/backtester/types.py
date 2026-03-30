"""Core data types for backtesting."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Game:
    """A single game with odds and outcome.

    Attributes:
        game_id: Unique identifier.
        sport: Sport name (e.g. "NFL").
        event: Event description (e.g. "Chiefs vs Ravens").
        home_odds: American odds for home team.
        away_odds: American odds for away team.
        outcome: 1 if home won, 0 if away won.
        model_prob_home: Model's probability that home wins.
        timestamp: ISO-8601 timestamp string.
    """

    game_id: str
    sport: str
    event: str
    home_odds: int
    away_odds: int
    outcome: int
    model_prob_home: float
    timestamp: str


@dataclass(frozen=True)
class BetRecord:
    """Record of a betting decision on a single game.

    Attributes:
        game_id: Which game this decision was for.
        side: "home", "away", or "pass".
        odds: American odds taken (0 if pass).
        fair_prob: De-vigged fair probability (0.0 if pass).
        model_prob: Model probability for the chosen side (0.0 if pass).
        edge: model_prob - fair_prob (0.0 if pass).
        stake: Dollar amount wagered (0.0 if pass).
        won: Whether the bet won (None if pass).
        pnl: Profit/loss on this bet (0.0 if pass).
        bankroll_after: Bankroll after this decision.
    """

    game_id: str
    side: str
    odds: int
    fair_prob: float
    model_prob: float
    edge: float
    stake: float
    won: bool | None
    pnl: float
    bankroll_after: float


@dataclass(frozen=True)
class BacktestResult:
    """Aggregate results from a backtest run.

    Attributes:
        label: Descriptive label for this run.
        starting_bankroll: Initial bankroll.
        final_bankroll: Bankroll at end of backtest.
        total_games: Number of games evaluated.
        total_bets: Number of bets placed (non-pass).
        wins: Number of winning bets.
        losses: Number of losing bets.
        win_rate: wins / total_bets.
        pnl: final_bankroll - starting_bankroll.
        roi: pnl / total amount staked.
        max_drawdown: Largest peak-to-trough decline (fraction).
        brier_score: Brier score over all games.
        bankroll_curve: Bankroll after each game.
        edge_distribution: List of edges for placed bets.
        records: Full list of BetRecords.
    """

    label: str
    starting_bankroll: float
    final_bankroll: float
    total_games: int
    total_bets: int
    wins: int
    losses: int
    win_rate: float
    pnl: float
    roi: float
    max_drawdown: float
    brier_score: float
    bankroll_curve: list[float]
    edge_distribution: list[float]
    records: list[BetRecord]
