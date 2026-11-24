# --------------------------------------------------
# BROKER-SPECIFIC INSTRUMENT SPECIFICATIONS
# --------------------------------------------------

from copy import deepcopy
from instruments import get_instrument, INSTRUMENTS

# --------------------------------------------------
# EXNESS STANDARD CENT SUPPORTED INSTRUMENTS
# --------------------------------------------------

EXNESS_CENT_SUPPORTED_SYMBOLS = {
    # Forex
    "AUDCAD",
    "AUDCHF",
    "AUDJPY",
    "AUDNZD",
    "AUDUSD",
    "CADJPY",
    "CHFJPY",
    "EURAUD",
    "EURCAD",
    "EURCHF",
    "EURGBP",
    "EURJPY",
    "EURNZD",
    "EURUSD",
    "GBPAUD",
    "GBPCAD",
    "GBPCHF",
    "GBPJPY",
    "GBPNZD",
    "NZDJPY",
    "NZDUSD",
    "USDCAD",
    "USDCHF",
    "USDJPY",
    # Metals
    "XAUUSD",
    "XAGUSD",
}


# --------------------------------------------------
# BROKER ACCOUNT TYPES
# --------------------------------------------------

BROKER_ACCOUNT_TYPES = [
    # EXNESS ACCOUNTS
    {
        "broker_id": "exness",
        "account_type_id": "standard",
        "account_type_name": "Standard",
        "minimum_lot_size": 0.01,
        "maximum_lot_size": None,
        "lot_step": None,
        "supported_categories": [
            "FOREX",
            "METALS",
            "CRYPTO",
            "ENERGIES",
            "STOCKS",
            "INDICES",
        ],
        "specification_status": "partially_verified",
        "source": "https://www.exness.com/standard-accounts/",
    },
    {
        "broker_id": "exness",
        "account_type_id": "standard_cent",
        "account_type_name": "Standard Cent",
        "minimum_lot_size": 0.01,
        "maximum_lot_size": 200,
        "lot_step": None,
        "supported_categories": ["FOREX", "METALS"],
        "specification_status": "partially_verified",
        "source": (
            "https://get.exness.help/hc/en-us/articles/"
            "17537782786588-Standard-Cent-account"
        ),
    },
    {
        "broker_id": "exness",
        "account_type_id": "pro",
        "account_type_name": "Pro",
        "minimum_lot_size": 0.01,
        "maximum_lot_size": None,
        "lot_step": None,
        "supported_categories": [
            "FOREX",
            "METALS",
            "CRYPTO",
            "ENERGIES",
            "STOCKS",
            "INDICES",
        ],
        "specification_status": "partially_verified",
        "source": "https://www.exness.com/pro-accounts/",
    },
    {
        "broker_id": "exness",
        "account_type_id": "raw_spread",
        "account_type_name": "Raw Spread",
        "minimum_lot_size": 0.01,
        "maximum_lot_size": None,
        "lot_step": None,
        "supported_categories": [
            "FOREX",
            "METALS",
            "CRYPTO",
            "ENERGIES",
            "STOCKS",
            "INDICES",
        ],
        "specification_status": "partially_verified",
        "source": "https://www.exness.com/pro-accounts/",
    },
    {
        "broker_id": "exness",
        "account_type_id": "zero",
        "account_type_name": "Zero",
        "minimum_lot_size": 0.01,
        "maximum_lot_size": None,
        "lot_step": None,
        "supported_categories": [
            "FOREX",
            "METALS",
            "CRYPTO",
            "ENERGIES",
            "STOCKS",
            "INDICES",
        ],
        "specification_status": "partially_verified",
        "source": "https://www.exness.com/pro-accounts/",
    },
    # HFM ACCOUNTS
    {
        "broker_id": "hfm",
        "account_type_id": "premium",
        "account_type_name": "Premium",
        "minimum_lot_size": 0.01,
        "maximum_lot_size": None,
        "lot_step": 0.01,
        "supported_categories": ["FOREX", "METALS"],
        "specification_status": "partially_verified",
        "source": "https://www.hfm.com/int/en/trading-accounts",
    },
    {
        "broker_id": "hfm",
        "account_type_id": "zero",
        "account_type_name": "Zero",
        "minimum_lot_size": 0.01,
        "maximum_lot_size": None,
        "lot_step": 0.01,
        "supported_categories": ["FOREX", "METALS"],
        "specification_status": "partially_verified",
        "source": "https://www.hfm.com/int/en/trading-accounts",
    },
    {
        "broker_id": "hfm",
        "account_type_id": "cent",
        "account_type_name": "Cent",
        "minimum_lot_size": 0.01,
        "maximum_lot_size": None,
        "lot_step": 0.01,
        "supported_categories": ["FOREX", "METALS"],
        "specification_status": "partially_verified",
        "source": "https://www.hfm.com/int/en/trading-accounts/cent-account",
    },
    {
        "broker_id": "hfm",
        "account_type_id": "pro",
        "account_type_name": "Pro",
        "minimum_lot_size": 0.01,
        "maximum_lot_size": None,
        "lot_step": 0.01,
        "supported_categories": ["FOREX", "METALS"],
        "specification_status": "partially_verified",
        "source": "https://www.hfm.com/int/en/trading-accounts/pro-account",
    },
    {
        "broker_id": "hfm",
        "account_type_id": "infinityx",
        "account_type_name": "InfinityX",
        "minimum_lot_size": 0.01,
        "maximum_lot_size": None,
        "lot_step": 0.01,
        "supported_categories": ["FOREX", "METALS"],
        "specification_status": "partially_verified",
        "source": "https://www.hfm.com/int/en/trading-accounts",
    },
]


# --------------------------------------------------
# DEFAULT SPECIFICATIONS BY BROKER AND ACCOUNT TYPE
# --------------------------------------------------

BROKER_DEFAULT_SPECS = {
    ("exness", "standard"): {
        "FOREX": {
            "contract_size": 100000,
            "calculation_type": "forex",
            "verified": True,
            "source": (
                "https://www.exness.com/cdn/media/docs/" "key_facts_statement.pdf"
            ),
        },
    },
    ("hfm", "premium"): {
        "FOREX": {
            "contract_size": 100000,
            "calculation_type": "forex",
            "verified": True,
            "source": "https://www.hfm.com/int/en/trading-accounts",
        },
    },
    ("hfm", "zero"): {
        "FOREX": {
            "contract_size": 100000,
            "calculation_type": "forex",
            "verified": True,
            "source": "https://www.hfm.com/int/en/trading-accounts",
        },
    },
    ("hfm", "cent"): {
        "FOREX": {
            "contract_size": 1000,
            "calculation_type": "forex",
            "verified": True,
            "source": "https://www.hfm.com/int/en/trading-accounts/cent-account",
        },
    },
    ("hfm", "pro"): {
        "FOREX": {
            "contract_size": 100000,
            "calculation_type": "forex",
            "verified": True,
            "source": "https://www.hfm.com/int/en/trading-accounts/pro-account",
        },
    },
    ("hfm", "infinityx"): {
        "FOREX": {
            "contract_size": 100000,
            "calculation_type": "forex",
            "verified": True,
            "source": "https://www.hfm.com/int/en/trading-accounts",
        },
    },
}


# --------------------------------------------------
# INSTRUMENT-SPECIFIC OVERRIDES
# --------------------------------------------------

BROKER_INSTRUMENT_OVERRIDES = {
    # EXNESS STANDARD GOLD
    ("exness", "standard", "XAUUSD"): {
        "contract_size": 100,
        "minimum_lot_size": 0.01,
        "maximum_lot_size_day": 200,
        "maximum_lot_size_night": 200,
        "calculation_type": "metal",
        "verified": True,
        "source": ("https://www.exness.com/blog/product/" "xauusd247-gold-trading/"),
    },
    # EXNESS STANDARD SILVER
    ("exness", "standard", "XAGUSD"): {
        "contract_size": 5000,
        "minimum_lot_size": 0.01,
        "maximum_lot_size_day": 200,
        "maximum_lot_size_night": 20,
        "calculation_type": "metal",
        "verified": True,
        "source": (
            "https://get.exness.help/hc/en-us/articles/" "17854173039388-Commodities"
        ),
    },
    # EXNESS STANDARD BITCOIN
    ("exness", "standard", "BTCUSD"): {
        "contract_size": 1,
        "price_decimals": 2,
        "minimum_lot_size": 0.01,
        "maximum_lot_size_day": 200,
        "maximum_lot_size_night": 200,
        "calculation_type": "crypto",
        "verified": True,
        "availability_by_entity": {
            "exness_ke": False,
            "international": True,
        },
        "source": (
            "https://get.exness.help/hc/en-us/articles/"
            "17854191888540-Cryptocurrencies"
        ),
    },
    # EXNESS STANDARD ETHEREUM
    ("exness", "standard", "ETHUSD"): {
        "contract_size": 1,
        "minimum_lot_size": 0.1,
        "maximum_lot_size_day": 2000,
        "maximum_lot_size_night": 2000,
        "calculation_type": "crypto",
        "verified": True,
        "availability_by_entity": {
            "exness_ke": False,
            "international": True,
        },
        "source": (
            "https://get.exness.help/hc/en-us/articles/"
            "17854191888540-Cryptocurrencies"
        ),
    },
    # HFM GOLD
    ("hfm", "premium", "XAUUSD"): {
        "contract_size": 100,
        "minimum_lot_size": 0.01,
        "maximum_lot_size": 60,
        "lot_step": 0.01,
        "calculation_type": "metal",
        "verified": True,
        "source": (
            "https://www.hfm.com/int/en/trading-instruments/"
            "single-product?symbol=XAUUSD"
        ),
    },
    ("hfm", "zero", "XAUUSD"): {
        "contract_size": 100,
        "minimum_lot_size": 0.01,
        "maximum_lot_size": 60,
        "lot_step": 0.01,
        "calculation_type": "metal",
        "verified": True,
        "source": (
            "https://www.hfm.com/int/en/trading-instruments/"
            "single-product?symbol=XAUUSD"
        ),
    },
    ("hfm", "cent", "XAUUSD"): {
        "contract_size": 1,
        "minimum_lot_size": 0.01,
        "maximum_lot_size": 200,
        "lot_step": 0.01,
        "calculation_type": "metal",
        "verified": True,
        "source": (
            "https://www.hfm.com/int/en/trading-instruments/"
            "single-product?symbol=XAUUSD"
        ),
    },
    ("hfm", "pro", "XAUUSD"): {
        "contract_size": 100,
        "minimum_lot_size": 0.01,
        "maximum_lot_size": 60,
        "lot_step": 0.01,
        "calculation_type": "metal",
        "verified": True,
        "source": (
            "https://www.hfm.com/int/en/trading-instruments/"
            "single-product?symbol=XAUUSD"
        ),
    },
    ("hfm", "infinityx", "XAUUSD"): {
        "contract_size": 100,
        "minimum_lot_size": 0.01,
        "maximum_lot_size": 60,
        "lot_step": 0.01,
        "calculation_type": "metal",
        "verified": True,
        "source": (
            "https://www.hfm.com/int/en/trading-instruments/"
            "single-product?symbol=XAUUSD"
        ),
    },
    # HFM SILVER
    ("hfm", "premium", "XAGUSD"): {
        "contract_size": 1000,
        "minimum_lot_size": 0.01,
        "maximum_lot_size": 60,
        "lot_step": 0.01,
        "price_decimals": 3,
        "calculation_type": "metal",
        "verified": True,
        "source": (
            "https://www.hfm.com/int/en/trading-instruments/"
            "single-product?symbol=XAGUSD"
        ),
    },
    ("hfm", "zero", "XAGUSD"): {
        "contract_size": 1000,
        "minimum_lot_size": 0.01,
        "maximum_lot_size": 60,
        "lot_step": 0.01,
        "price_decimals": 3,
        "calculation_type": "metal",
        "verified": True,
        "source": (
            "https://www.hfm.com/int/en/trading-instruments/"
            "single-product?symbol=XAGUSD"
        ),
    },
    ("hfm", "pro", "XAGUSD"): {
        "contract_size": 1000,
        "minimum_lot_size": 0.01,
        "maximum_lot_size": 60,
        "lot_step": 0.01,
        "price_decimals": 3,
        "calculation_type": "metal",
        "verified": True,
        "source": (
            "https://www.hfm.com/int/en/trading-instruments/"
            "single-product?symbol=XAGUSD"
        ),
    },
    ("hfm", "infinityx", "XAGUSD"): {
        "contract_size": 1000,
        "minimum_lot_size": 0.01,
        "maximum_lot_size": 60,
        "lot_step": 0.01,
        "price_decimals": 3,
        "calculation_type": "metal",
        "verified": True,
        "source": (
            "https://www.hfm.com/int/en/trading-instruments/"
            "single-product?symbol=XAGUSD"
        ),
    },
}


# --------------------------------------------------
# GET BROKER ACCOUNT TYPE
# --------------------------------------------------


def get_broker_account_type(broker_id, account_type_id):

    broker_id = broker_id.strip().lower()
    account_type_id = account_type_id.strip().lower()

    for account in BROKER_ACCOUNT_TYPES:

        if (
            account["broker_id"] == broker_id
            and account["account_type_id"] == account_type_id
        ):
            return deepcopy(account)

    return None


# --------------------------------------------------
# GET AVAILABLE ACCOUNT TYPES FOR A BROKER
# --------------------------------------------------


def get_account_types(broker_id):

    broker_id = broker_id.strip().lower()

    return [
        deepcopy(account)
        for account in BROKER_ACCOUNT_TYPES
        if account["broker_id"] == broker_id
    ]


# --------------------------------------------------
# GET BROKER-SPECIFIC INSTRUMENT SPECIFICATIONS
# --------------------------------------------------


def get_broker_instrument_spec(
    broker_id,
    account_type_id,
    symbol,
):

    broker_id = broker_id.strip().lower()
    account_type_id = account_type_id.strip().lower()
    symbol = symbol.strip().upper()

    # --------------------------------------------------
    # EXNESS STANDARD CENT
    # --------------------------------------------------

    if broker_id == "exness" and account_type_id == "standard_cent":

        if not symbol.endswith("C"):
            return None

        original_symbol = symbol[:-1]

        if original_symbol not in EXNESS_CENT_SUPPORTED_SYMBOLS:
            return None

        instrument = get_instrument(original_symbol)

        if instrument is None:
            return None

        category = instrument["category"]

        if category == "FOREX":
            contract_size = 1000
            calculation_type = "forex"

        elif original_symbol == "XAUUSD":
            contract_size = 1
            calculation_type = "metal"

        elif original_symbol == "XAGUSD":
            contract_size = 50
            calculation_type = "metal"

        else:
            return None

        return {
            "broker_id": broker_id,
            "account_type_id": account_type_id,
            "symbol": symbol,
            "category": category,
            "base_currency": instrument["base_currency"],
            "quote_currency": instrument["quote_currency"],
            "contract_size": contract_size,
            "minimum_lot_size": 0.01,
            "maximum_lot_size": 200,
            "lot_step": None,
            "price_decimals": instrument["price_decimals"],
            "calculation_type": calculation_type,
            "verified": True,
            "source": (
                "https://get.exness.help/hc/en-us/articles/"
                "17537782786588-Standard-Cent-account"
            ),
        }

    # --------------------------------------------------
    # NORMAL INSTRUMENT HANDLING
    # --------------------------------------------------

    instrument = get_instrument(symbol)

    if instrument is None:
        return None

    account = get_broker_account_type(
        broker_id,
        account_type_id,
    )

    if account is None:
        return None

    specification = {
        "broker_id": broker_id,
        "account_type_id": account_type_id,
        "symbol": symbol,
        "category": instrument["category"],
        "base_currency": instrument["base_currency"],
        "quote_currency": instrument["quote_currency"],
        "contract_size": None,
        "minimum_lot_size": account["minimum_lot_size"],
        "maximum_lot_size": account["maximum_lot_size"],
        "lot_step": account["lot_step"],
        "price_decimals": instrument["price_decimals"],
        "calculation_type": instrument["calculation_type"],
        "verified": False,
        "source": None,
    }

    # Apply verified category-level defaults.

    defaults = BROKER_DEFAULT_SPECS.get(
        (broker_id, account_type_id),
        {},
    )

    category_defaults = defaults.get(
        instrument["category"],
        {},
    )

    specification.update(category_defaults)

    # Apply verified instrument-specific overrides.

    override = BROKER_INSTRUMENT_OVERRIDES.get(
        (broker_id, account_type_id, symbol),
        {},
    )

    specification.update(override)

    return specification


# --------------------------------------------------
# BROKER ENTITY AVAILABILITY
# --------------------------------------------------


def is_instrument_available_for_entity(
    broker_id,
    account_type_id,
    symbol,
    entity_id,
):

    specification = get_broker_instrument_spec(
        broker_id,
        account_type_id,
        symbol,
    )

    if specification is None:
        return False

    availability = specification.get("availability_by_entity")

    if not availability:
        return True

    return availability.get(entity_id.strip().lower(), False)


# --------------------------------------------------
# GET AVAILABLE INSTRUMENTS FOR BROKER ENTITY
# --------------------------------------------------


def get_available_instruments_for_entity(
    broker_id,
    account_type_id,
    entity_id,
):

    broker_id = broker_id.strip().lower()
    account_type_id = account_type_id.strip().lower()
    entity_id = entity_id.strip().lower()

    available = []

    for instrument in INSTRUMENTS:

        base_symbol = instrument["symbol"]

        # Standard Cent uses suffixed symbols.
        if broker_id == "exness" and account_type_id == "standard_cent":

            if base_symbol not in EXNESS_CENT_SUPPORTED_SYMBOLS:
                continue

            symbol = f"{base_symbol}c"

        else:
            symbol = base_symbol

        spec = get_broker_instrument_spec(
            broker_id,
            account_type_id,
            symbol,
        )

        # Only include verified instruments with contract sizes.
        if (
            spec is None
            or not spec.get("verified")
            or spec.get("contract_size") is None
        ):
            continue

        # Check entity availability.
        if not is_instrument_available_for_entity(
            broker_id,
            account_type_id,
            symbol,
            entity_id,
        ):
            continue

        available_instrument = instrument.copy()

        # Return the actual broker symbol.
        available_instrument["symbol"] = symbol

        # Return broker-specific specifications.
        available_instrument["contract_size"] = spec["contract_size"]
        available_instrument["price_decimals"] = spec["price_decimals"]
        available_instrument["calculation_type"] = spec["calculation_type"]

        available.append(available_instrument)

    return available
