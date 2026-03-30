"""Core backtest engine — evaluates games and places bets."""

from __future__ import annotations

from betting_math_kit import devig, kelly_fraction

from .config import BacktestConfig
from .exceptions import DataError
from .types import BacktestResult, BetRecord, Game


def run_backtest(
    games: list[Game],
    config: BacktestConfig | None = None,
) -> BacktestResult:
    """Run a walk-forward backtest over a sequence of games.

    For each game, the engine:
    1. De-vigs the market odds to get fair probabilities.
    2. Computes edge (model_prob - fair_prob) for each side.
    3. If the best edge exceeds min_edge, sizes the bet via Kelly.
    4. Records the outcome and updates the bankroll.

    No future information is used — each decision uses only the
    current game's data and the bankroll at that point.

    Args:
        games: Sequence of games to evaluate in order.
        config: Backtest configuration. Uses defaults if None.

    Returns:
        BacktestResult with full records and aggregate metrics.

    Raises:
        DataError: If games is empty.
    """
    if not games:
        raise DataError("No games to backtest")

    if config is None:
        config = BacktestConfig()

    bankroll = config.starting_bankroll
    peak = bankroll
    max_drawdown = 0.0
    total_staked = 0.0
    records: list[BetRecord] = []
    bankroll_curve: list[float] = []

    for game in games:
        record = _evaluate_game(game, bankroll, config)
        bankroll = record.bankroll_after

        if record.side != "pass":
            total_staked += record.stake

        # Track drawdown
        if bankroll > peak:
            peak = bankroll
        if peak > 0:
            dd = (peak - bankroll) / peak
            if dd > max_drawdown:
                max_drawdown = dd

        records.append(record)
        bankroll_curve.append(bankroll)

    # Aggregate stats
    bet_records = [r for r in records if r.side != "pass"]
    wins = sum(1 for r in bet_records if r.won is True)
    losses = sum(1 for r in bet_records if r.won is False)
    total_bets = len(bet_records)
    win_rate = wins / total_bets if total_bets > 0 else 0.0
    pnl = bankroll - config.starting_bankroll
    roi = pnl / total_staked if total_staked > 0 else 0.0

    # Brier score over all games
    brier = _brier_score(games)

    edge_dist = [r.edge for r in bet_records]

    return BacktestResult(
        label=config.label,
        starting_bankroll=config.starting_bankroll,
        final_bankroll=bankroll,
        total_games=len(games),
        total_bets=total_bets,
        wins=wins,
        losses=losses,
        win_rate=win_rate,
        pnl=pnl,
        roi=roi,
        max_drawdown=max_drawdown,
        brier_score=brier,
        bankroll_curve=bankroll_curve,
        edge_distribution=edge_dist,
        records=records,
    )


def _evaluate_game(game: Game, bankroll: float, config: BacktestConfig) -> BetRecord:
    """Evaluate a single game and return a bet record."""
    # De-vig to get fair probabilities
    result = devig(game.home_odds, game.away_odds, method=config.devig_method)
    fair_home = result.fair_home
    fair_away = result.fair_away

    # Compute edges
    model_prob_away = 1.0 - game.model_prob_home
    edge_home = game.model_prob_home - fair_home
    edge_away = model_prob_away - fair_away

    # Pick the best side
    if edge_home >= edge_away and edge_home >= config.min_edge:
        side = "home"
        odds = game.home_odds
        fair_prob = fair_home
        model_prob = game.model_prob_home
        edge = edge_home
    elif edge_away > edge_home and edge_away >= config.min_edge:
        side = "away"
        odds = game.away_odds
        fair_prob = fair_away
        model_prob = model_prob_away
        edge = edge_away
    else:
        # Pass — no edge
        return BetRecord(
            game_id=game.game_id,
            side="pass",
            odds=0,
            fair_prob=0.0,
            model_prob=0.0,
            edge=0.0,
            stake=0.0,
            won=None,
            pnl=0.0,
            bankroll_after=bankroll,
        )

    # Size the bet via Kelly
    raw_fraction = kelly_fraction(model_prob, odds) * config.kelly_fraction

    # Apply constraints
    stake = raw_fraction * bankroll
    max_stake = config.max_stake_pct * bankroll
    stake = min(stake, max_stake)
    stake = round(stake, 2)

    if stake < config.min_bet:
        return BetRecord(
            game_id=game.game_id,
            side="pass",
            odds=0,
            fair_prob=0.0,
            model_prob=0.0,
            edge=0.0,
            stake=0.0,
            won=None,
            pnl=0.0,
            bankroll_after=bankroll,
        )

    # Determine outcome
    decimal_odds = _american_to_decimal(odds)
    won = (side == "home" and game.outcome == 1) or (
        side == "away" and game.outcome == 0
    )
    profit = stake * (decimal_odds - 1) if won else -stake
    bankroll_after = round(bankroll + profit, 2)

    return BetRecord(
        game_id=game.game_id,
        side=side,
        odds=odds,
        fair_prob=fair_prob,
        model_prob=model_prob,
        edge=edge,
        stake=stake,
        won=won,
        pnl=round(profit, 2),
        bankroll_after=bankroll_after,
    )


def _american_to_decimal(odds: int) -> float:
    """Convert American odds to decimal."""
    if odds > 0:
        return 1.0 + odds / 100.0
    else:
        return 1.0 + 100.0 / abs(odds)


def _brier_score(games: list[Game]) -> float:
    """Compute Brier score over all games."""
    total = 0.0
    for g in games:
        total += (g.model_prob_home - g.outcome) ** 2
    return total / len(games)
