import urllib.request
import xml.etree.ElementTree as ET
from datetime import date
import ssl
import certifi

ECB_HISTORICAL_URL = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist.xml"

# Keep downloaded rates in memory while Flask is running.
_HISTORICAL_RATES = None


def load_ecb_rates():

    global _HISTORICAL_RATES

    if _HISTORICAL_RATES is not None:
        return _HISTORICAL_RATES

    try:
        request = urllib.request.Request(
            ECB_HISTORICAL_URL,
            headers={"User-Agent": "ForexTradingJournal/1.0"},
        )

        ssl_context = ssl.create_default_context(cafile=certifi.where())

        with urllib.request.urlopen(
            request, timeout=20, context=ssl_context
        ) as response:
            xml_data = response.read()

        root = ET.fromstring(xml_data)

        historical_rates = {}

        for date_cube in root.iter():

            if "time" not in date_cube.attrib:
                continue

            rate_date = date_cube.attrib["time"]

            rates = {"EUR": 1.0}

            for currency_cube in date_cube:

                currency = currency_cube.attrib.get("currency")
                rate = currency_cube.attrib.get("rate")

                if currency and rate:
                    rates[currency] = float(rate)

            historical_rates[rate_date] = rates

        if not historical_rates:
            raise ValueError("No historical exchange rates were returned.")

        _HISTORICAL_RATES = historical_rates

        return _HISTORICAL_RATES

    except Exception as error:
        raise ValueError(
            "Unable to retrieve historical exchange rates from the ECB."
        ) from error


def get_historical_conversion_rate(quote_currency, trade_date):

    quote_currency = quote_currency.strip().upper()

    if isinstance(trade_date, str):
        trade_date = date.fromisoformat(trade_date)

    if not isinstance(trade_date, date):
        raise ValueError("Invalid trade date.")

    if quote_currency == "USD":
        return 1.0

    historical_rates = load_ecb_rates()

    available_dates = sorted(
        rate_date
        for rate_date in historical_rates
        if date.fromisoformat(rate_date) <= trade_date
    )

    if not available_dates:
        raise ValueError("No ECB exchange rates are available for this trade date.")

    selected_date = available_dates[-1]
    rates = historical_rates[selected_date]

    if quote_currency not in rates or "USD" not in rates:
        raise ValueError(f"ECB exchange rates are unavailable for {quote_currency}.")

    # Convert quote currency to USD using EUR as the common base.
    conversion_rate = rates["USD"] / rates[quote_currency]

    return round(conversion_rate, 8)
