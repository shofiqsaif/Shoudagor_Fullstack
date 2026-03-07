# Batch-Based Inventory Implementation - Phase 2: API, Backend Services & Tests

## Overview

This document describes the implementation of Phase 2 of the batch-based inventory system for Shoudagor ERP. Phase 2 adds API endpoints for batch management, inventory movements, batch allocation, returns processing, and batch-based reporting.

## What Was Implemented

### 1. Pydantic Schemas

Created `app/schemas/inventory/batch.py` with all request/response schemas:

#### Batch Schemas
- `BatchCreate` - Schema for creating a new batch
- `BatchUpdate` - Schema for updating batch metadata
- `BatchResponse` - Schema for batch response
- `BatchListItem` - Schema for batch list item (with computed fields)
- `BatchListResponse` - Schema for paginated batch list response
- `BatchDetailResponse` - Schema for batch detail with movement history

#### Inventory Movement Schemas
- `InventoryMovementCreate` - Schema for creating a manual inventory movement
- `InventoryMovementResponse` - Schema for inventory movement response
- `InventoryMovementListResponse` - Schema for paginated movement list response
- `MovementFilterParams` - Query parameters for filtering movements

#### Batch Allocation Schemas
- `AllocationRequest` - Schema for batch allocation request
- `AllocationItem` - Schema for individual allocation item
- `AllocationResponse` - Schema for batch allocation response

#### Return/Reverse Schemas
- `ReturnRequest` - Schema for sales return request
- `ReturnMovementItem` - Schema for return movement item
- `ReturnResponse` - Schema for sales return response

#### Batch Reports Schemas
- `ProductBatchItem` - Schema for batch in product batch drill-down
- `ProductBatchDrillDownResponse` - Schema for product batch drill-down response
- `BatchStockReportItem` - Schema for stock by batch report item
- `BatchStockReportResponse` - Schema for stock by batch report
- `InventoryAgingItem` - Schema for inventory aging report item
- `InventoryAgingResponse` - Schema for inventory aging report
- `COGSReportItem` - Schema for COGS by period report
- `COGSReportResponse` - Schema for COGS by period report
- `BatchPNLItem` - Schema for batch P&L report item
- `BatchPNLResponse` - Schema for batch P&L report
- `MarginAnalysisItem` - Schema for margin analysis report item
- `MarginAnalysisResponse` - Schema for margin analysis report

#### Company Inventory Setting Schemas
- `CompanyInventorySettingCreate` - Schema for creating company inventory setting
- `CompanyInventorySettingResponse` - Schema for company inventory setting response

---

## API Endpoints

### 1. Batch Management Endpoints

Prefix: `/api/company/inventory/batches`

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/company/inventory/batches` | Create inbound batch |
| GET | `/api/company/inventory/batches` | List batches with filtering |
| GET | `/api/company/inventory/batches/{batch_id}` | Get batch with movement history |
| PATCH | `/api/company/inventory/batches/{batch_id}` | Update batch metadata |

#### POST /api/company/inventory/batches

Create a new inbound batch (typically called internally by PO delivery service).

**Request:**
```json
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
```

**Response 201:**
```json
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

#### GET /api/company/inventory/batches

List batches with optional filtering.

**Query Parameters:**
- `product_id` - Filter by product ID
- `variant_id` - Filter by variant ID
- `location_id` - Filter by location ID
- `supplier_id` - Filter by supplier ID
- `status` - Filter by status (active, depleted, etc.)
- `include_depleted` - Include depleted batches (default: false)
- `start` - Pagination start (default: 0)
- `limit` - Page size (default: 50)

**Response 200:**
```json
{
    "items": [
        {
            "batch_id": 1042,
            "product_id": 101,
            "product_name": "Tissue Box Premium",
            "variant_id": 205,
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

#### GET /api/company/inventory/batches/{batch_id}

Get single batch with movement history.

**Response 200:**
```json
{
    "batch_id": 1042,
    "product_id": 101,
    "product_name": "Tissue Box Premium",
    "variant_id": 205,
    "variant_sku": "TB-PREM-100",
    "qty_received": 500.0000,
    "qty_on_hand": 320.0000,
    "unit_cost": 45.5000,
    "received_date": "2026-03-07T10:00:00+06:00",
    "supplier_id": 12,
    "supplier_name": "ABC Suppliers Ltd",
    "lot_number": "LOT-2026-0307-A",
    "status": "active",
    "location_id": 3,
    "location_name": "Main Warehouse Floor A",
    "is_synthetic": false,
    "source_type": "purchase",
    "purchase_order_detail_id": 789,
    "cd": "2026-03-07T10:01:00+06:00",
    "movements": [...]
}
```

#### PATCH /api/company/inventory/batches/{batch_id}

Update batch metadata (lot_number, notes). Cannot update unit_cost if batch has OUT movements.

**Request:**
```json
{
    "lot_number": "LOT-2026-0307-B"
}
```

---

### 2. Inventory Movements Endpoints

Prefix: `/api/company/inventory/movements`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/company/inventory/movements` | Query movement ledger |
| POST | `/api/company/inventory/movements` | Create manual movement |

#### GET /api/company/inventory/movements

Query the inventory movement ledger.

**Query Parameters:**
- `product_id` - Filter by product ID
- `variant_id` - Filter by variant ID
- `batch_id` - Filter by batch ID
- `location_id` - Filter by location ID
- `movement_type` - Filter by movement type (IN, OUT, RETURN_IN, etc.)
- `ref_type` - Filter by reference type
- `start_date` - Filter by start date
- `end_date` - Filter by end date
- `start` - Pagination start
- `limit` - Page size

**Response 200:**
```json
{
    "items": [
        {
            "movement_id": 5001,
            "batch_id": 1042,
            "product_id": 101,
            "product_name": "Tissue Box Premium",
            "variant_id": 205,
            "variant_sku": "TB-PREM-100",
            "qty": -20.0000,
            "movement_type": "OUT",
            "ref_type": "SALES_DELIVERY",
            "ref_id": 789,
            "unit_cost_at_txn": 45.5000,
            "actor_name": "1",
            "txn_timestamp": "2026-03-08T14:30:00+06:00",
            "location_name": "Main Warehouse Floor A",
            "notes": null,
            "related_movement_id": null
        }
    ],
    "total": 1
}
```

#### POST /api/company/inventory/movements

Create a manual inventory movement (adjustment type only, requires RBAC check).

**Request:**
```json
{
    "product_id": 101,
    "variant_id": 205,
    "batch_id": 1042,
    "qty": 10.0000,
    "movement_type": "ADJUSTMENT",
    "ref_type": "MANUAL_ADJUSTMENT",
    "unit_cost_at_txn": 45.5000,
    "location_id": 3,
    "notes": "Inventory count adjustment"
}
```

---

### 3. Batch Allocation Endpoints

Prefix: `/api/company/sales`

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/company/sales/{sales_order_id}/allocate` | Server-side batch allocation |
| POST | `/api/company/sales/{sales_order_id}/returns` | Process sales return |

#### POST /api/company/sales/{sales_order_id}/allocate

Server-side batch allocation for a sales order delivery.

**Request:**
```json
{
    "sales_order_detail_id": 456,
    "qty_to_allocate": 100.0000,
    "location_id": 3
}
```

**Response 200:**
```json
{
    "allocations": [
        {
            "allocation_id": 1,
            "batch_id": 1040,
            "qty_allocated": 80.0000,
            "unit_cost_at_allocation": 42.0000
        },
        {
            "allocation_id": 2,
            "batch_id": 1042,
            "qty_allocated": 20.0000,
            "unit_cost_at_allocation": 45.5000
        }
    ],
    "total_qty_allocated": 100.0000,
    "total_cogs": 4270.0000,
    "valuation_mode": "FIFO"
}
```

#### POST /api/company/sales/{sales_order_id}/returns

Process a sales return with batch traceability.

**Request:**
```json
{
    "sales_order_detail_id": 456,
    "qty_returned": 10.0000,
    "reason": "Customer returned - damaged packaging",
    "return_to_original_batch": true
}
```

**Response 200:**
```json
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

### 4. Batch Reports Endpoints

Prefix: `/api/company/reports`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/company/reports/stock-by-batch` | Stock by batch report |
| GET | `/api/company/reports/inventory-aging` | Inventory aging report |
| GET | `/api/company/reports/cogs-by-period` | COGS by period report |
| GET | `/api/company/reports/margin-analysis` | Margin analysis using actual batch costs vs selling prices |
| GET | `/api/company/reports/batch-pnl` | Batch P&L report |

---

### 5. Product Batch Drill-Down Endpoint

Prefix: `/api/company/products`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/company/products/{product_id}/batches` | Batch drill-down for product |

#### GET /api/company/products/{product_id}/batches

Batch drill-down for a specific product with computed averages.

**Response 200:**
```json
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

---

### 6. Inventory Settings Endpoints

Prefix: `/api/company/inventory/settings`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/company/inventory/settings` | Get company settings |
| POST | `/api/company/inventory/settings` | Create/update settings |

#### POST /api/company/inventory/settings

Create or update company inventory settings.

**Request:**
```json
{
    "company_id": 1,
    "valuation_mode": "FIFO",
    "batch_tracking_enabled": true
}
```

**Response:**
```json
{
    "setting_id": 1,
    "company_id": 1,
    "valuation_mode": "FIFO",
    "batch_tracking_enabled": true
}
```

---

## Files Created/Modified

### New Files

1. **`app/schemas/inventory/batch.py`** - Pydantic schemas for batch, movement, allocation, and reports
2. **`app/api/inventory/batch.py`** - Batch management & settings API routers
3. **`app/api/inventory/inventory_movement.py`** - Inventory movement API router
4. **`app/api/sales/batch_allocation.py`** - Allocation, returns & reports API routers

### Modified Files

1. **`app/schemas/inventory/__init__.py`** - Added exports for new batch schemas
2. **`app/api/inventory/__init__.py`** - Added exports for new routers
3. **`app/main.py`** - Registered new routers with the FastAPI app

---

## How to Enable Batch Tracking

### 1. Run the Migration (if not already done)

```bash
cd Shoudagor
alembic upgrade head
```

### 2. Enable Batch Tracking for a Company

Use the settings endpoint:

```bash
POST /api/company/inventory/settings
{
    "company_id": 1,
    "valuation_mode": "FIFO",  # FIFO, LIFO, or WEIGHTED_AVG
    "batch_tracking_enabled": true
}
```

Or via Python:

```python
from app.repositories.inventory.batch import CompanyInventorySettingRepository

setting_repo = CompanyInventorySettingRepository(db)
setting_repo.create_or_update(
    company_id=1,
    valuation_mode="FIFO",
    batch_tracking_enabled=True,
    user_id=1
)
```

### 3. Configuration Options

- **valuation_mode**: `"FIFO"` (default), `"LIFO"`, or `"WEIGHTED_AVG"`
- **batch_tracking_enabled**: `True` to enable batch tracking, `False` for legacy mode

---

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
   - **Weighted Average**: Average cost across all batches
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

---

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

---

## Verification

All Python files passed syntax compilation:

```bash
python -m py_compile app/main.py
python -m py_compile app/schemas/inventory/batch.py
python -m py_compile app/api/inventory/batch.py
python -m py_compile app/api/inventory/inventory_movement.py
python -m py_compile app/api/sales/batch_allocation.py
```

Import tests passed:

```python
from app.schemas.inventory.batch import BatchCreate, BatchResponse, AllocationRequest, ReturnRequest
from app.schemas.inventory.batch import MarginAnalysisItem, MarginAnalysisResponse
from app.api.inventory.batch import batch_router, settings_router
from app.api.inventory.inventory_movement import movement_router
from app.api.sales.batch_allocation import allocation_router, reports_router
```

---

## Testing Recommendations

1. **Unit Test**: Test allocation algorithms (FIFO, LIFO, Weighted Average)
2. **Integration Test**: Test PO delivery → batch creation → SO delivery → allocation
3. **Return Test**: Test return processing and synthetic batch creation
4. **Concurrency Test**: Test concurrent sales don't cause over-allocation
5. **Migration Test**: Test migration in staging before production

### Running Tests

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

---

## Future Considerations (Phase 3+)

- Multicurrency cost tracking
- Batch expiration tracking
- DSR-specific batch handling
- Enhanced reporting with drill-down capabilities
