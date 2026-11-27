from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

import app as app_module
from models import db, User
from storage import add_trade, get_trade_by_id


@pytest.fixture
def logged_in_user(client):
    """Create a test user and log them in."""

    with client.application.app_context():
        user = User(
            name="Test User",
            email="testuser@example.com",
            is_verified=True,
        )
        user.set_password("password123")

        db.session.add(user)
        db.session.commit()

        user_id = user.id

    with client.session_transaction() as session:
        session["_user_id"] = str(user_id)
        session["_fresh"] = True

    return user_id


@pytest.fixture
def sample_trade():
    return {
        "Broker": "exness",
        "Account Type": "standard",
        "Broker Entity": "international",
        "Pair": "EURUSD",
        "Direction": "BUY",
        "Entry Price": 1.10000,
        "Exit Price": 1.10500,
        "Lot Size": 0.01,
        "Contract Size": 100000,
        "Price Decimals": 5,
        "Quote-to-USD Conversion Rate": 1,
        "Risk percentage": 1,
        "Results": "WIN",
        "Stop loss": 1.09500,
        "Take profit": 1.11000,
        "Profit/Loss": 5.00,
        "Risk-to-Reward": 2.0,
        "Trade Date": "2026-11-26",
        "Trade Time": "10:30",
    }


def test_logged_in_user_can_view_trades_page(client, logged_in_user):
    response = client.get("/trades")

    print("Status:", response.status_code)
    print("Redirect location:", response.location)

    assert response.status_code == 200


def test_logged_in_user_can_add_trade(client, logged_in_user, monkeypatch):
    import app as app_module
    from storage import load_trades

    # Avoid depending on an external historical conversion service.
    monkeypatch.setattr(
        app_module,
        "get_historical_conversion_rate",
        lambda currency, trade_date: 1,
    )

    trade_date = datetime.now(ZoneInfo("Africa/Nairobi")).date().isoformat()

    response = client.post(
        "/add-trade",
        data={
            "broker": "exness",
            "account_type": "standard",
            "broker_entity": "international",
            "pair": "EURUSD",
            "direction": "BUY",
            "entry_price": "1.10000",
            "exit_price": "1.10500",
            "lot_size": "0.01",
            "risk_percentage": "1",
            "stop_loss": "1.09500",
            "take_profit": "1.11000",
            "trade_date": trade_date,
            "trade_time": "10:30",
        },
    )

    assert response.status_code == 302

    trades = load_trades(logged_in_user)

    assert len(trades) == 1
    assert trades[0]["Pair"] == "EURUSD"
    assert trades[0]["Direction"] == "BUY"
    assert trades[0]["Results"] == "WIN"
    assert trades[0]["Profit/Loss"] == 5.0


def test_logged_in_user_can_view_trade_details(client, logged_in_user, sample_trade):
    from storage import add_trade

    trade_id = add_trade(sample_trade, logged_in_user)

    response = client.get(f"/trade-details/{trade_id}")

    assert response.status_code == 200
    assert b"EURUSD" in response.data


def test_logged_in_user_can_edit_trade(client, logged_in_user, sample_trade):
    from storage import add_trade, get_trade_by_id

    trade_id = add_trade(sample_trade, logged_in_user)

    response = client.get(f"/edit-trade/{trade_id}")

    assert response.status_code == 200


def test_logged_in_user_can_update_trade(
    client, logged_in_user, sample_trade, monkeypatch
):
    from storage import add_trade, get_trade_by_id
    import app as app_module

    trade_id = add_trade(sample_trade, logged_in_user)

    monkeypatch.setattr(
        app_module,
        "get_historical_conversion_rate",
        lambda currency, trade_date: 1,
    )

    trade_date = datetime.now(ZoneInfo("Africa/Nairobi")).date().isoformat()

    response = client.post(
        f"/edit-trade/{trade_id}",
        data={
            "broker": "exness",
            "account_type": "standard",
            "broker_entity": "international",
            "pair": "EURUSD",
            "direction": "BUY",
            "entry_price": "1.10000",
            "exit_price": "1.11000",
            "lot_size": "0.01",
            "risk_percentage": "1",
            "stop_loss": "1.09500",
            "take_profit": "1.12000",
            "trade_date": trade_date,
            "trade_time": "10:30",
        },
    )

    assert response.status_code == 302

    updated_trade = get_trade_by_id(trade_id, logged_in_user)

    assert updated_trade["Exit Price"] == 1.11000
    assert updated_trade["Profit/Loss"] == 10.0
    assert updated_trade["Results"] == "WIN"


def test_logged_in_user_can_delete_trade(client, logged_in_user, sample_trade):
    from storage import add_trade, get_trade_by_id

    trade_id = add_trade(sample_trade, logged_in_user)

    response = client.post(f"/delete-trade/{trade_id}")

    assert response.status_code == 302

    deleted_trade = get_trade_by_id(trade_id, logged_in_user)

    assert deleted_trade is None


def test_csv_export(client, logged_in_user, sample_trade):
    from storage import add_trade

    add_trade(sample_trade, logged_in_user)

    response = client.get("/export-trades")

    assert response.status_code == 200
    assert response.mimetype == "text/csv"
    assert "attachment" in response.headers["Content-Disposition"]
    assert "forex_trading_history.csv" in response.headers["Content-Disposition"]

    csv_content = response.data.decode("utf-8")

    assert "EURUSD" in csv_content
    assert "Profit/Loss" in csv_content


def test_pdf_report_export(client, logged_in_user, sample_trade):
    from storage import add_trade

    add_trade(sample_trade, logged_in_user)

    response = client.get(
        "/reports/download-pdf",
        query_string={
            "period": "yearly",
            "year": 2026,
        },
    )

    assert response.status_code == 200
    assert response.mimetype == "application/pdf"
    assert "attachment" in response.headers["Content-Disposition"]
    assert response.data.startswith(b"%PDF")
    assert len(response.data) > 0
