"""Tests for core data types."""

import pytest

from backtester import BacktestResult, BetRecord, Game


class TestGame:
    def test_frozen(self):
        g = Game(
            game_id="g1",
            sport="NFL",
            event="A vs B",
            home_odds=-110,
            away_odds=-110,
            outcome=1,
            model_prob_home=0.55,
            timestamp="2026-01-01T13:00:00",
        )
        assert g.game_id == "g1"
        assert g.outcome == 1

    def test_immutable(self):
        g = Game("g1", "NFL", "A vs B", -110, -110, 1, 0.55, "2026-01-01T13:00:00")
        with pytest.raises(AttributeError):
            g.outcome = 0  # type: ignore[misc]


class TestBetRecord:
    def test_pass_record(self):
        r = BetRecord(
            game_id="g1",
            side="pass",
            odds=0,
            fair_prob=0.0,
            model_prob=0.0,
            edge=0.0,
            stake=0.0,
            won=None,
            pnl=0.0,
            bankroll_after=1000.0,
        )
        assert r.side == "pass"
        assert r.won is None

    def test_win_record(self):
        r = BetRecord(
            game_id="g1",
            side="home",
            odds=-110,
            fair_prob=0.50,
            model_prob=0.58,
            edge=0.08,
            stake=25.0,
            won=True,
            pnl=22.73,
            bankroll_after=1022.73,
        )
        assert r.won is True
        assert r.pnl > 0


class TestBacktestResult:
    def test_basic(self):
        result = BacktestResult(
            label="test",
            starting_bankroll=1000.0,
            final_bankroll=1050.0,
            total_games=10,
            total_bets=5,
            wins=3,
            losses=2,
            win_rate=0.6,
            pnl=50.0,
            roi=0.05,
            max_drawdown=0.02,
            brier_score=0.24,
            bankroll_curve=[1000.0] * 10,
            edge_distribution=[0.05] * 5,
            records=[],
        )
        assert result.pnl == 50.0
        assert result.total_bets == 5
