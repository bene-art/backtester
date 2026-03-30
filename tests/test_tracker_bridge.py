"""Tests for optional bet-tracker bridge."""

from backtester import BacktestConfig, generate_games, run_backtest
from backtester.tracker_bridge import replay_to_tracker


class TestTrackerBridge:
    def test_replay_creates_tracker(self):
        games = generate_games(n=50, seed=42)
        result = run_backtest(games)
        tracker = replay_to_tracker(result)

        # Should have the correct starting deposit
        bet_count = len([r for r in result.records if r.side != "pass"])
        bets = tracker.list_bets()  # type: ignore[union-attr]
        assert len(bets) == bet_count

    def test_replay_pnl_matches(self):
        games = generate_games(n=50, seed=42)
        result = run_backtest(games)
        tracker = replay_to_tracker(result)
        tracker_pnl = tracker.pnl()  # type: ignore[union-attr]
        # Should be approximately equal (small float rounding diffs ok)
        assert abs(tracker_pnl - result.pnl) < 1.0

    def test_replay_all_settled(self):
        games = generate_games(n=30, seed=42)
        result = run_backtest(games)
        tracker = replay_to_tracker(result)
        from bet_tracker import BetStatus

        open_bets = tracker.list_bets(status=BetStatus.OPEN)  # type: ignore[union-attr]
        assert len(open_bets) == 0

    def test_replay_with_no_bets(self):
        games = generate_games(n=10, seed=42)
        config = BacktestConfig(min_edge=0.99)  # nothing will qualify
        result = run_backtest(games, config)
        tracker = replay_to_tracker(result)
        bets = tracker.list_bets()  # type: ignore[union-attr]
        assert len(bets) == 0
