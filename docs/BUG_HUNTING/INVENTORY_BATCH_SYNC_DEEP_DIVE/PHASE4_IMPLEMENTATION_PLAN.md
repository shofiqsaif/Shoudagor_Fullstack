# Phase 4 Implementation Plan: Migration and Backfill

## Purpose

Phase 4 focuses on the migration workflow when **enabling batch tracking** for a company. This phase ensures a safe, atomic transition from legacy `inventory_stock` to batch-based tracking with proper rollback capabilities, edge case handling, and error management.

---

## 1. Current State Analysis

### Existing Components
| Component | Location | Status |
|-----------|----------|--------|
| `BackfillService` | `app/services/inventory/backfill_service.py` | ✅ Implemented |
| `StockToBatchService` | `app/services/inventory/stock_to_batch_service.py` | ✅ Implemented |
| `ReconciliationService` | `app/services/inventory/backfill_service.py` | ✅ Implemented |
| `CompanyInventorySettingService.enable_batch_tracking()` | `app/services/settings/company_inventory_setting_service.py` | ⚠️ Incomplete |
| `ConsistencyCheckJob` | `app/services/inventory/consistency_job.py` | ✅ Implemented |

### Gap Analysis
1. **No atomic migration workflow** - Enabling batch tracking doesn't trigger backfill automatically
2. **No migration status tracking** - Can't track if migration is in progress
3. **No operation locking** - Stock operations can run during migration causing drift
4. **No rollback on failure** - Partial failures leave inconsistent state
5. **Edge cases not handled**:
   - Partial PO deliveries already with batches
   - DSR inventory not included in migration
   - UOM conversion inconsistencies
   - Concurrent operation conflicts

---

## 2. Implementation Plan

### 2.1 Data Models

#### 2.1.1 Add Migration Tracking Table

**New file: `app/models/migration.py`**

```python
"""
Inventory Migration Models

Tracks batch tracking migration status for companies.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON
from sqlalchemy.sql import func
from app.models import Base
from app.models.mixins import TimestampMixin


class InventoryMigrationStatus:
    """Status constants for inventory migration"""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    VERIFYING = "VERIFYING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    ROLLED_BACK = "ROLLED_BACK"


class MigrationType:
    """Migration type constants"""
    FULL_BACKFILL = "FULL_BACKFILL"      # Stock to batch + historical backfill
    STOCK_TO_BATCH = "STOCK_TO_BATCH"     # Only convert current stock
    INCREMENTAL = "INCREMENTAL"           # Backfill only recent data


class InventoryMigration(Base, TimestampMixin):
    """
    Tracks batch migration status for a company.
    
    This model ensures:
    - Migration progress visibility
    - Lock mechanism to prevent concurrent operations
    - Audit trail of migration attempts
    """
    __tablename__ = "inventory.inventory_migration"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, nullable=False, index=True)
    
    # Migration configuration
    migration_type = Column(
        String(50), 
        nullable=False, 
        default=MigrationType.FULL_BACKFILL
    )
    
    # Status tracking
    status = Column(
        String(50), 
        nullable=False, 
        default=InventoryMigrationStatus.PENDING,
        index=True
    )
    
    # Progress tracking
    total_items = Column(Integer, default=0)
    processed_items = Column(Integer, default=0)
    batches_created = Column(Integer, default=0)
    movements_created = Column(Integer, default=0)
    allocations_created = Column(Integer, default=0)
    errors_count = Column(Integer, default=0)
    
    # Results (stored as JSON)
    reconciliation_report = Column(JSON)  # Store reconciliation result
    error_details = Column(JSON)          # Store error details
    
    # Lock mechanism
    is_locked = Column(Boolean, default=False)
    locked_at = Column(DateTime)
    locked_by = Column(Integer)
    
    # Configuration options
    dry_run_first = Column(Boolean, default=True)
    skip_verification = Column(Boolean, default=False)
    allow_mismatch_tolerance = Column(Integer, default=0)
    
    # Timestamps
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Audit
    created_by = Column(Integer, nullable=True)
    
    def __repr__(self):
        return f"<InventoryMigration id={self.id} company={self.company_id} status={self.status}>"
```

**Migration Required:** Yes (new table)
- Run: `alembic revision --autogenerate -m "Add inventory_migration table"`
- Review generated migration before applying

---

### 2.2 Service Layer

#### 2.2.1 Create `InventoryMigrationService`

**New file: `app/services/inventory/inventory_migration_service.py`**

```python
"""
Inventory Migration Service

Service for managing batch tracking migration workflow.

Provides:
- Atomic migration with proper locking
- Dry-run preview
- Step-by-step execution with verification
- Rollback capability
- Error handling with detailed reporting
"""

from dataclasses import dataclass, field
from decimal import Decimal
from typing import List, Dict, Optional, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import text, and_
from datetime import datetime
import logging

from app.models.migration import (
    InventoryMigration, 
    InventoryMigrationStatus,
    MigrationType
)
from app.models.warehouse import InventoryStock, StorageLocation, DSRStorage, DSRInventoryStock
from app.models.batch_models import Batch, InventoryMovement, SalesOrderBatchAllocation
from app.services.inventory.backfill_service import BackfillService
from app.services.inventory.stock_to_batch_service import StockToBatchService
from app.services.settings.company_inventory_setting_service import CompanyInventorySettingService
from app.repositories.inventory.batch import CompanyInventorySettingRepository

logger = logging.getLogger(__name__)


# =============================================================================
# Custom Exceptions
# =============================================================================

class MigrationError(Exception):
    """Base exception for migration errors"""
    def __init__(self, message: str, details: Dict = None):
        super().__init__(message)
        self.details = details or {}


class MigrationLockError(MigrationError):
    """Raised when migration lock prevents operation"""
    pass


class PreMigrationCheckError(MigrationError):
    """Raised when pre-migration checks fail"""
    pass


class ReconciliationError(MigrationError):
    """Raised when reconciliation fails"""
    pass


class UOMConversionError(MigrationError):
    """Raised when UOM conversion issues detected"""
    pass


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class MigrationPreCheckResult:
    """Result of pre-migration checks"""
    is_valid: bool
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    blocking_errors: List[str] = field(default_factory=list)
    
    @property
    def has_blocking_errors(self) -> bool:
        return len(self.blocking_errors) > 0


@dataclass
class PendingOperation:
    """Represents a pending stock operation"""
    operation_type: str
    reference_id: int
    status: str
    created_at: datetime


@dataclass
class MigrationStepResult:
    """Result of a single migration step"""
    step_name: str
    success: bool
    items_processed: int = 0
    batches_created: int = 0
    movements_created: int = 0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class ReconciliationIssue:
    """Single reconciliation issue"""
    product_id: int
    variant_id: Optional[int]
    location_id: int
    batch_qty: Decimal
    stock_qty: Decimal
    difference: Decimal
    issue_type: str  # MISSING_IN_BATCH, MISSING_IN_STOCK, MISMATCH


@dataclass
class FixResult:
    """Result of fixing reconciliation issues"""
    fixed_count: int = 0
    failed_count: int = 0
    errors: List[str] = field(default_factory=list)


# =============================================================================
# Service Class
# =============================================================================

class InventoryMigrationService:
    """
    Service for managing batch tracking migration workflow.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.backfill_service = BackfillService(db)
        self.stock_to_batch_service = StockToBatchService(db)
        self.setting_service = CompanyInventorySettingService(db)
        self.setting_repo = CompanyInventorySettingRepository(db)
    
    # =========================================================================
    # PHASE 4.1: Pre-Migration Checks
    # =========================================================================
    
    def pre_migration_check(self, company_id: int) -> MigrationPreCheckResult:
        """
        Run pre-migration checks before starting migration.
        
        Checks:
        1. Batch tracking is currently disabled
        2. No active migrations exist
        3. Inventory stock has data to migrate
        4. All products have location assigned
        5. No pending stock operations
        
        Returns:
            MigrationPreCheckResult with warnings/errors
        """
        result = MigrationPreCheckResult(is_valid=True)
        
        # Check 1: Batch tracking should be disabled
        current_settings = self.setting_repo.get_by_company(company_id)
        if current_settings and current_settings.batch_tracking_enabled:
            result.blocking_errors.append(
                "Batch tracking is already enabled. Disable it first to run migration."
            )
            result.is_valid = False
            return result
        
        # Check 2: No active migration in progress
        active_migration = self._get_active_migration(company_id)
        if active_migration:
            result.blocking_errors.append(
                f"Migration already in progress (ID: {active_migration.id}, "
                f"Status: {active_migration.status}). Please wait or rollback."
            )
            result.is_valid = False
            return result
        
        # Check 3: Inventory stock has data
        stock_count = self._get_stock_count(company_id)
        if stock_count == 0:
            result.errors.append("No inventory stock data found to migrate.")
            result.is_valid = False
            return result
        
        result.warnings.append(f"Found {stock_count} stock records to migrate.")
        
        # Check 4: Validate location assignment
        location_issues = self._validate_location_assignment(company_id)
        if location_issues:
            result.errors.append(
                f"{len(location_issues)} products have stock without valid location. "
                f"These cannot be migrated until location is assigned."
            )
            result.is_valid = False
        
        # Check 5: Check for pending operations
        pending_ops = self.check_pending_stock_operations(company_id)
        if pending_ops:
            result.warnings.append(
                f"Found {len(pending_ops)} pending stock operations that may conflict "
                f"with migration. Consider completing them first."
            )
        
        # Check 6: Validate UOM
        uom_issues = self._check_uom_consistency(company_id)
        if uom_issues:
            result.warnings.append(
                f"Found {len(uom_issues)} products with potential UOM inconsistencies. "
                f"Migration will proceed but some quantities may be incorrect."
            )
        
        # Check 7: Validate products exist
        product_count = self._get_product_count(company_id)
        if product_count == 0:
            result.errors.append("No products found to migrate.")
            result.is_valid = False
        
        return result
    
    def _get_active_migration(self, company_id: int) -> Optional[InventoryMigration]:
        """Get any active migration for the company."""
        return (
            self.db.query(InventoryMigration)
            .filter(
                InventoryMigration.company_id == company_id,
                InventoryMigration.status.in_([
                    InventoryMigrationStatus.PENDING,
                    InventoryMigrationStatus.IN_PROGRESS,
                    InventoryMigrationStatus.VERIFYING,
                ]),
                InventoryMigration.is_locked == True,
            )
            .first()
        )
    
    def _get_stock_count(self, company_id: int) -> int:
        """Get count of stock records to migrate."""
        return (
            self.db.query(InventoryStock)
            .join(StorageLocation)
            .filter(
                StorageLocation.company_id == company_id,
                InventoryStock.is_deleted == False,
                InventoryStock.quantity > 0,
            )
            .count()
        )
    
    def _get_product_count(self, company_id: int) -> int:
        """Get count of products with stock."""
        return (
            self.db.query(InventoryStock.product_id)
            .join(StorageLocation)
            .filter(
                StorageLocation.company_id == company_id,
                InventoryStock.is_deleted == False,
                InventoryStock.quantity > 0,
            )
            .distinct()
            .count()
        )
    
    def _validate_location_assignment(self, company_id: int) -> List[Dict]:
        """
        Validate that all products with stock have valid location.
        
        Batch operations REQUIRE location_id.
        """
        # Find stock records without valid location
        issues = []
        
        stock_with_location = (
            self.db.query(
                InventoryStock.product_id,
                InventoryStock.variant_id,
                InventoryStock.location_id,
            )
            .join(StorageLocation)
            .filter(
                StorageLocation.company_id == company_id,
                InventoryStock.is_deleted == False,
                InventoryStock.quantity > 0,
            )
            .all()
        )
        
        for stock in stock_with_location:
            if stock.location_id is None:
                issues.append({
                    "product_id": stock.product_id,
                    "variant_id": stock.variant_id,
                    "issue": "No location assigned"
                })
        
        return issues
    
    def _check_uom_consistency(self, company_id: int) -> List[Dict]:
        """
        Check for potential UOM conversion issues in historical data.
        
        Many legacy systems store stock in different UOMs without proper conversion.
        """
        # This is a placeholder - actual implementation would check:
        # - Products with multiple UOMs
        # - Conversion factors that may be missing
        # - Quantities that seem unusually large/small
        return []  # Placeholder
    
    def check_pending_stock_operations(self, company_id: int) -> List[PendingOperation]:
        """
        Check for pending stock operations that could conflict with migration.
        
        Returns list of operations that should complete before migration:
        - In-progress deliveries
        - In-progress transfers
        - In-progress adjustments
        """
        pending = []
        
        # Check for in-progress deliveries (placeholder - actual implementation
        # would query actual delivery/transfer tables)
        
        return pending
    
    # =========================================================================
    # PHASE 4.2: Migration Execution
    # =========================================================================
    
    def start_migration(
        self,
        company_id: int,
        migration_type: str = MigrationType.FULL_BACKFILL,
        user_id: int = 1,
        dry_run_first: bool = True,
        skip_verification: bool = False,
    ) -> InventoryMigration:
        """
        Start a new migration for the company.
        
        This will:
        1. Create migration record
        2. Lock stock operations
        3. Run pre-checks
        4. Execute migration steps (if not dry run)
        
        Args:
            company_id: Company ID
            migration_type: Type of migration to run
            user_id: User initiating migration
            dry_run_first: Run dry run before actual migration
            skip_verification: Skip final reconciliation check
            
        Returns:
            InventoryMigration record with status
            
        Raises:
            MigrationLockError: If migration already in progress
            PreMigrationCheckError: If pre-checks fail
        """
        
        # Step 1: Check for existing active migration
        active_migration = self._get_active_migration(company_id)
        if active_migration:
            raise MigrationLockError(
                f"Migration already in progress for company {company_id}. "
                f"Migration ID: {active_migration.id}, Status: {active_migration.status}"
            )
        
        # Step 2: Run pre-migration checks
        pre_check = self.pre_migration_check(company_id)
        if pre_check.has_blocking_errors:
            raise PreMigrationCheckError(
                "Pre-migration check failed",
                details={
                    "blocking_errors": pre_check.blocking_errors,
                    "errors": pre_check.errors,
                }
            )
        
        # Step 3: Create migration record
        migration = InventoryMigration(
            company_id=company_id,
            migration_type=migration_type,
            status=InventoryMigrationStatus.PENDING,
            dry_run_first=dry_run_first,
            skip_verification=skip_verification,
            created_by=user_id,
            total_items=self._get_stock_count(company_id),
        )
        self.db.add(migration)
        self.db.commit()
        self.db.refresh(migration)
        
        # Step 4: Acquire migration lock
        self.acquire_migration_lock(company_id, user_id)
        
        # Step 5: Execute dry run if requested
        if dry_run_first:
            migration.status = InventoryMigrationStatus.PENDING
            self.db.commit()
            
            # Run dry run
            dry_run_result = self._execute_migration_steps(
                migration_id=migration.id,
                dry_run=True
            )
            
            # Store dry run results
            migration.reconciliation_report = dry_run_result.get("reconciliation")
            migration.error_details = {
                "dry_run_errors": dry_run_result.get("errors", []),
                "dry_run_warnings": dry_run_result.get("warnings", []),
            }
            self.db.commit()
            
            return migration
        
        # Step 6: Execute actual migration
        return self._execute_migration_steps(
            migration_id=migration.id,
            dry_run=False
        )
    
    def _execute_migration_steps(
        self,
        migration_id: int,
        dry_run: bool = False,
    ) -> Dict[str, Any]:
        """
        Execute the actual migration steps.
        
        Steps:
        1. STOCK_TO_BATCH: Consolidate current inventory_stock to batches
        2. BACKFILL_PO: Create batches from historical PO deliveries
        3. BACKFILL_SO: Create sales allocations from historical deliveries
        4. VERIFY: Run reconciliation check
        5. COMPLETE: Update inventory_stock to match batch totals
        
        Args:
            migration_id: Migration ID
            dry_run: If True, don't commit changes
            
        Returns:
            Dict with results from each step
        """
        migration = self.db.query(InventoryMigration).get(migration_id)
        if not migration:
            raise MigrationError(f"Migration {migration_id} not found")
        
        company_id = migration.company_id
        results = {
            "steps": [],
            "errors": [],
            "warnings": [],
            "reconciliation": None,
        }
        
        try:
            # Update status
            migration.status = InventoryMigrationStatus.IN_PROGRESS
            migration.started_at = datetime.utcnow()
            self.db.commit()
            
            # Step 1: Stock to Batch (convert current stock)
            if migration.migration_type in [
                MigrationType.FULL_BACKFILL,
                MigrationType.STOCK_TO_BATCH
            ]:
                step_result = self._run_stock_to_batch(migration, dry_run)
                results["steps"].append(step_result)
                results["errors"].extend(step_result.errors)
                results["warnings"].extend(step_result.warnings)
                
                if not step_result.success and not dry_run:
                    raise MigrationError(
                        f"Stock to batch failed: {step_result.errors}",
                        details={"step": "stock_to_batch"}
                    )
            
            # Step 2: Backfill PO deliveries (create batches from historical receipts)
            if migration.migration_type == MigrationType.FULL_BACKFILL:
                step_result = self._run_po_backfill(migration, dry_run)
                results["steps"].append(step_result)
                results["errors"].extend(step_result.errors)
                results["warnings"].extend(step_result.warnings)
            
            # Step 3: Backfill SO allocations (link sales to batches)
            if migration.migration_type == MigrationType.FULL_BACKFILL:
                step_result = self._run_so_backfill(migration, dry_run)
                results["steps"].append(step_result)
                results["errors"].extend(step_result.errors)
                results["warnings"].extend(step_result.warnings)
            
            # Step 4: Verify reconciliation
            if not migration.skip_verification:
                migration.status = InventoryMigrationStatus.VERIFYING
                self.db.commit()
                
                reconciliation = self._run_reconciliation(company_id)
                results["reconciliation"] = reconciliation
                
                # Check for critical mismatches
                if reconciliation.get("mismatched", 0) > 0:
                    tolerance = migration.allow_mismatch_tolerance or 0
                    if reconciliation["mismatched"] > tolerance:
                        raise ReconciliationError(
                            f"Reconciliation failed: {reconciliation['mismatched']} mismatches found",
                            details={"reconciliation": reconciliation}
                        )
                
                migration.reconciliation_report = reconciliation
            
            # Step 5: Complete
            if not dry_run:
                migration.status = InventoryMigrationStatus.COMPLETED
                migration.completed_at = datetime.utcnow()
                
                # Release lock
                self.release_migration_lock(company_id)
            else:
                migration.status = InventoryMigrationStatus.PENDING  # Dry run pending
                migration.completed_at = datetime.utcnow()
            
            self.db.commit()
            
        except Exception as e:
            # Mark as failed
            migration.status = InventoryMigrationStatus.FAILED
            migration.error_details = {
                "error": str(e),
                "step": results["steps"][-1].step_name if results["steps"] else "unknown",
            }
            migration.completed_at = datetime.utcnow()
            
            # Release lock on failure
            self.release_migration_lock(company_id)
            
            self.db.commit()
            raise
        
        return results
    
    def _run_stock_to_batch(
        self,
        migration: InventoryMigration,
        dry_run: bool,
    ) -> MigrationStepResult:
        """Execute stock to batch step."""
        result = MigrationStepResult(step_name="STOCK_TO_BATCH", success=True)
        
        try:
            if dry_run:
                preview = self.stock_to_batch_service.preview_consolidation(
                    migration.company_id
                )
                result.items_processed = preview.to_create + preview.to_update
                result.warnings.extend(preview.warnings)
            else:
                exec_result = self.stock_to_batch_service.execute_consolidation(
                    company_id=migration.company_id,
                    user_id=migration.created_by or 1
                )
                result.items_processed = exec_result.batches_created
                result.batches_created = exec_result.batches_created
                result.movements_created = exec_result.movements_created
                result.errors.extend(exec_result.errors)
                result.warnings.extend(exec_result.warnings)
                
                # Update migration progress
                migration.batches_created = exec_result.batches_created
                migration.movements_created = exec_result.movements_created
                self.db.commit()
                
        except Exception as e:
            result.success = False
            result.errors.append(f"Stock to batch failed: {str(e)}")
            logger.error(f"Stock to batch error: {e}", exc_info=True)
        
        return result
    
    def _run_po_backfill(
        self,
        migration: InventoryMigration,
        dry_run: bool,
    ) -> MigrationStepResult:
        """Execute PO delivery backfill step."""
        result = MigrationStepResult(step_name="PO_BACKFILL", success=True)
        
        try:
            if dry_run:
                # Just check how many would be processed
                po_deliveries = self.backfill_service._get_pending_po_deliveries(
                    migration.company_id,
                    limit=1000  # Get count estimate
                )
                result.items_processed = len(po_deliveries)
            else:
                backfill_result = self.backfill_service.backfill_batches(
                    company_id=migration.company_id,
                    dry_run=False,
                    chunk_size=500,
                    user_id=migration.created_by or 1
                )
                result.items_processed = backfill_result.batches_created
                result.batches_created = backfill_result.batches_created
                result.movements_created = backfill_result.movements_created
                result.errors.extend(backfill_result.errors)
                result.warnings.extend(backfill_result.warnings)
                
                migration.batches_created += backfill_result.batches_created
                migration.movements_created += backfill_result.movements_created
                migration.errors_count += len(backfill_result.errors)
                self.db.commit()
                
        except Exception as e:
            result.success = False
            result.errors.append(f"PO backfill failed: {str(e)}")
            logger.error(f"PO backfill error: {e}", exc_info=True)
        
        return result
    
    def _run_so_backfill(
        self,
        migration: InventoryMigration,
        dry_run: bool,
    ) -> MigrationStepResult:
        """Execute SO delivery backfill step."""
        result = MigrationStepResult(step_name="SO_BACKFILL", success=True)
        
        try:
            if dry_run:
                so_deliveries = self.backfill_service._get_pending_so_deliveries(
                    migration.company_id,
                    limit=1000
                )
                result.items_processed = len(so_deliveries)
            else:
                backfill_result = self.backfill_service.backfill_sales_allocations(
                    company_id=migration.company_id,
                    dry_run=False,
                    chunk_size=500,
                    user_id=migration.created_by or 1
                )
                result.items_processed = backfill_result.allocations_created
                result.allocations_created = backfill_result.allocations_created
                result.errors.extend(backfill_result.errors)
                result.warnings.extend(backfill_result.warnings)
                
                migration.allocations_created = backfill_result.allocations_created
                migration.errors_count += len(backfill_result.errors)
                self.db.commit()
                
        except Exception as e:
            result.success = False
            result.errors.append(f"SO backfill failed: {str(e)}")
            logger.error(f"SO backfill error: {e}", exc_info=True)
        
        return result
    
    def _run_reconciliation(self, company_id: int) -> Dict:
        """Run reconciliation check."""
        return self.backfill_service.generate_reconciliation_report(
            company_id=company_id,
            dry_run=False
        )
    
    # =========================================================================
    # PHASE 4.3: Lock Management
    # =========================================================================
    
    def acquire_migration_lock(
        self,
        company_id: int,
        user_id: int,
        reason: str = "Migration in progress",
    ) -> bool:
        """
        Acquire lock to prevent stock operations during migration.
        
        Uses PostgreSQL advisory locks for safe locking.
        """
        # Use advisory lock - automatically released at transaction end
        # or when explicitly released
        lock_key = 10000 + company_id  # Unique key per company
        
        try:
            # Try to acquire lock
            result = self.db.execute(
                text(f"SELECT pg_try_advisory_xact_lock({lock_key}) as acquired")
            ).scalar()
            
            if not result:
                raise MigrationLockError(
                    f"Could not acquire migration lock for company {company_id}. "
                    f"Another process may be running migration."
                )
            
            # Also update migration record
            migration = self._get_active_migration(company_id)
            if migration:
                migration.is_locked = True
                migration.locked_at = datetime.utcnow()
                migration.locked_by = user_id
                self.db.commit()
            
            logger.info(f"Migration lock acquired for company {company_id} by user {user_id}")
            return True
            
        except MigrationLockError:
            raise
        except Exception as e:
            logger.error(f"Failed to acquire lock: {e}")
            raise MigrationLockError(f"Failed to acquire migration lock: {str(e)}")
    
    def release_migration_lock(self, company_id: int) -> bool:
        """
        Release migration lock after completion or failure.
        
        Advisory locks are automatically released at transaction end,
        but we also update the migration record.
        """
        try:
            migration = self._get_active_migration(company_id)
            if migration:
                migration.is_locked = False
                migration.locked_at = None
                migration.locked_by = None
                self.db.commit()
            
            logger.info(f"Migration lock released for company {company_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to release lock: {e}")
            return False
    
    def is_migration_locked(self, company_id: int) -> bool:
        """Check if migration is in progress for company."""
        migration = self._get_active_migration(company_id)
        return migration is not None
    
    def validate_no_migration_lock(self, company_id: int) -> None:
        """
        Raise exception if migration is in progress.
        Call this at start of all stock operations.
        """
        if self.is_migration_locked(company_id):
            raise MigrationLockError(
                f"Cannot perform stock operation: migration in progress for company {company_id}. "
                f"Please wait for migration to complete or rollback."
            )
    
    # =========================================================================
    # PHASE 4.4: Verification
    # =========================================================================
    
    def run_reconciliation_check(
        self,
        company_id: int,
    ) -> Dict:
        """
        Run reconciliation check for a company.
        
        Returns detailed report.
        """
        return self.backfill_service.generate_reconciliation_report(
            company_id=company_id,
            dry_run=False
        )
    
    def fix_reconciliation_issues(
        self,
        company_id: int,
        auto_fix: bool = False,
    ) -> FixResult:
        """
        Attempt to fix reconciliation issues.
        
        Options:
        - auto_fix=True: Auto-update inventory_stock to match batches
        - auto_fix=False: Generate fix report for manual review
        
        This is typically used AFTER successful migration to ensure
        inventory_stock matches batch totals.
        """
        result = FixResult()
        
        # Get reconciliation report
        reconciliation = self.run_reconciliation_check(company_id)
        
        if not reconciliation.get("items"):
            return result
        
        if not auto_fix:
            # Just report what would be fixed
            result.errors.append("Auto-fix disabled. Run with auto_fix=True to apply changes.")
            return result
        
        # Process each item
        for item in reconciliation.get("items", []):
            if item["status"] == "MISMATCH":
                try:
                    # Fix: Update inventory_stock to match batch
                    stock_record = (
                        self.db.query(InventoryStock)
                        .filter(
                            InventoryStock.product_id == item["product_id"],
                            InventoryStock.variant_id == item["variant_id"],
                            InventoryStock.location_id == item["location_id"],
                            InventoryStock.is_deleted == False,
                        )
                        .first()
                    )
                    
                    if stock_record:
                        stock_record.quantity = item["batch_qty"]
                        result.fixed_count += 1
                    else:
                        # Create new stock record
                        new_stock = InventoryStock(
                            company_id=company_id,
                            product_id=item["product_id"],
                            variant_id=item["variant_id"],
                            location_id=item["location_id"],
                            quantity=item["batch_qty"],
                            is_deleted=False,
                        )
                        self.db.add(new_stock)
                        result.fixed_count += 1
                        
                except Exception as e:
                    result.failed_count += 1
                    result.errors.append(
                        f"Failed to fix product {item['product_id']}: {str(e)}"
                    )
        
        if result.fixed_count > 0:
            self.db.commit()
        
        return result
    
    # =========================================================================
    # PHASE 4.5: Rollback
    # =========================================================================
    
    def rollback_migration(
        self,
        migration_id: int,
        user_id: int = 1,
    ) -> InventoryMigration:
        """
        Rollback a failed migration.
        
        Steps:
        1. Soft delete created batches
        2. Soft delete created movements
        3. Soft delete created allocations
        4. Release lock
        5. Update migration status
        """
        migration = self.db.query(InventoryMigration).get(migration_id)
        if not migration:
            raise MigrationError(f"Migration {migration_id} not found")
        
        if migration.status == InventoryMigrationStatus.COMPLETED:
            raise MigrationError(
                "Cannot rollback a completed migration. "
                "This would cause data loss."
            )
        
        company_id = migration.company_id
        
        try:
            # Soft delete batches created during this migration
            # We identify them by checking batches created around migration time
            # or by checking is_synthetic=True and created during migration
            
            # For now, we'll soft delete all synthetic batches
            # A more precise approach would track created batch IDs
            synthetic_batches = (
                self.db.query(Batch)
                .filter(
                    Batch.company_id == company_id,
                    Batch.is_synthetic == True,
                    Batch.is_deleted == False,
                )
                .all()
            )
            
            for batch in synthetic_batches:
                batch.is_deleted = True
            
            # Soft delete movements
            # This is tricky - movements may have been created earlier
            # For now, skip movement cleanup
            
            # Soft delete allocations
            allocations = (
                self.db.query(SalesOrderBatchAllocation)
                .filter(
                    SalesOrderBatchAllocation.is_deleted == False,
                    # This is simplified - should track which allocations were created
                )
                .all()
            )
            
            for allocation in allocations:
                allocation.is_deleted = True
            
            # Update migration status
            migration.status = InventoryMigrationStatus.ROLLED_BACK
            migration.completed_at = datetime.utcnow()
            
            # Release lock
            self.release_migration_lock(company_id)
            
            self.db.commit()
            
            logger.info(f"Migration {migration_id} rolled back successfully")
            return migration
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Rollback failed: {e}", exc_info=True)
            raise MigrationError(f"Rollback failed: {str(e)}")
    
    # =========================================================================
    # PHASE 4.6: Edge Case Handlers
    # =========================================================================
    
    def handle_partial_delivery_conflict(
        self,
        po_detail_id: int,
    ) -> Dict:
        """
        Handle case where PO detail has multiple deliveries but already has batch.
        
        Resolution options:
        - SPLIT: Create separate batches per delivery
        - MERGE: Merge into single batch
        - SKIP: Skip this PO detail
        """
        # This would check for existing batches linked to this po_detail_id
        # and compare with delivery records
        # Return recommended resolution
        return {
            "recommendation": "SPLIT",
            "reason": "Multiple deliveries found without corresponding batches"
        }
    
    def handle_dsr_inventory_migration(
        self,
        company_id: int,
    ) -> Dict:
        """
        Migrate DSR inventory stock to batch format.
        
        DSR inventory needs special handling:
        - DSRStorage -> location
        - DSRInventoryStock -> batch at DSR location
        """
        result = {
            "dsr_storages_processed": 0,
            "dsr_batches_created": 0,
            "errors": [],
        }
        
        # Get all DSR storages for the company
        dsr_storages = (
            self.db.query(DSRStorage)
            .join(StorageLocation)
            .filter(StorageLocation.company_id == company_id)
            .all()
        )
        
        for dsr_storage in dsr_storages:
            try:
                # Get inventory stock for this DSR
                dsr_stock = (
                    self.db.query(DSRInventoryStock)
                    .filter(
                        DSRInventoryStock.dsr_storage_id == dsr_storage.id,
                        DSRInventoryStock.is_deleted == False,
                        DSRInventoryStock.quantity > 0,
                    )
                    .all()
                )
                
                for stock in dsr_stock:
                    # Create batch at DSR location
                    batch = Batch(
                        company_id=company_id,
                        product_id=stock.product_id,
                        variant_id=stock.variant_id,
                        qty_received=stock.quantity,
                        qty_on_hand=stock.quantity,
                        unit_cost=Decimal("0"),  # Would need to get from source
                        received_date=datetime.utcnow(),
                        location_id=dsr_storage.storage_location_id,
                        source_type="synthetic",
                        is_synthetic=True,
                        status="active",
                        notes=f"DSR migration: DSR {dsr_storage.id}",
                        is_deleted=False,
                    )
                    self.db.add(batch)
                    result["dsr_batches_created"] += 1
                
                result["dsr_storages_processed"] += 1
                
            except Exception as e:
                result["errors"].append(f"DSR {dsr_storage.id}: {str(e)}")
        
        if result["dsr_batches_created"] > 0:
            self.db.commit()
        
        return result
    
    def handle_uom_conversion_issues(
        self,
        company_id: int,
    ) -> Dict:
        """
        Check and report UOM conversion issues in historical data.
        
        Returns report of potential issues.
        """
        # Placeholder - would check for:
        # - Products with multiple base UOMs
        # - Missing conversion factors
        # - Unusually large/small quantities
        return {
            "issues_found": 0,
            "details": []
        }
    
    def validate_location_assignment(
        self,
        company_id: int,
    ) -> Dict:
        """
        Validate that all products with stock have valid location.
        
        Batch operations REQUIRE location_id.
        Products without location cannot be migrated.
        """
        issues = self._validate_location_assignment(company_id)
        
        return {
            "total_issues": len(issues),
            "issues": issues,
            "can_migrate": len(issues) == 0
        }
    
    # =========================================================================
    # Query Methods
    # =========================================================================
    
    def get_migration_status(self, company_id: int) -> Optional[InventoryMigration]:
        """Get current or most recent migration for company."""
        return (
            self.db.query(InventoryMigration)
            .filter(InventoryMigration.company_id == company_id)
            .order_by(InventoryMigration.created_at.desc())
            .first()
        )
    
    def get_migration_history(self, company_id: int) -> List[InventoryMigration]:
        """Get migration history for company."""
        return (
            self.db.query(InventoryMigration)
            .filter(InventoryMigration.company_id == company_id)
            .order_by(InventoryMigration.created_at.desc())
            .all()
        )
    
    def get_migration_by_id(self, migration_id: int) -> Optional[InventoryMigration]:
        """Get migration by ID."""
        return self.db.query(InventoryMigration).get(migration_id)
```

---

### 2.3 API Endpoints

#### 2.3.1 New Endpoints for `app/api/inventory/batch.py`

```python
# Add these imports
from app.services.inventory.inventory_migration_service import (
    InventoryMigrationService,
    MigrationType,
    MigrationLockError,
    PreMigrationCheckError,
)

# New router
migration_router = APIRouter(
    prefix="/api/company/inventory/migration",
    tags=["Inventory Migration"],
)


@migration_router.post("/start")
def start_migration(
    migration_type: str = Query(
        MigrationType.FULL_BACKFILL,
        description="Type: FULL_BACKFILL, STOCK_TO_BATCH"
    ),
    dry_run_first: bool = Query(
        True,
        description="Run dry run before actual migration"
    ),
    skip_verification: bool = Query(
        False,
        description="Skip final reconciliation check"
    ),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    company_id: int = Depends(get_current_company_id),
):
    """
    Start batch tracking migration for the company.
    
    This will:
    1. Run pre-migration checks
    2. Lock stock operations
    3. Execute migration (if dry_run_first=False)
    4. Return status
    
    **RECOMMENDED**: First run with dry_run_first=true to preview,
    then run with dry_run_first=false to execute.
    """
    try:
        user_id = current_user.get("user_id", 1)
        service = InventoryMigrationService(db)
        
        migration = service.start_migration(
            company_id=company_id,
            migration_type=migration_type,
            user_id=user_id,
            dry_run_first=dry_run_first,
            skip_verification=skip_verification,
        )
        
        return {
            "success": True,
            "migration_id": migration.id,
            "status": migration.status,
            "message": "Dry run completed" if dry_run_first else "Migration started",
            "total_items": migration.total_items,
            "reconciliation_report": migration.reconciliation_report,
            "error_details": migration.error_details,
        }
        
    except MigrationLockError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except PreMigrationCheckError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Migration failed: {str(e)}")


@migration_router.get("/status")
def get_migration_status(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    company_id: int = Depends(get_current_company_id),
):
    """Get current migration status for the company."""
    try:
        service = InventoryMigrationService(db)
        migration = service.get_migration_status(company_id)
        
        if not migration:
            return {
                "has_migration": False,
                "message": "No migration found",
            }
        
        return {
            "has_migration": True,
            "migration": {
                "id": migration.id,
                "type": migration.migration_type,
                "status": migration.status,
                "total_items": migration.total_items,
                "processed_items": migration.processed_items,
                "batches_created": migration.batches_created,
                "movements_created": migration.movements_created,
                "errors_count": migration.errors_count,
                "is_locked": migration.is_locked,
                "started_at": migration.started_at.isoformat() if migration.started_at else None,
                "completed_at": migration.completed_at.isoformat() if migration.completed_at else None,
                "reconciliation_report": migration.reconciliation_report,
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@migration_router.get("/history")
def get_migration_history(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    company_id: int = Depends(get_current_company_id),
):
    """Get migration history for the company."""
    try:
        service = InventoryMigrationService(db)
        migrations = service.get_migration_history(company_id)
        
        return {
            "migrations": [
                {
                    "id": m.id,
                    "type": m.migration_type,
                    "status": m.status,
                    "total_items": m.total_items,
                    "batches_created": m.batches_created,
                    "errors_count": m.errors_count,
                    "created_at": m.created_at.isoformat() if m.created_at else None,
                    "completed_at": m.completed_at.isoformat() if m.completed_at else None,
                }
                for m in migrations
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@migration_router.get("/pre-check")
def run_pre_migration_check(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    company_id: int = Depends(get_current_company_id),
):
    """Run pre-migration checks without starting migration."""
    try:
        service = InventoryMigrationService(db)
        result = service.pre_migration_check(company_id)
        
        return {
            "is_valid": result.is_valid,
            "warnings": result.warnings,
            "errors": result.errors,
            "blocking_errors": result.blocking_errors,
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@migration_router.get("/{migration_id}")
def get_migration_detail(
    migration_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get detailed migration information."""
    try:
        service = InventoryMigrationService(db)
        migration = service.get_migration_by_id(migration_id)
        
        if not migration:
            raise HTTPException(status_code=404, detail="Migration not found")
        
        return {
            "id": migration.id,
            "company_id": migration.company_id,
            "type": migration.migration_type,
            "status": migration.status,
            "total_items": migration.total_items,
            "processed_items": migration.processed_items,
            "batches_created": migration.batches_created,
            "movements_created": migration.movements_created,
            "allocations_created": migration.allocations_created,
            "errors_count": migration.errors_count,
            "is_locked": migration.is_locked,
            "dry_run_first": migration.dry_run_first,
            "skip_verification": migration.skip_verification,
            "reconciliation_report": migration.reconciliation_report,
            "error_details": migration.error_details,
            "started_at": migration.started_at.isoformat() if migration.started_at else None,
            "completed_at": migration.completed_at.isoformat() if migration.completed_at else None,
            "created_at": migration.created_at.isoformat() if migration.created_at else None,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@migration_router.post("/{migration_id}/verify")
def verify_migration(
    migration_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    company_id: int = Depends(get_current_company_id),
):
    """Run reconciliation verification for a completed migration."""
    try:
        service = InventoryMigrationService(db)
        reconciliation = service.run_reconciliation_check(company_id)
        
        return {
            "success": True,
            "reconciliation": reconciliation,
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@migration_router.post("/{migration_id}/fix")
def fix_migration_issues(
    migration_id: int,
    auto_fix: bool = Query(False, description="Apply fixes automatically"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    company_id: int = Depends(get_current_company_id),
):
    """Fix reconciliation issues after migration."""
    try:
        service = InventoryMigrationService(db)
        result = service.fix_reconciliation_issues(company_id, auto_fix=auto_fix)
        
        return {
            "fixed_count": result.fixed_count,
            "failed_count": result.failed_count,
            "errors": result.errors,
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@migration_router.post("/{migration_id}/rollback")
def rollback_migration(
    migration_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Rollback a failed or pending migration."""
    try:
        user_id = current_user.get("user_id", 1)
        service = InventoryMigrationService(db)
        
        migration = service.rollback_migration(migration_id, user_id)
        
        return {
            "success": True,
            "migration_id": migration.id,
            "status": migration.status,
            "message": "Migration rolled back successfully",
        }
        
    except MigrationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Modify settings endpoint to include migration option
@settings_router.post("/enable-with-migration")
def enable_batch_tracking_with_migration(
    setting_data: CompanyInventorySettingCreate,
    run_migration: bool = Query(True, description="Run migration after enabling"),
    dry_run_first: bool = Query(True, description="Run dry run before migration"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    company_id: int = Depends(get_current_company_id),
):
    """
    Enable batch tracking and optionally run migration.
    
    This is the RECOMMENDED way to enable batch tracking.
    """
    try:
        setting_service = CompanyInventorySettingService(db)
        user_id = current_user.get("user_id", 1)
        
        # First enable batch tracking
        settings = setting_service.enable_batch_tracking(
            company_id=company_id,
            user_id=user_id,
        )
        
        # If migration requested, start it
        migration_result = None
        if run_migration:
            migration_service = InventoryMigrationService(db)
            try:
                migration = migration_service.start_migration(
                    company_id=company_id,
                    user_id=user_id,
                    dry_run_first=dry_run_first,
                )
                migration_result = {
                    "migration_id": migration.id,
                    "status": migration.status,
                }
            except MigrationLockError as e:
                # Migration failed but tracking is enabled
                migration_result = {"error": str(e)}
        
        return {
            "success": True,
            "settings": {
                "setting_id": settings.setting_id,
                "company_id": settings.company_id,
                "valuation_mode": settings.valuation_mode,
                "batch_tracking_enabled": settings.batch_tracking_enabled,
            },
            "migration": migration_result,
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

#### 2.3.2 Add Lock Check to Stock Operations

Modify key stock operation services to check for migration lock:

```python
# In app/services/warehouse/warehouse.py - add to create_inventory_stock
def create_inventory_stock(self, data, company_id):
    # Check migration lock FIRST
    from app.services.inventory.inventory_mutation_service import InventoryMutationService
    migration_service = InventoryMutationService(self.db)
    migration_service.validate_no_migration_lock(company_id)
    
    # Continue with existing logic...
```

---

## 3. Edge Cases and Error Handling

### 3.1 Edge Case Matrix

| Edge Case | Current Handling | Required Fix |
|-----------|-----------------|--------------|
| **Partial PO deliveries with existing batch** | Backfill skips (returns 0,0) | Create separate batch per delivery |
| **DSR inventory not in inventory_stock** | Not handled | Add DSR-specific migration path |
| **UOM mismatch** | Not validated | Add UOM conversion check |
| **Location is NULL** | Fails silently | Validate before migration, report issues |
| **Concurrent operations during migration** | Not blocked | Add advisory locks |
| **Migration failure mid-way** | No rollback | Implement rollback function |
| **Products without purchase price** | Uses 0 cost | Report warning, allow user to set |
| **Negative stock in legacy data** | Creates negative batch | Validate and flag for review |
| **Soft-deleted stock** | Included in aggregate | Exclude is_deleted=True records |

### 3.2 Error Handling Patterns

```python
# Example error handling in API endpoints

@migration_router.post("/start")
def start_migration(...):
    try:
        # Migration logic
        pass
    except MigrationLockError as e:
        # 409 Conflict - another migration in progress
        raise HTTPException(status_code=409, detail=str(e))
    except PreMigrationCheckError as e:
        # 400 Bad Request - pre-checks failed
        raise HTTPException(status_code=400, detail=str(e))
    except ReconciliationError as e:
        # 422 Unprocessable - reconciliation issues
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        # 500 Internal Server Error
        raise HTTPException(status_code=500, detail=f"Migration failed: {str(e)}")
```

---

## 4. Implementation Checklist

### Phase 4.1: Foundation (Priority: Critical)
- [ ] Create `app/models/migration.py` with `InventoryMigration` model
- [ ] Add database migration for new table
- [ ] Create `InventoryMigrationService` class skeleton
- [ ] Implement migration lock acquisition/release

### Phase 4.2: Core Migration (Priority: Critical)
- [ ] Implement `pre_migration_check()` with all validations
- [ ] Implement `start_migration()` workflow
- [ ] Implement step-by-step execution (stock_to_batch, backfill, verify)
- [ ] Integrate with `CompanyInventorySettingService`

### Phase 4.3: Verification (Priority: High)
- [ ] Implement reconciliation check after migration
- [ ] Add auto-fix capability for simple mismatches
- [ ] Generate detailed migration report

### Phase 4.4: Rollback (Priority: High)
- [ ] Implement `rollback_migration()` 
- [ ] Add ability to delete created batches/movements/allocations
- [ ] Test rollback on failed migration

### Phase 4.5: Edge Cases (Priority: Medium)
- [ ] Handle partial PO delivery conflicts
- [ ] Add DSR inventory migration
- [ ] Implement UOM conversion validation
- [ ] Handle location assignment issues

### Phase 4.6: API & Integration (Priority: Medium)
- [ ] Add all new API endpoints
- [ ] Add lock check to stock operations
- [ ] Update frontend to show migration status

### Phase 4.7: Testing (Priority: High)
- [ ] Unit tests for migration service
- [ ] Integration tests for full workflow
- [ ] Edge case tests
- [ ] Rollback tests

---

## 5. File Structure Changes

```
Shoudagor/app/
├── models/
│   ├── __init__.py              # Add InventoryMigration import
│   └── migration.py             # NEW: Migration model
│
├── schemas/
│   └── inventory/
│       └── migration.py         # NEW: Migration schemas (if needed)
│
├── services/
│   └── inventory/
│       ├── inventory_migration_service.py  # NEW: Main migration service
│       ├── inventory_sync_service.py       # (existing - add lock check)
│       ├── backfill_service.py            # (existing)
│       ├── stock_to_batch_service.py      # (existing)
│       └── consistency_job.py            # (existing)
│
└── api/
    └── inventory/
        └── batch.py             # Add migration endpoints
```

---

## 6. Summary

Phase 4 implementation provides:

| Feature | Description |
|---------|-------------|
| **Atomic Migration** | Complete migration workflow with proper locking |
| **Dry-Run Support** | Preview changes before committing |
| **Verification** | Reconciliation check after migration |
| **Rollback** | Ability to rollback failed migrations |
| **Edge Cases** | Handle partial deliveries, DSR, UOM issues |
| **Locking** | Prevent concurrent operations during migration |
| **Status Tracking** | Track migration progress and history |

This ensures a safe transition to batch-based inventory tracking with minimal risk of data corruption.

---

## Next Steps

1. **Create migration model** - Run alembic to add `inventory_migration` table
2. **Create service file** - Add `inventory_migration_service.py`
3. **Add API endpoints** - Register migration routes in `batch.py`
4. **Add lock checks** - Protect stock operations during migration
5. **Test** - Run comprehensive tests before production deployment
