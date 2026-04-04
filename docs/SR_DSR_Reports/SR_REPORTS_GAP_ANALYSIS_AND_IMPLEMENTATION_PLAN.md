# SR Reports Gap Analysis & Implementation Plan

> **Source:** `Sales March-25.xlsx` — 30 sheets covering Juice, Wonder, Ketchup, Milk Men, Danish, Gems, Treat product groups  
> **Analyzed:** 2026-04-01  
> **System:** Shoudagor Fullstack (FastAPI + React/TypeScript)

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Excel File Structure Overview](#2-excel-file-structure-overview)
3. [Existing Implementation Assessment](#3-existing-implementation-assessment)
4. [Detailed Gap Analysis by Report Type](#4-detailed-gap-analysis-by-report-type)
   - [4.1 Group Reports (Product Group Sales/Stock/Return)](#41-group-reports-product-group-salesstockreturn)
   - [4.2 Undelivery Reports (Date-wise DO Tracking)](#42-undelivery-reports-date-wise-do-tracking)
   - [4.3 Damage Reports (Product Damage per Date)](#43-damage-reports-product-damage-per-date)
   - [4.4 Cost & Profit Report (Daily Expense Breakdown)](#44-cost--profit-report-daily-expense-breakdown)
   - [4.5 Daily Report (Group-wise Sales & DO Cash)](#45-daily-report-group-wise-sales--do-cash)
   - [4.6 SR Program Reconciliation (SR vs Khata)](#46-sr-program-reconciliation-sr-vs-khata)
   - [4.7 DO Tracking Report (Delivery Order Detail)](#47-do-tracking-report-delivery-order-detail)
   - [4.8 Slow Moving Product Report](#48-slow-moving-product-report)
5. [Database Schema Changes Required](#5-database-schema-changes-required)
6. [Backend Implementation Plan](#6-backend-implementation-plan)
7. [Frontend Implementation Plan](#7-frontend-implementation-plan)
8. [Implementation Phases & Timeline](#8-implementation-phases--timeline)
9. [Technical Decisions & Tradeoffs](#9-technical-decisions--tradeoffs)
10. [Risk Assessment](#10-risk-assessment)

---

## 1. Executive Summary

The Excel file represents a **real-world distributor's operational reporting system** for Pran product distribution in Bangladesh. It tracks 7 product groups (Juice, Wonder/Rocker, Ketchup, Milk Men, Danish, Gems, Treat) across 3 report dimensions each (Group, Undelivery, Damage), plus financial reconciliation reports.

| Metric | Count |
|--------|-------|
| Total Excel Sheets | 30 |
| Product Groups Tracked | 7 |
| Distinct Report Types | 8 |
| Fully Implemented | 2 (SR Program Workflow, SR Summary) |
| Partially Implemented | 2 (Undelivery, DO Cash) |
| **NOT Implemented** | **6** |
| Estimated Backend Endpoints Needed | ~25 |
| Estimated Frontend Pages Needed | ~10 |
| Estimated Database Tables Needed | 3-4 |

---

## 2. Excel File Structure Overview

### Sheet Inventory

| Sheet Name | Report Type | Rows | Cols | Purpose |
|------------|-------------|------|------|---------|
| **Juice Group** | Group Report | 1000 | 247 | Per-product daily sales/stock/return for Juice group |
| **Juice Undelivery** | Undelivery Report | 1000 | 303 | Date-wise undelivered DOs for Juice group |
| **Juice Damage** | Damage Report | 1000 | 85 | Product damage tracking for Juice group |
| **Wonder Group** | Group Report | 1000 | 265 | Per-product daily sales/stock/return for Wonder/Rocker group |
| **Wonder Undelivery** | Undelivery Report | 1000 | 364 | Date-wise undelivered DOs for Wonder group |
| **Wonder Damage** | Damage Report | 1000 | 84 | Product damage tracking for Wonder group |
| **Ketchup Group** | Group Report | 122 | 266 | Per-product daily sales/stock/return for Ketchup group |
| **Ketchup Undelivery** | Undelivery Report | 81 | 392 | Date-wise undelivered DOs for Ketchup group |
| **Katchap Damage** | Damage Report | 1000 | 84 | Product damage tracking for Ketchup group |
| **Milk Men Group** | Group Report | 1000 | 243 | Per-product daily sales/stock/return for Milk Men group |
| **Milk Men Undelivery** | Undelivery Report | 1000 | 261 | Date-wise undelivered DOs for Milk Men group |
| **Milk Men Damage** | Damage Report | 1000 | 105 | Product damage tracking for Milk Men group |
| **Danish Group** | Group Report | 1000 | 241 | Per-product daily sales/stock/return for Danish group |
| **Danish Damage** | Damage Report | 1000 | 86 | Product damage tracking for Danish group |
| **Danish Undelivery** | Undelivery Report | 79 | 92 | Date-wise undelivered DOs for Danish group |
| **Gems Group** | Group Report | 1000 | 241 | Per-product daily sales/stock/return for Gems group |
| **Gems Undelivery** | Undelivery Report | 87 | 409 | Date-wise undelivered DOs for Gems group |
| **Gems Damage** | Damage Report | 1000 | 84 | Product damage tracking for Gems group |
| **Treat Group** | Group Report | 1000 | 245 | Per-product daily sales/stock/return for Treat group |
| **Treat Undelivery** | Undelivery Report | 90 | 371 | Date-wise undelivered DOs for Treat group |
| **Treat Damage** | Damage Report | 1000 | 90 | Product damage tracking for Treat group |
| **Cost & Profit** | Financial Report | 135 | 35 | Daily cost breakdown + profit per group |
| **Daily Report** | Daily Summary | 1000 | 106 | Group-wise daily sales, commission, DO cash, balance |
| **SR Proggram** | Reconciliation | 105 | 36 | SR report vs Khata difference tracking |
| **Record** | Reference | 219 | 23 | Historical date records |
| **Sheet1** | DO Tracking | 1000 | 26 | Delivery Order detail (DO number, product, qty, date) |
| **Sheet2** | Slow Moving | 1000 | 46 | Slow-moving product identification |
| **DPS** | Personal Finance | 152 | 17 | Bank DPS tracking (not business-related) |
| **Gari maintanence** | Vehicle Cost | 1000 | 9 | Vehicle (Gari) maintenance cost log |

---

## 3. Existing Implementation Assessment

### Currently Implemented Features

| Feature | Location | Status | Coverage |
|---------|----------|--------|----------|
| **SR Performance Summary** | `/reports/sr` | ✅ Complete | Per-SR P&L with drill-down to product-variant and customer level |
| **SR Program Workflow** | `/reports/sr-program` | ✅ Complete | 6 blocks: Financials, Channel Split, Projection, DO Cash, Undelivery, Growth |
| **SR Program Channel Admin** | `/reports/sr-program/admin` | ✅ Complete | Channel CRUD + customer mapping |
| **10 Sales Analytics Reports** | `/reports/sales/*` | ✅ Complete | Fulfillment, Profitability, Team Analytics, etc. |
| **DSR Loading Reports** | `/reports/dsr` | ✅ Complete | DSR summary, loading, SO breakdown |
| **Group-level Undelivery** | Backend `get_undelivery()` | ⚠️ Partial | Aggregated by group, NOT date-wise |
| **Group-level DO Cash** | Backend `get_do_cash()` | ⚠️ Partial | Aggregated by group, NOT date-wise |

### Backend SR Program Repository (`sr_program_reports.py`)

| Method | Purpose | Status |
|--------|---------|--------|
| `get_group_financials()` | Commission + Market Credit per group | ✅ Implemented |
| `get_channel_split()` | Sales by channel per group | ✅ Implemented |
| `get_sales_projection()` | Avg/day × full month projection | ✅ Implemented |
| `get_do_cash()` | Payment collected per group | ✅ Implemented (aggregated) |
| `get_undelivery()` | Unshipped qty per group | ✅ Implemented (aggregated) |
| `get_growth_comparison()` | YoY growth per group | ✅ Implemented |
| Channel CRUD | Channel management | ✅ Implemented |
| Customer mapping | Customer→Channel mapping | ✅ Implemented |

---

## 4. Detailed Gap Analysis by Report Type

### 4.1 Group Reports (Product Group Sales/Stock/Return)

**Excel Sheets:** Juice Group, Wonder Group, Ketchup Group, Milk Men Group, Danish Group, Gems Group, Treat Group

#### Excel Column Structure (per sheet)

```
| Sl No | Product Name | Ctn Factor | DP/P | TP/P | Dealer % | Stock | Value |
```
Followed by **31 day-columns** (one per day of month), each containing:
```
| Product In | Sumary | Return | Sales | Original Value | Sales Value | Total |
```
Plus summary columns:
```
| Total Sales | Sales Value | Total Return | Return Value | Final Stock | Final Stock Value |
| DP | DO | SALES | STOCK |
```

#### What Each Column Means

| Column | Meaning | Example |
|--------|---------|---------|
| **Sl No** | Serial number | 1, 2, 3... |
| **Product Name** | Product identifier | "White Mango-125", "Mango Juice-200" |
| **Ctn Factor** | Units per carton | 80, 48, 24, 12 |
| **DP/P** | Dealer Price per piece | 8.613, 14.174, 17.6 |
| **TP/P** | Trade Price per piece | 9.13, 15.1, 18.7 |
| **Dealer %** | Dealer margin = TP/DP - 100% | ~6% |
| **Stock** | Opening stock quantity | 3512, 0, 1072 |
| **Value** | Stock × DP | = Stock × DP/P |
| **Product In** | Stock received that day | 304, 240, 56... |
| **Return** | Stock returned that day | usually 0 or small |
| **Sales** | Units sold that day | = Product In - Return |
| **Original Value** | Sales × DP | = Sales × DP/P |
| **Sales Value** | Sales × TP | = Sales × TP/P |
| **Total** | Running balance | = Previous + Product In - Return - Sales |

#### Gap Assessment

| Requirement | Current State | Gap |
|-------------|---------------|-----|
| Per-product daily tracking | No daily product-level tracking exists | ❌ Full gap |
| Ctn Factor (carton conversion) | Not stored or tracked | ❌ Full gap |
| Dealer Price (DP/P) | `damage_price` exists on ProductPrice but not DP | ❌ Full gap |
| Trade Price (TP/P) | `sale_price` exists but not as TP concept | ❌ Full gap |
| Dealer margin % | Not calculated | ❌ Full gap |
| Daily Product In | No daily inflow tracking | ❌ Full gap |
| Daily Return per product | Returns tracked on orders, not daily summary | ❌ Full gap |
| Daily Sales per product | Sales exist but not daily per-product summary | ❌ Full gap |
| Original Value vs Sales Value | No dual-value tracking | ❌ Full gap |
| Product group filtering | Variant groups exist but not used for this report | ⚠️ Partial |

#### What Needs to Be Built

1. **New data model** for daily product movement tracking OR complex aggregation from existing tables
2. **New pricing fields** on ProductPrice model (dealer_price, trade_price)
3. **Carton factor** field on Product/Variant model
4. **Backend endpoint** for group report with date range, group filter
5. **Frontend page** with spreadsheet-like table view, date range picker, group selector

---

### 4.2 Undelivery Reports (Date-wise DO Tracking)

**Excel Sheets:** Juice Undelivery, Wonder Undelivery, Ketchup Undelivery, Milk Men Undelivery, Danish Undelivery, Gems Undelivery, Treat Undelivery

#### Excel Column Structure

```
| Sl No | Product Name | Ctn Factor | DP/P |
```
Followed by **date-columns** (each date in the month), each containing:
```
| Total | DO (Delivery Order) | Total | Delivery | Total | DO | Total | Delivery |
```

The pattern alternates between:
- **DO column**: Delivery Order quantity issued for that date
- **Delivery column**: Actual delivery quantity for that date
- **Total columns**: Running totals

#### Gap Assessment

| Requirement | Current State | Gap |
|-------------|---------------|-----|
| Date-wise undelivery | Only group-aggregated exists | ❌ Needs date-level breakdown |
| DO (Delivery Order) tracking | No DO concept in current system | ❌ Full gap |
| DO vs Delivery comparison | No comparison exists | ❌ Full gap |
| Per-product undelivery | Only per-group exists | ❌ Full gap |
| Per-product-group undelivery | ✅ `get_undelivery()` exists | ✅ Partially covered |

#### What Needs to Be Built

1. **DO (Delivery Order) concept** — either map to existing SalesOrder or create new entity
2. **Date-wise undelivery query** — enhance existing `get_undelivery()` to return per-date data
3. **Per-product undelivery** — add product/variant dimension to undelivery query
4. **Frontend enhancement** — add date-wise table view to existing SR Program Undelivery section

---

### 4.3 Damage Reports (Product Damage per Date)

**Excel Sheets:** Juice Damage, Wonder Damage, Katchap Damage, Milk Men Damage, Danish Damage, Gems Damage, Treat Damage

#### Excel Column Structure

```
| Sl No | Product Name | Ctn Factor | DP/P | Final | Value | Total |
```
Followed by **date-columns** (each date), each containing:
```
| Quantity | Value |
```

#### Gap Assessment

| Requirement | Current State | Gap |
|-------------|---------------|-----|
| Damage quantity tracking | No damage quantity field exists anywhere | ❌ Full gap |
| Per-product damage | Not tracked | ❌ Full gap |
| Per-date damage | Not tracked | ❌ Full gap |
| Per-group damage | Not tracked | ❌ Full gap |
| Damage value calculation | Not calculated | ❌ Full gap |

#### What Needs to Be Built

1. **New database model**: `ProductDamage` or add `damage_quantity` to existing order detail
2. **Damage recording API**: Endpoint to record damage per product per date
3. **Damage report query**: Aggregate damage by product, group, date
4. **Frontend page**: Damage report with date-wise table, group filter

---

### 4.4 Cost & Profit Report (Daily Expense Breakdown)

**Excel Sheet:** Cost & Profit (135 rows, 35 columns)

#### Excel Column Structure

**Left side — DO REPORT (Daily Cost):**
```
| Day | Date | Jush Group | Rocker Group | Katchup | Milk Men | Danish | Gems | Treat | Total |
| Oil | VAN Cost | Other | Total (cost) | Labour | Shaju | Basher | SELF | Office |
```

**Right side — Profit:**
```
| Date | Jush Profit | Rocker Profit | Ketchup Profit | Milk | Danish | Gems | Treat Profit | Total | Balance Profit |
```

#### What Each Section Means

| Section | Columns | Purpose |
|---------|---------|---------|
| **DO REPORT** | Group-wise daily DO values | Revenue per group per day |
| **Cost Breakdown** | Oil, VAN Cost, Other, Total, Labour (Shaju, Basher, SELF), Office | Daily operational costs |
| **Profit** | Per-group profit, Total profit, Balance profit | Profit = Revenue - Costs per group |

#### Gap Assessment

| Requirement | Current State | Gap |
|-------------|---------------|-----|
| Daily cost per group | Expense model exists but not group-tagged | ❌ Full gap |
| VAN Cost tracking | No vehicle cost model | ❌ Full gap |
| Labour cost tracking | No labour cost model | ❌ Full gap |
| Oil/Fuel cost | Not tracked | ❌ Full gap |
| Office expense by group | Expense model exists, not group-tagged | ⚠️ Partial |
| Per-group profit calculation | SR Program has commission/market credit | ⚠️ Partial |
| Balance profit (running) | Not tracked | ❌ Full gap |

#### What Needs to Be Built

1. **Enhance Expense model** — add `variant_group_id` for group tagging
2. **New model**: `VehicleExpense` (VAN Cost, Oil, Maintenance)
3. **New model**: `LabourExpense` (worker payments per day)
4. **Backend endpoint**: Daily cost & profit aggregation by group
5. **Frontend page**: Cost & Profit dashboard with daily table, group columns, cost breakdown

---

### 4.5 Daily Report (Group-wise Sales & DO Cash)

**Excel Sheet:** Daily Report (1000 rows, 106 columns)

#### Excel Column Structure

For each of 7 product groups:
```
| Group Sales | Group Original Sales | Commission | Market Credit | Damage Collection | Due Paid | Group DO Cash |
```

Plus summary section:
```
| Cash | Balance | Cost | Sales | DO Cash | HOUSE | INVEST |
| Total Sales | Sales Budget | % achievement | EXTRA | TOTAL |
```

#### What Each Column Means

| Column | Meaning |
|--------|---------|
| **Group Sales** | Actual sales value for the group that day |
| **Group Original Sales** | Original/standard sales value (before adjustments) |
| **Commission** | SR commission earned for that group |
| **Market Credit** | Customer store credit / market credit |
| **Damage Collection** | Revenue recovered from damaged goods |
| **Due Paid** | Previous dues collected that day |
| **Group DO Cash** | Cash collected from DOs for that group |
| **Balance** | Running balance |
| **Cost** | Total daily costs |
| **% achievement** | Sales vs Budget percentage |

#### Gap Assessment

| Requirement | Current State | Gap |
|-------------|---------------|-----|
| Daily group-wise sales | Can be aggregated from SalesOrder | ⚠️ Needs query |
| Daily commission | SR order has commission_amount | ⚠️ Needs daily aggregation |
| Damage collection | No damage model exists | ❌ Full gap |
| Due paid tracking | Customer has balance_amount | ⚠️ Needs daily tracking |
| DO Cash per group per day | DO Cash exists but not daily | ❌ Needs date breakdown |
| Sales vs Budget | No budget concept | ❌ Full gap |
| % achievement | Not calculated | ❌ Full gap |

#### What Needs to Be Built

1. **Backend endpoint**: Daily report aggregation by group with all financial columns
2. **Budget model**: Monthly/daily sales budget per group
3. **Frontend page**: Daily report dashboard with group columns, date navigation

---

### 4.6 SR Program Reconciliation (SR vs Khata)

**Excel Sheet:** SR Proggram (105 rows, 36 columns)

#### Excel Column Structure

```
| Date | SR Report-Order | In Khata-Order | Difference | SR Report-Sales | In Khata-Sales | Difference |
```

#### What Each Column Means

| Column | Meaning |
|--------|---------|
| **Date** | Day number (1, 2, 3...) |
| **SR Report-Order** | Orders reported by SRs |
| **In Khata-Order** | Orders recorded in ledger (khata/book) |
| **Difference** | SR Report - Khata (discrepancy) |
| **SR Report-Sales** | Sales reported by SRs |
| **In Khata-Sales** | Sales recorded in ledger |
| **Difference** | SR Sales - Khata Sales (discrepancy) |

#### Gap Assessment

| Requirement | Current State | Gap |
|-------------|---------------|-----|
| SR order tracking | SR_Order model exists | ✅ Covered |
| Khata (ledger) tracking | No separate ledger system | ❌ Full gap |
| Reconciliation/difference | No reconciliation feature | ❌ Full gap |
| SR sales tracking | SR order details exist | ✅ Covered |

#### What Needs to Be Built

1. **New model**: `SalesLedger` (khata entries — manual book entries)
2. **Reconciliation endpoint**: Compare SR orders vs ledger entries
3. **Frontend page**: Reconciliation table with difference highlighting

---

### 4.7 DO Tracking Report (Delivery Order Detail)

**Excel Sheet:** Sheet1 (1000 rows, 26 columns)

#### Excel Column Structure

```
| DO Number | Date | Product Code | Product Name | Quantity | Unit Price | Total Value | Month |
```

#### Gap Assessment

| Requirement | Current State | Gap |
|-------------|---------------|-----|
| DO Number tracking | No DO number concept | ❌ Full gap |
| DO detail per product | SalesOrderDetail exists | ⚠️ Partial |
| DO date tracking | Order date exists | ✅ Covered |

#### What Needs to Be Built

1. **Add DO number field** to SalesOrder model
2. **DO tracking endpoint**: List DOs with product details
3. **Frontend page**: DO tracking table with search/filter

---

### 4.8 Slow Moving Product Report

**Excel Sheet:** Sheet2 (1000 rows, 46 columns)

#### Excel Column Structure

```
| Sl No | Product Name | Ctn Factor | DP/P | TP/P | Dealer % | Carton TP |
| Product Name | Rate | Quantity | Web Entry | Note |
| Full Month Sales | Full Month Sales Value | Till Stock | Till Stock Value |
```

#### Gap Assessment

| Requirement | Current State | Gap |
|-------------|---------------|-----|
| Slow-moving identification | Dead stock report exists | ⚠️ Partial |
| Full month sales value | Can be aggregated | ⚠️ Needs query |
| Till stock value | Inventory stock exists | ⚠️ Needs query |
| Web Entry tracking | No web entry concept | ❌ Full gap |

#### What Needs to Be Built

1. **Backend endpoint**: Slow-moving product analysis (sales velocity + stock)
2. **Frontend page**: Slow-moving product table with sales vs stock comparison

---

## 5. Database Schema Changes Required

### 5.1 New Tables

#### `inventory.product_damage`
Tracks product damage/loss per date per product.

```sql
CREATE TABLE inventory.product_damage (
    damage_id SERIAL PRIMARY KEY,
    company_id INT NOT NULL REFERENCES security.app_client_company(company_id),
    product_id INT REFERENCES inventory.product(product_id),
    variant_id INT REFERENCES inventory.product_variant(variant_id),
    damage_date DATE NOT NULL,
    quantity NUMERIC(12, 3) NOT NULL DEFAULT 0,
    unit_cost NUMERIC(12, 2),
    total_value NUMERIC(14, 2),
    reason VARCHAR(100),  -- 'expired', 'broken', 'spoiled', 'other'
    notes TEXT,
    cb INT, cd TIMESTAMP, mb INT, md TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE
);
```

#### `reports.daily_cost_expense`
Daily operational cost tracking by group.

```sql
CREATE TABLE reports.daily_cost_expense (
    cost_id SERIAL PRIMARY KEY,
    company_id INT NOT NULL,
    expense_date DATE NOT NULL,
    variant_group_id INT REFERENCES inventory.variant_group(variant_group_id),
    van_cost NUMERIC(14, 2) DEFAULT 0,
    oil_cost NUMERIC(14, 2) DEFAULT 0,
    labour_cost NUMERIC(14, 2) DEFAULT 0,
    office_cost NUMERIC(14, 2) DEFAULT 0,
    other_cost NUMERIC(14, 2) DEFAULT 0,
    total_cost NUMERIC(14, 2),
    notes TEXT,
    cb INT, cd TIMESTAMP, mb INT, md TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE
);
```

#### `reports.sales_ledger` (Khata)
Manual ledger entries for reconciliation.

```sql
CREATE TABLE reports.sales_ledger (
    ledger_id SERIAL PRIMARY KEY,
    company_id INT NOT NULL,
    entry_date DATE NOT NULL,
    entry_type VARCHAR(20),  -- 'order', 'sales', 'payment', 'return'
    variant_group_id INT,
    customer_id INT,
    order_amount NUMERIC(14, 2),
    sales_amount NUMERIC(14, 2),
    payment_amount NUMERIC(14, 2),
    reference_type VARCHAR(20),  -- 'sr_order', 'sales_order'
    reference_id INT,
    notes TEXT,
    cb INT, cd TIMESTAMP, mb INT, md TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE
);
```

#### `reports.sales_budget`
Monthly/daily sales budget per group.

```sql
CREATE TABLE reports.sales_budget (
    budget_id SERIAL PRIMARY KEY,
    company_id INT NOT NULL,
    variant_group_id INT REFERENCES inventory.variant_group(variant_group_id),
    budget_month DATE NOT NULL,  -- first day of month
    budget_amount NUMERIC(14, 2) NOT NULL,
    cb INT, cd TIMESTAMP, mb INT, md TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE,
    UNIQUE(company_id, variant_group_id, budget_month)
);
```

### 5.2 Existing Table Modifications

#### `inventory.product_price` — Add pricing fields
```sql
ALTER TABLE inventory.product_price
ADD COLUMN IF NOT EXISTS dealer_price NUMERIC(12, 2),
ADD COLUMN IF NOT EXISTS trade_price NUMERIC(12, 2);
```

#### `inventory.product_variant` — Add carton factor
```sql
ALTER TABLE inventory.product_variant
ADD COLUMN IF NOT EXISTS carton_factor INT DEFAULT 1;
```

#### `sales.sales_order` — Add DO number
```sql
ALTER TABLE sales.sales_order
ADD COLUMN IF NOT EXISTS do_number VARCHAR(50);
```

#### `inventory.expenses` — Add variant group tag
```sql
ALTER TABLE inventory.expenses
ADD COLUMN IF NOT EXISTS variant_group_id INT REFERENCES inventory.variant_group(variant_group_id);
```

---

## 6. Backend Implementation Plan

### 6.1 New Repository Files

| File | Purpose | Methods |
|------|---------|---------|
| `app/repositories/reports/group_reports.py` | Group report queries | `get_group_report()`, `get_product_daily_movement()` |
| `app/repositories/reports/damage_reports.py` | Damage report queries | `get_damage_report()`, `get_damage_by_group()` |
| `app/repositories/reports/daily_cost_reports.py` | Cost & profit queries | `get_daily_cost()`, `get_daily_profit()`, `get_cost_breakdown()` |
| `app/repositories/reports/daily_reports.py` | Daily summary queries | `get_daily_report()`, `get_group_daily_summary()` |
| `app/repositories/reports/reconciliation_reports.py` | SR vs Khata queries | `get_reconciliation()`, `get_sr_vs_ledger()` |
| `app/repositories/reports/do_tracking_reports.py` | DO tracking queries | `get_do_list()`, `get_do_details()` |
| `app/repositories/reports/slow_moving_reports.py` | Slow-moving queries | `get_slow_moving_products()` |

### 6.2 New Service Files

| File | Purpose |
|------|---------|
| `app/services/reports/group_report_service.py` | Group report business logic |
| `app/services/reports/damage_report_service.py` | Damage report business logic |
| `app/services/reports/daily_cost_service.py` | Cost & profit business logic |
| `app/services/reports/daily_report_service.py` | Daily report business logic |
| `app/services/reports/reconciliation_service.py` | SR vs Khata reconciliation |
| `app/services/reports/do_tracking_service.py` | DO tracking business logic |

### 6.3 New API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `GET /reports/group-report/` | GET | Group report with date range, group filter |
| `GET /reports/group-report/products/` | GET | Per-product daily movement within group |
| `GET /reports/damage/` | GET | Damage report by date range, group, product |
| `POST /reports/damage/` | POST | Record product damage |
| `GET /reports/daily-cost/` | GET | Daily cost breakdown by group |
| `POST /reports/daily-cost/` | POST | Record daily operational costs |
| `GET /reports/daily-profit/` | GET | Daily profit by group (revenue - costs) |
| `GET /reports/daily-summary/` | GET | Full daily report (all groups, all columns) |
| `GET /reports/reconciliation/` | GET | SR vs Khata reconciliation |
| `POST /reports/ledger/` | POST | Record ledger (khata) entry |
| `GET /reports/do-tracking/` | GET | DO tracking list |
| `GET /reports/do-tracking/{do_number}/` | GET | DO detail by number |
| `GET /reports/slow-moving/` | GET | Slow-moving product analysis |
| `GET /reports/budget/` | GET | Sales budget by group/month |
| `POST /reports/budget/` | POST | Set sales budget |

### 6.4 New Pydantic Schemas

```python
# app/schemas/reports/group_report.py
class GroupReportRequest(BaseModel):
    start_date: date
    end_date: date
    group_ids: Optional[List[int]] = None
    product_ids: Optional[List[int]] = None

class GroupProductDailyRow(BaseModel):
    sl_no: int
    product_name: str
    carton_factor: int
    dealer_price: float
    trade_price: float
    dealer_margin_pct: float
    opening_stock: float
    opening_value: float
    daily_movements: List[DailyMovement]  # per day: product_in, return, sales, values
    total_sales: float
    total_sales_value: float
    total_return: float
    total_return_value: float
    closing_stock: float
    closing_stock_value: float

class DailyMovement(BaseModel):
    date: date
    product_in: float
    return_qty: float
    sales_qty: float
    original_value: float
    sales_value: float

# app/schemas/reports/damage_report.py
class DamageRecordCreate(BaseModel):
    product_id: int
    variant_id: Optional[int] = None
    damage_date: date
    quantity: float
    reason: Optional[str] = None
    notes: Optional[str] = None

class DamageReportRow(BaseModel):
    product_name: str
    variant_name: str
    damage_date: date
    quantity: float
    unit_cost: float
    total_value: float
    reason: str

# app/schemas/reports/daily_cost.py
class DailyCostCreate(BaseModel):
    expense_date: date
    variant_group_id: Optional[int] = None
    van_cost: float = 0
    oil_cost: float = 0
    labour_cost: float = 0
    office_cost: float = 0
    other_cost: float = 0
    notes: Optional[str] = None

class DailyCostReportRow(BaseModel):
    date: date
    group_name: str
    revenue: float
    van_cost: float
    oil_cost: float
    labour_cost: float
    office_cost: float
    other_cost: float
    total_cost: float
    profit: float

# app/schemas/reports/daily_report.py
class DailyReportGroupRow(BaseModel):
    group_name: str
    sales: float
    original_sales: float
    commission: float
    market_credit: float
    damage_collection: float
    due_paid: float
    do_cash: float

class DailyReportSummary(BaseModel):
    date: date
    groups: List[DailyReportGroupRow]
    total_sales: float
    total_do_cash: float
    total_cost: float
    balance: float
    budget_amount: float
    achievement_pct: float

# app/schemas/reports/reconciliation.py
class ReconciliationRow(BaseModel):
    date: date
    sr_report_order: float
    khata_order: float
    order_difference: float
    sr_report_sales: float
    khata_sales: float
    sales_difference: float

# app/schemas/reports/do_tracking.py
class DOTrackingRow(BaseModel):
    do_number: str
    date: date
    product_name: str
    quantity: float
    unit_price: float
    total_value: float
    month: str
```

---

## 7. Frontend Implementation Plan

### 7.1 New Pages

| Page | Route | Purpose | Components |
|------|-------|---------|------------|
| **Group Report** | `/reports/group` | Per-product daily movement by group | Spreadsheet-like table, date range picker, group selector |
| **Damage Report** | `/reports/damage` | Product damage tracking | Damage table, damage recording modal, group filter |
| **Cost & Profit** | `/reports/cost-profit` | Daily cost breakdown + profit | Cost table, profit table, expense recording modal |
| **Daily Report** | `/reports/daily` | Full daily summary dashboard | Group columns, date navigation, budget comparison |
| **Reconciliation** | `/reports/reconciliation` | SR vs Khata difference | Reconciliation table, difference highlighting |
| **DO Tracking** | `/reports/do-tracking` | Delivery order tracking | DO list table, DO detail modal, search |
| **Slow Moving** | `/reports/slow-moving` | Slow-moving product analysis | Product table with sales velocity |
| **Budget Management** | `/reports/budget` | Sales budget per group/month | Budget table, budget setting modal |

### 7.2 New API Client Files

| File | Purpose |
|------|---------|
| `src/lib/api/groupReportsApi.ts` | Group report API calls |
| `src/lib/api/damageReportsApi.ts` | Damage report API calls |
| `src/lib/api/dailyCostReportsApi.ts` | Cost & profit API calls |
| `src/lib/api/dailyReportsApi.ts` | Daily report API calls |
| `src/lib/api/reconciliationApi.ts` | Reconciliation API calls |
| `src/lib/api/doTrackingApi.ts` | DO tracking API calls |

### 7.3 New React Components

| Component | Purpose |
|-----------|---------|
| `GroupReportTable.tsx` | Spreadsheet-like table for group report with horizontal scrolling |
| `DamageRecordModal.tsx` | Modal for recording product damage |
| `DailyCostForm.tsx` | Form for recording daily operational costs |
| `DailyReportDashboard.tsx` | Full daily report with group columns |
| `ReconciliationTable.tsx` | SR vs Khata with difference highlighting |
| `DOTrackingTable.tsx` | DO tracking with search |
| `BudgetFormModal.tsx` | Modal for setting sales budget |
| `DateRangePicker.tsx` | Reusable date range picker (may already exist) |
| `GroupSelector.tsx` | Reusable product group selector |

### 7.4 Route Additions (App.tsx)

```typescript
// Inside AdminRoute > /reports/*
<Route path="group" element={<GroupReport />} />
<Route path="damage" element={<DamageReport />} />
<Route path="cost-profit" element={<CostProfitReport />} />
<Route path="daily" element={<DailyReport />} />
<Route path="reconciliation" element={<ReconciliationReport />} />
<Route path="do-tracking" element={<DOTrackingReport />} />
<Route path="slow-moving" element={<SlowMovingReport />} />
<Route path="budget" element={<BudgetManagement />} />
```

---

## 8. Implementation Phases & Timeline

### Phase 1: Foundation (Week 1-2)

**Priority: Critical** — These are prerequisites for all other reports.

| Task | Estimated Effort | Files |
|------|-----------------|-------|
| Database migrations (new tables + column additions) | 2 days | `alembic/versions/` |
| Add `dealer_price`, `trade_price`, `carton_factor` fields | 1 day | Models, schemas |
| Add `do_number` to SalesOrder | 0.5 day | Model, schema |
| Add `variant_group_id` to Expense | 0.5 day | Model, schema |
| Create `ProductDamage` model + CRUD | 1 day | Model, schema, service, repo, API |
| Create `DailyCostExpense` model + CRUD | 1 day | Model, schema, service, repo, API |
| Create `SalesLedger` model + CRUD | 1 day | Model, schema, service, repo, API |
| Create `SalesBudget` model + CRUD | 1 day | Model, schema, service, repo, API |

### Phase 2: Group Reports (Week 3)

**Priority: High** — Most frequently used report in the Excel.

| Task | Estimated Effort | Files |
|------|-----------------|-------|
| Group report repository queries | 2 days | `group_reports.py` |
| Group report service | 1 day | `group_report_service.py` |
| Group report API endpoints | 1 day | `app/api/reports.py` |
| Group report frontend page | 2 days | `GroupReport.tsx`, `groupReportsApi.ts` |
| Group report Pydantic schemas | 0.5 day | `schemas/reports/` |
| Frontend components (table, selectors) | 1 day | `GroupReportTable.tsx`, `GroupSelector.tsx` |

### Phase 3: Damage Reports (Week 4)

**Priority: High** — Critical for inventory accuracy.

| Task | Estimated Effort | Files |
|------|-----------------|-------|
| Damage report repository queries | 1 day | `damage_reports.py` |
| Damage report service | 1 day | `damage_report_service.py` |
| Damage report API endpoints | 0.5 day | `app/api/reports.py` |
| Damage report frontend page | 2 days | `DamageReport.tsx`, `damageReportsApi.ts` |
| Damage recording modal | 1 day | `DamageRecordModal.tsx` |

### Phase 4: Cost & Profit + Daily Report (Week 5)

**Priority: Medium** — Financial reporting.

| Task | Estimated Effort | Files |
|------|-----------------|-------|
| Daily cost repository queries | 1 day | `daily_cost_reports.py` |
| Daily cost service | 1 day | `daily_cost_service.py` |
| Daily cost API endpoints | 0.5 day | `app/api/reports.py` |
| Daily cost frontend page | 2 days | `CostProfitReport.tsx`, `dailyCostReportsApi.ts` |
| Daily report repository queries | 1 day | `daily_reports.py` |
| Daily report service | 1 day | `daily_report_service.py` |
| Daily report frontend page | 2 days | `DailyReport.tsx`, `dailyReportsApi.ts` |

### Phase 5: Reconciliation + DO Tracking + Slow Moving (Week 6)

**Priority: Medium** — Operational reporting.

| Task | Estimated Effort | Files |
|------|-----------------|-------|
| Reconciliation repository + service | 1.5 days | `reconciliation_reports.py`, service |
| Reconciliation API + frontend | 1.5 days | API, `ReconciliationReport.tsx` |
| DO tracking repository + service | 1 day | `do_tracking_reports.py`, service |
| DO tracking API + frontend | 1 day | API, `DOTrackingReport.tsx` |
| Slow-moving repository + service | 1 day | `slow_moving_reports.py`, service |
| Slow-moving frontend | 1 day | `SlowMovingReport.tsx` |

### Phase 6: Budget Management + Polish (Week 7)

**Priority: Low** — Enhancement.

| Task | Estimated Effort | Files |
|------|-----------------|-------|
| Budget CRUD API + service | 1 day | Model, service, API |
| Budget management frontend | 1 day | `BudgetManagement.tsx` |
| Integration testing | 2 days | All endpoints |
| UI polish + responsive | 1 day | All pages |
| Documentation | 1 day | API docs, user guide |

---

## 9. Technical Decisions & Tradeoffs

### 9.1 Data Aggregation Strategy

**Option A: Pre-aggregated daily tables** (Recommended)
- Create `daily_product_movement` table populated by triggers/subscribers
- Pros: Fast queries, simple report logic
- Cons: Additional write overhead, data consistency management

**Option B: On-the-fly aggregation**
- Query SalesOrder + InventoryMovement tables and aggregate
- Pros: No extra tables, always accurate
- Cons: Slow for large date ranges, complex SQL

**Decision:** Use **Option B** (on-the-fly) for initial implementation. Add pre-aggregated tables later if performance becomes an issue. The existing `InventoryMovement` table already captures all stock changes.

### 9.2 DO Number Implementation

**Option A: Add `do_number` field to SalesOrder**
- Simple, direct mapping
- One DO = One SalesOrder

**Option B: Create separate DO entity**
- One SalesOrder can have multiple DOs (partial deliveries)
- More flexible but more complex

**Decision:** Use **Option A** initially. Most distributors in this context have 1:1 DO-to-order mapping. Can evolve to Option B if needed.

### 9.3 Damage Recording

**Option A: Separate `ProductDamage` table** (Recommended)
- Clean separation, dedicated reporting
- Can track reason, notes, approval workflow

**Option B: Add `damage_quantity` to InventoryAdjustment**
- Reuse existing adjustment infrastructure
- Less granular tracking

**Decision:** Use **Option A**. Damage is conceptually different from stock adjustments and needs dedicated tracking with reasons and approval.

### 9.4 Khata (Ledger) System

**Option A: Simple `SalesLedger` table** (Recommended for MVP)
- Manual entries recorded by admin
- Basic reconciliation against SR orders

**Option B: Full double-entry ledger**
- Complete accounting system
- Overkill for current needs

**Decision:** Use **Option A**. The Excel shows a simple comparison, not a full accounting system.

### 9.5 Frontend Table Rendering

**Challenge:** Group reports have 31+ columns (one per day) × 6 values per day = 186+ columns.

**Solution:** 
- Use AG Grid or TanStack Table with horizontal virtualization
- Freeze first 8 columns (Sl No, Product, Ctn Factor, DP/P, TP/P, Dealer %, Stock, Value)
- Group day columns under collapsible date headers
- Provide export to Excel functionality

---

## 10. Risk Assessment

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Performance with large date ranges | High | Medium | Implement pagination, date range limits, caching |
| Data consistency between movement and daily reports | High | Medium | Use database transactions, add validation |
| Complex spreadsheet-like UI performance | Medium | High | Use virtualized tables, lazy loading |
| Migration of existing data to new schema | Medium | Low | Most new tables are empty initially |
| User adoption of new damage/cost recording | Medium | Medium | Intuitive forms, bulk import from Excel |
| Multi-tenant data isolation | High | Low | All queries include company_id filter |

---

## Appendix A: Excel Column Mapping to System Concepts

| Excel Concept | System Equivalent | Notes |
|---------------|-------------------|-------|
| Product Group | `VariantGroup` | Juice, Wonder, Ketchup, etc. |
| Product | `Product` + `ProductVariant` | e.g., "White Mango-125" |
| Ctn Factor | `ProductVariant.carton_factor` | Units per carton (NEW) |
| DP/P (Dealer Price) | `ProductPrice.dealer_price` | Price per piece (NEW) |
| TP/P (Trade Price) | `ProductPrice.trade_price` | Price per piece (NEW) |
| Dealer % | Calculated: TP/DP - 1 | Derived field |
| Stock | `InventoryStock.quantity` | Current stock level |
| Product In | `InventoryMovement` (IN type) | Daily inflow |
| Return | `InventoryMovement` (RETURN type) | Daily returns |
| Sales | `InventoryMovement` (OUT type) | Daily outflow |
| Original Value | Sales × DP | Calculated |
| Sales Value | Sales × TP | Calculated |
| DO (Delivery Order) | `SalesOrder.do_number` | Order reference (NEW) |
| Damage | `ProductDamage` (NEW) | Damage quantity |
| Commission | `SR_Order.commission_amount` | Already exists |
| Market Credit | `Customer.store_credit` | Already exists |
| VAN Cost | `DailyCostExpense.van_cost` | Vehicle cost (NEW) |
| Labour | `DailyCostExpense.labour_cost` | Worker cost (NEW) |
| Khata | `SalesLedger` (NEW) | Manual ledger entries |

---

## Appendix B: Existing Reports That Can Be Leveraged

| Existing Report | Can Provide | For New Report |
|-----------------|-------------|----------------|
| SR Program Workflow → Financials | Commission + Market Credit per group | Daily Report, Cost & Profit |
| SR Program Workflow → Undelivery | Group-level undelivery | Enhanced Undelivery (date-wise) |
| SR Program Workflow → DO Cash | Group-level DO cash | Daily Report DO Cash |
| SR Summary | Per-SR sales data | Reconciliation SR side |
| Inventory Movement Ledger | All stock movements | Group Report (Product In/Return/Sales) |
| Batch Reports | Cost-per-unit tracking | Group Report (Original Value) |
| Expense model | Existing expense records | Cost & Profit (Office cost) |
| Dead Stock Report | Slow-moving detection | Slow Moving Report |

---

*Document created: 2026-04-01*  
*Total estimated effort: ~7 weeks for full implementation*  
*Recommended starting point: Phase 1 (Foundation) — database schema changes*
