import csv
import os
import tempfile
import uuid

# --------------------------------------------------
# FILE CONFIGURATION
# --------------------------------------------------

DATA_FOLDER = "data"
CSV_FILE = os.path.join(DATA_FOLDER, "trades.csv")

FIELDNAMES = [
    "Trade ID",
    "Broker",
    "Account Type",
    "Broker Entity",
    "Pair",
    "Direction",
    "Entry Price",
    "Exit Price",
    "Lot Size",
    "Contract Size",
    "Price Decimals",
    "Quote-to-USD Conversion Rate",
    "Risk percentage",
    "Results",
    "Stop loss",
    "Take profit",
    "Profit/Loss",
    "Risk-to-Reward",
    "Trade Date",
    "Trade Time",
]


# --------------------------------------------------
# CREATE DATA FOLDER
# --------------------------------------------------


def ensure_data_folder():
    os.makedirs(DATA_FOLDER, exist_ok=True)


# --------------------------------------------------
# LOAD TRADES
# --------------------------------------------------


def load_trades():

    ensure_data_folder()

    if not os.path.exists(CSV_FILE):
        return []

    with open(CSV_FILE, "r", newline="", encoding="utf-8") as file:

        reader = csv.DictReader(file)

        if not reader.fieldnames:
            return []

        return list(reader)


# --------------------------------------------------
# SAVE ALL TRADES
# --------------------------------------------------


def save_trades(trades):

    ensure_data_folder()

    # Write to a temporary file first.
    # Replace the original only after writing succeeds.

    temp_path = None

    try:

        with tempfile.NamedTemporaryFile(
            mode="w", newline="", encoding="utf-8", dir=DATA_FOLDER, delete=False
        ) as file:

            temp_path = file.name

            writer = csv.DictWriter(
                file,
                fieldnames=FIELDNAMES,
                extrasaction="ignore",
            )

            writer.writeheader()

            for trade in trades:
                writer.writerow({field: trade.get(field, "") for field in FIELDNAMES})

        os.replace(temp_path, CSV_FILE)

    except Exception:

        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

        raise


# --------------------------------------------------
# ADD A TRADE
# --------------------------------------------------


def add_trade(trade):

    trades = load_trades()

    trade["Trade ID"] = uuid.uuid4().hex

    trades.append(trade)

    save_trades(trades)

    return trade["Trade ID"]


# --------------------------------------------------
# FIND A TRADE
# --------------------------------------------------


def get_trade_by_id(trade_id):

    trades = load_trades()

    for trade in trades:

        if trade.get("Trade ID") == trade_id:
            return trade

    return None


# --------------------------------------------------
# UPDATE A TRADE
# --------------------------------------------------


def update_trade(trade_id, updated_data):

    trades = load_trades()

    for trade in trades:

        if trade.get("Trade ID") == trade_id:

            for field in FIELDNAMES:

                if field != "Trade ID" and field in updated_data:
                    trade[field] = updated_data[field]

            save_trades(trades)

            return True

    return False


# --------------------------------------------------
# DELETE A TRADE
# --------------------------------------------------


def delete_trade(trade_id):

    trades = load_trades()

    updated_trades = [trade for trade in trades if trade.get("Trade ID") != trade_id]

    if len(updated_trades) == len(trades):
        return False

    save_trades(updated_trades)

    return True
