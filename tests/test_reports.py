import pytest

from reports import (
    filter_trades_by_period,
    calculate_report_summary,
)


@pytest.fixture
def sample_trades():
    return [
        {
            "Trade Date": "2026-11-02",
            "Pair": "EURUSD",
            "Direction": "BUY",
            "Results": "WIN",
            "Profit/Loss": 50,
            "Risk-to-Reward": 2.0,
        },
        {
            "Trade Date": "2026-11-10",
            "Pair": "GBPUSD",
            "Direction": "SELL",
            "Results": "LOSS",
            "Profit/Loss": -20,
            "Risk-to-Reward": 1.5,
        },
        {
            "Trade Date": "2026-11-15",
            "Pair": "EURUSD",
            "Direction": "BUY",
            "Results": "WIN",
            "Profit/Loss": 30,
            "Risk-to-Reward": 3.0,
        },
        {
            "Trade Date": "2026-12-05",
            "Pair": "XAUUSD",
            "Direction": "SELL",
            "Results": "BREAKEVEN",
            "Profit/Loss": 0,
            "Risk-to-Reward": 0,
        },
    ]


# --------------------------------------------------
# TEST REPORT PERIOD FILTERING
# --------------------------------------------------


def test_filter_monthly_trades(sample_trades):
    result = filter_trades_by_period(
        sample_trades,
        "monthly",
        year=2026,
        month=11,
    )

    assert len(result) == 3
    assert all(trade["Trade Date"].startswith("2026-11") for trade in result)


def test_filter_yearly_trades(sample_trades):
    result = filter_trades_by_period(
        sample_trades,
        "yearly",
        year=2026,
    )

    assert len(result) == 4


def test_filter_weekly_trades(sample_trades):
    result = filter_trades_by_period(
        sample_trades,
        "weekly",
        year=2026,
        week=46,
    )

    assert len(result) == 2
    assert all(trade["Trade Date"] in ["2026-11-10", "2026-11-15"] for trade in result)


def test_filter_returns_empty_for_no_matching_trades(sample_trades):
    result = filter_trades_by_period(
        sample_trades,
        "monthly",
        year=2025,
        month=1,
    )

    assert result == []


# --------------------------------------------------
# TEST REPORT SUMMARY
# --------------------------------------------------


def test_calculate_report_summary(sample_trades):
    summary = calculate_report_summary(sample_trades)

    assert summary["total_trades"] == 4
    assert summary["wins"] == 2
    assert summary["losses"] == 1
    assert summary["breakeven"] == 1

    assert summary["win_rate"] == 50.0

    assert summary["total_profit"] == 80.0
    assert summary["total_losses"] == 20.0
    assert summary["net_profit"] == 60.0

    assert summary["average_rrr"] == 2.17

    assert summary["buy_trades"] == 2
    assert summary["sell_trades"] == 2

    assert summary["best_pair"] == "EURUSD"
    assert summary["worst_pair"] == "GBPUSD"

    assert summary["largest_win"]["Profit/Loss"] == 50
    assert summary["largest_loss"]["Profit/Loss"] == -20


def test_calculate_report_summary_with_no_trades():
    summary = calculate_report_summary([])

    assert summary["total_trades"] == 0
    assert summary["wins"] == 0
    assert summary["losses"] == 0
    assert summary["win_rate"] == 0
    assert summary["net_profit"] == 0
    assert summary["average_rrr"] == 0
    assert summary["best_pair"] == "N/A"
    assert summary["worst_pair"] == "N/A"
    assert summary["largest_win"] is None
    assert summary["largest_loss"] is None
