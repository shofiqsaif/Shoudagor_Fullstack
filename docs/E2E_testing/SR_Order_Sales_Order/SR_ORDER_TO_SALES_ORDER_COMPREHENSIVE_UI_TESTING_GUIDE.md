# SR Order to Sales Order Lifecycle - Comprehensive UI Testing Guide

## Document Overview
**Purpose**: Complete UI testing guide for SR Order → Sales Order → Commission → DSR Delivery lifecycle  
**Scope**: All edge cases, scenarios, and verification steps from frontend UI  
**Last Updated**: 2025  
**Version**: 1.0

---

## Table of Contents
1. [System Architecture Overview](#system-architecture-overview)
2. [SR Order Creation & Management](#sr-order-creation--management)
3. [SR Order Consolidation to Sales Order](#sr-order-consolidation-to-sales-order)
4. [Sales Order Processing](#sales-order-processing)
5. [Commission Management](#commission-management)
6. [DSR Assignment & Delivery](#dsr-assignment--delivery)
7. [Payment Processing](#payment-processing)
8. [Edge Cases & Error Scenarios](#edge-cases--error-scenarios)
9. [Data Integrity Verification](#data-integrity-verification)

---

## System Architecture Overview

### Key Components
- **SR (Sales Representative)**: Creates orders for customers
- **SR Order**: Initial order created by SR with negotiated prices
- **Sales Order**: Consolidated order from one or more SR Orders
- **Commission**: Calculated based on price difference (Negotiated - Sale Price)
- **DSR (Distributor Sales Representative)**: Delivers orders to customers
- **Payment**: Collection and settlement tracking

### Workflow Stages
```
SR Order Creation → Approval → Consolidation → Sales Order → 
DSR Assignment → Loading → Delivery → Payment → Commission Disbursement
```

---

## SR Order Creation & Management

### Test Case 1.1: Create New SR Order - Basic Flow
**Objective**: Verify SR can create a valid order

**Prerequisites**:
- SR user logged in
- SR has product assignments
- SR has customer assignments
- Products have stock available

**Test Steps**:

1. Navigate to `/sr/orders/new`
2. Select Customer from dropdown (only assigned customers visible)
3. Order Date auto-populated to today
4. Add Order Items:
   - Select Product (only assigned products visible)
   - Select Variant
   - Select Unit of Measure
   - Enter Quantity
   - Verify Sale Price displayed (from SR assignment or product price)
   - Enter Negotiated Price
5. Observe Commission Calculation:
   - Commission = (Negotiated Price - Sale Price) × Quantity
   - Displayed in green if positive, red if negative
6. Add multiple items if needed
7. Review Total Amount and Total Commission
8. Click "Create Order"

**Expected Results**:
- ✅ Order created with unique order number format: `SR-YYYYMMDD-SRID-SEQ`
- ✅ Order status = "pending"
- ✅ Commission status = "pending"
- ✅ Success toast notification displayed
- ✅ Redirected to SR Orders list
- ✅ New order appears in list with correct details

**Verification Steps**:
```sql
-- Verify SR Order created
SELECT sr_order_id, order_number, status, total_amount, commission_disbursed
FROM sales.sr_order 
WHERE order_number = '[ORDER_NUMBER]';

-- Verify SR Order Details
SELECT product_id, variant_id, quantity, negotiated_price, sale_price
FROM sales.sr_order_detail 
WHERE sr_order_id = [SR_ORDER_ID];

-- Verify Commission Calculation
SELECT 
    (negotiated_price - sale_price) * quantity as calculated_commission
FROM sales.sr_order_detail 
WHERE sr_order_id = [SR_ORDER_ID];
```

---

### Test Case 1.2: SR Order with Stock Availability Check
**Objective**: Verify stock availability is displayed and validated

**Test Steps**:
1. Create SR Order
2. Select product/variant
3. Hover over "Available Stock" info icon
4. Verify stock breakdown by location displayed
5. Enter quantity exceeding available stock
6. Attempt to create order

**Expected Results**:
- ✅ Stock breakdown tooltip shows all locations with quantities
- ✅ Total available stock displayed correctly
- ✅ Warning if quantity exceeds available stock
- ✅ Order creation allowed (SR orders don't reserve stock)

**Edge Cases**:
- Zero stock products still selectable
- Negative stock scenarios
- Multi-location stock aggregation

---

### Test Case 1.3: SR Order with Unit of Measure Conversion
**Objective**: Verify UOM conversion affects pricing correctly

**Test Steps**:
1. Create SR Order
2. Select product with multiple UOMs (e.g., Box, Piece)
3. Select base UOM (e.g., Piece) - note price
4. Change to larger UOM (e.g., Box with conversion factor 12)
5. Verify price automatically adjusts
6. Verify commission calculation uses converted price

**Expected Results**:
- ✅ Price = Base Price × Conversion Factor
- ✅ Commission calculated on converted price
- ✅ Quantity stored in selected UOM
- ✅ Backend converts to base UOM for stock operations

**Verification**:
```sql
-- Check UOM conversion
SELECT 
    sod.quantity,
    sod.unit_of_measure_id,
    uom.unit_name,
    uom.conversion_factor,
    sod.negotiated_price,
    sod.sale_price
FROM sales.sr_order_detail sod
JOIN inventory.unit_of_measure uom ON sod.unit_of_measure_id = uom.unit_id
WHERE sr_order_id = [SR_ORDER_ID];
```

---

### Test Case 1.4: SR Order Approval Workflow
**Objective**: Verify order approval process

**Prerequisites**:
- Admin/Manager user logged in
- SR Order in "pending" status

**Test Steps**:
1. Navigate to `/sr/orders` (All SR Orders)
2. Locate pending order
3. Click "Approve" button
4. Verify status changes to "approved"
5. Verify order appears in "Unconsolidated SR Orders"

**Expected Results**:
- ✅ Status updated to "approved"
- ✅ Approve button disabled after approval
- ✅ Order available for consolidation
- ✅ Cannot delete approved orders

**Bulk Approval Test**:
1. Select multiple pending orders (checkbox)
2. Click "Bulk Approve"
3. Verify all selected orders approved
4. Check failed orders report if any

---

### Test Case 1.5: SR Order Commission Status Transitions
**Objective**: Verify commission status lifecycle

**Commission States**:
- `pending` → Initial state
- `Ready` → After SO completion
- `Disbursed` → After payment to SR

**Test Steps**:
1. Create SR Order (status = pending)
2. Approve SR Order (status = pending)
3. Consolidate to Sales Order (status = pending)
4. Complete Sales Order (delivery + payment)
5. Verify commission status = "Ready"
6. Disburse commission
7. Verify commission status = "Disbursed"

**Expected Results**:
- ✅ Commission amount calculated and stored
- ✅ SR commission_amount increased when Ready
- ✅ SR commission_amount decreased when Disbursed
- ✅ Disbursement record created with payment details

---

## SR Order Consolidation to Sales Order

### Test Case 2.1: Validate SR Orders for Consolidation
**Objective**: Verify validation before consolidation

**Test Steps**:
1. Navigate to `/sr/orders/unconsolidated`
2. Select customer with multiple approved SR orders
3. Click "Validate"
4. Select SR orders to consolidate
5. Select storage location
6. Click "Validate Selected Orders"

**Expected Results**:
- ✅ Only approved SR orders shown
- ✅ Stock validation performed for all items
- ✅ Warnings displayed if stock insufficient
- ✅ Validation success message if all checks pass
- ✅ Form expands to show consolidation options

**Validation Checks**:
- All orders belong to same customer
- All orders in "approved" status
- Sufficient stock at selected location
- No duplicate product/variant combinations

---

### Test Case 2.2: Consolidate SR Orders to Sales Order
**Objective**: Create Sales Order from multiple SR Orders

**Test Steps**:
1. After successful validation
2. Enter Expected Shipment Date
3. Add Consolidation Notes (optional)
4. Click "Generate Consolidated Order"

**Expected Results**:
- ✅ Sales Order created with unique order number
- ✅ `is_consolidated` = true
- ✅ `order_source` = "sr_consolidated"
- ✅ `consolidated_sr_orders` JSON contains SR order references
- ✅ All SR order statuses updated to "consolidated"
- ✅ Sales Order details created from SR order details
- ✅ Price differences tracked in `price_difference` field
- ✅ SR information preserved in SO details

**Verification**:
```sql
-- Verify Sales Order created
SELECT 
    sales_order_id,
    order_number,
    is_consolidated,
    order_source,
    consolidated_sr_orders,
    total_amount
FROM sales.sales_order
WHERE order_number = '[SO_NUMBER]';

-- Verify SR Orders updated
SELECT sr_order_id, order_number, status
FROM sales.sr_order
WHERE sr_order_id IN ([SR_ORDER_IDS]);

-- Verify SO Details with SR mapping
SELECT 
    sod.sales_order_detail_id,
    sod.product_id,
    sod.variant_id,
    sod.quantity,
    sod.unit_price,
    sod.negotiated_price,
    sod.price_difference,
    sod.sr_id,
    sod.sr_order_detail_id
FROM sales.sales_order_detail sod
WHERE sales_order_id = [SO_ID];
```

---

### Test Case 2.3: Consolidation with Scheme Application
**Objective**: Verify schemes applied during consolidation

**Test Steps**:
1. Create SR Orders with products eligible for schemes
2. Consolidate orders
3. Verify scheme benefits applied:
   - Free quantities added
   - Discounts applied
   - Separate free item lines created if needed

**Expected Results**:
- ✅ Schemes evaluated before stock validation
- ✅ Free quantities included in stock check
- ✅ `free_quantity` field populated
- ✅ `discount_amount` field populated
- ✅ `applied_scheme_id` stored
- ✅ Separate detail lines for buy_x_get_y with different products

---

## Sales Order Processing

### Test Case 3.1: View Sales Order Details
**Objective**: Verify SO displays all information correctly

**Test Steps**:
1. Navigate to `/sales`
2. Click on order number
3. Verify Order Details dialog shows:
   - Order information
   - Customer details
   - SR information (if consolidated)
   - Line items with quantities
   - Payment status
   - Delivery status
   - Commission status

**Expected Results**:
- ✅ All fields populated correctly
- ✅ SR Orders badge shown if consolidated
- ✅ Effective total calculated correctly (quantity - returned)
- ✅ Free items displayed separately
- ✅ Scheme information visible

---

### Test Case 3.2: Sales Order Status Transitions
**Objective**: Verify unified status updates

**Status Flow**:
```
Open → Partial → Completed
```

**Status Logic**:
- `Open`: Payment=Pending AND Delivery=Pending
- `Partial`: Payment≠Pending OR Delivery≠Pending (but not both complete)
- `Completed`: Payment=Completed AND Delivery=Completed

**Test Steps**:
1. Create Sales Order (status = Open)
2. Make partial payment → status = Partial
3. Make partial delivery → status = Partial
4. Complete payment → status = Partial
5. Complete delivery → status = Completed

**Expected Results**:
- ✅ Status updates automatically
- ✅ Commission status → Ready when Completed
- ✅ SR Order status synced to Completed

---

## Commission Management

### Test Case 4.1: Commission Calculation Verification
**Objective**: Verify commission calculated correctly

**Formula**:
```
Commission = Σ (Negotiated Price - Sale Price) × Shipped Quantity
```

**Test Steps**:
1. Create SR Order with known prices
2. Consolidate to SO
3. Deliver items (shipped_quantity updated)
4. Complete SO
5. Verify commission = Ready
6. Check commission amount

**Expected Results**:
- ✅ Commission calculated only on shipped quantity
- ✅ Returned items excluded from commission
- ✅ Commission amount stored on SR Order
- ✅ SR commission_amount increased

**Verification**:
```sql
-- Calculate expected commission
SELECT 
    sr_order_id,
    SUM((negotiated_price - sale_price) * shipped_quantity) as calculated_commission,
    (SELECT commission_amount FROM sales.sr_order WHERE sr_order_id = sod.sr_order_id) as stored_commission
FROM sales.sr_order_detail sod
WHERE sr_order_id = [SR_ORDER_ID]
GROUP BY sr_order_id;

-- Check SR commission balance
SELECT sr_id, sr_name, commission_amount
FROM sales.sales_representative
WHERE sr_id = [SR_ID];
```

---

### Test Case 4.2: Commission Disbursement - Single Order
**Objective**: Disburse commission for one order

**Test Steps**:
1. Navigate to `/sr/orders/undisbursed`
2. Filter commission_disbursed = "Ready"
3. Select order
4. Click "Disburse"
5. Enter payment method
6. Enter reference number
7. Confirm disbursement

**Expected Results**:
- ✅ Commission status → "Disbursed"
- ✅ SR commission_amount decreased
- ✅ Disbursement record created
- ✅ Payment method and reference stored
- ✅ Cannot disburse again

---

### Test Case 4.3: Bulk Commission Disbursement
**Objective**: Disburse multiple commissions at once

**Test Steps**:
1. Navigate to `/sr/orders/undisbursed`
2. Select multiple Ready orders (checkbox)
3. Click "Disburse (N)" button
4. Review summary by SR
5. Enter payment details
6. Confirm bulk disbursement

**Expected Results**:
- ✅ All selected orders disbursed
- ✅ Summary shows total by SR
- ✅ Failed orders reported with reasons
- ✅ Disbursement records created for each

---

### Test Case 4.4: Bulk Disbursement by Filters
**Objective**: Disburse all matching orders

**Test Steps**:
1. Apply filters (SR, date range, status)
2. Click "Disburse All Ready (N)"
3. Review preview (first 500 orders)
4. Confirm disbursement

**Expected Results**:
- ✅ All matching Ready orders processed
- ✅ Preview shows grouped by SR
- ✅ Total commission calculated
- ✅ Processes beyond preview limit

---

## DSR Assignment & Delivery

### Test Case 5.1: Assign Sales Order to DSR
**Objective**: Create DSR assignment

**Prerequisites**:
- DSR has storage configured
- DSR is active
- SO not already assigned

**Test Steps**:
1. Navigate to `/sales`
2. Select order
3. Click "Add to DSR"
4. Select DSR
5. Add notes
6. Click "Assign"

**Expected Results**:
- ✅ Assignment created
- ✅ SO shows DSR info
- ✅ DSR can see in "My Assignments"
- ✅ Stock validation performed

**Edge Cases**:
- Inactive DSR → Error
- No DSR storage → Error
- SO already loaded → Error
- Insufficient stock → Error

---

### Test Case 5.2: Load Sales Order to DSR Van
**Objective**: Transfer inventory to DSR storage

**Test Steps**:
1. DSR logs in
2. Navigate to `/dsr/my-assignments`
3. Select assigned order
4. Click "Load to Van"
5. Add notes (optional)
6. Confirm load

**Expected Results**:
- ✅ `is_loaded` = true
- ✅ `loaded_by_dsr_id` set
- ✅ `loaded_at` timestamp recorded
- ✅ Inventory transferred:
  - inventory_stock decreased at SO location
  - dsr_inventory_stock increased at DSR storage
- ✅ Batch allocations created if batch tracking enabled
- ✅ Inventory movements logged

**Verification**:
```sql
-- Check SO loaded status
SELECT is_loaded, loaded_by_dsr_id, loaded_at
FROM sales.sales_order
WHERE sales_order_id = [SO_ID];

-- Check inventory transfer
SELECT 
    product_id,
    variant_id,
    quantity
FROM warehouse.dsr_inventory_stock
WHERE dsr_storage_id = [DSR_STORAGE_ID];

-- Check batch allocations
SELECT *
FROM warehouse.dsr_batch_allocation
WHERE sales_order_id = [SO_ID];
```

---

### Test Case 5.3: DSR Delivery Process
**Objective**: Deliver items to customer

**Test Steps**:
1. DSR at customer location
2. Click "Make Delivery"
3. For each item:
   - Enter delivered quantity
   - Enter rejected quantity (if any)
   - Add remarks
4. Select delivery date
5. Click "Process Delivery"

**Expected Results**:
- ✅ Delivery details created
- ✅ `shipped_quantity` updated on SO detail
- ✅ `delivered_quantity` recorded
- ✅ Rejected items processed as returns
- ✅ DSR inventory decreased
- ✅ Batch allocations updated
- ✅ Delivery status updated

---

### Test Case 5.4: DSR Payment Collection
**Objective**: Collect payment from customer

**Test Steps**:
1. Click "Collect Payment"
2. Enter amount
3. Select payment method
4. Enter transaction reference
5. Add notes
6. Click "Collect"

**Expected Results**:
- ✅ Payment detail created
- ✅ SO `amount_paid` increased
- ✅ Customer balance decreased
- ✅ DSR `payment_on_hand` increased
- ✅ Payment status updated

---

### Test Case 5.5: Unload Sales Order from DSR Van
**Objective**: Return undelivered items to warehouse

**Test Steps**:
1. Select loaded order
2. Click "Unload from Van"
3. Select return location (optional)
4. Add notes
5. Confirm unload

**Expected Results**:
- ✅ `is_loaded` = false
- ✅ Remaining items transferred back
- ✅ DSR inventory decreased
- ✅ Warehouse inventory increased
- ✅ Batch allocations reversed

---

## Payment Processing

### Test Case 6.1: DSR Payment Settlement
**Objective**: Admin collects payment from DSR

**Test Steps**:
1. Admin navigates to `/dsr`
2. Select DSR with payment_on_hand > 0
3. Click "Settle Payment"
4. Enter amount (≤ payment_on_hand)
5. Select payment method
6. Enter reference
7. Add notes
8. Click "Settle"

**Expected Results**:
- ✅ Settlement record created
- ✅ DSR `payment_on_hand` decreased
- ✅ Settlement appears in history

---

### Test Case 6.2: View Settlement History
**Objective**: Track all settlements

**Test Steps**:
1. Navigate to `/dsr/settlement-history`
2. Apply filters (DSR, date range)
3. Review settlements

**Expected Results**:
- ✅ All settlements listed
- ✅ Filterable by DSR and date
- ✅ Shows amount, method, reference

---

## Edge Cases & Error Scenarios

### Edge Case 7.1: SR Order with Zero/Negative Commission
**Scenario**: Negotiated price < Sale price

**Test Steps**:
1. Create SR Order
2. Enter negotiated price lower than sale price
3. Observe negative commission displayed in red
4. Complete order flow

**Expected Results**:
- ✅ Negative commission allowed
- ✅ Displayed in red
- ✅ SR commission_amount can go negative
- ✅ Disbursement still processes

---

### Edge Case 7.2: Consolidation with Insufficient Stock
**Scenario**: Stock depleted between validation and consolidation

**Test Steps**:
1. Validate SR orders (passes)
2. Another user creates SO consuming stock
3. Attempt consolidation

**Expected Results**:
- ✅ Error message with specific items
- ✅ Consolidation blocked
- ✅ User must re-validate

---

### Edge Case 7.3: Partial Delivery with Returns
**Scenario**: Some items delivered, some returned

**Test Steps**:
1. Load SO to DSR
2. Deliver 50% of items
3. Return 30% of items
4. Collect partial payment

**Expected Results**:
- ✅ Effective total = (Qty - Returned) × Price
- ✅ Payment status = Partial
- ✅ Delivery status = Partial
- ✅ SO status = Partial
- ✅ Commission calculated on shipped only

---

### Edge Case 7.4: DSR Inactive During Assignment
**Scenario**: DSR deactivated after assignment

**Test Steps**:
1. Assign SO to active DSR
2. Admin deactivates DSR
3. DSR attempts to load order

**Expected Results**:
- ✅ Load operation succeeds (already assigned)
- ✅ New assignments blocked for inactive DSR

---

### Edge Case 7.5: Concurrent Commission Disbursement
**Scenario**: Multiple users disburse same order

**Test Steps**:
1. User A opens disburse dialog
2. User B disburses same order
3. User A confirms disbursement

**Expected Results**:
- ✅ Second disbursement fails
- ✅ Error: "Commission already disbursed"
- ✅ No double payment

---

### Edge Case 7.6: SO Cancellation After SR Order Consolidation
**Scenario**: Cancel SO that was consolidated from SR orders

**Test Steps**:
1. Consolidate SR orders to SO
2. Cancel SO

**Expected Results**:
- ✅ SO status = "Cancelled"
- ✅ SR order statuses remain "consolidated"
- ✅ Commission not calculated
- ✅ Stock released

---

## Data Integrity Verification

### Verification 8.1: Commission Balance Reconciliation
**Objective**: Ensure SR commission balances are accurate

**SQL Verification**:
```sql
-- Calculate expected commission balance
WITH commission_summary AS (
    SELECT 
        sr.sr_id,
        sr.sr_name,
        sr.commission_amount as current_balance,
        -- Ready commissions (not yet disbursed)
        COALESCE(SUM(CASE WHEN sro.commission_disbursed = 'Ready' 
                     THEN sro.commission_amount ELSE 0 END), 0) as ready_amount,
        -- Disbursed commissions
        COALESCE(SUM(CASE WHEN sro.commission_disbursed = 'Disbursed' 
                     THEN sro.commission_amount ELSE 0 END), 0) as disbursed_amount
    FROM sales.sales_representative sr
    LEFT JOIN sales.sr_order sro ON sr.sr_id = sro.sr_id
    WHERE sr.is_deleted = false
    GROUP BY sr.sr_id, sr.sr_name, sr.commission_amount
)
SELECT 
    *,
    ready_amount as expected_balance,
    current_balance - ready_amount as discrepancy
FROM commission_summary
WHERE ABS(current_balance - ready_amount) > 0.01;
```

**Expected**: No discrepancies

---

### Verification 8.2: DSR Payment Balance Reconciliation
**Objective**: Ensure DSR payment_on_hand is accurate

**SQL Verification**:
```sql
-- Calculate expected payment on hand
WITH dsr_payments AS (
    SELECT 
        dsr.dsr_id,
        dsr.dsr_name,
        dsr.payment_on_hand as current_balance,
        -- Collected payments
        COALESCE(SUM(sopd.amount_paid), 0) as total_collected,
        -- Settled payments
        COALESCE((SELECT SUM(amount) 
                  FROM sales.dsr_payment_settlement 
                  WHERE dsr_id = dsr.dsr_id 
                  AND is_deleted = false), 0) as total_settled
    FROM sales.delivery_sales_representative dsr
    LEFT JOIN sales.dsr_so_assignment dsa ON dsr.dsr_id = dsa.dsr_id
    LEFT JOIN sales.sales_order_payment_detail sopd ON dsa.sales_order_id = sopd.sales_order_id
    WHERE dsr.is_deleted = false
    GROUP BY dsr.dsr_id, dsr.dsr_name, dsr.payment_on_hand
)
SELECT 
    *,
    (total_collected - total_settled) as expected_balance,
    current_balance - (total_collected - total_settled) as discrepancy
FROM dsr_payments
WHERE ABS(current_balance - (total_collected - total_settled)) > 0.01;
```

**Expected**: No discrepancies

---

### Verification 8.3: Inventory Consistency After DSR Operations
**Objective**: Verify inventory matches after load/unload

**SQL Verification**:
```sql
-- Check DSR inventory matches allocations
SELECT 
    dis.product_id,
    dis.variant_id,
    dis.quantity as dsr_stock,
    COALESCE(SUM(dba.allocated_quantity - dba.delivered_quantity), 0) as allocated_stock,
    dis.quantity - COALESCE(SUM(dba.allocated_quantity - dba.delivered_quantity), 0) as discrepancy
FROM warehouse.dsr_inventory_stock dis
LEFT JOIN warehouse.dsr_batch_allocation dba ON 
    dis.product_id = dba.product_id AND 
    dis.variant_id = dba.variant_id AND
    dis.dsr_storage_id = dba.dsr_storage_id
WHERE dis.is_deleted = false
GROUP BY dis.product_id, dis.variant_id, dis.quantity
HAVING ABS(dis.quantity - COALESCE(SUM(dba.allocated_quantity - dba.delivered_quantity), 0)) > 0.01;
```

**Expected**: No discrepancies

---

### Verification 8.4: Sales Order Status Consistency
**Objective**: Verify SO status matches payment/delivery status

**SQL Verification**:
```sql
-- Check for status inconsistencies
SELECT 
    sales_order_id,
    order_number,
    status,
    payment_status,
    delivery_status,
    CASE 
        WHEN payment_status = 'Completed' AND delivery_status IN ('Completed', 'Delivered') 
            THEN 'Completed'
        WHEN payment_status != 'Pending' OR delivery_status NOT IN ('Pending', NULL) 
            THEN 'Partial'
        ELSE 'Open'
    END as expected_status
FROM sales.sales_order
WHERE is_deleted = false
    AND status != CASE 
        WHEN payment_status = 'Completed' AND delivery_status IN ('Completed', 'Delivered') 
            THEN 'Completed'
        WHEN payment_status != 'Pending' OR delivery_status NOT IN ('Pending', NULL) 
            THEN 'Partial'
        ELSE 'Open'
    END
    AND status != 'Cancelled';
```

**Expected**: No inconsistencies

---

## Testing Checklist

### Pre-Test Setup
- [ ] Test database with sample data
- [ ] SR users with product/customer assignments
- [ ] DSR users with storage configured
- [ ] Admin users for approvals
- [ ] Products with stock and pricing
- [ ] Active schemes configured

### Core Workflow Tests
- [ ] SR Order creation (all UOM scenarios)
- [ ] SR Order approval (single & bulk)
- [ ] SR Order consolidation validation
- [ ] Sales Order creation from consolidation
- [ ] DSR assignment
- [ ] DSR load operation
- [ ] DSR delivery (full & partial)
- [ ] DSR payment collection
- [ ] DSR unload operation
- [ ] Commission calculation
- [ ] Commission disbursement (single & bulk)
- [ ] DSR payment settlement

### Edge Case Tests
- [ ] Negative commission scenarios
- [ ] Insufficient stock handling
- [ ] Concurrent operations
- [ ] Inactive user scenarios
- [ ] Partial delivery/payment combinations
- [ ] Return processing
- [ ] Cancellation flows

### Data Integrity Checks
- [ ] Commission balance reconciliation
- [ ] DSR payment balance reconciliation
- [ ] Inventory consistency
- [ ] Status consistency
- [ ] Audit trail completeness

---

## Appendix: Common Issues & Resolutions

### Issue 1: Commission Not Calculated
**Symptoms**: Commission status stuck at "pending"  
**Cause**: SO not completed (payment or delivery incomplete)  
**Resolution**: Complete both payment and delivery

### Issue 2: Cannot Load SO to DSR
**Symptoms**: Load button disabled or error  
**Causes**:
- DSR has no storage configured
- DSR is inactive
- SO already loaded
- Insufficient stock at SO location  
**Resolution**: Check DSR configuration and stock availability

### Issue 3: Disbursement Fails
**Symptoms**: Error during commission disbursement  
**Causes**:
- Commission not in "Ready" status
- Order already disbursed
- SR not found  
**Resolution**: Verify commission status and SR existence

### Issue 4: Inventory Mismatch After DSR Operations
**Symptoms**: DSR inventory doesn't match expected  
**Causes**:
- Failed transaction rollback
- Concurrent operations
- Batch allocation errors  
**Resolution**: Run inventory reconciliation queries

---

## Document Maintenance

**Review Schedule**: Quarterly  
**Update Triggers**:
- New features added to SR/DSR workflow
- Schema changes
- Business logic updates
- Bug fixes affecting tested scenarios

**Contact**: Development Team  
**Version History**:
- v1.0 (2025): Initial comprehensive guide

---

**END OF DOCUMENT**
