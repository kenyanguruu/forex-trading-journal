import uuid

from models import db, Trade

# --------------------------------------------------
# TRADE STORAGE
# --------------------------------------------------


def load_trades(user_id):
    """Load only trades belonging to the specified user."""

    records = Trade.query.filter_by(user_id=user_id).all()

    trades = []

    for record in records:
        trade = record.trade_data.copy()
        trade["Trade ID"] = record.id
        trades.append(trade)

    return trades


def add_trade(trade, user_id):
    """Save a new trade belonging to a specific user."""

    trade_id = uuid.uuid4().hex

    trade_data = trade.copy()
    trade_data.pop("Trade ID", None)

    new_trade = Trade(
        id=trade_id,
        user_id=user_id,
        trade_data=trade_data,
    )

    try:
        db.session.add(new_trade)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    return trade_id


def get_trade_by_id(trade_id, user_id):
    """Find a trade only if it belongs to the specified user."""

    record = Trade.query.filter_by(
        id=trade_id,
        user_id=user_id,
    ).first()

    if record is None:
        return None

    trade = record.trade_data.copy()
    trade["Trade ID"] = record.id

    return trade


def update_trade(trade_id, updated_data, user_id):
    """Update a trade only if it belongs to the specified user."""

    record = Trade.query.filter_by(
        id=trade_id,
        user_id=user_id,
    ).first()

    if record is None:
        return False

    trade_data = record.trade_data.copy()

    for field, value in updated_data.items():
        if field != "Trade ID":
            trade_data[field] = value

    record.trade_data = trade_data

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    return True


def delete_trade(trade_id, user_id):
    """Delete a trade only if it belongs to the specified user."""

    record = Trade.query.filter_by(
        id=trade_id,
        user_id=user_id,
    ).first()

    if record is None:
        return False

    try:
        db.session.delete(record)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    return True
