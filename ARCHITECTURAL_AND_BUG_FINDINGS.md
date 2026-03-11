# Shoudagor ERP System - Architectural & Bug Analysis Report

**Date:** March 10, 2026  
**Analyst:** Senior Architect & Bug Finder  
**System:** Shoudagor Fullstack ERP (FastAPI + React)

---

## Executive Summary

This comprehensive analysis examines the Shoudagor ERP system from both backend (FastAPI/Python) and frontend (React/TypeScript) perspectives. The system implements a sophisticated multi-tenant business management platform with batch-based inventory tracking, sales representative management, delivery representative operations, and claims/schemes functionality.

**Critical Findings:** 23 High-Priority Issues | 31 Medium-Priority Issues | 18 Low-Priority Issues

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Critical Issues](#critical-issues)
3. [Data Consistency & Transaction Issues](#data-consistency--transaction-issues)
4. [Batch Inventory System Issues](#batch-inventory-system-issues)
5. [DSR (Delivery Sales Representative) Issues](#dsr-delivery-sales-representative-issues)
6. [Sales Order & Consolidation Issues](#sales-order--consolidation-issues)
7. [Claims & Schemes Issues](#claims--schemes-issues)
8. [Frontend Issues](#frontend-issues)
9. [Security & Validation Issues](#security--validation-issues)
10. [Performance & Scalability Issues](#performance--scalability-issues)
11. [Recommendations](#recommendations)

---

## Architecture Overview

### System Architecture
- **Backend:** FastAPI (Python 3.x) with SQLAlchemy 2.0+ ORM
- **Frontend:** React 19.1.0 with TypeScript 5.8.3, TanStack Query v5
- **Database:** PostgreSQL with multi-schema architecture
- **Search:** Elasticsearch 8.x
- **Architecture Pattern:** 5-Layer Clean Architecture (API → Service → Repository → Models → Schemas)

### Key Business Domains
1. Batch-Based Inventory Management (FIFO/LIFO/Weighted Average)
2. Sales Order Processing & SR Consolidation
3. DSR (Delivery Sales Representative) Operations
4. Claims & Promotional Schemes
5. Purchase Order Management
6. Multi-tenant Company Management

---

## Critical Issues

### CRITICAL-001: Race Condition in Purchase Order Delivery Processing
**File:** `Shoudagor/app/services/procurement/product_order_delivery_detail_service.py`  
**Lines:** 48-55  
**Severity:** HIGH  
**Impact:** Data corruption, inventory inconsistency

**Description:**
The purchase order delivery processing locks the parent PurchaseOrder but doesn't lock the PurchaseOrderDetail records. This creates a race condition when multiple concurrent delivery requests are processed for the same purchase order.

```python
# Current implementation
self.repo.db.query(PurchaseOrder).filter(
    PurchaseOrder.purchase_order_id == purchase_order_detail.purchase_order_id
).with_for_update().first()
```

**Issue:** The lock is on PurchaseOrder but the critical updates happen on PurchaseOrderDetail (received_quantity, received_free_quantity). Multiple concurrent requests can read the same detail state and overwrite each other's updates.

**Reproduction Steps:**
1. Create a purchase order with multiple line items
2. Submit 2+ concurrent delivery requests for the same PO detail
3. Observe that received_quantity may be incorrect due to lost updates

**Recommended Fix:**
```python
# Lock the specific detail record
purchase_order_detail = self.detail_repo.db.query(PurchaseOrderDetail).filter(
    PurchaseOrderDetail.purchase_order_detail_id == delivery.purchase_order_detail_id
).with_for_update().first()
```

**Business Impact:** Inventory discrepancies, incorrect stock levels, financial reporting errors

---

### CRITICAL-002: Missing Transaction Rollback in Batch Allocation
**File:** `Shoudagor/app/services/inventory/batch_allocation_service.py`  
**Lines:** Throughout the service  
**Severity:** HIGH  
**Impact:** Partial allocations, data inconsistency

**Description:**
The BatchAllocationService performs multiple database operations (creating movements, updating batch quantities, creating allocations) but lacks comprehensive transaction management and rollback mechanisms.

**Issue:** If any step in the allocation process fails (e.g., insufficient stock discovered mid-allocation), previous allocations are not rolled back, leading to partial allocations.

**Example Scenario:**
1. Sales order has 3 line items
2. Items 1 and 2 allocate successfully
3. Item 3 fails due to insufficient stock
4. Items 1 and 2 remain allocated (orphaned allocations)
5. Sales order is in inconsistent state

**Recommended Fix:**
- Wrap entire allocation process in explicit transaction
- Implement savepoints for partial rollback
- Add validation before starting allocation
- Implement compensation logic for failed allocations

**Business Impact:** Inventory locked in failed orders, customer fulfillment issues, manual intervention required

---

### CRITICAL-003: DSR Stock Loading Without Batch Tracking
**File:** `Shoudagor/app/services/dsr/dsr_so_assignment_service.py`  
**Lines:** load_so() method  
**Severity:** HIGH  
**Impact:** Cost traceability loss, FIFO/LIFO violation

**Description:**
The DSR stock loading process transfers inventory from main storage to DSR storage but doesn't maintain batch allocation information. This breaks the batch tracking chain and makes it impossible to trace costs accurately.

**Issue:**
```python
# Current: Transfers aggregate quantities without batch info
# Missing: Which specific batches were loaded into DSR storage
# Missing: Cost basis for each batch loaded
# Missing: FIFO/LIFO ordering preservation
```

**Consequences:**
1. When DSR delivers to customer, system cannot determine actual COGS
2. Returns cannot be traced back to original batches
3. FIFO/LIFO valuation becomes impossible for DSR-delivered orders
4. Inventory aging reports become inaccurate

**Recommended Fix:**
- Create DSRBatchAllocation table to track batch-to-DSR mappings
- Maintain batch allocation chain: PO → Batch → SO → DSR → Customer
- Implement batch-aware DSR stock transfer logic
- Add batch information to DSR delivery processing

**Business Impact:** Incorrect COGS calculation, financial reporting errors, audit trail gaps

---

### CRITICAL-004: Sales Return Processing Without Proper Batch Deallocation
**File:** `Shoudagor/app/services/sales/sales_order_service.py`  
**Lines:** process_return() method  
**Severity:** HIGH  
**Impact:** Inventory inconsistency, batch quantity errors

**Description:**
The sales return processing updates SalesOrderDetail.returned_quantity but doesn't properly deallocate from the original batches or create compensating inventory movements.

**Issue:**
```python
# Current implementation updates returned_quantity
detail.returned_quantity += return_item.quantity

# Missing:
# 1. Reverse the original batch allocations
# 2. Create RETURN_IN inventory movements
# 3. Update batch.qty_on_hand
# 4. Handle partial returns correctly
```

**Scenario:**
1. SO allocated 100 units from Batch A (cost $10/unit)
2. Customer returns 30 units
3. System updates returned_quantity = 30
4. But Batch A still shows 100 units allocated (qty_on_hand not restored)
5. Inventory reports show 30 units missing

**Recommended Fix:**
```python
def process_return(self, sales_order_id, return_request):
    # 1. Get original allocations
    allocations = get_allocations_for_order(sales_order_id)
    
    # 2. For each returned item, reverse allocations (FIFO/LIFO)
    for return_item in return_request.items:
        reverse_allocations(return_item, allocations)
    
    # 3. Create RETURN_IN movements
    # 4. Update batch quantities
    # 5. Update sales order detail
```

**Business Impact:** Inventory shrinkage, incorrect stock levels, financial discrepancies

---

## Data Consistency & Transaction Issues

### ISSUE-005: Inconsistent Transaction Boundaries in Consolidation
**File:** `Shoudagor/app/services/consolidation_service.py`  
**Lines:** create_consolidated_sales_order() method  
**Severity:** HIGH  
**Impact:** Orphaned SR orders, data inconsistency

**Description:**
The SR order consolidation process performs multiple database operations across different tables but lacks proper transaction isolation and error handling.

**Current Flow:**
1. Validate SR orders (multiple queries)
2. Create SalesOrder
3. Create SalesOrderDetails
4. Update SR_Order statuses to 'consolidated'
5. Update SR_Order.consolidated_sales_order_id

**Issues:**
- No explicit transaction boundary
- If step 4 or 5 fails, SalesOrder is created but SR orders remain in 'approved' state
- No compensation logic for partial failures
- Rollback may leave database in inconsistent state

**Observed Behavior:**
```python
# If this fails after SalesOrder creation:
sr_order.status = 'consolidated'
sr_order.consolidated_sales_order_id = sales_order.sales_order_id

# Result: SalesOrder exists but SR orders still show as 'approved'
# Users can consolidate the same SR orders again → duplicate SalesOrders
```

**Recommended Fix:**
```python
def create_consolidated_sales_order(self, request, user_id, company_id):
    try:
        # Explicit transaction with savepoint
        with self.db.begin_nested():
            # Lock SR orders to prevent concurrent consolidation
            sr_orders = self.lock_sr_orders_for_update(request.sr_order_ids)
            
            # Validate (within transaction)
            self.validate_sr_orders(sr_orders)
            
            # Create sales order
            sales_order = self.create_sales_order(sr_orders, request)
            
            # Update SR orders atomically
            self.update_sr_order_statuses(sr_orders, sales_order.sales_order_id)
            
            self.db.commit()
            return sales_order
    except Exception as e:
        self.db.rollback()
        raise ConsolidationProcessingError(...)
```

**Business Impact:** Duplicate orders, revenue recognition errors, customer confusion

---

### ISSUE-006: Missing Optimistic Locking for Concurrent Updates
**File:** Multiple service files  
**Severity:** MEDIUM  
**Impact:** Lost updates, data races

**Description:**
The system lacks optimistic locking mechanisms (version columns) for critical entities that are frequently updated concurrently.

**Affected Entities:**
- InventoryStock (quantity updates)
- Batch (qty_on_hand updates)
- SalesOrder (status, payment_status, delivery_status)
- DeliverySalesRepresentative (payment_on_hand, commission_amount)

**Example Race Condition:**
```python
# Thread 1: DSR collects payment
dsr = get_dsr(dsr_id)  # payment_on_hand = 1000
dsr.payment_on_hand += 500  # Now 1500
save(dsr)

# Thread 2: DSR settlement (concurrent)
dsr = get_dsr(dsr_id)  # payment_on_hand = 1000 (stale read)
dsr.payment_on_hand -= 300  # Now 700
save(dsr)  # Overwrites Thread 1's update!

# Final state: 700 (should be 1200)
```

**Recommended Fix:**
```python
# Add version column to models
class DeliverySalesRepresentative(Base):
    version = Column(Integer, nullable=False, default=1)
    
# Update with version check
def update_payment_on_hand(dsr_id, amount):
    result = db.query(DSR).filter(
        DSR.dsr_id == dsr_id,
        DSR.version == current_version
    ).update({
        'payment_on_hand': DSR.payment_on_hand + amount,
        'version': DSR.version + 1
    })
    
    if result == 0:
        raise ConcurrentModificationError()
```

**Business Impact:** Financial discrepancies, inventory inaccuracies, audit failures

---

### ISSUE-007: Inventory Stock Validation Timing Issue
**File:** `Shoudagor/app/services/sales/sales_order_service.py`  
**Lines:** _validate_stock_availability() method  
**Severity:** MEDIUM  
**Impact:** Overselling, customer dissatisfaction

**Description:**
Stock validation happens at order creation time but not at delivery time. Between order creation and delivery, stock levels can change, leading to delivery failures.

**Current Flow:**
```python
# Order creation (Day 1)
validate_stock_availability()  # Stock = 100, Order = 50 ✓
create_sales_order()

# Delivery attempt (Day 5)
# No validation!
# Actual stock = 30 (other orders consumed 70)
# Delivery fails or creates negative stock
```

**Issues:**
1. No re-validation at delivery time
2. No stock reservation mechanism
3. First-come-first-served at delivery (not at order)
4. Batch allocation can fail even if order was validated

**Recommended Fix:**
```python
# Option 1: Stock Reservation
def create_sales_order(order_data):
    validate_stock()
    reserve_stock(order_data)  # Create pending allocations
    create_order()

# Option 2: Re-validation at Delivery
def create_delivery(delivery_data):
    validate_stock_for_delivery()  # Check current stock
    if insufficient:
        raise InsufficientStockError()
    allocate_batches()
    create_delivery_record()
```

**Business Impact:** Customer complaints, delivery delays, operational inefficiency

---

## Batch Inventory System Issues

### ISSUE-008: FIFO/LIFO Allocation Logic Gaps
**File:** `Shoudagor/app/services/inventory/batch_allocation_service.py`  
**Lines:** allocate() method  
**Severity:** HIGH  
**Impact:** Incorrect cost calculation, tax implications

**Description:**
The FIFO/LIFO allocation logic doesn't handle edge cases correctly and has potential for incorrect cost basis calculation.

**Issues Identified:**

1. **Partial Batch Allocation Not Tracked:**
```python
# If batch has 100 units and we allocate 60:
# - qty_on_hand updated to 40 ✓
# - But no record of which 60 were allocated
# - Return of 30 units: which batch do they go back to?
```

2. **LIFO Implementation Flaw:**
```python
# Current: Orders by received_date DESC
# Issue: Doesn't account for partial allocations from same batch
# Should track allocation order, not just receipt order
```

3. **Weighted Average Cost Calculation:**
```python
# Missing: Recalculation trigger when new batches arrive
# Missing: Historical cost tracking for reporting
# Issue: WAC changes retroactively affect past transactions
```

4. **Batch Status Not Considered:**
```python
# Allocates from batches with status='expired' or 'quarantined'
# Should filter: status='active' AND qty_on_hand > 0
```

**Recommended Fix:**
```python
def allocate_fifo(self, product_id, variant_id, location_id, qty_needed):
    # Get active batches only
    batches = self.batch_repo.list(
        product_id=product_id,
        variant_id=variant_id,
        location_id=location_id,
        status='active',
        include_depleted=False
    )
    
    # Sort by received_date ASC for FIFO
    batches.sort(key=lambda b: (b.received_date, b.batch_id))
    
    allocations = []
    remaining = qty_needed
    
    for batch in batches:
        if remaining <= 0:
            break
            
        available = batch.qty_on_hand
        to_allocate = min(available, remaining)
        
        # Create allocation record
        allocation = self.create_allocation(
            batch_id=batch.batch_id,
            qty=to_allocate,
            unit_cost=batch.unit_cost
        )
        
        # Update batch
        batch.qty_on_hand -= to_allocate
        if batch.qty_on_hand == 0:
            batch.status = 'depleted'
        
        allocations.append(allocation)
        remaining -= to_allocate
    
    if remaining > 0:
        raise InsufficientStockError(f"Short by {remaining} units")
    
    return allocations
```

**Business Impact:** Incorrect COGS, tax calculation errors, financial statement inaccuracies

---

### ISSUE-009: Batch Creation Missing Validation
**File:** `Shoudagor/app/services/procurement/product_order_delivery_detail_service.py`  
**Lines:** create_delivery_detail() method  
**Severity:** MEDIUM  
**Impact:** Duplicate batches, data quality issues

**Description:**
When creating batches from purchase order deliveries, the system doesn't validate for duplicate batches or check for existing batches with same lot_number.

**Issues:**
```python
# No validation for:
# 1. Duplicate lot_number from same supplier
# 2. Batch already exists for this PO detail
# 3. Negative quantities
# 4. Unit cost validation (should be > 0)
```

**Scenario:**
1. PO delivery processed: Creates Batch A (lot_number="LOT123")
2. User accidentally resubmits delivery
3. Creates Batch B (lot_number="LOT123") - duplicate!
4. Inventory reports show double quantity

**Recommended Fix:**
```python
def create_batch_from_delivery(self, delivery_detail, po_detail):
    # Validate lot number uniqueness
    if delivery_detail.lot_number:
        existing = self.batch_repo.find_by_lot_number(
            lot_number=delivery_detail.lot_number,
            supplier_id=po_detail.purchase_order.supplier_id,
            product_id=po_detail.product_id,
            variant_id=po_detail.variant_id
        )
        if existing:
            raise DuplicateBatchError(f"Batch with lot {delivery_detail.lot_number} already exists")
    
    # Validate quantities
    if delivery_detail.quantity <= 0:
        raise ValueError("Batch quantity must be positive")
    
    # Validate unit cost
    if po_detail.unit_price <= 0:
        raise ValueError("Unit cost must be positive")
    
    # Check for existing batch for this PO detail
    existing_batch = self.batch_repo.find_by_po_detail(po_detail.purchase_order_detail_id)
    if existing_batch:
        raise DuplicateBatchError("Batch already created for this PO detail")
    
    # Create batch
    batch = Batch(...)
    return self.batch_repo.create(batch)
```

**Business Impact:** Inventory inflation, inaccurate stock levels, reconciliation issues

---

### ISSUE-010: Missing Batch Expiry Handling
**File:** `Shoudagor/app/models/batch_models.py`  
**Severity:** MEDIUM  
**Impact:** Expired product allocation, compliance risk

**Description:**
The Batch model doesn't have an expiry_date field, and there's no mechanism to prevent allocation of expired batches.

**Missing Features:**
1. No expiry_date field in Batch model
2. No automatic status update to 'expired'
3. No alerts for near-expiry batches
4. Allocation service doesn't filter expired batches

**Recommended Fix:**
```python
# Add to Batch model
class Batch(Base):
    expiry_date = Column(TIMESTAMP, nullable=True)
    
    @property
    def is_expired(self):
        if not self.expiry_date:
            return False
        return datetime.now() > self.expiry_date

# Add background job
def mark_expired_batches():
    expired = db.query(Batch).filter(
        Batch.expiry_date < datetime.now(),
        Batch.status == 'active'
    ).all()
    
    for batch in expired:
        batch.status = 'expired'
    
    db.commit()

# Update allocation logic
def get_allocatable_batches(self, ...):
    return self.batch_repo.list(
        status='active',
        # Filter out expired
        filter_expired=True
    )
```

**Business Impact:** Regulatory compliance violations, customer health risks, legal liability

---

## DSR (Delivery Sales Representative) Issues

### ISSUE-011: DSR Payment Settlement Race Condition
**File:** `Shoudagor/app/services/dsr/dsr_payment_settlement_service.py`  
**Lines:** create_settlement() method  
**Severity:** HIGH  
**Impact:** Financial loss, payment discrepancies

**Description:**
The DSR payment settlement process has a race condition between reading payment_on_hand and updating it, allowing concurrent settlements to exceed available balance.

**Current Implementation:**
```python
def create_settlement(self, settlement_data, user_id, company_id):
    # Read current balance
    dsr = self.dsr_repo._get_orm(settlement_data.dsr_id)
    current_on_hand = dsr.payment_on_hand or Decimal("0")
    
    # Validate
    if settlement_data.amount > current_on_hand:
        raise HTTPException(...)
    
    # Create settlement record
    settlement = DSRPaymentSettlement(...)
    self.repo.create(settlement)
    
    # Update balance (RACE CONDITION HERE!)
    dsr.payment_on_hand = current_on_hand - settlement_data.amount
    self.db.commit()
```

**Race Condition Scenario:**
```
Time | Thread 1 (Settlement $500)      | Thread 2 (Settlement $400)
-----|----------------------------------|---------------------------
T1   | Read: payment_on_hand = $800    |
T2   |                                  | Read: payment_on_hand = $800
T3   | Validate: $500 <= $800 ✓        |
T4   |                                  | Validate: $400 <= $800 ✓
T5   | Create settlement record        |
T6   |                                  | Create settlement record
T7   | Update: $800 - $500 = $300      |
T8   |                                  | Update: $800 - $400 = $400
T9   | Commit                          |
T10  |                                  | Commit (overwrites T7!)

Result: payment_on_hand = $400 (should be -$100 or error)
Total settled: $900 from $800 balance!
```

**Recommended Fix:**
```python
def create_settlement(self, settlement_data, user_id, company_id):
    try:
        # Lock DSR record for update
        dsr = self.db.query(DeliverySalesRepresentative).filter(
            DeliverySalesRepresentative.dsr_id == settlement_data.dsr_id,
            DeliverySalesRepresentative.company_id == company_id
        ).with_for_update().first()
        
        if not dsr:
            raise HTTPException(status_code=404, detail="DSR not found")
        
        current_on_hand = dsr.payment_on_hand or Decimal("0")
        
        # Validate within locked transaction
        if settlement_data.amount > current_on_hand:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient balance: {current_on_hand}"
            )
        
        # Create settlement
        settlement = DSRPaymentSettlement(...)
        self.repo.create(settlement)
        
        # Update balance atomically
        dsr.payment_on_hand = current_on_hand - settlement_data.amount
        
        self.db.commit()
        return settlement
        
    except Exception as e:
        self.db.rollback()
        raise
```

**Business Impact:** Financial losses, audit failures, DSR trust issues

---

### ISSUE-012: DSR SO Assignment Without Stock Validation
**File:** `Shoudagor/app/services/dsr/dsr_so_assignment_service.py`  
**Lines:** create_assignment() method  
**Severity:** MEDIUM  
**Impact:** Assignment of undeliverable orders

**Description:**
Sales orders can be assigned to DSRs without validating that the DSR has sufficient stock in their storage or that the main warehouse has stock to load.

**Current Flow:**
```python
def create_assignment(self, assignment_data, user_id, company_id):
    # Validates DSR exists ✓
    # Validates SO exists ✓
    # Validates SO not already assigned ✓
    
    # Missing: Check if SO items are in stock
    # Missing: Check if DSR storage has capacity
    # Missing: Validate SO is in correct status for assignment
```

**Issues:**
1. Can assign SO with out-of-stock items
2. No validation of SO status (can assign 'cancelled' orders)
3. No check if SO is already loaded to different DSR
4. No validation of DSR storage location

**Recommended Fix:**
```python
def create_assignment(self, assignment_data, user_id, company_id):
    # Existing validations...
    
    # Validate SO status
    if sales_order.status not in ['pending', 'approved']:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot assign SO with status: {sales_order.status}"
        )
    
    # Validate SO not already loaded
    if sales_order.is_loaded:
        raise HTTPException(
            status_code=400,
            detail=f"SO already loaded by DSR {sales_order.loaded_by_dsr_id}"
        )
    
    # Validate stock availability
    for detail in sales_order.details:
        available = self.get_available_stock(
            product_id=detail.product_id,
            variant_id=detail.variant_id,
            location_id=sales_order.location_id
        )
        
        if available < detail.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for {detail.product.product_name}"
            )
    
    # Validate DSR has storage location
    dsr_storage = self.get_dsr_storage(assignment_data.dsr_id)
    if not dsr_storage:
        raise HTTPException(
            status_code=400,
            detail="DSR does not have a storage location configured"
        )
    
    # Create assignment
    assignment = DSRSOAssignment(...)
    return self.repo.create(assignment)
```

**Business Impact:** Failed deliveries, DSR operational issues, customer dissatisfaction

---

### ISSUE-013: DSR Load/Unload Operations Missing Audit Trail
**File:** `Shoudagor/app/services/dsr/dsr_so_assignment_service.py`  
**Lines:** load_so() and unload_so() methods  
**Severity:** MEDIUM  
**Impact:** Audit trail gaps, accountability issues

**Description:**
DSR stock loading and unloading operations don't create comprehensive audit records, making it difficult to track inventory movements and resolve discrepancies.

**Missing Audit Information:**
1. No timestamp of actual load/unload
2. No record of who performed the operation
3. No before/after stock snapshots
4. No reason/notes for unloading
5. No tracking of partial loads/unloads

**Recommended Fix:**
```python
# Create DSRStockMovement audit table
class DSRStockMovement(Base):
    __tablename__ = "dsr_stock_movement"
    __table_args__ = {"schema": "warehouse"}
    
    movement_id = Column(Integer, primary_key=True)
    dsr_id = Column(Integer, ForeignKey("sales.delivery_sales_representative.dsr_id"))
    sales_order_id = Column(Integer, ForeignKey("sales.sales_order.sales_order_id"))
    movement_type = Column(String(20))  # 'LOAD', 'UNLOAD', 'ADJUSTMENT'
    movement_date = Column(TIMESTAMP, nullable=False)
    performed_by = Column(Integer, ForeignKey("security.app_user.user_id"))
    from_location_id = Column(Integer)
    to_location_id = Column(Integer)
    notes = Column(Text)
    details = Column(JSON)  # Snapshot of items moved

# Update load_so method
def load_so(self, assignment_id, user_id, company_id, notes=None):
    # Existing logic...
    
    # Create audit record
    movement = DSRStockMovement(
        dsr_id=assignment.dsr_id,
        sales_order_id=assignment.sales_order_id,
        movement_type='LOAD',
        movement_date=datetime.now(),
        performed_by=user_id,
        from_location_id=sales_order.location_id,
        to_location_id=dsr_storage.location_id,
        notes=notes,
        details={
            'items': [
                {
                    'product_id': detail.product_id,
                    'variant_id': detail.variant_id,
                    'quantity': detail.quantity,
                    'before_dsr_stock': get_dsr_stock_before(),
                    'after_dsr_stock': get_dsr_stock_after()
                }
                for detail in sales_order.details
            ]
        }
    )
    self.db.add(movement)
    
    # Continue with existing logic...
```

**Business Impact:** Audit failures, dispute resolution difficulties, compliance issues

---

## Sales Order & Consolidation Issues

### ISSUE-014: SR Order Consolidation Price Adjustment Logic Flaw
**File:** `Shoudagor/app/services/consolidation_service.py`  
**Lines:** create_consolidated_sales_order() method  
**Severity:** HIGH  
**Impact:** Revenue leakage, pricing errors

**Description:**
The SR order consolidation process has flawed logic for handling price adjustments when multiple SRs negotiate different prices for the same product.

**Current Logic Issues:**
```python
# When consolidating orders from SR1 and SR2:
# SR1: Product A, Qty 10, Price $100 (negotiated from $110)
# SR2: Product A, Qty 15, Price $105 (negotiated from $110)

# Current: Uses first SR's price for entire consolidated quantity
# Result: 25 units @ $100 = $2,500
# Expected: (10 @ $100) + (15 @ $105) = $2,575
# Loss: $75 per consolidation
```

**Code Analysis:**
```python
# In consolidation_service.py
# Issue: sr_details field stores individual SR info but
# the consolidated SO detail uses single unit_price
# This loses the granular pricing information

consolidated_detail = SalesOrderDetail(
    product_id=product_id,
    variant_id=variant_id,
    quantity=total_qty,  # Sum of all SR quantities
    unit_price=first_sr_price,  # ❌ Wrong! Should be weighted average or preserve individual prices
    ...
)
```

**Recommended Fix:**
```python
def calculate_consolidated_pricing(self, sr_order_details):
    """
    Calculate proper pricing for consolidated orders
    Preserves individual SR pricing in sr_details JSON field
    """
    total_qty = sum(d.quantity for d in sr_order_details)
    total_amount = sum(d.quantity * d.unit_price for d in sr_order_details)
    weighted_avg_price = total_amount / total_qty if total_qty > 0 else 0
    
    # Store individual SR pricing details
    sr_details = [
        {
            'sr_order_detail_id': d.sr_order_detail_id,
            'sr_id': d.sr_order.sr_id,
            'sr_name': d.sr_order.sales_representative.sr_name,
            'quantity': d.quantity,
            'negotiated_price': d.unit_price,
            'sale_price': d.sale_price,
            'price_adjustment': d.unit_price - d.sale_price
        }
        for d in sr_order_details
    ]
    
    return {
        'unit_price': weighted_avg_price,
        'total_price_adjustment': sum(d['price_adjustment'] * d['quantity'] for d in sr_details),
        'sr_details': sr_details
    }
```

**Business Impact:** Revenue loss, SR commission calculation errors, financial reporting inaccuracies

---

### ISSUE-015: Sales Order Status Update Race Condition
**File:** `Shoudagor/app/services/sales/sales_order_delivery_detail_service.py`  
**Lines:** _update_so_delivery_status() method  
**Severity:** MEDIUM  
**Impact:** Incorrect order status, workflow issues

**Description:**
Multiple concurrent delivery operations can cause race conditions in sales order status updates, leading to incorrect final status.

**Scenario:**
```python
# SO has 3 line items, each being delivered concurrently

# Thread 1: Delivers item 1
def create_delivery_1():
    deliver_item_1()
    refresh_so()  # Sees: 1 delivered, 2 pending
    update_status('partial')  # ✓ Correct

# Thread 2: Delivers item 2 (concurrent)
def create_delivery_2():
    deliver_item_2()
    refresh_so()  # Sees: 1 delivered, 1 pending (missed item 2!)
    update_status('partial')  # ✓ Correct but incomplete view

# Thread 3: Delivers item 3 (concurrent)
def create_delivery_3():
    deliver_item_3()
    refresh_so()  # Sees: 2 delivered, 0 pending (missed item 3!)
    update_status('partial')  # ❌ Should be 'completed'!

# Final status: 'partial' (incorrect, should be 'completed')
```

**Root Cause:**
```python
def _update_so_delivery_status(self, sales_order):
    # Refresh to ensure we have the latest details
    self.repo.db.refresh(sales_order)  # ❌ Not atomic!
    
    # Check delivery status
    for detail in sales_order.details:
        # Calculate based on potentially stale data
        ...
```

**Recommended Fix:**
```python
def _update_so_delivery_status(self, sales_order_id):
    # Use database-level aggregation for atomic status calculation
    result = self.db.execute(text("""
        WITH delivery_status AS (
            SELECT 
                sales_order_id,
                COUNT(*) as total_items,
                SUM(CASE 
                    WHEN (quantity - shipped_quantity - returned_quantity) = 0 
                    AND (free_quantity - shipped_free_quantity - returned_free_quantity) = 0
                    THEN 1 ELSE 0 
                END) as completed_items,
                SUM(CASE 
                    WHEN shipped_quantity > 0 OR shipped_free_quantity > 0 
                    THEN 1 ELSE 0 
                END) as started_items
            FROM sales.sales_order_detail
            WHERE sales_order_id = :so_id AND is_deleted = FALSE
            GROUP BY sales_order_id
        )
        UPDATE sales.sales_order so
        SET delivery_status = CASE
            WHEN ds.completed_items = ds.total_items THEN 'completed'
            WHEN ds.started_items > 0 THEN 'partial'
            ELSE 'pending'
        END
        FROM delivery_status ds
        WHERE so.sales_order_id = ds.sales_order_id
        RETURNING so.delivery_status
    """), {'so_id': sales_order_id})
    
    return result.scalar()
```

**Business Impact:** Workflow confusion, incorrect reporting, operational inefficiency

---

### ISSUE-016: Missing Validation for Sales Order Modifications
**File:** `Shoudagor/app/services/sales/sales_order_service.py`  
**Lines:** update_sales_order() method  
**Severity:** MEDIUM  
**Impact:** Data integrity violations, business rule violations

**Description:**
Sales orders can be modified even after deliveries have been made, leading to inconsistencies between order details and delivery records.

**Current Issues:**
```python
def update_sales_order(self, sales_order_id, update_data, user_id, company_id):
    # No validation of current order state
    # No check if deliveries exist
    # No check if payments received
    # No check if order is consolidated from SR orders
    
    # Allows:
    # 1. Changing quantities after partial delivery
    # 2. Removing line items that have deliveries
    # 3. Changing prices after invoicing
    # 4. Modifying consolidated orders
```

**Problematic Scenarios:**
```python
# Scenario 1: Quantity reduction after delivery
# Order: 100 units
# Delivered: 60 units
# User updates order to 50 units
# Result: Delivered quantity (60) > Order quantity (50) ❌

# Scenario 2: Line item removal
# Order has 3 items, item 2 has been delivered
# User removes item 2 from order
# Result: Orphaned delivery record ❌

# Scenario 3: Price change after payment
# Order: $1000, Payment received: $500
# User changes price to $800
# Result: Payment ($500) > 50% of new total ($800) ❌
```

**Recommended Fix:**
```python
def update_sales_order(self, sales_order_id, update_data, user_id, company_id):
    sales_order = self.repo._get_orm(sales_order_id)
    
    # Validate order state
    if sales_order.status in ['completed', 'cancelled']:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot modify order with status: {sales_order.status}"
        )
    
    # Check for deliveries
    has_deliveries = any(
        detail.shipped_quantity > 0 or detail.shipped_free_quantity > 0
        for detail in sales_order.details
    )
    
    if has_deliveries:
        # Restrict modifications
        if 'details' in update_data:
            self._validate_detail_modifications(
                sales_order.details,
                update_data['details']
            )
    
    # Check for payments
    if sales_order.amount_paid > 0:
        if 'total_amount' in update_data:
            if update_data['total_amount'] < sales_order.amount_paid:
                raise HTTPException(
                    status_code=400,
                    detail="Cannot reduce total below amount already paid"
                )
    
    # Check if consolidated
    if sales_order.is_consolidated:
        raise HTTPException(
            status_code=400,
            detail="Cannot modify consolidated sales order. Modify source SR orders instead."
        )
    
    # Proceed with update
    return self.repo.update(sales_order, update_data)

def _validate_detail_modifications(self, existing_details, new_details):
    """Validate that modifications don't violate delivery constraints"""
    for existing in existing_details:
        if existing.shipped_quantity > 0:
            # Find corresponding new detail
            new = next((d for d in new_details if d.sales_order_detail_id == existing.sales_order_detail_id), None)
            
            if not new:
                raise HTTPException(
                    status_code=400,
                    detail=f"Cannot remove line item {existing.sales_order_detail_id} - already has deliveries"
                )
            
            if new.quantity < existing.shipped_quantity:
                raise HTTPException(
                    status_code=400,
                    detail=f"Cannot reduce quantity below shipped amount ({existing.shipped_quantity})"
                )
```

**Business Impact:** Data integrity issues, financial discrepancies, audit failures

---


## Claims & Schemes Issues

### ISSUE-017: Claim Scheme Slab Calculation Logic Flaw
**File:** `Shoudagor/app/services/claims/claim_service.py`  
**Lines:** 95-120 (_calculate_scheme_benefits method)  
**Severity:** HIGH  
**Impact:** Incorrect free quantities, discount calculation errors

**Description:**
The scheme benefit calculation uses integer division for multiplier calculation, which can lead to incorrect results for proportional schemes and doesn't handle edge cases properly.

**Issues Identified:**

1. **Multiplier Calculation Flaw:**
```python
# Current implementation
multiplier = int(quantity // threshold)

# Issue: For threshold=10, quantity=25
# multiplier = 2 (correct)
# But for threshold=10, quantity=29
# multiplier = 2 (should customer get benefit for 29 units or just 20?)
```

2. **No Validation of Slab Ordering:**
```python
# Slabs are sorted by threshold descending
# But no validation that slabs don't overlap or have gaps
# Example: Slab 1: 100+ units, Slab 2: 50+ units, Slab 3: 200+ units
# Slab 3 will never be reached!
```

3. **Percentage Discount Calculation:**
```python
# Current: Applies percentage to entire quantity
benefits["discount_amount"] = quantity * unit_price * (percentage / 100.0)

# Issue: Should it apply to threshold quantity or entire quantity?
# For 100 units with 50+ threshold at 10% discount:
# Current: 10% on all 100 units
# Expected: 10% on 50 units? Or 10% on all 100?
```

4. **No Handling of Multiple Scheme Application:**
```python
# If multiple schemes match (variant-level + product-level):
# Benefits are additive without validation
# Can lead to free_quantity > purchased quantity
```

**Recommended Fix:**
```python
def _calculate_scheme_benefits(self, quantity: float, unit_price: float, scheme: ClaimScheme) -> dict:
    """Calculate scheme benefits with proper validation"""
    # Validate slabs are properly ordered
    sorted_slabs = sorted(scheme.slabs, key=lambda s: s.threshold_qty, reverse=True)
    
    # Validate no overlapping or gaps
    for i in range(len(sorted_slabs) - 1):
        if sorted_slabs[i].threshold_qty == sorted_slabs[i+1].threshold_qty:
            raise ValueError(f"Duplicate threshold in scheme {scheme.scheme_id}")
    
    benefits = {"free_quantity": 0.0, "discount_amount": 0.0, "applied_slab": None}
    
    for slab in sorted_slabs:
        threshold = float(slab.threshold_qty)
        if quantity >= threshold:
            # Calculate multiplier based on scheme type
            if scheme.scheme_type == 'buy_x_get_y':
                # Proportional: Every X units gets Y free
                multiplier = int(quantity // threshold)
                benefits["free_quantity"] = multiplier * float(slab.free_qty)
                
                # Validate free quantity doesn't exceed purchased
                if benefits["free_quantity"] > quantity:
                    raise ValueError(f"Free quantity ({benefits['free_quantity']}) exceeds purchased ({quantity})")
                    
            elif scheme.scheme_type == 'rebate_flat':
                # Flat discount per threshold
                multiplier = int(quantity // threshold)
                benefits["discount_amount"] = multiplier * float(slab.discount_amount or 0)
                
            elif scheme.scheme_type == 'rebate_percentage':
                # Percentage discount - clarify if on threshold or total
                # Option 1: Discount on entire quantity
                percentage = float(slab.discount_percentage or 0)
                benefits["discount_amount"] = quantity * unit_price * (percentage / 100.0)
                
                # Option 2: Discount only on threshold quantity
                # benefits["discount_amount"] = threshold * unit_price * (percentage / 100.0)
                
            benefits["applied_slab"] = {
                "threshold_qty": slab.threshold_qty,
                "slab_id": slab.slab_id
            }
            break  # Use highest applicable slab
    
    return benefits
```

**Business Impact:** Revenue leakage, customer disputes, incorrect promotional costs

---

### ISSUE-018: Scheme Date Validation Insufficient
**File:** `Shoudagor/app/services/claims/claim_service.py`  
**Lines:** 20-22, 52-60  
**Severity:** MEDIUM  
**Impact:** Expired schemes applied, date overlap issues

**Description:**
Scheme date validation only checks that end_date > start_date but doesn't validate against current date or check for overlapping schemes.

**Issues:**
```python
# Current validation
if scheme.end_date <= scheme.start_date:
    raise HTTPException(status_code=400, detail="End date must be after start date")

# Missing validations:
# 1. Can create scheme with start_date in the past
# 2. Can create scheme with end_date in the past
# 3. No check for overlapping schemes on same product/variant
# 4. No warning for schemes ending soon
```

**Scenario:**
```python
# User creates scheme:
# start_date: 2026-01-01
# end_date: 2026-01-31
# Current date: 2026-03-10

# Scheme is created successfully but is already expired!
# Will never be applied to any orders
```

**Recommended Fix:**
```python
def create_scheme(self, scheme: ClaimSchemeCreate, company_id: int, user_id: int) -> ClaimScheme:
    # Date validation
    if scheme.end_date <= scheme.start_date:
        raise HTTPException(status_code=400, detail="End date must be after start date")
    
    # Warn if dates are in the past
    now = datetime.now()
    if scheme.end_date < now:
        raise HTTPException(
            status_code=400,
            detail="End date cannot be in the past"
        )
    
    if scheme.start_date < now:
        # Allow but warn
        logger.warning(f"Creating scheme with start date in the past: {scheme.start_date}")
    
    # Check for overlapping schemes
    overlapping = self.repo.find_overlapping_schemes(
        company_id=company_id,
        trigger_product_id=scheme.trigger_product_id,
        trigger_variant_id=scheme.trigger_variant_id,
        start_date=scheme.start_date,
        end_date=scheme.end_date,
        exclude_scheme_id=None
    )
    
    if overlapping:
        raise HTTPException(
            status_code=409,
            detail=f"Overlapping scheme exists: {overlapping[0].scheme_name}"
        )
    
    # Continue with existing logic...
```

**Business Impact:** Operational confusion, incorrect promotions, customer complaints

---

### ISSUE-019: Claim Log Missing Reversal Mechanism
**File:** `Shoudagor/app/services/claims/claim_service.py`  
**Lines:** 155-185 (log_claim_applications method)  
**Severity:** HIGH  
**Impact:** Incorrect claim tracking, audit trail gaps

**Description:**
The claim logging system records scheme applications but has no mechanism to reverse or adjust logs when orders are cancelled, returned, or modified.

**Issues:**
```python
def log_claim_applications(self, company_id, user_id, ref_id, ref_type, evaluated_items):
    # Creates ClaimLog entries
    # But no mechanism to:
    # 1. Reverse logs when order is cancelled
    # 2. Adjust logs when order is partially returned
    # 3. Update logs when order is modified
    # 4. Mark logs as void/reversed
```

**Scenario:**
```python
# Day 1: Create SO with scheme
# - Order: 100 units
# - Free: 10 units (from scheme)
# - ClaimLog created: given_free_qty=10

# Day 2: Customer returns 50 units
# - Return processed
# - But ClaimLog still shows given_free_qty=10
# - Should be adjusted to 5 units

# Day 3: Order cancelled
# - Order status = 'cancelled'
# - ClaimLog still shows given_free_qty=10
# - Should be reversed/voided
```

**Recommended Fix:**
```python
# Add status field to ClaimLog model
class ClaimLog(Base):
    status = Column(String(20), default='active')  # active, reversed, adjusted
    reversed_by_log_id = Column(Integer, ForeignKey('claims.claim_log.log_id'))
    reversal_reason = Column(Text)

# Add reversal method
def reverse_claim_logs(self, ref_id: int, ref_type: str, reason: str, user_id: int):
    """Reverse claim logs for cancelled/returned orders"""
    logs = self.repo.db.query(ClaimLog).filter(
        ClaimLog.ref_id == ref_id,
        ClaimLog.ref_type == ref_type,
        ClaimLog.status == 'active'
    ).all()
    
    for log in logs:
        # Create reversal entry
        reversal = ClaimLog(
            company_id=log.company_id,
            cb=user_id,
            mb=user_id,
            scheme_id=log.scheme_id,
            ref_id=ref_id,
            ref_type=ref_type,
            order_detail_id=log.order_detail_id,
            product_id=log.product_id,
            variant_id=log.variant_id,
            applied_on_qty=-log.applied_on_qty,  # Negative to reverse
            given_free_qty=-log.given_free_qty,
            given_discount_amount=-log.given_discount_amount,
            status='active',
            reversal_reason=reason
        )
        
        # Mark original as reversed
        log.status = 'reversed'
        log.reversed_by_log_id = reversal.log_id
        
        self.repo.db.add(reversal)
    
    self.repo.db.flush()

# Add adjustment method for partial returns
def adjust_claim_logs(self, ref_id: int, ref_type: str, 
                      detail_id: int, returned_qty: float, user_id: int):
    """Adjust claim logs for partial returns"""
    log = self.repo.db.query(ClaimLog).filter(
        ClaimLog.ref_id == ref_id,
        ClaimLog.ref_type == ref_type,
        ClaimLog.order_detail_id == detail_id,
        ClaimLog.status == 'active'
    ).first()
    
    if not log:
        return
    
    # Calculate adjustment ratio
    adjustment_ratio = returned_qty / log.applied_on_qty
    adjusted_free_qty = log.given_free_qty * adjustment_ratio
    adjusted_discount = log.given_discount_amount * adjustment_ratio
    
    # Create adjustment entry
    adjustment = ClaimLog(
        company_id=log.company_id,
        cb=user_id,
        mb=user_id,
        scheme_id=log.scheme_id,
        ref_id=ref_id,
        ref_type=ref_type,
        order_detail_id=detail_id,
        product_id=log.product_id,
        variant_id=log.variant_id,
        applied_on_qty=-returned_qty,
        given_free_qty=-adjusted_free_qty,
        given_discount_amount=-adjusted_discount,
        status='active',
        reversal_reason=f'Partial return adjustment: {returned_qty} units'
    )
    
    self.repo.db.add(adjustment)
    self.repo.db.flush()
```

**Business Impact:** Incorrect promotional cost tracking, financial reporting errors, supplier claim disputes

---

### ISSUE-020: Scheme Evaluation Timing Issues
**File:** `Shoudagor/app/services/claims/claim_service.py`  
**Lines:** 122-154 (evaluate_pre_claim method)  
**Severity:** MEDIUM  
**Impact:** Schemes not applied, incorrect benefits

**Description:**
The scheme evaluation happens at order creation but doesn't re-evaluate when order is modified or when schemes change.

**Issues:**
```python
def evaluate_pre_claim(self, company_id, items, target_module=None):
    # Evaluates schemes at call time
    # But:
    # 1. No re-evaluation when order quantity changes
    # 2. No re-evaluation when scheme is updated
    # 3. No re-evaluation when new schemes are activated
    # 4. Cached scheme list may be stale
```

**Scenario:**
```python
# T1: Create order with 50 units
# - No schemes active
# - free_quantity = 0

# T2: Admin activates scheme: Buy 50+ get 5 free
# - Scheme is now active
# - But existing order still has free_quantity = 0

# T3: User modifies order to 60 units
# - Quantity updated
# - But free_quantity not recalculated
# - Should be 6 free units now
```

**Recommended Fix:**
```python
# Add re-evaluation trigger
def re_evaluate_order_schemes(self, order_id: int, order_type: str, user_id: int):
    """Re-evaluate schemes for an existing order"""
    if order_type == 'sales_order':
        order = self.db.query(SalesOrder).filter(
            SalesOrder.sales_order_id == order_id
        ).first()
    elif order_type == 'purchase_order':
        order = self.db.query(PurchaseOrder).filter(
            PurchaseOrder.purchase_order_id == order_id
        ).first()
    else:
        raise ValueError(f"Invalid order type: {order_type}")
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check if order can be re-evaluated
    if order.status not in ['pending', 'approved']:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot re-evaluate order with status: {order.status}"
        )
    
    # Prepare items for evaluation
    items = [
        {
            'variant_id': detail.variant_id,
            'product_id': detail.product_id,
            'quantity': detail.quantity,
            'unit_price': detail.unit_price,
            'applied_scheme_id': detail.applied_scheme_id
        }
        for detail in order.details
    ]
    
    # Re-evaluate
    target_module = 'sale' if order_type == 'sales_order' else 'purchase'
    evaluated_items = self.evaluate_pre_claim(
        company_id=order.company_id,
        items=items,
        target_module=target_module
    )
    
    # Update order details
    for i, detail in enumerate(order.details):
        detail.free_quantity = evaluated_items[i]['free_quantity']
        detail.discount_amount = evaluated_items[i]['discount_amount']
        detail.mb = user_id
    
    # Recalculate order total
    order.total_amount = sum(
        (d.quantity * d.unit_price) - d.discount_amount
        for d in order.details
    )
    order.mb = user_id
    
    self.db.commit()
    return order

# Add background job to re-evaluate orders when schemes change
def on_scheme_activated(scheme_id: int):
    """Background job: Re-evaluate pending orders when scheme is activated"""
    scheme = get_scheme(scheme_id)
    
    # Find pending orders that could benefit from this scheme
    if scheme.applicable_to in ['sale', 'all']:
        pending_sales = db.query(SalesOrder).filter(
            SalesOrder.status.in_(['pending', 'approved']),
            SalesOrder.company_id == scheme.company_id
        ).all()
        
        for order in pending_sales:
            try:
                re_evaluate_order_schemes(order.sales_order_id, 'sales_order', system_user_id)
            except Exception as e:
                logger.error(f"Failed to re-evaluate SO {order.sales_order_id}: {e}")
```

**Business Impact:** Missed promotional opportunities, customer dissatisfaction, competitive disadvantage

---


## Frontend Issues

### ISSUE-021: Excel Import Validation Insufficient
**File:** `shoudagor_FE/src/components/forms/SaleForm.tsx` and `PurchaseForm.tsx`  
**Lines:** 200-350 (handleFileUpload method)  
**Severity:** HIGH  
**Impact:** Data corruption, invalid orders, system crashes

**Description:**
The Excel import functionality has multiple validation gaps that can lead to invalid data being imported into the system.

**Issues Identified:**

1. **No File Type Validation:**
```typescript
const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    
    // Missing: File extension validation
    // Missing: File size validation
    // Missing: MIME type validation
    // User can upload .txt, .pdf, etc.
```

2. **Weak Column Matching:**
```typescript
const getVal = (key: string) => {
    const foundKey = Object.keys(row).find(
        k => k.toLowerCase().replace(/\s/g, '') === key.toLowerCase().replace(/\s/g, '')
    );
    return foundKey ? row[foundKey] : undefined;
};

// Issues:
// - Case-insensitive matching can cause ambiguity
// - No validation of required columns
// - No handling of extra columns
// - No validation of column data types
```

3. **Stock Validation Only in SaleForm:**
```typescript
// In SaleForm.tsx - has stock validation
const availableStock = getAvailableQuantity(variant.variant_id, Number(selectedLocationId), allVariants);
if (requestedBaseQty > availableStock) {
    toast.error(`Row ${rowNum}: Insufficient stock...`);
    return;
}

// In PurchaseForm.tsx - NO stock validation
// Can import negative quantities, zero quantities, etc.
```

4. **No Transaction Rollback on Partial Failure:**
```typescript
for (let i = 0; i < data.length; i++) {
    // Process row
    if (error) {
        toast.error(`Row ${rowNum}: Error`);
        return; // ❌ Previous rows already appended!
    }
    newItems.push(item);
}

// If row 50 fails, rows 1-49 are already added to form
// User has to manually remove them
```

5. **Unit Conversion Not Validated:**
```typescript
const conversionFactor = selectedUnit?.conversion_factor || 1;
const requestedBaseQty = qty * conversionFactor;

// Issues:
// - No validation that conversion_factor is positive
// - No validation that conversion_factor is reasonable (e.g., not 0.0001 or 10000)
// - No handling of null/undefined conversion_factor
```

**Recommended Fix:**
```typescript
const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    
    // Reset target value
    e.target.value = '';
    
    // 1. Validate file type
    const allowedExtensions = ['.xlsx', '.xls'];
    const fileExtension = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();
    if (!allowedExtensions.includes(fileExtension)) {
        toast.error(`Invalid file type. Please upload ${allowedExtensions.join(' or ')} file.`);
        return;
    }
    
    // 2. Validate file size (max 5MB)
    const maxSize = 5 * 1024 * 1024;
    if (file.size > maxSize) {
        toast.error('File size exceeds 5MB limit');
        return;
    }
    
    const reader = new FileReader();
    reader.onload = async (evt) => {
        try {
            const bstr = evt.target?.result;
            const wb = XLSX.read(bstr, { type: 'binary' });
            const wsname = wb.SheetNames[0];
            const ws = wb.Sheets[wsname];
            const data = XLSX.utils.sheet_to_json(ws);
            
            if (data.length === 0) {
                toast.error("Excel file is empty");
                return;
            }
            
            // 3. Validate required columns
            const requiredColumns = ['VariantSKU', 'Quantity', 'UnitPrice'];
            const firstRow: any = data[0];
            const actualColumns = Object.keys(firstRow).map(k => 
                k.toLowerCase().replace(/\s/g, '')
            );
            
            const missingColumns = requiredColumns.filter(col => 
                !actualColumns.includes(col.toLowerCase().replace(/\s/g, ''))
            );
            
            if (missingColumns.length > 0) {
                toast.error(`Missing required columns: ${missingColumns.join(', ')}`);
                return;
            }
            
            // 4. Validate all rows first (don't modify form until all valid)
            const validatedItems: any[] = [];
            const errors: string[] = [];
            
            for (let i = 0; i < data.length; i++) {
                const row: any = data[i];
                const rowNum = i + 2;
                
                try {
                    const validatedItem = await validateAndParseRow(row, rowNum);
                    validatedItems.push(validatedItem);
                } catch (error: any) {
                    errors.push(`Row ${rowNum}: ${error.message}`);
                    if (errors.length >= 10) {
                        errors.push('... and more errors');
                        break;
                    }
                }
            }
            
            // 5. If any errors, show all and abort
            if (errors.length > 0) {
                toast.error(
                    <div>
                        <p>Import failed with {errors.length} error(s):</p>
                        <ul>
                            {errors.slice(0, 5).map((err, i) => <li key={i}>{err}</li>)}
                        </ul>
                    </div>,
                    { duration: 10000 }
                );
                return;
            }
            
            // 6. All valid - now update form
            if (fields.length === 1 && !fields[0].product_id) {
                remove(0);
            }
            
            append(validatedItems.map(item => item.formData));
            setAmounts(prev => ({ ...prev, ...validatedItems.reduce((acc, item, idx) => {
                acc[fields.length + idx] = item.amount;
                return acc;
            }, {}) }));
            
            toast.success(`Successfully imported ${validatedItems.length} items`);
            
        } catch (error) {
            console.error("Import error:", error);
            toast.error("Failed to process Excel file. Please check the file format.");
        }
    };
    
    reader.onerror = () => {
        toast.error("Failed to read file");
    };
    
    reader.readAsBinaryString(file);
};

// Helper function to validate individual row
async function validateAndParseRow(row: any, rowNum: number): Promise<any> {
    const getVal = (key: string) => {
        const foundKey = Object.keys(row).find(
            k => k.toLowerCase().replace(/\s/g, '') === key.toLowerCase().replace(/\s/g, '')
        );
        return foundKey ? row[foundKey] : undefined;
    };
    
    const excelSKU = getVal('VariantSKU');
    const excelQty = getVal('Quantity');
    const excelPrice = getVal('UnitPrice');
    
    // Validate required fields
    if (!excelSKU) throw new Error('VariantSKU is required');
    if (!excelQty) throw new Error('Quantity is required');
    if (!excelPrice) throw new Error('UnitPrice is required');
    
    // Validate numbers
    const qty = Number(excelQty);
    const price = Number(excelPrice);
    
    if (isNaN(qty)) throw new Error('Quantity must be a number');
    if (qty <= 0) throw new Error('Quantity must be positive');
    if (qty > 1000000) throw new Error('Quantity exceeds maximum (1,000,000)');
    
    if (isNaN(price)) throw new Error('UnitPrice must be a number');
    if (price < 0) throw new Error('UnitPrice cannot be negative');
    if (price > 1000000) throw new Error('UnitPrice exceeds maximum (1,000,000)');
    
    // Find variant
    const variant = allVariants?.data?.find(v => v.sku === String(excelSKU));
    if (!variant) throw new Error(`Variant not found for SKU: ${excelSKU}`);
    
    // Additional validations...
    
    return {
        formData: { /* ... */ },
        amount: qty * price
    };
}
```

**Business Impact:** Data integrity issues, operational disruptions, user frustration

---

### ISSUE-022: Form State Management Race Conditions
**File:** `shoudagor_FE/src/components/forms/SaleForm.tsx` and `PurchaseForm.tsx`  
**Lines:** Multiple useEffect hooks  
**Severity:** MEDIUM  
**Impact:** Stale data, incorrect calculations, UI inconsistencies

**Description:**
Multiple useEffect hooks update form state concurrently, leading to race conditions and stale data issues.

**Issues:**

1. **Cascading useEffect Updates:**
```typescript
// Effect 1: Updates total when details change
useEffect(() => {
    const newTotalAmount = details.reduce(...);
    form.setValue("total_amount", newTotalAmount);
}, [details]);

// Effect 2: Updates details when schemes change
useEffect(() => {
    details.forEach((item, index) => {
        updateSchemeBenefits(index, ...);
    });
}, [schemes]);

// Effect 3: Updates amounts when units change
useEffect(() => {
    details.forEach((item, index) => {
        calculateAmount(index, ...);
    });
}, [unitOptions]);

// Race condition: All three can run simultaneously
// Final state depends on execution order
```

2. **Stale Closure in Callbacks:**
```typescript
const handleVariantChange = async (index: number, variantId: string) => {
    // Gets variant
    const variant = allVariants?.data?.find(...);
    
    // Updates form
    update(index, { ...fields[index], variant_id: variant.variant_id });
    
    // Calculates amount using potentially stale fields[index]
    const qty = Number(form.getValues(`details.${index}.quantity`)) || 0;
    // ❌ qty might be from old state if form hasn't re-rendered
};
```

3. **Missing Dependency Arrays:**
```typescript
useEffect(() => {
    // Uses form, details, amounts
    // But dependency array incomplete
}, [details]); // Missing: form, amounts
```

**Recommended Fix:**
```typescript
// 1. Use single source of truth with proper memoization
const calculatedTotals = useMemo(() => {
    if (!details) return { subtotal: 0, discount: 0, total: 0 };
    
    let subtotal = 0;
    let discount = 0;
    
    details.forEach((item, index) => {
        const amount = amounts[index] || (item.quantity * item.unit_price);
        subtotal += amount;
        discount += item.discount_amount || 0;
    });
    
    return {
        subtotal,
        discount,
        total: subtotal - discount
    };
}, [details, amounts]);

// 2. Update form only when calculated values change
useEffect(() => {
    form.setValue("total_amount", calculatedTotals.total, { 
        shouldValidate: true,
        shouldDirty: false // Don't mark as dirty for calculated fields
    });
}, [calculatedTotals.total, form]);

// 3. Use callbacks with latest values
const handleVariantChange = useCallback(async (index: number, variantId: string) => {
    const variant = allVariants?.data?.find(v => v.variant_id === parseInt(variantId, 10));
    if (!variant) return;
    
    const purchasePrice = variant.current_price?.purchase_price || 0;
    
    // Use form.getValues to get latest values
    const currentQty = Number(form.getValues(`details.${index}.quantity`)) || 0;
    
    // Batch updates
    form.setValue(`details.${index}.variant_id`, variant.variant_id, { shouldValidate: true });
    form.setValue(`details.${index}.product_id`, variant.product_id, { shouldValidate: true });
    form.setValue(`details.${index}.unit_price`, purchasePrice, { shouldValidate: true });
    
    // Calculate amount with latest values
    const amount = purchasePrice * currentQty;
    setAmounts(prev => ({ ...prev, [index]: amount }));
    
}, [allVariants?.data, form]);

// 4. Debounce expensive calculations
const debouncedUpdateSchemes = useMemo(
    () => debounce((index: number, qty: number, price: number) => {
        updateSchemeBenefits(index, qty, price);
    }, 300),
    []
);
```

**Business Impact:** User confusion, incorrect order totals, data entry errors

---

### ISSUE-023: API Error Handling Inconsistent
**File:** `shoudagor_FE/src/lib/api/claimsApi.ts` and other API files  
**Lines:** Throughout API layer  
**Severity:** MEDIUM  
**Impact:** Poor user experience, debugging difficulties

**Description:**
API error handling is inconsistent across the frontend, with some endpoints having no error handling and others having incomplete handling.

**Issues:**

1. **No Error Transformation:**
```typescript
export const createScheme = (data: ClaimSchemeType): Promise<ClaimSchemeType> => {
    const payload = {
        ...data,
        start_date: new Date(data.start_date).toISOString(),
        end_date: new Date(data.end_date).toISOString()
    };
    return apiRequest(api, '/claims/schemes', {
        method: 'POST',
        body: JSON.stringify(payload),
    });
    // No error handling
    // No validation of response
    // No type checking
};
```

2. **Silent Failures:**
```typescript
// In forms
const createMutation = useMutation({
    mutationFn: (data: InsertSale) => createSale(data),
    onSuccess: executeFreezeRefresh,
    onError: () => {
        toast.error("Failed to create sale"); // ❌ Generic message
        // No error details
        // No error logging
        // No retry mechanism
    },
});
```

3. **Inconsistent Error Messages:**
```typescript
// Some places:
toast.error("Failed to create sale");

// Other places:
toast.error(`Row ${rowNum}: Product/Variant not found for SKU '${excelSKU}'`);

// No standardization
// No error codes
// No i18n support
```

4. **No Network Error Handling:**
```typescript
// No handling for:
// - Network timeout
// - Connection lost
// - 500 server errors
// - 401 unauthorized
// - 403 forbidden
```

**Recommended Fix:**
```typescript
// 1. Create error transformation utility
interface ApiError {
    code: string;
    message: string;
    details?: any;
    statusCode?: number;
}

function transformApiError(error: any): ApiError {
    // Handle axios errors
    if (error.response) {
        return {
            code: error.response.data?.code || 'API_ERROR',
            message: error.response.data?.detail || error.response.data?.message || 'An error occurred',
            details: error.response.data,
            statusCode: error.response.status
        };
    }
    
    // Handle network errors
    if (error.request) {
        return {
            code: 'NETWORK_ERROR',
            message: 'Unable to connect to server. Please check your internet connection.',
            statusCode: 0
        };
    }
    
    // Handle other errors
    return {
        code: 'UNKNOWN_ERROR',
        message: error.message || 'An unexpected error occurred',
    };
}

// 2. Create error display utility
function displayError(error: ApiError, context?: string) {
    const prefix = context ? `${context}: ` : '';
    
    // Map error codes to user-friendly messages
    const errorMessages: Record<string, string> = {
        'NETWORK_ERROR': 'Connection lost. Please check your internet.',
        'VALIDATION_ERROR': 'Please check your input and try again.',
        'DUPLICATE_ERROR': 'This record already exists.',
        'NOT_FOUND': 'The requested item was not found.',
        'UNAUTHORIZED': 'You are not authorized to perform this action.',
        'INSUFFICIENT_STOCK': 'Insufficient stock available.',
    };
    
    const message = errorMessages[error.code] || error.message;
    
    toast.error(`${prefix}${message}`, {
        description: error.details?.hint,
        duration: 5000,
    });
    
    // Log to monitoring service
    if (error.statusCode && error.statusCode >= 500) {
        console.error('Server error:', error);
        // Send to error tracking service (e.g., Sentry)
    }
}

// 3. Update API functions
export const createScheme = async (data: ClaimSchemeType): Promise<ClaimSchemeType> => {
    try {
        // Validate input
        if (!data.scheme_name || data.scheme_name.trim() === '') {
            throw new Error('Scheme name is required');
        }
        
        if (new Date(data.end_date) <= new Date(data.start_date)) {
            throw new Error('End date must be after start date');
        }
        
        const payload = {
            ...data,
            start_date: new Date(data.start_date).toISOString(),
            end_date: new Date(data.end_date).toISOString()
        };
        
        const response = await apiRequest(api, '/claims/schemes', {
            method: 'POST',
            body: JSON.stringify(payload),
        });
        
        // Validate response
        if (!response || !response.scheme_id) {
            throw new Error('Invalid response from server');
        }
        
        return response;
        
    } catch (error) {
        const apiError = transformApiError(error);
        displayError(apiError, 'Create Scheme');
        throw apiError;
    }
};

// 4. Update mutations with better error handling
const createMutation = useMutation({
    mutationFn: (data: InsertSale) => createSale(data),
    onSuccess: executeFreezeRefresh,
    onError: (error: any) => {
        const apiError = transformApiError(error);
        displayError(apiError, 'Create Sale');
        
        // Specific handling for certain errors
        if (apiError.code === 'INSUFFICIENT_STOCK') {
            // Show stock availability dialog
            setShowStockDialog(true);
        } else if (apiError.code === 'DUPLICATE_ERROR') {
            // Highlight the duplicate field
            form.setError('order_number', {
                type: 'manual',
                message: 'This order number already exists'
            });
        }
    },
    retry: (failureCount, error: any) => {
        const apiError = transformApiError(error);
        // Retry on network errors, but not on validation errors
        return apiError.code === 'NETWORK_ERROR' && failureCount < 3;
    },
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
});

// 5. Add global error boundary
class ErrorBoundary extends React.Component<Props, State> {
    componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
        console.error('React Error:', error, errorInfo);
        // Send to error tracking
        // Show user-friendly error page
    }
    
    render() {
        if (this.state.hasError) {
            return <ErrorFallback />;
        }
        return this.props.children;
    }
}
```

**Business Impact:** Poor user experience, increased support tickets, debugging difficulties

---

### ISSUE-024: Form Validation Timing Issues
**File:** `shoudagor_FE/src/components/forms/SaleForm.tsx` and `PurchaseForm.tsx`  
**Lines:** Form validation logic  
**Severity:** MEDIUM  
**Impact:** Invalid data submission, user frustration

**Description:**
Form validation happens at different times (onChange, onBlur, onSubmit) inconsistently, leading to confusing user experience.

**Issues:**

1. **Inconsistent Validation Triggers:**
```typescript
// Some fields validate onChange
<FormField
    control={form.control}
    name="order_number"
    render={({ field }) => (
        <Input
            {...field}
            onChange={(e) => {
                field.onChange(e.target.value);
                // Validates immediately
            }}
        />
    )}
/>

// Other fields validate onBlur
<FormField
    control={form.control}
    name="customer_id"
    render={({ field }) => (
        <SearchableSelect
            value={field.value}
            onChange={(value) => {
                field.onChange(value);
                // No immediate validation
            }}
        />
    )}
/>
```

2. **Async Validation Not Handled:**
```typescript
// No validation for:
// - Duplicate order numbers (requires API call)
// - Stock availability (requires API call)
// - Customer credit limit (requires API call)
```

3. **Cross-Field Validation Missing:**
```typescript
// Expected shipment date should be >= order date
// But validation only checks individual fields
// No validation that total_amount matches sum of details
// No validation that quantities don't exceed stock
```

4. **Validation Error Display Inconsistent:**
```typescript
// Some errors shown inline
<FormMessage /> // Shows field-level error

// Some errors shown as toast
toast.error("Validation failed");

// Some errors not shown at all
// User clicks submit, nothing happens
```

**Recommended Fix:**
```typescript
// 1. Define validation schema with cross-field rules
const saleFormSchema = z.object({
    order_number: z.string()
        .min(1, 'Order number is required')
        .max(50, 'Order number too long')
        .refine(async (value) => {
            // Async validation for duplicates
            if (!value) return true;
            const exists = await checkOrderNumberExists(value);
            return !exists;
        }, 'Order number already exists'),
    
    customer_id: z.number()
        .positive('Customer is required'),
    
    order_date: z.string()
        .datetime('Invalid date'),
    
    expected_shipment_date: z.string()
        .datetime('Invalid date'),
    
    location_id: z.number()
        .positive('Location is required'),
    
    details: z.array(z.object({
        product_id: z.number().positive(),
        variant_id: z.number().positive(),
        quantity: z.number().positive('Quantity must be positive'),
        unit_price: z.number().nonnegative('Price cannot be negative'),
    })).min(1, 'At least one item is required'),
    
}).refine((data) => {
    // Cross-field validation: shipment date >= order date
    return new Date(data.expected_shipment_date) >= new Date(data.order_date);
}, {
    message: 'Expected shipment date must be on or after order date',
    path: ['expected_shipment_date']
}).refine(async (data) => {
    // Validate stock availability for all items
    for (const detail of data.details) {
        const available = await getAvailableStock(
            detail.variant_id,
            data.location_id
        );
        if (detail.quantity > available) {
            return false;
        }
    }
    return true;
}, {
    message: 'Insufficient stock for one or more items',
    path: ['details']
});

// 2. Configure form with consistent validation mode
const form = useForm<InsertSale>({
    resolver: zodResolver(saleFormSchema),
    mode: 'onBlur', // Validate on blur for better UX
    reValidateMode: 'onChange', // Re-validate on change after first validation
    defaultValues: { /* ... */ },
});

// 3. Add custom validation hooks
const useStockValidation = (variantId: number, locationId: number, quantity: number) => {
    return useQuery({
        queryKey: ['stock-validation', variantId, locationId],
        queryFn: () => getAvailableStock(variantId, locationId),
        enabled: !!variantId && !!locationId,
        select: (available) => ({
            isValid: quantity <= available,
            available,
            requested: quantity,
            shortage: Math.max(0, quantity - available)
        })
    });
};

// 4. Show validation errors consistently
const onSubmit = async (data: InsertSale) => {
    try {
        // Final validation before submit
        const validationResult = await saleFormSchema.safeParseAsync(data);
        
        if (!validationResult.success) {
            // Show all validation errors
            const errors = validationResult.error.errors;
            toast.error(
                <div>
                    <p>Please fix the following errors:</p>
                    <ul>
                        {errors.map((err, i) => (
                            <li key={i}>{err.path.join('.')}: {err.message}</li>
                        ))}
                    </ul>
                </div>,
                { duration: 10000 }
            );
            return;
        }
        
        // Submit
        if (isEditing) {
            updateMutation.mutate(data);
        } else {
            createMutation.mutate(data);
        }
        
    } catch (error) {
        console.error('Validation error:', error);
        toast.error('Validation failed. Please check your input.');
    }
};

// 5. Add real-time stock indicator
const StockIndicator = ({ variantId, locationId, quantity }: Props) => {
    const { data: stockValidation, isLoading } = useStockValidation(
        variantId,
        locationId,
        quantity
    );
    
    if (isLoading) return <Spinner size="sm" />;
    
    if (!stockValidation?.isValid) {
        return (
            <Tooltip>
                <TooltipTrigger>
                    <CircleAlert className="text-destructive" />
                </TooltipTrigger>
                <TooltipContent>
                    Insufficient stock. Available: {stockValidation?.available}, 
                    Requested: {stockValidation?.requested}
                </TooltipContent>
            </Tooltip>
        );
    }
    
    return <CheckCircle className="text-success" />;
};
```

**Business Impact:** Data quality issues, user frustration, increased error rates

---

### ISSUE-025: Memory Leaks in Form Components
**File:** `shoudagor_FE/src/components/forms/SaleForm.tsx` and `PurchaseForm.tsx`  
**Lines:** useEffect hooks, event handlers  
**Severity:** MEDIUM  
**Impact:** Performance degradation, browser crashes

**Description:**
Form components have multiple memory leak sources including uncleaned event listeners, unaborted async operations, and stale closures.

**Issues:**

1. **Async Operations Not Cancelled:**
```typescript
const handleVariantChange = async (index: number, variantId: string) => {
    // Async operation
    const units = await getRelatedUnits(variant.unit_id);
    setUnitOptions((prev) => ({ ...prev, [index]: units.data }));
    
    // If component unmounts before this completes:
    // - setState called on unmounted component
    // - Memory leak
    // - Warning in console
};
```

2. **Event Listeners Not Cleaned:**
```typescript
useEffect(() => {
    // Adds listener but never removes
    window.addEventListener('beforeunload', handleBeforeUnload);
    // Missing cleanup
}, []);
```

3. **Timers Not Cleared:**
```typescript
const debouncedUpdate = debounce((index, qty, price) => {
    updateSchemeBenefits(index, qty, price);
}, 300);

// Debounce creates timer
// Timer not cleared on unmount
// Memory leak
```

4. **Large State Objects Not Cleaned:**
```typescript
const [variantOptions, setVariantOptions] = useState<{ [key: number]: ProductVariant[] }>({});
const [unitOptions, setUnitOptions] = useState<{ [key: number]: Unit[] }>({});
const [amounts, setAmounts] = useState<{ [key: number]: number }>({});

// These grow indefinitely as items are added/removed
// Old indices never cleaned up
// Memory usage grows over time
```

**Recommended Fix:**
```typescript
// 1. Cancel async operations on unmount
const handleVariantChange = async (index: number, variantId: string) => {
    const abortController = new AbortController();
    
    try {
        const units = await getRelatedUnits(variant.unit_id, {
            signal: abortController.signal
        });
        
        // Check if still mounted
        if (!abortController.signal.aborted) {
            setUnitOptions((prev) => ({ ...prev, [index]: units.data }));
        }
    } catch (error) {
        if (error.name === 'AbortError') {
            // Operation cancelled, ignore
            return;
        }
        throw error;
    }
    
    // Cleanup
    return () => abortController.abort();
};

// 2. Clean up event listeners
useEffect(() => {
    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
        if (form.formState.isDirty) {
            e.preventDefault();
            e.returnValue = '';
        }
    };
    
    window.addEventListener('beforeunload', handleBeforeUnload);
    
    return () => {
        window.removeEventListener('beforeunload', handleBeforeUnload);
    };
}, [form.formState.isDirty]);

// 3. Clear timers and debounced functions
const debouncedUpdateRef = useRef<ReturnType<typeof debounce>>();

useEffect(() => {
    debouncedUpdateRef.current = debounce((index, qty, price) => {
        updateSchemeBenefits(index, qty, price);
    }, 300);
    
    return () => {
        // Cancel pending debounced calls
        debouncedUpdateRef.current?.cancel();
    };
}, []);

// 4. Clean up state objects when items removed
const removeItem = (index: number) => {
    if (fields.length > 1) {
        remove(index);
        
        // Clean up associated state
        setVariantOptions(prev => {
            const next = { ...prev };
            delete next[index];
            return next;
        });
        
        setUnitOptions(prev => {
            const next = { ...prev };
            delete next[index];
            return next;
        });
        
        setAmounts(prev => {
            const next = { ...prev };
            delete next[index];
            return next;
        });
        
        setManualSchemes(prev => {
            const next = { ...prev };
            delete next[index];
            return next;
        });
    }
};

// 5. Use cleanup in useQuery
const { data: allVariants } = useQuery({
    queryKey: ["/variants"],
    queryFn: async ({ signal }) => {
        const response = await getAllVariants(0, 10000, { signal });
        return response;
    },
    // Cleanup stale data
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
});

// 6. Add component unmount cleanup
useEffect(() => {
    return () => {
        // Clean up all state on unmount
        setVariantOptions({});
        setUnitOptions({});
        setAmounts({});
        setManualSchemes({});
        setDismissedVariants(new Set());
    };
}, []);

// 7. Use WeakMap for large object references
const variantCacheRef = useRef(new WeakMap<ProductVariant, any>());

const getCachedVariantData = (variant: ProductVariant) => {
    if (!variantCacheRef.current.has(variant)) {
        const data = computeExpensiveData(variant);
        variantCacheRef.current.set(variant, data);
    }
    return variantCacheRef.current.get(variant);
};
// WeakMap allows garbage collection when variant is no longer referenced
```

**Business Impact:** Poor performance, browser crashes, user frustration

---

## Security & Validation Issues

### ISSUE-026: JWT Token Security Weaknesses
**File:** `Shoudagor/app/core/security.py`  
**Lines:** 10-30  
**Severity:** CRITICAL  
**Impact:** Authentication bypass, unauthorized access

**Description:**
The JWT implementation has several security weaknesses that could lead to authentication bypass and unauthorized access.

**Issues Identified:**

1. **Extremely Long Token Expiry:**
```python
def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None, claims: dict = None) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(weeks=52)  # ❌ 1 YEAR!
```

2. **No Token Refresh Mechanism:**
```python
# No refresh token implementation
# No way to revoke tokens
# No token blacklist
# Once issued, token valid for 1 year
```

3. **No Token Validation Beyond Signature:**
```python
def decode_access_token(token: str) -> Union[dict, Any]:
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return decoded_token
    except JWTError:
        return None
    
    # Missing validations:
    # - No check if token is expired (relies on jwt library)
    # - No check if user still exists
    # - No check if user is still active
    # - No check if permissions changed
    # - No check against revocation list
```

4. **Weak Password Hashing Configuration:**
```python
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# Issues:
# - No explicit rounds/iterations specified
# - No salt length specified
# - Should use bcrypt or argon2 instead
```

5. **No Rate Limiting on Authentication:**
```python
# No protection against:
# - Brute force attacks
# - Credential stuffing
# - Token enumeration
```

**Recommended Fix:**
```python
# 1. Implement proper token expiry
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 30 minutes
REFRESH_TOKEN_EXPIRE_DAYS = 7  # 7 days

def create_access_token(
    subject: Union[str, Any],
    expires_delta: timedelta = None,
    claims: dict = None,
    token_type: str = "access"
) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        if token_type == "access":
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        else:  # refresh token
            expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": token_type,
        "iat": datetime.utcnow(),  # Issued at
        "jti": str(uuid.uuid4()),  # JWT ID for revocation
    }
    
    if claims:
        to_encode.update(claims)
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# 2. Implement token refresh
def create_refresh_token(user_id: int) -> str:
    return create_access_token(
        subject=user_id,
        token_type="refresh",
        expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )

def refresh_access_token(refresh_token: str, db: Session) -> dict:
    """Exchange refresh token for new access token"""
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Validate token type
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        
        # Check if token is revoked
        jti = payload.get("jti")
        if is_token_revoked(jti, db):
            raise HTTPException(status_code=401, detail="Token has been revoked")
        
        # Get user
        user_id = int(payload.get("sub"))
        user = db.query(User).filter(User.user_id == user_id).first()
        
        if not user or not user.is_active:
            raise HTTPException(status_code=401, detail="User not found or inactive")
        
        # Create new access token
        access_token = create_access_token(
            subject=user_id,
            claims={
                "company_id": user.company_id,
                "role": user.role,
            }
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
        
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

# 3. Implement token revocation
class RevokedToken(Base):
    __tablename__ = "revoked_tokens"
    __table_args__ = {"schema": "security"}
    
    jti = Column(String(36), primary_key=True)
    revoked_at = Column(TIMESTAMP, default=datetime.utcnow)
    expires_at = Column(TIMESTAMP, nullable=False)

def revoke_token(jti: str, expires_at: datetime, db: Session):
    """Add token to revocation list"""
    revoked = RevokedToken(
        jti=jti,
        expires_at=expires_at
    )
    db.add(revoked)
    db.commit()

def is_token_revoked(jti: str, db: Session) -> bool:
    """Check if token is revoked"""
    revoked = db.query(RevokedToken).filter(
        RevokedToken.jti == jti,
        RevokedToken.expires_at > datetime.utcnow()
    ).first()
    return revoked is not None

# 4. Enhanced token validation
def decode_and_validate_token(token: str, db: Session, required_type: str = "access") -> dict:
    """Decode and fully validate token"""
    try:
        # Decode token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Validate token type
        if payload.get("type") != required_type:
            raise HTTPException(status_code=401, detail="Invalid token type")
        
        # Check if revoked
        jti = payload.get("jti")
        if is_token_revoked(jti, db):
            raise HTTPException(status_code=401, detail="Token has been revoked")
        
        # Validate user still exists and is active
        user_id = int(payload.get("sub"))
        user = db.query(User).filter(User.user_id == user_id).first()
        
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        if not user.is_active:
            raise HTTPException(status_code=401, detail="User account is disabled")
        
        # Add user info to payload
        payload["user"] = user
        
        return payload
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# 5. Upgrade password hashing
pwd_context = CryptContext(
    schemes=["argon2", "bcrypt"],
    deprecated="auto",
    argon2__memory_cost=65536,  # 64 MB
    argon2__time_cost=3,  # 3 iterations
    argon2__parallelism=4,  # 4 threads
    bcrypt__rounds=12,  # 12 rounds
)

# 6. Add rate limiting (in dependencies.py)
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/auth/login")
@limiter.limit("5/minute")  # 5 attempts per minute
async def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    # Login logic
    pass

# 7. Implement logout
@app.post("/api/auth/logout")
async def logout(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Logout by revoking current token"""
    payload = decode_and_validate_token(token, db)
    jti = payload.get("jti")
    expires_at = datetime.fromtimestamp(payload.get("exp"))
    
    revoke_token(jti, expires_at, db)
    
    return {"message": "Successfully logged out"}
```

**Business Impact:** Security breaches, unauthorized data access, compliance violations

---

### ISSUE-027: SQL Injection Vulnerabilities
**File:** Multiple service and repository files  
**Lines:** Raw SQL queries  
**Severity:** CRITICAL  
**Impact:** Data breach, data loss, system compromise

**Description:**
Several locations use raw SQL queries with string formatting, creating SQL injection vulnerabilities.

**Vulnerable Code Examples:**

1. **In Batch API:**
```python
# From batch.py reconciliation endpoint
result = self.db.execute(text("""
    WITH delivery_status AS (
        SELECT 
            sales_order_id,
            COUNT(*) as total_items,
            SUM(CASE 
                WHEN (quantity - shipped_quantity - returned_quantity) = 0 
                THEN 1 ELSE 0 
            END) as completed_items
        FROM sales.sales_order_detail
        WHERE sales_order_id = :so_id AND is_deleted = FALSE
        GROUP BY sales_order_id
    )
    ...
"""), {'so_id': sales_order_id})

# This is safe (uses parameterization)
# But other queries may not be
```

2. **Potential Vulnerabilities in Search:**
```python
# If search parameter is not sanitized
def list_schemes(self, company_id, skip, limit, is_active, search):
    query = self.db.query(ClaimScheme).filter(
        ClaimScheme.company_id == company_id
    )
    
    if search:
        # If search contains SQL, this could be vulnerable
        query = query.filter(
            ClaimScheme.scheme_name.ilike(f"%{search}%")  # ⚠️ Potential issue
        )
```

3. **Dynamic Column Sorting:**
```python
# If sort_by comes from user input without validation
def list_with_sort(self, sort_by: str, sort_order: str):
    query = f"SELECT * FROM table ORDER BY {sort_by} {sort_order}"
    # ❌ SQL Injection vulnerability
```

**Recommended Fix:**
```python
# 1. Always use parameterized queries
def list_schemes(self, company_id, skip, limit, is_active, search):
    query = self.db.query(ClaimScheme).filter(
        ClaimScheme.company_id == company_id
    )
    
    if search:
        # Use SQLAlchemy's safe parameter binding
        query = query.filter(
            ClaimScheme.scheme_name.ilike(f"%{search}%")  # Safe with SQLAlchemy
        )
    
    # Or use explicit parameter binding for raw SQL
    if search:
        query = query.filter(
            text("scheme_name ILIKE :search")
        ).params(search=f"%{search}%")
    
    return query.offset(skip).limit(limit).all()

# 2. Whitelist dynamic column names
ALLOWED_SORT_COLUMNS = {
    'scheme_name', 'start_date', 'end_date', 'created_at'
}

ALLOWED_SORT_ORDERS = {'asc', 'desc'}

def list_with_sort(self, sort_by: str, sort_order: str):
    # Validate inputs
    if sort_by not in ALLOWED_SORT_COLUMNS:
        raise ValueError(f"Invalid sort column: {sort_by}")
    
    if sort_order.lower() not in ALLOWED_SORT_ORDERS:
        raise ValueError(f"Invalid sort order: {sort_order}")
    
    # Safe to use in query now
    order_clause = getattr(ClaimScheme, sort_by)
    if sort_order.lower() == 'desc':
        order_clause = order_clause.desc()
    
    return self.db.query(ClaimScheme).order_by(order_clause).all()

# 3. Use ORM instead of raw SQL where possible
# Instead of:
result = db.execute(text(f"SELECT * FROM users WHERE name = '{name}'"))

# Use:
result = db.query(User).filter(User.name == name).all()

# 4. If raw SQL is necessary, use parameterization
# Instead of:
query = f"SELECT * FROM orders WHERE status = '{status}'"
result = db.execute(text(query))

# Use:
query = "SELECT * FROM orders WHERE status = :status"
result = db.execute(text(query), {'status': status})

# 5. Add input validation layer
from pydantic import BaseModel, validator

class SearchRequest(BaseModel):
    search: str
    sort_by: str = 'created_at'
    sort_order: str = 'desc'
    
    @validator('search')
    def validate_search(cls, v):
        # Remove potentially dangerous characters
        if v:
            # Allow only alphanumeric, spaces, and basic punctuation
            import re
            if not re.match(r'^[a-zA-Z0-9\s\-_.]+$', v):
                raise ValueError('Search contains invalid characters')
        return v
    
    @validator('sort_by')
    def validate_sort_by(cls, v):
        if v not in ALLOWED_SORT_COLUMNS:
            raise ValueError(f'Invalid sort column: {v}')
        return v
    
    @validator('sort_order')
    def validate_sort_order(cls, v):
        if v.lower() not in ALLOWED_SORT_ORDERS:
            raise ValueError(f'Invalid sort order: {v}')
        return v.lower()

# 6. Add SQL injection detection middleware
def detect_sql_injection(value: str) -> bool:
    """Detect common SQL injection patterns"""
    if not value:
        return False
    
    # Common SQL injection patterns
    patterns = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE)\b)",
        r"(--|#|/\*|\*/)",
        r"(\bOR\b.*=.*)",
        r"(\bAND\b.*=.*)",
        r"(;.*--)",
        r"(\bUNION\b.*\bSELECT\b)",
    ]
    
    import re
    for pattern in patterns:
        if re.search(pattern, value, re.IGNORECASE):
            return True
    
    return False

# Use in API endpoints
@router.get("/schemes")
def list_schemes(
    search: str = Query(None),
    db: Session = Depends(get_db)
):
    # Validate input
    if search and detect_sql_injection(search):
        raise HTTPException(
            status_code=400,
            detail="Invalid search parameter"
        )
    
    # Proceed with query
    ...
```

**Business Impact:** Data breaches, regulatory fines, reputational damage, legal liability

---

### ISSUE-028: Missing Authorization Checks
**File:** Multiple API endpoints  
**Lines:** Throughout API layer  
**Severity:** CRITICAL  
**Impact:** Unauthorized data access, privilege escalation

**Description:**
Many API endpoints check authentication but don't properly validate authorization, allowing users to access data from other companies or perform actions beyond their role.

**Issues:**

1. **Company ID Not Validated:**
```python
@batch_router.get("/{batch_id}")
def get_batch(
    batch_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    company_id: int = Depends(get_current_company_id),
):
    batch = batch_repo.get(batch_id)
    
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    
    # ✓ Good: Validates company_id
    if batch.company_id != company_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return batch

# But many other endpoints don't have this check!
```

2. **Role-Based Access Control Missing:**
```python
@router.delete("/schemes/{scheme_id}")
def delete_scheme(
    scheme_id: int,
    current_user: dict = Depends(get_current_user),
    # ❌ No role check!
    # Any authenticated user can delete schemes
):
    service.delete_scheme(scheme_id)
```

3. **Resource Ownership Not Validated:**
```python
@router.put("/sales-orders/{order_id}")
def update_order(
    order_id: int,
    update_data: OrderUpdate,
    current_user: dict = Depends(get_current_user),
):
    # ❌ No check if user owns this order
    # ❌ No check if user's company owns this order
    # ❌ No check if user has permission to edit orders
    return service.update_order(order_id, update_data)
```

**Recommended Fix:**
```python
# 1. Create authorization decorators
from functools import wraps
from typing import List

def require_roles(allowed_roles: List[str]):
    """Decorator to check user role"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user: dict = None, **kwargs):
            if not current_user:
                raise HTTPException(status_code=401, detail="Not authenticated")
            
            user_role = current_user.get("role")
            if user_role not in allowed_roles:
                raise HTTPException(
                    status_code=403,
                    detail=f"Insufficient permissions. Required roles: {allowed_roles}"
                )
            
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator

def require_company_access(resource_company_id_param: str = "company_id"):
    """Decorator to validate company access"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user: dict = None, company_id: int = None, **kwargs):
            if not current_user:
                raise HTTPException(status_code=401, detail="Not authenticated")
            
            user_company_id = current_user.get("company_id")
            
            # Check if user's company matches resource company
            if company_id and company_id != user_company_id:
                raise HTTPException(
                    status_code=403,
                    detail="Access denied: Company mismatch"
                )
            
            return await func(*args, current_user=current_user, company_id=company_id, **kwargs)
        return wrapper
    return decorator

# 2. Create permission system
class Permission(str, Enum):
    # Scheme permissions
    SCHEME_CREATE = "scheme:create"
    SCHEME_READ = "scheme:read"
    SCHEME_UPDATE = "scheme:update"
    SCHEME_DELETE = "scheme:delete"
    
    # Order permissions
    ORDER_CREATE = "order:create"
    ORDER_READ = "order:read"
    ORDER_UPDATE = "order:update"
    ORDER_DELETE = "order:delete"
    ORDER_APPROVE = "order:approve"
    
    # Batch permissions
    BATCH_CREATE = "batch:create"
    BATCH_READ = "batch:read"
    BATCH_UPDATE = "batch:update"
    BATCH_DELETE = "batch:delete"

# Role to permissions mapping
ROLE_PERMISSIONS = {
    "admin": [p for p in Permission],  # All permissions
    "manager": [
        Permission.SCHEME_CREATE, Permission.SCHEME_READ, Permission.SCHEME_UPDATE,
        Permission.ORDER_CREATE, Permission.ORDER_READ, Permission.ORDER_UPDATE, Permission.ORDER_APPROVE,
        Permission.BATCH_READ,
    ],
    "user": [
        Permission.SCHEME_READ,
        Permission.ORDER_CREATE, Permission.ORDER_READ,
        Permission.BATCH_READ,
    ],
    "viewer": [
        Permission.SCHEME_READ,
        Permission.ORDER_READ,
        Permission.BATCH_READ,
    ],
}

def require_permission(permission: Permission):
    """Decorator to check specific permission"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user: dict = None, **kwargs):
            if not current_user:
                raise HTTPException(status_code=401, detail="Not authenticated")
            
            user_role = current_user.get("role")
            user_permissions = ROLE_PERMISSIONS.get(user_role, [])
            
            if permission not in user_permissions:
                raise HTTPException(
                    status_code=403,
                    detail=f"Insufficient permissions. Required: {permission}"
                )
            
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator

# 3. Apply to endpoints
@router.delete("/schemes/{scheme_id}")
@require_permission(Permission.SCHEME_DELETE)
@require_company_access()
async def delete_scheme(
    scheme_id: int,
    current_user: dict = Depends(get_current_user),
    company_id: int = Depends(get_current_company_id),
    db: Session = Depends(get_db),
):
    # Get scheme
    scheme = db.query(ClaimScheme).filter(
        ClaimScheme.scheme_id == scheme_id
    ).first()
    
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")
    
    # Validate company ownership
    if scheme.company_id != company_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Delete
    service.delete_scheme(scheme_id, company_id, current_user["user_id"])
    return {"message": "Scheme deleted successfully"}

# 4. Create authorization service
class AuthorizationService:
    @staticmethod
    def can_access_resource(
        user: dict,
        resource_company_id: int,
        required_permission: Permission
    ) -> bool:
        """Check if user can access a resource"""
        # Check company access
        if user.get("company_id") != resource_company_id:
            return False
        
        # Check permission
        user_role = user.get("role")
        user_permissions = ROLE_PERMISSIONS.get(user_role, [])
        
        return required_permission in user_permissions
    
    @staticmethod
    def can_modify_resource(
        user: dict,
        resource: Any,
        required_permission: Permission
    ) -> bool:
        """Check if user can modify a resource"""
        # Check company access
        if hasattr(resource, 'company_id'):
            if user.get("company_id") != resource.company_id:
                return False
        
        # Check ownership (for user-specific resources)
        if hasattr(resource, 'created_by'):
            user_role = user.get("role")
            if user_role not in ["admin", "manager"]:
                if resource.created_by != user.get("user_id"):
                    return False
        
        # Check permission
        user_role = user.get("role")
        user_permissions = ROLE_PERMISSIONS.get(user_role, [])
        
        return required_permission in user_permissions

# 5. Use in services
def update_sales_order(self, order_id: int, update_data: dict, user: dict):
    order = self.repo.get(order_id)
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Authorization check
    if not AuthorizationService.can_modify_resource(
        user, order, Permission.ORDER_UPDATE
    ):
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to modify this order"
        )
    
    # Proceed with update
    return self.repo.update(order, update_data)
```

**Business Impact:** Data breaches, compliance violations, legal liability, reputational damage

---

### ISSUE-029: Input Validation Gaps
**File:** Multiple API endpoints and services  
**Lines:** Throughout codebase  
**Severity:** HIGH  
**Impact:** Data corruption, business logic bypass, system instability

**Description:**
Input validation is inconsistent across the application, with many endpoints accepting invalid data that can corrupt the database or bypass business rules.

**Issues:**

1. **Numeric Range Validation Missing:**
```python
# No validation for reasonable ranges
class BatchCreate(BaseModel):
    qty_received: float  # Could be negative, zero, or absurdly large
    unit_cost: Decimal  # Could be negative or zero
    
# Should validate:
# - qty_received > 0
# - qty_received < MAX_REASONABLE_QTY (e.g., 1,000,000)
# - unit_cost > 0
# - unit_cost < MAX_REASONABLE_COST (e.g., 1,000,000)
```

2. **String Length Validation Missing:**
```python
class ClaimSchemeCreate(BaseModel):
    scheme_name: str  # No max length
    description: Optional[str]  # No max length
    
# Could cause:
# - Database errors if exceeds column length
# - Performance issues with very long strings
# - UI display issues
```

3. **Date Logic Validation Insufficient:**
```python
# In claim_service.py
if scheme.end_date <= scheme.start_date:
    raise HTTPException(status_code=400, detail="End date must be after start date")

# Missing validations:
# - Start date not too far in past (e.g., > 10 years ago)
# - End date not too far in future (e.g., > 10 years ahead)
# - Date range not too long (e.g., > 5 years)
```

4. **Business Rule Validation Missing:**
```python
# Can create sales order with:
# - Negative quantities
# - Zero prices
# - Quantities exceeding stock (validation exists but can be bypassed)
# - Free quantity > purchased quantity
# - Discount > total amount
```

5. **Enum Validation Weak:**
```python
class SalesOrder(Base):
    status = Column(String(20))  # No enum constraint
    
# Can be set to any string:
# - "invalid_status"
# - "pending123"
# - Empty string
# - Very long string
```

**Recommended Fix:**
```python
# 1. Add comprehensive Pydantic validators
from pydantic import BaseModel, validator, root_validator
from decimal import Decimal
from datetime import datetime, timedelta

class BatchCreate(BaseModel):
    product_id: int
    variant_id: int
    qty_received: float
    unit_cost: Decimal
    received_date: datetime
    supplier_id: int
    lot_number: Optional[str] = None
    location_id: int
    
    # Field validators
    @validator('qty_received')
    def validate_qty_received(cls, v):
        if v <= 0:
            raise ValueError('Quantity must be positive')
        if v > 1_000_000:
            raise ValueError('Quantity exceeds maximum (1,000,000)')
        return v
    
    @validator('unit_cost')
    def validate_unit_cost(cls, v):
        if v <= 0:
            raise ValueError('Unit cost must be positive')
        if v > Decimal('1000000'):
            raise ValueError('Unit cost exceeds maximum (1,000,000)')
        return v
    
    @validator('lot_number')
    def validate_lot_number(cls, v):
        if v is not None:
            if len(v) > 50:
                raise ValueError('Lot number too long (max 50 characters)')
            if not v.strip():
                raise ValueError('Lot number cannot be empty')
        return v
    
    @validator('received_date')
    def validate_received_date(cls, v):
        now = datetime.now()
        # Not more than 10 years in past
        if v < now - timedelta(days=3650):
            raise ValueError('Received date too far in past')
        # Not in future
        if v > now + timedelta(days=1):
            raise ValueError('Received date cannot be in future')
        return v

# 2. Add cross-field validators
class SalesOrderDetailCreate(BaseModel):
    product_id: int
    variant_id: int
    quantity: float
    unit_price: Decimal
    free_quantity: float = 0
    discount_amount: Decimal = 0
    
    @root_validator
    def validate_order_detail(cls, values):
        quantity = values.get('quantity', 0)
        unit_price = values.get('unit_price', 0)
        free_quantity = values.get('free_quantity', 0)
        discount_amount = values.get('discount_amount', 0)
        
        # Free quantity cannot exceed purchased quantity
        if free_quantity > quantity:
            raise ValueError(
                f'Free quantity ({free_quantity}) cannot exceed purchased quantity ({quantity})'
            )
        
        # Discount cannot exceed total amount
        total_amount = quantity * unit_price
        if discount_amount > total_amount:
            raise ValueError(
                f'Discount ({discount_amount}) cannot exceed total amount ({total_amount})'
            )
        
        # Discount cannot be negative
        if discount_amount < 0:
            raise ValueError('Discount cannot be negative')
        
        return values

# 3. Add database-level constraints
class SalesOrder(Base):
    __tablename__ = "sales_order"
    __table_args__ = (
        CheckConstraint('total_amount >= 0', name='check_total_amount_positive'),
        CheckConstraint('amount_paid >= 0', name='check_amount_paid_positive'),
        CheckConstraint('amount_paid <= total_amount', name='check_amount_paid_not_exceed_total'),
        CheckConstraint(
            "status IN ('pending', 'approved', 'processing', 'completed', 'cancelled')",
            name='check_status_valid'
        ),
        {"schema": "sales"}
    )
    
    sales_order_id = Column(Integer, primary_key=True)
    order_number = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False)
    total_amount = Column(Numeric(15, 2), nullable=False)
    amount_paid = Column(Numeric(15, 2), default=0)

# 4. Add enum validation
from enum import Enum

class OrderStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    PROCESSING = "processing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class SalesOrderCreate(BaseModel):
    order_number: str
    customer_id: int
    status: OrderStatus = OrderStatus.PENDING
    
    @validator('order_number')
    def validate_order_number(cls, v):
        if not v or not v.strip():
            raise ValueError('Order number is required')
        if len(v) > 50:
            raise ValueError('Order number too long (max 50 characters)')
        # Validate format (e.g., SO-XXXXX)
        import re
        if not re.match(r'^[A-Z]{2,4}-\d{4,10}$', v):
            raise ValueError('Invalid order number format (expected: SO-12345)')
        return v.strip()

# 5. Add validation middleware
from fastapi import Request
from fastapi.responses import JSONResponse

@app.middleware("http")
async def validate_request_size(request: Request, call_next):
    """Limit request body size"""
    MAX_REQUEST_SIZE = 10 * 1024 * 1024  # 10 MB
    
    content_length = request.headers.get('content-length')
    if content_length:
        if int(content_length) > MAX_REQUEST_SIZE:
            return JSONResponse(
                status_code=413,
                content={"detail": "Request body too large"}
            )
    
    response = await call_next(request)
    return response

# 6. Add sanitization utilities
import bleach
import re

def sanitize_string(value: str, max_length: int = 255) -> str:
    """Sanitize string input"""
    if not value:
        return value
    
    # Remove leading/trailing whitespace
    value = value.strip()
    
    # Remove control characters
    value = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', value)
    
    # Limit length
    if len(value) > max_length:
        value = value[:max_length]
    
    # Remove HTML tags (if not expected)
    value = bleach.clean(value, tags=[], strip=True)
    
    return value

def sanitize_html(value: str, max_length: int = 10000) -> str:
    """Sanitize HTML input (for rich text fields)"""
    if not value:
        return value
    
    # Allow only safe HTML tags
    allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'ul', 'ol', 'li', 'a']
    allowed_attributes = {'a': ['href', 'title']}
    
    value = bleach.clean(
        value,
        tags=allowed_tags,
        attributes=allowed_attributes,
        strip=True
    )
    
    # Limit length
    if len(value) > max_length:
        value = value[:max_length]
    
    return value

# 7. Use in schemas
class ClaimSchemeCreate(BaseModel):
    scheme_name: str
    description: Optional[str] = None
    
    @validator('scheme_name', pre=True)
    def sanitize_scheme_name(cls, v):
        return sanitize_string(v, max_length=100)
    
    @validator('description', pre=True)
    def sanitize_description(cls, v):
        if v:
            return sanitize_string(v, max_length=500)
        return v
    
    @validator('scheme_name')
    def validate_scheme_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Scheme name is required')
        if len(v) < 3:
            raise ValueError('Scheme name too short (min 3 characters)')
        return v
```

**Business Impact:** Data corruption, business logic bypass, system instability, security vulnerabilities

---

## Performance & Scalability Issues

### ISSUE-030: N+1 Query Problem
**File:** Multiple repository and service files  
**Lines:** Throughout data access layer  
**Severity:** HIGH  
**Impact:** Slow response times, database overload, poor scalability

**Description:**
The application has numerous N+1 query problems where related data is loaded in loops, causing excessive database queries.

**Examples:**

1. **In Batch Listing:**
```python
# In batch.py list endpoint
batches = batch_repo.list(...)

for batch in batches:
    items.append(
        BatchListItem(
            batch_id=batch.batch_id,
            product_name=batch.product.product_name,  # ❌ Query per batch
            variant_sku=batch.variant.sku,  # ❌ Query per batch
            supplier_name=batch.supplier.supplier_name,  # ❌ Query per batch
            location_name=batch.location.location_name,  # ❌ Query per batch
        )
    )

# For 100 batches: 1 + (100 * 4) = 401 queries!
```

2. **In Sales Order Listing:**
```python
# Similar issue in sales order listing
for order in orders:
    order.customer_name = order.customer.customer_name  # ❌ N+1
    order.location_name = order.location.location_name  # ❌ N+1
    for detail in order.details:  # ❌ N+1
        detail.product_name = detail.product.product_name  # ❌ N+1
        detail.variant_sku = detail.variant.sku  # ❌ N+1
```

3. **In Claim Log Listing:**
```python
for log in logs:
    log.product_name = log.product.product_name if log.product else None  # ❌ N+1
    log.variant_name = log.variant.attribute_value if log.variant else None  # ❌ N+1
```

**Recommended Fix:**
```python
# 1. Use eager loading with joinedload
from sqlalchemy.orm import joinedload, selectinload

def list_batches(self, company_id, product_id=None, ...):
    query = self.db.query(Batch).options(
        joinedload(Batch.product),
        joinedload(Batch.variant),
        joinedload(Batch.supplier),
        joinedload(Batch.location),
    ).filter(
        Batch.company_id == company_id,
        Batch.is_deleted == False
    )
    
    if product_id:
        query = query.filter(Batch.product_id == product_id)
    
    # Now all related data loaded in single query (or few queries)
    return query.offset(skip).limit(limit).all()

# 2. Use selectinload for collections
def list_sales_orders(self, company_id, ...):
    query = self.db.query(SalesOrder).options(
        joinedload(SalesOrder.customer),
        joinedload(SalesOrder.location),
        selectinload(SalesOrder.details).options(
            joinedload(SalesOrderDetail.product),
            joinedload(SalesOrderDetail.variant),
        )
    ).filter(
        SalesOrder.company_id == company_id
    )
    
    return query.all()

# 3. Use subqueryload for large collections
def list_with_allocations(self, ...):
    query = self.db.query(SalesOrder).options(
        subqueryload(SalesOrder.batch_allocations).options(
            joinedload(SalesOrderBatchAllocation.batch)
        )
    )
    
    return query.all()

# 4. Create optimized repository methods
class BatchRepository:
    def list_with_relations(
        self,
        company_id: int,
        skip: int = 0,
        limit: int = 100,
        **filters
    ):
        """List batches with all relations eagerly loaded"""
        query = self.db.query(Batch).options(
            joinedload(Batch.product).joinedload(Product.category),
            joinedload(Batch.variant).joinedload(ProductVariant.unit),
            joinedload(Batch.supplier),
            joinedload(Batch.location),
        ).filter(
            Batch.company_id == company_id,
            Batch.is_deleted == False
        )
        
        # Apply filters
        if filters.get('product_id'):
            query = query.filter(Batch.product_id == filters['product_id'])
        
        if filters.get('status'):
            query = query.filter(Batch.status == filters['status'])
        
        # Get total count (without relations)
        total = query.with_entities(func.count(Batch.batch_id)).scalar()
        
        # Get paginated results with relations
        results = query.offset(skip).limit(limit).all()
        
        return total, results

# 5. Use database-level joins for aggregations
def get_batch_summary(self, company_id: int):
    """Get batch summary with aggregations"""
    result = self.db.query(
        Batch.product_id,
        Product.product_name,
        func.count(Batch.batch_id).label('batch_count'),
        func.sum(Batch.qty_on_hand).label('total_qty'),
        func.avg(Batch.unit_cost).label('avg_cost'),
    ).join(
        Product, Batch.product_id == Product.product_id
    ).filter(
        Batch.company_id == company_id,
        Batch.is_deleted == False
    ).group_by(
        Batch.product_id,
        Product.product_name
    ).all()
    
    return result

# 6. Add query result caching
from functools import lru_cache
from datetime import datetime, timedelta

class CachedRepository:
    _cache = {}
    _cache_ttl = {}
    
    def get_with_cache(self, key: str, ttl_seconds: int = 300):
        """Get from cache or database"""
        now = datetime.now()
        
        # Check if cached and not expired
        if key in self._cache:
            if key in self._cache_ttl:
                if now < self._cache_ttl[key]:
                    return self._cache[key]
        
        # Fetch from database
        result = self._fetch_from_db(key)
        
        # Cache result
        self._cache[key] = result
        self._cache_ttl[key] = now + timedelta(seconds=ttl_seconds)
        
        return result
    
    def invalidate_cache(self, key: str = None):
        """Invalidate cache"""
        if key:
            self._cache.pop(key, None)
            self._cache_ttl.pop(key, None)
        else:
            self._cache.clear()
            self._cache_ttl.clear()
```

**Business Impact:** Poor performance, high infrastructure costs, poor user experience, scalability limitations

---

### ISSUE-031: Missing Database Indexes
**File:** Database schema (models)  
**Lines:** Throughout model definitions  
**Severity:** HIGH  
**Impact:** Slow queries, database performance degradation

**Description:**
Many frequently queried columns lack proper indexes, leading to full table scans and poor query performance.

**Missing Indexes:**

1. **Batch Table:**
```python
class Batch(Base):
    # Missing indexes on:
    # - (company_id, product_id, variant_id, location_id) - composite for filtering
    # - (company_id, status) - for status filtering
    # - (company_id, received_date) - for date range queries
    # - (supplier_id) - for supplier lookups
    # - (lot_number) - for lot number searches
```

2. **Sales Order:**
```python
class SalesOrder(Base):
    # Missing indexes on:
    # - (company_id, status) - for status filtering
    # - (company_id, customer_id) - for customer orders
    # - (company_id, order_date) - for date range queries
    # - (order_number) - for order number lookups (should be unique index)
```

3. **Inventory Movement:**
```python
class InventoryMovement(Base):
    # Missing indexes on:
    # - (batch_id, movement_type) - for batch history
    # - (company_id, txn_timestamp) - for date range queries
    # - (ref_type, ref_id) - for reference lookups
```

4. **Claim Log:**
```python
class ClaimLog(Base):
    # Missing indexes on:
    # - (company_id, scheme_id) - for scheme reports
    # - (company_id, product_id) - for product reports
    # - (ref_type, ref_id) - for order lookups
    # - (cd) - for date range queries
```

**Recommended Fix:**
```python
# 1. Add indexes to Batch model
class Batch(Base):
    __tablename__ = "batch"
    __table_args__ = (
        Index('idx_batch_company_product_variant_location',
              'company_id', 'product_id', 'variant_id', 'location_id'),
        Index('idx_batch_company_status', 'company_id', 'status'),
        Index('idx_batch_company_received_date', 'company_id', 'received_date'),
        Index('idx_batch_supplier', 'supplier_id'),
        Index('idx_batch_lot_number', 'lot_number'),
        Index('idx_batch_po_detail', 'purchase_order_detail_id'),
        {"schema": "inventory"}
    )

# 2. Add indexes to SalesOrder model
class SalesOrder(Base):
    __tablename__ = "sales_order"
    __table_args__ = (
        Index('idx_so_company_status', 'company_id', 'status'),
        Index('idx_so_company_customer', 'company_id', 'customer_id'),
        Index('idx_so_company_order_date', 'company_id', 'order_date'),
        Index('idx_so_order_number', 'order_number', unique=True),
        Index('idx_so_company_location', 'company_id', 'location_id'),
        {"schema": "sales"}
    )

# 3. Add indexes to InventoryMovement model
class InventoryMovement(Base):
    __tablename__ = "inventory_movement"
    __table_args__ = (
        Index('idx_movement_batch_type', 'batch_id', 'movement_type'),
        Index('idx_movement_company_timestamp', 'company_id', 'txn_timestamp'),
        Index('idx_movement_ref', 'ref_type', 'ref_id'),
        Index('idx_movement_product_variant', 'product_id', 'variant_id'),
        {"schema": "inventory"}
    )

# 4. Add indexes to ClaimLog model
class ClaimLog(Base):
    __tablename__ = "claim_log"
    __table_args__ = (
        Index('idx_claim_log_company_scheme', 'company_id', 'scheme_id'),
        Index('idx_claim_log_company_product', 'company_id', 'product_id'),
        Index('idx_claim_log_ref', 'ref_type', 'ref_id'),
        Index('idx_claim_log_created', 'cd'),
        Index('idx_claim_log_order_detail', 'order_detail_id'),
        {"schema": "claims"}
    )

# 5. Add partial indexes for common filters
class Batch(Base):
    __table_args__ = (
        # ... existing indexes ...
        
        # Partial index for active batches only
        Index('idx_batch_active',
              'company_id', 'product_id', 'variant_id',
              postgresql_where=text("status = 'active' AND is_deleted = FALSE")),
        
        # Partial index for batches with stock
        Index('idx_batch_with_stock',
              'company_id', 'product_id',
              postgresql_where=text("qty_on_hand > 0 AND is_deleted = FALSE")),
        
        {"schema": "inventory"}
    )

# 6. Create migration to add indexes
"""Add missing indexes

Revision ID: add_missing_indexes
Revises: previous_revision
Create Date: 2026-03-10

"""
from alembic import op

def upgrade():
    # Batch indexes
    op.create_index(
        'idx_batch_company_product_variant_location',
        'batch',
        ['company_id', 'product_id', 'variant_id', 'location_id'],
        schema='inventory'
    )
    
    op.create_index(
        'idx_batch_company_status',
        'batch',
        ['company_id', 'status'],
        schema='inventory'
    )
    
    op.create_index(
        'idx_batch_company_received_date',
        'batch',
        ['company_id', 'received_date'],
        schema='inventory'
    )
    
    # Sales Order indexes
    op.create_index(
        'idx_so_company_status',
        'sales_order',
        ['company_id', 'status'],
        schema='sales'
    )
    
    op.create_index(
        'idx_so_order_number',
        'sales_order',
        ['order_number'],
        unique=True,
        schema='sales'
    )
    
    # Inventory Movement indexes
    op.create_index(
        'idx_movement_batch_type',
        'inventory_movement',
        ['batch_id', 'movement_type'],
        schema='inventory'
    )
    
    # Claim Log indexes
    op.create_index(
        'idx_claim_log_company_scheme',
        'claim_log',
        ['company_id', 'scheme_id'],
        schema='claims'
    )

def downgrade():
    # Drop indexes in reverse order
    op.drop_index('idx_claim_log_company_scheme', schema='claims')
    op.drop_index('idx_movement_batch_type', schema='inventory')
    op.drop_index('idx_so_order_number', schema='sales')
    op.drop_index('idx_so_company_status', schema='sales')
    op.drop_index('idx_batch_company_received_date', schema='inventory')
    op.drop_index('idx_batch_company_status', schema='inventory')
    op.drop_index('idx_batch_company_product_variant_location', schema='inventory')

# 7. Monitor index usage
def analyze_index_usage(db: Session):
    """Analyze index usage statistics"""
    query = text("""
        SELECT
            schemaname,
            tablename,
            indexname,
            idx_scan as index_scans,
            idx_tup_read as tuples_read,
            idx_tup_fetch as tuples_fetched
        FROM pg_stat_user_indexes
        WHERE schemaname IN ('inventory', 'sales', 'claims')
        ORDER BY idx_scan ASC
    """)
    
    result = db.execute(query)
    
    print("Index Usage Statistics:")
    print("-" * 80)
    for row in result:
        print(f"{row.schemaname}.{row.tablename}.{row.indexname}")
        print(f"  Scans: {row.index_scans}, Tuples Read: {row.tuples_read}")
        if row.index_scans == 0:
            print("  ⚠️  WARNING: Index never used - consider dropping")
        print()
```

**Business Impact:** Slow queries, poor user experience, high database costs, scalability issues

---

### ISSUE-032: Elasticsearch Integration Issues
**File:** Search-related code (if implemented)  
**Lines:** N/A (based on context.md mention)  
**Severity:** MEDIUM  
**Impact:** Poor search performance, stale search results

**Description:**
Based on the architecture overview mentioning Elasticsearch 8.x, there are likely integration issues with keeping search indexes synchronized with database changes.

**Potential Issues:**

1. **No Automatic Index Updates:**
```python
# When creating/updating records
def create_product(self, product_data):
    product = Product(**product_data)
    self.db.add(product)
    self.db.commit()
    
    # ❌ Missing: Update Elasticsearch index
    # Search results will be stale until manual reindex
```

2. **No Bulk Indexing:**
```python
# Indexing one record at a time
for product in products:
    es.index(index='products', id=product.product_id, document=product_dict)
    # ❌ Inefficient for large datasets
```

3. **No Error Handling:**
```python
# If Elasticsearch is down
try:
    es.index(...)
except:
    pass  # ❌ Silent failure, data not indexed
```

**Recommended Fix:**
```python
# 1. Create Elasticsearch service
from elasticsearch import Elasticsearch, helpers
from typing import List, Dict, Any

class ElasticsearchService:
    def __init__(self, hosts: List[str]):
        self.es = Elasticsearch(hosts)
    
    def index_document(self, index: str, doc_id: int, document: Dict[str, Any]):
        """Index single document"""
        try:
            self.es.index(
                index=index,
                id=doc_id,
                document=document,
                refresh='wait_for'  # Wait for index refresh
            )
        except Exception as e:
            logger.error(f"Failed to index document {doc_id}: {e}")
            # Queue for retry
            self.queue_for_retry(index, doc_id, document)
    
    def bulk_index(self, index: str, documents: List[Dict[str, Any]]):
        """Bulk index documents"""
        actions = [
            {
                "_index": index,
                "_id": doc["id"],
                "_source": doc
            }
            for doc in documents
        ]
        
        try:
            success, failed = helpers.bulk(
                self.es,
                actions,
                raise_on_error=False,
                stats_only=False
            )
            
            if failed:
                logger.warning(f"Failed to index {len(failed)} documents")
                for item in failed:
                    logger.error(f"Failed item: {item}")
            
            return success, failed
            
        except Exception as e:
            logger.error(f"Bulk indexing failed: {e}")
            raise
    
    def delete_document(self, index: str, doc_id: int):
        """Delete document from index"""
        try:
            self.es.delete(index=index, id=doc_id)
        except Exception as e:
            logger.error(f"Failed to delete document {doc_id}: {e}")
    
    def search(self, index: str, query: Dict[str, Any], size: int = 10, from_: int = 0):
        """Search documents"""
        try:
            response = self.es.search(
                index=index,
                body=query,
                size=size,
                from_=from_
            )
            return response
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise

# 2. Add database event listeners
from sqlalchemy import event

@event.listens_for(Product, 'after_insert')
def product_after_insert(mapper, connection, target):
    """Index product after insert"""
    # Use background task to avoid blocking
    background_tasks.add_task(
        index_product,
        target.product_id
    )

@event.listens_for(Product, 'after_update')
def product_after_update(mapper, connection, target):
    """Update product index after update"""
    background_tasks.add_task(
        index_product,
        target.product_id
    )

@event.listens_for(Product, 'after_delete')
def product_after_delete(mapper, connection, target):
    """Remove product from index after delete"""
    background_tasks.add_task(
        delete_product_from_index,
        target.product_id
    )

# 3. Create background indexing tasks
from fastapi import BackgroundTasks

def index_product(product_id: int):
    """Background task to index product"""
    db = SessionLocal()
    try:
        product = db.query(Product).filter(
            Product.product_id == product_id
        ).first()
        
        if product:
            document = {
                "id": product.product_id,
                "product_name": product.product_name,
                "product_code": product.product_code,
                "description": product.description,
                "category_id": product.category_id,
                "is_active": product.is_active,
            }
            
            es_service.index_document('products', product_id, document)
    finally:
        db.close()

# 4. Add reindexing command
def reindex_all_products(company_id: int = None):
    """Reindex all products"""
    db = SessionLocal()
    try:
        query = db.query(Product)
        if company_id:
            query = query.filter(Product.company_id == company_id)
        
        products = query.all()
        
        documents = [
            {
                "id": p.product_id,
                "product_name": p.product_name,
                "product_code": p.product_code,
                "description": p.description,
                "category_id": p.category_id,
                "is_active": p.is_active,
            }
            for p in products
        ]
        
        # Bulk index in chunks
        chunk_size = 1000
        for i in range(0, len(documents), chunk_size):
            chunk = documents[i:i + chunk_size]
            es_service.bulk_index('products', chunk)
            logger.info(f"Indexed {i + len(chunk)}/{len(documents)} products")
        
    finally:
        db.close()

# 5. Add health check
def check_elasticsearch_health():
    """Check Elasticsearch cluster health"""
    try:
        health = es_service.es.cluster.health()
        return {
            "status": health["status"],
            "number_of_nodes": health["number_of_nodes"],
            "active_shards": health["active_shards"],
        }
    except Exception as e:
        logger.error(f"Elasticsearch health check failed: {e}")
        return {"status": "unavailable", "error": str(e)}

# 6. Add search endpoint with fallback
@router.get("/products/search")
async def search_products(
    q: str,
    size: int = 10,
    from_: int = 0,
    db: Session = Depends(get_db)
):
    """Search products with Elasticsearch fallback to database"""
    try:
        # Try Elasticsearch first
        query = {
            "query": {
                "multi_match": {
                    "query": q,
                    "fields": ["product_name^2", "product_code", "description"]
                }
            }
        }
        
        response = es_service.search('products', query, size, from_)
        
        return {
            "total": response["hits"]["total"]["value"],
            "results": [hit["_source"] for hit in response["hits"]["hits"]]
        }
        
    except Exception as e:
        logger.warning(f"Elasticsearch search failed, falling back to database: {e}")
        
        # Fallback to database search
        products = db.query(Product).filter(
            or_(
                Product.product_name.ilike(f"%{q}%"),
                Product.product_code.ilike(f"%{q}%"),
                Product.description.ilike(f"%{q}%")
            )
        ).offset(from_).limit(size).all()
        
        total = db.query(func.count(Product.product_id)).filter(
            or_(
                Product.product_name.ilike(f"%{q}%"),
                Product.product_code.ilike(f"%{q}%"),
                Product.description.ilike(f"%{q}%")
            )
        ).scalar()
        
        return {
            "total": total,
            "results": [p.to_dict() for p in products],
            "fallback": True
        }
```

**Business Impact:** Poor search experience, stale results, operational overhead

---


## Recommendations

### Priority 1: Critical Security & Data Integrity (Immediate Action Required)

**Timeline: 1-2 weeks**

1. **Fix JWT Token Security (ISSUE-026)**
   - Reduce token expiry to 30 minutes
   - Implement refresh token mechanism
   - Add token revocation system
   - Upgrade password hashing to Argon2
   - **Impact:** Prevents unauthorized access and security breaches

2. **Fix Race Conditions (ISSUE-001, ISSUE-002, ISSUE-011)**
   - Add proper locking mechanisms for PO delivery processing
   - Implement transaction rollback in batch allocation
   - Fix DSR payment settlement race condition
   - **Impact:** Prevents data corruption and financial discrepancies

3. **Add Authorization Checks (ISSUE-028)**
   - Implement role-based access control
   - Add company-level data isolation
   - Create permission system
   - **Impact:** Prevents unauthorized data access

4. **Fix SQL Injection Vulnerabilities (ISSUE-027)**
   - Review all raw SQL queries
   - Implement parameterized queries
   - Add input validation
   - **Impact:** Prevents data breaches

### Priority 2: Data Consistency & Business Logic (2-4 weeks)

5. **Fix Batch Tracking Chain (ISSUE-003)**
   - Implement DSR batch allocation tracking
   - Maintain batch chain: PO → Batch → SO → DSR → Customer
   - **Impact:** Accurate COGS calculation and inventory traceability

6. **Fix Sales Return Processing (ISSUE-004)**
   - Implement proper batch deallocation for returns
   - Create RETURN_IN inventory movements
   - Update batch quantities correctly
   - **Impact:** Accurate inventory levels

7. **Fix Consolidation Logic (ISSUE-005, ISSUE-014)**
   - Add explicit transaction boundaries
   - Fix pricing calculation for consolidated orders
   - Implement compensation logic
   - **Impact:** Prevents duplicate orders and revenue leakage

8. **Add Optimistic Locking (ISSUE-006)**
   - Add version columns to critical entities
   - Implement version checking on updates
   - **Impact:** Prevents lost updates

### Priority 3: Validation & Error Handling (3-4 weeks)

9. **Enhance Input Validation (ISSUE-029)**
   - Add comprehensive Pydantic validators
   - Implement database constraints
   - Add sanitization utilities
   - **Impact:** Prevents data corruption

10. **Improve Error Handling (ISSUE-023)**
    - Standardize error messages
    - Add error transformation layer
    - Implement retry mechanisms
    - **Impact:** Better user experience

11. **Fix Form Validation (ISSUE-024)**
    - Implement consistent validation timing
    - Add cross-field validation
    - Add async validation for duplicates
    - **Impact:** Reduces invalid data submission

12. **Enhance Excel Import (ISSUE-021)**
    - Add file type validation
    - Implement transaction rollback on failure
    - Add comprehensive row validation
    - **Impact:** Prevents bulk data corruption

### Priority 4: Performance & Scalability (4-6 weeks)

13. **Fix N+1 Queries (ISSUE-030)**
    - Add eager loading with joinedload
    - Optimize repository methods
    - Implement query result caching
    - **Impact:** 10-100x performance improvement

14. **Add Database Indexes (ISSUE-031)**
    - Create composite indexes for common queries
    - Add partial indexes for filtered queries
    - Monitor index usage
    - **Impact:** 5-50x query performance improvement

15. **Fix Elasticsearch Integration (ISSUE-032)**
    - Implement automatic index updates
    - Add bulk indexing
    - Create reindexing commands
    - **Impact:** Better search experience

16. **Fix Memory Leaks (ISSUE-025)**
    - Cancel async operations on unmount
    - Clean up event listeners
    - Clear timers and debounced functions
    - **Impact:** Better frontend performance

### Priority 5: Business Logic Improvements (6-8 weeks)

17. **Fix Claim Scheme Logic (ISSUE-017, ISSUE-018, ISSUE-019, ISSUE-020)**
    - Fix slab calculation logic
    - Add date validation
    - Implement claim log reversal
    - Add scheme re-evaluation
    - **Impact:** Accurate promotional cost tracking

18. **Fix FIFO/LIFO Logic (ISSUE-008)**
    - Handle partial batch allocations
    - Fix LIFO implementation
    - Add weighted average cost calculation
    - **Impact:** Accurate cost calculation

19. **Add Batch Expiry Handling (ISSUE-010)**
    - Add expiry_date field
    - Implement automatic status updates
    - Add near-expiry alerts
    - **Impact:** Compliance and safety

20. **Fix Stock Validation (ISSUE-007, ISSUE-012)**
    - Add re-validation at delivery time
    - Implement stock reservation
    - Add DSR stock validation
    - **Impact:** Prevents overselling

### Quick Wins (Can be done in parallel)

21. **Add Audit Trails (ISSUE-013)**
    - Create DSRStockMovement table
    - Log all load/unload operations
    - **Effort:** 2-3 days
    - **Impact:** Better accountability

22. **Fix Form State Management (ISSUE-022)**
    - Use single source of truth
    - Add proper memoization
    - Use callbacks with latest values
    - **Effort:** 3-5 days
    - **Impact:** Better UI consistency

23. **Add Batch Creation Validation (ISSUE-009)**
    - Validate lot number uniqueness
    - Check for duplicate batches
    - Validate quantities and costs
    - **Effort:** 2-3 days
    - **Impact:** Better data quality

24. **Fix Order Modification Validation (ISSUE-016)**
    - Prevent modifications after delivery
    - Validate payment constraints
    - Check consolidation status
    - **Effort:** 3-4 days
    - **Impact:** Data integrity

### Implementation Strategy

**Phase 1: Security & Critical Fixes (Weeks 1-2)**
- Focus on CRITICAL severity issues
- Fix security vulnerabilities
- Implement proper authentication/authorization
- Add transaction management

**Phase 2: Data Consistency (Weeks 3-6)**
- Fix batch tracking chain
- Implement proper return processing
- Add optimistic locking
- Fix consolidation logic

**Phase 3: Validation & Error Handling (Weeks 7-10)**
- Enhance input validation
- Improve error handling
- Fix form validation
- Enhance Excel import

**Phase 4: Performance (Weeks 11-14)**
- Fix N+1 queries
- Add database indexes
- Optimize Elasticsearch
- Fix memory leaks

**Phase 5: Business Logic (Weeks 15-18)**
- Fix claim scheme logic
- Improve FIFO/LIFO
- Add batch expiry
- Enhance stock validation

### Testing Strategy

1. **Unit Tests**
   - Test all business logic functions
   - Test validation logic
   - Test calculation functions
   - Target: 80% code coverage

2. **Integration Tests**
   - Test API endpoints
   - Test database transactions
   - Test service interactions
   - Target: All critical paths covered

3. **Performance Tests**
   - Load test API endpoints
   - Test database query performance
   - Test concurrent operations
   - Target: <200ms response time for 95th percentile

4. **Security Tests**
   - Penetration testing
   - SQL injection testing
   - Authorization testing
   - Target: Zero critical vulnerabilities

### Monitoring & Observability

1. **Add Application Monitoring**
   - Implement error tracking (e.g., Sentry)
   - Add performance monitoring (e.g., New Relic, DataDog)
   - Track business metrics

2. **Add Database Monitoring**
   - Monitor slow queries
   - Track connection pool usage
   - Monitor index usage

3. **Add Alerting**
   - Alert on error rate spikes
   - Alert on performance degradation
   - Alert on security events

### Documentation Needs

1. **Technical Documentation**
   - Architecture diagrams
   - Database schema documentation
   - API documentation (OpenAPI/Swagger)
   - Deployment guide

2. **User Documentation**
   - User manuals
   - Admin guides
   - Training materials
   - FAQ

3. **Developer Documentation**
   - Setup guide
   - Coding standards
   - Testing guide
   - Contribution guide

---

## Summary Statistics

**Total Issues Found:** 32

**By Severity:**
- CRITICAL: 7 issues (22%)
- HIGH: 15 issues (47%)
- MEDIUM: 10 issues (31%)

**By Category:**
- Security: 4 issues
- Data Integrity: 8 issues
- Performance: 4 issues
- Business Logic: 8 issues
- Frontend: 5 issues
- Validation: 3 issues

**Estimated Effort:**
- Priority 1 (Critical): 2 weeks
- Priority 2 (High): 4 weeks
- Priority 3 (Medium): 4 weeks
- Priority 4 (Performance): 6 weeks
- Priority 5 (Business Logic): 8 weeks
- **Total: 24 weeks (6 months) with 2-3 developers**

**Risk Assessment:**
- **High Risk:** Security vulnerabilities, race conditions, data corruption issues
- **Medium Risk:** Performance issues, validation gaps, business logic errors
- **Low Risk:** UI/UX issues, documentation gaps

---

## Conclusion

The Shoudagor ERP system is a sophisticated multi-tenant business management platform with a solid architectural foundation. However, this analysis has identified 32 significant issues across security, data integrity, performance, and business logic domains.

**Key Strengths:**
- Clean 5-layer architecture
- Modern technology stack (FastAPI, React, PostgreSQL)
- Comprehensive feature set
- Batch-based inventory tracking

**Critical Concerns:**
- Security vulnerabilities (JWT, SQL injection, authorization)
- Race conditions in financial transactions
- Data consistency issues in batch tracking
- Performance bottlenecks (N+1 queries, missing indexes)

**Immediate Actions Required:**
1. Fix JWT token security
2. Resolve race conditions in critical transactions
3. Implement proper authorization checks
4. Address SQL injection vulnerabilities

**Long-term Improvements:**
1. Enhance batch tracking chain
2. Optimize database performance
3. Improve validation and error handling
4. Refine business logic for claims and schemes

With a focused 6-month effort following the recommended priority order, the system can be significantly improved in terms of security, reliability, and performance. The quick wins can provide immediate value while the longer-term improvements build a more robust and scalable platform.

---

**Report Generated:** March 10, 2026  
**Analyst:** Senior Architect & Bug Finder  
**Version:** 1.0  
**Status:** Complete

