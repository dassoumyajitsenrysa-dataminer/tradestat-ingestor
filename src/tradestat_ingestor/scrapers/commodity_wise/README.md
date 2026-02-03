# Commodity-wise Scraper

## Overview

This scraper extracts **commodity-wise trade data** from India's official trade statistics portal ([tradestat.commerce.gov.in](https://tradestat.commerce.gov.in)). It fetches export and import data for specific HS (Harmonized System) codes, providing trade values, market share percentages, and year-over-year growth rates.

### How It Works

1. **Session Bootstrap**: Establishes a session with the TradeStat portal and retrieves a CSRF token for authentication.
2. **Form Submission**: Submits a POST request mimicking the web form with parameters like HS code, year, trade type, and value unit.
3. **HTML Parsing**: Parses the returned HTML table using BeautifulSoup to extract structured data.
4. **JSON Output**: Saves the extracted data as JSON with comprehensive metadata including data quality metrics, lineage information, and audit trail.

### Data Source

- **Provider**: DGCI&S (Directorate General of Commercial Intelligence and Statistics), Kolkata
- **Ministry**: Ministry of Commerce and Industry, Government of India
- **Coverage**: 2017-2018 to 2025-2026 (financial years)
- **Update Frequency**: Monthly

---

## Basic Usage
```bash
python scrape_commodity_wise.py --hscode <code> --year <year> --type <export|import>
```

---

## Scenarios

### 1. By Trade Type

**Export Data**
```bash
python scrape_commodity_wise.py --hscode 27 --year 2024 --type export
```

**Import Data**
```bash
python scrape_commodity_wise.py --hscode 27 --year 2024 --type import
```

---

### 2. By HS Code Digit Level

**2-digit (Chapter)**
```bash
python scrape_commodity_wise.py --hscode 27 --year 2024 --type export
```

**4-digit (Heading)**
```bash
python scrape_commodity_wise.py --hscode 2701 --year 2024 --type export
```

**6-digit (Sub-heading)**
```bash
python scrape_commodity_wise.py --hscode 271019 --year 2024 --type export
```

**8-digit (Tariff Item)**
```bash
python scrape_commodity_wise.py --hscode 27101944 --year 2024 --type export
```

---

### 3. By Value Type

**US $ Million (default)**
```bash
python scrape_commodity_wise.py --hscode 27 --year 2024 --type export --value-type usd
```

**₹ Crore**
```bash
python scrape_commodity_wise.py --hscode 27 --year 2024 --type export --value-type inr
```

**Quantity (8-digit only)**
```bash
python scrape_commodity_wise.py --hscode 27101944 --year 2024 --type export --value-type quantity
```

---

### 4. By Year Selection

**Single Year**
```bash
python scrape_commodity_wise.py --hscode 27 --year 2024 --type export
```

**Multiple Years (comma-separated)**
```bash
python scrape_commodity_wise.py --hscode 27 --years 2022,2023,2024 --type export
```

**All Available Years (2018-2024)**
```bash
python scrape_commodity_wise.py --hscode 27 --all-years --type export
```

---

### 5. All Commodities at Digit Level

**All 2-digit commodities**
```bash
python scrape_commodity_wise.py --all --digit-level 2 --year 2024 --type export
```

**All 4-digit commodities**
```bash
python scrape_commodity_wise.py --all --digit-level 4 --year 2024 --type export
```

---

## Output Location
```
src/data/raw/commodity_wise/
├── export/
│   ├── 27_2024_usd.json
│   ├── 27101944_2024_quantity.json
│   └── ...
└── import/
    ├── 27_2024_usd.json
    └── ...
```

---

## Available Options

| Option | Values | Description |
|--------|--------|-------------|
| `--hscode` | 2-8 digit code | Specific HS code to scrape |
| `--all` | flag | Scrape all commodities at digit level |
| `--digit-level` | 2, 4, 6, 8 | Required with `--all` |
| `--year` | 2018-2024 | Single year |
| `--years` | comma-separated | Multiple years |
| `--all-years` | flag | All available years |
| `--type` | export, import | Trade type (default: export) |
| `--value-type` | usd, inr, quantity | Value unit (default: usd) |

> **Note:** `--value-type quantity` only works with 8-digit HS codes.
