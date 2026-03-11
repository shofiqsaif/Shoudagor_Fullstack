# Inventory Stock and Batch Sync Deep Dive

## Purpose
When batch tracking is enabled, `inventory_stock` must be a consistent mirror of batch quantities. The invariant is:

- For every `(company_id, product_id, variant_id, location_id)`:
  - `SUM(batch.qty_on_hand)` must equal `inventory_stock.quantity`.
  - This must hold after every operation that affects stock.

This document audits the current implementation, identifies concrete flaws, and provides a fix plan with edge cases and error handling.

## Scope
Backend areas reviewed:

- Batch tracking and allocation: `Shoudagor/app/services/inventory/batch_allocation_service.py`
- Batch models and ledger: `Shoudagor/app/models/batch_models.py`
- Inventory stock model and APIs: `Shoudagor/app/models/warehouse.py`, `Shoudagor/app/services/warehouse/warehouse.py`
- Purchase order deliveries: `Shoudagor/app/services/procurement/product_order_delivery_detail_service.py`
- Sales deliveries/returns: `Shoudagor/app/services/sales/sales_order_delivery_detail_service.py`, `Shoudagor/app/services/sales/sales_order_service.py`
- Inventory adjustments: `Shoudagor/app/services/transaction/inventory_adjustment.py`
- Stock transfers: `Shoudagor/app/services/warehouse/stock_transfer.py`
- DSR load/unload and DSR transfers: `Shoudagor/app/services/dsr/dsr_so_assignment_service.py`, `Shoudagor/app/services/warehouse/dsr_stock_transfer.py`
- Product/variant stock creation/update: `Shoudagor/app/services/inventory/product_service.py`, `Shoudagor/app/services/inventory/product_variant_service.py`, `Shoudagor/app/services/inventory/product_import_nested_service.py`
- Purchase order returns: `Shoudagor/app/services/procurement/purchase_order_service.py`
- Inventory reports/variant listing: `Shoudagor/app/repositories/inventory/product_variant.py`
- Reconciliation/backfill: `Shoudagor/app/services/inventory/backfill_service.py`, `Shoudagor/app/services/inventory/stock_to_batch_service.py`

## Current Data Model

### `inventory_stock`
- Table: `warehouse.inventory_stock` (`Shoudagor/app/models/warehouse.py`)
- Quantity stored in base UOM (most services convert)
- Legacy stock source used by many services

### Batch Tables
- `inventory.batch` and `inventory.inventory_movement` (`Shoudagor/app/models/batch_models.py`)
- `SalesOrderBatchAllocation` and `DSRBatchAllocation`
- `CompanyInventorySetting.batch_tracking_enabled` as feature flag

### Intended Sync
- Batch operations should create ledger movements and update `batch.qty_on_hand`
- Legacy stock updates often still run for backward compatibility
- There is a reconciliation service and backfill utilities

## Current Behavior by Operation

### 1. Manual Inventory Stock CRUD (Warehouse Service)
File: `Shoudagor/app/services/warehouse/warehouse.py`

- `create_inventory_stock`, `update_inventory_stock`, `delete_inventory_stock` update only `inventory_stock`
- No batch movements or batch qty updates

**Impact:** If batch tracking is enabled, direct stock edits immediately break the invariant.

### 2. Product Creation with Initial Stock
File: `Shoudagor/app/services/inventory/product_service.py`

- Creates `inventory_stock`
- If batch tracking enabled, creates synthetic batch via `create_adjustment_movement`
- If batch creation fails, it continues and leaves stock without batch

**Impact:** Partial failures cause divergence. No rollback behavior.

### 3. Variant Nested Create/Update (Inventory Stocks)
File: `Shoudagor/app/services/inventory/product_variant_service.py`

- Creates/deletes `inventory_stock` without any batch sync
- Update path deletes existing inventory_stock and recreates new entries

**Impact:** Guaranteed mismatch when batch tracking is enabled.

### 4. Product Import
File: `Shoudagor/app/services/inventory/product_import_nested_service.py`

- Creates `inventory_stock`
- Optionally creates synthetic batch
- If batch creation fails, it continues

**Impact:** Mismatch on partial failures.

### 5. Purchase Order Delivery (Receipts)
File: `Shoudagor/app/services/procurement/product_order_delivery_detail_service.py`

- Creates batch for each delivery if batch tracking enabled
- Uses `create_batch_for_purchase_receipt` which **blocks** duplicate `purchase_order_detail_id`
- If batch creation fails, it continues and updates `inventory_stock` only

**Impact:** If partial deliveries exist for a single PO detail, batch creation fails after the first receipt. Stock increases, batch does not.

### 6. Purchase Order Returns
File: `Shoudagor/app/services/procurement/purchase_order_service.py`

- Reduces `inventory_stock`
- If batches exist, decrements batch qty and creates RETURN_OUT movements
- If no batches exist, still proceeds
- Quantity appears to use PO detail quantity without explicit UOM conversion

**Impact:** If batch tracking is enabled but batches are missing, stock decreases without batch changes. Possible UOM mismatch between stock and batch.

### 7. Sales Order Deliveries (Warehouse)
File: `Shoudagor/app/services/sales/sales_order_delivery_detail_service.py`

- On delivery, `_update_inventory_stock`:
  - allocates from batches if enabled
  - **always** updates `inventory_stock`
  - if allocation fails, falls back to legacy stock update

**Impact:** Any allocation failure leaves stock and batch out of sync. The failure is swallowed and the operation still commits.

### 8. Sales Returns
File: `Shoudagor/app/services/sales/sales_order_service.py`

- Uses `BatchAllocationService.process_return` if enabled
- Updates `inventory_stock` and transactions

**Impact:** If batch allocation data is incorrect or missing, stock can be updated without corresponding batch reversal. Return logic uses SalesOrderBatchAllocation, which may be stale in DSR workflows.

### 9. Inventory Adjustments
File: `Shoudagor/app/services/transaction/inventory_adjustment.py`

- Negative adjustments use `batch_service.allocate` with `sales_order_detail_id=0`
- This creates SalesOrderBatchAllocation records and OUT movements with ref_type `SALES_DELIVERY`
- Errors are swallowed and stock is still updated
- Adjustment update/delete **rolls back stock only**, not batch

**Impact:**
- Invalid FK (`sales_order_detail_id=0`) likely fails or creates unusable allocations
- Wrong movement ref_type
- Mismatch from fallback paths and missing rollback

### 10. Stock Transfers (Location to Location)
File: `Shoudagor/app/services/warehouse/stock_transfer.py`

- Uses `batch_service.allocate` with `sales_order_detail_id=0`
- Then **also** calls `create_transfer_movements`, which decrements batch again
- If batch logic errors, it falls back to legacy stock update

**Impact:**
- Double-decrement of batch qty on successful path
- Incorrect allocations (FK 0)
- Fallback causes mismatches

### 11. DSR Load (Assign SO to DSR Storage)
File: `Shoudagor/app/services/dsr/dsr_so_assignment_service.py`

- Allocates batches for the unshipped quantity
- Rewrites `InventoryMovement` ref_type for the entire sales order detail from `SALES_DELIVERY` to `DSR_TRANSFER`
- Creates `DSRBatchAllocation` for all allocations

**Impact:**
- If any deliveries existed before loading, their movements are incorrectly reclassified
- DSR allocations may include quantities already shipped
- This pollutes SalesOrderBatchAllocation and InventoryMovement semantics

### 12. DSR Unload
File: `Shoudagor/app/services/dsr/dsr_so_assignment_service.py`

- Uses DSRBatchAllocation to return quantities to batches
- Also deallocates SalesOrderBatchAllocation

**Impact:**
- If DSRBatchAllocation is incorrect (see load issues), batch and allocation reversal will be wrong
- Does not enforce that DSR inventory and batch allocations match

### 13. DSR Stock Transfer (General)
File: `Shoudagor/app/services/warehouse/dsr_stock_transfer.py`

- Updates `inventory_stock` / `dsr_inventory_stock`
- No batch movement or batch qty updates

**Impact:** Breaks batch/inventory sync for any DSR transfer done outside SO load/unload.

### 14. Batch API Direct Create
File: `Shoudagor/app/api/inventory/batch.py`

- Allows creating batches directly
- Does not update `inventory_stock`

**Impact:** Direct mismatch when using the batch API under batch tracking.

### 15. Reporting Logic Double Counts
File: `Shoudagor/app/repositories/inventory/product_variant.py`

- When batch tracking enabled, total stock is computed as `inventory_stock + batch_qty`

**Impact:** If the system goal is strict equality, this logic doubles stock and distorts reports.

## Systemic Flaws (Summary)

1. **Split authority**: inventory_stock and batch are both updated, but there is no single authoritative source.
2. **Fallback on error**: many services continue updating inventory_stock even if batch changes fail.
3. **Incorrect allocation usage**: stock transfers and adjustments use sales allocations (`sales_order_detail_id=0`).
4. **Movement semantics corruption**: ref_type and movement_type are reused incorrectly for non-sales flows.
5. **Partial delivery handling**: PO deliveries assume one batch per PO detail; repeated deliveries break batch sync.
6. **DSR flow inconsistencies**: load/unload and DSR transfer paths are inconsistent and can mutate unrelated movements.
7. **Manual stock operations**: inventory_stock CRUD bypasses batch logic entirely.
8. **Reporting drift**: reports and variant listing double count when batch tracking is enabled.
9. **Lack of enforcement**: no runtime guard prevents operations from leaving stock and batch out of sync.

## Fix Plan

### Phase 0: Define Invariant and Ownership

- When `CompanyInventorySetting.batch_tracking_enabled = true`, batch is the **source of truth**.
- `inventory_stock` becomes a **denormalized mirror** that must be updated in the same transaction.
- Do not allow operations to update inventory_stock without batch changes in batch-enabled mode.

### Phase 1: Centralize Stock Mutations

Create a single service that owns stock changes for all workflows, for example:

- `InventorySyncService` (or `StockLedgerService`)
  - Input: `StockChange` object with fields:
    - `company_id`, `product_id`, `variant_id`, `location_id`
    - `qty_delta` in base UOM
    - `source` (PURCHASE_RECEIPT, SALES_DELIVERY, SALES_RETURN, ADJUSTMENT, TRANSFER, DSR_LOAD, DSR_UNLOAD)
    - `ref_type`, `ref_id`
    - `unit_cost` if applicable
  - Responsibilities:
    - Batch operations (allocate, create, transfer, return)
    - InventoryStock updates
    - InventoryMovement creation
    - Optional allocation linking

**Key rule:** If batch tracking is enabled, failure in any batch operation must roll back the entire transaction.

### Phase 2: Fix Each Workflow

#### 1. Purchase Receipts
- Allow multiple deliveries per PO detail.
- Replace `create_batch_for_purchase_receipt` uniqueness check with:
  - Either allow multiple batches per PO detail
  - Or create/append to a single batch per `(po_detail_id, delivery_id)`
- Use delivery detail ID as ref_id for batch movements if possible.
- If batch creation fails, do not update inventory_stock.

#### 2. Sales Deliveries
- Remove fallback that updates inventory_stock when batch allocation fails.
- If batch tracking enabled, allocation must succeed or the delivery should fail.
- Keep inventory_stock updates, but only after allocation succeeds, in the same transaction.

#### 3. Sales Returns
- Ensure that DSR and non-DSR returns update both `SalesOrderBatchAllocation` and `DSRBatchAllocation` consistently.
- Use a dedicated return method in `InventorySyncService` to reverse allocations and update batches.

#### 4. Inventory Adjustments
- Replace use of `BatchAllocationService.allocate` for negative adjustments.
- Create a new batch-consumption path for adjustments that:
  - Uses `InventoryMovement.ref_type = ADJUSTMENT`
  - Does NOT create SalesOrderBatchAllocation
- Add rollback logic for adjustment update/delete to reverse batch movements.

#### 5. Stock Transfers (Warehouse)
- Replace `allocate(..., sales_order_detail_id=0)` with a transfer-specific allocation method:
  - Returns per-batch quantities and unit costs
  - Creates `TRANSFER_OUT` movements per batch
  - Creates `TRANSFER_IN` movement(s) for target batch(es)
  - Does not double-decrement batch qty

#### 6. DSR Load/Unload
- Treat DSR load as a true stock transfer between warehouse and DSR storage:
  - Do not re-label existing SALES_DELIVERY movements
  - Create DSR-specific transfer movements and DSR batch allocations
- Ensure DSRBatchAllocation reflects only quantities actually loaded
- In unload, reverse DSR transfer movements and update allocations atomically

#### 7. DSR Stock Transfers
- If batch tracking enabled, DSR transfers must adjust batches:
  - Decrement warehouse batch qty on load to DSR
  - Increment batch qty on unload from DSR
- Add a non-assignment DSR batch holding concept or extend DSRBatchAllocation to support generic DSR transfers

#### 8. Manual Inventory Stock CRUD
- When batch tracking is enabled:
  - Block direct CRUD operations, or
  - Route them through adjustment logic that updates batches and inventory_stock together

#### 9. Variant Nested Stock Updates
- When batch tracking enabled:
  - Compute per-location delta from old vs new stocks
  - Apply delta via InventorySyncService (synthetic adjustments)
  - Avoid wholesale delete + recreate

#### 10. Reporting
- When batch tracking enabled:
  - Do not sum `inventory_stock` and batch totals.
  - Use batch totals as authoritative or show them side-by-side.

### Phase 3: Guardrails and Consistency Checks

- Add a post-transaction consistency check in batch-enabled mode:
  - Compare updated `(product_id, variant_id, location_id)` with batch totals
  - Raise error if divergence exceeds tolerance
- Add reconciliation endpoint/job that flags drift and suggests repair actions
- Add optional database triggers or materialized views for audit

### Phase 4: Migration and Backfill

- On enabling batch tracking for a company:
  - Run `stock_to_batch` or `backfill_service`
  - Lock stock operations during migration
  - Verify reconciliation report is clean before allowing new operations

### Phase 5: Tests

Minimum integration tests (batch enabled):

- PO delivery with partial deliveries
- Sales delivery + return
- Inventory adjustment (positive and negative)
- Stock transfer between locations
- DSR load -> DSR sale -> unload
- Manual stock update blocked or synced
- Product variant nested update adjusts batches correctly

## Edge Cases and Error Handling

### UOM Conversion
- Always convert to base UOM before batch allocation or stock updates.
- Avoid mixing converted and raw quantities in the same transaction.

### Partial Deliveries and Free Quantities
- PO deliveries should treat billable + free quantity consistently for batch creation.
- Sales deliveries should allocate for total (billable + free) quantity.

### Location is NULL
- Batch allocation requires a location. When `location_id` is NULL, batch tracking should fail with a clear error.

### Concurrency
- Use row-level locks on both `inventory_stock` and `batch` rows when changing quantities.
- Avoid independent commits inside batch logic.

### Soft Deletes
- When deleting `inventory_stock`, ensure corresponding batch quantities are adjusted or block deletion.

### DSR Flows
- DSR load/unload should not rewrite sales delivery movements.
- DSR allocations must reflect actual loaded quantities, not total allocations.

### Failure Paths
- If batch update fails, the entire operation should rollback.
- Never leave `inventory_stock` updated while batch changes failed.

## Recommended Immediate Fixes (Highest Impact)

1. Stop fallback to legacy stock updates when batch operations fail.
2. Fix stock transfer double-decrement and remove use of `sales_order_detail_id=0`.
3. Add batch sync in variant nested create/update and warehouse inventory CRUD.
4. Fix PO delivery batch creation so partial deliveries do not skip batch creation.
5. Update report logic to avoid double counting.

## Suggested Documentation Additions (for future maintainers)

- A single diagram showing the authoritative flow:
  - PO receipt -> batch + movement -> inventory_stock mirror
  - Sales delivery -> batch allocation -> inventory_stock mirror
  - Returns -> reverse allocation -> inventory_stock mirror
  - Adjustments -> batch adjustment -> inventory_stock mirror

- A clear rule in engineering docs:
  - "If batch tracking is enabled, all stock changes must go through InventorySyncService."

---

## Appendix: Key Code References

- Batch allocation core: `Shoudagor/app/services/inventory/batch_allocation_service.py`
- Batch models: `Shoudagor/app/models/batch_models.py`
- Inventory stock CRUD: `Shoudagor/app/services/warehouse/warehouse.py`
- PO delivery detail: `Shoudagor/app/services/procurement/product_order_delivery_detail_service.py`
- PO return: `Shoudagor/app/services/procurement/purchase_order_service.py`
- Sales delivery detail: `Shoudagor/app/services/sales/sales_order_delivery_detail_service.py`
- Sales returns: `Shoudagor/app/services/sales/sales_order_service.py`
- Inventory adjustment: `Shoudagor/app/services/transaction/inventory_adjustment.py`
- Stock transfer: `Shoudagor/app/services/warehouse/stock_transfer.py`
- DSR assignment load/unload: `Shoudagor/app/services/dsr/dsr_so_assignment_service.py`
- DSR stock transfer: `Shoudagor/app/services/warehouse/dsr_stock_transfer.py`
- Variant nested stock updates: `Shoudagor/app/services/inventory/product_variant_service.py`
- Product import: `Shoudagor/app/services/inventory/product_import_nested_service.py`
- Variant reporting totals: `Shoudagor/app/repositories/inventory/product_variant.py`
- Reconciliation: `Shoudagor/app/services/inventory/backfill_service.py`
- Stock-to-batch: `Shoudagor/app/services/inventory/stock_to_batch_service.py`
