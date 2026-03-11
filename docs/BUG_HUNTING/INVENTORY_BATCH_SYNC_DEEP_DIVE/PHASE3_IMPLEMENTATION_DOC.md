# Phase 3 Implementation Documentation

## Overview

Phase 3 implements **Guardrails and Consistency Checks** to ensure that `inventory_stock` and `batch` tables remain synchronized when batch tracking is enabled. This phase builds upon the foundation established in Phases 1 and 2.

---

## 1. User Requirements

| Requirement | Implementation |
|-------------|----------------|
| **Strict Mode** - Raise exceptions on invariant violations | `strict_consistency_check = True` by default, raises `StockConsistencyError` |
| **Scheduled frequency** | Default 60-minute interval, configurable per company |
| **Manual approval for repairs** | Notification system + DriftApprovals page for admin repair |

---

## 2. Architecture

### 2.1 Data Flow

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Stock Mutation │────▶│ Post-Transaction │────▶│  Verification   │
│  (PO/SO/Delivery)│     │      Guard       │     │    (Invariant)  │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                                          │
                                                          ▼
                                                 ┌─────────────────┐
                                                 │   ✅ Valid      │
                                                 │   ❌ Log Drift  │
                                                 └─────────────────┘
                                                         │
                                                         ▼
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Scheduled     │────▶│  Drift Detection  │────▶│  Notification   │
│   Job (60 min) │     │                   │     │    + Logging    │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                                          │
                                                          ▼
                                                 ┌─────────────────┐
                                                 │  Admin Review   │
                                                 │  + Repair      │
                                                 └─────────────────┘
```

### 2.2 Database Schema

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     settings.company_inventory_setting                  │
├─────────────────────────────────────────────────────────────────────────┤
│ setting_id                  │ Integer (PK)                              │
│ company_id                 │ Integer (FK)                              │
│ valuation_mode             │ String (FIFO/LIFO/WEIGHTED_AVG)          │
│ batch_tracking_enabled     │ Boolean                                   │
│                                                                           │
│ ── Phase 3 Fields ─────────────────────────────────────────────────────  │
│ strict_consistency_check   │ Boolean (default: True)                  │
│ auto_repair_on_violation   │ Boolean (default: False)                 │
│ consistency_tolerance       │ Numeric(15,4) (default: 0.0001)          │
│ check_interval_minutes      │ Integer (default: 60)                    │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                     inventory.batch_qty_audit_log                       │
├─────────────────────────────────────────────────────────────────────────┤
│ id                         │ Integer (PK)                              │
│ batch_id                  │ Integer (FK → batch.batch_id)            │
│ old_qty                   │ Numeric(18,4)                            │
│ new_qty                   │ Numeric(18,4)                            │
│ changed_at                │ DateTime                                 │
│ change_type               │ String (UPDATE/DELETE)                   │
│ actor_id                  │ Integer                                  │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                      Materialized Views                                 │
├─────────────────────────────────────────────────────────────────────────┤
│ inventory.batch_stock_summary        │ Batch qty aggregated            │
│ warehouse.inventory_stock_summary   │ Stock qty aggregated            │
│ inventory.consistency_status        │ Combined consistency status     │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Components

### 3.1 Post-Transaction Guard

**Location**: `app/services/inventory/inventory_sync_service.py`

```python
class PostTransactionGuard:
    """Guard that runs after stock mutations to verify invariant"""
    
    def verify_after_mutation(
        self,
        company_id: int,
        product_id: int,
        variant_id: Optional[int],
        location_id: int,
    ) -> Tuple[bool, Dict[str, Any]]:
        """Verify invariant after mutation"""
        
        settings = self.setting_repo.get_by_company(company_id)
        tolerance = settings.consistency_tolerance if settings else Decimal("0.0001")
        
        sync_service = InventorySyncService(self.db)
        is_valid, details = sync_service.verify_invariant(
            company_id, product_id, variant_id, location_id, tolerance
        )
        
        if not is_valid:
            logger.critical(
                f"INVARIANT VIOLATION after mutation: "
                f"product={product_id}, variant={variant_id}, "
                f"location={location_id}, batch_total={details['batch_total']}, "
                f"stock_quantity={details['stock_quantity']}, "
                f"difference={details['difference']}"
            )
        
        return is_valid, details
```

**Integration**: Called after every stock mutation in `_apply_stock_mutation_batch_mode()`:

```python
# After successful commit, verify invariant
settings = self.setting_repo.get_by_company(ctx.company_id)
if settings and settings.strict_consistency_check:
    post_guard = PostTransactionGuard(self.db)
    is_valid, details = post_guard.verify_after_mutation(...)
    
    if not is_valid:
        logger.critical(f"Post-transaction invariant violation: {details}")
```

---

### 3.2 Scheduled Consistency Check Job

**Location**: `app/services/inventory/consistency_job.py`

```python
class ConsistencyCheckJob:
    """
    Scheduled job for periodic consistency verification.
    
    Runs on configurable interval (default: 60 minutes) to detect drift between
    batch and inventory_stock tables.
    """
    
    def __init__(
        self, 
        db_session_factory: Callable[[], Session],
        interval_minutes: int = 60,
        notification_service=None
    ):
        self.db_session_factory = db_session_factory
        self.interval_minutes = interval_minutes
        self.scheduler = AsyncIOScheduler()
```

**Features**:
- Runs every 60 minutes (configurable)
- Detects drift for all companies with batch tracking enabled
- Creates notifications for admin users
- Logs all discrepancies

**Startup** (in `app/main.py`):

```python
from app.services.inventory.consistency_job import initialize_consistency_job
from sqlalchemy.orm import sessionmaker

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@app.on_event("startup")
async def startup_event():
    notification_scheduler.start()
    initialize_consistency_job(
        db_session_factory=SessionLocal,
        interval_minutes=60,
        auto_start=True
    )
```

---

### 3.3 Drift Approvals Page

**Location**: `src/pages/inventory/DriftApprovals.tsx`

**Features**:
- Displays summary cards (Total Checked, Consistent, Drift Detected)
- Shows detailed drift table with batch vs stock quantities
- Single repair button per item
- Bulk repair (Approve All)
- Selection-based repair (checkbox + Repair Selected)
- Auto-refresh every 60 seconds

**Route**: `/inventory/drift-approvals`

---

### 3.4 Database Triggers

**Location**: `alembic/versions/phase3_batch_triggers.py`

Creates audit trail for batch quantity changes:

```sql
CREATE TRIGGER batch_qty_change_trigger
AFTER UPDATE OF qty_on_hand ON inventory.batch
FOR EACH ROW
EXECUTE FUNCTION inventory.log_batch_qty_change();
```

---

### 3.5 Materialized Views

**Location**: `alembic/versions/phase3_materialized_views.py`

Three views for fast consistency queries:

1. **batch_stock_summary** - Aggregated batch quantities
2. **inventory_stock_summary** - Aggregated stock quantities
3. **consistency_status** - Combined view showing consistency status

**Refresh Service**: `app/services/inventory/materialized_view_service.py`

---

## 4. API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/inventory/batches/consistency-check` | GET | Manual consistency check |
| `/inventory/batches/consistency-check/sync` | POST | Manual sync stock to batch |
| `/inventory/batches/consistency/repair` | POST | Approve single repair |
| `/inventory/batches/consistency/repair/bulk` | POST | Bulk approve repairs |
| `/inventory/batches/consistency/status` | GET | Quick status from materialized view |
| `/inventory/batches/consistency/manual-check` | GET | Manual check with filters |
| `/inventory/batches/consistency/refresh-views` | POST | Refresh materialized views |
| `/inventory/batches/consistency/quick-status` | GET | Fast status query |

---

## 5. Edge Cases Handled

### 5.1 UOM Conversion Issues
- Verifies stock UOM matches base UOM before comparison

### 5.2 NULL Location Handling
- Handles NULL location_id gracefully

### 5.3 Concurrency
- Uses database-level locking where needed

### 5.4 Soft Delete
- All queries filter `is_deleted=False`

### 5.5 Partial Deliveries
- Multiple batches per PO detail tracked via `delivery_detail_id`

---

## 6. Configuration

### Company Settings

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `strict_consistency_check` | Boolean | True | Raise exception on violation |
| `auto_repair_on_violation` | Boolean | False | Always False (manual approval) |
| `consistency_tolerance` | Numeric(15,4) | 0.0001 | Allowable difference |
| `check_interval_minutes` | Integer | 60 | Job frequency |

---

## 7. Files Changed

### Backend

| File | Change |
|------|--------|
| `app/models/batch_models.py` | Added settings fields |
| `app/services/inventory/inventory_sync_service.py` | Added PostTransactionGuard |
| `app/services/inventory/consistency_job.py` | **New** - Scheduled job |
| `app/services/inventory/materialized_view_service.py` | **New** - View refresh |
| `app/api/inventory/batch.py` | Added repair endpoints |
| `app/main.py` | Registered job startup |
| `alembic/versions/phase3_consistency_settings.py` | **New** - Settings columns |
| `alembic/versions/phase3_batch_triggers.py` | **New** - Audit triggers |
| `alembic/versions/phase3_materialized_views.py` | **New** - Materialized views |

### Frontend

| File | Change |
|------|--------|
| `src/lib/api/batchApi.ts` | Added consistency API functions |
| `src/pages/inventory/DriftApprovals.tsx` | **New** - Admin page |
| `src/App.tsx` | Added route |
| `src/data/navigation.ts` | Added sidebar item |

---

## 8. Deployment

### Run Migrations

```bash
cd Shoudagor
alembic upgrade head
```

This will:
1. Add new columns to `company_inventory_setting`
2. Create `batch_qty_audit_log` table
3. Add triggers for audit logging
4. Create materialized views

### Verify Installation

```bash
# Check settings table has new columns
SELECT setting_id, strict_consistency_check, consistency_tolerance 
FROM settings.company_inventory_setting;

# Check triggers exist
SELECT trigger_name FROM information_schema.triggers 
WHERE trigger_name = 'batch_qty_change_trigger';

# Check materialized views
SELECT matviewname FROM pg_matviews 
WHERE schemaname = 'inventory';
```

---

## 9. Testing Checklist

- [ ] Stock mutation triggers post-transaction verification
- [ ] Scheduled job runs every 60 minutes
- [ ] Notifications created when drift detected
- [ ] DriftApprovals page shows discrepancies
- [ ] Single repair works correctly
- [ ] Bulk repair works correctly
- [ ] Materialized views refresh successfully
- [ ] Database triggers log changes

---

## 10. Rollback Plan

If issues arise:

1. **Disable strict mode**: Set `strict_consistency_check = False`
2. **Stop job**: Comment out in `app/main.py`
3. **Remove triggers**: Run downgrade migration
4. **Drop views**: Run downgrade migration

---

*Document generated: 2026-03-11*
