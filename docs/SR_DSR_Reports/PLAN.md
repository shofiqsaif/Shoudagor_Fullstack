# SR Reports Workflow Incorporation  
## Deep Study + Detailed Implementation Plan (No Implementation Yet)

**Project:** Shoudagor Fullstack  
**Prepared on:** April 1, 2026  
**Requested outcome:** Incorporate spreadsheet-based SR workflow into existing SR Reports, with deep study and full implementation plan only (no code changes yet).

---

## 1) Executive Summary

The current SR report in the system is primarily a **profitability analytics report by SR** (revenue/cost/profit/commission), with drill-downs into product variants and order-level details.  
Your reference SR spreadsheet workflow is a **multi-block operational and financial control board** centered on:

1. Group-wise commission + market credit + total  
2. Channel split matrix (`Muslim Bakary`, `Traders`, `Auto`)  
3. Group-wise sales report + average/day + full-month projection  
4. Group-wise DO cash  
5. Group-wise undelivery (Total/Web/Sample Product)  
6. Periodic comparison/growth table (2023/2024 style)

To incorporate this properly, we should **add a new dedicated SR Program Workflow report page** (not replace current SR profitability page), backed by new APIs and a reusable metrics layer.  
We will use:

- **Product Group** as the `Group` dimension
- **Configurable customer-channel mapping** for channel columns
- **Dynamic year/month comparison** for growth section
- **Exact formula parity** from exported Sheet/XLSX as source of truth

---

## 2) Inputs Studied (Deep Study Scope)

### 2.1 Visual Source Inputs
- `ss/in_1.png` (workflow blocks: commission-credit-total, channel split, projection block)
- `ss/in_2.png` (workflow blocks: DO cash, undelivery, growth table)

### 2.2 Existing System Implementation (Backend)
- SR report API endpoints: `Shoudagor/app/api/reports.py:564`
- SR report services: `Shoudagor/app/services/reports.py:1185`
- SR report repository SQL: `Shoudagor/app/repositories/reports/sr_reports.py:18`
- DSR report repository (for modal/report pattern reuse): `Shoudagor/app/repositories/reports/dsr_reports.py:18`
- Core sales model (SR/SO fields): `Shoudagor/app/models/sales.py:122`
- Product group model: `Shoudagor/app/models/inventory.py:237`

### 2.3 Existing System Implementation (Frontend)
- SR reports page: `shoudagor_FE/src/pages/reports/SRReports.tsx:30`
- SR reports API client: `shoudagor_FE/src/lib/api/srReportsApi.ts:86`
- SR drilldown modals:
  - `shoudagor_FE/src/components/modals/SRDetailModal.tsx:27`
  - `shoudagor_FE/src/components/modals/SRProductVariantDetailModal.tsx:40`
- Route and nav wiring:
  - `shoudagor_FE/src/App.tsx:317`
  - `shoudagor_FE/src/data/navigation.ts:532`

### 2.4 Existing Reporting Foundation
- General sales report interfaces and endpoints: `shoudagor_FE/src/lib/api/reportsApi.ts:75`
- Related sales report repository functions: `Shoudagor/app/repositories/reports/sales_reports.py:270`

---

## 3) Current State Study (System as-is)

## 3.1 What Current SR Report Actually Does

The current SR report stack calculates:

- SR-level totals:
  - order count
  - quantity
  - revenue (based on negotiated price)
  - estimated cost (historical purchase price lateral join)
  - gross profit / margin
  - total commission
  - net profit  
  (`Shoudagor/app/repositories/reports/sr_reports.py:18`)

- Drilldown 1: product-variant aggregation per SR  
  (`Shoudagor/app/repositories/reports/sr_reports.py:112`)

- Drilldown 2: customer/order-level detail for selected product+variant  
  (`Shoudagor/app/repositories/reports/sr_reports.py:188`)

UI presents this as a profitability dashboard + table + click-through modals.

## 3.2 What Current SR Report Does NOT Cover

It does not currently provide the spreadsheet-like workflow blocks for:

- Group-wise market credit table
- Channel split matrix with custom columns
- DO cash by group
- Undelivery by group with multiple undelivery dimensions
- Growth/year comparison matrix with month span logic

## 3.3 Data Model Readiness Check

- `inventory.product_group` exists and is suitable for your `Group` labels  
  (`Shoudagor/app/models/inventory.py:237`)
- `sales.customer` has financial fields including `store_credit`, but no direct workflow-specific channel dimension like `Muslim Bakary/Traders/Auto`  
  (`Shoudagor/app/models/sales.py:46`)
- SR commission + disbursement data is available in SR order + disbursement flow  
  (`Shoudagor/app/models/sales.py:520`, `Shoudagor/app/models/sales.py:591` neighborhood)

## 3.4 Important Consistency Observation

Some existing sales report logic filters `order_source = 'sr_order'` in pipeline functions, while consolidation sets `order_source = 'sr_consolidated'`.  
- Pipeline code: `Shoudagor/app/repositories/reports/sales_reports.py:504`, `:728`
- Consolidation writes: `Shoudagor/app/services/consolidation_service.py:401`

This inconsistency must be addressed during workflow integration to avoid miscounting SR-derived sales.

---

## 4) Spreadsheet Workflow Reverse Engineering (Block-by-Block)

> Note: Below reflects what is visibly inferable from screenshots. Final formulas must be locked from Sheet/XLSX export.

## 4.1 Block A — Group Financial Summary
Columns seen:
- `Group`
- `Comision`
- `Market Credit`
- `Total`

Interpretation:
- Group-level money position where `Total` likely combines commission and market credit components.

## 4.2 Block B — Channel Split Matrix
Rows:
- Group names (Gems, Ketchup, Juicepack, Wonder, Treat, Danish, milkman)
Columns:
- `Muslim Bakary`, `Traders`, `Auto`, `Total`

Interpretation:
- Group values distributed by channel/customer segment; row totals and grand totals.

## 4.3 Block C — Sales + Projection
Columns:
- `Group`
- `Sales Report`
- `Average sales/Day`
- `Sales Projection` (Full Month)

Interpretation:
- For each group: current period sales, daily average, projected month total.

## 4.4 Block D — Group Wise DO Cash
Columns:
- `Group`
- `DO Cash`

Interpretation:
- Group-level delivered/order cash position (possibly collected vs expected depending source logic).

## 4.5 Block E — Group Wise Undelivery
Columns:
- `Group`
- `Total Undelivery`
- `Web Undelivery`
- `Undelivery Sample Product`

Interpretation:
- Unfulfilled value/quantity decomposition with specific sub-types.

## 4.6 Block F — Growth/Year Comparison Table
Visible pattern:
- Year markers (2023/2024 style)
- Monthly columns
- Growth % and growth volume

Interpretation:
- Compare selected month range across two years at group level.

## 4.7 Formula Confidence Split
- High confidence: dimensional intent and section structure.
- Medium confidence: each KPI’s data source mapping.
- Low confidence: exact hidden formulas, date window specifics, rounding/override behavior.

Therefore formula extraction from source workbook is mandatory before implementation starts.

---

## 5) Gap Analysis (Existing vs Desired)

| Area | Existing SR Reports | Desired Workflow | Gap |
|---|---|---|---|
| Primary dimension | SR-centric | Group-centric | New group-first aggregates needed |
| Channel split | Not explicit | Muslim Bakary / Traders / Auto | Need configurable customer-channel mapping |
| Projection | Not in SR report | avg/day + full month projection | New metric block + formula parity |
| DO cash | Not in SR report | Group DO cash | New metric definition + query |
| Undelivery split | Partial in other sales contexts | Group + web + sample undelivery | New consolidated workflow metric |
| Growth matrix | No dedicated SR program growth table | Dynamic period comparison | New comparison endpoint and UI |
| Formula parity | DB-driven report metrics | Match sheet workflow exactly | Need formula source extraction/lock |

---

## 6) Target Architecture (Recommended)

## 6.1 Product Decision
Keep existing SR profitability report page (`/reports/sr`) unchanged.  
Add new workflow page:
- `/reports/sr-program`

## 6.2 Backend Components to Add
- New repository module for SR Program workflow aggregates.
- Service orchestrator for all workflow blocks.
- API endpoints returning block-wise response.
- Channel mapping CRUD endpoints.

## 6.3 Frontend Components to Add
- New page `SRProgramWorkflow.tsx`
- Section components for each workflow block
- Filter bar (date range + compare period + group + channel)
- Table and summary cards matching sheet mental model

---

## 7) Public API / Interface Specification (Detailed)

## 7.1 Main Workflow Endpoint
`GET /reports/sr-program/workflow`

### Query params
- `start_date` (required)
- `end_date` (required)
- `compare_start_date` (optional, for growth)
- `compare_end_date` (optional, for growth)
- `group_ids` (optional, comma-separated)
- `channel_ids` (optional, comma-separated)
- `projection_mode` (optional: `sheet_exact`, `calendar_day`, `working_day`; default `sheet_exact`)

### Response (high-level)
```json
{
  "meta": {
    "start_date": "2026-03-01",
    "end_date": "2026-03-25",
    "compare_start_date": "2025-03-01",
    "compare_end_date": "2025-03-25",
    "projection_mode": "sheet_exact",
    "currency": "BDT"
  },
  "group_financials": {
    "rows": [],
    "totals": {}
  },
  "channel_split": {
    "channels": [],
    "rows": [],
    "column_totals": {},
    "grand_total": 0
  },
  "sales_projection": {
    "rows": [],
    "totals": {}
  },
  "do_cash": {
    "rows": [],
    "total": 0
  },
  "undelivery": {
    "rows": [],
    "totals": {}
  },
  "growth": {
    "base_period": {},
    "compare_period": {},
    "rows": [],
    "totals": {}
  }
}
```

## 7.2 Channel Mapping Endpoints
- `GET /reports/sr-program/channel-mappings`
- `PUT /reports/sr-program/channel-mappings` (bulk replace/upsert)

### Mapping contract
- channel id/name/order
- customer assignment list
- company-scoped isolation

---

## 8) Data Model / Migration Plan

## 8.1 New Tables (Recommended)

### A) Channel master
- `reports.sr_program_channel`
  - `channel_id` PK
  - `channel_name` (e.g., Muslim Bakary, Traders, Auto)
  - `display_order`
  - `is_active`
  - `company_id`
  - audit fields + soft delete

### B) Customer-channel mapping
- `reports.sr_program_customer_channel`
  - `mapping_id` PK
  - `customer_id` FK
  - `channel_id` FK
  - `company_id`
  - audit fields + soft delete
  - unique(company_id, customer_id)

## 8.2 Existing Tables Used
- Sales orders and details
- SR orders and details
- customer
- product/product_variant
- product_group + product_group_items
- delivery/payment detail tables where needed for DO cash / undelivery logic

---

## 9) Metric Definition Strategy (Decision-Complete)

## 9.1 Formula Source of Truth
Before coding any SQL:
1. Export source spreadsheet to XLSX.
2. Extract formulas for each target metric.
3. Lock a metric spec document with:
   - source range
   - equation
   - data mapping
   - rounding/formatting
   - null behavior

No implementation starts until this metric spec is approved.

## 9.2 Group Mapping Rule
- Group dimension = `inventory.product_group.group_name`
- If product belongs to multiple groups, apply deterministic assignment policy (to be defined in formula spec—single-primary or split logic).
- If product has no group, route to `Ungrouped` bucket.

## 9.3 Channel Mapping Rule
- Channel derived from customer-channel mapping table.
- Unmapped customers go to `Unmapped` until assigned.
- Channel display order controlled by channel master table.

## 9.4 Date Logic Rule
- `sheet_exact` mode uses workbook-equivalent elapsed-day logic.
- Growth section supports independent base/compare ranges.

---

## 10) Backend Implementation Plan (Detailed)

## Phase 0 — Formula Extraction & Lock
- Build one-time extraction script/notebook from XLSX.
- Produce `SR_PROGRAM_METRIC_SPEC.md` with final formulas.
- Validate sample rows against screenshot outputs where possible.

## Phase 1 — Schema + Repository Foundation
- Add channel master/mapping migrations.
- Add repository methods:
  - base fact CTE by date/company
  - group financials query
  - channel split query
  - sales projection query
  - DO cash query
  - undelivery query
  - growth comparison query

## Phase 2 — Service Orchestration
- Build `get_sr_program_workflow(...)` service:
  - executes all block queries
  - applies formula transformations
  - computes totals and metadata
  - harmonizes decimal/currency precision

## Phase 3 — API Layer
- Add FastAPI routes under reports router.
- Add strict validation for date range and compare range.
- Add channel mapping CRUD endpoints with scope checks.

## Phase 4 — Data Consistency Hardening
- Align SR source filters (`sr_order` vs `sr_consolidated`) where needed.
- Add test guards so future changes cannot reintroduce inconsistent source logic.

## Phase 5 — Performance Optimization
- Add indexes for mapping tables and report-heavy predicates.
- Cache static channel mapping for report requests.
- Use CTE pre-aggregation to avoid repeated scans across blocks.

---

## 11) Frontend Implementation Plan (Detailed)

## 11.1 New Route and Navigation
- Add route: `/reports/sr-program`
- Add nav item: “SR Program Workflow”
- Keep existing `/reports/sr` unchanged

## 11.2 New API Client
- Add `srProgramReportsApi.ts` with:
  - `getSRProgramWorkflow(...)`
  - `getSRProgramChannelMappings()`
  - `updateSRProgramChannelMappings(...)`

## 11.3 Page Composition
- Header + filter controls (date range, compare range, group, channel)
- Section A: Group Financial Summary
- Section B: Channel Split Matrix
- Section C: Sales Projection
- Section D: Group DO Cash
- Section E: Group Undelivery
- Section F: Growth Comparison Table

## 11.4 UX Rules
- Consistent BDT formatting, negative values highlighted
- Frozen header + horizontal scroll for wide matrices
- Skeleton loading + clear empty states
- Export-friendly table layout parity with sheet format

---

## 12) Testing Plan (Comprehensive)

## 12.1 Backend Unit Tests
- Metric computation tests per block
- Date range edge tests
- Mapping fallback tests (`Unmapped`, `Ungrouped`)
- Decimal precision and rounding tests

## 12.2 Backend Integration Tests
- End-to-end `GET /reports/sr-program/workflow`
- Channel mapping CRUD with company isolation
- Comparison mode across dynamic year ranges

## 12.3 Golden Parity Tests (Critical)
- Build fixture dataset from source sheet period
- Assert each block’s row values and totals match locked formula outputs
- Tolerance only where explicitly allowed by spec

## 12.4 Frontend Tests
- Page render test with all sections
- Filter interaction tests (query-key and refetch correctness)
- Column totals and grand totals display checks
- Error/empty/loading state tests

## 12.5 Regression Tests
- Existing SR profitability report (`/reports/sr`) remains unchanged
- Existing DSR reports unaffected
- Existing sales report routes unaffected

---

## 13) Rollout Plan

## Stage 1 — Internal QA
- Run parity suite with known period data
- Validate with stakeholders against source workbook

## Stage 2 — Feature Flag (Optional but recommended)
- Gate new page via config/permission toggle for limited users

## Stage 3 — Controlled Launch
- Enable for reporting/admin users
- Monitor response times and mismatch incidents

## Stage 4 — Full Availability
- Update internal user guide + quick walkthrough video/screens

---

## 14) Risks & Mitigations

1. **Formula mismatch risk**  
   - Mitigation: formula-lock phase + golden parity tests before release.

2. **Ambiguous data ownership for channel**  
   - Mitigation: explicit customer-channel mapping with admin maintenance UI.

3. **Order source inconsistency in existing reports**  
   - Mitigation: normalize SR source semantics and add regression tests.

4. **Performance risk from multi-block aggregates**  
   - Mitigation: shared base CTEs, indexes, and selective caching.

5. **Unmapped products/customers**  
   - Mitigation: explicit `Ungrouped` and `Unmapped` buckets + mapping completeness dashboard.

---

## 15) Acceptance Criteria (Definition of Done)

- New `/reports/sr-program` page available and stable.
- All six workflow blocks render with totals and formatting.
- Dynamic compare period works for growth section.
- Channel mapping endpoints functional and secured by company.
- Formula parity suite passes against locked spec.
- Existing `/reports/sr` profitability report unchanged.
- Documentation updated with metric definitions and mapping admin guide.

---

## 16) Detailed Task Breakdown

## Backend
1. Create migration for channel and customer-channel mapping tables.
2. Add repository queries for all workflow blocks.
3. Add service orchestrator response assembler.
4. Add report endpoints + validation.
5. Add channel mapping CRUD endpoints.
6. Add unit/integration/parity test suites.
7. Normalize SR source semantics where required.

## Frontend
1. Add new route + nav entry.
2. Add API client interfaces and hooks.
3. Build SR Program page sections.
4. Build filter bar and compare-period controls.
5. Implement table totals/highlights/formatting.
6. Add tests and loading/error/empty states.

## Documentation
1. Metric spec document from sheet formulas.
2. Channel mapping admin usage doc.
3. SR Program report user guide with examples.

---

## 17) File-Level Change Intent (for implementation phase)

> No edits now (planning only).  
> Expected touchpoints during implementation:

- Backend:
  - `Shoudagor/app/api/reports.py:564` (add new SR Program endpoints nearby)
  - `Shoudagor/app/services/reports.py:1185` (add SR Program service methods)
  - `Shoudagor/app/repositories/reports/` (new SR Program repo module)
  - `Shoudagor/app/schemas/` (new SR Program response/request schemas)
  - new Alembic migration files for channel mapping tables

- Frontend:
  - `shoudagor_FE/src/App.tsx:317` (new route)
  - `shoudagor_FE/src/data/navigation.ts:532` (new nav item)
  - new page under `shoudagor_FE/src/pages/reports/`
  - new API client under `shoudagor_FE/src/lib/api/`

---

## 18) Assumptions Locked from This Planning Session

- Group basis: **Product Group** (recommended and accepted)
- Channel split source: **Config mapping table** (recommended and accepted)
- UI placement: **new SR Program page** (recommended and accepted)
- YoY/growth: **dynamic years + month range** (recommended and accepted)
- Formula source: **actual sheet export/access** (recommended and accepted)
- Plan file target path (when execution mode is available):  
  `plans/sr_reports_workflow_plan.md`

---

## 19) Final Note

This plan is intentionally exhaustive and implementation-ready.  
No coding, no schema mutation, and no file writing has been performed in this step (as requested).
