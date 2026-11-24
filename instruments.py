# --------------------------------------------------
# TRADING INSTRUMENT CATALOGUE
# --------------------------------------------------

INSTRUMENTS = [
    # --------------------------------------------------
    # FOREX
    # --------------------------------------------------
    {
        "symbol": "EURUSD",
        "name": "Euro / US Dollar",
        "category": "FOREX",
        "base_currency": "EUR",
        "quote_currency": "USD",
        "contract_size": 100000,
        "price_decimals": 5,
        "calculation_type": "forex",
    },
    {
        "symbol": "GBPUSD",
        "name": "British Pound / US Dollar",
        "category": "FOREX",
        "base_currency": "GBP",
        "quote_currency": "USD",
        "contract_size": 100000,
        "price_decimals": 5,
        "calculation_type": "forex",
    },
    {
        "symbol": "USDJPY",
        "name": "US Dollar / Japanese Yen",
        "category": "FOREX",
        "base_currency": "USD",
        "quote_currency": "JPY",
        "contract_size": 100000,
        "price_decimals": 3,
        "calculation_type": "forex",
    },
    {
        "symbol": "USDCHF",
        "name": "US Dollar / Swiss Franc",
        "category": "FOREX",
        "base_currency": "USD",
        "quote_currency": "CHF",
        "contract_size": 100000,
        "price_decimals": 5,
        "calculation_type": "forex",
    },
    {
        "symbol": "USDCAD",
        "name": "US Dollar / Canadian Dollar",
        "category": "FOREX",
        "base_currency": "USD",
        "quote_currency": "CAD",
        "contract_size": 100000,
        "price_decimals": 5,
        "calculation_type": "forex",
    },
    {
        "symbol": "AUDUSD",
        "name": "Australian Dollar / US Dollar",
        "category": "FOREX",
        "base_currency": "AUD",
        "quote_currency": "USD",
        "contract_size": 100000,
        "price_decimals": 5,
        "calculation_type": "forex",
    },
    {
        "symbol": "NZDUSD",
        "name": "New Zealand Dollar / US Dollar",
        "category": "FOREX",
        "base_currency": "NZD",
        "quote_currency": "USD",
        "contract_size": 100000,
        "price_decimals": 5,
        "calculation_type": "forex",
    },
    # Forex crosses
    *[
        {
            "symbol": pair,
            "name": f"{pair[:3]} / {pair[3:]}",
            "category": "FOREX",
            "base_currency": pair[:3],
            "quote_currency": pair[3:],
            "contract_size": 100000,
            "price_decimals": 3 if pair.endswith("JPY") else 5,
            "calculation_type": "forex",
        }
        for pair in [
            "EURGBP",
            "EURJPY",
            "EURCHF",
            "EURCAD",
            "EURAUD",
            "EURNZD",
            "GBPJPY",
            "GBPCHF",
            "GBPCAD",
            "GBPAUD",
            "GBPNZD",
            "CHFJPY",
            "CADJPY",
            "AUDJPY",
            "NZDJPY",
            "AUDCAD",
            "AUDCHF",
            "AUDNZD",
            "CADCHF",
            "NZDCAD",
            "NZDCHF",
        ]
    ],
    # --------------------------------------------------
    # METALS
    # --------------------------------------------------
    {
        "symbol": "XAUUSD",
        "name": "Gold / US Dollar",
        "category": "METALS",
        "base_currency": "XAU",
        "quote_currency": "USD",
        "contract_size": None,
        "price_decimals": 2,
        "calculation_type": "metal",
    },
    {
        "symbol": "XAGUSD",
        "name": "Silver / US Dollar",
        "category": "METALS",
        "base_currency": "XAG",
        "quote_currency": "USD",
        "contract_size": None,
        "price_decimals": 3,
        "calculation_type": "metal",
    },
    # --------------------------------------------------
    # CRYPTOCURRENCIES
    # --------------------------------------------------
    *[
        {
            "symbol": symbol,
            "name": name,
            "category": "CRYPTO",
            "base_currency": base,
            "quote_currency": quote,
            "contract_size": None,
            "price_decimals": None,
            "calculation_type": "crypto",
        }
        for symbol, name, base, quote in [
            ("BTCUSD", "Bitcoin / US Dollar", "BTC", "USD"),
            ("ETHUSD", "Ethereum / US Dollar", "ETH", "USD"),
            ("LTCUSD", "Litecoin / US Dollar", "LTC", "USD"),
            ("BCHUSD", "Bitcoin Cash / US Dollar", "BCH", "USD"),
            ("XRPUSD", "XRP / US Dollar", "XRP", "USD"),
            ("ADAUSD", "Cardano / US Dollar", "ADA", "USD"),
            ("SOLUSD", "Solana / US Dollar", "SOL", "USD"),
            ("BNBUSD", "BNB / US Dollar", "BNB", "USD"),
            ("BTCEUR", "Bitcoin / Euro", "BTC", "EUR"),
            ("ETHEUR", "Ethereum / Euro", "ETH", "EUR"),
        ]
    ],
]


# --------------------------------------------------
# GET AN INSTRUMENT
# --------------------------------------------------


def get_instrument(symbol):

    symbol = symbol.strip().upper()

    for instrument in INSTRUMENTS:
        if instrument["symbol"] == symbol:
            return instrument.copy()

    return None


# --------------------------------------------------
# SEARCH INSTRUMENTS
# --------------------------------------------------


def search_instruments(query, limit=10):

    query = query.strip().upper()

    if not query:
        return []

    matches = []

    for instrument in INSTRUMENTS:

        symbol = instrument["symbol"]
        name = instrument["name"].upper()

        if query in symbol or query in name:

            matches.append(instrument.copy())

        if len(matches) >= limit:
            break

    return matches
