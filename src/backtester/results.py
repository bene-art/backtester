"""Result formatting and display utilities."""

from __future__ import annotations

from .types import BacktestResult


def format_summary(result: BacktestResult) -> str:
    """Format a BacktestResult as a human-readable summary string."""
    label = result.label or "Backtest"
    lines = [
        f"=== {label} ===",
        f"Games: {result.total_games}  |  Bets: {result.total_bets}  |  "
        f"Pass rate: {1 - result.total_bets / result.total_games:.0%}"
        if result.total_games > 0
        else "Games: 0  |  Bets: 0",
        f"Win rate: {result.win_rate:.1%} ({result.wins}W / {result.losses}L)",
        f"P&L: ${result.pnl:+,.2f}  |  ROI: {result.roi:.1%}",
        f"Bankroll: ${result.starting_bankroll:,.2f} -> ${result.final_bankroll:,.2f}",
        f"Max drawdown: {result.max_drawdown:.1%}",
        f"Brier score: {result.brier_score:.4f}",
    ]

    if result.edge_distribution:
        avg_edge = sum(result.edge_distribution) / len(result.edge_distribution)
        lines.append(f"Avg edge: {avg_edge:.1%}")

    return "\n".join(lines)


def format_comparison(results: list[BacktestResult]) -> str:
    """Format multiple results side-by-side for comparison."""
    if not results:
        return "No results to compare."

    header = (
        f"{'Label':<20} {'Bets':>5} {'Win%':>6} {'ROI':>7} "
        f"{'P&L':>10} {'MaxDD':>7} {'Brier':>7}"
    )
    sep = "-" * len(header)
    lines = [header, sep]

    for r in results:
        label = (r.label or "unnamed")[:20]
        lines.append(
            f"{label:<20} {r.total_bets:>5} {r.win_rate:>5.1%} "
            f"{r.roi:>6.1%} {r.pnl:>+10,.2f} "
            f"{r.max_drawdown:>6.1%} {r.brier_score:>7.4f}"
        )

    return "\n".join(lines)
