# DSR Integration Scenarios - Cross-Module Testing

**Document Version:** 1.0  
**Created:** March 26, 2026  
**Purpose:** Integration testing scenarios across DSR, Inventory, Sales, and Commission modules

---

## Integration Test Scenarios

### Scenario 1: Complete End-to-End Flow

**Objective**: Test complete lifecycle from SR order to commission disbursement

**Steps**:
1. **SR Order Creation**
   - SR creates order for Customer A
   - Product: Widget A, Qty: 20, Negotiated: 120, Sale: 100
   - Expected Commission: 400 (20 × 20)

2. **Admin Approval**
   - Admin approves SR order
   - Status changes to "approved"

3. **Consolidation**
   - Admin consolidates to Sales Order
   - SO created with is_consolidated=true
   - SR order status = "consolidated"

4. **DSR Assignment**
   - Admin assigns SO to DSR-001
   - Assignment created

5. **DSR Load**
   - DSR-001 loads order to van
   - Inventory transferred: Warehouse → DSR Storage
   - SO.is_loaded = true

6. **DSR Delivery**
   - DSR delivers all 20 units
   - shipped_quantity = 20
   - Delivery status = "Completed"

7. **DSR Payment Collection**
   - DSR collects 2400 (20 × 120)
   - DSR.payment_on_hand = 2400
   - Customer balance decreased
   - Payment status = "Completed"

8. **SO Completion**
   - SO status = "Completed"
   - SR Order commission_disbursed = "Ready"
   - SR.commission_amount increased by 400

9. **DSR Settlement**
   - Admin settles 2400 from DSR
   - DSR.payment_on_hand = 0
   - Settlement record created

10. **Commission Disbursement**
    - Admin disburses 400 to SR
    - SR.commission_amount decreased by 400
    - SR Order commission_disbursed = "Disbursed"
    - Disbursement record created

**Expected Results**:
- ✅ All operations complete successfully
- ✅ Inventory correctly transferred and consumed
- ✅ All balances reconcile to zero
- ✅ All statuses updated correctly
- ✅ Complete audit trail exists

**Verification Queries**:
```sql
-- Final state verification
SELECT 
    'SR Order' as entity,
    status,
    commission_disbursed,
    commission_amount
FROM sales.sr_order WHERE sr_order_id = [SR_ORDER_ID]
UNION ALL
SELECT 
    'Sales Order',
    status,
    payment_status,
    delivery_status
FROM sales.sales_order WHERE sales_order_id = [SO_ID]
UNION ALL
SELECT 
    'DSR',
    CAST(is_active AS VARCHAR),
    CAST(payment_on_hand AS VARCHAR),
    NULL
FROM sales.delivery_sales_representative WHERE dsr_id = [DSR_ID]
UNION ALL
SELECT 
    'SR',
    CAST(is_active AS VARCHAR),
    CAST(commission_amount AS VARCHAR),
    NULL
FROM sales.sales_representative WHERE sr_id = [SR_ID];
```

---

### Scenario 2: Multi-SR Order Consolidation with Partial Delivery

**Objective**: Test consolidation of multiple SR orders with partial delivery

**Steps**:
1. SR-001 creates order: Product A, Qty: 10, Negotiated: 110
2. SR-002 creates order: Product B, Qty: 5, Negotiated: 220
3. Both orders for same customer
4. Admin approves both
5. Admin consolidates into single SO
6. Assign to DSR
7. DSR loads order
8. DSR delivers:
   - Product A: 8 units (2 returned)
   - Product B: 5 units (full)
9. DSR collects partial payment

**Expected Results**:
- ✅ SO has 2 details with different SR mappings
- ✅ Commission calculated per SR based on shipped quantity
- ✅ SR-001 commission: 8 × (110-100) = 80
- ✅ SR-002 commission: 5 × (220-200) = 100
- ✅ Returns handled correctly
- ✅ Effective total recalculated

---

### Scenario 3: DSR Load-Unload-Reload Cycle

**Objective**: Test multiple load/unload cycles for same SO

**Steps**:
1. Assign SO to DSR
2. DSR loads order
3. DSR makes partial delivery (50%)
4. DSR unloads remaining items
5. Later, DSR loads same order again
6. DSR completes delivery

**Expected Results**:
- ✅ First load: Full inventory transferred
- ✅ Partial delivery: 50% consumed from DSR inventory
- ✅ Unload: Remaining 50% returned to warehouse
- ✅ Second load: Only remaining 50% transferred
- ✅ Final delivery: All items delivered
- ✅ Inventory movements logged correctly

---

### Scenario 4: Concurrent DSR Operations

**Objective**: Test concurrent operations by multiple DSRs

**Steps**:
1. Create 3 Sales Orders
2. Assign SO-1 to DSR-A
3. Assign SO-2 to DSR-B
4. Assign SO-3 to DSR-C
5. All DSRs load simultaneously
6. All DSRs deliver simultaneously
7. All DSRs collect payment simultaneously
8. Admin settles all DSRs simultaneously

**Expected Results**:
- ✅ All operations succeed without conflicts
- ✅ Inventory correctly allocated per DSR
- ✅ No race conditions
- ✅ All balances correct
- ✅ No deadlocks

---

### Scenario 5: Scheme Application in SR Order with DSR Delivery

**Objective**: Test scheme benefits through complete DSR flow

**Steps**:
1. SR creates order with scheme-eligible product
   - Product: Widget A, Qty: 10
   - Scheme: Buy 10 Get 2 Free
   - Total to deliver: 12 units (10 billable + 2 free)
2. Consolidate to SO
3. Assign to DSR
4. DSR loads 12 units
5. DSR delivers all 12 units
6. DSR collects payment for 10 units only

**Expected Results**:
- ✅ Stock validation includes free quantity (12 units)
- ✅ DSR loads 12 units
- ✅ shipped_quantity = 10, shipped_free_quantity = 2
- ✅ Payment calculated on billable quantity only
- ✅ Commission calculated on billable quantity
- ✅ Free items tracked separately

---

### Scenario 6: Customer Balance Management Across Multiple DSRs

**Objective**: Test customer balance with multiple DSRs collecting payments

**Steps**:
1. Customer has 3 Sales Orders
2. SO-1 assigned to DSR-A (Amount: 5000)
3. SO-2 assigned to DSR-B (Amount: 3000)
4. SO-3 assigned to DSR-C (Amount: 2000)
5. All DSRs deliver and collect payments
6. Verify customer balance

**Expected Results**:
- ✅ Customer balance increases by 10000 on SO creation
- ✅ DSR-A collects 5000 → Customer balance: 5000
- ✅ DSR-B collects 3000 → Customer balance: 2000
- ✅ DSR-C collects 2000 → Customer balance: 0
- ✅ All DSRs have correct payment_on_hand
- ✅ No balance discrepancies

---

### Scenario 7: DSR Reassignment After Partial Delivery

**Objective**: Test reassigning SO to different DSR mid-delivery

**Steps**:
1. Assign SO to DSR-A
2. DSR-A loads order
3. DSR-A makes partial delivery (50%)
4. DSR-A unloads remaining items
5. Admin reassigns SO to DSR-B
6. DSR-B loads remaining items
7. DSR-B completes delivery

**Expected Results**:
- ✅ DSR-A assignment status = "completed" or "reassigned"
- ✅ New assignment created for DSR-B
- ✅ DSR-B loads only remaining 50%
- ✅ Inventory correctly tracked
- ✅ Payments tracked per DSR

---

### Scenario 8: Batch Expiry During DSR Operations

**Objective**: Test handling of expiring batches in DSR storage

**Steps**:
1. Load SO with batch expiring in 7 days
2. DSR holds inventory for 10 days
3. Attempt delivery with expired batch

**Expected Results**:
- ✅ Warning displayed about expiring batch
- ✅ Delivery allowed (business decision)
- ✅ Expired batch tracked
- ✅ Inventory movement logged with batch info

---

### Scenario 9: Commission Calculation with Returns

**Objective**: Verify commission calculated only on shipped quantity

**Steps**:
1. SR Order: Qty 20, Negotiated: 120, Sale: 100
2. Expected Commission: 400 (20 × 20)
3. DSR delivers 15, returns 5
4. Actual Commission: 300 (15 × 20)

**Expected Results**:
- ✅ Commission calculated on shipped_quantity (15)
- ✅ Not on ordered quantity (20)
- ✅ SR.commission_amount = 300
- ✅ Disbursement amount = 300

---

### Scenario 10: Settlement with Multiple Payment Methods

**Objective**: Test settlement tracking with different payment methods

**Steps**:
1. DSR collects payments:
   - SO-1: 5000 (Cash)
   - SO-2: 3000 (Bank Transfer)
   - SO-3: 2000 (Mobile Banking)
2. DSR.payment_on_hand = 10000
3. Admin settles:
   - Settlement-1: 5000 (Cash)
   - Settlement-2: 5000 (Bank Transfer, Ref: TXN123)

**Expected Results**:
- ✅ Both settlements recorded
- ✅ Payment methods tracked
- ✅ Reference numbers stored
- ✅ DSR.payment_on_hand = 0
- ✅ Settlement history shows all details

---

## Performance Testing Scenarios

### Performance Test 1: Bulk DSR Load Operations

**Objective**: Test system performance with multiple concurrent loads

**Steps**:
1. Create 50 Sales Orders
2. Assign all to different DSRs
3. All DSRs load simultaneously

**Expected Results**:
- ✅ All loads complete within acceptable time (< 5 seconds each)
- ✅ No database deadlocks
- ✅ Inventory correctly allocated
- ✅ No race conditions

---

### Performance Test 2: Large Order Delivery

**Objective**: Test delivery of order with many line items

**Steps**:
1. Create SO with 100 line items
2. Assign to DSR
3. DSR loads order
4. DSR delivers all items

**Expected Results**:
- ✅ Load completes within 10 seconds
- ✅ Delivery processes within 15 seconds
- ✅ UI remains responsive
- ✅ All items tracked correctly

---

### Performance Test 3: Bulk Commission Disbursement

**Objective**: Test bulk disbursement of 1000+ commissions

**Steps**:
1. Create 1000 SR orders with commissions
2. Complete all to Ready status
3. Bulk disburse all

**Expected Results**:
- ✅ Disbursement completes within 30 seconds
- ✅ All records created
- ✅ All balances updated correctly
- ✅ No timeouts

---

## Security Testing Scenarios

### Security Test 1: DSR Access Control

**Objective**: Verify DSR can only access assigned orders

**Steps**:
1. DSR-A assigned SO-1
2. DSR-B assigned SO-2
3. DSR-A attempts to load SO-2

**Expected Results**:
- ✅ Error: "Access denied"
- ✅ DSR-A cannot see SO-2 in list
- ✅ Load operation blocked

---

### Security Test 2: SR Product Assignment Enforcement

**Objective**: Verify SR can only order assigned products

**Steps**:
1. SR-A assigned Product-A only
2. SR-A attempts to create order with Product-B

**Expected Results**:
- ✅ Product-B not visible in dropdown
- ✅ API rejects if bypassed
- ✅ Error: "Product not assigned to SR"

---

### Security Test 3: Settlement Authorization

**Objective**: Verify only authorized users can settle

**Steps**:
1. DSR user attempts to access settlement page
2. SR user attempts to settle DSR

**Expected Results**:
- ✅ DSR cannot access settlement page
- ✅ SR cannot access settlement page
- ✅ Only Admin/Manager can settle
- ✅ Proper authorization checks

---

## Data Consistency Scenarios

### Consistency Test 1: Inventory Reconciliation After Multiple Operations

**Objective**: Verify inventory consistency after complex operations

**Steps**:
1. Initial warehouse stock: 1000 units
2. Create 5 SOs totaling 500 units
3. Load all to DSRs
4. Deliver 400 units
5. Return 50 units
6. Unload 50 units
7. Verify final inventory

**Expected Results**:
- ✅ Warehouse stock: 600 (1000 - 500 + 50 + 50)
- ✅ DSR stock: 0 (all unloaded)
- ✅ Delivered: 400
- ✅ Returned: 50
- ✅ All movements logged

---

### Consistency Test 2: Balance Reconciliation Across All Entities

**Objective**: Verify all balances reconcile correctly

**Steps**:
1. Run complete flow for 10 orders
2. Execute reconciliation queries
3. Verify no discrepancies

**Expected Results**:
- ✅ Customer balances match payment records
- ✅ DSR payment_on_hand matches collections - settlements
- ✅ SR commission_amount matches Ready - Disbursed
- ✅ Inventory matches allocations
- ✅ All audit trails complete

---

## Error Recovery Scenarios

### Recovery Test 1: Failed Load Operation

**Objective**: Test rollback on failed load

**Steps**:
1. Start load operation
2. Simulate database error mid-transaction
3. Verify rollback

**Expected Results**:
- ✅ Transaction rolled back
- ✅ No partial inventory transfer
- ✅ SO.is_loaded remains false
- ✅ Error message displayed
- ✅ User can retry

---

### Recovery Test 2: Network Failure During Delivery

**Objective**: Test handling of network failure

**Steps**:
1. DSR starts delivery
2. Simulate network disconnection
3. DSR reconnects
4. Verify state

**Expected Results**:
- ✅ Delivery not saved if not committed
- ✅ User can retry
- ✅ No duplicate deliveries
- ✅ Inventory consistent

---

## Audit Trail Scenarios

### Audit Test 1: Complete Operation Audit

**Objective**: Verify all operations logged

**Steps**:
1. Execute complete DSR lifecycle
2. Query audit tables
3. Verify all operations logged

**Expected Results**:
- ✅ SR Order creation logged
- ✅ Approval logged with user
- ✅ Consolidation logged
- ✅ DSR assignment logged
- ✅ Load operation logged
- ✅ Delivery logged
- ✅ Payment logged
- ✅ Unload logged
- ✅ Settlement logged
- ✅ Disbursement logged

---

### Audit Test 2: User Action Tracking

**Objective**: Verify user actions tracked

**Steps**:
1. Multiple users perform operations
2. Query audit trail
3. Verify user attribution

**Expected Results**:
- ✅ cb (created_by) populated
- ✅ mb (modified_by) populated
- ✅ cd (created_date) accurate
- ✅ md (modified_date) accurate
- ✅ Can trace all actions to users

---

## Document Maintenance

**Review Schedule**: Quarterly  
**Update Triggers**: New integration points, schema changes, business logic updates

**Version History**:
- v1.0 (March 26, 2026): Initial integration scenarios

---

**END OF DOCUMENT**
