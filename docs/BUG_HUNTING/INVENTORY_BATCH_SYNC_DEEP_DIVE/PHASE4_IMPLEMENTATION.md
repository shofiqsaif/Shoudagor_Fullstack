# Phase 4: Migration and Backfill Implementation

## Overview

Phase 4 implements a comprehensive migration workflow for enabling batch tracking for a company. It provides atomic migration with proper locking, dry-run support, verification, rollback capability, and protection against concurrent modifications during migration.

---

## Architecture

### Data Model

**`InventoryMigration`** (`app/models/migration.py`)

Tracks batch tracking migration status for companies:

| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer | Primary key |
| `company_id` | Integer | Company reference |
| `migration_type` | String | FULL_BACKFILL, STOCK_TO_BATCH, INCREMENTAL |
| `status` | String | PENDING, IN_PROGRESS, VERIFYING, COMPLETED, FAILED, ROLLED_BACK |
| `total_items` | Integer | Total stock records to migrate |
| `processed_items` | Integer | Items processed so far |
| `batches_created` | Integer | Batches created during migration |
| `movements_created` | Integer | Inventory movements created |
| `allocations_created` | Integer | Sales allocations created |
| `errors_count` | Integer | Number of errors encountered |
| `reconciliation_report` | JSON | Post-migration reconciliation result |
| `error_details` | JSON | Error information if failed |
| `is_locked` | Boolean | Whether migration lock is active |
| `locked_at` | DateTime | When lock was acquired |
| `locked_by` | Integer | User who started migration |
| `dry_run_first` | Boolean | Whether dry run was requested |
| `skip_verification` | Boolean | Whether to skip reconciliation |
| `started_at` | DateTime | When migration started |
| `completed_at` | DateTime | When migration completed |

### Status Flow

```
PENDING → IN_PROGRESS → VERIFYING → COMPLETED
                ↓                   
              FAILED  ──→ ROLLED_BACK
```

---

## Services

### InventoryMigrationService

**Location**: `app/services/inventory/inventory_migration_service.py`

Core service managing the migration workflow:

#### Pre-Migration Checks

```python
service = InventoryMigrationService(db)
result = service.pre_migration_check(company_id)

# Returns MigrationPreCheckResult:
# - is_valid: bool - Whether migration can proceed
# - warnings: List[str] - Non-blocking issues
# - errors: List[str] - Blocking issues
# - blocking_errors: List[str] - Critical errors
```

**Checks performed**:
1. Batch tracking is currently disabled
2. No active migrations exist
3. Inventory stock has data to migrate
4. All products have valid location assigned
5. No pending stock operations conflict
6. UOM consistency validation
7. Products exist for migration

#### Starting Migration

```python
migration = service.start_migration(
    company_id=1,
    migration_type="FULL_BACKFILL",  # or "STOCK_TO_BATCH"
    user_id=1,
    dry_run_first=True,  # Preview before actual migration
    skip_verification=False,
)
```

**Migration Types**:
- `FULL_BACKFILL`: Convert current stock + backfill historical PO/SO data
- `STOCK_TO_BATCH`: Only convert current inventory_stock to batches

#### Migration Steps

1. **STOCK_TO_BATCH**: Converts current inventory_stock to batch records
2. **PO_BACKFILL**: Creates batches from historical purchase order deliveries
3. **SO_BACKFILL**: Links historical sales orders to batches
4. **VERIFY**: Runs reconciliation check

#### Lock Management

```python
# Acquire migration lock
service.acquire_migration_lock(company_id, user_id)

# Check if locked
if service.is_migration_locked(company_id):
    # Migration in progress

# Release lock
service.release_migration_lock(company_id)

# Validate no lock (for stock operations)
service.validate_no_migration_lock(company_id)  # Raises MigrationLockError if locked
```

#### Reconciliation

```python
# Run reconciliation check
result = service.run_reconciliation_check(company_id)
# Returns: { matched: int, mismatched: int, items: [...] }

# Fix reconciliation issues
fix_result = service.fix_reconciliation_issues(
    company_id=1,
    auto_fix=False,  # Set True to apply fixes
)
```

#### Rollback

```python
# Rollback a failed/pending migration
migration = service.rollback_migration(migration_id=1, user_id=1)
# Soft deletes synthetic batches and allocations created during migration
```

---

## Lock Integration

### Stock Operations Protection

During migration, stock operations are blocked to prevent data drift. This is implemented in:

#### 1. InventorySyncService

```python
# app/services/inventory/inventory_sync_service.py
class InventorySyncService:
    def apply_stock_mutation(self, ctx: StockChangeContext) -> Dict[str, Any]:
        # Validates no migration lock before any stock change
        self.validate_no_migration_lock(ctx.company_id)
        # ... rest of operation
```

#### 2. Batch Guard

```python
# app/services/inventory/batch_guard.py
def block_stock_mutation_in_batch_mode(db, company_id, operation):
    # Checks migration lock
    sync_service.validate_no_migration_lock(company_id)
    # Checks batch mode
    sync_service.validate_mutation_allowed(company_id, operation)
```

#### 3. Warehouse Service

```python
# app/services/warehouse/warehouse.py
def create_inventory_stock(self, stock, user_id):
    # Uses batch_guard which includes migration check
    block_stock_mutation_in_batch_mode(self.repo.db, company_id, "create_inventory_stock")
```

#### 4. Inventory Adjustment

```python
# app/services/transaction/inventory_adjustment.py
def create_inventory_adjustment(self, adjustment, company_id, user_id):
    sync_service = InventorySyncService(self.repository.db)
    sync_service.validate_no_migration_lock(company_id)
```

### Lock Mechanism

Uses PostgreSQL advisory locks:

```python
lock_key = 10000 + company_id
result = db.execute(
    text(f"SELECT pg_try_advisory_xact_lock({lock_key}) as acquired")
)
```

---

## API Endpoints

### Migration Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/company/inventory/migration/start` | POST | Start new migration |
| `/api/company/inventory/migration/status` | GET | Get current migration status |
| `/api/company/inventory/migration/history` | GET | Get migration history |
| `/api/company/inventory/migration/pre-check` | GET | Run pre-migration checks |
| `/api/company/inventory/migration/{id}` | GET | Get migration details |
| `/api/company/inventory/migration/{id}/verify` | POST | Verify migration reconciliation |
| `/api/company/inventory/migration/{id}/rollback` | POST | Rollback failed migration |
| `/api/company/inventory/migration/reconciliation/check` | GET | Run reconciliation check |
| `/api/company/inventory/migration/reconciliation/fix` | POST | Fix reconciliation issues |

### Settings Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/company/inventory/settings/enable-with-migration` | POST | Enable batch tracking + run migration |

#### Start Migration

```bash
POST /api/company/inventory/migration/start
Query params:
  - migration_type: FULL_BACKFILL | STOCK_TO_BATCH
  - dry_run_first: true | false
  - skip_verification: true | false

Response:
{
  "success": true,
  "migration_id": 1,
  "status": "PENDING",
  "message": "Dry run completed",
  "total_items": 150,
  "reconciliation_report": {...},
  "error_details": null
}
```

#### Enable with Migration

```bash
POST /api/company/inventory/settings/enable-with-migration
Query params:
  - run_migration: true | false
  - dry_run_first: true | false
  - migration_type: FULL_BACKFILL | STOCK_TO_BATCH

Response:
{
  "success": true,
  "settings": {
    "setting_id": 1,
    "company_id": 1,
    "valuation_mode": "FIFO",
    "batch_tracking_enabled": true
  },
  "migration": {
    "migration_id": 1,
    "status": "PENDING",
    "total_items": 150
  }
}
```

---

## Workflow

### Recommended Migration Flow

```
1. Run Pre-Check
   GET /api/company/inventory/migration/pre-check
   
2. Review Warnings/Errors
   - Fix any blocking issues
   - Note any warnings

3. Start Dry Run
   POST /api/company/inventory/migration/start?dry_run_first=true
   
4. Review Dry Run Results
   - Check reconciliation_report
   - Check error_details

5. If Dry Run OK, Start Actual Migration
   POST /api/company/inventory/migration/start?dry_run_first=false
   
6. Verify Migration
   POST /api/company/inventory/migration/{id}/verify
   
7. Fix Any Issues
   POST /api/company/inventory/migration/reconciliation/fix?auto_fix=true
```

### Handling Failures

If migration fails:

```bash
# Check error details
GET /api/company/inventory/migration/{id}

# Rollback if needed
POST /api/company/inventory/migration/{id}/rollback

# Fix issues and retry
```

---

## Edge Cases

### 1. Partial PO Deliveries with Existing Batch

The system handles this by checking for existing batches linked to PO delivery and creating separate batches per delivery.

### 2. DSR Inventory

DSR inventory is migrated separately:

```python
result = service.handle_dsr_inventory_migration(company_id)
# Creates batches at DSR storage locations
```

### 3. Location Assignment

Products without location cannot be migrated. Pre-check validates:

```python
location_issues = service.validate_location_assignment(company_id)
# Returns { total_issues: int, issues: [...], can_migrate: bool }
```

### 4. Concurrent Operations

During migration, stock operations are blocked:

```
Stock Operation → Check Migration Lock → Blocked if Migration Active
```

---

## Error Handling

### Exception Types

| Exception | HTTP Code | Description |
|-----------|-----------|-------------|
| `MigrationLockError` | 409 | Migration already in progress |
| `PreMigrationCheckError` | 400 | Pre-checks failed |
| `ReconciliationError` | 422 | Reconciliation issues found |

### Example Error Response

```json
{
  "detail": "Migration already in progress for company 1. Migration ID: 5, Status: IN_PROGRESS"
}
```

---

## Database Migration

### Required Migration

```bash
alembic revision --autogenerate -m "Add inventory_migration table"
alembic upgrade head
```

Creates table: `inventory.inventory_migration`

---

## Testing Checklist

- [ ] Pre-migration check passes for valid data
- [ ] Pre-migration check fails when batch tracking enabled
- [ ] Pre-migration check fails when migration in progress
- [ ] Dry run completes without modifying data
- [ ] Full migration creates correct batches
- [ ] Migration lock blocks stock operations
- [ ] Rollback removes synthetic batches
- [ ] Reconciliation detects mismatches
- [ ] Auto-fix corrects inventory_stock

---

## Files Reference

| File | Purpose |
|------|---------|
| `app/models/migration.py` | InventoryMigration model |
| `app/services/inventory/inventory_migration_service.py` | Migration service |
| `app/services/inventory/inventory_sync_service.py` | Stock sync + lock check |
| `app/services/inventory/batch_guard.py` | Batch mode enforcement |
| `app/services/transaction/inventory_adjustment.py` | Adjustment + lock check |
| `app/api/inventory/batch.py` | API endpoints |
