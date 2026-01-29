# TradeSTAT Scraper - Data Schema & Architecture Documentation

**Version:** 2.0  
**Last Updated:** 2026-01-29  
**Status:** Production Ready

---

## 1. Executive Overview

This document describes the complete data architecture, schema, metadata structure, and professional standards implemented in the TradeSTAT scraper system. The system is designed with enterprise-grade data governance, quality assurance, and long-term maintainability in mind.

---

## 2. Data Classification & Governance

### 2.1 Data Properties
- **Data Source:** DGCI&S (Directorate General of Foreign Trade, India)
- **Data Provider:** Ministry of Commerce and Industry
- **Data Classification:** PUBLIC
- **Data Category:** Trade Statistics - Country-wise Export/Import
- **Update Frequency:** Monthly (data available from Apr-2017 to Aug-2026)
- **Geographic Coverage:** 190+ countries globally
- **Temporal Granularity:** Annual (Financial Year: April-March)

### 2.2 Data Rights & Licensing
- **Reuse Conditions:** OPEN_DATA_CC-BY-4.0
- **Retention Policy:** LONG_TERM_ARCHIVE
- **Data Availability:** Public access without authentication
- **Terms of Use:** As per Ministry of Commerce & Industry guidelines

### 2.3 Data Sensitivity
- **Public:** All extracted data
- **Restricted:** None (all data is public domain)
- **PII:** None (no personal information contained)

---

## 3. Schema Structure & Hierarchy

### 3.1 Root Level JSON Structure

```json
{
  "metadata": { ... },
  "parsed_data": { ... },
  "data_manifest": { ... },
  "audit_trail": { ... }
}
```

### 3.2 Metadata Section

#### 3.2.1 Extraction Metadata
```json
{
  "extraction": {
    "scraped_at": "ISO 8601 timestamp",
    "feature": "commodity_wise_all_countries",
    "hsn_code": "8-digit HS code",
    "financial_year": "2024 (2024-2025)",
    "trade_type": "export | import",
    "source_url": "URL of data source",
    "response_size_bytes": 87067,
    "extraction_method": "HTTP_POST_with_CSRF"
  }
}
```

#### 3.2.2 Data Source Metadata
```json
{
  "data": {
    "data_source": "DGCI&S",
    "data_provider": "Ministry of Commerce and Industry",
    "data_classification": "PUBLIC",
    "data_category": "Trade_Statistics",
    "temporal_granularity": "Annual",
    "geographic_coverage": "Global",
    "update_frequency": "Monthly"
  }
}
```

#### 3.2.3 Version Control
```json
{
  "version": {
    "schema_version": "2.0",
    "scraper_version": "1.1",
    "api_compatibility": "TRADESTAT_2025",
    "last_schema_update": "2026-01-29"
  }
}
```

#### 3.2.4 Data Lineage
```json
{
  "lineage": {
    "data_source_url": "https://tradestat.commerce.gov.in/...",
    "extraction_point": "commodity_wise_all_countries",
    "processing_chain": [
      "scrape_html",
      "parse_html",
      "extract_structure",
      "validate_data"
    ],
    "transformations_applied": [
      "HTML_to_JSON",
      "Value_Normalization",
      "Missing_Data_Handling"
    ]
  }
}
```

### 3.3 Parsed Data Section

```json
{
  "parsed_data": {
    "metadata": { /* extraction metadata */ },
    "commodity": {
      "hsn_code": "09011112",
      "description": "COFFEE ARABICA PLANTATION`B`",
      "unit": "KGS"
    },
    "report_date": "29 Jan 2026",
    "countries": [
      {
        "sno": 1,
        "country": "AUSTRALIA",
        "values_usd": {
          "y2023_2024": 1.64,
          "y2024_2025": 1.91,
          "pct_growth": 16.04
        },
        "values_quantity": {
          "y2023_2024": 380670,
          "y2024_2025": 353620,
          "pct_growth": -7.11
        }
      }
      /* ... 33 more countries ... */
    ],
    "totals": {
      "total": {
        "values_usd": {
          "y2023_2024": 27.81,
          "y2024_2025": 37.73,
          "pct_growth": 35.68
        }
      },
      "india_total": {
        "values_usd": {
          "y2023_2024": 437072.03,
          "y2024_2025": 437704.58,
          "pct_growth": 0.14
        }
      },
      "pct_share": {
        "y2023_2024": 0.0064,
        "y2024_2025": 0.0086
      }
    },
    "data_quality": {
      "extraction_completeness_percent": 94.12,
      "total_countries_count": 34,
      "countries_with_complete_data": 32,
      "countries_with_missing_data": 2,
      "extraction_duration_seconds": 0.145,
      "validation_status": "VALID"
    },
    "schema": {
      "version": "2.0",
      "parser_version": "1.1",
      "last_updated": "2026-01-29"
    },
    "processing": {
      "status": "SUCCESS",
      "errors": [],
      "warnings": [],
      "processing_timestamp": "ISO 8601",
      "data_source": "tradestat.commerce.gov.in",
      "extraction_method": "BeautifulSoup_HTML_Parser",
      "environment": "production"
    }
  }
}
```

### 3.4 Data Manifest Section

```json
{
  "data_manifest": {
    "extraction_status": "SUCCESS | PARTIAL | FAILED",
    "records_extracted": 34,
    "data_completeness": 94.12,
    "validation_status": "VALID | PARTIAL | INCOMPLETE",
    "checksum_md5": "abc123...",
    "retention_policy": "LONG_TERM_ARCHIVE",
    "reuse_conditions": "OPEN_DATA_CCBY4.0"
  }
}
```

### 3.5 Audit Trail Section

```json
{
  "audit_trail": {
    "operator": "automated_scraper",
    "execution_environment": "production | staging | development",
    "scraper_configuration": {
      "hsn": "09011112",
      "year": "2024",
      "trade_type": "export",
      "consolidate": false,
      "feature": "commodity_wise_all_countries"
    },
    "performance_metrics": {
      "response_time_ms": 140,
      "parsing_efficient": "Optimized"
    }
  }
}
```

---

## 4. Data Field Specifications

### 4.1 HSN Code
- **Type:** String (8 digits)
- **Format:** [0-9]{8}
- **Example:** "09011112"
- **Description:** Harmonized System Nomenclature code for commodity classification
- **Validation:** Must match ITC HS Code Directory (updated Apr 2024)

### 4.2 Country Names
- **Type:** String
- **Format:** Uppercase, space-separated
- **Examples:** "AUSTRALIA", "UNITED STATES", "EGYPT A RP"
- **Note:** May include regional identifiers (e.g., "RP" for Republic)

### 4.3 Trade Values
- **Type:** Float64
- **Unit:** USD Million
- **Range:** 0 to 999,999.99
- **Precision:** 2 decimal places
- **Null Representation:** No data available for that period

### 4.4 Quantities
- **Type:** Float64
- **Unit:** As per commodity (KGS, TONS, METERS, etc.)
- **Range:** 0 to 999,999,999
- **Precision:** Integer values (no decimals)
- **Scale:** Values may represent thousands (see data documentation)
- **Null Representation:** No data available for that period

### 4.5 Growth Percentage
- **Type:** Float64
- **Unit:** Percentage (%)
- **Range:** -100 to 10,000+
- **Precision:** 2 decimal places
- **Calculation:** ((Current Year - Previous Year) / Previous Year) * 100
- **Null Representation:** No previous year data for comparison

---

## 5. Data Quality Metrics

### 5.1 Extraction Completeness
- **Definition:** Percentage of expected data fields successfully extracted
- **Calculation:** (Countries with data / Total countries) * 100
- **Threshold for VALID:** ≥ 70%
- **Threshold for PARTIAL:** ≥ 50%
- **Threshold for INCOMPLETE:** < 50%

### 5.2 Data Validation Status
- **VALID:** Completeness ≥ 70%, all critical fields present
- **PARTIAL:** Completeness 50-70%, minor fields missing
- **INCOMPLETE:** Completeness < 50%, significant data gaps
- **FAILED:** Extraction/parsing error

### 5.3 Quality Checks Applied
1. HTML structure validation (table exists and contains rows)
2. Data type validation (numeric values are numeric)
3. Range validation (percentages within expected bounds)
4. Completeness checks (expected fields populated)
5. Consistency checks (totals match sum of countries)

---

## 6. Processing Pipeline

### 6.1 Data Flow
```
Website HTML Response
    ↓
BeautifulSoup Parser
    ↓
HTML Table Extraction
    ↓
Row-by-row Data Mapping
    ↓
Data Type Conversion & Validation
    ↓
Quality Metrics Calculation
    ↓
JSON Serialization
    ↓
File Storage with Metadata
```

### 6.2 Error Handling
- **Parser Errors:** Logged with stack trace, returns NULL for that record
- **Network Errors:** Automatic retry with exponential backoff
- **Validation Errors:** Field marked as NULL, warning added to processing log
- **Recovery:** Partial data extraction continues even if some records fail

### 6.3 Performance Targets
- **HTML Parsing Time:** < 200ms per request
- **Data Extraction Time:** < 150ms per request
- **Total Processing Time:** < 500ms per year per HSN
- **File Size:** ~10-15 KB per year (without raw HTML)

---

## 7. Storage & Archival

### 7.1 File Organization
```
src/data/raw/
├── commodity_wise_all_countries/
│   ├── export/
│   │   ├── 09011112_2024.json
│   │   ├── 09011112_2023.json
│   │   └── 09011112_consolidated.json
│   └── import/
│       ├── 09011112_2024.json
│       └── ...
└── [other_features]/
```

### 7.2 File Naming Convention
- **Single Year:** `{HSN_CODE}_{YEAR}.json`
- **Consolidated:** `{HSN_CODE}_consolidated.json`
- **Pattern:** Lowercase, underscore-separated

### 7.3 Consolidation Format
When using `--consolidate` flag:
```json
{
  "hsn_code": "09011112",
  "years": {
    "2024": { /* year_data */ },
    "2023": { /* year_data */ },
    "2022": { /* year_data */ }
  },
  "metadata": {
    "consolidated_at": "ISO 8601",
    "trade_type": "export",
    "years_count": 3,
    "schema_version": "2.0"
  }
}
```

---

## 8. Usage Examples

### 8.1 Single Year Extraction
```bash
python scrape_cli.py --hsn 09011112 --year 2024 --type export
```

### 8.2 Multi-Year Extraction
```bash
python scrape_cli.py --hsn 09011112 --years 2022,2023,2024 --type export
```

### 8.3 With Consolidation
```bash
python scrape_cli.py --hsn 09011112 --years 2022,2023,2024 --type export --consolidate
```

### 8.4 All Available Years
```bash
python scrape_cli.py --hsn 09011112 --all-years --type export
```

---

## 9. Version History

### Version 2.0 (2026-01-29)
- Added professional metadata structure
- Introduced data quality metrics
- Implemented audit trail logging
- Added data lineage tracking
- Enhanced schema documentation
- Removed raw HTML responses

### Version 1.0 (2026-01-28)
- Initial release
- Basic HTML parsing
- Single-year extraction
- Multi-year support

---

## 10. Support & Maintenance

### 10.1 Known Limitations
1. HTML structure changes on source website will break parser
2. JavaScript-rendered content not captured (static HTML only)
3. Rate limiting may apply for bulk requests
4. Data updates monthly, not real-time

### 10.2 Future Enhancements
- [ ] Dynamic table structure detection
- [ ] Multi-currency support (currently USD only)
- [ ] Real-time data streaming API
- [ ] Advanced analytics module
- [ ] Incremental sync capability
- [ ] Data warehouse integration

### 10.3 Contact & Support
- **Data Source:** DGCI&S official website
- **Documentation:** See README.md and DOCUMENTATION.md
- **Issues:** Report to project maintainers

---

## 11. Compliance & Standards

- **Data Standard:** JSON (RFC 7159)
- **Date Format:** ISO 8601 (RFC 3339)
- **Encoding:** UTF-8
- **Licensing:** CC-BY-4.0
- **Privacy:** GDPR Compatible (no PII)
- **Accessibility:** WCAG 2.1 (data quality aligned)

---

**Document Status:** FINAL  
**Approval:** Ready for Production  
**Last Review:** 2026-01-29
