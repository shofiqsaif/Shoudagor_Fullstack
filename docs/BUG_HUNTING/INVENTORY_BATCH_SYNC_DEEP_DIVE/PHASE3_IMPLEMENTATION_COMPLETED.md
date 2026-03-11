# Phase 3 Implementation Documentation

**Date:** 2026-03-11  
**Status:** Implemented

---

## Overview

This document describes the Phase 3 implementation for Guardrails and Consistency Checks, addressing gaps identified in `docs/INVENTORY_BATCH_SYNC_DEEP_DIVE.md`.

---

## Implemented Components

### 1. Edge Case Handling (Task 3)

**File:** `app/services/inventory/inventory_sync_service.py`

Enhanced `verify_invariant()` method with:

- **NULL variant handling:** Properly handles NULL variant_id using SQLAlchemy conditional expressions
- **Soft-delete awareness:** Explicitly filters `is_deleted=False` for both batch and inventory_stock
- **Decimal precision:** Uses Decimal for tolerance comparison to avoid floating-point issues
- **Location validation:** Validates that location_id is not NULL
- **Additional debugging info:** Returns batch_count and has_stock_record for diagnostics

```python
# Example: NULL variant handling
(
    (Batch.variant_id == variant_id)
    if variant_id is not None
    else Batch.variant_id.is_(None)
)
```

---

### 2. Repair Action Suggestions (Task 1)

**File:** `app/api/inventory/batch.py`

Added two new endpoints:

#### GET `/consistency/repair-suggestions`
Analyzes discrepancies and provides actionable recommendations:

| Action | Condition | Description |
|--------|----------|-------------|
| `SYNC_TO_BATCH` | batch_total = 0, stock > 0 | Stock has qty but batch doesn't |
| `CREATE_BATCH` | stock = 0, batch > 0 | Batch has qty but stock doesn't |
| `SYNC_TO_STOCK` | both exist but differ | Batch is authoritative |
| `INVESTIGATE` | both = 0 | Requires manual investigation |

Response includes severity level and repair endpoint.

#### POST `/consistency/repair-suggestions/execute`
Executes repair for a specific product/location:
- `sync_to_batch`: Sets inventory_stock to match batch total

---

### 3. Enhanced Post-Transaction Guard (Task 2)

**File:** `app/services/inventory/inventory_sync_service.py`

Enhanced `PostTransactionGuard` class:

- **`_determine_repair_action()`**: Determines recommended action based on discrepancy pattern
- **`verify_and_raise()`**: Now includes `force_strict` parameter to override company setting
- Includes suggested action in error messages for easier debugging

```python
def _determine_repair_action(self, details: Dict) -> str:
    batch_total = details.get("batch_total", 0)
    stock_quantity = details.get("stock_quantity", 0)
    
    if batch_total == 0 and stock_quantity == 0:
        return "INVESTIGATE"
    elif batch_total == 0:
        return "SYNC_TO_BATCH"
    elif stock_quantity == 0:
        return "CREATE_BATCH"
    else:
        return "SYNC_TO_STOCK"
```

---

### 4. Blocking Validation (Task 4)

**Status:** Already implemented in codebase

**File:** `app/services/warehouse/warehouse.py`

Direct stock CRUD operations are blocked when batch tracking is enabled:

```python
# BLOCK: Prevent manual stock creation when batch tracking is enabled
block_stock_mutation_in_batch_mode(
    self.repo.db, company_id, "create_inventory_stock"
)
```

---

### 5. Scheduled Job Error Handling (Task 6)

**File:** `app/services/inventory/consistency_job.py`

Enhanced `run_consistency_check()` with:

- **Per-company error isolation:** One company failure doesn't stop others
- **Retry logic:** 3 attempts with exponential backoff
- **Failure tracking:** Separate list for failed companies
- **Job failure notification:** Sends notification when job fails

```python
for attempt in range(max_retries):
    try:
        discrepancies = self._check_company(db, company)
        break
    except Exception as e:
        if attempt == max_retries - 1:
            company_failures.append({...})
        else:
            time.sleep(retry_delay * (2 ** attempt))
```

---

### 6. Settings API (Task 7)

**File:** `app/api/inventory/batch.py`

Added endpoints to manage consistency settings:

#### GET `/settings/consistency`
Returns all consistency settings for the company:
- `strict_consistency_check`
- `consistency_tolerance`
- `check_interval_minutes`
- `auto_repair_on_violation`

#### PATCH `/settings/consistency`
Updates consistency settings (partial update):
- Only updates fields that are provided
- `auto_repair_on_violation` remains read-only (manual approval required)

---

### 7. DSR Consistency Verification (Task 8)

**Files:** 
- `app/services/inventory/inventory_sync_service.py` (service class)
- `app/api/inventory/batch.py` (endpoints)

Added `DSRConsistencyService` class with methods:

#### `verify_dsr_allocation_consistency(dsr_assignment_id)`
Checks for:
- **Orphan allocations:** Batch deleted but allocation exists
- **Over-allocations:** Allocation qty > batch qty_on_hand

#### `verify_all_dsr_allocations(company_id)`
Verifies all DSR assignments for a company.

#### API Endpoints:
- `GET /dsr/allocation-consistency/{assignment_id}`
- `GET /dsr/allocation-consistency`

---

### 8. Stock Mutation Audit Trail (Task 5)

**File:** `alembic/versions/phase3_stock_audit.py` (migration created)

**Note:** Migration created but NOT applied. Run with:
```bash
alembic upgrade head
```

Table schema:
```sql
CREATE TABLE inventory.stock_mutation_audit (
    id SERIAL PRIMARY KEY,
    company_id INT NOT NULL,
    product_id INT NOT NULL,
    variant_id INT,
    location_id INT NOT NULL,
    operation VARCHAR(50) NOT NULL,
    qty_delta NUMERIC(18,4) NOT NULL,
    user_id INT,
    ref_type VARCHAR(50),
    ref_id INT,
    success BOOLEAN NOT NULL,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

Indexes for efficient querying:
- `ix_stock_mutation_audit_company_created`
- `ix_stock_mutation_audit_product_created`
- `ix_stock_mutation_audit_operation`
- `ix_stock_mutation_audit_ref`

---

## New API Endpoints Summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/consistency/repair-suggestions` | GET | Get actionable repair recommendations |
| `/consistency/repair-suggestions/execute` | POST | Execute a repair action |
| `/settings/consistency` | GET | Get consistency settings |
| `/settings/consistency` | PATCH | Update consistency settings |
| `/dsr/allocation-consistency/{id}` | GET | Verify single DSR assignment |
| `/dsr/allocation-consistency` | GET | Verify all DSR allocations |

---

## Database Changes

### Required Migration
Run the audit trail migration:
```bash
alembic upgrade head
```

This will create:
- `inventory.stock_mutation_audit` table
- Related indexes

### Existing Tables (already have columns)
- `settings.company_inventory_setting` - Has `strict_consistency_check`, `consistency_tolerance`, `check_interval_minutes`, `auto_repair_on_violation`

---

## Configuration

### Consistency Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `strict_consistency_check` | Boolean | true | Raise exception if invariant violated |
| `consistency_tolerance` | Decimal | 0.0001 | Allowable difference |
| `check_interval_minutes` | Integer | 60 | Scheduled check interval |
| `auto_repair_on_violation` | Boolean | false | Auto-repair (reserved) |

---

## Testing Recommendations

1. **Edge Cases:**
   - Test NULL variant handling
   - Test soft-deleted records
   - Test tolerance comparison

2. **Integration:**
   - Test repair workflow end-to-end
   - Test blocking validation
   - Test DSR consistency checks

3. **Job:**
   - Test retry logic
   - Test per-company isolation

---

## Rollback Plan

If issues arise:

1. **Quick Rollback:** Disable strict mode:
   ```bash
   # Via API
   PATCH /settings/consistency?strict_consistency_check=false
   ```

2. **Full Rollback:** 
   - Set `batch_tracking_enabled = False` for affected companies
   - Revert migrations if needed

---

## Files Modified

| File | Changes |
|------|---------|
| `app/services/inventory/inventory_sync_service.py` | Enhanced verify_invariant, PostTransactionGuard, added DSRConsistencyService |
| `app/api/inventory/batch.py` | Added repair suggestions, settings API, DSR endpoints |
| `app/services/inventory/consistency_job.py` | Enhanced error handling |
| `app/services/inventory/batch_guard.py` | Fixed import |
| `alembic/versions/phase3_stock_audit.py` | Created (not applied) |

---

*Document generated as part of Phase 3 implementation*
