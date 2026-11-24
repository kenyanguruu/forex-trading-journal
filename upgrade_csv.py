import csv
import os

old_file = "trades_backup.csv"
temp_file = "trades_temp.csv"
new_file = "trades.csv"

new_fields = [
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

if os.path.exists(old_file):

    with open(old_file, "r", newline="") as source:
        reader = csv.DictReader(source)
        old_trades = list(reader)

    with open(temp_file, "w", newline="") as target:

        writer = csv.DictWriter(target, fieldnames=new_fields)

        writer.writeheader()

        for trade in old_trades:
            trade.setdefault("Lot Size", "")
            trade.setdefault("Contract Size", "")
            writer.writerow(trade)

    os.replace(temp_file, new_file)

    print("CSV upgraded successfully!")
    print("Backup preserved:", old_file)

else:
    print("Backup file not found.")
