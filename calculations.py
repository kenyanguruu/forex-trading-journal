# --------------------------------------------------
# CURRENCY PAIR AND CONTRACT SIZE
# --------------------------------------------------


def get_contract_size(pair):

    pair = pair.strip().upper()

    if pair == "XAUUSD":
        return 100

    currencies = ["USD", "EUR", "GBP", "JPY", "CHF", "CAD", "AUD", "NZD"]

    if len(pair) == 6:

        base_currency = pair[:3]
        quote_currency = pair[3:]

        if (
            base_currency in currencies
            and quote_currency in currencies
            and base_currency != quote_currency
        ):
            return 100000

    return None


# --------------------------------------------------
# VALIDATE TRADE LEVELS
# --------------------------------------------------


def validate_trade(entry_price, stop_loss, take_profit, direction):

    if direction == "BUY":

        return stop_loss < entry_price < take_profit

    elif direction == "SELL":

        return stop_loss > entry_price > take_profit

    return False


# --------------------------------------------------
# CALCULATE RISK-TO-REWARD
# --------------------------------------------------


def calculate_rrr(entry_price, stop_loss, take_profit, direction):

    if direction == "BUY":

        risk = entry_price - stop_loss
        reward = take_profit - entry_price

    elif direction == "SELL":

        risk = stop_loss - entry_price
        reward = entry_price - take_profit

    else:
        return None

    if risk <= 0 or reward <= 0:
        return None

    return round(reward / risk, 2)


# --------------------------------------------------
# DETERMINE TRADE RESULT
# --------------------------------------------------


def check_trade_result(profit):

    if profit > 0:
        return "WIN"

    elif profit < 0:
        return "LOSS"

    return "BREAKEVEN"


def calculate_profit_loss(
    entry_price, exit_price, lot_size, contract_size, direction, conversion_rate=1
):
    if direction == "BUY":
        price_difference = exit_price - entry_price
    elif direction == "SELL":
        price_difference = entry_price - exit_price
    else:
        return None

    profit_in_quote_currency = price_difference * lot_size * contract_size

    profit_in_usd = profit_in_quote_currency * conversion_rate

    return round(profit_in_usd, 2)
