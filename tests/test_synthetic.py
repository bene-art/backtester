"""Tests for synthetic game generation."""

import pytest

from backtester import DataError, Game, generate_games


class TestGenerateGames:
    def test_returns_correct_count(self):
        games = generate_games(n=100)
        assert len(games) == 100

    def test_deterministic_with_seed(self):
        g1 = generate_games(n=50, seed=123)
        g2 = generate_games(n=50, seed=123)
        assert [g.outcome for g in g1] == [g.outcome for g in g2]
        assert [g.home_odds for g in g1] == [g.home_odds for g in g2]

    def test_different_seeds_different_results(self):
        g1 = generate_games(n=50, seed=1)
        g2 = generate_games(n=50, seed=2)
        outcomes1 = [g.outcome for g in g1]
        outcomes2 = [g.outcome for g in g2]
        assert outcomes1 != outcomes2

    def test_game_fields_populated(self):
        games = generate_games(n=10)
        for g in games:
            assert isinstance(g, Game)
            assert g.sport == "NFL"
            assert g.game_id.startswith("game_")
            assert "vs" in g.event
            assert g.outcome in (0, 1)
            assert 0.01 <= g.model_prob_home <= 0.99
            assert g.timestamp != ""

    def test_custom_sport(self):
        games = generate_games(n=5, sport="NBA")
        assert all(g.sport == "NBA" for g in games)

    def test_odds_are_reasonable(self):
        games = generate_games(n=200)
        for g in games:
            # Both sides should have valid odds
            assert g.home_odds != 0
            assert g.away_odds != 0
            # At least some favorites and underdogs
        favorites = [g for g in games if g.home_odds < 0]
        underdogs = [g for g in games if g.home_odds > 0]
        assert len(favorites) > 0
        assert len(underdogs) > 0

    def test_n_zero_raises(self):
        with pytest.raises(DataError, match="n must be"):
            generate_games(n=0)

    def test_n_negative_raises(self):
        with pytest.raises(DataError, match="n must be"):
            generate_games(n=-5)

    def test_edge_out_of_range_raises(self):
        with pytest.raises(DataError, match="edge"):
            generate_games(edge=0.6)

    def test_no_seed_still_works(self):
        games = generate_games(n=10, seed=None)
        assert len(games) == 10

    def test_high_edge_model(self):
        games = generate_games(n=200, edge=0.15, seed=42)
        # With 15% edge, model probs should tend to be higher for winners
        correct = sum(
            1
            for g in games
            if (g.model_prob_home > 0.5 and g.outcome == 1)
            or (g.model_prob_home < 0.5 and g.outcome == 0)
        )
        assert correct / len(games) > 0.5
