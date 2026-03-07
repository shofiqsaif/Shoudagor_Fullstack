# Batch-Based Inventory Implementation - Phase 1 Documentation

## Overview

This document describes the implementation of Phase 1 of the batch-based inventory system for Shoudagor ERP. The implementation adds per-receipt cost tracking using batches and an immutable inventory movement ledger.

## What Was Implemented

### 1. New Database Models

Four new models were created in [`app/models/batch_models.py`](app/models/batch_models.py):

- **Batch** (`inventory.batch`): Tracks groups of inventory units received together with a common cost
- **InventoryMovement** (`inventory.inventory_movement`): Immutable ledger recording every stock change with cost locked at transaction time
- **CompanyInventorySetting** (`settings.company_inventory_setting`): Company-level configuration for valuation mode and batch tracking enable/disable
- **SalesOrderBatchAllocation** (`sales.sales_order_batch_allocation`): Links sales order details to allocated batches

### 2. Database Migration

Alembic migration script created at [`alembic/versions/add_batch_inventory_phase1.py`](alembic/versions/add_batch_inventory_phase1.py) that:

- Creates the `inventory.batch` table with indexes
- Creates the `inventory.inventory_movement` table with indexes
- Creates the `settings.company_inventory_setting` table
- Creates the `sales.sales_order_batch_allocation` table
- Adds optional `cogs_amount` column to `billing.invoice_detail`

### 3. Repositories

Created repositories in [`app/repositories/inventory/batch.py`](app/repositories/inventory/batch.py):

- **BatchRepository**: CRUD operations for batches, batch locking for allocation
- **InventoryMovementRepository**: CRUD operations for movements, COGS calculation
- **SalesOrderBatchAllocationRepository**: Allocation tracking
- **CompanyInventorySettingRepository**: Company settings management

### 4. Core Allocation Service

Created [`app/services/inventory/batch_allocation_service.py`](app/services/inventory/batch_allocation_service.py) with:

- **FIFO Allocation**: Oldest batches allocated first (default)
- **LIFO Allocation**: Newest batches allocated first
- **Weighted Average Allocation**: Average cost across all batches
- **Batch Creation**: For purchase order receipts
- **Return Processing**: Return to original batches or create synthetic batches
- **Adjustment Movements**: For inventory adjustments
- **Transfer Movements**: For stock transfers between locations

### 5. Integration with Existing Services

Modified existing services to integrate batch tracking:

- **Procurement Delivery Detail Service** ([`app/services/procurement/product_order_delivery_detail_service.py`](app/services/procurement/product_order_delivery_detail_service.py)):
  - Creates batches when receiving PO deliveries (if batch tracking enabled)
  
- **Sales Order Delivery Detail Service** ([`app/services/sales/sales_order_delivery_detail_service.py`](app/services/sales/sales_order_delivery_detail_service.py)):
  - Allocates from batches when making sales deliveries (if batch tracking enabled)
  - Falls back to legacy stock update for backward compatibility

## How to Enable Batch Tracking

### 1. Run the Migration

```bash
cd Shoudagor
alembic upgrade head
```

### 2. Enable Batch Tracking for a Company

Use the `CompanyInventorySettingRepository` to enable batch tracking:

```python
from app.repositories.inventory.batch import CompanyInventorySettingRepository
from decimal import Decimal

# In your service or API endpoint
setting_repo = CompanyInventorySettingRepository(db)
setting_repo.create_or_update(
    company_id=1,
    valuation_mode="FIFO",  # FIFO, LIFO, or WEIGHTED_AVG
    batch_tracking_enabled=True,
    user_id=1
)
```

### 3. Configuration Options

- **valuation_mode**: `"FIFO"` (default), `"LIFO"`, or `"WEIGHTED_AVG"`
- **batch_tracking_enabled**: `True` to enable batch tracking, `False` for legacy mode

## How It Works

### Purchase Receipt Flow

1. When a PO delivery is created, the system checks if batch tracking is enabled
2. If enabled, a new batch is created with:
   - Quantity received
   - Unit cost from PO detail
   - Supplier, lot number, location info
3. An IN movement is created in the ledger
4. Legacy inventory stock is still updated for backward compatibility

### Sales Delivery Flow

1. When a SO delivery is created, the system checks if batch tracking is enabled
2. If enabled, batches are allocated based on company's valuation mode:
   - **FIFO**: Oldest batches first
   - **LIFO**: Newest batches first
   - **Weighted Average**: Uses average cost
3. Each allocation creates:
   - Decrement in batch qty_on_hand
   - OUT movement in ledger
   - Allocation record linking SO detail to batch
4. Legacy inventory stock is still updated for backward compatibility

### Return Flow

1. When processing a return, the system looks up original allocations
2. If original batch still exists and is active, returns to that batch
3. If original batch is depleted/deleted, creates a synthetic batch
4. RETURN_IN movement is created linking to original sale

## Key Features

### Concurrency Control

Uses `SELECT ... FOR UPDATE SKIP LOCKED` to prevent double allocation in concurrent sales scenarios.

### Backward Compatibility

- Legacy inventory stock table (`warehouse.inventory_stock`) is still maintained
- Existing transactions continue to work
- Batch tracking is opt-in per company

### COGS Calculation

COGS can be calculated from the inventory movement ledger:

```python
from app.repositories.inventory.batch import InventoryMovementRepository

movement_repo = InventoryMovementRepository(db)
cogs = movement_repo.calculate_cogs_for_sales(sales_order_detail_id)
```

## Database Schema

### inventory.batch

| Column | Type | Description |
|--------|------|-------------|
| batch_id | SERIAL | Primary key |
| company_id | INTEGER | FK to company |
| product_id | INTEGER | FK to product |
| variant_id | INTEGER | FK to variant (nullable) |
| qty_received | NUMERIC(18,4) | Original quantity received |
| qty_on_hand | NUMERIC(18,4) | Current quantity available |
| unit_cost | NUMERIC(18,4) | Cost per unit at receipt |
| received_date | TIMESTAMP | Date of receipt |
| supplier_id | INTEGER | FK to supplier |
| lot_number | VARCHAR(100) | Lot/batch number |
| status | VARCHAR(20) | active, depleted, expired, returned, quarantined |
| location_id | INTEGER | FK to storage location |
| purchase_order_detail_id | INTEGER | FK to PO detail |
| source_type | VARCHAR(30) | purchase, return, adjustment, transfer, synthetic |
| is_synthetic | BOOLEAN | True for synthetic batches (backfill/returns) |

### inventory.inventory_movement

| Column | Type | Description |
|--------|------|-------------|
| movement_id | SERIAL | Primary key |
| company_id | INTEGER | FK to company |
| batch_id | INTEGER | FK to batch |
| product_id | INTEGER | FK to product |
| variant_id | INTEGER | FK to variant (nullable) |
| qty | NUMERIC(18,4) | +ve for inbound, -ve for outbound |
| movement_type | VARCHAR(20) | IN, OUT, RETURN_IN, etc. |
| ref_type | VARCHAR(50) | Source document type |
| ref_id | INTEGER | Source document ID |
| unit_cost_at_txn | NUMERIC(18,4) | Cost locked at transaction time |
| actor | INTEGER | User who performed action |
| txn_timestamp | TIMESTAMP | Transaction timestamp |
| location_id | INTEGER | FK to storage location |
| related_movement_id | INTEGER | For returns - links to original |

### settings.company_inventory_setting

| Column | Type | Description |
|--------|------|-------------|
| setting_id | SERIAL | Primary key |
| company_id | INTEGER | FK to company (unique) |
| valuation_mode | VARCHAR(20) | FIFO, LIFO, WEIGHTED_AVG |
| batch_tracking_enabled | BOOLEAN | Feature flag |

### sales.sales_order_batch_allocation

| Column | Type | Description |
|--------|------|-------------|
| allocation_id | SERIAL | Primary key |
| sales_order_detail_id | INTEGER | FK to SO detail |
| batch_id | INTEGER | FK to batch |
| qty_allocated | NUMERIC(18,4) | Quantity allocated |
| unit_cost_at_allocation | NUMERIC(18,4) | Cost at allocation time |
| movement_id | INTEGER | FK to OUT movement |

## Files Created/Modified

### New Files

1. `app/models/batch_models.py` - New models
2. `app/repositories/inventory/batch.py` - Repositories
3. `app/services/inventory/batch_allocation_service.py` - Core allocation logic
4. `alembic/versions/add_batch_inventory_phase1.py` - Migration
5. `BATCH_INVENTORY_PHASE1_IMPLEMENTATION.md` - This documentation

### Modified Files

1. `app/models/__init__.py` - Added batch model exports
2. `app/models/inventory.py` - Added batch relationships
3. `app/models/warehouse.py` - Added batch/movement relationships
4. `app/models/sales.py` - Added batch allocation relationship
5. `app/models/procurement.py` - Added batch relationships
6. `app/models/security.py` - Added inventory settings relationship
7. `app/repositories/inventory/__init__.py` - Added batch repository exports
8. `app/services/procurement/product_order_delivery_detail_service.py` - Added batch creation
9. `app/services/sales/sales_order_delivery_detail_service.py` - Added batch allocation

## Testing Recommendations

1. **Unit Test**: Test allocation algorithms (FIFO, LIFO, Weighted Average)
2. **Integration Test**: Test PO delivery → batch creation → SO delivery → allocation
3. **Return Test**: Test return processing and synthetic batch creation
4. **Concurrency Test**: Test concurrent sales don't cause over-allocation
5. **Migration Test**: Test migration in staging before production

## Future Considerations (Phase 2+)

- Multicurrency cost tracking
- Batch expiration tracking
- DSR-specific batch handling
- Reporting enhancements using movement ledger
