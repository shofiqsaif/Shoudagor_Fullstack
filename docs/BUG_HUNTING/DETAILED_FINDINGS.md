# Shoudagor ERP Detailed Findings (Backend + Frontend)

Date: 2026-03-11
Scope: Fullstack review with emphasis on requirements in `context.md` and `Intended.md`.

This document lists concrete issues and bugs found in architecture, functional logic, and service flows. Each item includes location, expected vs actual behavior, impact, and a suggested remediation direction.

---

## Findings

### FND-001: Delivery Creation Is Not Persisted (Missing Commit)
Severity: Critical
Area: Backend > Sales Delivery, Procurement Delivery
Location: `Shoudagor/app/services/sales/sales_order_delivery_detail_service.py` (create_delivery_detail), `Shoudagor/app/services/procurement/product_order_delivery_detail_service.py` (create_delivery_detail), `Shoudagor/app/api/sales/sales_order_delivery_detail.py`, `Shoudagor/app/api/procurement/product_order_delivery_detail.py`, `Shoudagor/app/core/database.py`
Details: Both delivery creation services call repository `.create()` (which only flushes) and return without committing. The API endpoints do not commit either, and `get_db()` does not auto-commit. As a result, delivery rows, stock updates, and related changes are rolled back when the session closes.
Expected: POST delivery endpoints should persist delivery records, inventory adjustments, and batch allocations reliably.
Actual: Delivery creation succeeds in response but does not persist to the database.
Impact: Inventory and financial state diverge from user actions. Users see successful delivery responses while stock and statuses remain unchanged.
Reproduction: Call POST `/api/company/sales/sales-order-delivery-detail/` or `/api/company/procurement/product-order-delivery-detail/` and then query for the created delivery in a new session; it is missing.
Suggested fix: Ensure the service or API commits after successful creation, or adopt a consistent Unit of Work pattern where API layer commits on success for all write operations.

### FND-002: Batch Allocation Uses Non-Base Quantities
Severity: High
Area: Backend > Inventory > Batch Allocation
Location: `Shoudagor/app/services/sales/sales_order_delivery_detail_service.py` (_update_inventory_stock)
Details: Batch allocation is executed before converting quantities to base UOM. `qty_needed` is computed from the raw `quantity_change`, which is in the order’s UOM, not necessarily base. Batches store `qty_on_hand` in base units.
Expected: Batch allocations should always use base-unit quantities to avoid under/over-allocation.
Actual: Allocation uses non-base quantities when `unit_of_measure_id` is not the base unit.
Impact: FIFO/LIFO allocation becomes incorrect; batch balances and COGS calculations drift.
Reproduction: Create a sales order in a derived UOM (e.g., carton) and deliver it. The batch allocation will subtract the wrong quantity if conversion factor != 1.
Suggested fix: Convert `quantity_change` to base before passing `qty_needed` into `batch_service.allocate()`.

### FND-003: Batch Allocation Defaults to Location ID 1 When Location Is Missing
Severity: High
Area: Backend > Inventory > Batch Allocation
Location: `Shoudagor/app/services/sales/sales_order_delivery_detail_service.py` (_update_inventory_stock)
Details: When `location_id` is `None`, batch allocation is executed with `location_id if location_id else 1`. This arbitrarily allocates from location 1, which may not be related to the order.
Expected: If no location exists, either block delivery or allocate from an explicitly defined location.
Actual: Allocation silently consumes batches from location 1.
Impact: Inventory is deducted from the wrong storage location; batch history and inventory counts become inaccurate.
Reproduction: Create a sales order without a location and deliver it with batch tracking enabled.
Suggested fix: Treat missing location as a validation error or enforce a default location at the order level before allocation.

### FND-004: Stock Transfer Ignores Batch Tracking
Severity: High
Area: Backend > Warehouse > Stock Transfer
Location: `Shoudagor/app/services/warehouse/stock_transfer.py`, `Shoudagor/app/services/warehouse/warehouse.py` (transfer_stock)
Details: Stock transfers only modify `inventory_stock` and write legacy `InventoryTransaction` entries. They do not allocate from source batches, do not create destination batches, and do not generate `InventoryMovement` entries.
Expected: When batch tracking is enabled, transfers should consume source batches (FIFO/LIFO) and create corresponding destination batches to preserve costing traceability.
Actual: Transfers bypass the batch ledger entirely.
Impact: Batch tracking chain breaks, FIFO/LIFO valuation and batch aging reports become unreliable after transfers.
Reproduction: Enable batch tracking, create batches via PO delivery, then perform a stock transfer. Batch stock quantities remain unchanged despite transfer.
Suggested fix: Route transfer logic through `BatchAllocationService` (create transfer movements) and update `Batch` and `InventoryMovement` consistently.

### FND-005: Inventory Adjustments Ignore Batch Tracking
Severity: High
Area: Backend > Inventory > Stock Adjustment
Location: `Shoudagor/app/services/transaction/inventory_adjustment.py`
Details: Inventory adjustments update `inventory_stock` and write a legacy `InventoryTransaction` only. There is no batch creation for positive adjustments or batch consumption for negative adjustments.
Expected: Adjustments should either create a synthetic batch for positive adjustments or consume existing batches (FIFO/LIFO) for negative adjustments when batch tracking is enabled.
Actual: Batch ledger is untouched.
Impact: Batch and inventory totals diverge; batch-based COGS and aging reports become incorrect.
Reproduction: Enable batch tracking, run an adjustment. Batch tables show no change, while inventory_stock changes.
Suggested fix: Integrate `BatchAllocationService.create_adjustment_movement()` into adjustment flows and reconcile stock totals.

### FND-006: Negative Adjustment Without Stock Creates Zero Stock Record and Logs Negative Transaction
Severity: Medium
Area: Backend > Inventory > Stock Adjustment
Location: `Shoudagor/app/services/transaction/inventory_adjustment.py` (_process_inventory_update)
Details: When no stock exists and `quantity_change` is negative, the service creates an `InventoryStock` record with quantity `0` and still logs a negative transaction. This produces a transaction that is not reflected in stock quantities.
Expected: Negative adjustments should be blocked if no stock exists or should create negative stock explicitly (if allowed by business rule).
Actual: Stock remains at 0 while transactions indicate a decrease.
Impact: Reporting inconsistencies and confusion during reconciliation.
Reproduction: Attempt a negative adjustment on a product/location with no stock.
Suggested fix: Reject negative adjustments when no stock exists, or handle negative stock consistently (including validation and display).

### FND-007: Initial Product Stock Does Not Create Batches
Severity: High
Area: Backend > Inventory > Product Creation
Location: `Shoudagor/app/services/inventory/product_service.py` (create_product, create_product_nested)
Details: Product creation creates `InventoryStock` records for initial quantities but does not create batch records when batch tracking is enabled.
Expected: Initial stock should create batches with cost information when batch tracking is enabled.
Actual: Inventory stock is created without any batch linkage.
Impact: Batch ledger starts incomplete; subsequent batch allocation and valuation are inaccurate.
Reproduction: Enable batch tracking, create a product with initial stock in the UI, then check batch tables; no batch is created.
Suggested fix: Integrate batch creation for initial stock (with explicit unit cost input or default cost rules).

### FND-008: Product Import Does Not Create Batches
Severity: High
Area: Backend > Inventory > Product Import
Location: `Shoudagor/app/services/inventory/product_import_nested_service.py` (_process_nested_import)
Details: Excel import creates `InventoryStock` for imported quantities but never creates batches.
Expected: Import should create batches when batch tracking is enabled, using purchase_price or a provided cost basis.
Actual: Batch tables remain empty while inventory_stock is populated.
Impact: Batch valuation and aging reports are incorrect for imported stock.
Reproduction: Import products with quantities and enable batch tracking; inspect batch tables.
Suggested fix: Create batches per imported stock location using purchase_price or an explicit cost column.

### FND-009: PO Delivery Update/Delete Does Not Reverse Batch Quantities
Severity: High
Area: Backend > Procurement > Delivery
Location: `Shoudagor/app/services/procurement/product_order_delivery_detail_service.py` (_update_inventory_stock)
Details: Batch creation occurs only for positive quantity changes. When delivery details are updated or deleted (negative change), batch quantities and movements are not reversed.
Expected: Updating or deleting a delivery should reverse batches and inventory movements accordingly.
Actual: Inventory stock is reduced, but batch ledger remains unchanged.
Impact: Batch totals drift; FIFO/LIFO valuation becomes inaccurate after delivery edits or deletions.
Reproduction: Create a PO delivery, then edit or delete it; batch quantities do not roll back.
Suggested fix: Add batch reversal logic for negative quantity adjustments and delivery deletions.

### FND-010: SO Delivery Update/Delete Does Not Reverse Batch Allocations
Severity: High
Area: Backend > Sales > Delivery
Location: `Shoudagor/app/services/sales/sales_order_delivery_detail_service.py` (update_delivery_detail, delete_delivery_detail)
Details: For non-DSR deliveries, edits and deletes update `inventory_stock` but do not reverse batch allocations or movements.
Expected: Reducing or deleting a delivery should restore batch quantities and update `SalesOrderBatchAllocation`/`InventoryMovement`.
Actual: Batch allocations remain, causing overstated batch depletion.
Impact: Batch ledger and COGS are overstated; reconciliation errors.
Reproduction: Deliver items with batch tracking, then delete the delivery. Batch allocations remain depleted.
Suggested fix: Add batch reversal logic when quantity decreases or deliveries are deleted.

### FND-011: Sales Returns Do Not Adjust Customer Balance or Order Totals
Severity: High
Area: Backend > Sales > Returns
Location: `Shoudagor/app/services/sales/sales_order_service.py` (process_return)
Details: Sales return processing updates order detail quantities and inventory, but does not adjust customer balance or order total. The Intended behavior requires customer balance to decrease by effective sales price for returned items.
Expected: Customer `balance_amount` and order totals should decrease based on returned quantities and effective price.
Actual: Receivables remain unchanged; order financials remain overstated.
Impact: AR aging and customer balances are incorrect; financial reports unreliable.
Reproduction: Create a sale, process a return, then check customer balance. It remains unchanged.
Suggested fix: Compute refund/credit amount from `effective_total_amount` logic and update customer balance and order totals during returns.

### FND-012: Sales Returns Do Not Adjust Claim/Scheme Logs
Severity: High
Area: Backend > Claims/Schemes
Location: `Shoudagor/app/services/sales/sales_order_service.py` (process_return), `Shoudagor/app/services/claims/claim_service.py` (adjust_claim_logs exists but unused)
Details: Claim logs are created on order creation, but partial returns do not trigger claim log adjustments or reversals. There is a service method (`adjust_claim_logs`) but it is not called.
Expected: Returns should proportionally reverse free quantities and discounts applied by schemes.
Actual: Scheme benefits remain fully applied after returns.
Impact: Scheme liability and discount reporting are overstated.
Reproduction: Create a sales order with a scheme, process a partial return, then check claim logs.
Suggested fix: Call `adjust_claim_logs()` or `reverse_claim_logs()` when processing returns.

### FND-013: Repository-Level Commits Break Transaction Atomicity
Severity: High
Area: Backend > Architecture > Data Consistency
Location: `Shoudagor/app/repositories/warehouse/inventory_stock.py` (create/update/delete commit inside repository), `Shoudagor/app/services/procurement/purchase_order_service.py` (process_return)
Details: `InventoryStockRepository.update()` commits immediately. Services like `process_return()` update stock inside loops and rely on additional operations (batch movements, supplier balance). If later steps fail, earlier commits are not rolled back.
Expected: Atomic transactions across stock, batch, and financial updates.
Actual: Partial commits can leave stock updated while batch or financial changes fail.
Impact: Data corruption and reconciliation issues under error conditions.
Reproduction: Force an exception after inventory update inside `process_return()` and observe partial updates persist.
Suggested fix: Remove commits from repository methods and enforce commits only at the service/transaction boundary.

### FND-014: Scheme Evaluation Stacks Multiple Schemes Instead of Selecting Best
Severity: Medium
Area: Backend + Frontend > Claims/Schemes
Location: `Shoudagor/app/services/claims/claim_service.py` (evaluate_pre_claim), `shoudagor_FE/src/components/forms/SaleForm.tsx` (calculateSchemeBenefits)
Details: When multiple schemes match (variant and product schemes), benefits are summed across schemes. Intended behavior calls for applying the best slab, not stacking multiple schemes.
Expected: Choose the best applicable scheme/slab (e.g., maximum benefit), not sum multiple schemes.
Actual: Free quantities and discounts can accumulate across multiple schemes.
Impact: Excessive discounts/free items and financial leakage.
Reproduction: Configure overlapping product + variant schemes and create an order; benefits stack.
Suggested fix: Implement a deterministic “best scheme” selection rule and apply only one scheme.

### FND-015: Manual Scheme Overrides Can Be Lost
Severity: Medium
Area: Backend > Claims/Schemes
Location: `Shoudagor/app/services/claims/claim_service.py` (evaluate_pre_claim)
Details: If `applied_scheme_id` is set but the scheme is not found in active schemes, the system resets `free_quantity` and `discount_amount` to 0. Manual override values are discarded.
Expected: Manual override values should be preserved or the request should fail validation.
Actual: Benefits are silently zeroed.
Impact: User-entered manual overrides are lost without warning.
Reproduction: Select a scheme that becomes inactive and re-submit the order.
Suggested fix: If a scheme is specified but not active, return a validation error or preserve manual values explicitly.

### FND-016: UOM Conversions Use Float, Causing Precision Drift
Severity: Medium
Area: Backend > UOM/Prices
Location: `Shoudagor/app/services/uom_utils.py`
Details: All conversions coerce to `float`, introducing rounding errors in quantities and pricing. This propagates into inventory quantities, costs, and totals.
Expected: Use `Decimal` for all quantity and price calculations to preserve accuracy.
Actual: Precision loss occurs for repeated conversions and large quantities.
Impact: Stock quantities drift and financial totals misalign over time.
Reproduction: Convert quantities with non-integer conversion factors and compare against Decimal-based conversions.
Suggested fix: Replace `float` conversions with `Decimal` arithmetic end-to-end.

### FND-017: DSR Load/Unload Ignores UOM Conversion
Severity: High
Area: Backend > DSR > Inventory Transfers
Location: `Shoudagor/app/services/dsr/dsr_so_assignment_service.py` (load_so, unload_so)
Details: `quantity_to_load` and `quantity_to_return` are based on order detail quantities without converting to base UOM. DSR inventory and main inventory stocks store base units.
Expected: Quantities should be converted to base UOM before stock updates and batch allocations.
Actual: Raw order units are used, leading to incorrect stock in DSR and warehouse.
Impact: DSR stock and warehouse stock become inconsistent; delivery validation becomes unreliable.
Reproduction: Use a derived UOM for sales order details and perform DSR load/unload.
Suggested fix: Convert quantities to base UOM before any stock or batch updates in DSR flows.

### FND-018: Stock Availability Checks Ignore Free Quantities and Existing Allocations
Severity: Medium
Area: Backend > Sales
Location: `Shoudagor/app/services/sales/sales_order_service.py` (_validate_stock_availability)
Details: Stock validation checks only ordered quantity, ignoring free quantities from schemes and any existing batch allocations/reservations.
Expected: Validation should consider total (billable + free) and any reserved/allocated stock.
Actual: Orders can be accepted even when free items or allocations cause insufficient stock.
Impact: Overselling risk and delivery failures later.
Reproduction: Apply a scheme with free quantities and place an order near stock limits.
Suggested fix: Include free quantities in required stock and optionally account for allocated quantities when batch tracking is enabled.

### FND-019: Variant Stock Totals Ignore Batch Stock When Tracking Enabled
Severity: Medium
Area: Backend + Frontend > Inventory Listing
Location: `Shoudagor/app/repositories/inventory/product_variant.py` (_process_nested_results)
Details: `total_stock` is calculated from `inventory_stocks` only. When batch tracking is enabled, the UI uses `batch_stocks` for availability but the `total_stock` summary and some reports still rely on `inventory_stocks`.
Expected: When batch tracking is enabled, `total_stock` should be computed from batch quantities to remain consistent.
Actual: Total stock can show zero or outdated values despite batch stock existing.
Impact: Misleading inventory totals on the UI and in reports.
Reproduction: Enable batch tracking, create batch inventory without matching `inventory_stock` updates, then view variant totals.
Suggested fix: Use batch stock summary for total_stock when batch tracking is enabled.

### FND-020: Duplicate Stock Transfer Implementations Cause Divergent Behavior
Severity: Medium
Area: Backend > Architecture
Location: `Shoudagor/app/services/warehouse/stock_transfer.py` and `Shoudagor/app/services/warehouse/warehouse.py` (transfer_stock)
Details: Two different services implement stock transfer logic with overlapping responsibilities. Neither is batch-aware. The duplication leads to inconsistent validation, transaction handling, and missing features.
Expected: A single authoritative stock transfer workflow with consistent validation and batch support.
Actual: Two competing implementations with different behaviors and no batch integration.
Impact: Hard-to-maintain code, inconsistent transfer results, and elevated bug risk.
Reproduction: Compare behavior between endpoints wired to each service (if both exposed).
Suggested fix: Consolidate into a single service that supports batch tracking and consistent transaction boundaries.

---

End of findings.
