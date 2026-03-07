# Batch-Based Inventory Implementation Plan — Phase 3: UI/UX, Rollout & Risk Analysis

## 10. UI/UX — Frontend Component Plan

### 10.1 Technology Context
- **Framework**: React + Vite + TypeScript
- **Styling**: shadcn/ui components (confirmed from `components.json`)
- **State**: React contexts + hooks
- **Pages**: Located in `src/pages/`, components in `src/components/`

### 10.2 New Pages & Components

#### A. Product Stock View (Enhanced)
**File**: `src/pages/products/ProductDetail.tsx` (MODIFY)

Default view shows **friendly totals** — no batch complexity visible until drill-down.

| Element | Description |
|---|---|
| Total Stock badge | `SUM(batch.qty_on_hand)` — aggregated across all locations |
| Average Cost | `SUM(qty_on_hand × unit_cost) / SUM(qty_on_hand)` |
| Valuation summary | Total inventory value at current valuation mode |
| "View Batches" button | Opens drill-down (only for users with batch_view permission) |

#### B. Batch Drill-Down Page
**File**: `src/pages/inventory/BatchDrillDown.tsx` (NEW)

| Component | Description |
|---|---|
| Batch Table | Columns: Batch ID, Lot#, Qty On Hand, Unit Cost, Received Date, Supplier, Age (days), Status |
| Filters | Product, Variant, Location, Supplier, Status, Date Range |
| Pagination | Standard paginated table with 50 rows/page |
| Batch Detail Modal | Click batch → show movement history for that batch |
| Export CSV | Export filtered batch list to CSV |
| Cost Edit Lock indicator | 🔒 icon on batches with OUT movements (cost immutable) |

#### C. Batch Movement Ledger Page
**File**: `src/pages/inventory/MovementLedger.tsx` (NEW)

| Component | Description |
|---|---|
| Movement Table | Columns: Movement ID, Batch ID, Product, Qty, Type, Ref Type, Ref ID (linked), Unit Cost, Actor, Timestamp, Location |
| Filters | Product, Variant, Batch, Movement Type, Ref Type, Date Range, Location |
| Movement Type badges | Color-coded: IN (green), OUT (red), RETURN_IN (blue), ADJUSTMENT (yellow), TRANSFER (purple) |
| Linkable references | Ref ID links to originating PO/SO/Adjustment/Transfer |

#### D. Sales Order — Batch Allocations (Read-Only)
**File**: `src/pages/sales/SalesOrderDetail.tsx` (MODIFY)

| Element | Description |
|---|---|
| Allocation table | Per SO detail line: show allocated batches (Batch ID, Qty, Unit Cost) |
| COGS summary line | Total COGS = sum(qty_allocated × unit_cost_at_allocation) |
| Read-only note | "Batch allocations are computed automatically and cannot be manually modified" |

#### E. Purchase Order — Batch Creation Indicator
**File**: `src/pages/purchases/PurchaseOrderDetail.tsx` (MODIFY)

| Element | Description |
|---|---|
| Batch created badge | After delivery, show "Batch #1042 created" next to delivery detail |
| Link to batch | Click → navigate to Batch Drill-Down filtered for that batch |

#### F. Company Settings — Valuation Mode
**File**: `src/pages/settings/CompanySettings.tsx` (MODIFY)

| Element | Description |
|---|---|
| Valuation Mode dropdown | FIFO (default), LIFO, Weighted Average |
| Batch Tracking toggle | Enable/disable batch tracking (feature flag) |
| Warning on change | "Changing valuation mode will affect future transactions only. Historical COGS remains unchanged." |

### 10.3 New Report Pages

| Report | File | Description |
|---|---|---|
| Stock by Batch | `src/pages/reports/inventory/StockByBatch.tsx` | Grid: Product → Batches → Qty, Cost, Age, Location |
| Inventory Aging | `src/pages/reports/inventory/InventoryAging.tsx` | Replace current aging report with batch-based aging (0-30, 31-60, 61-90, 90+ days) |
| COGS by Period | `src/pages/reports/inventory/COGSByPeriod.tsx` | Monthly/quarterly COGS from movement ledger, broken by product |
| Margin Analysis | `src/pages/reports/inventory/MarginAnalysis.tsx` | Selling price vs actual batch cost, margin % per product/period |
| Batch P&L | `src/pages/reports/inventory/BatchPnL.tsx` | Per-batch: qty sold, revenue, cost, profit, margin |

### 10.4 Role-Based Visibility

| Feature | Warehouse Staff | Accountant | Admin |
|---|---|---|---|
| Product stock (totals) | ✅ | ✅ | ✅ |
| Batch drill-down | ✅ (qty only) | ✅ (qty + cost) | ✅ |
| Movement ledger | ❌ | ✅ | ✅ |
| SO batch allocations | ❌ | ✅ (read-only) | ✅ |
| COGS/Margin reports | ❌ | ✅ | ✅ |
| Valuation mode settings | ❌ | ❌ | ✅ |
| Batch cost edit | ❌ | ❌ | ❌ (immutable by design) |

### 10.5 New Screens in Security System

Register the following screens in `security.screen` table:

| Screen Name | Controller | Action | Module | Section |
|---|---|---|---|---|
| Batch Drill-Down | inventory | batch-drilldown | Inventory | Stock Management |
| Movement Ledger | inventory | movement-ledger | Inventory | Stock Management |
| Stock by Batch Report | reports | stock-by-batch | Reports | Inventory Reports |
| COGS Report | reports | cogs-by-period | Reports | Financial Reports |
| Margin Analysis | reports | margin-analysis | Reports | Financial Reports |
| Batch P&L | reports | batch-pnl | Reports | Financial Reports |
| Inventory Aging (Batch) | reports | inventory-aging-batch | Reports | Inventory Reports |
| Company Batch Settings | settings | batch-settings | Settings | Company |

---

## 11. System Rules & Safeguards

### 11.1 Cost Immutability
- `Batch.unit_cost` **CANNOT** be modified once any `OUT` movement exists for that batch.
- Service-layer enforcement: `BatchService.update_batch()` checks for OUT movements before allowing cost edit.
- API returns `409 Conflict` with message: "Cannot modify unit cost for a batch that has been used in sales. Create an accounting journal entry instead."

### 11.2 Ledger Immutability
- `inventory_movement` records are **never physically deleted** or updated.
- "Deletion" creates a new `ADJUSTMENT` movement that reverses the original.
- All corrections use offsetting entries (debit/credit pattern).

### 11.3 Batch Merging Prevention
- **No API endpoint** exists for merging batches.
- Service layer enforces: batches with different `unit_cost` cannot be combined.
- Transfer between locations creates paired movements but preserves batch identity.

### 11.4 Single Currency Policy
- All batches use the company's default currency (`AppClientCompany.currency_id`).
- `unit_cost` and `unit_cost_at_txn` are always in the company's currency.
- No cross-currency conversion is needed at this stage.
- If multicurrency support is required in the future, add `currency_id` fields to `batch` and `inventory_movement` tables.

---

## 12. Rollout Plan

### 12.1 Feature-Flagged Rollout Stages

```
Stage 0: Schema Migration (batch_tracking_enabled = FALSE for all companies)
         ↳ Tables exist but are not populated. Zero impact on existing system.

Stage 1: Shadow Write Mode (1-2 weeks)
         ↳ Enable for pilot company. PO deliveries create batches + movements.
         ↳ SO deliveries create shadow allocations (write movements but don't block on errors).
         ↳ Monitor: batch quantities vs inventory_stock quantities.

Stage 2: Full Batch Mode — Pilot Company (2-4 weeks)
         ↳ Enable full allocation + movement enforcement for pilot.
         ↳ New reports available. Old reports still work.
         ↳ Monitor: COGS accuracy, allocation latency, error rates.

Stage 3: General Availability (after pilot validation)
         ↳ Run backfill for each company (with dry-run + reconciliation).
         ↳ Enable batch_tracking_enabled = TRUE.
         ↳ Old reports show "(Legacy)" label.

Stage 4: Legacy Report Deprecation (6 months post-GA)
         ↳ Remove legacy cost calculation paths.
         ↳ Make batch-based reports the default.
```

### 12.2 Staging Validation Checklist

- [ ] Tables created without errors
- [ ] Backfill dry-run produces zero mismatches for test company
- [ ] PO delivery creates batch + movement
- [ ] SO delivery allocates from correct batch (FIFO order verified)
- [ ] Return restores to original batch
- [ ] Concurrent allocation test passes (no double allocation)
- [ ] Reports show correct COGS from movements
- [ ] Feature flag toggle works (disable → legacy mode, enable → batch mode)
- [ ] All existing tests still pass (backward compatibility)
- [ ] FE batch drill-down page renders correctly
- [ ] FE movement ledger page renders correctly
- [ ] RBAC enforced (warehouse staff cannot see costs)

---

## 13. Operations Checklist

### 13.1 Monitoring Metrics

| Metric | Source | Alert Threshold |
|---|---|---|
| Allocation failure rate | `allocation_service` logger | > 1% of requests |
| Avg allocation latency | `allocation_service` timer | > 200ms |
| Batch qty mismatch | Scheduled reconciliation job | Any delta > 0 |
| Negative `qty_on_hand` | DB constraint check | Any occurrence |
| Movement ledger growth | `pg_total_relation_size` | > 100M rows/month |
| Feature flag state | `company_inventory_setting` | Unexpected changes |

### 13.2 Alerts

| Alert | Condition | Action |
|---|---|---|
| CRITICAL: Negative batch qty | `qty_on_hand < 0` | Investigate double allocation, restore from movement ledger |
| WARNING: Allocation conflict rate high | Lock contention > 5% | Review transaction isolation, consider batch partitioning |
| WARNING: Backfill mismatch | Reconciliation delta > 0 | Review synthetic batches, check for missed PO deliveries |
| INFO: Large movement write | > 1000 movements/minute | Normal during backfill, alert outside backfill window |

### 13.3 Reconciliation Runbook

```
1. Run reconciliation query (see backfill section) weekly.
2. Export mismatches to CSV.
3. For each mismatch:
   a. Check if recent transactions are pending (uncommitted).
   b. Check for race conditions (concurrent allocation + stock update).
   c. If genuine mismatch: create adjustment movement to align.
4. Log reconciliation results with timestamp.
```

### 13.4 Performance Knobs

| Setting | Default | Description |
|---|---|---|
| `BATCH_ALLOCATION_LOCK_TIMEOUT` | 5s | Max time to wait for batch lock |
| `BATCH_ALLOCATION_MAX_RETRIES` | 3 | Retries on lock contention |
| `BACKFILL_CHUNK_SIZE` | 500 | Records per backfill transaction |
| `MOVEMENT_PARTITION_INTERVAL` | monthly | Partition interval for large deployments |
| `RECONCILIATION_SCHEDULE` | weekly | Auto-reconciliation frequency |

---

## 14. Performance & Scaling

### 14.1 Index Strategy
Already specified in SQL migration. Key indexes:
- `idx_batch_product_qty` — Partial index on active batches with stock (most queries)
- `idx_movement_ref` — Fast lookup by reference type/id (for returns)
- `idx_movement_timestamp` — Range queries for reports

### 14.2 Partitioning (Future)
- `inventory_movement` — Partition by `txn_timestamp` (monthly) when > 10M rows
- Benefits: Faster range queries, easier archival, parallel backfill

### 14.3 Hotspot Analysis

| Operation | Hotspot Risk | Mitigation |
|---|---|---|
| Batch allocation during peak sales | HIGH | `SKIP LOCKED`, short transactions, retry logic |
| Movement ledger writes | MEDIUM | Batched inserts, async where possible |
| Backfill large history | HIGH | Chunked processing, off-hours, replica read |
| COGS/Margin reports on large ledger | MEDIUM | Materialized views or pre-computed aggregates |
| Reconciliation full scan | LOW | Run on read replica, indexed scans |

---

*Continued in Phase 4 document...*
