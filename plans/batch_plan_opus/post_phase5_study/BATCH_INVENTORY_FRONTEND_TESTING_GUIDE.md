# Batch Inventory Frontend Testing Guide

## Overview

This document provides comprehensive testing instructions for the Batch Inventory feature implementations in the Shoudagor ERP frontend. It covers all implemented pages, API endpoints, test scenarios, and validation procedures.

---

## Table of Contents

1. [Prerequisites & Test Data Requirements](#1-prerequisites--test-data-requirements)
2. [Implemented Pages & Routes](#2-implemented-pages--routes)
3. [API Endpoints Reference](#3-api-endpoints-reference)
4. [Testing Each Page](#4-testing-each-page)
5. [Integration Testing Scenarios](#5-integration-testing-scenarios)
6. [Test Scenarios by Workflow](#6-test-scenarios-by-workflow)
7. [Troubleshooting & Common Issues](#7-troubleshooting--common-issues)
8. [Testing Checklist](#8-testing-checklist)

---

## 1. Prerequisites & Test Data Requirements

### 1.1 Backend Prerequisites

Before testing the frontend, ensure the following backend components are in place:

| Requirement | Description | How to Verify |
|-------------|-------------|---------------|
| Database Migration | Run Alembic migration for batch tables | Check `inventory.batch`, `inventory.inventory_movement` tables exist |
| Company Settings | Enable batch tracking for test company | POST to `/api/company/inventory/settings` with `batch_tracking_enabled: true` |
| Sample Data | Create test products, suppliers, locations | Create at least 2 products with variants |
| PO Deliveries | Create purchase order deliveries | These create batches automatically |

### 1.2 Enabling Batch Tracking

Before testing, you must enable batch tracking for your company:

```bash
# Enable batch tracking via API
curl -X POST "http://localhost:8000/api/company/inventory/settings" \
  -H "Content-Type: application/json" \
  -d '{
    "valuation_mode": "FIFO",
    "batch_tracking_enabled": true
  }'
```

Or via the Settings page:
1. Navigate to **Settings** → **Invoice** tab
2. Find **Batch Inventory** section
3. Enable **Batch Tracking** toggle
4. Select **Valuation Mode** (FIFO, LIFO, or WEIGHTED_AVG)
5. Click Save

### 1.3 Required Test Data

Create the following test data for comprehensive testing:

| Data Type | Required | Description |
|------------|----------|-------------|
| Products | 3+ | At least 2 products with variants |
| Suppliers | 2+ | For batch supplier filtering |
| Storage Locations | 2+ | For location filtering |
| Purchase Orders | 2+ | With deliveries to create batches |
| Sales Orders | 2+ | With deliveries to test allocation |
| Inventory Stock | Existing | Legacy stock for reconciliation testing |

---

## 2. Implemented Pages & Routes

### 2.1 Batch Inventory Navigation

The Batch Inventory section is located in the sidebar navigation:

```
Batch Inventory (Package Icon)
├── Batch Drilldown       → /inventory/batch-drilldown
├── Movement Ledger       → /inventory/movement-ledger
├── Reconciliation        → /inventory/reconciliation
└── Backfill             → /inventory/backfill
```

### 2.2 All Batch-Related Routes

| Route | Page Component | Description |
|-------|---------------|-------------|
| `/inventory/batch-drilldown` | `BatchDrillDown.tsx` | View and manage batches |
| `/inventory/movement-ledger` | `MovementLedger.tsx` | View all inventory movements |
| `/inventory/reconciliation` | `BatchReconciliation.tsx` | View batch vs stock mismatches |
| `/inventory/backfill` | `BatchBackfill.tsx` | Run backfill to create historical batches |
| `/reports/inventory/stock-by-batch` | `StockByBatch.tsx` | Stock by batch report |
| `/reports/inventory/inventory-aging-batch` | `InventoryAgingBatch.tsx` | Batch-based aging report |
| `/reports/inventory/cogs-by-period` | `COGSByPeriod.tsx` | COGS from movement ledger |
| `/reports/inventory/margin-analysis` | `MarginAnalysis.tsx` | Margin analysis report |
| `/reports/inventory/batch-pnl` | `BatchPnL.tsx` | Batch P&L report |

### 2.3 Settings Integration

Batch inventory settings are configured in:
- **Location**: Settings → Invoice tab → Batch Inventory section
- **Route**: `/settings/invoice`

---

## 3. API Endpoints Reference

### 3.1 Batch Management APIs

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/company/inventory/batches` | List batches with filters |
| GET | `/api/company/inventory/batches/{id}` | Get batch detail with movements |
| POST | `/api/company/inventory/batches` | Create new batch |
| PATCH | `/api/company/inventory/batches/{id}` | Update batch metadata |

**Query Parameters for GET /batches:**
```
product_id, variant_id, location_id, supplier_id, status, 
include_depleted, start, limit
```

### 3.2 Inventory Movement APIs

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/company/inventory/movements` | Query movement ledger |

**Query Parameters:**
```
batch_id, product_id, variant_id, movement_type, ref_type,
location_id, start_date, end_date, start, limit
```

### 3.3 Settings APIs

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/company/inventory/settings` | Get company settings |
| POST | `/api/company/inventory/settings` | Create/update settings |

### 3.4 Report APIs

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/company/reports/stock-by-batch` | Stock by batch report |
| GET | `/api/company/reports/inventory-aging` | Batch-based aging |
| GET | `/api/company/reports/cogs-by-period` | COGS by period |
| GET | `/api/company/reports/batch-pnl` | Batch P&L |
| GET | `/api/company/reports/margin-analysis` | Margin analysis |
| GET | `/api/company/products/{id}/batches` | Product batch drill-down |

### 3.5 Reconciliation & Backfill APIs

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/company/inventory/reconciliation` | Get reconciliation report |
| GET | `/api/company/inventory/reconciliation/product/{id}` | Product-specific reconciliation |
| POST | `/api/company/inventory/reconciliation/backfill` | Run batch backfill |
| POST | `/api/company/inventory/reconciliation/backfill-sales` | Run sales allocation backfill |

---

## 4. Testing Each Page

### 4.1 Batch Drill-Down Page

**Route**: `/inventory/batch-drilldown`

#### Features to Test

| Feature | Test Steps | Expected Result |
|---------|------------|-----------------|
| Page Load | Navigate to page | Page loads without errors, shows batch table |
| Filter by Product | Select a product from dropdown | Table filters to show only batches for that product |
| Filter by Location | Select a location | Table shows batches only for that location |
| Filter by Supplier | Select a supplier | Table shows batches from that supplier |
| Filter by Status | Select status (active/depleted/etc.) | Table shows batches with matching status |
| Pagination | Click Next/Previous | Table navigates to next/previous page |
| Export CSV | Click Export CSV button | CSV file downloads with current batch data |
| Batch Detail Modal | Click eye icon on a batch | Modal opens showing batch details and movement history |
| Cost Lock Indicator | Look for lock icon | Lock icon appears on batches with OUT movements |

#### Test Data Requirements

- At least 5 batches with different statuses (active, depleted)
- Batches from different products, locations, and suppliers

#### Validation Formulas

```
Total Qty On Hand (displayed) = SUM(batch.qty_on_hand) for all displayed batches
Average Cost (displayed) = SUM(qty_on_hand * unit_cost) / SUM(qty_on_hand)
```

---

### 4.2 Movement Ledger Page

**Route**: `/inventory/movement-ledger`

#### Features to Test

| Feature | Test Steps | Expected Result |
|---------|------------|-----------------|
| Page Load | Navigate to page | Page loads, shows movement table |
| Filter by Product | Select product | Table shows movements for that product only |
| Filter by Batch ID | Enter batch ID | Table shows movements for that batch |
| Filter by Movement Type | Select type (IN/OUT/etc.) | Table shows only movements of that type |
| Filter by Date Range | Set start and end dates | Table shows movements within date range |
| Filter by Location | Select location | Table shows movements at that location |
| Movement Type Badges | Check badge colors | IN=green, OUT=red, RETURN_IN=blue, ADJUSTMENT=yellow |
| Pagination | Navigate through pages | Table shows correct page of results |
| Export | Click export button | CSV downloads with movement data |

#### Test Data Requirements

- At least 20 movements covering different types
- Movements from different dates, products, and batches

#### Validation Formulas

```
Total IN Qty = SUM(qty) WHERE movement_type = 'IN'
Total OUT Qty = ABS(SUM(qty)) WHERE movement_type = 'OUT'
Net Change = Total IN - Total OUT
```

---

### 4.3 Reconciliation Page

**Route**: `/inventory/reconciliation`

#### Features to Test

| Feature | Test Steps | Expected Result |
|---------|------------|-----------------|
| Page Load | Navigate to page | Page loads, shows reconciliation summary |
| Summary Cards | Check displayed values | Shows total batches, mismatches, products checked |
| Mismatch Table | View mismatches section | Shows products where batch qty ≠ stock qty |
| Empty State | Before any backfill | Shows message to run backfill |
| Product Details | Click on product row | Expands to show variant-level details |

#### Understanding Reconciliation Results

| Term | Description |
|------|-------------|
| Total Batches | Number of batches in the system |
| Mismatches Found | Products where batch total ≠ inventory stock |
| Products Checked | Total products analyzed |
| Match Rate | (Products Matched / Products Checked) × 100 |

---

### 4.4 Backfill Page

**Route**: `/inventory/backfill`

#### Features to Test

| Feature | Test Steps | Expected Result |
|---------|------------|-----------------|
| Page Load | Navigate to page | Page loads with backfill options |
| Dry Run Toggle | Toggle dry run on/off | Toggle changes mode (preview vs execute) |
| Chunk Size | Adjust chunk size slider | Value updates in request |
| Backfill Type | Select batches or sales | Different backfill operations |
| Run Backfill | Click Run button | Progress shown, results displayed |
| Results Summary | View after completion | Shows batches created, records processed |
| Reconciliation Report | Check reconciliation section | Shows mismatches before/after |
| Error Handling | Run with no data | Appropriate error message shown |

#### Backfill Modes

| Mode | Behavior | Risk Level |
|------|----------|------------|
| Dry Run (default) | Shows what would happen, no data changes | Safe |
| Execute | Actually creates/modifies data | Requires caution |

#### Test Scenario: Dry Run

1. Set Dry Run: ON
2. Select Chunk Size: 500
3. Click Run Backfill
4. Verify: Results show planned changes but no actual data modification
5. Check: Reconciliation report shows current mismatches

#### Test Scenario: Execute Backfill

1. **WARNING**: Only run with test data or during low-traffic period
2. Set Dry Run: OFF
3. Click Run Backfill
4. Verify: Batches are created in database
5. Verify: Reconciliation shows reduced mismatches

---

### 4.5 Stock by Batch Report

**Route**: `/reports/inventory/stock-by-batch`

#### Features to Test

| Feature | Test Steps | Expected Result |
|---------|------------|-----------------|
| Page Load | Navigate to page | Report loads with summary cards |
| Summary Cards | Check values | Total Batches, Total Value, Active Batches |
| Filter by Product | Select product | Table filters accordingly |
| Filter by Location | Select location | Table filters accordingly |
| Table Data | Check columns | Batch ID, Product, SKU, Qty, Cost, Value |
| Export | Click export | CSV downloads |

#### Validation Formulas

```
Total Value = SUM(qty_on_hand * unit_cost) for all batches
Average Cost = Total Value / SUM(qty_on_hand)
```

---

### 4.6 Inventory Aging (Batch-Based) Report

**Route**: `/reports/inventory/inventory-aging-batch`

#### Features to Test

| Feature | Test Steps | Expected Result |
|---------|------------|-----------------|
| Page Load | Navigate to page | Report loads with aging buckets |
| Aging Buckets | Check columns | 0-30, 31-60, 61-90, 91-180, 180+ days |
| Filter by Location | Select location | Buckets recalculate |
| Summary Values | Check totals | Total qty and value by age bucket |
| Color Coding | Check visual indicators | Different colors for different age ranges |

#### Validation Formulas

```
0-30 Days Qty = SUM(qty_on_hand) WHERE age_days <= 30
31-60 Days Qty = SUM(qty_on_hand) WHERE age_days BETWEEN 31 AND 60
...and so on
```

---

### 4.7 COGS by Period Report

**Route**: `/reports/inventory/cogs-by-period`

#### Features to Test

| Feature | Test Steps | Expected Result |
|---------|------------|-----------------|
| Date Range | Set start and end dates | Report filters by period |
| Period Breakdown | Check grouping | Data grouped by month/period |
| COGS Values | Verify calculations | COGS = SUM(OUT movement qty × unit_cost_at_txn) |
| Export | Export report | CSV downloads |

---

### 4.8 Margin Analysis Report

**Route**: `/reports/inventory/margin-analysis`

#### Features to Test

| Feature | Test Steps | Expected Result |
|---------|------------|-----------------|
| Page Load | Navigate to page | Shows margin analysis by product |
| Filter by Product | Select product | Shows margin for single product |
| Filter by Location | Select location | Filters by warehouse |
| Date Range | Set dates | Shows margin for period |
| Margin Calculation | Verify formula | Margin = Revenue - Cost |
| Margin % | Verify formula | Margin% = (Revenue - Cost) / Revenue × 100 |

---

### 4.9 Batch P&L Report

**Route**: `/reports/inventory/batch-pnl`

#### Features to Test

| Feature | Test Steps | Expected Result |
|---------|------------|-----------------|
| Page Load | Navigate to page | Shows P&L by batch |
| Batch Details | Check columns | Batch ID, Product, Qty Sold, Cost, Revenue, Profit |
| Profit Calculation | Verify | Profit = Revenue - Cost |
| Margin % | Verify | Margin% = Profit / Revenue × 100 |
| Totals | Check summary | Total Revenue, Cost, Profit, Avg Margin |

---

## 5. Integration Testing Scenarios

### 5.1 End-to-End: PO Delivery Creates Batch

**Prerequisites**: Batch tracking enabled

**Test Steps**:

1. Create a new Purchase Order
2. Add product line items with quantity and unit cost
3. Create a Delivery for the PO
4. Navigate to **Batch Drill-Down**
5. Verify: New batch appears with:
   - qty_received = delivered quantity
   - qty_on_hand = delivered quantity (full)
   - unit_cost = PO line unit price
   - status = "active"
6. Navigate to **Movement Ledger**
7. Verify: IN movement exists for the batch

### 5.2 End-to-End: SO Delivery Allocates from Batch

**Prerequisites**: Batch tracking enabled, existing batches

**Test Steps**:

1. Create a Sales Order
2. Add product line items
3. Create a Delivery for the SO
4. Navigate to **Batch Drill-Down**
5. Verify: Batch qty_on_hand decreased
6. Check: Cost lock indicator (lock icon) appears
7. Navigate to **Movement Ledger**
8. Verify: OUT movement exists with correct cost
9. Navigate to **Batch Detail Modal** for the batch
10. Verify: Movement history shows the OUT movement

### 5.3 End-to-End: Sales Return Restores to Batch

**Prerequisites**: Completed sale with batch allocation

**Test Steps**:

1. Create a Sales Return for the previous sale
2. Specify quantity to return
3. Process the return
4. Navigate to **Batch Drill-Down**
5. Verify: Original batch qty_on_hand increased
6. Navigate to **Movement Ledger**
7. Verify: RETURN_IN movement exists linked to original OUT

### 5.4 Valuation Mode Testing

**Test FIFO Mode**:

1. Set company valuation mode to FIFO
2. Create multiple batches at different costs
3. Create a sale
4. Verify: Oldest batch (lowest received_date) is allocated first

**Test LIFO Mode**:

1. Set company valuation mode to LIFO
2. Create multiple batches at different costs
3. Create a sale
4. Verify: Newest batch (highest received_date) is allocated first

**Test Weighted Average Mode**:

1. Set company valuation mode to WEIGHTED_AVG
2. Create batches at different costs
3. Create a sale
4. Verify: Allocations use average cost across all batches

---

## 6. Test Scenarios by Workflow

### 6.1 Pre-Implementation Testing (Before Batch Tracking)

Use these tests to verify the system handles companies without batch tracking:

1. **Disable batch tracking** in settings
2. Create PO delivery → Should NOT create batch
3. Create SO delivery → Should work with legacy stock system
4. Verify: Reports still work in legacy mode

### 6.2 Post-Implementation Testing (After Enabling)

1. **Enable batch tracking** in settings
2. Run **Backfill** (dry run first)
3. Check **Reconciliation** - should show mismatches before backfill
4. Run **Backfill** (execute mode)
5. Check **Reconciliation** - mismatches should reduce
6. Test **PO → Batch → Sale → Return** workflow

### 6.3 Data Integrity Testing

| Test | Expected Result |
|------|-----------------|
| Batch qty_on_hand never negative | DB constraint prevents negative values |
| Movement ledger immutable | No UPDATE/DELETE on movements |
| Cost locked after OUT movement | Cannot edit unit_cost |
| Reconciliation accuracy | Batch total = Stock total after backfill |

---

## 7. Troubleshooting & Common Issues

### 7.1 Page Shows "No Batches Found"

**Possible Causes**:
- Batch tracking not enabled
- No PO deliveries have been created
- Filters are too restrictive

**Solutions**:
1. Verify batch tracking is enabled in Settings
2. Create PO deliveries to generate batches
3. Reset filters to "All"

### 7.2 Reconciliation Shows High Mismatches

**Possible Causes**:
- Backfill not run
- Manual inventory adjustments not reflected in batches
- Concurrent operations caused discrepancies

**Solutions**:
1. Run backfill in dry-run mode first
2. Review mismatches in reconciliation page
3. Run backfill in execute mode to create synthetic batches

### 7.3 Movement Ledger Shows No Data

**Possible Causes**:
- No transactions after enabling batch tracking
- Wrong date range filter

**Solutions**:
1. Clear date filters
2. Create PO delivery to generate IN movement
3. Create SO delivery to generate OUT movement

### 7.4 Backfill Fails or Times Out

**Possible Causes**:
- Large dataset
- Server timeout

**Solutions**:
1. Reduce chunk size (try 100 instead of 500)
2. Run during low-traffic period
3. Break up backfill by location

### 7.5 Cost Lock Indicator Not Showing

**Possible Causes**:
- Batch hasn't been used in sales yet
- qty_on_hand equals qty_received (no OUT movements)

**Solutions**:
1. Create a sale delivery to allocate from the batch
2. Check batch detail modal for movement history

---

## 8. Testing Checklist

### 8.1 Pre-Test Checklist

- [ ] Backend server running and accessible
- [ ] Database migrations applied
- [ ] Test company created
- [ ] Batch tracking enabled for test company
- [ ] Test products created with variants
- [ ] Test suppliers and locations created

### 8.2 Page-by-Page Testing Checklist

#### Batch Drill-Down
- [ ] Page loads successfully
- [ ] Default batch list displays
- [ ] Product filter works
- [ ] Location filter works
- [ ] Supplier filter works
- [ ] Status filter works
- [ ] Pagination works
- [ ] CSV export works
- [ ] Batch detail modal opens
- [ ] Cost lock indicator displays correctly

#### Movement Ledger
- [ ] Page loads successfully
- [ ] Movement list displays
- [ ] All filters work (product, batch, type, date, location)
- [ ] Movement type badges display correctly
- [ ] Pagination works
- [ ] Export works

#### Reconciliation
- [ ] Page loads successfully
- [ ] Summary cards display correct values
- [ ] Mismatch table shows data
- [ ] Empty state displays when no data

#### Backfill
- [ ] Page loads successfully
- [ ] Dry run mode works
- [ ] Execute mode works
- [ ] Chunk size setting works
- [ ] Results display correctly
- [ ] Error handling works

#### Reports
- [ ] Stock by Batch loads and displays data
- [ ] Inventory Aging displays aging buckets correctly
- [ ] COGS by Period calculates correctly
- [ ] Margin Analysis shows correct margins
- [ ] Batch P&L calculates profits correctly
- [ ] All exports work

### 8.3 Integration Testing Checklist

- [ ] PO delivery creates batch
- [ ] PO delivery creates IN movement
- [ ] SO delivery allocates from batch
- [ ] SO delivery creates OUT movement
- [ ] Return restores to original batch
- [ ] Return creates RETURN_IN movement
- [ ] FIFO allocation works correctly
- [ ] LIFO allocation works correctly
- [ ] Weighted Average allocation works correctly

### 8.4 Post-Test Validation

- [ ] No console errors in browser
- [ ] All API calls return 200 status
- [ ] Data displays correctly in all tables
- [ ] Filters produce expected results
- [ ] Pagination works throughout
- [ ] Export files are valid

---

## Appendix: API Quick Reference

### Authentication

All API calls require authentication token. The frontend automatically includes this via the `api` client setup.

### Example API Calls (JavaScript)

```typescript
// Get batches
import { getBatches } from '@/lib/api/batchApi';

const batches = await getBatches({
  product_id: 1,
  location_id: 1,
  status: 'active',
  start: 0,
  limit: 50
});

// Get reconciliation
import { getReconciliationReport } from '@/lib/api/batchApi';

const reconciliation = await getReconciliationReport();

// Run backfill
import { runBackfill } from '@/lib/api/batchApi';

const result = await runBackfill(true, 500); // dryRun=true, chunkSize=500
```

---

## Version History

| Version | Date | Description |
|---------|------|-------------|
| 1.0 | March 2026 | Initial testing guide |

---

*This document is part of the Batch Inventory Implementation documentation suite.*
