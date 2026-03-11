# Phase 3 Implementation Plan: Guardrails and Consistency Checks

## Overview

Phase 3 focuses on implementing guardrails and consistency checks to ensure that `inventory_stock` and `batch` tables remain synchronized when batch tracking is enabled. This phase builds upon the foundation established in Phases 1 and 2.

Based on deep analysis of `docs/INVENTORY_BATCH_SYNC_DEEP_DIVE.md` and the existing codebase, this document outlines the implementation strategy with comprehensive edge case handling.

---

## 1. User Requirements (Incorporated)

| Requirement | Implementation Decision |
|-------------|------------------------|
| **Strict Mode** - Raise exceptions on invariant violations | `strict_consistency_check = True` by default, raises `StockConsistencyError` |
| **Scheduled frequency** | Default 60-minute interval, configurable per company |
| **Manual approval for repairs** | Create notification/alert system + Admin approval page for drift repair |

---

## 2. Current State Assessment

### Already Implemented (Phase 1 & 2)

| Component | Location | Status |
|-----------|----------|--------|
| `InventorySyncService` | `app/services/inventory/inventory_sync_service.py` | ✅ Complete |
| `verify_invariant()` | Same as above | ✅ Complete |
| `verify_all_invariants()` | Same as above | ✅ Complete |
| `sync_stock_to_batch()` | Same as above | ✅ Complete |
| POST `/consistency-check/sync` | `app/api/inventory/batch.py:893` | ✅ Complete |
| GET `/consistency-check` | `app/api/inventory/batch.py:828` | ✅ Complete |
| `ReconciliationService` | `app/services/inventory/backfill_service.py:721` | ✅ Complete |
| `InventoryStockMutationGuard` | `app/services/inventory/inventory_sync_service.py:1182` | ✅ Complete |

### Gap Analysis for Phase 3

1. **No post-transaction invariant verification** - Mutations don't automatically verify consistency after execution
2. **No scheduled reconciliation job** - No automated drift detection with 60-min interval
3. **No database triggers** - No audit-level enforcement
4. **No materialized views** - Slow reporting on large datasets
5. **No manual approval workflow** - No page to review drift and approve repairs

---

## 3. Implementation Components

### 3.1 Post-Transaction Consistency Guard

**Purpose**: Automatically verify the invariant (batch total == inventory_stock) after every stock mutation in batch mode. Raises exception if divergent.

**Implementation Location**: `app/services/inventory/inventory_sync_service.py`

**New Configuration Fields** (add to `CompanyInventorySetting` model):
```python
# In app/models/inventory.py - CompanyInventorySetting
strict_consistency_check = Column(Boolean, default=True, nullable=False)
auto_repair_on_violation = Column(Boolean, default=False, nullable=False)  # Always False - manual approval
consistency_tolerance = Column(Numeric(15, 4), default=Decimal("0.0001"))
check_interval_minutes = Column(Integer, default=60)  # Configurable interval
```

**New Class**:

```python
class PostTransactionGuard:
    """Guard that runs after stock mutations to verify invariant"""
    
    def __init__(self, db: Session):
        self.db = db
        self.setting_repo = CompanyInventorySettingRepository(db)
    
    def verify_after_mutation(
        self,
        company_id: int,
        product_id: int,
        variant_id: Optional[int],
        location_id: int,
    ) -> Tuple[bool, Dict[str, Any]]:
        """Verify invariant after mutation, raise if divergent"""
        
        settings = self.setting_repo.get_by_company(company_id)
        tolerance = settings.consistency_tolerance if settings else Decimal("0.0001")
        
        sync_service = InventorySyncService(self.db)
        is_valid, details = sync_service.verify_invariant(
            company_id, product_id, variant_id, location_id, tolerance
        )
        
        if not is_valid:
            # Log critical error
            logger.critical(
                f"INVARIANT VIOLATION after mutation: "
                f"product={product_id}, variant={variant_id}, "
                f"location={location_id}, batch_total={details['batch_total']}, "
                f"stock_quantity={details['stock_quantity']}, "
                f"difference={details['difference']}"
            )
        
        return is_valid, details
```

**Integration Point**: Add to `_apply_stock_mutation_batch_mode()` after successful commit:

```python
# After successful commit, verify invariant
settings = self.setting_repo.get_by_company(ctx.company_id)

if settings and settings.strict_consistency_check:
    post_guard = PostTransactionGuard(self.db)
    is_valid, details = post_guard.verify_after_mutation(
        ctx.company_id,
        ctx.product_id,
        ctx.variant_id,
        ctx.location_id
    )
    
    if not is_valid:
        # Rollback and raise exception
        self.db.rollback()
        raise StockConsistencyError(
            f"Post-mutation invariant violated. Batch: {details['batch_total']}, "
            f"Stock: {details['stock_quantity']}, Diff: {details['difference']}. "
            f"Operation rolled back."
        )
```

---

### 3.2 Scheduled Reconciliation Job

**Purpose**: Automatically detect and report drift on a 60-minute scheduled basis.

**Implementation Location**: New file `app/services/inventory/consistency_job.py`

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class ConsistencyCheckJob:
    """
    Scheduled job for periodic consistency verification.
    
    Runs on configurable interval (default: 60 minutes) to detect drift between
    batch and inventory_stock tables.
    """
    
    def __init__(self, db_session_factory, interval_minutes: int = 60):
        self.db_session_factory = db_session_factory
        self.interval_minutes = interval_minutes
        self.scheduler = AsyncIOScheduler()
        
    def start(self):
        """Start the scheduled job"""
        self.scheduler.add_job(
            self.run_consistency_check,
            trigger=IntervalTrigger(minutes=self.interval_minutes),
            id="inventory_consistency_check",
            replace_existing=True,
        )
        logger.info(
            f"Consistency check job scheduled every {self.interval_minutes} minutes"
        )
        
    def run_consistency_check(self) -> Dict[str, Any]:
        """
        Run consistency check for all companies with batch tracking enabled.
        
        This runs as a background task and logs/records any discrepancies.
        Creates notifications for admin users when drift is detected.
        """
        db = self.db_session_factory()
        try:
            # Get all companies with batch tracking enabled
            companies = self._get_batch_enabled_companies(db)
            
            total_discrepancies = 0
            for company in companies:
                discrepancies = self._check_company(db, company)
                total_discrepancies += len(discrepancies)
                
                if discrepancies:
                    self._log_discrepancies(company.id, discrepancies)
                    # Create notification for drift detection
                    self._create_drift_notification(db, company.id, discrepancies)
                    
            logger.info(
                f"Consistency check complete: {total_discrepancies} discrepancies "
                f"across {len(companies)} companies"
            )
            
            return {
                "companies_checked": len(companies),
                "total_discrepancies": total_discrepancies,
            }
            
        except Exception as e:
            logger.error(f"Consistency check job failed: {e}")
            raise
        finally:
            db.close()
            
    def _get_batch_enabled_companies(self, db: Session) -> List[Any]:
        """Get all companies with batch tracking enabled"""
        from app.models.batch_models import CompanyInventorySetting
        from app.models.security import AppClientCompany
        
        settings = db.query(CompanyInventorySetting).filter(
            CompanyInventorySetting.batch_tracking_enabled == True
        ).all()
        
        company_ids = [s.company_id for s in settings]
        return db.query(AppClientCompany).filter(
            AppClientCompany.id.in_(company_ids),
            AppClientCompany.is_deleted == False
        ).all()
        
    def _check_company(
        self, db: Session, company: Any
    ) -> List[Dict[str, Any]]:
        """Check consistency for a single company"""
        from app.services.inventory.inventory_sync_service import InventorySyncService
        
        sync_service = InventorySyncService(db)
        
        # Get company-specific settings
        settings_repo = CompanyInventorySettingRepository(db)
        settings = settings_repo.get_by_company(company.id)
        
        interval = settings.check_interval_minutes if settings else 60
        
        result = sync_service.verify_all_invariants(company.id)
        return result.get("discrepancies", [])
        
    def _log_discrepancies(
        self, company_id: int, discrepancies: List[Dict[str, Any]]
    ):
        """Log discrepancies to application log"""
        for d in discrepancies:
            logger.warning(
                f"Consistency drift: company={company_id}, "
                f"product={d['product_id']}, variant={d['variant_id']}, "
                f"location={d['location_id']}, batch={d['batch_total']}, "
                f"stock={d['stock_quantity']}, diff={d['difference']}"
            )
            
    def _create_drift_notification(
        self, db: Session, company_id: int, discrepancies: List[Dict[str, Any]]
    ):
        """Create notification for admin users about drift"""
        from app.models.notification import Notification, NotificationType
        from app.models.security import User
        
        # Get or create notification type
        notif_type = db.query(NotificationType NotificationType.type_code).filter(
            == "INVENTORY_DR        ).first()
        
        if not notif_type:
            notIFT"
if_type = NotificationType(
                type_code="INVENTORY_DRIFT",
                name="Inventory Drift Detected",
                description="Notifies when batch and inventory_stock are out of sync",
                priority="high",
            )
            db.add(notif_type)
            db.flush()
        
        # Get company admin users
        admin_users = db.query(User).filter(
            User.company_id == company_id,
            User.is_deleted == False,
            User.role.in_(["admin", "super_admin"])
        ).all()
        
        # Create notification for each admin
        for user in admin_users:
            notification = Notification(
                company_id=company_id,
                user_id=user.user_id,
                notification_type_id=notif_type.id,
                title="Inventory Drift Detected",
                message=f"{len(discrepancies)} inventory drift(s) detected. Review and approve repairs.",
                priority="high",
                is_read=False,
                metadata_json={
                    "discrepancy_count": len(discrepancies),
                    "company_id": company_id,
                    "requires_approval": True,
                }
            )
            db.add(notification)
        
        db.commit()
        
    def shutdown(self):
        """Shutdown the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
```

**Integration**: Add to `app/main.py`:

```python
from app.services.inventory.consistency_job import ConsistencyCheckJob
from app.core.database import engine
from sqlalchemy.orm import sessionmaker

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Initialize and start consistency job
consistency_job = ConsistencyCheckJob(
    db_session_factory=SessionLocal,
    interval_minutes=60  # Default 60 minutes as per requirement
)

@app.on_event("startup")
async def startup_event():
    # ... existing startup code ...
    consistency_job.start()

@app.on_event("shutdown")
async def shutdown_event():
    # ... existing shutdown code ...
    consistency_job.shutdown()
```

---

### 3.3 Drift Approval Page (Frontend)

**Purpose**: Provide admin users a page to view drift notifications and manually approve repairs.

**New Backend Endpoint**: `POST /api/company/inventory/consistency/approve-repair`

```python
# In app/api/inventory/batch.py - add to consistency router

@consistency_router.post("/approve-repair")
async def approve_repair(
    product_id: int,
    variant_id: Optional[int] = None,
    location_id: int,
    repair_type: str = Query(..., description="sync_to_batch or sync_to_stock"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    company_id: int = Depends(get_current_company_id),
):
    """
    Manually approve and execute a stock repair.
    
    Repair types:
    - sync_to_batch: Set inventory_stock to match batch total
    - sync_to_stock: Set batch qty_on_hand to match inventory_stock (rare)
    """
    # Verify user has admin role
    if current_user.get("role") not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Admin role required")
    
    sync_service = InventorySyncService(db)
    
    # Execute the repair
    if repair_type == "sync_to_batch":
        result = sync_service.sync_stock_to_batch(
            company_id=company_id,
            product_id=product_id,
            variant_id=variant_id,
            location_id=location_id,
            user_id=current_user.get("user_id", 1),
        )
    elif repair_type == "sync_to_stock":
        # This is rare - batch is source of truth
        raise HTTPException(
            status_code=400,
            detail="sync_to_stock requires manual intervention. Contact support."
        )
    else:
        raise HTTPException(status_code=400, detail="Invalid repair_type")
    
    # Log the approval action
    logger.info(
        f"Drift repair approved: user={current_user['user_id']}, "
        f"company={company_id}, product={product_id}, "
        f"repair_type={repair_type}, result={result}"
    )
    
    return {
        "success": True,
        "message": "Repair executed successfully",
        "result": result,
    }


@consistency_router.post("/approve-repair/bulk")
async def bulk_approve_repairs(
    repairs: List[RepairRequest],
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    company_id: int = Depends(get_current_company_id),
):
    """Bulk approve and execute multiple stock repairs"""
    
    if current_user.get("role") not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Admin role required")
    
    sync_service = InventorySyncService(db)
    
    results = []
    errors = []
    
    for repair in repairs:
        try:
            result = sync_service.sync_stock_to_batch(
                company_id=company_id,
                product_id=repair.product_id,
                variant_id=repair.variant_id,
                location_id=repair.location_id,
                user_id=current_user.get("user_id", 1),
            )
            results.append({
                "product_id": repair.product_id,
                "variant_id": repair.variant_id,
                "location_id": repair.location_id,
                "success": True,
                "result": result,
            })
        except Exception as e:
            errors.append({
                "product_id": repair.product_id,
                "variant_id": repair.variant_id,
                "location_id": repair.location_id,
                "error": str(e),
            })
    
    return {
        "total": len(repairs),
        "successful": len(results),
        "failed": len(errors),
        "results": results,
        "errors": errors,
    }
```

**Frontend Page**: New page `src/pages/inventory/DriftApprovals.tsx`

```typescript
import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { DataTable } from '@/components/ui/data-table';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import { batchApi } from '@/lib/api/batchApi';

interface DriftItem {
  product_id: number;
  variant_id: number | null;
  location_id: number;
  batch_total: number;
  stock_quantity: number;
  difference: number;
}

export default function DriftApprovals() {
  const queryClient = useQueryClient();
  
  // Fetch drift notifications
  const { data: driftData, isLoading } = useQuery({
    queryKey: ['inventory-drift'],
    queryFn: () => batchApi.getConsistencyCheck(),
  });

  // Fetch pending approvals from notifications
  const { data: notifications } = useQuery({
    queryKey: ['notifications', 'inventory-drift'],
    queryFn: () => notificationApi.getNotifications({ 
      type: 'INVENTORY_DRIFT',
      is_read: false 
    }),
  });

  // Repair mutation
  const repairMutation = useMutation({
    mutationFn: (item: DriftItem) => batchApi.approveRepair({
      product_id: item.product_id,
      variant_id: item.variant_id,
      location_id: item.location_id,
      repair_type: 'sync_to_batch',
    }),
    onSuccess: () => {
      toast.success('Repair approved successfully');
      queryClient.invalidateQueries({ queryKey: ['inventory-drift'] });
    },
    onError: (error) => {
      toast.error('Repair failed: ' + error.message);
    },
  });

  // Bulk repair mutation
  const bulkRepairMutation = useMutation({
    mutationFn: (items: DriftItem[]) => batchApi.bulkApproveRepair(items),
    onSuccess: (data) => {
      toast.success(`Repaired ${data.successful} items`);
      if (data.errors.length > 0) {
        toast.error(`${data.errors.length} items failed`);
      }
      queryClient.invalidateQueries({ queryKey: ['inventory-drift'] });
    },
  });

  const discrepancies = driftData?.discrepancies || [];

  return (
    <div className="container mx-auto py-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Inventory Drift Approvals</h1>
        <div className="space-x-2">
          <Button 
            variant="outline"
            onClick={() => queryClient.invalidateQueries({ queryKey: ['inventory-drift'] })}
          >
            Refresh
          </Button>
          <Button
            disabled={discrepancies.length === 0}
            onClick={() => bulkRepairMutation.mutate(discrepancies)}
          >
            Approve All Repairs ({discrepancies.length})
          </Button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Total Checked</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{driftData?.consistency?.total_checked || 0}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Consistent</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              {driftData?.consistency?.valid_count || 0}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Drift Detected</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">
              {driftData?.consistency?.invalid_count || 0}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Pending Approvals</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-amber-600">
              {notifications?.filter(n => !n.is_read).length || 0}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Drift Table */}
      <Card>
        <CardHeader>
          <CardTitle>Drift Details</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div>Loading...</div>
          ) : discrepancies.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              No drift detected. All inventory is consistent.
            </div>
          ) : (
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-3 px-4">Product</th>
                  <th className="text-left py-3 px-4">Variant</th>
                  <th className="text-left py-3 px-4">Location</th>
                  <th className="text-right py-3 px-4">Batch Total</th>
                  <th className="text-right py-3 px-4">Stock Qty</th>
                  <th className="text-right py-3 px-4">Difference</th>
                  <th className="text-center py-3 px-4">Action</th>
                </tr>
              </thead>
              <tbody>
                {discrepancies.map((item: DriftItem, idx: number) => (
                  <tr key={idx} className="border-b hover:bg-gray-50">
                    <td className="py-3 px-4">{item.product_id}</td>
                    <td className="py-3 px-4">{item.variant_id || '-'}</td>
                    <td className="py-3 px-4">{item.location_id}</td>
                    <td className="py-3 px-4 text-right">{item.batch_total.toFixed(4)}</td>
                    <td className="py-3 px-4 text-right">{item.stock_quantity.toFixed(4)}</td>
                    <td className="py-3 px-4 text-right">
                      <Badge variant={item.difference > 0 ? 'destructive' : 'secondary'}>
                        {item.difference.toFixed(4)}
                      </Badge>
                    </td>
                    <td className="py-3 px-4 text-center">
                      <Button
                        size="sm"
                        onClick={() => repairMutation.mutate(item)}
                        disabled={repairMutation.isPending}
                      >
                        Approve
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
```

**Add Route to App.tsx**:

```typescript
// Add to routes array
{
  path: '/inventory/drift-approvals',
  element: <AdminRoute><DriftApprovals /></AdminRoute>,
},
```

---

### 3.4 Database Triggers (Optional Audit Layer)

**Purpose**: Provide database-level audit trail for changes.

**Implementation**: Create migration file `alembic/versions/xxxx_add_inventory_triggers.py`

```python
"""
Add database triggers for inventory consistency audit.
"""

from alembic import op
import sqlalchemy as sa


def upgrade():
    # Create audit log table
    op.create_table(
        'batch_qty_audit_log',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('batch_id', sa.Integer(), sa.ForeignKey('inventory.batch.batch_id'), nullable=False),
        sa.Column('old_qty', sa.Numeric(15, 4)),
        sa.Column('new_qty', sa.Numeric(15, 4)),
        sa.Column('changed_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('change_type', sa.String(10)),  # UPDATE, DELETE
        sa.Column('actor_id', sa.Integer(), nullable=True),
    )
    
    # Trigger function
    op.execute("""
        CREATE OR REPLACE FUNCTION log_batch_qty_change()
        RETURNS TRIGGER AS $$
        BEGIN
            IF OLD.qty_on_hand IS DISTINCT FROM NEW.qty_on_hand THEN
                INSERT INTO inventory.batch_qty_audit_log (
                    batch_id, old_qty, new_qty, changed_at, change_type
                ) VALUES (
                    NEW.batch_id,
                    OLD.qty_on_hand,
                    NEW.qty_on_hand,
                    NOW(),
                    TG_OP
                );
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    # Attach trigger
    op.execute("""
        CREATE TRIGGER batch_qty_change_trigger
        AFTER UPDATE OF qty_on_hand ON inventory.batch
        FOR EACH ROW
        EXECUTE FUNCTION log_batch_qty_change();
    """)


def downgrade():
    op.execute("DROP TRIGGER IF EXISTS batch_qty_change_trigger ON inventory.batch")
    op.execute("DROP FUNCTION IF EXISTS log_batch_qty_change()")
    op.drop_table('batch_qty_audit_log')
```

---

### 3.5 Materialized Views for Fast Reporting

**Purpose**: Provide fast consistency status queries without scanning entire tables.

**Implementation**: Create migration `alembic/versions/xxxx_add_inventory_materialized_views.py`

```python
"""
Add materialized views for inventory consistency reporting.
"""

from alembic import op
import sqlalchemy as sa


def upgrade():
    # Materialized view for batch stock summary
    op.execute("""
        CREATE MATERIALIZED VIEW inventory.batch_stock_summary AS
        SELECT 
            b.company_id,
            b.product_id,
            b.variant_id,
            b.location_id,
            SUM(b.qty_on_hand) as total_batch_qty,
            COUNT(b.batch_id) as batch_count
        FROM inventory.batch b
        WHERE b.status = 'active' AND b.is_deleted = FALSE
        GROUP BY b.company_id, b.product_id, b.variant_id, b.location_id
        WITH DATA;
    """)
    
    # Materialized view for inventory stock
    op.execute("""
        CREATE MATERIALIZED VIEW warehouse.inventory_stock_summary AS
        SELECT 
            company_id,
            product_id,
            variant_id,
            location_id,
            SUM(quantity) as total_stock_qty,
            COUNT(*) as stock_record_count
        FROM warehouse.inventory_stock
        WHERE is_deleted = FALSE
        GROUP BY company_id, product_id, variant_id, location_id
        WITH DATA;
    """)
    
    # Materialized view for consistency status
    op.execute("""
        CREATE MATERIALIZED VIEW inventory.consistency_status AS
        SELECT 
            COALESCE(b.company_id, s.company_id) as company_id,
            COALESCE(b.product_id, s.product_id) as product_id,
            COALESCE(b.variant_id, s.variant_id) as variant_id,
            COALESCE(b.location_id, s.location_id) as location_id,
            b.total_batch_qty,
            s.total_stock_qty,
            CASE 
                WHEN b.total_batch_qty IS NULL AND s.total_stock_qty IS NULL 
                THEN 'both_missing'
                WHEN b.total_batch_qty IS NULL 
                THEN 'batch_missing'
                WHEN s.total_stock_qty IS NULL 
                THEN 'stock_missing'
                WHEN ABS(COALESCE(b.total_batch_qty, 0) - COALESCE(s.total_stock_qty, 0)) > 0.0001 
                THEN 'inconsistent'
                ELSE 'consistent'
            END as status
        FROM inventory.batch_stock_summary b
        FULL OUTER JOIN warehouse.inventory_stock_summary s
            ON b.company_id = s.company_id
            AND b.product_id = s.product_id
            AND COALESCE(b.variant_id, 0) = COALESCE(s.variant_id, 0)
            AND b.location_id = s.location_id
        WITH DATA;
    """)
    
    # Create indexes
    op.execute("""
        CREATE UNIQUE INDEX batch_stock_summary_idx 
        ON inventory.batch_stock_summary (company_id, product_id, variant_id, location_id)
    """)
    op.execute("""
        CREATE UNIQUE INDEX inventory_stock_summary_idx 
        ON warehouse.inventory_stock_summary (company_id, product_id, variant_id, location_id)
    """)
    op.execute("""
        CREATE UNIQUE INDEX consistency_status_idx 
        ON inventory.consistency_status (company_id, product_id, variant_id, location_id)
    """)


def downgrade():
    op.execute("DROP MATERIALIZED VIEW IF EXISTS inventory.consistency_status")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS warehouse.inventory_stock_summary")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS inventory.batch_stock_summary")
```

**Refresh Service**:

```python
class MaterializedViewRefreshService:
    """Service to refresh materialized views"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def refresh_all(self):
        """Refresh all inventory materialized views"""
        self.db.execute(text("REFRESH MATERIALIZED VIEW CONCURRENTLY inventory.batch_stock_summary"))
        self.db.execute(text("REFRESH MATERIALIZED VIEW CONCURRENTLY warehouse.inventory_stock_summary"))
        self.db.execute(text("REFRESH MATERIALIZED VIEW CONCURRENTLY inventory.consistency_status"))
        self.db.commit()
    
    def get_quick_status(self, company_id: int) -> Dict:
        """Get quick consistency summary from materialized view"""
        result = self.db.execute(
            text("""
                SELECT status, COUNT(*) as count
                FROM inventory.consistency_status
                WHERE company_id = :company_id
                GROUP BY status
            """),
            {"company_id": company_id}
        )
        return {row.status: row.count for row in result}
```

**New API Endpoint**:

```python
@consistency_router.get("/status")
async def get_quick_consistency_status(
    company_id: int = Depends(get_current_company_id),
    db: Session = Depends(get_db),
):
    """Get quick consistency status from materialized view"""
    from app.services.inventory.materialized_view_service import MaterializedViewRefreshService
    
    service = MaterializedViewRefreshService(db)
    status = service.get_quick_status(company_id)
    
    return {
        "company_id": company_id,
        "status": status,
    }


@consistency_router.post("/refresh-views")
async def refresh_materialized_views(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Manually refresh materialized views"""
    from app.services.inventory.materialized_view_service import MaterializedViewRefreshService
    
    service = MaterializedViewRefreshService(db)
    service.refresh_all()
    
    return {"success": True, "message": "Materialized views refreshed"}
```

---

## 4. Edge Cases and Error Handling

### 4.1 UOM Conversion Issues

```python
def verify_invariant_with_uom_check(
    self,
    company_id: int,
    product_id: int,
    variant_id: Optional[int],
    location_id: int,
) -> Dict[str, Any]:
    """Verify invariant with UOM conversion validation"""
    
    product = db.query(Product).get(product_id)
    base_uom = product.base_uom
    
    batch_total = self.get_batch_total_qty(...)
    
    stock = self._get_stock_record(...)
    
    if stock and stock.unit_of_measure_id != base_uom.uom_id:
        return {
            "has_issue": True,
            "issue_type": "uom_mismatch",
            "message": f"Stock UOM differs",
            "requires from base UOM_conversion": True,
        }
    
    return {"has_issue": False}
```

### 4.2 NULL Location Handling

```python
def handle_null_location_discrepancy(
    self,
    company_id: int,
    product_id: int,
    variant_id: Optional[int],
) -> List[Dict[str, Any]]:
    """Find and report NULL location discrepancies"""
    
    null_location_stocks = db.query(InventoryStock).filter(
        InventoryStock.company_id == company_id,
        InventoryStock.location_id.is_(None),
        InventoryStock.is_deleted == False,
    ).all()
    
    discrepancies = []
    for stock in null_location_stocks:
        batch_at_default = db.query(Batch).filter(
            Batch.company_id == company_id,
            Batch.product_id == stock.product_id,
            Batch.variant_id == stock.variant_id,
            Batch.location_id.isnot(None),
            Batch.status == 'active',
        ).first()
        
        if batch_at_default and stock.quantity > 0:
            discrepancies.append({
                "type": "null_location_stock",
                "product_id": stock.product_id,
                "suggested_location_id": batch_at_default.location_id,
            })
    
    return discrepancies
```

### 4.3 Concurrency Handling

```python
from sqlalchemy.orm import with_for_update

def atomic_mutation_with_lock(
    self,
    ctx: StockChangeContext,
) -> Dict[str, Any]:
    """Execute mutation with row-level locking"""
    
    # Lock the stock record
    stock = db.query(InventoryStock).filter(
        InventoryStock.company_id == ctx.company_id,
        InventoryStock.product_id == ctx.product_id,
        InventoryStock.location_id == ctx.location_id,
    ).with_for_update().first()
    
    # Proceed with mutation...
```

### 4.4 Soft Delete Handling

```python
def verify_with_soft_delete_awareness(
    self,
    company_id: int,
    product_id: int,
    variant_id: Optional[int],
    location_id: int,
) -> Dict[str, Any]:
    """Verify invariant accounting for soft-delete states"""
    
    active_batch_total = self.get_batch_total_qty(...)  # Already filters is_deleted=False
    
    stock = db.query(InventoryStock).filter(
        InventoryStock.company_id == company_id,
        InventoryStock.product_id == product_id,
        InventoryStock.location_id == location_id,
        InventoryStock.is_deleted == False,
    ).first()
    
    stock_qty = stock.quantity if stock else Decimal("0")
    
    return {
        "active_batch_total": float(active_batch_total),
        "stock_quantity": float(stock_qty),
    }
```

### 4.5 DSR Flow Consistency

```python
def verify_dsr_allocation_consistency(
    self,
    dsr_assignment_id: int,
) -> Dict[str, Any]:
    """Verify DSR allocations are consistent with batches"""
    
    dsr_allocations = db.query(DSRBatchAllocation).filter(
        DSRBatchAllocation.assignment_id == dsr_assignment_id,
        DSRBatchAllocation.is_deleted == False,
    ).all()
    
    issues = []
    
    for alloc in dsr_allocations:
        batch = db.query(Batch).get(alloc.batch_id)
        
        if not batch:
            issues.append({
                "type": "orphan_allocation",
                "allocation_id": alloc.dsr_allocation_id,
            })
            continue
            
        if alloc.qty_allocated > batch.qty_on_hand:
            issues.append({
                "type": "over_allocation",
                "batch_id": alloc.batch_id,
                "allocated": float(alloc.qty_allocated),
                "available": float(batch.qty_on_hand),
            })
    
    return {
        "assignment_id": dsr_assignment_id,
        "issue_count": len(issues),
        "issues": issues,
    }
```

---

## 5. API Endpoints Summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/inventory/consistency-check` | GET | Manual consistency check |
| `/inventory/consistency-check/sync` | POST | Manual sync stock to batch |
| `/inventory/consistency/status` | GET | Quick status from materialized view |
| `/inventory/consistency/refresh-views` | POST | Refresh materialized views |
| `/inventory/consistency/approve-repair` | POST | Approve single repair |
| `/inventory/consistency/approve-repair/bulk` | POST | Bulk approve repairs |

---

## 6. Testing Strategy

### 6.1 Unit Tests

| Test | Expected Behavior |
|------|-------------------|
| `test_verify_after_mutation_success` | Invariant verified after successful mutation |
| `test_verify_after_mutation_failure` | Exception raised on invariant violation |
| `test_tolerance_handling` | Small differences are tolerated |
| `test_job_detects_drift` | Job detects drift between batch and stock |
| `test_creates_notification` | Notification created when drift detected |
| `test_repair_approval` | Repair only executes after approval |

### 6.2 Integration Tests

| Test Scenario | Expected Result |
|---------------|-----------------|
| PO delivery with partial quantities | Batch total = stock after each delivery |
| Sales delivery + return | Invariant maintained after full cycle |
| Negative inventory adjustment | Stock decrements, batch decrements, invariant holds |
| Stock transfer between locations | Both source and dest maintain invariant |
| DSR load → sale → unload | All stages maintain consistency |
| Concurrent deliveries | No race conditions, invariant holds |

---

## 7. Implementation Phases

### Phase 3.1: Post-Transaction Guard + Config (Week 1)
- [ ] Add config fields to `CompanyInventorySetting`
- [ ] Add `PostTransactionGuard` class
- [ ] Integrate into `InventorySyncService`
- [ ] Unit tests

### Phase 3.2: Scheduled Job (Week 2)
- [ ] Create `ConsistencyCheckJob` service
- [ ] Add to main.py startup/shutdown
- [ ] Integrate with notification system
- [ ] Integration tests

### Phase 3.3: Drift Approval Workflow (Week 2-3)
- [ ] Add repair approval API endpoints
- [ ] Create `DriftApprovals.tsx` frontend page
- [ ] Add route to App.tsx
- [ ] Test approval flow

### Phase 3.4: Database Triggers (Week 3)
- [ ] Create migration for audit log table
- [ ] Create trigger functions
- [ ] Attach triggers to batch table

### Phase 3.5: Materialized Views (Week 3-4)
- [ ] Create migration for materialized views
- [ ] Add refresh service
- [ ] Create fast-status API endpoint

### Phase 3.6: Testing & Documentation (Week 5)
- [ ] Comprehensive unit tests
- [ ] Integration tests
- [ ] Update API documentation

---

## 8. Rollback Plan

If Phase 3 introduces issues:

1. **Disable post-transaction guard**: Set `strict_consistency_check = False` in settings
2. **Stop scheduled job**: Comment out job registration in main.py
3. **Remove triggers**: Run downgrade migration
4. **Drop materialized views**: Run downgrade migration

---

## 9. Success Criteria

- [ ] All stock mutations verify invariant after execution and raise exception if divergent
- [ ] Scheduled job runs every 60 minutes without errors
- [ ] Drift notifications appear in notification center
- [ ] Admin can view drift page and approve repairs
- [ ] Materialized views refresh within 30 seconds for companies with <10k products
- [ ] No regression in existing workflows

---

## 10. File Changes Summary

### New Files
- `app/services/inventory/consistency_job.py` - Scheduled consistency check
- `app/services/inventory/materialized_view_service.py` - View refresh service
- `src/pages/inventory/DriftApprovals.tsx` - Frontend approval page
- `alembic/versions/xxxx_add_inventory_triggers.py` - Database triggers
- `alembic/versions/xxxx_add_inventory_materialized_views.py` - Materialized views
- `alembic/versions/xxxx_add_consistency_settings.py` - New config fields

### Modified Files
- `app/services/inventory/inventory_sync_service.py` - Add PostTransactionGuard
- `app/models/inventory.py` - Add settings fields
- `app/main.py` - Register scheduled job
- `app/api/inventory/batch.py` - Add new endpoints
- `src/App.tsx` - Add drift approvals route

---

*Document prepared based on deep analysis of INVENTORY_BATCH_SYNC_DEEP_DIVE.md and existing codebase.*
*Last updated: 2026-03-11*
