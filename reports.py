from datetime import datetime, date, timedelta


def filter_trades_by_period(trades, period, year=None, month=None, week=None):
    today = date.today()

    if year is None:
        year = today.year

    selected_trades = []

    for trade in trades:
        trade_date = datetime.strptime(trade["Trade Date"], "%Y-%m-%d").date()

        if period == "weekly":
            selected_week = week if week is not None else today.isocalendar().week
            if (
                trade_date.isocalendar().year == year
                and trade_date.isocalendar().week == selected_week
            ):
                selected_trades.append(trade)

        elif period == "monthly":
            selected_month = month if month is not None else today.month

            if trade_date.year == year and trade_date.month == selected_month:
                selected_trades.append(trade)

        elif period == "yearly":
            if trade_date.year == year:
                selected_trades.append(trade)

    return selected_trades


def calculate_report_summary(trades):
    total_trades = len(trades)

    wins = 0
    losses = 0
    breakeven = 0

    total_profit = 0
    total_losses = 0
    net_profit = 0

    winning_trades = []
    losing_trades = []

    total_rrr = 0
    rrr_count = 0

    buy_trades = 0
    sell_trades = 0

    pair_performance = {}

    for trade in trades:
        profit = float(trade.get("Profit/Loss") or 0)

        result = trade.get("Results", "").upper()

        if result == "WIN":
            wins += 1
            total_profit += profit
            winning_trades.append(trade)

        elif result == "LOSS":
            losses += 1
            total_losses += abs(profit)
            losing_trades.append(trade)

        else:
            breakeven += 1

        net_profit += profit

        if result in ("WIN", "LOSS"):
            try:
                total_rrr += float(trade.get("Risk-to-Reward") or 0)
                rrr_count += 1
            except ValueError:
                pass

        if trade.get("Direction", "").upper() == "BUY":
            buy_trades += 1

        elif trade.get("Direction", "").upper() == "SELL":
            sell_trades += 1

        pair = trade.get("Pair", "Unknown")

        pair_performance[pair] = pair_performance.get(pair, 0) + profit

    win_rate = (wins / total_trades) * 100 if total_trades else 0

    average_rrr = total_rrr / rrr_count if rrr_count else 0

    best_pair = (
        max(pair_performance, key=pair_performance.get) if pair_performance else "N/A"
    )

    worst_pair = (
        min(pair_performance, key=pair_performance.get) if pair_performance else "N/A"
    )

    largest_win = (
        max(winning_trades, key=lambda trade: float(trade.get("Profit/Loss") or 0))
        if winning_trades
        else None
    )

    largest_loss = (
        min(losing_trades, key=lambda trade: float(trade.get("Profit/Loss") or 0))
        if losing_trades
        else None
    )

    return {
        "total_trades": total_trades,
        "wins": wins,
        "losses": losses,
        "breakeven": breakeven,
        "win_rate": round(win_rate, 2),
        "total_profit": round(total_profit, 2),
        "total_losses": round(total_losses, 2),
        "net_profit": round(net_profit, 2),
        "average_rrr": round(average_rrr, 2),
        "buy_trades": buy_trades,
        "sell_trades": sell_trades,
        "best_pair": best_pair,
        "worst_pair": worst_pair,
        "largest_win": largest_win,
        "largest_loss": largest_loss,
    }
