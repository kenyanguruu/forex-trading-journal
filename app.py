from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from instruments import search_instruments
from flask import Response
import csv
from ecb_rates import get_historical_conversion_rate
import io
from reports import (
    filter_trades_by_period,
    calculate_report_summary,
)
from brokers import BROKERS, get_broker_entities
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from storage import (
    add_trade as save_trade,
    load_trades,
    get_trade_by_id,
    update_trade as save_updated_trade,
    delete_trade as remove_trade,
    update_trade,
)
from calculations import (
    get_contract_size,
    validate_trade,
    calculate_rrr,
    check_trade_result,
    calculate_profit_loss,
)
from broker_specs import (
    get_account_types,
    get_broker_account_type,
    get_broker_instrument_spec,
    get_available_instruments_for_entity,
    is_instrument_available_for_entity,
)
from datetime import datetime, date
from zoneinfo import ZoneInfo

import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

if not app.config["SECRET_KEY"]:
    raise RuntimeError("SECRET_KEY is missing. Check your .env file.")


def get_verified_price_decimals(spec, pair):

    decimals = spec.get("price_decimals")

    # Fall back to the instrument catalogue if broker precision is empty.
    if decimals is None or str(decimals).strip() == "":

        catalogue_symbol = pair.upper()

        if catalogue_symbol.endswith("C"):
            catalogue_symbol = catalogue_symbol[:-1]

        instruments = search_instruments(catalogue_symbol)

        instrument = next(
            (
                item
                for item in instruments
                if item["symbol"].upper() == catalogue_symbol
            ),
            None,
        )

        if instrument is not None:
            decimals = instrument.get("price_decimals")

    if decimals is None or str(decimals).strip() == "":
        raise ValueError(f"Price precision is unavailable for {pair}.")

    try:
        decimals = int(decimals)
    except (ValueError, TypeError):
        raise ValueError(f"Invalid price precision for {pair}.")

    if not 0 <= decimals <= 12:
        raise ValueError(f"Invalid price precision for {pair}.")

    return decimals


# --------------------------------------------------
# HOME PAGE
# --------------------------------------------------


@app.route("/")
def home():

    return render_template("index.html")


# --------------------------------------------------
# INSTRUMENT SEARCH API
# --------------------------------------------------


@app.route("/api/instruments")
def instrument_search():

    query = request.args.get("q", "").strip()
    broker_id = request.args.get("broker_id", "").strip().lower()
    account_type_id = request.args.get("account_type_id", "").strip().lower()
    entity_id = request.args.get("entity_id", "").strip().lower()

    if not all([broker_id, account_type_id, entity_id]):
        return jsonify([])

    results = []

    # --------------------------------------------------
    # EXNESS STANDARD CENT
    # --------------------------------------------------

    if broker_id == "exness" and account_type_id == "standard_cent":

        base_query = query.upper()

        if base_query.endswith("C"):
            base_query = base_query[:-1]

        instruments = search_instruments(base_query)

        for instrument in instruments:

            base_symbol = instrument["symbol"]
            cent_symbol = base_symbol + "c"

            spec = get_broker_instrument_spec(
                broker_id,
                account_type_id,
                cent_symbol,
            )

            if (
                spec is None
                or not spec.get("verified")
                or spec.get("contract_size") is None
            ):
                continue

            if not is_instrument_available_for_entity(
                broker_id,
                account_type_id,
                cent_symbol,
                entity_id,
            ):
                continue

            cent_instrument = instrument.copy()

            cent_instrument["symbol"] = cent_symbol
            cent_instrument["name"] = instrument["name"] + " (Standard Cent)"

            results.append(
                {
                    **cent_instrument,
                    "contract_size": spec["contract_size"],
                    "minimum_lot_size": spec["minimum_lot_size"],
                    "maximum_lot_size_day": spec.get("maximum_lot_size_day"),
                    "maximum_lot_size_night": spec.get("maximum_lot_size_night"),
                    "price_decimals": get_verified_price_decimals(spec, symbol),
                    "calculation_type": spec["calculation_type"],
                }
            )

        return jsonify(results)

    # --------------------------------------------------
    # ALL OTHER BROKERS AND ACCOUNT TYPES
    # --------------------------------------------------

    instruments = search_instruments(query)

    for instrument in instruments:

        symbol = instrument["symbol"]

        if not is_instrument_available_for_entity(
            broker_id,
            account_type_id,
            symbol,
            entity_id,
        ):
            continue

        spec = get_broker_instrument_spec(
            broker_id,
            account_type_id,
            symbol,
        )

        if (
            spec is None
            or not spec.get("verified")
            or spec.get("contract_size") is None
        ):
            continue

        results.append(
            {
                **instrument,
                "contract_size": spec["contract_size"],
                "minimum_lot_size": spec["minimum_lot_size"],
                "maximum_lot_size_day": spec.get("maximum_lot_size_day"),
                "maximum_lot_size_night": spec.get("maximum_lot_size_night"),
                "price_decimals": get_verified_price_decimals(spec, symbol),
                "calculation_type": spec["calculation_type"],
            }
        )

    return jsonify(results)


@app.route("/api/account-types/<broker_id>")
def api_account_types(broker_id):

    accounts = get_account_types(broker_id)

    return jsonify(accounts)


@app.route("/api/broker-entities/<broker_id>")
def api_broker_entities(broker_id):

    entities = get_broker_entities(broker_id)

    return jsonify(entities)


# --------------------------------------------------
# ADD TRADE PAGE
# --------------------------------------------------


@app.route("/add-trade", methods=["GET", "POST"])
def add_trade():

    if request.method == "POST":
        try:
            broker_id = request.form.get("broker", "").strip().lower()
            account_type_id = request.form.get("account_type", "").strip().lower()
            entity_id = request.form.get("broker_entity", "").strip().lower()

            pair = request.form.get("pair", "").strip().upper()
            direction = request.form.get("direction", "").strip().upper()

            entry_price = float(request.form.get("entry_price", ""))
            exit_price = float(request.form.get("exit_price", ""))
            lot_size = float(request.form.get("lot_size", ""))
            risk_percentage = float(request.form.get("risk_percentage", ""))
            stop_loss = float(request.form.get("stop_loss", ""))
            take_profit = float(request.form.get("take_profit", ""))

            trade_date = request.form.get("trade_date", "")
            trade_time = request.form.get("trade_time", "")

            if not all([broker_id, account_type_id, entity_id, pair]):
                raise ValueError(
                    "Select your broker, account type, entity and instrument."
                )

            # VALIDATE THE ACCOUNT TYPE
            account = get_broker_account_type(broker_id, account_type_id)

            if account is None:
                raise ValueError(
                    "The selected account type does not belong to this broker."
                )

            # VALIDATE THE BROKER ENTITY
            valid_entities = get_broker_entities(broker_id)

            if not any(item["id"] == entity_id for item in valid_entities):
                raise ValueError(
                    "The selected broker entity does not belong to this broker."
                )

            # GET THE AUTHORITATIVE BROKER SPECIFICATION
            spec = get_broker_instrument_spec(broker_id, account_type_id, pair)

            if spec is None or not spec.get("verified"):
                raise ValueError(
                    "Verified specifications are unavailable for this instrument."
                )

            if not is_instrument_available_for_entity(
                broker_id, account_type_id, pair, entity_id
            ):
                raise ValueError(
                    "This instrument is not available for the selected broker entity."
                )

            contract_size = spec["contract_size"]
            minimum_lot_size = spec["minimum_lot_size"]
            price_decimals = get_verified_price_decimals(spec, pair)

            if lot_size < minimum_lot_size:
                raise ValueError(f"Minimum lot size for {pair} is {minimum_lot_size}.")

            if direction not in ("BUY", "SELL"):
                raise ValueError("Invalid trade direction.")

            if (
                min(
                    entry_price,
                    exit_price,
                    lot_size,
                    risk_percentage,
                    stop_loss,
                    take_profit,
                )
                <= 0
            ):
                raise ValueError("All numerical values must be greater than zero.")

            if not 0 < risk_percentage <= 100:
                raise ValueError("Risk percentage must be above 0 and at most 100.")

            if not trade_date or not trade_time:
                raise ValueError("Please provide the trade date and time.")

            datetime.strptime(trade_date, "%Y-%m-%d")
            datetime.strptime(trade_time, "%H:%M")
            conversion_rate = get_historical_conversion_rate(
                spec["quote_currency"],
                trade_date,
            )

            if not validate_trade(entry_price, stop_loss, take_profit, direction):
                raise ValueError(
                    "Stop loss and take profit are invalid for this direction."
                )

            # USD-QUOTED INSTRUMENTS USE CONVERSION RATE 1
            if spec["quote_currency"] == "USD" and conversion_rate != 1:
                raise ValueError(
                    "USD-quoted instruments must use a conversion rate of 1."
                )

            profit = calculate_profit_loss(
                entry_price,
                exit_price,
                lot_size,
                contract_size,
                direction,
                conversion_rate,
            )

            result = check_trade_result(profit)
            rrr = calculate_rrr(entry_price, stop_loss, take_profit, direction)

            trade = {
                "Broker": broker_id,
                "Account Type": account_type_id,
                "Broker Entity": entity_id,
                "Pair": pair,
                "Direction": direction,
                "Entry Price": entry_price,
                "Exit Price": exit_price,
                "Lot Size": lot_size,
                "Contract Size": contract_size,
                "Price Decimals": price_decimals,
                "Quote-to-USD Conversion Rate": conversion_rate,
                "Risk percentage": risk_percentage,
                "Results": result,
                "Stop loss": stop_loss,
                "Take profit": take_profit,
                "Profit/Loss": round(profit, 2),
                "Risk-to-Reward": rrr,
                "Trade Date": trade_date,
                "Trade Time": trade_time,
            }

            save_trade(trade)

            flash("Trade saved successfully!", "success")
            return redirect(url_for("add_trade"))

        except ValueError as error:
            flash(str(error), "error")

        except Exception:
            app.logger.exception("Failed to save trade.")
            flash("An unexpected error occurred while saving the trade.", "error")

    # Only display brokers that have registered account types.
    supported_brokers = [
        broker for broker in BROKERS if get_account_types(broker["id"])
    ]

    # Preserve the selected broker when the page reloads.
    selected_broker = (
        request.args.get("broker", request.form.get("broker", "exness")).strip().lower()
    )

    # Confirm that the selected broker is supported.
    if not any(broker["id"] == selected_broker for broker in supported_brokers):
        selected_broker = "exness"

    accounts = get_account_types(selected_broker)
    entities = get_broker_entities(selected_broker)

    return render_template(
        "add_trade.html",
        accounts=accounts,
        brokers=supported_brokers,
        selected_broker=selected_broker,
        entities=entities,
    )


@app.route("/trades")
def view_trades():
    all_trades = load_trades()

    # Read filter values
    start_date = request.args.get("start_date", "").strip()
    end_date = request.args.get("end_date", "").strip()
    selected_pair = request.args.get("pair", "").strip().upper()
    selected_direction = request.args.get("direction", "").strip().upper()
    selected_result = request.args.get("result", "").strip().upper()

    # Available currency pairs from saved trades
    available_pairs = sorted(
        {trade.get("Pair", "").upper() for trade in all_trades if trade.get("Pair")}
    )

    # Validate date filters
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else None

        end = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else None

        if start and end and start > end:
            raise ValueError("Start date cannot be after end date.")

    except ValueError:
        flash("Please enter valid dates and check the date range.", "error")
        start_date = ""
        end_date = ""
        start = None
        end = None

    # Validate dropdown selections
    if selected_direction not in ("", "BUY", "SELL"):
        selected_direction = ""

    if selected_result not in ("", "WIN", "LOSS", "BREAKEVEN"):
        selected_result = ""

    if selected_pair not in available_pairs:
        selected_pair = ""

    # Apply all selected filters
    filtered_trades = []

    for trade in all_trades:

        # Date filter
        try:
            trade_date = datetime.strptime(
                trade.get("Trade Date", ""), "%Y-%m-%d"
            ).date()
        except (ValueError, TypeError):
            if start or end:
                continue
            trade_date = None

        if start and (trade_date is None or trade_date < start):
            continue

        if end and (trade_date is None or trade_date > end):
            continue

        # Currency pair filter
        if selected_pair and trade.get("Pair", "").upper() != selected_pair:
            continue

        # Direction filter
        if (
            selected_direction
            and trade.get("Direction", "").upper() != selected_direction
        ):
            continue

        # Result filter
        if selected_result and trade.get("Results", "").upper() != selected_result:
            continue

        filtered_trades.append(trade)

    return render_template(
        "trades.html",
        trades=filtered_trades,
        total_trades=len(all_trades),
        start_date=start_date,
        end_date=end_date,
        available_pairs=available_pairs,
        selected_pair=selected_pair,
        selected_direction=selected_direction,
        selected_result=selected_result,
    )


@app.route("/reports")
def trading_reports():
    today = date.today()
    current_iso = today.isocalendar()

    period = request.args.get("period", "weekly").lower()

    if period not in ("weekly", "monthly", "yearly"):
        period = "weekly"

    # Use the ISO week-year for weekly reports.
    default_year = current_iso.year if period == "weekly" else today.year

    try:
        year = int(request.args.get("year", default_year))
        month = int(request.args.get("month", today.month))
        week = int(request.args.get("week", current_iso.week))

        if not 2000 <= year <= 2100:
            raise ValueError

        if not 1 <= month <= 12:
            raise ValueError

        if not 1 <= week <= 53:
            raise ValueError

        if period == "weekly":
            date.fromisocalendar(year, week, 1)

    except (ValueError, TypeError):
        flash("Invalid report period selected.", "error")
        return redirect(url_for("trading_reports"))

    all_trades = load_trades()

    # Build a list of years from existing trades, plus recent years.
    available_years = {today.year, current_iso.year}

    for trade in all_trades:
        try:
            trade_date = date.fromisoformat(trade["Trade Date"])
            available_years.add(trade_date.year)
            available_years.add(trade_date.isocalendar().year)
        except (ValueError, TypeError, KeyError):
            continue

    years = sorted(available_years, reverse=True)

    # Build valid ISO weeks for the selected week-year.
    weeks = []

    for week_number in range(1, 54):
        try:
            monday = date.fromisocalendar(year, week_number, 1)
            sunday = date.fromisocalendar(year, week_number, 7)

            weeks.append(
                {
                    "number": week_number,
                    "label": (
                        f"Week {week_number} "
                        f"({monday.strftime('%d %b')} – "
                        f"{sunday.strftime('%d %b')})"
                    ),
                }
            )

        except ValueError:
            continue

    # Filter trades for the selected reporting period.
    report_trades = filter_trades_by_period(
        all_trades,
        period,
        year=year,
        month=month,
        week=week,
    )

    summary = calculate_report_summary(report_trades)

    # Convert Profit/Loss safely into a number.
    def get_trade_profit(trade):
        try:
            return float(trade.get("Profit/Loss") or 0)
        except (ValueError, TypeError):
            return 0.0

    # Sort trades chronologically for the cumulative P/L chart.
    chart_trades = sorted(report_trades, key=lambda trade: trade.get("Trade Date", ""))

    # CHART 1: Cumulative Profit/Loss.
    equity_labels = []
    equity_values = []
    cumulative_profit = 0

    for trade in chart_trades:
        cumulative_profit += get_trade_profit(trade)

        equity_labels.append(trade.get("Trade Date", ""))
        equity_values.append(round(cumulative_profit, 2))

    # CHART 2: Winning, losing and breakeven trades.
    result_labels = ["Wins", "Losses", "Breakeven"]

    result_values = [
        summary["wins"],
        summary["losses"],
        summary["breakeven"],
    ]

    # CHART 3: BUY versus SELL performance.
    direction_totals = {
        "BUY": 0,
        "SELL": 0,
    }

    for trade in report_trades:
        direction = trade.get("Direction", "").strip().upper()

        if direction in direction_totals:
            direction_totals[direction] += get_trade_profit(trade)

    direction_labels = ["BUY", "SELL"]

    direction_values = [
        round(direction_totals["BUY"], 2),
        round(direction_totals["SELL"], 2),
    ]

    # CHART 4: Net Profit/Loss by trading pair.
    pair_totals = {}

    for trade in report_trades:
        pair = trade.get("Pair", "Unknown")
        pair_totals[pair] = pair_totals.get(pair, 0) + get_trade_profit(trade)

    pair_labels = list(pair_totals.keys())

    pair_values = [round(pair_totals[pair], 2) for pair in pair_labels]

    return render_template(
        "reports.html",
        period=period,
        year=year,
        month=month,
        week=week,
        years=years,
        weeks=weeks,
        summary=summary,
        trades=report_trades,
        # Chart data.
        equity_labels=equity_labels,
        equity_values=equity_values,
        result_labels=result_labels,
        result_values=result_values,
        direction_labels=direction_labels,
        direction_values=direction_values,
        pair_labels=pair_labels,
        pair_values=pair_values,
    )


@app.route("/reports/download-pdf")
def download_report_pdf():
    period = request.args.get("period", "weekly").lower()

    if period not in ("weekly", "monthly", "yearly"):
        period = "weekly"

    today = date.today()
    current_iso = today.isocalendar()

    default_year = current_iso.year if period == "weekly" else today.year

    try:
        year = int(request.args.get("year", default_year))
        month = int(request.args.get("month", today.month))
        week = int(request.args.get("week", current_iso.week))

        if not 2000 <= year <= 2100:
            raise ValueError

        if not 1 <= month <= 12:
            raise ValueError

        if not 1 <= week <= 53:
            raise ValueError

        if period == "weekly":
            date.fromisocalendar(year, week, 1)

    except (ValueError, TypeError):
        flash("Invalid report period selected.", "error")
        return redirect(url_for("trading_reports"))

    all_trades = load_trades()

    report_trades = filter_trades_by_period(
        all_trades,
        period,
        year=year,
        month=month,
        week=week,
    )

    summary = calculate_report_summary(report_trades)

    # Create the PDF in memory.
    pdf_buffer = io.BytesIO()

    document = SimpleDocTemplate(
        pdf_buffer,
        pagesize=A4,
        rightMargin=25,
        leftMargin=25,
        topMargin=30,
        bottomMargin=30,
    )

    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("Forex Trading Journal", styles["Title"]))

    elements.append(Paragraph("Trading Performance Report", styles["Heading2"]))

    elements.append(Spacer(1, 12))

    if period == "weekly":
        monday = date.fromisocalendar(year, week, 1)
        sunday = date.fromisocalendar(year, week, 7)
        period_label = (
            f"Week {week}, {year}: "
            f"{monday.strftime('%d %b %Y')} - "
            f"{sunday.strftime('%d %b %Y')}"
        )

    elif period == "monthly":
        month_name = date(year, month, 1).strftime("%B")
        period_label = f"{month_name} {year}"

    else:
        period_label = str(year)

    elements.append(Paragraph(f"Report Period: {period_label}", styles["Normal"]))

    elements.append(
        Paragraph(
            f"Generated: {today.strftime('%d %B %Y')}",
            styles["Normal"],
        )
    )

    elements.append(Spacer(1, 20))

    elements.append(Paragraph("Performance Summary", styles["Heading2"]))

    summary_data = [
        ["Metric", "Value"],
        ["Total Trades", str(summary["total_trades"])],
        ["Wins", str(summary["wins"])],
        ["Losses", str(summary["losses"])],
        ["Breakeven", str(summary["breakeven"])],
        ["Win Rate", f'{summary["win_rate"]}%'],
        ["Gross Profit", f'${summary["total_profit"]:,.2f}'],
        ["Gross Losses", f'${summary["total_losses"]:,.2f}'],
        ["Net Profit", f'${summary["net_profit"]:,.2f}'],
        ["Average Risk-to-Reward", f'{summary["average_rrr"]}R'],
        ["BUY Trades", str(summary["buy_trades"])],
        ["SELL Trades", str(summary["sell_trades"])],
        ["Best Pair", summary["best_pair"]],
        ["Worst Pair", summary["worst_pair"]],
    ]

    summary_table = Table(
        summary_data,
        colWidths=[220, 180],
    )

    summary_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#243b53")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("PADDING", (0, 0), (-1, -1), 7),
                ("ALIGN", (1, 1), (1, -1), "RIGHT"),
            ]
        )
    )

    elements.append(summary_table)
    elements.append(Spacer(1, 20))

    elements.append(Paragraph("Trade History", styles["Heading2"]))

    trade_data = [
        [
            "Date",
            "Pair",
            "Direction",
            "Entry",
            "Exit",
            "Result",
            "Profit/Loss",
            "R:R",
        ]
    ]

    for trade in report_trades:
        trade_data.append(
            [
                trade.get("Trade Date", ""),
                trade.get("Pair", ""),
                trade.get("Direction", ""),
                trade.get("Entry Price", ""),
                trade.get("Exit Price", ""),
                trade.get("Results", ""),
                f'${float(trade.get("Profit/Loss") or 0):,.2f}',
                f'{trade.get("Risk-to-Reward", "")}R',
            ]
        )

    trade_table = Table(
        trade_data,
        repeatRows=1,
        colWidths=[62, 55, 42, 68, 68, 48, 85, 45],
    )

    trade_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#243b53")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("PADDING", (0, 0), (-1, -1), 4),
                ("FONTSIZE", (0, 0), (-1, -1), 7),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )

    elements.append(trade_table)

    document.build(elements)

    pdf_buffer.seek(0)

    filename = f"trading_report_{period}_{year}.pdf"

    return Response(
        pdf_buffer.getvalue(),
        mimetype="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@app.route("/export-trades")
def export_trades():
    trades = load_trades()

    output = io.StringIO()

    if trades:
        fieldnames = trades[0].keys()
    else:
        fieldnames = []

    writer = csv.DictWriter(output, fieldnames=fieldnames)

    if fieldnames:
        writer.writeheader()
        writer.writerows(trades)

    response = Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=forex_trading_history.csv"
        },
    )

    return response


@app.route("/trade-details/<trade_id>")
def trade_details(trade_id):
    trade = get_trade_by_id(trade_id)

    if trade is None:
        flash("Trade not found.", "error")
        return redirect(url_for("view_trades"))

    return render_template("trade_details.html", trade=trade)


@app.route("/edit-trade/<trade_id>", methods=["GET", "POST"])
def edit_trade(trade_id):

    trade = get_trade_by_id(trade_id)

    if trade is None:
        flash("Trade not found.", "error")
        return redirect(url_for("view_trades"))

    # --------------------------------------------------
    # UPDATE TRADE
    # --------------------------------------------------

    if request.method == "POST":

        try:

            broker_id = request.form.get("broker", "").strip().lower()

            account_type_id = request.form.get("account_type", "").strip().lower()

            entity_id = request.form.get("broker_entity", "").strip().lower()

            pair = request.form.get("pair", "").strip().upper()

            direction = request.form.get("direction", "").strip().upper()

            entry_price = float(request.form.get("entry_price", ""))
            exit_price = float(request.form.get("exit_price", ""))
            lot_size = float(request.form.get("lot_size", ""))
            risk_percentage = float(request.form.get("risk_percentage", ""))
            stop_loss = float(request.form.get("stop_loss", ""))
            take_profit = float(request.form.get("take_profit", ""))

            trade_date = request.form.get("trade_date", "").strip()
            trade_time = request.form.get("trade_time", "").strip()

            # --------------------------------------------------
            # VALIDATE BROKER, ACCOUNT AND ENTITY
            # --------------------------------------------------

            if not all([broker_id, account_type_id, entity_id, pair]):

                raise ValueError(
                    "Select your broker, account type, entity and instrument."
                )

            account = get_broker_account_type(broker_id, account_type_id)

            if account is None:

                raise ValueError(
                    "The selected account type does not belong to this broker."
                )

            valid_entities = get_broker_entities(broker_id)

            if not any(item["id"] == entity_id for item in valid_entities):

                raise ValueError(
                    "The selected broker entity does not belong to this broker."
                )

            # --------------------------------------------------
            # VALIDATE INSTRUMENT SPECIFICATIONS
            # --------------------------------------------------

            spec = get_broker_instrument_spec(broker_id, account_type_id, pair)

            if spec is None or not spec.get("verified"):

                raise ValueError(
                    "Verified specifications are unavailable for this instrument."
                )

            if not is_instrument_available_for_entity(
                broker_id, account_type_id, pair, entity_id
            ):

                raise ValueError(
                    "This instrument is unavailable for the selected broker entity."
                )

            contract_size = spec["contract_size"]
            minimum_lot_size = spec["minimum_lot_size"]
            price_decimals = get_verified_price_decimals(spec, pair)

            if lot_size < minimum_lot_size:

                raise ValueError(f"Minimum lot size for {pair} is {minimum_lot_size}.")

            # --------------------------------------------------
            # VALIDATE NUMERICAL VALUES
            # --------------------------------------------------

            if direction not in ("BUY", "SELL"):

                raise ValueError("Invalid trade direction.")

            numerical_values = [
                entry_price,
                exit_price,
                lot_size,
                risk_percentage,
                stop_loss,
                take_profit,
            ]

            if any(value <= 0 for value in numerical_values):

                raise ValueError("All numerical values must be greater than zero.")

            if not 0 < risk_percentage <= 100:

                raise ValueError("Risk percentage must be above 0 and at most 100.")

            # --------------------------------------------------
            # VALIDATE DATE AND TIME
            # --------------------------------------------------

            if not trade_date or not trade_time:

                raise ValueError("Please provide the trade date and time.")

            datetime.strptime(trade_date, "%Y-%m-%d")
            datetime.strptime(trade_time, "%H:%M")
            conversion_rate = get_historical_conversion_rate(
                spec["quote_currency"],
                trade_date,
            )

            # --------------------------------------------------
            # VALIDATE STOP LOSS AND TAKE PROFIT
            # --------------------------------------------------

            if not validate_trade(entry_price, stop_loss, take_profit, direction):

                raise ValueError(
                    "Stop loss and take profit are invalid for this direction."
                )

            # --------------------------------------------------
            # VALIDATE CONVERSION RATE
            # --------------------------------------------------

            if spec["quote_currency"] == "USD" and conversion_rate != 1:

                raise ValueError(
                    "USD-quoted instruments must use a conversion rate of 1."
                )

            # --------------------------------------------------
            # CALCULATE PROFIT AND LOSS
            # --------------------------------------------------

            profit = calculate_profit_loss(
                entry_price,
                exit_price,
                lot_size,
                contract_size,
                direction,
                conversion_rate,
            )

            result = check_trade_result(profit)

            rrr = calculate_rrr(
                entry_price,
                stop_loss,
                take_profit,
                direction,
            )

            # --------------------------------------------------
            # PREPARE UPDATED TRADE
            # --------------------------------------------------

            updated_data = {
                "Broker": broker_id,
                "Account Type": account_type_id,
                "Broker Entity": entity_id,
                "Pair": pair,
                "Direction": direction,
                "Entry Price": entry_price,
                "Exit Price": exit_price,
                "Lot Size": lot_size,
                "Contract Size": contract_size,
                "Price Decimals": price_decimals,
                "Quote-to-USD Conversion Rate": conversion_rate,
                "Risk percentage": risk_percentage,
                "Results": result,
                "Stop loss": stop_loss,
                "Take profit": take_profit,
                "Profit/Loss": round(profit, 2),
                "Risk-to-Reward": rrr,
                "Trade Date": trade_date,
                "Trade Time": trade_time,
            }

            # --------------------------------------------------
            # SAVE UPDATED TRADE
            # --------------------------------------------------

            if update_trade(trade_id, updated_data):

                flash("Trade updated successfully!", "success")

                return redirect(url_for("view_trades"))

            flash("Unable to update this trade.", "error")

        except ValueError as error:

            flash(str(error), "error")

        except Exception:

            app.logger.exception("Failed to update trade.")

            flash("An unexpected error occurred while updating the trade.", "error")

    # --------------------------------------------------
    # LOAD DATA FOR EDIT TRADE PAGE
    # --------------------------------------------------

    selected_broker = (
        (request.form.get("broker") or trade.get("Broker") or "exness").strip().lower()
    )

    supported_brokers = [
        broker_item for broker_item in BROKERS if get_account_types(broker_item["id"])
    ]

    accounts = get_account_types(selected_broker)

    entities = get_broker_entities(selected_broker)

    return render_template(
        "edit_trade.html",
        trade=trade,
        brokers=supported_brokers,
        accounts=accounts,
        entities=entities,
        selected_broker=selected_broker,
    )


@app.route("/delete-trade/<trade_id>", methods=["POST"])
def delete_trade_route(trade_id):
    if remove_trade(trade_id):
        flash("Trade deleted successfully.", "success")
    else:
        flash("Trade not found.", "error")

    return redirect(url_for("view_trades"))


@app.route("/dashboard")
def dashboard():
    trades = load_trades()

    def get_number(value):
        try:
            return float(value or 0)
        except (TypeError, ValueError):
            return 0.0

    total_trades = len(trades)

    wins = sum(1 for trade in trades if trade.get("Results", "").upper() == "WIN")

    losses = sum(1 for trade in trades if trade.get("Results", "").upper() == "LOSS")

    breakeven = sum(
        1 for trade in trades if trade.get("Results", "").upper() == "BREAKEVEN"
    )

    win_rate = (wins / total_trades) * 100 if total_trades else 0

    profits = [get_number(trade.get("Profit/Loss")) for trade in trades]

    gross_profit = sum(value for value in profits if value > 0)
    gross_loss = abs(sum(value for value in profits if value < 0))
    net_profit = sum(profits)

    average_profit = net_profit / total_trades if total_trades else 0

    buy_trades = sum(
        1 for trade in trades if trade.get("Direction", "").upper() == "BUY"
    )

    sell_trades = sum(
        1 for trade in trades if trade.get("Direction", "").upper() == "SELL"
    )

    rrr_values = [
        get_number(trade.get("Risk-to-Reward"))
        for trade in trades
        if trade.get("Risk-to-Reward") not in ("", None)
        and get_number(trade.get("Risk-to-Reward")) > 0
    ]

    average_rrr = sum(rrr_values) / len(rrr_values) if rrr_values else 0

    best_trade = max(profits, default=0)
    worst_trade = min(profits, default=0)

    # Performance breakdown by currency pair
    pair_stats = {}

    for trade in trades:
        pair = trade.get("Pair", "Unknown").upper()
        result = trade.get("Results", "").upper()
        profit = get_number(trade.get("Profit/Loss"))

        if pair not in pair_stats:
            pair_stats[pair] = {
                "pair": pair,
                "total": 0,
                "wins": 0,
                "losses": 0,
                "breakeven": 0,
                "net_profit": 0,
            }

        stats = pair_stats[pair]
        stats["total"] += 1
        stats["net_profit"] += profit

        if result == "WIN":
            stats["wins"] += 1
        elif result == "LOSS":
            stats["losses"] += 1
        elif result == "BREAKEVEN":
            stats["breakeven"] += 1

    pair_stats = list(pair_stats.values())

    for stats in pair_stats:
        stats["win_rate"] = (
            stats["wins"] / stats["total"] * 100 if stats["total"] else 0
        )

    # Sort pairs from highest to lowest net profit
    pair_stats.sort(key=lambda item: item["net_profit"], reverse=True)

    # Calculate bar widths for the visual comparison
    largest_result = max((abs(item["net_profit"]) for item in pair_stats), default=0)

    for stats in pair_stats:
        stats["bar_width"] = (
            abs(stats["net_profit"]) / largest_result * 100 if largest_result else 0
        )

    # Monthly performance analysis
    monthly_data = {}

    for trade in trades:
        trade_date = trade.get("Trade Date", "")

        try:
            parsed_date = datetime.strptime(trade_date, "%Y-%m-%d")
        except (ValueError, TypeError):
            continue

        month_key = parsed_date.strftime("%Y-%m")
        month_name = parsed_date.strftime("%B %Y")

        if month_key not in monthly_data:
            monthly_data[month_key] = {
                "month": month_name,
                "total": 0,
                "wins": 0,
                "losses": 0,
                "net_profit": 0,
            }

        stats = monthly_data[month_key]
        stats["total"] += 1
        stats["net_profit"] += get_number(trade.get("Profit/Loss"))

        result = trade.get("Results", "").upper()

        if result == "WIN":
            stats["wins"] += 1
        elif result == "LOSS":
            stats["losses"] += 1

    monthly_stats = [monthly_data[key] for key in sorted(monthly_data)]

    for stats in monthly_stats:
        stats["win_rate"] = (
            stats["wins"] / stats["total"] * 100 if stats["total"] else 0
        )

    largest_monthly_result = max(
        (abs(item["net_profit"]) for item in monthly_stats), default=0
    )

    for stats in monthly_stats:
        stats["bar_width"] = (
            abs(stats["net_profit"]) / largest_monthly_result * 100
            if largest_monthly_result
            else 0
        )

    # Prepare trades for the equity curve
    dated_trades = []

    for trade in trades:
        try:
            trade_datetime = datetime.fromisoformat(
                f"{trade['Trade Date']}T{trade['Trade Time']}"
            )
        except (ValueError, TypeError, KeyError):
            try:
                trade_datetime = datetime.strptime(trade["Trade Date"], "%Y-%m-%d")
            except (ValueError, TypeError, KeyError):
                continue

        dated_trades.append((trade_datetime, trade))

    # Sort chronologically
    dated_trades.sort(key=lambda item: item[0])

    equity_labels = []
    equity_values = []
    running_profit = 0

    for trade_datetime, trade in dated_trades:
        running_profit += get_number(trade.get("Profit/Loss"))

        equity_labels.append(trade_datetime.strftime("%d %b %Y %H:%M"))
        equity_values.append(round(running_profit, 2))

    # Win/loss distribution
    result_labels = ["Wins", "Losses", "Breakeven"]
    result_values = [wins, losses, breakeven]

    # Monthly chart data
    monthly_labels = [item["month"] for item in monthly_stats]

    monthly_values = [round(item["net_profit"], 2) for item in monthly_stats]

    return render_template(
        "dashboard.html",
        total_trades=total_trades,
        wins=wins,
        losses=losses,
        breakeven=breakeven,
        win_rate=win_rate,
        gross_profit=gross_profit,
        gross_loss=gross_loss,
        net_profit=net_profit,
        average_profit=average_profit,
        buy_trades=buy_trades,
        sell_trades=sell_trades,
        average_rrr=average_rrr,
        best_trade=best_trade,
        worst_trade=worst_trade,
        pair_stats=pair_stats,
        monthly_stats=monthly_stats,
        equity_labels=equity_labels,
        equity_values=equity_values,
        result_labels=result_labels,
        result_values=result_values,
        monthly_labels=monthly_labels,
        monthly_values=monthly_values,
    )


# --------------------------------------------------
# RUN APPLICATION
# --------------------------------------------------

if __name__ == "__main__":

    app.run(debug=True)
