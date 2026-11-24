# --------------------------------------------------
# BROKER DIRECTORY
# --------------------------------------------------
# This directory identifies brokers and their regional
# verification status.
#
# IMPORTANT:
# A broker listed here is not automatically verified
# as available or regulated in every listed country.
# --------------------------------------------------


BROKERS = [
    # --------------------------------------------------
    # EAST AFRICA - KENYA CMA REGISTER
    # --------------------------------------------------
    {
        "id": "fxpesa",
        "name": "FXPesa",
        "legal_entity": "EGM Securities Limited",
        "regions": ["east_africa"],
        "regional_status": {"east_africa": "cma_listed"},
    },
    {
        "id": "scope_markets",
        "name": "Scope Markets",
        "legal_entity": "SCFM Limited",
        "regions": ["east_africa", "south_africa"],
        "regional_status": {
            "east_africa": "cma_listed",
            "south_africa": "verify_required",
        },
    },
    {
        "id": "pepperstone",
        "name": "Pepperstone",
        "legal_entity": "Pepperstone Markets Kenya Limited",
        "regions": ["east_africa", "south_africa", "west_africa"],
        "regional_status": {
            "east_africa": "cma_listed",
            "south_africa": "verify_required",
            "west_africa": "availability_to_confirm",
        },
    },
    {
        "id": "fxtm",
        "name": "FXTM",
        "legal_entity": "Exinity Capital East Africa Limited",
        "regions": ["east_africa", "south_africa", "west_africa"],
        "regional_status": {
            "east_africa": "cma_listed",
            "south_africa": "verify_required",
            "west_africa": "availability_to_confirm",
        },
    },
    {
        "id": "hfm",
        "name": "HFM",
        "legal_entity": "HFM Investments Limited",
        "regions": ["east_africa", "south_africa", "west_africa"],
        "regional_status": {
            "east_africa": "cma_listed",
            "south_africa": "verify_required",
            "west_africa": "availability_to_confirm",
        },
    },
    {
        "id": "windsor",
        "name": "Windsor Brokers",
        "legal_entity": "Windsor Markets Kenya Limited",
        "regions": ["east_africa"],
        "regional_status": {
            "east_africa": "cma_listed",
        },
    },
    {
        "id": "exness",
        "name": "Exness",
        "legal_entity": "Exness KE Limited",
        "regions": ["east_africa", "south_africa", "west_africa"],
        "regional_status": {
            "east_africa": "cma_listed",
            "south_africa": "verify_required",
            "west_africa": "availability_to_confirm",
        },
    },
    {
        "id": "ingot",
        "name": "INGOT Brokers",
        "legal_entity": "Ingot KE Limited",
        "regions": ["east_africa", "south_africa"],
        "regional_status": {
            "east_africa": "cma_listed",
            "south_africa": "verify_required",
        },
    },
    {
        "id": "admirals",
        "name": "Admirals",
        "legal_entity": "Admirals KE Limited",
        "regions": ["east_africa", "south_africa"],
        "regional_status": {
            "east_africa": "cma_listed",
            "south_africa": "verify_required",
        },
    },
    {
        "id": "fp_markets",
        "name": "FP Markets",
        "legal_entity": "FP Markets Limited",
        "regions": ["east_africa", "south_africa", "west_africa"],
        "regional_status": {
            "east_africa": "cma_listed",
            "south_africa": "verify_required",
            "west_africa": "availability_to_confirm",
        },
    },
    {
        "id": "ic_markets",
        "name": "IC Markets",
        "legal_entity": "IC Markets (KE) Limited",
        "regions": ["east_africa", "south_africa", "west_africa"],
        "regional_status": {
            "east_africa": "cma_listed",
            "south_africa": "verify_required",
            "west_africa": "availability_to_confirm",
        },
    },
    {
        "id": "anzo_capital",
        "name": "ANZO Capital",
        "legal_entity": "ANZO Capital Limited",
        "regions": ["east_africa", "south_africa"],
        "regional_status": {
            "east_africa": "cma_listed",
            "south_africa": "verify_required",
        },
    },
    {
        "id": "tpxmglobal",
        "name": "TPXMGlobal",
        "legal_entity": "TPXMGlobal Kenya Limited",
        "regions": ["east_africa"],
        "regional_status": {
            "east_africa": "cma_listed",
        },
    },
    {
        "id": "avatrade",
        "name": "AvaTrade",
        "legal_entity": "Ava Trade Kenya Limited",
        "regions": ["east_africa", "south_africa", "west_africa"],
        "regional_status": {
            "east_africa": "cma_listed",
            "south_africa": "verify_required",
            "west_africa": "availability_to_confirm",
        },
    },
    # --------------------------------------------------
    # ADDITIONAL KENYA CMA DEALING BROKERS
    # --------------------------------------------------
    {
        "id": "empire_fx",
        "name": "Empire FX",
        "legal_entity": "Empire FX Trade Limited",
        "regions": ["east_africa"],
        "regional_status": {
            "east_africa": "cma_listed",
        },
    },
    {
        "id": "capital_com",
        "name": "Capital.com",
        "legal_entity": "CC Kenya Securities Limited",
        "regions": ["east_africa", "south_africa"],
        "regional_status": {
            "east_africa": "cma_listed",
            "south_africa": "verify_required",
        },
    },
    # --------------------------------------------------
    # ADDITIONAL SOUTH AFRICAN MARKET CANDIDATES
    # --------------------------------------------------
    {
        "id": "tickmill",
        "name": "Tickmill",
        "legal_entity": None,
        "regions": ["south_africa", "west_africa"],
        "regional_status": {
            "south_africa": "verify_required",
            "west_africa": "availability_to_confirm",
        },
    },
    {
        "id": "ig",
        "name": "IG",
        "legal_entity": None,
        "regions": ["south_africa"],
        "regional_status": {
            "south_africa": "verify_required",
        },
    },
    {
        "id": "vantage",
        "name": "Vantage",
        "legal_entity": None,
        "regions": ["south_africa", "west_africa"],
        "regional_status": {
            "south_africa": "verify_required",
            "west_africa": "availability_to_confirm",
        },
    },
    {
        "id": "acy",
        "name": "ACY Securities",
        "legal_entity": None,
        "regions": ["south_africa"],
        "regional_status": {
            "south_africa": "verify_required",
        },
    },
    {
        "id": "atfx",
        "name": "ATFX",
        "legal_entity": None,
        "regions": ["south_africa", "west_africa"],
        "regional_status": {
            "south_africa": "verify_required",
            "west_africa": "availability_to_confirm",
        },
    },
    {
        "id": "xm",
        "name": "XM",
        "legal_entity": None,
        "regions": ["south_africa", "west_africa"],
        "regional_status": {
            "south_africa": "verify_required",
            "west_africa": "availability_to_confirm",
        },
    },
    # --------------------------------------------------
    # ADDITIONAL WEST AFRICAN MARKET CANDIDATES
    # --------------------------------------------------
    {
        "id": "deriv",
        "name": "Deriv",
        "legal_entity": None,
        "regions": ["west_africa"],
        "regional_status": {
            "west_africa": "availability_to_confirm",
        },
    },
    {
        "id": "axi",
        "name": "Axi",
        "legal_entity": None,
        "regions": ["west_africa", "south_africa"],
        "regional_status": {
            "west_africa": "availability_to_confirm",
            "south_africa": "verify_required",
        },
    },
    {
        "id": "roboforex",
        "name": "RoboForex",
        "legal_entity": None,
        "regions": ["west_africa"],
        "regional_status": {
            "west_africa": "availability_to_confirm",
        },
    },
    {
        "id": "fbs",
        "name": "FBS",
        "legal_entity": None,
        "regions": ["west_africa", "south_africa"],
        "regional_status": {
            "west_africa": "availability_to_confirm",
            "south_africa": "verify_required",
        },
    },
]


# --------------------------------------------------
# BROKER LEGAL ENTITIES
# --------------------------------------------------

BROKER_ENTITIES = {
    "exness": [
        {
            "id": "exness_ke",
            "name": "Exness Kenya",
        },
        {
            "id": "international",
            "name": "Exness International",
        },
    ],
    "hfm": [
        {
            "id": "hfm_ke",
            "name": "HFM Investments Ltd (Kenya)",
        },
        {
            "id": "hfm_sv",
            "name": "HF Markets (SV) Ltd (International)",
        },
    ],
}


# --------------------------------------------------
# GET ENTITIES FOR A BROKER
# --------------------------------------------------


def get_broker_entities(broker_id):

    broker_id = broker_id.strip().lower()

    return [entity.copy() for entity in BROKER_ENTITIES.get(broker_id, [])]


# --------------------------------------------------
# GET BROKER BY ID
# --------------------------------------------------


def get_broker(broker_id):

    broker_id = broker_id.strip().lower()

    for broker in BROKERS:

        if broker["id"] == broker_id:
            return broker.copy()

    return None


# --------------------------------------------------
# SEARCH BROKERS
# --------------------------------------------------


def search_brokers(query, limit=10):

    query = query.strip().lower()

    if not query:
        return []

    matches = []

    for broker in BROKERS:

        if query in broker["name"].lower() or query in broker["id"].lower():
            matches.append(broker.copy())

        if len(matches) >= limit:
            break

    return matches


# --------------------------------------------------
# GET BROKERS BY REGION
# --------------------------------------------------


def get_brokers_for_region(region):

    region = region.strip().lower()

    return [broker.copy() for broker in BROKERS if region in broker["regions"]]


# --------------------------------------------------
# GET REGIONAL VERIFICATION STATUS
# --------------------------------------------------


def get_broker_region_status(broker_id, region):

    broker = get_broker(broker_id)

    if broker is None:
        return None

    return broker["regional_status"].get(region.strip().lower())
