# Commodity-wise Export Page Reference

## URL
- **Base**: `https://tradestat.commerce.gov.in/eidb/commodity_wise_export`
- **Method**: POST

## Form Fields

| Field Name | Description | Values |
|------------|-------------|--------|
| `_token` | CSRF Token | Dynamic (must fetch from page) |
| `EidbYearCwe` | Year | 2024, 2023, 2022, 2021, 2020, 2019, 2018 |
| `comType` | Commodity type radio | `all` = All Commodity |
| `commodityType` | Commodity type radio | `specific` = Specific HSCode |
| `EidbComLevelCwe` | Digit level dropdown | 2, 4, 6, 8 |
| `Eidb_hscodeCwe` | HS Code input | 2-8 digit code |
| `Eidb_ReportCwe` | Values unit | 2=US $ Million, 1=₹ Crore, 3=Quantity |

## Validation Rules
- **Quantity (value=3)** is only available at **8-digit level**
- HS Code max length: 8 characters

## Result Table Columns
| Column | Description |
|--------|-------------|
| S.No. | Serial number |
| HSCode | HS code (2/4/6/8 digit) |
| Commodity | Commodity description |
| {Prev Year} | Previous year value |
| %Share | Percentage share (prev year) |
| {Current Year} | Current year value |
| %Share | Percentage share (current year) |
| %Growth | Year-over-year growth |

## Notes
- Also shows **India's Total Export** row at bottom
- Year format: Fiscal year (Apr-Mar), e.g., 2024-2025
- Data available: 2017-2018 to 2025-2026 (Apr-Aug)
