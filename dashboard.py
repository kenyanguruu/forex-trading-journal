import csv
import os

print("==============================")
print("FOREX TRADING DASHBOARD")
print("==============================")

# INITIALIZE COUNTERS

wins = 0
losses = 0
breakeven = 0

total_buy_trades = 0
total_sell_trades = 0
total_recorded_trades = 0

gross_profit = 0
gross_losses = 0
total_gross_pl = 0

valid_profit_trades = 0

pair_stats = {}

# CHECK IF CSV EXISTS

if os.path.exists("trades.csv"):

    with open("trades.csv", "r", newline="") as file:

        reader = csv.DictReader(file)

        for row in reader:

            total_recorded_trades += 1

            result = row.get("Results", "").strip().upper()

            # COUNT RESULTS

            if result == "WIN":
                wins += 1

            elif result == "LOSS":
                losses += 1

            elif result == "BREAKEVEN":
                breakeven += 1

            # COUNT DIRECTIONS

            direction = row.get("Direction", "").strip().upper()

            if direction == "BUY":
                total_buy_trades += 1

            elif direction == "SELL":
                total_sell_trades += 1

            # PAIR STATISTICS

            pair = row.get("Pair", "").strip().upper()

            if not pair:
                pair = "UNKNOWN"

            if pair not in pair_stats:

                pair_stats[pair] = {
                    "trades": 0,
                    "completed": 0,
                    "wins": 0,
                    "losses": 0,
                    "breakeven": 0,
                    "profit": 0,
                    "money_trades": 0,
                }

            pair_stats[pair]["trades"] += 1

            if result == "WIN":
                pair_stats[pair]["wins"] += 1
                pair_stats[pair]["completed"] += 1

            elif result == "LOSS":
                pair_stats[pair]["losses"] += 1
                pair_stats[pair]["completed"] += 1

            elif result == "BREAKEVEN":
                pair_stats[pair]["breakeven"] += 1
                pair_stats[pair]["completed"] += 1

            # MONETARY PROFIT VALIDATION

            try:

                lot_size = float(row["Lot Size"])
                contract_size = float(row["Contract Size"])
                trade_profit = float(row["Profit/Loss"])

                if lot_size <= 0 or contract_size <= 0:
                    raise ValueError

                total_gross_pl += trade_profit

                pair_stats[pair]["profit"] += trade_profit
                pair_stats[pair]["money_trades"] += 1

                valid_profit_trades += 1

                if trade_profit > 0:
                    gross_profit += trade_profit

                elif trade_profit < 0:
                    gross_losses += abs(trade_profit)

            except (ValueError, TypeError, KeyError):
                print(
                    f"Warning: {pair} has an old or invalid "
                    "monetary record. Excluded from P/L totals."
                )

else:

    print("No trading records found.")


# OVERALL STATISTICS

total_trades = wins + losses + breakeven

if total_trades > 0:
    win_rate = (wins / total_trades) * 100
else:
    win_rate = 0

if valid_profit_trades > 0:
    average_gross_pl = total_gross_pl / valid_profit_trades
else:
    average_gross_pl = 0


# WIN RATE BY CURRENCY PAIR

print("\nWIN RATE BY CURRENCY PAIR")
print("------------------------------")

for pair, stats in pair_stats.items():

    if stats["completed"] > 0:
        pair_win_rate = (stats["wins"] / stats["completed"]) * 100
    else:
        pair_win_rate = 0

    print(f"Pair: {pair}")
    print(f"Total recorded trades: {stats['trades']}")
    print(f"Completed trades: {stats['completed']}")
    print(f"Wins: {stats['wins']}")
    print(f"Losses: {stats['losses']}")
    print(f"Breakeven: {stats['breakeven']}")
    print(f"Win rate: {pair_win_rate:.2f}%")
    print("------------------------------")


# MONETARY PERFORMANCE BY PAIR

print("\nMONETARY PERFORMANCE BY PAIR")
print("------------------------------")

for pair, stats in pair_stats.items():

    print(f"Pair: {pair}")
    print(f"Monetary trades: {stats['money_trades']}")
    print(f"Gross P/L: ${stats['profit']:.2f}")
    print("------------------------------")


# BEST PERFORMING PAIR BY GROSS P/L

money_pairs = {
    pair: stats for pair, stats in pair_stats.items() if stats["money_trades"] > 0
}

if money_pairs:

    best_pair = max(money_pairs, key=lambda pair: money_pairs[pair]["profit"])

    best_profit = money_pairs[best_pair]["profit"]

    print("\nBEST PERFORMING PAIR")
    print("------------------------------")
    print(f"Pair: {best_pair}")
    print(f"Gross P/L: ${best_profit:.2f}")

else:

    print("\nNo monetary trade records available.")


# BEST PAIR BY WIN RATE

valid_pairs = {
    pair: stats for pair, stats in pair_stats.items() if stats["completed"] > 0
}

if valid_pairs:

    best_win_rate = max(
        (stats["wins"] / stats["completed"]) * 100 for stats in valid_pairs.values()
    )

    print("\nBEST PAIR BY WIN RATE")
    print("------------------------------")

    for pair, stats in valid_pairs.items():

        pair_rate = (stats["wins"] / stats["completed"]) * 100

        if pair_rate == best_win_rate:

            print(f"Pair: {pair}")
            print(f"Win rate: {pair_rate:.2f}%")


# FINAL DASHBOARD

print("\nOVERALL TRADING PERFORMANCE")
print("==============================")

print(f"Total recorded trades: {total_recorded_trades}")
print(f"Completed trade results: {total_trades}")

print(f"Winning trades: {wins}")
print(f"Losing trades: {losses}")
print(f"Breakeven trades: {breakeven}")

print(f"Win rate: {win_rate:.2f}%")

print(f"Total BUY trades: {total_buy_trades}")
print(f"Total SELL trades: {total_sell_trades}")

print("\nMONETARY PERFORMANCE")
print("------------------------------")

print(f"Monetary trades: {valid_profit_trades}")
print(f"Gross profit: ${gross_profit:.2f}")
print(f"Gross losses: ${gross_losses:.2f}")
print(f"Gross P/L: ${total_gross_pl:.2f}")
print(f"Average gross P/L: ${average_gross_pl:.2f}")

print("==============================")
