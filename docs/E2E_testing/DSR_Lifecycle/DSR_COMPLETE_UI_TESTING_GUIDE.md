# DSR Complete Lifecycle - Comprehensive UI Testing Guide
## All SR Order → DSR Assignment → Load/Unload → Delivery → Settlement Scenarios

**Document Version:** 2.0  
**Created:** March 26, 2026  
**System:** Shoudagor Distribution Management System  

---

## Quick Navigation

- [Overview & Prerequisites](#overview--prerequisites)
- [SR Order Testing](#sr-order-testing)
- [DSR Assignment Testing](#dsr-assignment-testing)
- [DSR Load Operations](#dsr-load-operations)
- [DSR Delivery & Payment](#dsr-delivery--payment)
- [DSR Unload Operations](#dsr-unload-operations)
- [Settlement Testing](#settlement-testing)
- [Commission Testing](#commission-testing)
- [Edge Cases](#edge-cases)
- [Data Verification](#data-verification)

---

## Overview & Prerequisites

### Complete Lifecycle Flow
```
SR Order Creation → Approval → Consolidation to SO → 
DSR Assignment → Load to Van → Delivery → Payment Collection → 
Unload Remaining → Settlement with Admin → Commission Disbursement
```

### Prerequisites
- **Users**: Admin, SR, DSR with proper credentials
- **Master Data**: Products, Customers, Storage Locations
- **DSR Setup**: DSR with storage configured and active
- **Inventory**: Sufficient stock at warehouse locations
- **Schemes**: Active claim schemes for testing

---

## SR Order Testing

### Test Case 1: Create SR Order with Commission Calculation

**Objective**: Verify SR order creation with automatic commission calculation

**Steps**:
1. Login as SR user
2. Navigate to /sr/orders/new
3. Select assigned customer
4. Add product with:
   - Quantity: 10
   - Sale Price: 100.00 (auto-populated)
   - Negotiated Price: 110.00
5. Verify commission displayed: 100.00 (10 × (110-100))
6. Submit order

**Expected Results**:
- ✅ Order created with unique number (SR-YYYYMMDD-SRID-SEQ)
- ✅ Status = "pending"
- ✅ Commission calculated correctly
- ✅ Commission status = "pending"

**Verification**:
```sql
SELECT sr_order_id, order_number, status, total_amount, commission_disbursed
FROM sales.sr_order WHERE order_number = '[ORDER_NUMBER]';

SELECT (negotiated_price - sale_price) * quantity as commission
FROM sales.sr_order_detail WHERE sr_order_id = [ID];
```

---

### Test Case 2: Bulk Approve SR Orders

**Objective**: Verify bulk approval of multiple SR orders

**Steps**:
1. Login as Admin
2. Navigate to /sr/orders
3. Filter status = "pending"
4. Select multiple orders (checkbox)
5. Click "Bulk Approve"
6. Confirm action

**Expected Results**:
- ✅ All selected orders status = "approved"
- ✅ Success message with count
- ✅ Orders appear in unconsolidated list
- ✅ Cannot delete approved orders

---

### Test Case 3: Consolidate SR Orders to Sales Order

**Objective**: Verify consolidation of multiple SR orders into single SO

**Steps**:
1. Navigate to /sr/orders/unconsolidated
2. Select customer with multiple approved SR orders
3. Click "Validate"
4. Select SR orders to consolidate
5. Select storage location
6. Click "Validate Selected Orders"
7. Enter expected shipment date
8. Click "Generate Consolidated Order"

**Expected Results**:
- ✅ Sales Order created with unique number
- ✅ SO.is_consolidated = true
- ✅ SO.order_source = "sr_consolidated"
- ✅ All SR orders status = "consolidated"
- ✅ SO details contain SR mapping
- ✅ Price differences tracked

**Verification**:
```sql
SELECT sales_order_id, order_number, is_consolidated, 
       consolidated_sr_orders, total_amount
FROM sales.sales_order WHERE order_number = '[SO_NUMBER]';

SELECT sr_order_id, status FROM sales.sr_order 
WHERE sr_order_id IN ([SR_ORDER_IDS]);
```

---

## DSR Assignment Testing

### Test Case 4: Assign Sales Order to DSR

**Objective**: Verify DSR assignment to Sales Order

**Steps**:
1. Login as Admin
2. Navigate to /sales
3. Select Sales Order (not loaded)
4. Click "Add to DSR" from actions menu
5. Select active DSR from dropdown
6. Add notes (optional)
7. Click "Assign"

**Expected Results**:
- ✅ Assignment created successfully
- ✅ SO shows DSR information
- ✅ DSR can see order in "My Assignments"
- ✅ Stock validated at SO location

**Verification**:
```sql
SELECT assignment_id, dsr_id, sales_order_id, status, assigned_date
FROM sales.dsr_so_assignment WHERE sales_order_id = [SO_ID];
```

---

### Test Case 5: DSR Assignment Validation - Inactive DSR

**Objective**: Verify error when assigning to inactive DSR

**Steps**:
1. Admin deactivates DSR
2. Attempt to assign SO to inactive DSR

**Expected Results**:
- ✅ Error message: "DSR is not active"
- ✅ Assignment not created
- ✅ User remains on form

---

### Test Case 6: DSR Assignment Validation - No Storage

**Objective**: Verify error when DSR has no storage configured

**Steps**:
1. Create DSR without storage
2. Attempt to assign SO to DSR

**Expected Results**:
- ✅ Error message: "DSR storage not configured"
- ✅ Assignment not created

---

## DSR Load Operations

### Test Case 7: Load Sales Order to DSR Van

**Objective**: Verify inventory transfer from warehouse to DSR storage

**Steps**:
1. Login as DSR user
2. Navigate to /dsr/my-assignments
3. Select assigned order (not loaded)
4. Click "Load to Van"
5. Review items to be loaded
6. Add notes (optional)
7. Confirm load

**Expected Results**:
- ✅ SO.is_loaded = true
- ✅ SO.loaded_by_dsr_id = dsr_id
- ✅ SO.loaded_at = current timestamp
- ✅ Inventory transferred:
  - inventory_stock decreased at warehouse
  - dsr_inventory_stock increased at DSR storage
- ✅ Batch allocations created
- ✅ Success message displayed

**Verification**:
```sql
-- Check SO loaded status
SELECT is_loaded, loaded_by_dsr_id, loaded_at
FROM sales.sales_order WHERE sales_order_id = [SO_ID];

-- Check warehouse inventory decreased
SELECT product_id, variant_id, quantity
FROM warehouse.inventory_stock 
WHERE location_id = [WAREHOUSE_LOCATION_ID];

-- Check DSR inventory increased
SELECT product_id, variant_id, quantity
FROM warehouse.dsr_inventory_stock 
WHERE dsr_storage_id = [DSR_STORAGE_ID];

-- Check batch allocations
SELECT * FROM warehouse.dsr_batch_allocation 
WHERE sales_order_id = [SO_ID];
```

---

### Test Case 8: Load Validation - Insufficient Stock

**Objective**: Verify error when warehouse has insufficient stock

**Steps**:
1. Create SO with quantity exceeding warehouse stock
2. Assign to DSR
3. Attempt to load

**Expected Results**:
- ✅ Error message with specific items
- ✅ Shows requested vs available quantities
- ✅ Load operation blocked
- ✅ No inventory transferred

---

### Test Case 9: Load Validation - Already Loaded

**Objective**: Verify error when SO already loaded

**Steps**:
1. Load SO to DSR van
2. Attempt to load same SO again

**Expected Results**:
- ✅ Error message: "Sales Order already loaded"
- ✅ Load button disabled
- ✅ Shows "Loaded" badge

---

## DSR Delivery & Payment

### Test Case 10: Full Delivery with Full Payment

**Objective**: Verify complete delivery and payment collection

**Steps**:
1. DSR navigates to loaded order
2. Click "Make Delivery"
3. For each item, enter delivered quantity = ordered quantity
4. Select delivery date
5. Click "Process Delivery"
6. Click "Collect Payment"
7. Enter amount = effective total
8. Select payment method: "Cash"
9. Click "Collect"

**Expected Results**:
- ✅ Delivery details created
- ✅ shipped_quantity updated on SO details
- ✅ DSR inventory decreased
- ✅ Delivery status = "Completed"
- ✅ Payment detail created
- ✅ SO.amount_paid = effective_total_amount
- ✅ DSR.payment_on_hand increased
- ✅ Customer.balance_amount decreased
- ✅ Payment status = "Completed"
- ✅ SO status = "Completed"

**Verification**:
```sql
-- Check delivery
SELECT shipped_quantity, delivered_quantity
FROM sales.sales_order_detail WHERE sales_order_id = [SO_ID];

-- Check payment
SELECT amount_paid, payment_status, delivery_status, status
FROM sales.sales_order WHERE sales_order_id = [SO_ID];

-- Check DSR balance
SELECT payment_on_hand FROM sales.delivery_sales_representative 
WHERE dsr_id = [DSR_ID];

-- Check customer balance
SELECT balance_amount FROM sales.customer WHERE customer_id = [CUSTOMER_ID];
```

---

### Test Case 11: Partial Delivery with Partial Payment

**Objective**: Verify partial delivery and payment handling

**Steps**:
1. DSR makes delivery
2. Deliver 50% of each item
3. Collect 50% of total amount

**Expected Results**:
- ✅ shipped_quantity = 50% of quantity
- ✅ Delivery status = "Partial"
- ✅ amount_paid = 50% of effective_total
- ✅ Payment status = "Partial"
- ✅ SO status = "Partial"
- ✅ Remaining items still in DSR inventory

---

### Test Case 12: Delivery with Returns/Rejections

**Objective**: Verify return handling during delivery

**Steps**:
1. DSR makes delivery
2. For one item:
   - Delivered quantity: 8
   - Rejected quantity: 2
   - Rejection reason: "Damaged"
3. Process delivery

**Expected Results**:
- ✅ shipped_quantity = 8
- ✅ returned_quantity = 2
- ✅ Rejected items returned to DSR inventory
- ✅ Effective total recalculated
- ✅ Delivery status updated

---

### Test Case 13: Payment Collection - Non-Cash Method

**Objective**: Verify payment with bank transfer/check

**Steps**:
1. Click "Collect Payment"
2. Select payment method: "Bank Transfer"
3. Enter reference number: "TXN123456"
4. Enter amount
5. Add notes
6. Collect

**Expected Results**:
- ✅ Payment method stored
- ✅ Reference number required and stored
- ✅ Payment detail created with all info
- ✅ DSR.payment_on_hand increased

---

### Test Case 14: Payment Collection - Overpayment

**Objective**: Verify overpayment handling

**Steps**:
1. Collect payment amount > effective_total_amount
2. Add remarks explaining overpayment

**Expected Results**:
- ✅ Overpayment allowed
- ✅ Customer balance becomes negative
- ✅ Payment status = "Completed"
- ✅ Remarks stored

---

## DSR Unload Operations

### Test Case 15: Unload Undelivered Items

**Objective**: Verify unload operation returns items to warehouse

**Steps**:
1. DSR has partially delivered order
2. Navigate to loaded order
3. Click "Unload from Van"
4. Select return location (optional, defaults to original)
5. Add notes
6. Confirm unload

**Expected Results**:
- ✅ SO.is_loaded = false
- ✅ loaded_by_dsr_id and loaded_at cleared
- ✅ Undelivered items transferred:
  - dsr_inventory_stock decreased
  - inventory_stock increased at warehouse
- ✅ Batch allocations reversed
- ✅ Inventory movements logged

**Verification**:
```sql
-- Check SO unloaded
SELECT is_loaded, loaded_by_dsr_id, loaded_at
FROM sales.sales_order WHERE sales_order_id = [SO_ID];

-- Check DSR inventory decreased
SELECT product_id, variant_id, quantity
FROM warehouse.dsr_inventory_stock 
WHERE dsr_storage_id = [DSR_STORAGE_ID];

-- Check warehouse inventory increased
SELECT product_id, variant_id, quantity
FROM warehouse.inventory_stock 
WHERE location_id = [WAREHOUSE_LOCATION_ID];
```

---

### Test Case 16: Unload Fully Delivered Order

**Objective**: Verify unload when all items delivered

**Steps**:
1. DSR delivers all items
2. Attempt to unload

**Expected Results**:
- ✅ Unload button disabled or
- ✅ Message: "All items delivered, nothing to unload"

---

## Settlement Testing

### Test Case 17: DSR Payment Settlement - Full Amount

**Objective**: Verify admin collects full payment from DSR

**Steps**:
1. Login as Admin
2. Navigate to /dsr
3. Select DSR with payment_on_hand > 0
4. Click "Settle Payment"
5. Click "Settle Full Amount" button
6. Select payment method: "Cash"
7. Enter reference number (if non-cash)
8. Add notes
9. Click "Confirm Settlement"

**Expected Results**:
- ✅ Settlement record created
- ✅ DSR.payment_on_hand = 0
- ✅ Settlement appears in history
- ✅ Success message displayed

**Verification**:
```sql
-- Check settlement
SELECT settlement_id, dsr_id, amount, payment_method, 
       reference_number, settlement_date
FROM sales.dsr_payment_settlement 
WHERE dsr_id = [DSR_ID] ORDER BY settlement_date DESC LIMIT 1;

-- Check DSR balance
SELECT payment_on_hand FROM sales.delivery_sales_representative 
WHERE dsr_id = [DSR_ID];
```

---

### Test Case 18: Settlement - Partial Amount

**Objective**: Verify partial settlement

**Steps**:
1. DSR has payment_on_hand = 10000
2. Admin settles 6000
3. Verify remaining balance = 4000

**Expected Results**:
- ✅ Settlement amount = 6000
- ✅ DSR.payment_on_hand = 4000
- ✅ Can settle remaining later

---

### Test Case 19: Settlement Validation - Exceeds Balance

**Objective**: Verify error when settlement > payment_on_hand

**Steps**:
1. DSR has payment_on_hand = 5000
2. Attempt to settle 6000

**Expected Results**:
- ✅ Error: "Settlement amount exceeds payment on hand"
- ✅ Shows current balance
- ✅ Settlement not created

---

### Test Case 20: Settlement - Duplicate Reference Number

**Objective**: Verify unique reference number validation

**Steps**:
1. Create settlement with reference "REF001"
2. Attempt another settlement with same reference

**Expected Results**:
- ✅ Error: "Reference number already exists"
- ✅ Settlement not created

---

### Test Case 21: View Settlement History

**Objective**: Verify settlement history tracking

**Steps**:
1. Navigate to /dsr/settlement-history
2. Filter by DSR
3. Filter by date range
4. Review settlements

**Expected Results**:
- ✅ All settlements listed
- ✅ Shows amount, method, reference, date
- ✅ Filterable and sortable
- ✅ Pagination works

---

## Commission Testing

### Test Case 22: Commission Calculation on SO Completion

**Objective**: Verify commission becomes Ready when SO completes

**Steps**:
1. Create SR order with commission
2. Consolidate to SO
3. Complete SO (full delivery + payment)
4. Check SR order commission status

**Expected Results**:
- ✅ SR_Order.commission_disbursed = "Ready"
- ✅ SR.commission_amount increased
- ✅ Commission = (negotiated - sale) × shipped_quantity

**Verification**:
```sql
-- Check SR order commission
SELECT sr_order_id, commission_disbursed, commission_amount
FROM sales.sr_order WHERE sr_order_id = [SR_ORDER_ID];

-- Check SR balance
SELECT commission_amount FROM sales.sales_representative 
WHERE sr_id = [SR_ID];

-- Calculate expected commission
SELECT SUM((negotiated_price - sale_price) * shipped_quantity) 
FROM sales.sr_order_detail WHERE sr_order_id = [SR_ORDER_ID];
```

---

### Test Case 23: Single Commission Disbursement

**Objective**: Verify disbursing commission for one order

**Steps**:
1. Navigate to /sr/orders/undisbursed
2. Filter commission_disbursed = "Ready"
3. Select order
4. Click "Disburse"
5. Enter payment method
6. Enter reference number
7. Confirm

**Expected Results**:
- ✅ SR_Order.commission_disbursed = "Disbursed"
- ✅ SR.commission_amount decreased
- ✅ Disbursement record created
- ✅ Cannot disburse again

---

### Test Case 24: Bulk Commission Disbursement

**Objective**: Verify bulk disbursement of multiple commissions

**Steps**:
1. Select multiple Ready orders
2. Click "Disburse (N)"
3. Review summary by SR
4. Enter payment details
5. Confirm

**Expected Results**:
- ✅ All selected orders disbursed
- ✅ Summary shows total by SR
- ✅ Disbursement records created
- ✅ SR balances updated

---

### Test Case 25: Negative Commission Handling

**Objective**: Verify negative commission (negotiated < sale price)

**Steps**:
1. Create SR order with negotiated_price < sale_price
2. Complete flow to disbursement

**Expected Results**:
- ✅ Negative commission displayed in red
- ✅ SR.commission_amount can go negative
- ✅ Disbursement still processes
- ✅ Negative amount tracked

---

## Edge Cases

### Edge Case 1: Concurrent DSR Load Operations

**Scenario**: Two DSRs attempt to load same SO simultaneously

**Steps**:
1. User A starts load for SO
2. User B starts load for same SO
3. User A confirms load
4. User B confirms load

**Expected Results**:
- ✅ First load succeeds
- ✅ Second load fails with error
- ✅ Error: "Sales Order already loaded"
- ✅ No double inventory transfer

---

### Edge Case 2: Stock Depletion Between Validation and Load

**Scenario**: Stock consumed by another order between validation and load

**Steps**:
1. DSR validates SO for loading (passes)
2. Another user creates SO consuming stock
3. DSR attempts to load

**Expected Results**:
- ✅ Load fails with error
- ✅ Error shows specific items with insufficient stock
- ✅ No partial load
- ✅ Transaction rolled back

---

### Edge Case 3: DSR Deactivated After Assignment

**Scenario**: DSR deactivated while having assigned orders

**Steps**:
1. Assign SO to active DSR
2. Admin deactivates DSR
3. DSR attempts to load order

**Expected Results**:
- ✅ Load operation succeeds (already assigned)
- ✅ New assignments blocked for inactive DSR
- ✅ Existing assignments can complete

---

### Edge Case 4: Concurrent Settlement Operations

**Scenario**: Multiple admins attempt to settle same DSR

**Steps**:
1. Admin A opens settlement dialog
2. Admin B settles DSR
3. Admin A confirms settlement

**Expected Results**:
- ✅ Second settlement fails
- ✅ Error: "Insufficient payment on hand" or version conflict
- ✅ No double settlement
- ✅ Optimistic locking prevents race condition

---

### Edge Case 5: SO Cancellation After DSR Load

**Scenario**: Cancel SO that is loaded to DSR van

**Steps**:
1. Load SO to DSR
2. Attempt to cancel SO

**Expected Results**:
- ✅ Cancellation blocked or
- ✅ Requires unload first
- ✅ Error: "Cannot cancel loaded order"

---

### Edge Case 6: Return Quantity Exceeds Delivered

**Scenario**: Attempt to return more than delivered

**Steps**:
1. Deliver 10 units
2. Attempt to return 15 units

**Expected Results**:
- ✅ Validation error
- ✅ Error: "Return quantity exceeds delivered quantity"
- ✅ Return not processed

---

### Edge Case 7: Payment Collection Exceeds Outstanding

**Scenario**: Collect more than outstanding amount

**Steps**:
1. SO effective total = 10000
2. Already paid = 6000
3. Attempt to collect 5000 (total would be 11000)

**Expected Results**:
- ✅ Overpayment allowed with warning
- ✅ Requires remarks/notes
- ✅ Customer balance becomes negative
- ✅ Payment status = "Completed"

---

## Data Verification

### Verification 1: DSR Payment Balance Reconciliation

**Objective**: Ensure DSR payment_on_hand is accurate

```sql
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

### Verification 2: SR Commission Balance Reconciliation

```sql
WITH commission_summary AS (
    SELECT 
        sr.sr_id,
        sr.sr_name,
        sr.commission_amount as current_balance,
        -- Ready commissions
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

### Verification 3: DSR Inventory Consistency

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

### Verification 4: Sales Order Status Consistency

```sql
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

## Complete Testing Checklist

### Pre-Test Setup
- [ ] Test database with sample data
- [ ] SR users with product/customer assignments
- [ ] DSR users with storage configured
- [ ] Admin users for approvals and settlements
- [ ] Products with stock and pricing
- [ ] Active schemes configured

### SR Order Workflow
- [ ] SR Order creation (all UOM scenarios)
- [ ] Commission calculation (positive and negative)
- [ ] SR Order approval (single & bulk)
- [ ] SR Order consolidation validation
- [ ] Sales Order creation from consolidation
- [ ] Price difference tracking

### DSR Assignment & Loading
- [ ] DSR assignment to SO
- [ ] Assignment validation (inactive DSR, no storage)
- [ ] Load operation (full inventory transfer)
- [ ] Load validation (insufficient stock, already loaded)
- [ ] Batch allocation creation
- [ ] Inventory movement logging

### DSR Delivery & Payment
- [ ] Full delivery with full payment
- [ ] Partial delivery with partial payment
- [ ] Delivery with returns/rejections
- [ ] Payment collection (cash and non-cash)
- [ ] Overpayment handling
- [ ] Status updates (delivery, payment, SO)

### DSR Unload Operations
- [ ] Unload undelivered items
- [ ] Inventory transfer back to warehouse
- [ ] Batch allocation reversal
- [ ] Unload validation (fully delivered)

### Settlement & Commission
- [ ] DSR payment settlement (full and partial)
- [ ] Settlement validation (exceeds balance, duplicate reference)
- [ ] Settlement history tracking
- [ ] Commission calculation on SO completion
- [ ] Single commission disbursement
- [ ] Bulk commission disbursement
- [ ] Negative commission handling

### Edge Cases
- [ ] Concurrent load operations
- [ ] Stock depletion between validation and load
- [ ] DSR deactivation scenarios
- [ ] Concurrent settlement operations
- [ ] SO cancellation after load
- [ ] Return quantity validation
- [ ] Payment collection edge cases

### Data Integrity
- [ ] DSR payment balance reconciliation
- [ ] SR commission balance reconciliation
- [ ] DSR inventory consistency
- [ ] SO status consistency
- [ ] Audit trail completeness

---

## Document Maintenance

**Review Schedule**: Quarterly  
**Update Triggers**:
- New features added to DSR workflow
- Schema changes
- Business logic updates
- Bug fixes affecting tested scenarios

**Related Documents**:
- [DSR_LIFECYCLE_OVERVIEW.md](./DSR_LIFECYCLE_OVERVIEW.md) - System architecture
- [SALES_ORDER_COMPREHENSIVE_UI_TESTING_GUIDE.md](../Sales_Order/SALES_ORDER_COMPREHENSIVE_UI_TESTING_GUIDE.md) - SO testing
- [SR_ORDER_TO_SALES_ORDER_COMPREHENSIVE_UI_TESTING_GUIDE.md](../SR_Order_Sales_Order/SR_ORDER_TO_SALES_ORDER_COMPREHENSIVE_UI_TESTING_GUIDE.md) - SR Order testing

**Contact**: Development Team  
**Version History**:
- v2.0 (March 26, 2026): Complete DSR lifecycle guide with all edge cases

---

**END OF DOCUMENT**
