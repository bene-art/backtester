"""Tests for BacktestConfig."""

import pytest

from backtester import BacktestConfig, ConfigError


class TestConfig:
    def test_defaults(self):
        c = BacktestConfig()
        assert c.starting_bankroll == 1000.0
        assert c.kelly_fraction == 0.25
        assert c.min_edge == 0.03
        assert c.max_stake_pct == 0.05
        assert c.devig_method == "multiplicative"
        assert c.min_bet == 1.0
        assert c.label == ""

    def test_custom_values(self):
        c = BacktestConfig(
            starting_bankroll=5000.0,
            kelly_fraction=0.5,
            min_edge=0.05,
            max_stake_pct=0.10,
            devig_method="power",
            min_bet=5.0,
            label="aggressive",
        )
        assert c.starting_bankroll == 5000.0
        assert c.label == "aggressive"

    def test_frozen(self):
        c = BacktestConfig()
        with pytest.raises(AttributeError):
            c.kelly_fraction = 0.5  # type: ignore[misc]

    def test_negative_bankroll_raises(self):
        with pytest.raises(ConfigError, match="starting_bankroll"):
            BacktestConfig(starting_bankroll=-100)

    def test_zero_bankroll_raises(self):
        with pytest.raises(ConfigError, match="starting_bankroll"):
            BacktestConfig(starting_bankroll=0)

    def test_kelly_fraction_zero_raises(self):
        with pytest.raises(ConfigError, match="kelly_fraction"):
            BacktestConfig(kelly_fraction=0)

    def test_kelly_fraction_over_one_raises(self):
        with pytest.raises(ConfigError, match="kelly_fraction"):
            BacktestConfig(kelly_fraction=1.5)

    def test_negative_min_edge_raises(self):
        with pytest.raises(ConfigError, match="min_edge"):
            BacktestConfig(min_edge=-0.01)

    def test_max_stake_zero_raises(self):
        with pytest.raises(ConfigError, match="max_stake_pct"):
            BacktestConfig(max_stake_pct=0)

    def test_max_stake_over_one_raises(self):
        with pytest.raises(ConfigError, match="max_stake_pct"):
            BacktestConfig(max_stake_pct=1.5)

    def test_negative_min_bet_raises(self):
        with pytest.raises(ConfigError, match="min_bet"):
            BacktestConfig(min_bet=-1)
