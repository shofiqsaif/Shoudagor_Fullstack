# Inventory Stock to Batch Consolidation Script - Plan

## Objective

Create a script to consolidate ALL existing `inventory_stock` records across the entire company into single synthetic batches per product-variant-location, using purchase price from `product_price`.

## Script Location

`Shoudagor/app/services/inventory/stock_to_batch_service.py` (new file)

---

## Core Logic

### Step 1: Identify All Unique (product_id, variant_id, location_id) Combinations

- Query `InventoryStock` grouped by `(product_id, variant_id, location_id)`
- Sum quantities for each combination

### Step 2: Get Purchase Price from ProductPrice

- Query most recent active `product_price` for each product-variant
- Priority: variant-specific price → product-level price (fallback)
- Use `purchase_price` field

### Step 3: Handle Existing Batches (Replace Mode)

- Check if batch exists for the same (product_id, variant_id, location_id)
- If exists: Delete existing batch AND its movements (cascade)
- If not exists: Proceed to create

### Step 4: Create Synthetic Batch

```python
Batch(
    company_id=company_id,
    product_id=product_id,
    variant_id=variant_id,
    location_id=location_id,
    qty_received=total_stock_qty,
    qty_on_hand=total_stock_qty,
    unit_cost=purchase_price,
    received_date=datetime.utcnow(),
    source_type="synthetic",  # or "adjustment"
    is_synthetic=True,
    status="active",
    notes=f"Full backfill: consolidated from inventory_stock"
)
```

### Step 5: Create Opening Balance Movement

```python
InventoryMovement(
    company_id=company_id,
    batch_id=created_batch.batch_id,
    product_id=product_id,
    variant_id=variant_id,
    location_id=location_id,
    qty=total_stock_qty,  # positive for IN
    movement_type="OPENING_BALANCE",  # or "BACKFILL"
    ref_type="BACKFILL",
    unit_cost_at_txn=purchase_price,
    txn_timestamp=datetime.utcnow()
)
```

### Step 6: DRY-RUN Mode

- If `dry_run=True`: Return preview without making changes
- Show: how many batches will be created, updated, skipped
- Show: total quantities and costs

---

## API Endpoint

**File:** `Shoudagor/app/api/inventory/batch.py` (add new endpoint)

### Preview Endpoint (Dry-Run)

```
POST /inventory/stock-to-batch
Body: {
    "company_id": int,
    "dry_run": bool (default: true)
}
Response: {
    "to_create": int,
    "to_update": int,
    "to_skip": int,
    "details": [
        {"product_id": int, "variant_id": int, "location_id": int, "qty": decimal, "unit_cost": decimal}
    ]
}
```

### Execute Endpoint

```
POST /inventory/stock-to-batch/execute
Body: {
    "company_id": int,
    "dry_run": false
}
```

---

## Key Design Decisions

| Aspect | Decision |
|--------|----------|
| **Price Source** | Most recent active `product_price.purchase_price` |
| **Price Fallback** | Variant-specific → Product-level → 0 (if none) |
| **Batch Replace** | Delete existing + movements, create new |
| **Scope** | Full company backfill (all locations/products) |
| **InventoryStock** | Kept as-is (not deleted) |
| **Movement Type** | `OPENING_BALANCE` for traceability |
| **Batch Status** | `active` |
| **Source Type** | `synthetic` |

---

## Files to Create/Modify

| File | Action |
|------|--------|
| `app/services/inventory/stock_to_batch_service.py` | **Create** - Main service |
| `app/api/inventory/batch.py` | **Modify** - Add endpoints |
| `app/repositories/inventory/batch_repository.py` | **Modify** - Add delete method if needed |

---

## Dependencies

- `InventoryStock` model from `warehouse`
- `Batch`, `InventoryMovement` models from `inventory`
- `ProductPrice` model from `inventory`
- Existing `BatchRepository` for CRUD operations

---

## Error Handling

- If no `product_price` found: Use 0 and log warning
- If batch deletion fails: Rollback transaction
- If movement creation fails: Rollback batch creation
- Log each operation for audit trail

---

## Implementation Notes

### ProductPrice Query Pattern

```python
# First try variant-specific, then fall back to product-level
price = db.query(ProductPrice).filter(
    ProductPrice.product_id == product_id,
    ProductPrice.variant_id == variant_id,
    ProductPrice.is_active == True,
    ProductPrice.is_deleted == False
).order_by(ProductPrice.effective_date.desc()).first()

if not price:
    # Fall back to product-level price (variant_id = None)
    price = db.query(ProductPrice).filter(
        ProductPrice.product_id == product_id,
        ProductPrice.variant_id == None,
        ProductPrice.is_active == True,
        ProductPrice.is_deleted == False
    ).order_by(ProductPrice.effective_date.desc()).first()

unit_cost = float(price.purchase_price) if price else Decimal("0")
```

### InventoryStock Aggregation Query

```python
from sqlalchemy import func
from app.models.warehouse import InventoryStock

stock_aggregates = db.query(
    InventoryStock.product_id,
    InventoryStock.variant_id,
    InventoryStock.location_id,
    func.sum(InventoryStock.quantity).label('total_qty')
).filter(
    InventoryStock.is_deleted == False,
    InventoryStock.quantity > 0
).group_by(
    InventoryStock.product_id,
    InventoryStock.variant_id,
    InventoryStock.location_id
).all()
```

### Batch Delete (with Cascade)

```python
# Delete existing batch and its movements
existing_batch = db.query(Batch).filter(
    Batch.product_id == product_id,
    Batch.variant_id == variant_id,
    Batch.location_id == location_id,
    Batch.is_deleted == False
).first()

if existing_batch:
    # Delete movements first (or use cascade delete)
    db.query(InventoryMovement).filter(
        InventoryMovement.batch_id == existing_batch.batch_id
    ).delete()
    # Delete batch
    existing_batch.is_deleted = True
    db.commit()
```
