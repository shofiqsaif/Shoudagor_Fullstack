# Reports Module (Analytics & Reporting System) - Complete Reference

---

**Generated:** April 17, 2026  
**Scope:** Full-stack analysis of the Reports Module  
**Coverage:** Backend API, Frontend UI, Interconnected Workflows, Special Features

---

## Table of Contents

1. [Module Architecture Overview](#1-module-architecture-overview)
2. [Entity Inventory](#2-entity-inventory)
3. [Backend Operations Reference](#3-backend-operations-reference)
4. [Frontend UI Walkthrough](#4-frontend-ui-walkthrough)
5. [Interconnected Workflows](#5-interconnected-workflows)
6. [Special Features Deep-Dive](#6-special-features-deep-dive)
7. [API Quick Reference](#7-api-quick-reference)
8. [File Map](#8-file-map)
9. [Appendix: Operation Counts](#9-appendix-operation-counts)

---

## 1. Module Architecture Overview

### 1.1 Layer Structure

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           LAYER STRUCTURE                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────┐                                                      │
│  │   PRESENTATION      │  React + TypeScript + Tailwind CSS                 │
│  │   LAYER             │  Shadcn/UI Components + Recharts                   │
│  │                     │  React Query (TanStack Query)                      │
│  │                     │  React Hook Form + Zod Validation                  │
│  └─────────────────────┘                                                      │
│           │                                                                  │
│           ▼                                                                  │
│  ┌─────────────────────┐                                                      │
│  │   API LAYER         │  RESTful API Client (axios wrapper)                │
│  │                     │  Zod Schema Validation                              │
│  │                     │  Modular API Functions per Report Type             │
│  └─────────────────────┘                                                      │
│           │                                                                  │
│           ▼                                                                  │
│  ┌─────────────────────┐                                                      │
│  │   BACKEND           │  FastAPI (Python)                                   │
│  │   LAYER             │  SQLAlchemy ORM                                     │
│  │                     │  Pydantic Schemas                                   │
│  │                     │  Repository Pattern + Service Layer               │
│  └─────────────────────┘                                                      │
│           │                                                                  │
│           ▼                                                                  │
│  ┌─────────────────────┐                                                      │
│  │   DATA LAYER        │  PostgreSQL (inventory, sales, reports schemas)    │
│  │                     │  Database Indexes + Foreign Keys                    │
│  └─────────────────────┘                                                      │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Entity Relationships

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ENTITY RELATIONSHIPS                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌──────────────────────┐                                                  │
│   │  AppClientCompany    │                                                  │
│   │       (1)            │                                                  │
│   └──────────┬───────────┘                                                  │
│              │ 1:N                                                            │
│              │                                                                │
│    ┌─────────┼─────────┬──────────┬─────────────┐                          │
│    │         │         │          │             │                          │
│    ▼         ▼         ▼          ▼             ▼                          │
│ ┌──────┐ ┌────────┐ ┌───────┐ ┌─────────┐ ┌───────────┐                    │
│ │Damage│ │Daily   │ │Sales  │ │Sales    │ │SalesBudget│                    │
│ │Report│ │Cost    │ │Ledger│ │Rep.     │ │           │                    │
│ │  (N) │ │Expense │ │  (N)  │ │Summary  │ │    (N)    │                    │
│ │      │ │  (N)   │ │       │ │  (N)   │ │           │                    │
│ └──┬───┘ └───┬────┘ └───┬───┘ └────┬────┘ └─────┬─────┘                    │
│    │         │          │          │            │                          │
│    │ N:1     │ N:1      │ N:1      │            │ N:1                      │
│    │         │          │          │            │                          │
│    ▼         ▼          ▼          │            ▼                          │
│ ┌────────┐ ┌────────┐ ┌─────────┐    │      ┌──────────┐                    │
│ │Product │ │Variant │ │Customer│    │      │ Variant  │                    │
│ │ (1)    │ │Group   │ │  (1)    │    │      │ Group    │                    │
│ │        │ │  (1)   │ │         │    │      │  (1)     │                    │
│ └────────┘ └────────┘ └─────────┘    │      └──────────┘                    │
│                                      │                                      │
│                                      │ N:M                                    │
│                                      ▼                                      │
│                               ┌───────────┐                                 │
│                               │  Product  │                                 │
│                               │  Variant  │                                 │
│                               │    (1)    │                                 │
│                               └───────────┘                                 │
│                                                                              │
│   ADDITIONAL REPORT ENTITIES (Aggregated Views):                            │
│                                                                              │
│   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐                   │
│   │   Purchase   │   │    Sales     │   │  Operational │                   │
│   │    Orders    │   │    Orders    │   │  Fulfillment │                   │
│   │  (Read-Only) │   │  (Read-Only) │   │  (Read-Only) │                   │
│   └──────────────┘   └──────────────┘   └──────────────┘                   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.3 Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Frontend Framework** | React 18 + TypeScript | UI components and state management |
| **Styling** | Tailwind CSS + Shadcn/UI | Modern component styling |
| **Data Fetching** | TanStack Query (React Query) | Server state management, caching |
| **Forms** | React Hook Form | Form handling with validation |
| **Validation** | Zod | Schema validation (frontend & backend) |
| **Charts** | Recharts | Data visualization |
| **Backend API** | FastAPI | High-performance Python API framework |
| **ORM** | SQLAlchemy 2.0 | Database abstraction |
| **Schemas** | Pydantic | Request/response validation |
| **Database** | PostgreSQL 15 | Primary data store |
| **Auth** | JWT + OAuth2 | Secure API access |

---

## 2. Entity Inventory

### 2.1 Product Damage (`inventory.product_damage`)

Tracks product damage/loss per date per product.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `damage_id` | Integer | PK, Auto-increment | Unique identifier |
| `company_id` | Integer | FK → app_client_company | Multi-tenant isolation |
| `product_id` | Integer | FK → product, Nullable | Product reference |
| `variant_id` | Integer | FK → product_variant, Nullable | Variant reference |
| `damage_date` | Date | NOT NULL | Date of damage incident |
| `quantity` | Numeric(12,3) | NOT NULL, Default 0 | Damaged quantity |
| `unit_cost` | Numeric(12,2) | Nullable | Cost per unit |
| `total_value` | Numeric(14,2) | Nullable | Calculated: quantity × unit_cost |
| `reason` | String(100) | Nullable | Reason for damage |
| `notes` | Text | Nullable | Additional notes |
| `cb` | Integer | Nullable | Created by user ID |
| `cd` | TIMESTAMP | Default NOW | Creation timestamp |
| `mb` | Integer | Nullable | Modified by user ID |
| `md` | TIMESTAMP | Auto-update | Last modified timestamp |
| `is_deleted` | Boolean | NOT NULL, Default FALSE | Soft delete flag |

**Indexes:**
- `idx_product_damage_company` (company_id)
- `idx_product_damage_date` (damage_date)
- `idx_product_damage_product` (product_id, variant_id)

**Relationships:**
- `product` → Product (N:1)
- `variant` → ProductVariant (N:1)

---

### 2.2 Daily Cost Expense (`reports.daily_cost_expense`)

Daily operational cost tracking by product group.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `cost_id` | Integer | PK, Auto-increment | Unique identifier |
| `company_id` | Integer | FK → app_client_company | Multi-tenant isolation |
| `expense_date` | Date | NOT NULL | Date of expense |
| `variant_group_id` | Integer | FK → variant_group, Nullable | Product group |
| `van_cost` | Numeric(14,2) | NOT NULL, Default 0 | Van/transport cost |
| `oil_cost` | Numeric(14,2) | NOT NULL, Default 0 | Fuel/oil cost |
| `labour_cost` | Numeric(14,2) | NOT NULL, Default 0 | Labor cost |
| `office_cost` | Numeric(14,2) | NOT NULL, Default 0 | Office expenses |
| `other_cost` | Numeric(14,2) | NOT NULL, Default 0 | Other expenses |
| `total_cost` | Numeric(14,2) | Nullable | Auto-calculated sum |
| `notes` | Text | Nullable | Additional notes |
| `cb` | Integer | Nullable | Created by user ID |
| `cd` | TIMESTAMP | Default NOW | Creation timestamp |
| `mb` | Integer | Nullable | Modified by user ID |
| `md` | TIMESTAMP | Auto-update | Last modified timestamp |
| `is_deleted` | Boolean | NOT NULL, Default FALSE | Soft delete flag |

**Indexes:**
- `idx_daily_cost_company` (company_id)
- `idx_daily_cost_date` (expense_date)
- `idx_daily_cost_group` (variant_group_id)

**Relationships:**
- `variant_group` → VariantGroup (N:1)

---

### 2.3 Sales Ledger (`reports.sales_ledger`)

Manual ledger entries (khata) for reconciliation with SR reports.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `ledger_id` | Integer | PK, Auto-increment | Unique identifier |
| `company_id` | Integer | FK → app_client_company | Multi-tenant isolation |
| `entry_date` | Date | NOT NULL | Ledger entry date |
| `entry_type` | String(20) | Nullable | Type of entry (order/sales/payment) |
| `variant_group_id` | Integer | FK → variant_group, Nullable | Product group |
| `customer_id` | Integer | FK → customer, Nullable | Customer reference |
| `order_amount` | Numeric(14,2) | Nullable | Order amount |
| `sales_amount` | Numeric(14,2) | Nullable | Sales amount |
| `payment_amount` | Numeric(14,2) | Nullable | Payment amount |
| `reference_type` | String(20) | Nullable | Reference document type |
| `reference_id` | Integer | Nullable | Reference document ID |
| `notes` | Text | Nullable | Additional notes |
| `cb` | Integer | Nullable | Created by user ID |
| `cd` | TIMESTAMP | Default NOW | Creation timestamp |
| `mb` | Integer | Nullable | Modified by user ID |
| `md` | TIMESTAMP | Auto-update | Last modified timestamp |
| `is_deleted` | Boolean | NOT NULL, Default FALSE | Soft delete flag |

**Indexes:**
- `idx_sales_ledger_company` (company_id)
- `idx_sales_ledger_date` (entry_date)
- `idx_sales_ledger_type` (entry_type)
- `idx_sales_ledger_reference` (reference_type, reference_id)

**Relationships:**
- `variant_group` → VariantGroup (N:1)
- `customer` → Customer (N:1)

---

### 2.4 Sales Budget (`reports.sales_budget`)

Monthly sales budget per product group.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `budget_id` | Integer | PK, Auto-increment | Unique identifier |
| `company_id` | Integer | FK → app_client_company | Multi-tenant isolation |
| `variant_group_id` | Integer | FK → variant_group, Nullable | Product group |
| `budget_month` | Date | NOT NULL | Month of budget (YYYY-MM-01) |
| `budget_amount` | Numeric(14,2) | NOT NULL | Budgeted sales amount |
| `cb` | Integer | Nullable | Created by user ID |
| `cd` | TIMESTAMP | Default NOW | Creation timestamp |
| `mb` | Integer | Nullable | Modified by user ID |
| `md` | TIMESTAMP | Auto-update | Last modified timestamp |
| `is_deleted` | Boolean | NOT NULL, Default FALSE | Soft delete flag |

**Constraints:**
- Unique: `(company_id, variant_group_id, budget_month)` - One budget per group per month

**Indexes:**
- `idx_sales_budget_company` (company_id)
- `idx_sales_budget_month` (budget_month)

**Relationships:**
- `variant_group` → VariantGroup (N:1)

---

## 3. Backend Operations Reference

### 3.1 Product Damage Operations

| Operation | Method | Endpoint | Service/Repository | Description |
|-----------|--------|----------|-------------------|-------------|
| List | GET | `/api/company/sr-reports/damage` | ProductDamageRepository.get_all() | Paginated list with filters |
| Get Single | GET | `/api/company/sr-reports/damage/{id}` | ProductDamageRepository.get_by_id() | Single damage record |
| Create | POST | `/api/company/sr-reports/damage` | ProductDamageRepository.create() | Create damage entry |
| Update | PATCH | `/api/company/sr-reports/damage/{id}` | ProductDamageRepository.update() | Update damage entry |
| Delete | DELETE | `/api/company/sr-reports/damage/{id}` | ProductDamageRepository.delete() | Soft delete |
| Aggregate Report | GET | `/api/company/sr-reports/damage/report` | ProductDamageRepository.get_report() | Grouped damage report |
| Summary by Group | GET | `/api/company/sr-reports/damage/report` | get_summary_by_group() | Group-wise summary |
| Summary by Date | GET | `/api/company/sr-reports/damage/report` | get_summary_by_date() | Date-wise summary |
| Summary by Reason | GET | `/api/company/sr-reports/damage/report` | get_summary_by_reason() | Reason-wise summary |

### 3.2 Daily Cost Expense Operations

| Operation | Method | Endpoint | Service/Repository | Description |
|-----------|--------|----------|-------------------|-------------|
| List | GET | `/api/company/sr-reports/daily-cost` | DailyCostExpenseRepository.get_all() | Paginated list with filters |
| Get Single | GET | `/api/company/sr-reports/daily-cost/{id}` | DailyCostExpenseRepository.get_by_id() | Single cost record |
| Create | POST | `/api/company/sr-reports/daily-cost` | DailyCostExpenseRepository.create() | Create expense entry (auto-calculates total) |
| Update | PATCH | `/api/company/sr-reports/daily-cost/{id}` | DailyCostExpenseRepository.update() | Update expense entry (auto-recalculates total) |
| Delete | DELETE | `/api/company/sr-reports/daily-cost/{id}` | DailyCostExpenseRepository.delete() | Soft delete |
| Get by Date/Group | Internal | - | get_by_date_and_group() | Lookup for existing entries |

### 3.3 Sales Ledger Operations

| Operation | Method | Endpoint | Service/Repository | Description |
|-----------|--------|----------|-------------------|-------------|
| List | GET | `/api/company/sr-reports/ledger` | SalesLedgerRepository.get_all() | Paginated list with date/type filters |
| Get Single | GET | `/api/company/sr-reports/ledger/{id}` | SalesLedgerRepository.get_by_id() | Single ledger entry |
| Create | POST | `/api/company/sr-reports/ledger` | SalesLedgerRepository.create() | Create ledger entry |
| Delete | DELETE | `/api/company/sr-reports/ledger/{id}` | SalesLedgerRepository.delete() | Soft delete |
| Get by Date | Internal | - | get_by_date() | Lookup for reconciliation |

### 3.4 Sales Budget Operations

| Operation | Method | Endpoint | Service/Repository | Description |
|-----------|--------|----------|-------------------|-------------|
| List | GET | `/api/company/sr-reports/budget` | SalesBudgetRepository.get_all() | Paginated list with month/group filters |
| Get Single | GET | `/api/company/sr-reports/budget/{id}` | SalesBudgetRepository.get_by_id() | Single budget entry |
| Create | POST | `/api/company/sr-reports/budget` | SalesBudgetRepository.create() | Create budget (upserts if exists) |
| Update | PATCH | `/api/company/sr-reports/budget/{id}` | SalesBudgetRepository.update() | Update budget entry |
| Delete | DELETE | `/api/company/sr-reports/budget/{id}` | SalesBudgetRepository.delete() | Soft delete |
| Get by Group/Month | Internal | - | get_by_group_and_month() | Lookup for duplicate prevention |
| Get by Month | Internal | - | get_by_month() | Monthly budget retrieval |

### 3.5 Aggregated Report Operations (Read-Only)

| Operation | Method | Endpoint | Repository | Description |
|-----------|--------|----------|------------|-------------|
| Group Report | GET | `/api/company/sr-reports/group-report` | GroupReportRepository | Daily movement per product in group |
| DO Tracking | GET | `/api/company/sr-reports/do-tracking` | DOTrackingRepository | Delivery order tracking |
| Reconciliation | GET | `/api/company/sr-reports/reconciliation` | ReconciliationRepository | SR report vs Khata comparison |
| Slow Moving | GET | `/api/company/sr-reports/slow-moving` | SlowMovingRepository | Products with low velocity |
| Daily Report | GET | `/api/company/sr-reports/daily-report` | DailyReportRepository | Single day summary |
| Cost & Profit | GET | `/api/company/sr-reports/cost-profit` | DailyReportRepository | Date-wise cost breakdown |
| Undelivery Report | GET | `/api/company/sr-reports/undelivery` | SRProgramReportsRepository | Undelivery breakdown |
| DO Cash Report | GET | `/api/company/sr-reports/do-cash` | SRProgramReportsRepository | DO cash breakdown |

### 3.6 Main Reports API Operations

| Report Type | Method | Endpoint | Service Method |
|-------------|--------|----------|----------------|
| Inventory KPI | GET | `/api/company/reports/inventory` | get_inventory_kpi_ribbon_data() |
| Product Stock | GET | `/api/company/reports/inventory/product-report` | get_current_stock() |
| Purchase Order | GET | `/api/company/reports/procurement/purchase-order-report` | get_purchase_order_report() |
| Sales Fulfillment | GET | `/api/company/reports/sales/fulfillment` | get_operational_excellence_report() |
| Sales Profitability | GET | `/api/company/reports/sales/profitability` | get_sales_financial_report() |
| Inventory Performance | GET | `/api/company/reports/sales/inventory-performance` | get_inventory_performance_report() |
| Team Performance | GET | `/api/company/reports/sales/team-performance` | get_sales_team_performance_report() |
| Advanced Analytics | GET | `/api/company/reports/sales/advanced` | get_sales_advanced_analytics_report() |
| Product Analysis | GET | `/api/company/reports/sales/product-analysis` | get_product_sales_analysis() |
| Territory Performance | GET | `/api/company/reports/sales/territory-performance` | get_territory_sales_report() |
| Customer Activity | GET | `/api/company/reports/sales/customer-activity` | get_customer_activity_report() |
| Pipeline Analysis | GET | `/api/company/reports/sales/pipeline-analysis` | get_pipeline_analysis() |
| Demand Forecast | GET | `/api/company/reports/sales/demand-forecast` | get_demand_forecast() |
| Warehouse Summary | GET | `/api/company/reports/inventory/warehouse-summary` | get_warehouse_summary_report() |
| Inventory Valuation | GET | `/api/company/reports/inventory/valuation` | get_inventory_valuation_report() |
| DSI & GMROI | GET | `/api/company/reports/inventory/dsi-gmroi` | get_dsi_gmroi_report() |
| Dead Stock | GET | `/api/company/reports/inventory/dead-stock` | get_dead_stock_report() |
| Safety Stock | GET | `/api/company/reports/inventory/safety-stock` | get_safety_stock_report() |
| SR Summary | GET | `/api/company/reports/sr-summary` | get_sr_summary_report() |
| SR Product Variants | GET | `/api/company/reports/sr-product-variants/{sr_id}` | get_sr_product_variants() |
| SR Variant Details | GET | `/api/company/reports/sr-product-variant-details/{sr_id}` | get_sr_product_variant_details() |
| DSR Summary | GET | `/api/company/reports/dsr-summary` | get_dsr_summary_report() |
| DSR Loading | GET | `/api/company/reports/dsr-loading/{dsr_id}` | get_dsr_loading_report() |
| DSR SO Breakdown | GET | `/api/company/reports/dsr-so-breakdown/{dsr_id}` | get_dsr_so_breakdown() |
| SR Program Workflow | GET | `/api/company/reports/sr-program/workflow` | get_sr_program_workflow() |

---

## 4. Frontend UI Walkthrough

### 4.1 Pages Inventory

| Page | Route | Status | Description |
|------|-------|--------|-------------|
| Reports Dashboard | `/reports` | ✅ | Main reports landing page with categories |
| Damage Report | `/reports/damage` | ✅ | Product damage tracking and management |
| Group Report | `/reports/group` | ✅ | Daily product movement by group |
| Daily Report | `/reports/daily` | ✅ | Single day operational summary |
| DO Tracking | `/reports/do-tracking` | ✅ | Delivery order tracking |
| Reconciliation | `/reports/reconciliation` | ✅ | SR report vs Khata comparison |
| Slow Moving | `/reports/slow-moving` | ✅ | Low velocity product identification |
| Cost & Profit | `/reports/cost-profit` | ✅ | Cost analysis with date breakdown |
| Budget Management | `/reports/budget` | ✅ | Monthly sales budget management |
| Ledger Management | `/reports/ledger` | ✅ | Khata/manual ledger entries |
| SR Reports | `/reports/sr` | ✅ | Sales Representative performance |
| DSR Reports | `/reports/dsr` | ✅ | Delivery SR performance |
| SR Program Admin | `/reports/sr-program/admin` | ✅ | Channel admin view |
| SR Program Workflow | `/reports/sr-program/workflow` | ✅ | Workflow visualization |
| Inventory Report | `/reports/inventory` | ✅ | Inventory KPI ribbon |
| Purchase Order Report | `/reports/purchaseorder` | ✅ | Procurement analytics |
| Fulfillment Report | `/reports/sales/fulfillment` | ✅ | Order fulfillment metrics |
| Sales Profitability | `/reports/sales/profitability` | ✅ | Customer ABC analysis |
| Product Analysis | `/reports/sales/product-analysis` | ✅ | Product sales breakdown |
| Customer Activity | `/reports/sales/customer-activity` | ✅ | Customer purchase patterns |
| Territory Performance | `/reports/sales/territory-performance` | ✅ | Beat/territory sales |
| Pipeline Analysis | `/reports/sales/pipeline-analysis` | ✅ | Quote-to-order conversion |
| Team Performance | `/reports/sales/team-performance` | ✅ | SR velocity metrics |
| Advanced Analytics | `/reports/sales/advanced` | ✅ | Churn risk & elasticity |
| Demand Forecast | `/reports/sales/demand-forecast` | ✅ | AI-enhanced predictions |
| Warehouse Summary | `/reports/inventory/warehouse-summary` | ✅ | Location-wise stock |
| Inventory Valuation | `/reports/inventory/valuation` | ✅ | Financial stock snapshot |
| DSI & GMROI | `/reports/inventory/dsi-gmroi` | ✅ | Inventory efficiency metrics |
| Dead Stock | `/reports/inventory/dead-stock` | ✅ | Obsolete inventory |
| Expense Intelligence | `/reports/expenses` | ✅ | Expense category breakdown |

### 4.2 Forms & Modals

| Component | File Path | Purpose |
|-----------|-----------|---------|
| Damage Entry Form | `DamageReport.tsx` (inline) | Create/edit damage records |
| Cost Entry Form | `CostProfitReport.tsx` (inline) | Create/edit daily costs |
| Budget Entry Form | `BudgetManagement.tsx` (inline) | Create/edit monthly budgets |
| Ledger Entry Form | `LedgerManagement.tsx` (inline) | Create/edit ledger entries |
| SR Detail Modal | `SRReports.tsx` (inline) | Product variant drill-down |
| DSR Detail Modal | `DSRReports.tsx` (inline) | Loading details view |
| Date Range Picker | `components/DateRangePicker.tsx` | Report date selection |
| Product Selector | Shared component | Product/variant selection |
| Group Selector | Shared component | Variant group selection |

### 4.3 Shared Components

| Component | File Path | Purpose |
|-----------|-----------|---------|
| ReportInfo | `components/ReportInfo.tsx` | Hover information card for reports |
| DateRangePicker | `components/DateRangePicker.tsx` | Date range selection |
| DataTable | `components/ui/data-table.tsx` | Reusable sortable/filterable table |
| ChartContainer | `components/ui/chart.tsx` | Chart wrapper with theming |
| Card | `components/ui/card.tsx` | Report metric cards |
| Alert | `components/ui/alert.tsx` | Error/success messages |
| Skeleton | `components/ui/skeleton.tsx` | Loading placeholders |
| Badge | `components/ui/badge.tsx` | Status indicators |
| Button | `components/ui/button.tsx` | Action buttons |

### 4.4 Context Providers

| Context | File Path | Purpose |
|---------|-----------|---------|
| AuthContext | `contexts/AuthContext.tsx` | User authentication state |
| CompanyContext | `contexts/CompanyContext.tsx` | Current company selection |
| ThemeProvider | `components/theme-provider.tsx` | Dark/light mode |
| QueryClient | `lib/queryClient.ts` | React Query configuration |

### 4.5 API Layer

| API File | Key Functions |
|----------|---------------|
| `lib/api/srReportsApi.ts` | `getSRSummaryReport()`, `getSRProductVariants()`, `getSRProductVariantDetails()` |
| `lib/api/dsrReportsApi.ts` | `getDSRSummaryReport()`, `getDSRLoadingReport()`, `getDSRSOBreakdown()` |
| `lib/api/reportsApi.ts` | `getInventoryReport()`, `getPurchaseOrderReport()`, `getSalesFulfillmentReport()`, `getSalesProfitabilityReport()`, etc. |

### 4.6 Types & Zod Schemas

| Schema | File | Key Fields |
|--------|------|------------|
| PurchaseOrderReport | `lib/schema/purchaseOrderReport.ts` | `year`, `start_date`, `end_date`, `supplier_performance`, `spend_analysis` |
| ProductDamage | Backend: `schemas/sr_reports.py` | `product_id`, `variant_id`, `damage_date`, `quantity`, `unit_cost`, `reason` |
| DailyCostExpense | Backend: `schemas/sr_reports.py` | `expense_date`, `variant_group_id`, `van_cost`, `oil_cost`, `labour_cost`, `office_cost`, `other_cost` |
| SalesLedger | Backend: `schemas/sr_reports.py` | `entry_date`, `entry_type`, `order_amount`, `sales_amount`, `payment_amount` |
| SalesBudget | Backend: `schemas/sr_reports.py` | `variant_group_id`, `budget_month`, `budget_amount` |
| GroupReport | Backend: `schemas/sr_reports.py` | `group_id`, `start_date`, `end_date`, `products[]`, `daily_movements[]` |
| SRSummary | Backend: `schemas/sr_reports.py` | `sr_id`, `total_orders`, `total_revenue`, `gross_profit`, `net_profit` |
| DSRSummary | Backend: `schemas/dsr_reports.py` | `dsr_id`, `total_assignments`, `total_value`, `payment_on_hand` |

---

## 5. Interconnected Workflows

### 5.1 Damage Report Entry Flow

```
┌─────────────────────────────────────────────────────────────────┐
│  USER opens Damage Report page                                  │
│  → Route: /reports/damage                                       │
│  → Component: DamageReport.tsx                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  LIST VIEW displays existing damage records                     │
│  → GET /api/company/sr-reports/damage?start=0&limit=20          │
│  → Repository: ProductDamageRepository.get_all()              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  USER clicks "Add Damage Entry"                                   │
│  → Inline form or modal appears                                  │
│  → Form validation with Zod schema                             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  USER fills form:                                                 │
│  • Product (searchable dropdown) → Product selector            │
│  • Variant (if applicable)                                       │
│  • Damage Date (date picker)                                     │
│  • Quantity (numeric input)                                      │
│  • Unit Cost (auto-fills from product price)                     │
│  • Reason (dropdown: Damaged, Expired, Lost, etc.)               │
│  • Notes (text area)                                             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  SUBMIT creates damage record                                     │
│  → POST /api/company/sr-reports/damage                           │
│  → Body: ProductDamageCreate schema                              │
│  → Auto-calculates: total_value = quantity × unit_cost          │
│  → Sets: cb = current_user_id, cd = NOW()                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  SUCCESS: Refetch list and show success toast                   │
│  → React Query invalidates "damage" cache key                    │
│  → List auto-updates                                              │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 Daily Cost Entry Flow

```
┌─────────────────────────────────────────────────────────────────┐
│  USER opens Cost & Profit Report                                │
│  → Route: /reports/cost-profit                                  │
│  → Component: CostProfitReport.tsx                                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  USER selects date range and clicks "Load Report"                 │
│  → GET /api/company/sr-reports/cost-profit                       │
│  → Params: start_date, end_date, group_ids                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  USER clicks "Add Daily Cost" in specific date cell              │
│  → Inline edit form appears                                      │
│  → Fields: van_cost, oil_cost, labour_cost, office_cost, other   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  SUBMIT creates/updates cost record                              │
│  → POST /api/company/sr-reports/daily-cost                       │
│  → Auto-calculates: total_cost = sum of all cost fields          │
│  → Uses upsert: Updates if (company_id, date, group) exists    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Report recalculates profit metrics                              │
│  → Front-end: sales - total_cost = profit                        │
│  → Charts auto-update                                              │
└─────────────────────────────────────────────────────────────────┘
```

### 5.3 Group Report Generation Flow

```
┌─────────────────────────────────────────────────────────────────┐
│  USER opens Group Report page                                     │
│  → Route: /reports/group                                          │
│  → Component: GroupReport.tsx                                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  USER selects:                                                    │
│  • Variant Group (dropdown)                                        │
│  • Date Range (start_date, end_date)                             │
│  • Clicks "Generate Report"                                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  API call fetches group report data                              │
│  → GET /api/company/sr-reports/group-report                       │
│  → Params: group_id, start_date, end_date                        │
│  → Repository: GroupReportRepository                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Backend processing per product in group:                        │
│  1. get_products_in_group() - List all products in group         │
│  2. get_opening_stock() - Stock before start_date                │
│  3. get_daily_movement() - IN/OUT/RETURN per day                  │
│  4. get_current_stock() - Current inventory level               │
│  5. Calculate: closing = opening + in - sales - returns          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Response includes:                                               │
│  • Products array with daily movements                            │
│  • Opening/closing stock values                                   │
│  • Sales and return totals                                        │
│  • Summary metrics                                                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Frontend renders:                                                │
│  • Expandable product rows                                        │
│  • Daily movement table per product                              │
│  • Charts for sales trends                                        │
│  • Summary cards with totals                                      │
└─────────────────────────────────────────────────────────────────┘
```

### 5.4 Reconciliation Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│  USER opens Reconciliation Report                                │
│  → Route: /reports/reconciliation                                 │
│  → Component: ReconciliationReport.tsx                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  USER selects date range                                          │
│  → API call: GET /api/company/sr-reports/reconciliation            │
│  → Repository: ReconciliationRepository                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Backend compares:                                                │
│  • SR Orders: Total from sales.sr_order per date                 │
│  • Khata Orders: Total from reports.sales_ledger per date        │
│  • SR Sales: Total from sales.sales_order (order_source='sr')    │
│  • Khata Sales: Total from sales_ledger.sales_amount             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Response shows:                                                  │
│  • Date-by-date comparison table                                 │
│  • Difference columns (SR - Khata)                                │
│  • Summary totals at bottom                                       │
│  • Color-coded: Green (match), Red (mismatch)                     │
└─────────────────────────────────────────────────────────────────┘
```

### 5.5 SR Performance Drill-Down Flow

```
┌─────────────────────────────────────────────────────────────────┐
│  USER opens SR Reports page                                       │
│  → Route: /reports/sr                                             │
│  → Component: SRReports.tsx                                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  LIST VIEW shows SR summary                                       │
│  → GET /api/company/reports/sr-summary                           │
│  → Service: ReportsService.get_sr_summary_report()               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  USER clicks on specific SR row                                   │
│  → Modal opens with product variant breakdown                    │
│  → GET /api/company/reports/sr-product-variants/{sr_id}          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  USER clicks on specific product-variant                          │
│  → Deep dive modal opens                                          │
│  → GET /api/company/reports/sr-product-variant-details/{sr_id}   │
│  → Params: product_id, variant_id, start_date, end_date          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Detail view shows:                                               │
│  • Customer-level order breakdown                                  │
│  • Order numbers and dates                                        │
│  • Quantities, prices, profits                                    │
│  • Status for each order                                          │
└─────────────────────────────────────────────────────────────────┘
```

---

## 6. Special Features Deep-Dive

### 6.1 Auto-Calculation Logic

#### Daily Cost Total Auto-Calculation

```python
# On Create (sr_reports.py API)
record_data["total_cost"] = (
    (data.van_cost or 0)
    + (data.oil_cost or 0)
    + (data.labour_cost or 0)
    + (data.office_cost or 0)
    + (data.other_cost or 0)
)

# On Update (sr_reports.py Repository)
if any(k in data for k in ["van_cost", "oil_cost", "labour_cost", "office_cost", "other_cost"]):
    record.total_cost = (
        (record.van_cost or 0)
        + (record.oil_cost or 0)
        + (record.labour_cost or 0)
        + (record.office_cost or 0)
        + (record.other_cost or 0)
    )
```

#### Damage Value Auto-Calculation

```python
# API calculates total_value if quantity and unit_cost provided
if record_data.get("quantity") and record_data.get("unit_cost"):
    record_data["total_value"] = record_data["quantity"] * record_data["unit_cost"]
```

### 6.2 Soft Delete Pattern

All report entities use soft delete (is_deleted flag):

```python
# Delete operation (Repository)
def delete(self, record):
    record.is_deleted = True
    self.db.commit()

# Query operations always filter
query = self.db.query(Model).filter(
    Model.company_id == company_id,
    Model.is_deleted == False  # Never show deleted
)
```

### 6.3 Sales Budget Upsert Logic

```python
# Budget creation with duplicate prevention
existing = repo.get_by_group_and_month(
    company_id, 
    record_data.get("variant_group_id", 0), 
    record_data["budget_month"]
)
if existing:
    return repo.update(existing, record_data)  # Update existing
return repo.create(record_data)  # Create new
```

### 6.4 Multi-Tenant Security

All queries include `company_id` filter:

```python
def get_company_id(user: dict = Depends(get_current_user)) -> int:
    return user.get("company_id") or user.get("Company", {}).get("company_id")

# Every endpoint uses this
def get_damage(
    damage_id: int,
    db: Session = Depends(get_db),
    company_id: int = Depends(get_company_id),  # Injected
):
    record = repo.get_by_id(damage_id, company_id)  # Scoped query
```

### 6.5 Date Range Validation

```python
# Consistent date validation across report endpoints
if start_date > end_date:
    raise HTTPException(
        status_code=400, 
        detail="start_date must be less than or equal to end_date"
    )

# Default date ranges
if not (start_date and end_date):
    end_date = date.today()
    start_date = end_date - timedelta(days=30)
```

### 6.6 Decimal to Float Conversion

For JSON serialization of PostgreSQL Numeric types:

```python
# Service layer converts Decimal to float
def get_sr_summary_report(...):
    raw = self.sr_repo.get_sr_summary(...)
    items = []
    for row in raw:
        item = dict(row)
        for field in ["total_revenue", "total_cost", "gross_profit", ...]:
            if field in item and item[field] is not None:
                item[field] = float(item[field])
        items.append(item)
```

### 6.7 Inventory Movement Tracking

Group Report uses inventory_movements for accurate stock tracking:

```python
def get_daily_movement(self, company_id, product_id, variant_id, start_date, end_date):
    query = self.db.query(
        func.date(InventoryMovement.txn_timestamp).label("move_date"),
        InventoryMovement.movement_type,
        func.sum(InventoryMovement.qty).label("qty"),
    ).filter(...)
    
    # Categorize movements
    daily = {}
    for row in results:
        if row.movement_type in ("IN", "OPENING_BALANCE", "BACKFILL"):
            daily[d]["product_in"] += float(row.qty or 0)
        elif row.movement_type in ("RETURN_IN",):
            daily[d]["return_qty"] += float(row.qty or 0)
        elif row.movement_type in ("OUT", "RETURN_OUT"):
            daily[d]["sales_qty"] += abs(float(row.qty or 0))
```

### 6.8 Slow Moving Product Detection

```python
def get_slow_moving(self, company_id, start_date, end_date, threshold_days=30):
    date_range = (end_date - start_date).days or 1
    
    for product in products:
        sales = sales_map.get(key, {"qty": 0})
        stock = stock_map.get(key, 0)
        
        daily_velocity = sales["qty"] / date_range if date_range > 0 else 0
        days_of_stock = stock / daily_velocity if daily_velocity > 0 else 999
        
        is_slow = daily_velocity < 1 or days_of_stock > threshold_days
```

### 6.9 JSON Response Structure Examples

#### Group Report Response
```json
{
  "group_id": 1,
  "group_name": "Beverages",
  "start_date": "2024-01-01",
  "end_date": "2024-01-31",
  "products": [
    {
      "sl_no": 1,
      "product_id": 101,
      "product_name": "Cola 500ml",
      "opening_stock": 100,
      "daily_movements": [
        {
          "date": "2024-01-01",
          "product_in": 50,
          "return_qty": 5,
          "sales_qty": 30
        }
      ],
      "total_sales": 150,
      "closing_stock": 120
    }
  ],
  "summary": {
    "total_products": 25,
    "total_opening_value": 50000,
    "total_sales_value": 75000,
    "total_closing_value": 60000
  }
}
```

#### SR Summary Response
```json
{
  "items": [
    {
      "sr_id": 1,
      "sr_name": "John Doe",
      "sr_code": "SR001",
      "total_orders": 45,
      "total_quantity": 1250,
      "total_revenue": 150000.00,
      "total_cost": 120000.00,
      "gross_profit": 30000.00,
      "profit_margin_percent": 20.0,
      "total_commission": 7500.00,
      "net_profit": 22500.00
    }
  ],
  "total_count": 5,
  "total_revenue": 750000.00,
  "total_gross_profit": 150000.00,
  "total_net_profit": 112500.00
}
```

---

## 7. API Quick Reference

### 7.1 SR Reports API Endpoints

| Entity | List | Get | Create | Update | Delete | Special |
|--------|------|-----|--------|--------|--------|---------|
| **ProductDamage** | `GET /damage` | `GET /damage/{id}` | `POST /damage` | `PATCH /damage/{id}` | `DELETE /damage/{id}` | `GET /damage/report` |
| **DailyCostExpense** | `GET /daily-cost` | `GET /daily-cost/{id}` | `POST /daily-cost` | `PATCH /daily-cost/{id}` | `DELETE /daily-cost/{id}` | - |
| **SalesLedger** | `GET /ledger` | `GET /ledger/{id}` | `POST /ledger` | - | `DELETE /ledger/{id}` | - |
| **SalesBudget** | `GET /budget` | `GET /budget/{id}` | `POST /budget` | `PATCH /budget/{id}` | `DELETE /budget/{id}` | Upsert on create |

### 7.2 Aggregated Report Endpoints

| Report | Endpoint |
|--------|----------|
| Group Report | `GET /api/company/sr-reports/group-report?group_id=X&start_date=Y&end_date=Z` |
| DO Tracking | `GET /api/company/sr-reports/do-tracking?start_date=X&end_date=Y` |
| Reconciliation | `GET /api/company/sr-reports/reconciliation?start_date=X&end_date=Y` |
| Slow Moving | `GET /api/company/sr-reports/slow-moving?start_date=X&end_date=Y&threshold_days=30` |
| Daily Report | `GET /api/company/sr-reports/daily-report?report_date=YYYY-MM-DD` |
| Cost & Profit | `GET /api/company/sr-reports/cost-profit?start_date=X&end_date=Y` |
| Undelivery | `GET /api/company/sr-reports/undelivery?start_date=X&end_date=Y` |
| DO Cash | `GET /api/company/sr-reports/do-cash?start_date=X&end_date=Y` |

### 7.3 Main Reports API Endpoints

| Report | Endpoint |
|--------|----------|
| Inventory KPI | `GET /api/company/reports/inventory` |
| Product Stock | `GET /api/company/reports/inventory/product-report?product_id=X&variant_id=Y` |
| Purchase Order Report | `GET /api/company/reports/procurement/purchase-order-report?year=N` |
| Sales Fulfillment | `GET /api/company/reports/sales/fulfillment?start_date=X&end_date=Y` |
| Sales Profitability | `GET /api/company/reports/sales/profitability?start_date=X&end_date=Y` |
| SR Summary | `GET /api/company/reports/sr-summary?start_date=X&end_date=Y&sr_id=Z` |
| SR Product Variants | `GET /api/company/reports/sr-product-variants/{sr_id}?start_date=X&end_date=Y` |
| SR Variant Details | `GET /api/company/reports/sr-product-variant-details/{sr_id}?product_id=X&variant_id=Y` |
| DSR Summary | `GET /api/company/reports/dsr-summary?start_date=X&end_date=Y&dsr_id=Z` |
| DSR Loading | `GET /api/company/reports/dsr-loading/{dsr_id}?start_date=X&end_date=Y` |
| DSR SO Breakdown | `GET /api/company/reports/dsr-so-breakdown/{dsr_id}?product_id=X&variant_id=Y` |

### 7.4 Frontend API Function Map

| Operation | Frontend Function | Backend Endpoint |
|-----------|-------------------|----------------|
| Get Damage List | `getDamageReport()` | `GET /api/company/sr-reports/damage` |
| Create Damage | `createDamage(data)` | `POST /api/company/sr-reports/damage` |
| Update Damage | `updateDamage(id, data)` | `PATCH /api/company/sr-reports/damage/{id}` |
| Delete Damage | `deleteDamage(id)` | `DELETE /api/company/sr-reports/damage/{id}` |
| Get Daily Costs | `getDailyCosts()` | `GET /api/company/sr-reports/daily-cost` |
| Create Daily Cost | `createDailyCost(data)` | `POST /api/company/sr-reports/daily-cost` |
| Get Budgets | `getBudgets()` | `GET /api/company/sr-reports/budget` |
| Create Budget | `createBudget(data)` | `POST /api/company/sr-reports/budget` |
| Get Ledger | `getLedgerEntries()` | `GET /api/company/sr-reports/ledger` |
| Create Ledger Entry | `createLedgerEntry(data)` | `POST /api/company/sr-reports/ledger` |
| Get Group Report | `getGroupReport(groupId, dates)` | `GET /api/company/sr-reports/group-report` |
| Get SR Summary | `getSRSummaryReport(dates, srId)` | `GET /api/company/reports/sr-summary` |
| Get DSR Summary | `getDSRSummaryReport(dates, dsrId)` | `GET /api/company/reports/dsr-summary` |
| Get Inventory Report | `getInventoryReport()` | `GET /api/company/reports/inventory` |
| Get Purchase Order Report | `getPurchaseOrderReport(params)` | `GET /api/company/reports/procurement/purchase-order-report` |

---

## 8. File Map

### 8.1 Backend Files

| Layer | File Path | Purpose |
|-------|-----------|---------|
| **Models** | `Shoudagor/app/models/sr_reports.py` | ProductDamage, DailyCostExpense, SalesLedger, SalesBudget models |
| **Schemas** | `Shoudagor/app/schemas/sr_reports.py` | Pydantic schemas for SR reports |
| **Schemas** | `Shoudagor/app/schemas/reports.py` | Pydantic schemas for main reports |
| **Schemas** | `Shoudagor/app/schemas/dsr_reports.py` | Pydantic schemas for DSR reports |
| **Repositories** | `Shoudagor/app/repositories/sr_reports.py` | ProductDamageRepository, DailyCostExpenseRepository, SalesLedgerRepository, SalesBudgetRepository |
| **Repositories** | `Shoudagor/app/repositories/sr_report_aggregations.py` | GroupReportRepository, DOTrackingRepository, ReconciliationRepository, SlowMovingRepository, DailyReportRepository |
| **Services** | `Shoudagor/app/services/reports.py` | ReportsService - main report generation logic |
| **API** | `Shoudagor/app/api/sr_reports.py` | SR Reports API endpoints (778 lines) |
| **API** | `Shoudagor/app/api/reports.py` | Main Reports API endpoints (763 lines) |

### 8.2 Frontend Files

| Layer | File Path | Purpose |
|-------|-----------|---------|
| **Pages** | `shoudagor_FE/src/pages/reports/Reports.tsx` | Main reports dashboard |
| **Pages** | `shoudagor_FE/src/pages/reports/DamageReport.tsx` | Damage report management |
| **Pages** | `shoudagor_FE/src/pages/reports/GroupReport.tsx` | Group daily movement report |
| **Pages** | `shoudagor_FE/src/pages/reports/DailyReport.tsx` | Daily operational summary |
| **Pages** | `shoudagor_FE/src/pages/reports/DOTrackingReport.tsx` | DO tracking |
| **Pages** | `shoudagor_FE/src/pages/reports/ReconciliationReport.tsx` | Reconciliation |
| **Pages** | `shoudagor_FE/src/pages/reports/SlowMovingReport.tsx` | Slow moving products |
| **Pages** | `shoudagor_FE/src/pages/reports/CostProfitReport.tsx` | Cost & profit analysis |
| **Pages** | `shoudagor_FE/src/pages/reports/BudgetManagement.tsx` | Budget management |
| **Pages** | `shoudagor_FE/src/pages/reports/LedgerManagement.tsx` | Ledger entries |
| **Pages** | `shoudagor_FE/src/pages/reports/SRReports.tsx` | SR performance |
| **Pages** | `shoudagor_FE/src/pages/reports/DSRReports.tsx` | DSR performance |
| **Pages** | `shoudagor_FE/src/pages/reports/SRProgramChannelAdmin.tsx` | Channel admin |
| **Pages** | `shoudagor_FE/src/pages/reports/SRProgramWorkflow.tsx` | Workflow view |
| **Pages** | `shoudagor_FE/src/pages/reports/Inventory.tsx` | Inventory report |
| **Pages** | `shoudagor_FE/src/pages/reports/PurchaseOrder.tsx` | PO report |
| **Pages** | `shoudagor_FE/src/pages/reports/sales/*.tsx` | Sales reports (10 files) |
| **Pages** | `shoudagor_FE/src/pages/reports/inventory/*.tsx` | Inventory reports (10 files) |
| **API** | `shoudagor_FE/src/lib/api/srReportsApi.ts` | SR reports API functions |
| **API** | `shoudagor_FE/src/lib/api/dsrReportsApi.ts` | DSR reports API functions |
| **API** | `shoudagor_FE/src/lib/api/reportsApi.ts` | Main reports API functions |
| **Schemas** | `shoudagor_FE/src/lib/schema/purchaseOrderReport.ts` | PO report types |
| **Components** | `shoudagor_FE/src/components/ReportInfo.tsx` | Report information hover card |
| **Components** | `shoudagor_FE/src/components/DateRangePicker.tsx` | Date range selector |

---

## 9. Appendix: Operation Counts

### 9.1 Backend CRUD Operations Summary

| Entity | Backend CRUD Ops | Backend Special Ops | Frontend API Functions | Frontend Components |
|--------|-----------------|---------------------|----------------------|---------------------|
| **ProductDamage** | 5 | 4 | 4 | 1 |
| **DailyCostExpense** | 5 | 1 | 4 | 1 |
| **SalesLedger** | 4 | 1 | 3 | 1 |
| **SalesBudget** | 5 | 2 | 4 | 1 |
| **GroupReport** | 0 | 1 | 1 | 1 |
| **DOTracking** | 0 | 1 | 1 | 1 |
| **Reconciliation** | 0 | 1 | 1 | 1 |
| **SlowMoving** | 0 | 1 | 1 | 1 |
| **DailyReport** | 0 | 2 | 2 | 1 |
| **SR Reports** | 0 | 3 | 3 | 2 |
| **DSR Reports** | 0 | 3 | 3 | 1 |
| **Inventory Reports** | 0 | 8 | 8 | 8 |
| **Sales Reports** | 0 | 8 | 8 | 8 |
| **Purchase Reports** | 0 | 1 | 1 | 2 |
| **Expense Reports** | 0 | 1 | 1 | 1 |
| **TOTAL** | **19** | **38** | **45** | **32** |

### 9.2 Page Component Inventory

| Category | Pages Count | Routes |
|----------|-------------|--------|
| SR Reports | 4 | /reports/sr, /reports/dsr, /reports/sr-program/* |
| Operational Reports | 5 | /reports/damage, /reports/group, /reports/daily, /reports/do-tracking, /reports/reconciliation |
| Financial Reports | 3 | /reports/cost-profit, /reports/budget, /reports/ledger |
| Inventory Reports | 10 | /reports/inventory, /reports/inventory/* |
| Sales Reports | 10 | /reports/sales/* |
| Purchase Reports | 2 | /reports/purchaseorder, /reports/expenses |
| **TOTAL** | **34** | - |

### 9.3 API Endpoint Summary

| API Router | Endpoints Count | Base Path |
|------------|-----------------|-----------|
| sr_reports.py | 27 | `/api/company/sr-reports` |
| reports.py | 28 | `/api/company/reports` |
| **TOTAL** | **55** | - |

---

**Document End**

*This documentation provides a complete reference for the Reports module in the Shoudagor ERP system. For questions or updates, refer to the source files listed in the File Map sections.*
