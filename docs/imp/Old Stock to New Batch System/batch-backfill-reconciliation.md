# Batch Backfill & Batch Reconciliation

## Overview

These two features work together to enable batch-based inventory tracking for historical data that was recorded before batch tracking was implemented in the Shoudagor ERP system.

---

## Batch Backfill

### Purpose

Creates **synthetic batch records** from historical Purchase Order (PO) and Sales Order (SO) data, enabling FIFO cost traceability for transactions that predate the batch tracking system.

### Why It Matters

When a company enables batch tracking, all new inventory movements are tracked with batch information. However, historical data (existing stock, past purchases, past sales) has no batch records. The backfill feature solves this by generating synthetic batches that represent the historical inventory state.

### Two Types of Backfill

| Type | Source Data | Creates |
|------|-------------|---------|
| **Batch Data** | PO Delivery records (`ProductOrderDeliveryDetail`) | Synthetic `Batch` + IN `InventoryMovement` |
| **Sales Allocations** | SO Delivery records (`SalesOrderDeliveryDetail`) | `SalesOrderBatchAllocation` + OUT `InventoryMovement` |

### Key Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `dry_run` | `true` | Preview without committing changes to database |
| `chunk_size` | 500 | Number of records to process per batch (1-5000) |
| `company_id` | (required) | The company to backfill data for |
| `user_id` | 1 (system) | User ID for audit trail |

### Process Flow

#### 1. Batch Backfill (PO Deliveries)

```
1. Get pending PO deliveries (not yet linked to batches)
   └─ Query: ProductOrderDeliveryDetail where no Batch exists for purchase_order_detail_id

2. For each delivery:
   a. Calculate: qty = received_quantity + delivered_free_quantity
   b. Get unit_cost from PO detail
   c. Get location_id and company_id from PO
   d. Check if batch already exists (idempotency check)
   e. Create synthetic Batch record:
      - is_synthetic = True
      - source_type = "synthetic"
      - notes = "Backfilled from PO delivery {id}"
   f. Create InventoryMovement (type=IN, ref_type=BACKFILL)

3. If dry_run = False: commit to database
   If dry_run = True: rollback (preview only)

4. Generate reconciliation report comparing batch totals vs inventory_stock
```

#### 2. Sales Allocation Backfill (SO Deliveries)

```
1. Get pending SO deliveries (not yet allocated to batches)
   └─ Query: SalesOrderDeliveryDetail where no SalesOrderBatchAllocation exists

2. For each delivery:
   a. Calculate: qty = quantity - returned_quantity
   b. Find eligible batches (FIFO ordered by received_date)
   c. Allocate qty from oldest batches first:
      - For each batch:
        - alloc_qty = min(remaining_qty, batch.qty_on_hand)
        - Create SalesOrderBatchAllocation record
        - Create OUT movement with ref_type = "BACKFILL_SALES"
        - Decrement batch.qty_on_hand
        - remaining_qty -= alloc_qty

3. If dry_run = False: commit
   If dry_run = True: rollback

4. Return allocation count
```

### Data Created

#### Synthetic Batch Record
```python
Batch(
    batch_id="SYN-{timestamp}-{sequence}",
    product_id=...,
    variant_id=...,
    qty_received=qty_received,
    qty_on_hand=qty_received,
    unit_cost=unit_cost_from_po,
    received_date=delivery_date,
    supplier_id=po.supplier_id,
    location_id=po.location_id,
    purchase_order_detail_id=po_detail.id,
    source_type="synthetic",     # Distinguishes from real purchases
    is_synthetic=True,            # Marks as backfilled
    notes="Backfilled from PO delivery {id}"
)
```

#### InventoryMovement Record
```python
InventoryMovement(
    movement_type="IN",           # Inbound movement
    ref_type="BACKFILL",         # Marks as backfill operation
    product_id=...,
    variant_id=batch.id,
    batch_id=batch.id,
    qty=quantity,
    unit_cost_at_txn=unit_cost, # Locked at transaction time
    txn_timestamp=now(),
    actor=user_id,
    location_id=...
)
```

### Safety Features

| Feature | Description |
|---------|-------------|
| **Idempotent** | Safe to run multiple times - checks existing records before creating new ones |
| **DRY RUN** | Default mode shows preview without committing - always run this first |
| **Chunked Processing** | Handles large datasets in configurable chunks (default 500) to prevent memory issues |
| **Audit Trail** | All operations record user_id and timestamps |

---

## Batch Reconciliation

### Purpose

Verifies data integrity by comparing two parallel inventory tracking methods:

1. **Batch-based inventory** (`inventory.batch` table) - New batch tracking system with full cost traceability
2. **Legacy inventory stock** (`warehouse.inventory_stock` table) - Traditional inventory tracking by product/variant/location

The reconciliation ensures both systems agree on quantities, helping identify:
- Data migration issues
- Missing batches
- Quantity discrepancies
- System synchronization problems

### Comparison Logic

```
1. Sum Batch.qty_on_hand grouped by (product_id, variant_id, location_id)
   └─ Query: SELECT product_id, variant_id, location_id, SUM(qty_on_hand) FROM batch GROUP BY ...

2. Sum InventoryStock.quantity grouped by (product_id, variant_id, location_id)
   └─ Query: SELECT product_id, variant_id, location_id, SUM(quantity) FROM inventory_stock GROUP BY ...

3. Compare each item (product + variant + location combination):
   batch_qty vs stock_qty

4. Categorize each item:
   - MATCH: |batch_qty - stock_qty| < 0.0001 (essentially equal)
   - MISMATCH: Both have quantities but they differ
   - MISSING_IN_BATCH: stock has qty but batch has zero
   - MISSING_IN_STOCK: batch has qty but stock has zero

5. Calculate totals:
   - total_batch_qty = sum of all batch quantities
   - total_stock_qty = sum of all stock quantities
```

### Reconciliation Report Structure

```json
{
  "company_id": 1,
  "generated_at": "2026-03-09T10:30:00Z",
  "total_items": 150,
  "matched": 145,
  "mismatched": 3,
  "missing_in_batch": 1,
  "missing_in_stock": 1,
  "total_batch_qty": 5000.0,
  "total_stock_qty": 4950.0,
  "items": [
    {
      "product_id": 1,
      "variant_id": 5,
      "location_id": 10,
      "product_name": "Product A",
      "variant_sku": "SKU-001",
      "batch_qty": 100.0,
      "stock_qty": 100.0,
      "difference": 0.0,
      "status": "MATCH"
    },
    {
      "product_id": 2,
      "variant_id": 3,
      "location_id": 10,
      "product_name": "Product B",
      "variant_sku": "SKU-002",
      "batch_qty": 50.0,
      "stock_qty": 45.0,
      "difference": -5.0,
      "status": "MISMATCH"
    }
  ]
}
```

### Reconciliation Statuses

| Status | Meaning | Action Required |
|--------|---------|-----------------|
| **MATCH** | Batch qty equals Stock qty | None - data is consistent |
| **MISMATCH** | Both exist but quantities differ | Investigate - possible data drift |
| **MISSING_IN_BATCH** | Stock has qty but no batch exists | Run batch backfill |
| **MISSING_IN_STOCK** | Batch has qty but no stock record | Investigate - possible data corruption |

---

## How They Work Together

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         COMPLETE WORKFLOW                                  │
└─────────────────────────────────────────────────────────────────────────────┘

STEP 1: Initial Setup
        │
        ▼
   Company enables batch tracking in CompanyInventorySetting
        │
        ▼

STEP 2: Run Batch Backfill (DRY RUN first!)
        │
        ▼
   ┌────────────────────────────────────────────────────────────────────────┐
   │  backfill_batches()                                                   │
   │  ────────────────────                                                  │
   │  1. Get pending PO deliveries (not yet backfilled)                   │
   │  2. For each delivery:                                                │
   │     - Create synthetic Batch record                                    │
   │     - Create IN movement in inventory_movement                        │
   │  3. Generate reconciliation report                                    │
   └────────────────────────────────────────────────────────────────────────┘
        │
        ▼

STEP 3: Run Sales Allocation Backfill
        │
        ▼
   ┌────────────────────────────────────────────────────────────────────────┐
   │  backfill_sales_allocations()                                         │
   │  ─────────────────────────────                                       │
   │  1. Get pending SO deliveries (not yet backfilled)                   │
   │  2. For each delivery:                                                │
   │     - Find eligible FIFO batches                                      │
   │     - Create SalesOrderBatchAllocation                                │
   │     - Create OUT movement                                             │
   │     - Decrement batch.qty_on_hand                                     │
   └────────────────────────────────────────────────────────────────────────┘
        │
        ▼

STEP 4: Generate and Review Reconciliation Report
        │
        ▼
   ┌────────────────────────────────────────────────────────────────────────┐
   │  generate_reconciliation_report()                                     │
   │  ─────────────────────────────────                                    │
   │  Query batch totals vs stock totals                                   │
   │  Categorize each item: MATCH, MISMATCH, MISSING_IN_BATCH, etc.       │
   │  Display summary and detailed breakdown                               │
   └────────────────────────────────────────────────────────────────────────┘
        │
        ▼

STEP 5: Execute (if DRY RUN was successful)
        │
        ▼
   Run backfill with dry_run=false to commit changes
        │
        ▼

STEP 6: Verify
        │
        ▼
   Run reconciliation again to confirm all items show MATCH status
```

---

## API Endpoints

### Backend API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/inventory/reconciliation/` | GET | Get full reconciliation report |
| `/inventory/reconciliation/product/{product_id}` | GET | Get reconciliation for specific product |
| `/inventory/reconciliation/backfill` | POST | Run batch data backfill |
| `/inventory/reconciliation/backfill-sales` | POST | Run sales allocation backfill |

### Frontend API Functions (batchApi.ts)

| Function | Purpose |
|----------|---------|
| `getReconciliationReport()` | Fetch reconciliation report |
| `getReconciliationByProduct()` | Fetch reconciliation for specific product |
| `runBackfill(dryRun, chunkSize)` | Run batch backfill |
| `runSalesBackfill(dryRun, chunkSize)` | Run sales allocation backfill |

---

## Frontend Pages

| Page | Purpose |
|------|---------|
| `/inventory/backfill` | Run batch and sales backfill operations |
| `/inventory/reconciliation` | View reconciliation report and status |

---

## Key Files

| Layer | File Path | Purpose |
|-------|-----------|---------|
| **Backend Service** | `app/services/inventory/backfill_service.py` | Main backfill and reconciliation logic |
| **Backend API** | `app/api/inventory/batch.py` | REST endpoints (lines 490-639) |
| **Batch Model** | `app/models/batch_models.py` | Batch table definition |
| **Movement Model** | `app/models/batch_models.py` | InventoryMovement table |
| **Frontend Page** | `src/pages/inventory/BatchBackfill.tsx` | UI for running backfill |
| **Frontend Page** | `src/pages/inventory/BatchReconciliation.tsx` | UI for viewing results |
| **Frontend API** | `src/lib/api/batchApi.ts` | API client functions |

---

## Typical Usage Workflow

### First Time Setup

1. **Enable batch tracking** in `CompanyInventorySetting`
   - Set `batch_tracking_enabled = True`
   - Set `valuation_mode` (FIFO, LIFO, or WEIGHTED_AVG)

2. **Run batch backfill (DRY RUN)**
   ```json
   POST /inventory/reconciliation/backfill
   { "dry_run": true, "chunk_size": 500 }
   ```
   - Review how many batches will be created
   - Check for any warnings/errors
   - Review reconciliation report for data integrity

3. **Execute batch backfill** (if DRY RUN is satisfactory)
   ```json
   POST /inventory/reconciliation/backfill
   { "dry_run": false, "chunk_size": 500 }
   ```

4. **Run sales allocation backfill** (optional but recommended)
   ```json
   POST /inventory/reconciliation/backfill-sales
   { "dry_run": true, "chunk_size": 500 }
   ```
   - This links historical sales to batches
   - Enables full cost traceability for historical sales

5. **Verify with reconciliation**
   ```json
   GET /inventory/reconciliation/
   ```
   - Confirm all items show MATCH status

### Regular Maintenance

- **Periodic audits**: Run reconciliation periodically to catch data drift
- **After migrations**: Always verify reconciliation after any inventory data migration
- **Monitor mismatches**: Investigate any MISMATCH status items immediately

---

## Important Notes

1. **Always run DRY RUN first** - This is the default and safest option. It shows you what will happen without making changes.

2. **Order matters** - Run batch backfill before sales allocation backfill. Sales allocations require existing batches to allocate from.

3. **Idempotent operations** - Running backfill multiple times is safe. The system checks for existing records before creating new ones.

4. **Chunk size tuning** - Start with default (500). Increase for faster processing on large datasets, decrease if you encounter memory issues.

5. **Reconciliation is separate** - You can run reconciliation independently to check data integrity without running backfill.

---

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| All items show MISSING_IN_BATCH | No batches created yet | Run batch backfill |
| MISMATCH items after backfill | Data inconsistency in source | Investigate source data |
| Large number of MISSING_IN_STOCK | Stock not properly migrated | Check inventory_stock table |
| Backfill runs slowly | Large dataset, small chunk size | Increase chunk_size |

### Investigation Steps

1. Run DRY RUN to see preview
2. Check reconciliation report for specific products with issues
3. Verify source data (PO deliveries, SO deliveries) exists
4. Check for duplicate or conflicting records
5. Consult backend logs for detailed error messages
