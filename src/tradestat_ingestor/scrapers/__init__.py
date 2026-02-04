"""
Site-specific scrapers for tradestat.commerce.gov.in

Each scraper module handles a specific feature/endpoint.
All scrapers return raw HTML/JSON responses without any parsing or storage.

Data Banks:
- EIDB: Export Import Data Bank (Annual data)
- MEIDB: Monthly Export Import Data Bank (Monthly data)
- FTPA: Foreign Trade Policy Analysis (future)
- FTSPCC: Foreign Trade Statistics by Principal Commodity Classification (future)
"""

from . import eidb
from . import meidb
