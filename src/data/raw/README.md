# Indian Trade Data (2018-2024)

**Comprehensive export and import trade data for 11,185+ Indian HSN (Harmonized System of Nomenclature) codes covering 7 years.**

## Overview

This repository contains consolidated trade statistics for all Indian commodity codes at the HS8 digit level, sourced from India's Economic Intelligence Data Bank (EIDB). The data includes both export and import records with country-wise breakdown.

## Dataset Coverage

- **HSN Codes**: 11,185+ (HS8 digit classification)
- **Time Period**: 2018-2024 (7 years)
- **Trade Types**: Export & Import
- **Countries**: All trading partners
- **Data Points**: Quantity, Value (USD), Unit prices
- **Total Records**: 22,370+ consolidated JSON files

## Directory Structure

```
raw/
├── export/              # Export data by HSN
│   ├── 01012100/
│   │   └── 01012100_export.json
│   ├── 01012910/
│   │   └── 01012910_export.json
│   └── ...
└── import/              # Import data by HSN
    ├── 01012100/
    │   └── 01012100_import.json
    ├── 01012910/
    │   └── 01012910_import.json
    └── ...
```

## Data Format

Each JSON file contains 7 years of consolidated trade data:

```json
{
  "metadata": {
    "consolidated_at": "2026-01-27T02:51:30.123456",
    "trade_type": "export",
    "years_count": 7,
    "schema_version": "2.0",
    "source_url": "https://tradestat.commerce.gov.in/eidb"
  },
  "commodity": {
    "hsn_code": "01012100",
    "description": "Live horses"
  },
  "years": {
    "2024": {
      "report_date": "2024-12-31",
      "scraped_at": "2026-01-27T02:45:23",
      "countries": [
        {
          "name": "Afghanistan",
          "quantity": 15000,
          "unit": "No",
          "value": 1500000,
          "unit_price": 100
        }
      ],
      "totals": {
        "total_quantity": 150000,
        "total_value": 15000000
      }
    },
    "2023": { ... },
    "2022": { ... },
    ...
  }
}
```

## File Naming Convention

- **Export files**: `{HSN_CODE}_export.json`
- **Import files**: `{HSN_CODE}_import.json`

Example: `01012100_export.json` contains 7-year export data for HSN code 01012100

## Quick Start

### 1. Explore Single HSN Code

```bash
# View export data for HSN 01012100
cat export/01012100/01012100_export.json

# View import data for HSN 01012100
cat import/01012100/01012100_import.json
```

### 2. Python - Load & Analyze

```python
import json
from pathlib import Path

# Load export data
with open('export/01012100/01012100_export.json') as f:
    data = json.load(f)

# Access 2024 data
year_2024 = data['years']['2024']
print(f"Countries: {len(year_2024['countries'])}")
print(f"Total Value: ${year_2024['totals']['total_value']:,}")

# Iterate all countries
for country in year_2024['countries']:
    print(f"{country['name']}: {country['quantity']} {country['unit']}")
```

### 3. Find HSN Codes by Pattern

```bash
# List all automotive codes (HS 87xx)
ls export/ | grep "^87"

# List all chemical codes (HS 29xx)
ls export/ | grep "^29"
```

### 4. Get Summary Statistics

```bash
# Count total export files
ls -R export/ | grep "_export.json" | wc -l

# Count total import files
ls -R import/ | grep "_import.json" | wc -l
```

## Data Quality Notes

- **Scraped Data**: All data sourced from official EIDB website
- **Completeness**: Some HSN codes may have missing years or countries
- **Currency**: All values are in USD
- **Quantities**: Units vary by commodity (kg, liters, pieces, etc.)
- **Consolidation**: Data consolidated from multiple yearly reports

## Source Information

- **Source**: Economic Intelligence Data Bank (EIDB)
- **URL**: https://tradestat.commerce.gov.in/eidb
- **Authority**: Ministry of Commerce & Industry, Government of India
- **Data Type**: Official government trade statistics

## Use Cases

✅ Trade analysis and forecasting  
✅ Commodity market research  
✅ Supply chain optimization  
✅ Export/import trend analysis  
✅ Competitive intelligence  
✅ Economic research and policy analysis  
✅ Business intelligence dashboards  

## Data Updates

New data is typically added by the EIDB annually:
- October: Full year data released
- Monthly: Partial updates available

To refresh data, re-run the scraper with latest HSN codes.

## File Size

- **Average file size**: 20-80 KB per HSN
- **Total dataset size**: ~500+ MB
- **Storage format**: JSON (text, compressible)

## Version Information

- **Schema Version**: 2.0
- **Last Updated**: 2026-01-27
- **Total HSN Codes**: 11,185+
- **Years Available**: 2018-2024

## Support & Issues

For data inconsistencies or access issues:
1. Verify source data at https://tradestat.commerce.gov.in/eidb
2. Check file encoding (UTF-8)
3. Validate JSON format with `jq` or online validators

## License

This data is sourced from Government of India official sources. Usage follows applicable government data policies and regulations.

---

**Last Generated**: 2026-01-27  
**Processing Time**: ~30-40 minutes (11,185 HSN codes × 2 trade types × 7 years)
