"""Tests for compare functionality."""

from backtester import BacktestConfig, compare, generate_games


class TestCompare:
    def test_compare_returns_list(self):
        games = generate_games(n=50, seed=42)
        configs = [
            BacktestConfig(kelly_fraction=0.1, label="small"),
            BacktestConfig(kelly_fraction=0.5, label="big"),
        ]
        results = compare(games, configs)
        assert len(results) == 2

    def test_compare_same_games(self):
        games = generate_games(n=50, seed=42)
        configs = [
            BacktestConfig(label="a"),
            BacktestConfig(label="b"),
        ]
        results = compare(games, configs)
        # Same config should give same results
        assert results[0].total_bets == results[1].total_bets
        assert results[0].final_bankroll == results[1].final_bankroll

    def test_compare_labels_preserved(self):
        games = generate_games(n=20, seed=42)
        configs = [
            BacktestConfig(label="alpha"),
            BacktestConfig(label="beta"),
        ]
        results = compare(games, configs)
        assert results[0].label == "alpha"
        assert results[1].label == "beta"

    def test_compare_different_configs(self):
        games = generate_games(n=100, seed=42)
        configs = [
            BacktestConfig(min_edge=0.01, label="loose"),
            BacktestConfig(min_edge=0.10, label="tight"),
        ]
        results = compare(games, configs)
        # Tight filter should have fewer bets
        assert results[1].total_bets <= results[0].total_bets

    def test_compare_empty_configs(self):
        games = generate_games(n=20, seed=42)
        results = compare(games, [])
        assert results == []
