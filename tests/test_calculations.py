import pytest

from calculations import (
    get_contract_size,
    validate_trade,
    calculate_rrr,
    check_trade_result,
    calculate_profit_loss,
)

# --------------------------------------------------
# TEST CONTRACT SIZE
# --------------------------------------------------


@pytest.mark.parametrize(
    "pair, expected",
    [
        ("EURUSD", 100000),
        ("GBPUSD", 100000),
        ("USDJPY", 100000),
        ("XAUUSD", 100),
        ("eurusd", 100000),
        ("INVALID", None),
        ("USDEURUSD", None),
    ],
)
def test_get_contract_size(pair, expected):
    assert get_contract_size(pair) == expected


# --------------------------------------------------
# TEST TRADE VALIDATION
# --------------------------------------------------


@pytest.mark.parametrize(
    "entry, stop_loss, take_profit, direction, expected",
    [
        (1.1000, 1.0950, 1.1100, "BUY", True),
        (1.1000, 1.1050, 1.0900, "SELL", True),
        (1.1000, 1.1100, 1.0900, "BUY", False),
        (1.1000, 1.0900, 1.1100, "SELL", False),
        (1.1000, 1.0950, 1.1100, "INVALID", False),
        (0, 1.0950, 1.1100, "BUY", False),
        ("invalid", 1.0950, 1.1100, "BUY", False),
        (float("inf"), 1.0950, 1.1100, "BUY", False),
    ],
)
def test_validate_trade(entry, stop_loss, take_profit, direction, expected):
    assert validate_trade(entry, stop_loss, take_profit, direction) is expected


# --------------------------------------------------
# TEST RISK-TO-REWARD
# --------------------------------------------------


@pytest.mark.parametrize(
    "entry, stop_loss, take_profit, direction, expected",
    [
        (1.1000, 1.0950, 1.1100, "BUY", 2.0),
        (1.1000, 1.1050, 1.0900, "SELL", 2.0),
        (1.1000, 1.0950, 1.1050, "BUY", 1.0),
        (1.1000, 1.1100, 1.0900, "BUY", None),
        (1.1000, 1.0950, 1.1100, "INVALID", None),
    ],
)
def test_calculate_rrr(entry, stop_loss, take_profit, direction, expected):
    assert calculate_rrr(entry, stop_loss, take_profit, direction) == expected


# --------------------------------------------------
# TEST TRADE RESULTS
# --------------------------------------------------


@pytest.mark.parametrize(
    "profit, expected",
    [
        (10, "WIN"),
        (-10, "LOSS"),
        (0, "BREAKEVEN"),
    ],
)
def test_check_trade_result(profit, expected):
    assert check_trade_result(profit) == expected


# --------------------------------------------------
# TEST PROFIT AND LOSS
# --------------------------------------------------


@pytest.mark.parametrize(
    "entry, exit, lot, contract, direction, conversion, expected",
    [
        (1.1000, 1.1050, 0.01, 100000, "BUY", 1, 5.0),
        (1.1000, 1.0950, 0.01, 100000, "BUY", 1, -5.0),
        (1.1000, 1.0950, 0.01, 100000, "SELL", 1, 5.0),
        (1.1000, 1.1050, 0.01, 100000, "SELL", 1, -5.0),
        (1.1000, 1.1050, 0.01, 100000, "BUY", 2, 10.0),
        (1.1000, 1.1000, 0.01, 100000, "BUY", 1, 0.0),
        (1.1000, 1.1050, 0.01, 100000, "INVALID", 1, None),
    ],
)
def test_calculate_profit_loss(
    entry, exit, lot, contract, direction, conversion, expected
):
    assert (
        calculate_profit_loss(entry, exit, lot, contract, direction, conversion)
        == expected
    )
