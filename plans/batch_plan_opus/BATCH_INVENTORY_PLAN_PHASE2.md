# Batch-Based Inventory Implementation Plan — Phase 2: API, Backend Services & Tests

## 6. API Specification

### 6.1 New Endpoints — Batch Management

#### `POST /api/company/inventory/batches`
Create inbound batch (typically called internally by PO delivery service).

```json
// Request
{
    "product_id": 101,
    "variant_id": 205,
    "qty_received": 500.0000,
    "unit_cost": 45.5000,
    "received_date": "2026-03-07T10:00:00+06:00",
    "supplier_id": 12,
    "lot_number": "LOT-2026-0307-A",
    "location_id": 3,
    "purchase_order_detail_id": 789,
    "source_type": "purchase"
}

// Response 201
{
    "batch_id": 1042,
    "product_id": 101,
    "variant_id": 205,
    "qty_received": 500.0000,
    "qty_on_hand": 500.0000,
    "unit_cost": 45.5000,
    "received_date": "2026-03-07T10:00:00+06:00",
    "supplier_id": 12,
    "supplier_name": "ABC Suppliers Ltd",
    "lot_number": "LOT-2026-0307-A",
    "status": "active",
    "location_id": 3,
    "location_name": "Main Warehouse Floor A",
    "is_synthetic": false,
    "cd": "2026-03-07T10:01:00+06:00"
}
```

#### `GET /api/company/inventory/batches`
List batches with filtering.

Query params: `product_id`, `variant_id`, `location_id`, `supplier_id`, `status`, `start`, `limit`, `include_depleted` (default false)

```json
// Response 200
{
    "items": [
        {
            "batch_id": 1042,
            "product_name": "Tissue Box Premium",
            "variant_sku": "TB-PREM-100",
            "qty_received": 500.0000,
            "qty_on_hand": 320.0000,
            "unit_cost": 45.5000,
            "received_date": "2026-03-07T10:00:00+06:00",
            "supplier_name": "ABC Suppliers Ltd",
            "lot_number": "LOT-2026-0307-A",
            "status": "active",
            "location_name": "Main Warehouse Floor A",
            "age_days": 14
        }
    ],
    "total": 1,
    "page": 1,
    "page_size": 50
}
```

#### `GET /api/company/inventory/batches/{batch_id}`
Get single batch with movement history.

#### `PATCH /api/company/inventory/batches/{batch_id}`
Update batch metadata (lot_number, notes). **Cannot update unit_cost if batch has OUT movements.**

---

### 6.2 New Endpoints — Batch Allocation

#### `POST /api/company/sales/{sales_order_id}/allocate`
Server-side batch allocation for a sales order delivery.

```json
// Request
{
    "sales_order_detail_id": 456,
    "qty_to_allocate": 100.0000,
    "location_id": 3
}

// Response 200
{
    "allocations": [
        {
            "allocation_id": 1,
            "batch_id": 1040,
            "qty_allocated": 80.0000,
            "unit_cost_at_allocation": 42.0000,
            "batch_received_date": "2026-02-15T10:00:00+06:00"
        },
        {
            "allocation_id": 2,
            "batch_id": 1042,
            "qty_allocated": 20.0000,
            "unit_cost_at_allocation": 45.5000,
            "batch_received_date": "2026-03-07T10:00:00+06:00"
        }
    ],
    "total_qty_allocated": 100.0000,
    "total_cogs": 4270.0000,
    "valuation_mode": "FIFO"
}
```

---

### 6.3 New Endpoints — Inventory Movements

#### `GET /api/company/inventory/movements`
Query the movement ledger.

Query params: `product_id`, `variant_id`, `batch_id`, `location_id`, `movement_type`, `ref_type`, `start_date`, `end_date`, `start`, `limit`

```json
// Response 200
{
    "items": [
        {
            "movement_id": 5001,
            "batch_id": 1042,
            "product_name": "Tissue Box Premium",
            "variant_sku": "TB-PREM-100",
            "qty": -20.0000,
            "movement_type": "OUT",
            "ref_type": "SALES_DELIVERY",
            "ref_id": 789,
            "unit_cost_at_txn": 45.5000,
            "actor_name": "Admin User",
            "txn_timestamp": "2026-03-08T14:30:00+06:00",
            "location_name": "Main Warehouse Floor A",
            "notes": null
        }
    ],
    "total": 1
}
```

#### `POST /api/company/inventory/movements`
Create manual movement (adjustment type only, requires RBAC check).

---

### 6.4 New Endpoints — Batch Drill-Down & Reports

#### `GET /api/company/products/{product_id}/batches`
Batch drill-down for a specific product with computed averages.

```json
// Response 200
{
    "product_id": 101,
    "product_name": "Tissue Box Premium",
    "total_stock": 820.0000,
    "avg_cost": 43.2195,
    "batches": [
        {
            "batch_id": 1040,
            "variant_sku": "TB-PREM-100",
            "qty_on_hand": 500.0000,
            "unit_cost": 42.0000,
            "received_date": "2026-02-15T10:00:00+06:00",
            "supplier_name": "ABC Suppliers Ltd",
            "age_days": 20
        },
        {
            "batch_id": 1042,
            "variant_sku": "TB-PREM-100",
            "qty_on_hand": 320.0000,
            "unit_cost": 45.5000,
            "received_date": "2026-03-07T10:00:00+06:00",
            "supplier_name": "ABC Suppliers Ltd",
            "age_days": 0
        }
    ]
}
```

#### `GET /api/company/reports/stock-by-batch`
Stock by batch report (all products).

#### `GET /api/company/reports/inventory-aging`
Inventory aging report (replaces current FIFO aging with batch-based aging).

#### `GET /api/company/reports/cogs-by-period`
COGS by period derived from the movement ledger.

#### `GET /api/company/reports/margin-analysis`
Margin analysis using actual batch costs vs selling prices.

#### `GET /api/company/reports/batch-pnl`
Batch P&L report showing profitability per batch.

---

### 6.5 Return / Reverse Endpoints

#### `POST /api/company/sales/{sales_order_id}/returns`
Process a sales return with batch traceability.

```json
// Request
{
    "sales_order_detail_id": 456,
    "qty_returned": 10.0000,
    "reason": "Customer returned - damaged packaging",
    "return_to_original_batch": true
}

// Response 200
{
    "return_movements": [
        {
            "movement_id": 5010,
            "batch_id": 1040,
            "qty": 10.0000,
            "unit_cost_at_txn": 42.0000,
            "movement_type": "RETURN_IN",
            "related_movement_id": 4990
        }
    ],
    "total_returned": 10.0000,
    "credit_amount": 420.0000
}
```

---

## 7. Backend Service Architecture

### 7.1 New Services

| Service | File Path | Responsibility |
|---|---|---|
| `BatchService` | `app/services/inventory/batch_service.py` | CRUD for batches, cost immutability enforcement |
| `InventoryMovementService` | `app/services/inventory/inventory_movement_service.py` | Create movements, query ledger, immutability enforcement |
| `BatchAllocationService` | `app/services/inventory/batch_allocation_service.py` | FIFO/LIFO/WAC allocation with concurrency control |
| `CompanyInventorySettingService` | `app/services/settings/company_inventory_setting_service.py` | Company valuation mode, feature flag |
| `BackfillService` | `app/services/inventory/backfill_service.py` | Backfill script logic, reconciliation |

### 7.2 New Repositories

| Repository | File Path |
|---|---|
| `BatchRepository` | `app/repositories/inventory/batch_repository.py` |
| `InventoryMovementRepository` | `app/repositories/inventory/inventory_movement_repository.py` |
| `BatchAllocationRepository` | `app/repositories/inventory/batch_allocation_repository.py` |
| `CompanyInventorySettingRepository` | `app/repositories/settings/company_inventory_setting_repository.py` |

### 7.3 New Schemas (Pydantic)

| Schema | File Path |
|---|---|
| `BatchCreate`, `BatchUpdate`, `BatchResponse` | `app/schemas/inventory/batch.py` |
| `InventoryMovementCreate`, `InventoryMovementResponse` | `app/schemas/inventory/inventory_movement.py` |
| `AllocationRequest`, `AllocationResult`, `AllocationResponse` | `app/schemas/inventory/batch_allocation.py` |
| `CompanyInventorySettingCreate`, `CompanyInventorySettingResponse` | `app/schemas/settings/company_inventory_setting.py` |

### 7.4 New API Route Files

| Router | File Path | Prefix |
|---|---|---|
| `batch_router` | `app/api/inventory/batch.py` | `/api/company/inventory/batches` |
| `movement_router` | `app/api/inventory/inventory_movement.py` | `/api/company/inventory/movements` |
| `allocation_router` | `app/api/sales/batch_allocation.py` | `/api/company/sales/{so_id}/allocate` |
| `batch_reports_router` | `app/api/reports/batch_reports.py` | `/api/company/reports/batch-*` |

### 7.5 Modified Services — Integration Points

#### `ProductOrderDeliveryDetailService` — Modified Methods

```python
# In create_delivery_detail():
# AFTER existing stock update logic, ADD:
if self._is_batch_tracking_enabled(company_id):
    batch = self.batch_service.create_batch(
        product_id=po_detail.product_id,
        variant_id=po_detail.variant_id,
        qty_received=base_quantity_change,
        unit_cost=po_detail.unit_price,  # Purchase cost
        received_date=delivery.delivery_date,
        supplier_id=purchase_order.supplier_id,
        location_id=purchase_order.location_id,
        purchase_order_detail_id=po_detail.purchase_order_detail_id,
        user_id=user_id,
        company_id=company_id,
    )
    self.movement_service.create_movement(
        batch_id=batch.batch_id,
        product_id=po_detail.product_id,
        variant_id=po_detail.variant_id,
        qty=base_quantity_change,  # Positive = inbound
        movement_type='IN',
        ref_type='PURCHASE_DELIVERY',
        ref_id=delivery_detail.delivery_detail_id,
        unit_cost_at_txn=po_detail.unit_price,
        actor=user_id,
        location_id=purchase_order.location_id,
        company_id=company_id,
    )
```

#### `SalesOrderDeliveryDetailService` — Modified Methods

```python
# In create_delivery_detail():
# BEFORE existing stock update logic, ADD:
if self._is_batch_tracking_enabled(company_id):
    allocations = self.allocation_service.allocate(
        company_id=company_id,
        product_id=so_detail.product_id,
        variant_id=so_detail.variant_id,
        location_id=sales_order.location_id,
        qty_needed=base_quantity_change,
        so_detail_id=so_detail.sales_order_detail_id,
        user_id=user_id,
    )
    # allocations are committed by the allocation service
    # including batch decrements and movement records
```

#### `InventoryAdjustmentService` — Modified Methods

```python
# In _process_inventory_update():
# ADD batch movement creation for adjustments
if self._is_batch_tracking_enabled(company_id):
    if detail.quantity > 0:  # Stock increase
        batch = self.batch_service.create_batch(
            source_type='adjustment', unit_cost=detail.unit_cost, ...)
        self.movement_service.create_movement(
            movement_type='ADJUSTMENT', ref_type='ADJUSTMENT', ...)
    else:  # Stock decrease
        # Allocate from batches using configured valuation mode
        self.allocation_service.allocate_for_adjustment(...)
```

---

## 8. Backfill & Migration Strategy

### 8.1 Backfill Script — Step by Step

```
Step 1: Add tables (empty) — via Alembic migration
Step 2: Insert company_inventory_setting for all companies (batch_tracking_enabled=FALSE)
Step 3: Run backfill script in DRY RUN mode
Step 4: Review reconciliation CSV output
Step 5: Run backfill in PRODUCTION mode (chunked, idempotent)
Step 6: Enable batch_tracking for one pilot company (batch_tracking_enabled=TRUE)
Step 7: Monitor for 1 week
Step 8: Enable for all companies
```

### 8.2 Backfill Logic (Pseudo-code)

```python
def backfill_batches(db, company_id, dry_run=True):
    """
    Create synthetic batches from historical PO deliveries.
    Idempotent: checks if batch already exists for PO detail.
    """
    # Get all delivered PO details with received quantities
    po_details = db.execute(text("""
        SELECT pod.purchase_order_detail_id, pod.product_id, pod.variant_id,
               pod.unit_price, pod.received_quantity, pod.free_quantity,
               po.supplier_id, po.location_id, po.order_date,
               SUM(dd.delivered_quantity) as total_delivered
        FROM procurement.purchase_order_detail pod
        JOIN procurement.purchase_order po
            ON pod.purchase_order_id = po.purchase_order_id
        LEFT JOIN procurement.product_order_delivery_detail dd
            ON dd.purchase_order_detail_id = pod.purchase_order_detail_id
            AND dd.is_deleted = FALSE
        WHERE po.company_id = :company_id
          AND po.is_deleted = FALSE
          AND pod.is_deleted = FALSE
        GROUP BY pod.purchase_order_detail_id, pod.product_id, pod.variant_id,
                 pod.unit_price, pod.received_quantity, pod.free_quantity,
                 po.supplier_id, po.location_id, po.order_date
        HAVING SUM(dd.delivered_quantity) > 0
        ORDER BY po.order_date ASC
    """), {"company_id": company_id}).fetchall()

    for pod in po_details:
        # Check idempotency
        existing = db.execute(text("""
            SELECT batch_id FROM inventory.batch
            WHERE purchase_order_detail_id = :pod_id AND is_deleted = FALSE
        """), {"pod_id": pod.purchase_order_detail_id}).fetchone()

        if existing:
            continue  # Already backfilled

        total_received = pod.total_delivered + (pod.free_quantity or 0)

        # Create synthetic batch
        batch_id = insert_batch(
            db, company_id=company_id,
            product_id=pod.product_id, variant_id=pod.variant_id,
            qty_received=total_received,
            qty_on_hand=total_received,  # Will be adjusted in step 2
            unit_cost=pod.unit_price,
            supplier_id=pod.supplier_id,
            location_id=pod.location_id,
            received_date=pod.order_date,
            purchase_order_detail_id=pod.purchase_order_detail_id,
            source_type='synthetic', is_synthetic=True,
        )

        # Create IN movement
        insert_movement(db, batch_id=batch_id, qty=total_received,
                       movement_type='IN', ref_type='BACKFILL', ...)

    # Step 2: Create OUT movements for sold quantities
    backfill_outbound_movements(db, company_id)

    # Step 3: Reconcile
    reconciliation = reconcile(db, company_id)

    if dry_run:
        db.rollback()
        return reconciliation
    else:
        db.commit()
        return reconciliation


def reconcile(db, company_id):
    """Compare SUM(batch.qty_on_hand) vs inventory_stock.quantity"""
    mismatches = db.execute(text("""
        SELECT is.product_id, is.variant_id, is.location_id,
               is.quantity as stock_qty,
               COALESCE(SUM(b.qty_on_hand), 0) as batch_qty,
               is.quantity - COALESCE(SUM(b.qty_on_hand), 0) as delta
        FROM warehouse.inventory_stock is
        LEFT JOIN inventory.batch b
            ON b.product_id = is.product_id
            AND COALESCE(b.variant_id, 0) = COALESCE(is.variant_id, 0)
            AND b.location_id = is.location_id
            AND b.status = 'active' AND b.is_deleted = FALSE
        WHERE is.is_deleted = FALSE
          AND EXISTS (SELECT 1 FROM warehouse.storage_location sl
                      WHERE sl.location_id = is.location_id
                      AND sl.company_id = :company_id)
        GROUP BY is.product_id, is.variant_id, is.location_id, is.quantity
        HAVING is.quantity != COALESCE(SUM(b.qty_on_hand), 0)
    """), {"company_id": company_id}).fetchall()
    return mismatches
```

### 8.3 Rollback Strategy

1. **Feature flag OFF**: Set `batch_tracking_enabled = FALSE` — system returns to legacy mode instantly.
2. **Table drop**: If backfill data is invalid, truncate `inventory_movement` and `batch` tables, re-run.
3. **Alembic downgrade**: Full rollback via `alembic downgrade -1` removes new tables and `cogs_amount` column.

---

## 9. Test Plan

### 9.1 Unit Tests — Allocation

| Test Case | Description | Expected |
|---|---|---|
| `test_fifo_single_batch` | Allocate 50 from batch of 100 | batch.qty_on_hand = 50, 1 OUT movement |
| `test_fifo_multi_batch` | Allocate 150 from batches [100, 100] | batch1 depleted, batch2.qty = 50 |
| `test_fifo_exact_depletion` | Allocate exactly batch qty | batch.status = 'depleted' |
| `test_fifo_insufficient_stock` | Allocate 200 from batch of 100 | `InsufficientStockError` |
| `test_lifo_ordering` | LIFO: newest batch allocated first | Newest batch decremented first |
| `test_weighted_avg_cost` | WAC: cost is weighted average | `unit_cost_at_txn` = weighted avg |
| `test_concurrent_allocation` | Two parallel allocations for same product | Both succeed, no double allocation |
| `test_partial_shipment` | Ship 30 of SO line for 100, then ship 70 | Two allocations, total matches |
| `test_skip_locked_concurrent` | Simultaneous orders lock different batches | `SKIP LOCKED` prevents deadlock |

### 9.2 Unit Tests — Returns

| Test Case | Description | Expected |
|---|---|---|
| `test_return_to_original_batch` | Return 10 units sold from batch B1 | B1.qty_on_hand += 10, RETURN_IN movement |
| `test_return_depleted_batch` | Return to depleted batch | New synthetic batch created with original cost |
| `test_return_audit_chain` | Return links to original movement | `related_movement_id` points to original OUT |
| `test_partial_return` | Return 5 of 20 allocated from batch | Only 5 returned, 15 remain out |

### 9.3 Integration Tests

| Test Case | Description |
|---|---|
| `test_po_delivery_creates_batch_and_movement` | PO delivery → batch + IN movement created |
| `test_so_delivery_allocates_and_creates_movements` | SO delivery → allocation + OUT movements |
| `test_full_cycle_po_to_so_to_return` | PO delivery → SO delivery → return → verify ledger |
| `test_cogs_matches_accounting` | COGS from movements = sum(qty × unit_cost_at_txn) |
| `test_adjustment_creates_movement` | Stock adjustment → adjustment movement with cost |
| `test_stock_transfer_creates_paired_movements` | Transfer → TRANSFER_OUT + TRANSFER_IN movements |
| `test_backfill_reconciliation` | Run backfill → check totals match inventory_stock |

### 9.4 Migration Tests

| Test Case | Description |
|---|---|
| `test_backfill_dry_run` | Dry run produces reconciliation report, no data committed |
| `test_backfill_idempotent` | Running backfill twice produces same result |
| `test_backfill_reconcile_totals` | Post-backfill SUM(batch.qty_on_hand) = inventory_stock.quantity |

### 9.5 How to Run Tests

```bash
# Run all batch inventory tests
python -m pytest tests/test_batch_inventory/ -v

# Run specific test file
python -m pytest tests/test_batch_inventory/test_allocation.py -v

# Run with coverage
python -m pytest tests/test_batch_inventory/ --cov=app.services.inventory --cov-report=html

# Run concurrency tests
python -m pytest tests/test_batch_inventory/test_concurrent_allocation.py -v -s
```

### 9.6 Acceptance Scenarios (5 Examples)

#### Scenario 1: Simple FIFO Sale
- Batch B1: 100 units @ BDT 40, received Jan 1
- Batch B2: 100 units @ BDT 45, received Feb 1
- Sale: 120 units
- **Expected**: 100 from B1 (cost 4000) + 20 from B2 (cost 900) = COGS 4900
- **Movements**: 2 OUT movements, B1 depleted, B2.qty = 80

#### Scenario 2: Partial Shipment
- Batch B1: 200 units @ BDT 50
- SO line: 200 units
- Delivery 1: Ship 80 → Allocate 80 from B1 (B1.qty = 120)
- Delivery 2: Ship 120 → Allocate 120 from B1 (B1.qty = 0, status = depleted)
- **Expected COGS**: 200 × 50 = 10,000

#### Scenario 3: Return to Original Batch
- Batch B1: 100 units @ BDT 40
- Sale: 50 units from B1 (B1.qty = 50)
- Return: 10 units
- **Expected**: B1.qty = 60, RETURN_IN movement with cost 40, related to original OUT
- **Net COGS**: 40 × 40 = 1,600

#### Scenario 4: Concurrent Sales
- Batch B1: 100 units @ BDT 40
- Sale A: 60 units (arrives first, locks B1)
- Sale B: 60 units (concurrent, sees B1 locked via SKIP LOCKED)
- **Expected**: Sale A succeeds (B1.qty = 40), Sale B fails with InsufficientStockError (only 40 available)

#### Scenario 5: Inventory Adjustment
- Batch B1: 100 units @ BDT 40
- Physical count: only 95 units found
- Adjustment: -5 units
- **Expected**: B1.qty = 95, ADJUSTMENT movement with cost 40, qty = -5
- **Net inventory value**: 95 × 40 = 3,800

---

*Continued in Phase 3 document...*
