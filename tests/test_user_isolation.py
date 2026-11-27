import pytest

from models import db, User
from storage import (
    add_trade,
    load_trades,
    get_trade_by_id,
    update_trade,
    delete_trade,
)


@pytest.fixture
def two_users(client):
    """Create two separate users for isolation tests."""

    with client.application.app_context():
        user_a = User(
            name="User A",
            email="user_a@example.com",
            is_verified=True,
        )
        user_a.set_password("password123")

        user_b = User(
            name="User B",
            email="user_b@example.com",
            is_verified=True,
        )
        user_b.set_password("password123")

        db.session.add_all([user_a, user_b])
        db.session.commit()

        return user_a.id, user_b.id


@pytest.fixture
def sample_trade():
    return {
        "Pair": "EURUSD",
        "Direction": "BUY",
        "Entry Price": 1.1000,
        "Exit Price": 1.1050,
        "Profit/Loss": 50.0,
    }


def test_users_only_load_their_own_trades(client, two_users, sample_trade):
    user_a_id, user_b_id = two_users

    add_trade(sample_trade, user_a_id)
    add_trade(sample_trade, user_b_id)

    with client.application.app_context():
        trades_a = load_trades(user_a_id)
        trades_b = load_trades(user_b_id)

        assert len(trades_a) == 1
        assert len(trades_b) == 1


def test_user_cannot_view_another_users_trade(client, two_users, sample_trade):
    user_a_id, user_b_id = two_users

    trade_id = add_trade(sample_trade, user_a_id)

    with client.application.app_context():
        result = get_trade_by_id(trade_id, user_b_id)

        assert result is None


def test_user_cannot_update_another_users_trade(client, two_users, sample_trade):
    user_a_id, user_b_id = two_users

    trade_id = add_trade(sample_trade, user_a_id)

    with client.application.app_context():
        result = update_trade(
            trade_id,
            {"Pair": "GBPUSD"},
            user_b_id,
        )

        assert result is False

        original_trade = get_trade_by_id(trade_id, user_a_id)

        assert original_trade["Pair"] == "EURUSD"


def test_user_cannot_delete_another_users_trade(client, two_users, sample_trade):
    user_a_id, user_b_id = two_users

    trade_id = add_trade(sample_trade, user_a_id)

    with client.application.app_context():
        result = delete_trade(trade_id, user_b_id)

        assert result is False

        original_trade = get_trade_by_id(trade_id, user_a_id)

        assert original_trade is not None
