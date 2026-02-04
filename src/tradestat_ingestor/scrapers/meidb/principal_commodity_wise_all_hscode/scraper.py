"""
MEIDB Principal Commodity-wise All HSCode scraper.
Fetches all HSCode breakdowns for a given principal commodity from MEIDB.
"""

from loguru import logger
from typing import Optional

# URL paths for MEIDB principal commodity-wise all HSCode reports
EXPORT_PATH = "/meidb/principal_commodity_wise_all_HSCode_export"
IMPORT_PATH = "/meidb/principal_commodity_wise_all_HSCode_import"

# Month mapping
MONTHS = {
    1: "January", 2: "February", 3: "March", 4: "April",
    5: "May", 6: "June", 7: "July", 8: "August",
    9: "September", 10: "October", 11: "November", 12: "December"
}

# Value type mapping for form submission
VALUE_TYPES = {"usd": "1", "quantity": "2", "inr": "3"}
YEAR_TYPES = {"financial": "1", "calendar": "2"}

# Principal commodity codes mapping
PRINCIPAL_COMMODITIES = {
    "A1": "TEA", "A2": "COFFEE", "A3": "RICE -BASMOTI", "A4": "RICE(OTHER THAN BASMOTI)",
    "A5": "WHEAT", "A6": "OTHER CEREALS", "A7": "PULSES", "A8": "TOBACCO UNMANUFACTURED",
    "A9": "TOBACCO MANUFACTURED", "B1": "SPICES", "B2": "CASHEW", "B3": "CASHEW NUT SHELL LIQUID",
    "B4": "SESAME SEEDS", "B5": "NIGER SEEDS", "B6": "GROUNDNUT", "B7": "OTHER OIL SEEDS",
    "B8": "VEGETABLE OILS", "B9": "OIL MEALS", "C1": "GUERGAM MEAL", "C2": "CASTOR OIL",
    "C3": "SHELLAC", "C4": "SUGAR", "C5": "MOLLASES", "C6": "FRUITS / VEGETABLE SEEDS",
    "C7": "FRESH FRUITS", "C8": "FRESH VEGETABLES", "C9": "PROCESSED VEGETABLES",
    "D1": "PROCESSED FRUITS AND JUICES", "D2": "CEREAL PREPARATIONS", "D3": "COCOA PRODUCTS",
    "D4": "MILLED PRODUCTS", "D5": "MISC PROCESSED ITEMS", "D6": "ANIMAL CASINGS",
    "D7": "BUFFALO MEAT", "D8": "SHEEP/GOAT MEAT", "D9": "OTHER MEAT", "E1": "PROCESSED MEAT",
    "E2": "DAIRY PRODUCTS", "E3": "POULTRY PRODUCTS", "E4": "FLORICLTR PRODUCTS",
    "E5": "NATURAL RUBBER", "E6": "ALCOHOLIC BEVERAGES", "E7": "MARINE PRODUCTS",
    "E8": "IRON ORE", "E9": "MICA", "F1": "COAL", "F2": "BULK MINERALS AND ORES",
    "F3": "GRANIT", "F4": "PROCESSED MINERALS", "F5": "SULPHER", "F6": "OTHER CRUDE MINERALS",
    "F7": "RAW HIDES AND SKINS", "F8": "FINISHED LEATHER", "F9": "LEATHER GOODS",
    "G1": "LEATHER GARMENTS", "G2": "FOOTWEAR OF LEATHER", "G3": "LEATHER FOOTWEAR COMPONENT",
    "G4": "SADDLERY AND HARNESS", "G5": "PEARL", "G6": "GOLD", "G7": "SILVER",
    "G8": "OTHER PRECIOUS AND BASE METALS", "G9": "GOLD AND OTH PRECS METL JWLERY",
    "H1": "SPORTS GOODS", "H2": "FERTILEZERS CRUDE", "H3": "FERTILEZERS MANUFACTURED",
    "H4": "AYUSH AND HERBAL PRODUCTS", "H5": "BULK DRUGS", "H6": "DYE INTERMEDIATES",
    "H7": "DYES", "H8": "DRUG FORMULATIONS", "H9": "AGRO CHEMICALS", "I1": "SURGICALS",
    "I2": "INORGANIC CHEMICALS", "I3": "ORGANIC CHEMICALS", "I4": "OTHER MISCELLAENIOUS CHEMICALS",
    "I5": "COSMETICS AND TOILETRIES", "I6": "ESSENTIAL OILS", "I7": "RESIDUL CHEMICL AND ALLED PROD",
    "I8": "AUTO TYRES AND TUBES", "I9": "OTHR RUBBER PRODCT EXCPT FOOTW",
    "J1": "FOOTWEAR OF RUBBER/CANVAS ETC.", "J2": "PAINT", "J3": "GRAPHITE", "J4": "CMNT",
    "J5": "CERAMICS AND ALLIED PRODUCTS", "J6": "GLASS AND GLASSWARE", "J7": "BOOKS",
    "J8": "NEWSPRINT", "J9": "PAPER", "K1": "PLYWOOD AND ALLIED PRODUCTS",
    "K2": "OTHER WOOD AND WOOD PRODUCTS", "K3": "PULP AND WASTE PAPER",
    "K4": "OPTICAL ITEMS (INCL.LENS ETC)", "K5": "HUMAN HAIR", "K6": "MOULDED AND EXTRUDED GOODS",
    "K7": "PACKAGING MATERIALS", "K8": "PLASTIC RAW MATERIALS", "K9": "PLASTC SHT",
    "L1": "STATIONRY/OFFCE", "L2": "OTHER PLASTIC ITEMS", "L3": "IRON AND STEEL",
    "L4": "PRODUCTS OF IRON AND STEEL", "L5": "ALUMINIUM", "L6": "COPPER AND PRDCTS MADE OF COPR",
    "L7": "LEAD AND PRODUCTS MADE OF LED", "L8": "NICKEL", "L9": "TIN AND PRODUCTS MADE OF TIN",
    "M1": "ZINC AND PRODUCTS MADE OF ZINC", "M2": "OTH NON FEROUS METAL AND PRODC",
    "M3": "AUTO COMPONENTS/PARTS", "M4": "ELECTRODES", "M5": "ACCUMULATORS AND BATTERIES",
    "M6": "HND TOOL", "M7": "MACHINE TOOLS", "M8": "MEDICAL AND SCIENTIFIC INSTRUM",
    "M9": "OFFICE EQUIPMENTS", "N1": "AC", "N2": "BICYCLE AND PARTS", "N3": "CRANES",
    "N4": "ELECTRIC MACHINERY AND EQUIPME", "N5": "IC ENGINES AND PARTS",
    "N6": "INDL. MACHNRY FOR DAIRY ETC", "N7": "ATM", "N8": "NUCLER REACTR",
    "N9": "OTHER CONSTRUCTION MACHINERY", "O1": "OTHER MISC. ENGINEERING ITEMS",
    "O2": "PRIME MICA AND MICA PRODUCTS", "O3": "PUMPS OF ALL TYPES", "O4": "AIRCRAFT",
    "O5": "MOTOR VEHICLE/CARS", "O6": "RAILWY TRNSPRT EQUIPMNTS", "O7": "SHIP",
    "O8": "TWO AND THREE WHEELERS", "O9": "COMPUTER HARDWARE", "P1": "CONSUMER ELECTRONICS",
    "P2": "ELECTRONICS COMPONENTS", "P3": "ELECTRONICS INSTRUMENTS", "P4": "TELECOM INSTRUMENTS",
    "P5": "PROJECT GOODS", "P6": "MANMADE STAPLE FIBRE", "P7": "COTTON YARN",
    "P8": "COTTON FABRICS", "P9": "OTH TXTL YRN", "Q1": "SILK", "Q2": "NATRL SILK YARN",
    "Q3": "MANMADE YARN", "Q4": "WOOL", "Q5": "WOLLEN YARN", "Q6": "RMG COTTON INCL ACCESSORIES",
    "Q7": "RMG SILK", "Q8": "RMG MANMADE FIBRES", "Q9": "RMG WOOL", "R1": "RMG OF OTHR TEXTLE MATRL",
    "R2": "COIR AND COIR MANUFACTURES", "R3": "HANDLOOM PRODUCTS", "R4": "SILK WASTE",
    "R5": "JUTE", "R6": "JUTE YARN", "R7": "JUTE HESSIAN", "R8": "FLOOR CVRNG OF JUTE",
    "R9": "OTHER JUTE MANUFACTURES", "S1": "HANDCRFS(EXCL.HANDMADE CRPTS)",
    "S2": "CARPET(EXCL. SILK) HANDMADE", "S3": "SILK CARPET", "S4": "COTTON RAW INCLD. WASTE",
    "S5": "PETROLEUM: CRUDE", "S6": "PETROLEUM PRODUCTS", "ZZ": "OTHER COMMODITIES",
}


def get_commodity_name(code: str) -> str:
    """Get the commodity name for a given principal commodity code."""
    return PRINCIPAL_COMMODITIES.get(code.upper(), code)


def scrape_meidb_principal_commodity_wise_all_hscode(
    session,
    base_url: str,
    commodity_code: str,
    month: int,
    year: int,
    trade_type: str = "export",
    value_type: str = "usd",
    year_type: str = "financial",
    state: dict = None
) -> Optional[str]:
    """
    Scrape monthly principal commodity-wise all HSCode data from MEIDB.

    Args:
        session: requests.Session object with CSRF token support
        base_url: Base URL of tradestat website
        commodity_code: Principal commodity code (e.g., A1=TEA, L3=IRON AND STEEL)
        month: Month (1-12)
        year: Year (e.g., 2024, 2025)
        trade_type: "export" or "import"
        value_type: "usd" (US $ Million), "inr" (₹ Crore), or "quantity"
        year_type: "financial" or "calendar"
        state: Dictionary containing CSRF token and other auth state

    Returns:
        HTML response as string, or None if request fails
    """
    # Validate month
    if month < 1 or month > 12:
        logger.error(f"Invalid month: {month}. Must be 1-12")
        return None

    # Validate commodity code
    commodity_code = commodity_code.upper()
    if commodity_code not in PRINCIPAL_COMMODITIES:
        logger.error(f"Invalid commodity code: {commodity_code}")
        return None

    # Determine the URL path based on trade type
    if trade_type.lower() == "export":
        path = EXPORT_PATH
    elif trade_type.lower() == "import":
        path = IMPORT_PATH
    else:
        logger.error(f"Invalid trade_type: {trade_type}. Must be 'export' or 'import'")
        return None

    # Build payload - field names have 'p' prefix for export, 'imp' prefix for import
    # Export: pddMonth, pddYear, pbrcitmdata, pddReportVal, pddReportYear
    # Import: impddMonth, impddYear, impbrcitmdata, impddReportVal, impddReportYear
    if trade_type.lower() == "export":
        payload = {
            "_token": state.get("_token", "") if state else "",
            "pddMonth": str(month),
            "pddYear": str(year),
            "pbrcitmdata": commodity_code,
            "pddReportVal": VALUE_TYPES.get(value_type.lower(), "1"),
            "pddReportYear": YEAR_TYPES.get(year_type.lower(), "1"),
        }
    else:
        # Import uses 'imp' prefix for all field names
        payload = {
            "_token": state.get("_token", "") if state else "",
            "impddMonth": str(month),
            "impddYear": str(year),
            "impbrcitmdata": commodity_code,
            "impddReportVal": VALUE_TYPES.get(value_type.lower(), "1"),
            "impddReportYear": YEAR_TYPES.get(year_type.lower(), "1"),
        }

    commodity_name = get_commodity_name(commodity_code)
    logger.info(f"Fetching MEIDB principal commodity data: {commodity_name} ({commodity_code}), {MONTHS.get(month)}/{year}, {trade_type}")

    try:
        resp = session.post(base_url + path, data=payload, timeout=120)
        resp.raise_for_status()
        logger.success(f"Fetch successful: {len(resp.text)} bytes")
        return resp.text
    except Exception as e:
        logger.error(f"Fetch failed: {e}")
        return None
