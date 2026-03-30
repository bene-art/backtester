"""Tests for result formatting."""

from backtester import BacktestResult, generate_games, run_backtest
from backtester.results import format_comparison, format_summary


class TestFormatSummary:
    def test_contains_key_metrics(self):
        games = generate_games(n=50, seed=42)
        result = run_backtest(games)
        text = format_summary(result)
        assert "P&L" in text
        assert "ROI" in text
        assert "Win rate" in text
        assert "Brier" in text
        assert "drawdown" in text

    def test_uses_label(self):
        result = BacktestResult(
            label="My Test",
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
            bankroll_curve=[],
            edge_distribution=[0.05],
            records=[],
        )
        text = format_summary(result)
        assert "My Test" in text

    def test_avg_edge_shown(self):
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
            bankroll_curve=[],
            edge_distribution=[0.05, 0.10],
            records=[],
        )
        text = format_summary(result)
        assert "Avg edge" in text


class TestFormatComparison:
    def test_header_present(self):
        games = generate_games(n=30, seed=42)
        results = [run_backtest(games)]
        text = format_comparison(results)
        assert "Label" in text
        assert "ROI" in text

    def test_multiple_rows(self):
        games = generate_games(n=30, seed=42)
        from backtester import BacktestConfig, compare

        configs = [
            BacktestConfig(label="a"),
            BacktestConfig(label="b"),
        ]
        results = compare(games, configs)
        text = format_comparison(results)
        assert "a" in text
        assert "b" in text

    def test_empty_results(self):
        text = format_comparison([])
        assert "No results" in text
