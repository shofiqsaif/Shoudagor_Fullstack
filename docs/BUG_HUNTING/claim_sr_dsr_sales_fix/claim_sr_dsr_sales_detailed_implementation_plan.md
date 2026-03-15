# Claims, SR/SO/DSR, Commission Workflow - Detailed Implementation Plan

**Date:** 2026-03-13  
**Status:** Planned  
**Based on:** `claim_sr_dsr_sales_fix_plan.md`

---

## Executive Summary

This document provides a comprehensive implementation plan for fixing issues across Claims & Schemes, SR Orders, Sales Orders, DSR flows, and Commission handling. The implementation spans database migrations, backend services, and frontend updates.

### Key Goals
1. Persist applied schemes on order details and align evaluation logic
2. Support buy_x_get_y schemes with different free products via separate free lines
3. Ensure stock validation and DSR flows account for free items
4. Fix delivery update/delete handling for free quantities
5. Ensure commissions are recalculated/adjusted on returns with audit trail

---

## Phase 1: Database Schema Changes

### 1.1 Sales Order Detail Changes

**File:** `Shoudagor/app/models/sales.py`

Add new fields to `SalesOrderDetail` model:

```python
# Add after applied_scheme_id field
is_free_item: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)
parent_detail_id: Mapped[Optional[int]] = mapped_column(
    Integer, ForeignKey('sales.sales_order_detail.sales_order_detail_id'),
    nullable=True
)
```

### 1.2 Purchase Order Detail Changes

**File:** `Shoudagor/app/models/procurement.py`

Add new fields to `PurchaseOrderDetail` model:

```python
# Add after applied_scheme_id field
is_free_item: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)
parent_detail_id: Mapped[Optional[int]] = mapped_column(
    Integer, ForeignKey('procurement.purchase_order_detail.purchase_order_detail_id'),
    nullable=True
)
```

### 1.3 Claim Log Changes

**File:** `Shoudagor/app/models/claims.py`

Add fields to `ClaimLog` model:

```python
# Add after given_discount_amount field
free_product_id: Mapped[Optional[int]] = mapped_column(
    Integer, ForeignKey('inventory.product.product_id'), nullable=True
)
free_variant_id: Mapped[Optional[int]] = mapped_column(
    Integer, ForeignKey('inventory.product_variant.product_variant_id'), nullable=True
)
```

### 1.4 SR Order Commission Field

**File:** `Shoudagor/app/models/sales.py`

Add commission persistence to `SR_Order` model:

```python
# Add to SR_Order model after commission_disbursed field
commission_amount: Mapped[Optional[Decimal]] = mapped_column(
    Numeric(18, 4), nullable=True
)
```

### 1.5 Alembic Migration

Create migration file for all schema changes:

```bash
alembic revision --autogenerate -m "add_is_free_item_and_parent_detail_id"
```

---

## Phase 2: Backend - Claims Service Updates

### 2.1 Enhance `evaluate_pre_claim` Return Value

**File:** `Shoudagor/app/services/claims/claim_service.py`

Update the method to return richer results:

```python
def evaluate_pre_claim(
    self, company_id: int, items: List[dict], target_module: str = None
) -> List[dict]:
    """
    Returns items with additional fields:
    - free_quantity: Calculated free quantity
    - discount_amount: Calculated discount
    - applied_scheme_id: The scheme_id applied
    - free_product_id: Product ID for free item (if different)
    - free_variant_id: Variant ID for free item (if different)
    - applied_slab_id: The slab that was applied
    - benefit_type: 'free_quantity' or 'discount'
    - is_free_item_line_needed: Whether a separate line is needed
    """
```

### 2.2 Fix Percentage Rebate Calculation

Update slab calculation logic to use threshold-multiplier:

```python
# Current (WRONG): applies discount to full quantity
discount_amount = applied_slab.discount_percentage / 100 * unit_price * quantity

# Fixed: applies discount based on threshold multiplier
threshold_multiplier = quantity // applied_slab.threshold_qty
if threshold_multiplier > 0:
    discountable_qty = threshold_multiplier * applied_slab.threshold_qty
    discount_amount = (applied_slab.discount_percentage / 100) * unit_price * discountable_qty
```

### 2.3 Add Idempotency to `log_claim_applications`

**File:** `Shoudagor/app/services/claims/claim_service.py`

```python
def log_claim_applications(
    self,
    company_id: int,
    user_id: int,
    ref_id: int,
    ref_type: str,
    evaluated_items: List[dict],
):
    # Check for existing logs before creating new ones
    existing_logs = self.repo.get_logs_by_reference(
        ref_id=ref_id, ref_type=ref_type
    )
    
    existing_detail_ids = {
        (log.order_detail_id, log.scheme_id) 
        for log in existing_logs 
        if log.status == 'active'
    }
    
    # Only create logs for items not already logged
    new_logs = []
    for item in evaluated_items:
        if item.get('free_quantity', 0) > 0 or item.get('discount_amount', 0) > 0:
            key = (item.get('order_detail_id'), item.get('applied_scheme_id'))
            if key not in existing_detail_ids:
                # Create log entry
                new_logs.append(...)
    
    if new_logs:
        self.db.add_all(new_logs)
        self.db.flush()
```

### 2.4 Fix Overlap Validation

**File:** `Shoudagor/app/repositories/claims_repository.py`

Update `find_overlapping_schemes` to consider `applicable_to`:

```python
def find_overlapping_schemes(
    self,
    company_id: int,
    trigger_product_id: int,
    trigger_variant_id: int,
    start_date: datetime,
    end_date: datetime,
    exclude_scheme_id: int = None,
    applicable_to: str = None,  # NEW PARAMETER
):
    query = self.db.query(ClaimScheme).filter(
        ClaimScheme.company_id == company_id,
        ClaimScheme.is_active == True,
        ClaimScheme.trigger_product_id == trigger_product_id,
        # ... date overlap logic
    )
    
    if applicable_to:
        # Allow overlap between purchase-only and sale-only schemes
        query = query.filter(
            or_(
                ClaimScheme.applicable_to == applicable_to,
                ClaimScheme.applicable_to == 'all',
                applicable_to == 'all'
            )
        )
    
    return query.all()
```

---

## Phase 3: Backend - Sales Order Service Updates

### 3.1 Reorder Operations

**File:** `Shoudagor/app/services/sales/sales_order_service.py`

Move scheme evaluation BEFORE stock validation:

```python
async def create_sales_order(self, order_data, user_id, company_id):
    # Step 1: Evaluate schemes FIRST (to get free quantities)
    evaluated_items = claim_service.evaluate_pre_claim(
        company_id, items_to_evaluate, target_module="sale"
    )
    
    # Step 2: Build order details including free lines
    order_details = self._build_order_details(evaluated_items)
    
    # Step 3: NOW validate stock including free quantities
    self._validate_stock_availability(sales_order, company_id)
    
    # Step 4: Create order and log claims
    ...
```

### 3.2 Create Free Lines for buy_x_get_y

**File:** `Shoudagor/app/services/sales/sales_order_service.py`

```python
def _build_order_details(self, evaluated_items):
    """Build order details with separate free lines for different products."""
    details = []
    detail_id_map = {}  # Track created details for parent linking
    
    for item in evaluated_items:
        # Create base detail line
        base_detail = self._create_detail_from_item(item)
        details.append(base_detail)
        self.db.flush()  # Get the ID
        
        detail_id_map[id(item)] = base_detail.sales_order_detail_id
        
        # Check if separate free line is needed
        if item.get('is_free_item_line_needed'):
            free_line = SalesOrderDetail(
                product_id=item['free_product_id'],
                variant_id=item.get('free_variant_id'),
                quantity=item['free_quantity'],
                unit_price=0,  # Free!
                is_free_item=True,
                parent_detail_id=base_detail.sales_order_detail_id,
                applied_scheme_id=item['applied_scheme_id'],
                # ... other fields
            )
            details.append(free_line)
    
    return details
```

### 3.3 Update Total Calculation

Ensure `effective_total_amount` excludes free lines:

```python
@hybrid_property
def effective_total_amount(self):
    return sum(
        d.quantity * d.unit_price 
        for d in self.details 
        if not d.is_free_item  # Exclude free lines
    )
```

---

## Phase 4: Backend - DSR Service Updates

### 4.1 Include Free Items in DSR Assignment

**File:** `Shoudagor/app/services/dsr/dsr_so_assignment_service.py`

```python
def create_assignment(self, assignment_data, user_id, company_id):
    # Include free quantities in stock validation
    for detail in sales_order.details:
        total_required = detail.quantity + detail.free_quantity
        
        # Validate stock for total (billable + free)
        self._validate_stock_available(
            detail.variant_id, detail.product_id, 
            total_required, location_id
        )
```

### 4.2 Include Free Items in DSR Load

```python
def load_so(self, assignment_id, user_id, company_id):
    # Transfer both billable and free quantities to DSR
    for detail in sales_order.details:
        transfer_qty = detail.quantity + detail.free_quantity
        
        # Create DSR stock transfer
        self._transfer_to_dsr_storage(
            detail.product_id, detail.variant_id,
            transfer_qty, detail.location_id
        )
```

### 4.3 Update Delivery to Handle Free Quantities

**File:** `Shoudagor/app/services/sales/sales_order_delivery_detail_service.py`

```python
def create_delivery_detail(self, delivery_data, user_id, company_id):
    # Validate free quantity delivery
    if delivery_data.delivered_free_quantity > 0:
        detail = self._get_order_detail(delivery_data.sales_order_detail_id)
        max_free = detail.free_quantity - detail.shipped_free_quantity
        
        if delivery_data.delivered_free_quantity > max_free:
            raise HTTPException(
                400, 
                f"Cannot deliver more than {max_free} free units"
            )
    
    # Deduct from inventory (both billable + free)
    total_to_deduct = (
        delivery_data.delivered_quantity + 
        delivery_data.delivered_free_quantity
    )
    
    # For DSR orders, adjust DSR inventory
    if assignment and assignment.dsr:
        self._adjust_dsr_inventory(
            variant_id, total_to_deduct, 
            is_deduction=True
        )
```

### 4.4 Fix DSR Collect Payment

**File:** `Shoudagor/app/services/dsr/dsr_so_assignment_service.py`

Replace direct payment updates with service call:

```python
def collect_payment(self, assignment_id, payment_data, user_id, company_id):
    # Use SalesOrderPaymentDetailService instead of direct creation
    payment_service = SalesOrderPaymentDetailService(self.db)
    
    payment_detail = payment_service.create_payment_detail(
        sales_order_id=assignment.sales_order_id,
        payment_date=payment_data.payment_date or datetime.now(),
        amount_paid=payment_data.amount,
        payment_method=payment_data.payment_method,
        transaction_reference=payment_data.transaction_reference,
        cb=user_id,
        mb=user_id,
    )
    
    # Update customer balance through proper service
    customer_service = CustomerService(self.db)
    customer_service.update_balance(
        customer_id=assignment.sales_order.customer_id,
        amount=-payment_data.amount,  # Reduce balance
        company_id=company_id
    )
    
    # Update DSR payment on hand
    if assignment.dsr:
        assignment.dsr.payment_on_hand += payment_data.amount
    
    # Sync SO status
    self._sync_sales_order_status(assignment.sales_order)
```

---

## Phase 5: Backend - Commission Adjustments

### 5.1 Persist Commission on SR Order Ready

**File:** `Shoudagor/app/services/sr/sr_order_service.py`

```python
def mark_sr_order_ready(self, sr_order_id, user_id, company_id):
    sr_order = self.get_sr_order(sr_order_id)
    
    # Calculate commission
    total_commission = 0
    for detail in sr_order.details:
        if detail.shipped_quantity > 0:
            detail_commission = (
                detail.negotiated_price - detail.sale_price
            ) * detail.shipped_quantity
            total_commission += detail_commission
    
    # Persist commission on SR_Order
    sr_order.commission_amount = total_commission
    
    # Add to SR balance (idempotent check)
    sr = sr_order.sales_representative
    if sr_order.commission_disbursed == 'pending':
        sr.commission_amount = (sr.commission_amount or 0) + total_commission
        sr_order.commission_disbursed = 'ready'
    
    self.db.commit()
```

### 5.2 Commission Adjustment on Return/Cancellation

**File:** `Shoudagor/app/services/sales/sales_return_service.py`

```python
def process_return(self, return_data, user_id, company_id):
    # After processing the return...
    
    # Adjust commission if SR order exists
    for detail in return_data.details:
        if detail.sr_order_detail_id:
            sr_order_detail = self._get_sr_order_detail(
                detail.sr_order_detail_id
            )
            sr_order = sr_order_detail.sr_order
            
            # Calculate commission delta
            returned_commission = (
                sr_order_detail.negotiated_price - sr_order_detail.sale_price
            ) * detail.returned_quantity
            
            # Adjust SR balance
            sr = sr_order.sales_representative
            sr.commission_amount -= returned_commission
            
            # If already disbursed, create negative disbursement
            if sr_order.commission_disbursed == 'disbursed':
                self._create_negative_disbursement(
                    sr_id=sr.sr_id,
                    amount=returned_commission,
                    reason=f"Return adjustment for SR Order {sr_order.order_number}",
                    user_id=user_id,
                    company_id=company_id
                )
```

### 5.3 Negative Disbursement Creation

```python
def _create_negative_disbursement(
    self, sr_id, amount, reason, user_id, company_id
):
    negative_disbursement = SRDisbursement(
        sr_id=sr_id,
        disbursement_amount=-abs(amount),  # Negative!
        disbursement_date=datetime.now(),
        disbursement_method='adjustment',
        remarks=reason,
        cb=user_id,
        mb=user_id,
        company_id=company_id,
    )
    self.db.add(negative_disbursement)
    
    # SR balance already adjusted above
    # This record provides audit trail
```

---

## Phase 6: Backend - Schema Updates

### 6.1 Sales Order Detail Schemas

**File:** `Shoudagor/app/schemas/sales/sales_order_detail.py`

```python
class SalesOrderDetailBase(BaseModel):
    # ... existing fields ...
    
    # NEW FIELDS
    is_free_item: bool = Field(False, description="Whether this is a free item line")
    parent_detail_id: Optional[int] = Field(
        None, description="Link to base detail for free items"
    )
```

### 6.2 Purchase Order Detail Schemas

**File:** `Shoudagor/app/schemas/procurement/purchase_order.py`

```python
class PurchaseOrderDetailBase(BaseModel):
    # ... existing fields ...
    
    # NEW FIELDS
    is_free_item: bool = Field(False, description="Whether this is a free item line")
    parent_detail_id: Optional[int] = Field(
        None, description="Link to base detail for free items"
    )
```

### 6.3 Claim Log Schemas

**File:** `Shoudagor/app/schemas/claims.py`

```python
class ClaimLogCreate(BaseModel):
    # ... existing fields ...
    
    # NEW FIELDS
    free_product_id: Optional[int] = None
    free_variant_id: Optional[int] = None
```

---

## Phase 7: Frontend Updates

### 7.1 Update Sales Schema

**File:** `shoudagor_FE/src/lib/schema/sales.ts`

```typescript
export const insertSaleDetailSchema = z.object({
    // ... existing fields ...
    is_free_item: z.boolean().default(false),
    parent_detail_id: z.number().optional().nullable(),
});
```

### 7.2 Update Purchase Schema

**File:** `shoudagor_FE/src/lib/schema/purchases.ts`

```typescript
export const insertPurchaseDetailSchema = z.object({
    // ... existing fields ...
    is_free_item: z.boolean().default(false),
    parent_detail_id: z.number().optional().nullable(),
});
```

### 7.3 SaleForm Updates

**File:** `shoudagor_FE/src/components/forms/SaleForm.tsx`

```typescript
// Display free lines as read-only
const freeLines = details.filter(d => d.is_free_item);
const billableLines = details.filter(d => !d.is_free_item);

// Prevent editing of free line fields
const handleDetailChange = (index, field, value) => {
    const detail = details[index];
    if (detail.is_free_item) return; // Read-only!
    
    // Allow editing for billable lines
    setDetails(prev => /* update logic */);
};

// Total calculation excludes free lines
const totalAmount = billableLines.reduce(
    (sum, d) => sum + (d.quantity * d.unit_price), 0
);
```

### 7.4 UnifiedDeliveryForm Updates

**File:** `shoudagor_FE/src/components/forms/UnifiedDeliveryForm.tsx`

```typescript
// Add delivered_free_quantity field
const deliverySchema = z.object({
    // ... existing fields ...
    delivered_free_quantity: z.number().min(0).default(0),
});

// Validate free quantity not exceeded
const validateDelivery = (detail, delivery) => {
    const maxFree = detail.free_quantity - detail.shipped_free_quantity;
    if (delivery.delivered_free_quantity > maxFree) {
        return `Cannot deliver more than ${maxFree} free units`;
    }
    return null;
};
```

### 7.5 Returns UI Updates

**File:** `shoudagor_FE/src/components/forms/SalesReturnForm.tsx`

```typescript
// Allow returning free items
const returnSchema = z.object({
    // ... existing fields ...
    returned_free_quantity: z.number().min(0).default(0),
});

// Refund totals exclude free items
const calculateRefund = (returns) => {
    return returns
        .filter(r => !r.is_free_item)
        .reduce((sum, r) => sum + (r.returned_quantity * r.unit_price), 0);
};
```

---

## Phase 8: Edge Case Handling

### 8.1 Scheme Applied with -1 (Manual Override)

When `applied_scheme_id = -1`, preserve manual free/discount inputs:

```python
# In evaluate_pre_claim
if item.get('applied_scheme_id') == -1:
    # Skip evaluation, preserve manual values
    item['free_quantity'] = item.get('manual_free_quantity', 0)
    item['discount_amount'] = item.get('manual_discount_amount', 0)
    item['applied_scheme_id'] = None  # No scheme applied
```

### 8.2 Scheme Becomes Inactive

Handle in order creation:

```python
def create_sales_order(self, ...):
    evaluated_items = claim_service.evaluate_pre_claim(...)
    
    for item in evaluated_items:
        if item.get('applied_scheme_id'):
            scheme = self._get_scheme(item['applied_scheme_id'])
            if not scheme or not scheme.is_active:
                # Log warning, preserve manual override values
                logger.warning(
                    f"Scheme {item['applied_scheme_id']} became inactive "
                    f"between evaluation and save"
                )
                # Reset to manual mode
                item['applied_scheme_id'] = -1
```

### 8.3 DSR Unload with Partial Delivery

```python
def unload_so(self, assignment_id, user_id, company_id):
    sales_order = assignment.sales_order
    
    for detail in sales_order.details:
        delivered = detail.shipped_quantity
        ordered = detail.quantity + detail.free_quantity
        remaining = ordered - delivered
        
        # Only return remaining to warehouse
        if remaining > 0:
            self._return_to_warehouse(
                detail.product_id, detail.variant_id,
                remaining, detail.location_id
            )
```

---

## Phase 9: Data Backfill

### 9.1 Sales Order Detail Backfill

```sql
-- Set is_free_item = false for all existing records
UPDATE sales.sales_order_detail 
SET is_free_item = false 
WHERE is_free_item IS NULL;

-- parent_detail_id remains NULL for existing records
```

### 9.2 Purchase Order Detail Backfill

```sql
UPDATE procurement.purchase_order_detail 
SET is_free_item = false 
WHERE is_free_item IS NULL;
```

### 9.3 Claim Log Backfill

For existing buy_x_get_y schemes, set free_product_id/free_variant_id:

```sql
UPDATE inventory.claim_log cl
SET 
    free_product_id = cs.trigger_product_id,
    free_variant_id = cs.trigger_variant_id
FROM inventory.claim_scheme cs
WHERE cl.scheme_id = cs.scheme_id
    AND cs.scheme_type = 'buy_x_get_y'
    AND cl.free_product_id IS NULL;
```

---

## Phase 10: Automated Test Specifications

### 10.1 Claims Tests

**Test: buy_x_get_y with Different Free Product**
```python
def test_buy_x_get_y_creates_separate_free_line():
    """Verify separate free line created when free product differs from trigger."""
    # Create scheme: buy 5 Product A, get 1 Product B free
    # Create order with Product A qty=5
    # Verify: 2 detail lines created (1 billable, 1 free)
    # Verify: free line has is_free_item=True, parent_detail_id set
```

**Test: Percentage Rebate Uses Threshold Multiplier**
```python
def test_percentage_rebate_threshold_multiplier():
    """Verify discount applies only to threshold-multiplied quantity."""
    # Create slab: buy 5, get 10% rebate
    # Order quantity = 12 (2x threshold)
    # Expected discount: 10% * (5*2) * unit_price, NOT 10% * 12 * unit_price
```

**Test: Duplicate Order Does Not Duplicate ClaimLogs**
```python
def test_idempotent_claim_logging():
    """Verify creating same order twice doesn't duplicate logs."""
    # Create order with scheme
    # Verify: 1 claim log created
    # Create same order again (same ref_id)
    # Verify: still 1 claim log, not 2
```

### 10.2 Sales Order Tests

**Test: Stock Validation Includes Free Items**
```python
def test_stock_validation_includes_free_quantity():
    """Verify stock validation accounts for free quantities."""
    # Stock: 10 units
    # Order: 8 units + 4 free (from scheme)
    # Expected: validation FAILS (12 > 10)
```

**Test: Applied Scheme Persisted**
```python
def test_applied_scheme_persisted_on_detail():
    """Verify applied scheme ID is stored on order detail."""
    # Create order with active scheme
    # Verify: detail.applied_scheme_id matches scheme ID
```

### 10.3 DSR Tests

**Test: DSR Load Includes Free Quantities**
```python
def test_dsr_load_includes_free_items():
    """Verify DSR receives free items in load operation."""
    # Order: 10 billable + 3 free
    # After load: DSR inventory should have 13
```

**Test: Delivery Update Adjusts DSR Inventory**
```python
def test_delivery_update_adjusts_dsr_stock():
    """Verify reducing delivery returns stock to DSR."""
    # DSR has 10 units
    # Delivery: 8 units
    # Update delivery to 6 units
    # Expected: DSR has 8 units (2 returned)
```

### 10.4 Commission Tests

**Test: Ready Marks Commission and Updates Balance**
```python
def test_ready_marks_commission_amount():
    """Verify SR order ready stores commission and updates SR balance."""
    # SR order: negotiated=100, sale=80, shipped=10
    # Commission: (100-80)*10 = 200
    # After ready: sr_order.commission_amount = 200
    # SR balance increases by 200
```

**Test: Return After Disbursement Creates Negative Disbursement**
```python
def test_return_after_disbursement_creates_negative():
    """Verify return creates negative disbursement for audit."""
    # SR order ready and disbursed: commission=200
    # Return 50% of quantity
    # Expected: commission reduced by 100
    # Expected: negative SRDisbursement created with amount=-100
```

---

## Implementation Order

### Phase Sequence

| Phase | Description | Dependencies |
|-------|-------------|--------------|
| 1 | Database Migrations | None |
| 2 | Claims Service Updates | Phase 1 |
| 3 | Sales Order Service | Phase 1, 2 |
| 4 | DSR Service Updates | Phase 1, 3 |
| 5 | Commission Adjustments | Phase 1 |
| 6 | Schema Updates | Phase 1 |
| 7 | Frontend Updates | Phase 6 |
| 8 | Edge Cases | Phase 2, 3, 4 |
| 9 | Data Backfill | Phase 1 |
| 10 | Testing | All phases |

### Rollout Checklist

- [ ] Apply database migrations
- [ ] Deploy backend changes
- [ ] Run targeted API tests
- [ ] Deploy frontend updates
- [ ] Monitor claim logs for duplicates
- [ ] Monitor commission balances
- [ ] Verify DSR stock accuracy

---

## Acceptance Criteria

| Area | Criteria |
|------|----------|
| **Claims** | Free items logged with correct product/variant; no duplicate logs; overlap validation respects applicable_to |
| **Sales Orders** | Stock validation includes free items; applied scheme persisted; totals exclude free lines |
| **DSR Flow** | Assignment/load/unload include free items; delivery handles free quantities; payment updates customer balance |
| **Commission** | Ready stores commission_amount; disbursement uses stored amount; return creates negative disbursement |
| **Frontend** | Free lines shown read-only; delivery includes free quantity; totals correct |

---

## Files Impacted Summary

### Backend
- `Shoudagor/app/models/sales.py`
- `Shoudagor/app/models/procurement.py`
- `Shoudagor/app/models/claims.py`
- `Shoudagor/app/services/claims/claim_service.py`
- `Shoudagor/app/services/claims/claim_repository.py`
- `Shoudagor/app/services/sales/sales_order_service.py`
- `Shoudagor/app/services/sales/sales_order_delivery_detail_service.py`
- `Shoudagor/app/services/sales/sales_return_service.py`
- `Shoudagor/app/services/dsr/dsr_so_assignment_service.py`
- `Shoudagor/app/services/sr/sr_order_service.py`
- `Shoudagor/app/schemas/sales/sales_order_detail.py`
- `Shoudagor/app/schemas/procurement/purchase_order.py`
- `Shoudagor/app/schemas/claims.py`

### Frontend
- `shoudagor_FE/src/lib/schema/sales.ts`
- `shoudagor_FE/src/lib/schema/purchases.ts`
- `shoudagor_FE/src/components/forms/SaleForm.tsx`
- `shoudagor_FE/src/components/forms/PurchaseForm.tsx`
- `shoudagor_FE/src/components/forms/UnifiedDeliveryForm.tsx`
- `shoudagor_FE/src/components/forms/SalesReturnForm.tsx`

---

*Document generated for implementation planning. All changes require code review before deployment.*
