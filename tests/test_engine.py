"""Tests for the backtest engine."""

import pytest

from backtester import (
    BacktestConfig,
    BacktestResult,
    DataError,
    generate_games,
    run_backtest,
)


class TestRunBacktest:
    def test_returns_result(self):
        games = generate_games(n=50, seed=42)
        result = run_backtest(games)
        assert isinstance(result, BacktestResult)
        assert result.total_games == 50

    def test_default_config(self):
        games = generate_games(n=20, seed=42)
        result = run_backtest(games)
        assert result.starting_bankroll == 1000.0

    def test_custom_config(self):
        games = generate_games(n=20, seed=42)
        config = BacktestConfig(starting_bankroll=5000.0, label="big")
        result = run_backtest(games, config)
        assert result.starting_bankroll == 5000.0
        assert result.label == "big"

    def test_bankroll_curve_length(self):
        games = generate_games(n=30, seed=42)
        result = run_backtest(games)
        assert len(result.bankroll_curve) == 30

    def test_records_length(self):
        games = generate_games(n=30, seed=42)
        result = run_backtest(games)
        assert len(result.records) == 30

    def test_bets_plus_passes_equals_games(self):
        games = generate_games(n=100, seed=42)
        result = run_backtest(games)
        passes = sum(1 for r in result.records if r.side == "pass")
        assert result.total_bets + passes == result.total_games

    def test_wins_plus_losses(self):
        games = generate_games(n=100, seed=42)
        result = run_backtest(games)
        assert result.wins + result.losses == result.total_bets

    def test_pnl_equals_final_minus_start(self):
        games = generate_games(n=50, seed=42)
        result = run_backtest(games)
        diff = result.pnl - (result.final_bankroll - result.starting_bankroll)
        assert abs(diff) < 0.01

    def test_empty_games_raises(self):
        with pytest.raises(DataError, match="No games"):
            run_backtest([])

    def test_no_edge_all_pass(self):
        # With very high min_edge, everything should pass
        games = generate_games(n=20, edge=0.01, seed=42)
        config = BacktestConfig(min_edge=0.50)
        result = run_backtest(games, config)
        assert result.total_bets == 0
        assert result.final_bankroll == result.starting_bankroll

    def test_high_edge_places_bets(self):
        games = generate_games(n=100, edge=0.10, seed=42)
        config = BacktestConfig(min_edge=0.03)
        result = run_backtest(games, config)
        assert result.total_bets > 0

    def test_max_drawdown_non_negative(self):
        games = generate_games(n=100, seed=42)
        result = run_backtest(games)
        assert result.max_drawdown >= 0

    def test_brier_score_bounded(self):
        games = generate_games(n=50, seed=42)
        result = run_backtest(games)
        assert 0 <= result.brier_score <= 1

    def test_deterministic(self):
        games = generate_games(n=50, seed=42)
        r1 = run_backtest(games)
        r2 = run_backtest(games)
        assert r1.final_bankroll == r2.final_bankroll
        assert r1.total_bets == r2.total_bets

    def test_conservative_vs_aggressive(self):
        games = generate_games(n=200, seed=42)
        conservative = BacktestConfig(kelly_fraction=0.1, label="conservative")
        aggressive = BacktestConfig(kelly_fraction=0.5, label="aggressive")
        r_con = run_backtest(games, conservative)
        r_agg = run_backtest(games, aggressive)
        # Aggressive should have larger absolute P&L (positive or negative)
        assert abs(r_agg.pnl) >= abs(r_con.pnl) * 0.5  # roughly

    def test_edge_distribution(self):
        games = generate_games(n=100, seed=42)
        config = BacktestConfig(min_edge=0.03)
        result = run_backtest(games, config)
        # All edges in distribution should be >= min_edge
        for e in result.edge_distribution:
            assert e >= config.min_edge
