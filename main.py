import csv
import os
from datetime import datetime
from zoneinfo import ZoneInfo

print("==============================")
print("FOREX TRADING JOURNAL")
print("==============================")


# 1. USER INPUT FUNCTIONS


def get_text(prompt):
    return input(prompt).strip().upper()


def get_number(prompt):
    while True:
        try:
            value = float(input(prompt))

            if value <= 0:
                print("Please enter a number greater than zero.")
            else:
                return value

        except ValueError:
            print("Invalid input. Please enter a number.")


# 2. CONTRACT SIZE


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


# 3. CALCULATE PROFIT


def calculate_profit(pair, entry_price, exit_price, direction, lot_size, contract_size):

    if direction == "BUY":
        price_difference = exit_price - entry_price

    elif direction == "SELL":
        price_difference = entry_price - exit_price

    else:
        return "Invalid direction"

    # Direct USD calculation only
    if pair != "XAUUSD" and not pair.endswith("USD"):
        return "USD conversion required"

    profit = price_difference * lot_size * contract_size

    return round(profit, 2)


# 4. CHECK TRADE RESULT


def check_trade_result(profit):

    if profit > 0:
        return "WIN"

    elif profit < 0:
        return "LOSS"

    else:
        return "BREAKEVEN"


# 5. CALCULATE RRR


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

    return reward / risk


# 6. VALIDATE TRADE


def validate_trade(entry_price, stop_loss, take_profit, direction):

    if direction == "BUY":
        return stop_loss < entry_price and take_profit > entry_price

    elif direction == "SELL":
        return stop_loss > entry_price and take_profit < entry_price

    return False


# 7. COLLECT TRADE INFORMATION

print("\nENTER TRADE INFORMATION")
print("------------------------------")

pair = get_text("Enter currency pair: ")

direction = get_text("Enter direction (BUY/SELL): ")

while direction not in ["BUY", "SELL"]:
    print("Invalid direction. Enter BUY or SELL.")
    direction = get_text("Enter direction (BUY/SELL): ")

entry_price = get_number("Enter entry price: ")
exit_price = get_number("Enter exit price: ")

risk_percentage = get_number("Enter risk percentage: ")

stop_loss = get_number("Enter stop loss: ")
take_profit = get_number("Enter take profit: ")

lot_size = get_number("Enter lot size: ")

contract_size = get_contract_size(pair)


# 8. VALIDATE AND CALCULATE

trade_is_valid = contract_size is not None and validate_trade(
    entry_price, stop_loss, take_profit, direction
)

if contract_size is None:
    print("\nUnsupported currency pair or instrument.")

if not validate_trade(entry_price, stop_loss, take_profit, direction):
    print("\nInvalid trade levels.")

if trade_is_valid:

    rrr = calculate_rrr(entry_price, stop_loss, take_profit, direction)

    profit = calculate_profit(
        pair, entry_price, exit_price, direction, lot_size, contract_size
    )

    if isinstance(profit, (int, float)):

        result = check_trade_result(profit)

        print("\nTRADE CALCULATION")
        print("------------------------------")
        print(f"Contract size: {contract_size}")
        print(f"Risk-to-reward: 1:{rrr:.2f}")
        print(f"Gross P/L: ${profit:.2f}")
        print(f"Trade result: {result}")

    else:
        result = "USD CONVERSION REQUIRED"
        print(f"\nCannot calculate USD P/L: {profit}")

else:
    rrr = "Invalid trade levels"
    profit = "Invalid trade"
    result = "INVALID"


# 9. DATE AND TIME

trade_time = datetime.now(ZoneInfo("Africa/Nairobi"))

trade_date = trade_time.strftime("%d-%m-%Y")
trade_clock = trade_time.strftime("%H:%M:%S")


# 10. STORE TRADE IN DICTIONARY

trade = {
    "Pair": pair,
    "Direction": direction,
    "Entry Price": entry_price,
    "Exit Price": exit_price,
    "Risk percentage": risk_percentage,
    "Results": result,
    "Stop loss": stop_loss,
    "Take profit": take_profit,
    "Profit/Loss": profit,
    "Risk-to-Reward": rrr,
    "Lot Size": lot_size,
    "Contract Size": contract_size,
    "Trade Date": trade_date,
    "Trade Time": trade_clock,
}


# 11. CSV FIELDS

fields = [
    "Pair",
    "Direction",
    "Entry Price",
    "Exit Price",
    "Lot Size",
    "Contract Size",
    "Risk percentage",
    "Results",
    "Stop loss",
    "Take profit",
    "Profit/Loss",
    "Risk-to-Reward",
    "Trade Date",
    "Trade Time",
]


# 12. CHECK CSV FILE

file_exists = os.path.exists("trades.csv")

if file_exists:
    file_empty = os.path.getsize("trades.csv") == 0
else:
    file_empty = True


# 13. SAVE TRADE

if trade_is_valid and isinstance(profit, (int, float)):

    with open("trades.csv", "a", newline="") as file:

        writer = csv.DictWriter(file, fieldnames=fields)

        if file_empty:
            writer.writeheader()

        writer.writerow(trade)

    print("\nTrade saved to CSV successfully!")

    with open("trades.txt", "a") as file:

        for key, value in trade.items():
            file.write(f"{key}: {value}\n")

        file.write("==============================\n")

    print("Trade saved to text file successfully!")

else:
    print("\nTrade was NOT saved.")


# 14. READ SAVED TRADES

if os.path.exists("trades.csv"):

    with open("trades.csv", "r", newline="") as file:

        reader = csv.DictReader(file)

        print("\nSAVED TRADES")
        print("------------------------------")

        for row in reader:

            print(f"Pair: {row['Pair']}")
            print(f"Direction: {row['Direction']}")
            print(f"Result: {row['Results']}")
            print("------------------------------")

else:
    print("No saved trades available yet.")


# 15. DISPLAY CURRENT TRADE

print("\nCURRENT TRADE DETAILS")
print("------------------------------")

for key, value in trade.items():
    print(f"{key}: {value}")
