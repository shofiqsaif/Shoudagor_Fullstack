## 13. Edge Cases & Error Scenarios

### 13.1 Concurrent SO Operations

**Test Case: TC-EDGE-001 - Concurrent SO Editing**

**Objective:** Verify optimistic locking prevents lost updates

**Test Steps:**

1. **Open SO in Two Browser Tabs**
   - Tab 1: Open SO for editing
   - Tab 2: Open same SO for editing

2. **Edit in Tab 1**
   - Update total amount
   - Save changes
   - Verify success

3. **Edit in Tab 2**
   - Update different field
   - Attempt to save
   - Verify version conflict error

4. **Refresh and Retry**
   - Refresh Tab 2
   - Make changes again
   - Save successfully

**Expected Results:**
- ✅ Optimistic locking prevents lost updates
- ✅ Version conflict detected
- ✅ User notified to refresh
- ✅ Data integrity maintained

---

### 13.2 Deleted Product in SO

**Test Case: TC-EDGE-002 - Delivery with Deleted Product**

**Objective:** Verify validation prevents delivery of deleted products

**Prerequisites:**
- SO with Product "Widget A"
- Product "Widget A" soft-deleted after SO creation

**Test Steps:**

1. **Attempt Delivery**
   - Open delivery form
   - Try to deliver Widget A
   - Click "Record Delivery"

2. **Verify Validation Error**
   - Error: "Product Widget A has been deleted"
   - Delivery not recorded
   - User notified

**Expected Results:**
- ✅ Deleted product validation
- ✅ Clear error message
- ✅ Delivery prevented
- ✅ Data integrity maintained

---

### 13.3 Negative Stock Prevention

**Test Case: TC-EDGE-003 - Prevent Negative Inventory**

**Objective:** Verify system prevents negative stock

**Prerequisites:**
- Product "Widget A" has 10 units in stock
- SO1 for 8 units (not yet delivered)
- SO2 for 5 units (attempting delivery)

**Test Steps:**

1. **Deliver SO1**
   - Deliver 8 units
   - Stock: 2 units remaining

2. **Attempt to Deliver SO2**
   - Try to deliver 5 units
   - Available: 2 units
   - Click "Record Delivery"

3. **Verify Stock Validation**
   - Error: "Insufficient stock"
   - Shows: Requested: 5, Available: 2
   - Delivery not recorded

**Expected Results:**
- ✅ Stock validation prevents negative inventory
- ✅ Real-time stock check
- ✅ Clear error message
- ✅ No negative stock allowed

---

### 13.4 UOM Conversion Failure

**Test Case: TC-EDGE-004 - Missing UOM Conversion**

**Objective:** Verify error handling for missing UOM conversions

**Prerequisites:**
- Product "Widget A" with UOM "Box"
- No conversion defined from Box to base UOM

**Test Steps:**

1. **Attempt SO Creation**
   - Add Widget A with UOM: Box
   - Qty: 10
   - Click "Create Sales Order"

2. **Verify Conversion Error**
   - Error: "UOM conversion not defined"
   - SO not created
   - User notified to configure conversion

**Expected Results:**
- ✅ UOM conversion validated
- ✅ Clear error message
- ✅ SO creation prevented
- ✅ User guided to fix configuration

---

### 13.5 Batch Expiry Validation

**Test Case: TC-EDGE-005 - Expired Batch Allocation**

**Objective:** Verify expired batches not allocated

**Prerequisites:**
- Product "Widget A" has 2 batches:
  - Batch A: 50 units, Expiry: Yesterday (expired)
  - Batch B: 50 units, Expiry: Next month (valid)

**Test Steps:**

1. **Create SO for 30 Units**
   - Add Widget A, Qty: 30
   - Submit SO

2. **Verify Batch Allocation**
   - Batch A NOT allocated (expired)
   - Batch B allocated (30 units)
   - Only valid batches used

3. **Attempt SO for 60 Units**
   - Add Widget A, Qty: 60
   - Available valid stock: 50 units (Batch B only)
   - Verify error: "Insufficient stock"

**Expected Results:**
- ✅ Expired batches excluded from allocation
- ✅ Only valid batches allocated
- ✅ Stock validation considers expiry
- ✅ Prevents selling expired products

---

### 13.6 Cross-Company Data Isolation

**Test Case: TC-EDGE-006 - Company Data Isolation**

**Objective:** Verify users cannot access other company's SOs

**Prerequisites:**
- Company A: SO-A-001
- Company B: SO-B-001
- User logged in to Company A

**Test Steps:**

1. **Attempt to Access Company B SO**
   - Try to open SO-B-001 via direct URL
   - Verify access denied

2. **Attempt to List Company B SOs**
   - SO list should only show Company A SOs
   - SO-B-001 not visible

3. **Attempt to Edit Company B SO**
   - Try to edit SO-B-001 via API
   - Verify 403 Forbidden error

**Expected Results:**
- ✅ Company data isolated
- ✅ Access denied for other company's data
- ✅ API enforces company_id filtering
- ✅ Security maintained

---

### 13.7 Large Order Performance

**Test Case: TC-EDGE-007 - SO with 100+ Line Items**

**Objective:** Verify performance with large orders

**Test Steps:**

1. **Create SO with 100 Line Items**
   - Add 100 different products
   - Each with quantity, price, UOM
   - Submit SO

2. **Verify Performance**
   - SO creation completes within 5 seconds
   - No timeout errors
   - All items saved correctly

3. **Verify Batch Allocation**
   - 100 batch allocations created
   - Allocation completes within reasonable time

4. **Verify SO Display**
   - SO details page loads within 3 seconds
   - All 100 items displayed
   - Pagination works correctly

**Expected Results:**
- ✅ Handles large orders efficiently
- ✅ No performance degradation
- ✅ All items processed correctly
- ✅ UI remains responsive

---

### 13.8 Special Characters in Data

**Test Case: TC-EDGE-008 - Special Characters Handling**

**Objective:** Verify special characters handled correctly

**Test Steps:**

1. **Create SO with Special Characters**
   - Customer name: "O'Brien & Sons"
   - Remarks: "Deliver to 123 Main St. (Rear entrance)"
   - Product name: "Widget A/B"
   - Submit SO

2. **Verify Data Storage**
   - Special characters stored correctly
   - No SQL injection
   - No encoding issues

3. **Verify Data Display**
   - Special characters displayed correctly
   - No HTML escaping issues
   - PDF generation works

**Expected Results:**
- ✅ Special characters handled correctly
- ✅ No SQL injection vulnerabilities
- ✅ Proper encoding/escaping
- ✅ Display and export work correctly

---

### 13.9 Network Interruption During SO Creation

**Test Case: TC-EDGE-009 - Network Failure Handling**

**Objective:** Verify graceful handling of network interruptions

**Test Steps:**

1. **Start SO Creation**
   - Fill all SO details
   - Click "Create Sales Order"
   - Simulate network disconnection during submission

2. **Verify Error Handling**
   - Error message: "Network error, please try again"
   - Form data preserved (not lost)
   - User can retry submission

3. **Reconnect and Retry**
   - Restore network connection
   - Click "Create Sales Order" again
   - SO created successfully
   - No duplicate SO created

**Expected Results:**
- ✅ Network errors handled gracefully
- ✅ Form data preserved
- ✅ User can retry
- ✅ No duplicate submissions

---

### 13.10 Browser Back Button During SO Creation

**Test Case: TC-EDGE-010 - Browser Navigation Handling**

**Objective:** Verify data handling with browser back button

**Test Steps:**

1. **Fill SO Form**
   - Enter all SO details
   - Do NOT submit

2. **Click Browser Back Button**
   - Navigate away from form
   - Verify unsaved changes warning (if implemented)

3. **Navigate Forward**
   - Click browser forward button
   - Verify form data preserved OR cleared (based on design)

4. **Submit SO**
   - Complete SO creation
   - Click back button
   - Verify cannot resubmit (no duplicate)

**Expected Results:**
- ✅ Unsaved changes warning (optional)
- ✅ Form data handling consistent
- ✅ No duplicate submissions
- ✅ User experience smooth

---

## 14. Data Consistency Verification

### 14.1 SO and Customer Balance Consistency

**Verification Query:**
```sql
-- Verify customer balance matches sum of unpaid SOs
SELECT 
    c.customer_id,
    c.customer_name,
    c.balance_amount as recorded_balance,
    COALESCE(SUM(so.total_amount - so.amount_paid), 0) as calculated_balance,
    c.balance_amount - COALESCE(SUM(so.total_amount - so.amount_paid), 0) as difference
FROM sales.customer c
LEFT JOIN sales.sales_order so ON c.customer_id = so.customer_id 
    AND so.is_deleted = FALSE
WHERE c.is_deleted = FALSE
GROUP BY c.customer_id, c.customer_name, c.balance_amount
HAVING ABS(c.balance_amount - COALESCE(SUM(so.total_amount - so.amount_paid), 0)) > 0.01;
```

**Expected Result:** No rows (all balances match)

---

### 14.2 SO Payment Status Consistency

**Verification Query:**
```sql
-- Verify payment_status matches actual payment amounts
SELECT 
    so.sales_order_id,
    so.order_number,
    so.payment_status,
    so.amount_paid,
    so.effective_total_amount,
    CASE 
        WHEN so.amount_paid >= so.effective_total_amount THEN 'Completed'
        WHEN so.amount_paid > 0 THEN 'Partial'
        ELSE 'Pending'
    END as calculated_status
FROM sales.sales_order so
WHERE so.is_deleted = FALSE
    AND so.payment_status != CASE 
        WHEN so.amount_paid >= so.effective_total_amount THEN 'Completed'
        WHEN so.amount_paid > 0 THEN 'Partial'
        ELSE 'Pending'
    END;
```

**Expected Result:** No rows (all statuses correct)

---

### 14.3 SO Delivery Status Consistency

**Verification Query:**
```sql
-- Verify delivery_status matches actual shipped quantities
WITH delivery_summary AS (
    SELECT 
        sod.sales_order_id,
        COUNT(*) as total_items,
        COUNT(*) FILTER (
            WHERE (sod.quantity - sod.shipped_quantity - sod.returned_quantity) <= 0
            AND (COALESCE(sod.free_quantity, 0) - COALESCE(sod.shipped_free_quantity, 0) - COALESCE(sod.returned_free_quantity, 0)) <= 0
        ) as completed_items
    FROM sales.sales_order_detail sod
    WHERE sod.is_deleted = FALSE
    GROUP BY sod.sales_order_id
)
SELECT 
    so.sales_order_id,
    so.order_number,
    so.delivery_status,
    ds.total_items,
    ds.completed_items,
    CASE 
        WHEN ds.completed_items = ds.total_items THEN 'Completed'
        WHEN ds.completed_items > 0 THEN 'Partial'
        ELSE 'Pending'
    END as calculated_status
FROM sales.sales_order so
JOIN delivery_summary ds ON so.sales_order_id = ds.sales_order_id
WHERE so.is_deleted = FALSE
    AND so.delivery_status != CASE 
        WHEN ds.completed_items = ds.total_items THEN 'Completed'
        WHEN ds.completed_items > 0 THEN 'Partial'
        ELSE 'Pending'
    END;
```

**Expected Result:** No rows (all statuses correct)

---

### 14.4 Batch Allocation Consistency

**Verification Query:**
```sql
-- Verify batch allocations match SO details
SELECT 
    sod.sales_order_detail_id,
    sod.product_id,
    sod.variant_id,
    sod.quantity + COALESCE(sod.free_quantity, 0) as total_quantity,
    COALESCE(SUM(ba.allocated_quantity), 0) as allocated_quantity,
    (sod.quantity + COALESCE(sod.free_quantity, 0)) - COALESCE(SUM(ba.allocated_quantity), 0) as difference
FROM sales.sales_order_detail sod
LEFT JOIN warehouse.batch_allocation ba ON sod.sales_order_detail_id = ba.sales_order_detail_id
WHERE sod.is_deleted = FALSE
GROUP BY sod.sales_order_detail_id, sod.product_id, sod.variant_id, sod.quantity, sod.free_quantity
HAVING ABS((sod.quantity + COALESCE(sod.free_quantity, 0)) - COALESCE(SUM(ba.allocated_quantity), 0)) > 0.01;
```

**Expected Result:** No rows (all allocations match)

---

### 14.5 Inventory Transaction Completeness

**Verification Query:**
```sql
-- Verify all deliveries have corresponding inventory transactions
SELECT 
    sodd.delivery_detail_id,
    sodd.sales_order_id,
    sodd.delivered_quantity,
    it.transaction_id
FROM sales.sales_order_delivery_detail sodd
LEFT JOIN warehouse.inventory_transaction it ON 
    it.reference_type = 'sales_order_delivery' 
    AND it.reference_id = sodd.delivery_detail_id
WHERE sodd.is_deleted = FALSE
    AND it.transaction_id IS NULL;
```

**Expected Result:** No rows (all deliveries logged)

---

## 16. Complete Testing Checklist

### SO Creation Module
- [ ] TC-SO-001: Create basic SO with single product
- [ ] TC-SO-002: Create SO with multiple products
- [ ] TC-SO-003: Create SO with Buy X Get Y scheme
- [ ] TC-SO-004: Create SO with different free product scheme
- [ ] TC-SO-005: Create SO with flat discount scheme
- [ ] TC-SO-006: Create SO with percentage discount scheme
- [ ] TC-SO-007: Create SO with tiered scheme
- [ ] TC-SO-008: Create SO with UOM conversion
- [ ] TC-SO-009: Create SO with insufficient stock (error)
- [ ] TC-SO-010: Create SO with scheme free items exceeding stock (error)

### Payment Processing Module
- [ ] TC-PAY-001: Record full payment
- [ ] TC-PAY-002: Record partial payments
- [ ] TC-PAY-003: Record overpayment
- [ ] TC-PAY-004: Payment after partial return
- [ ] TC-PAY-005: Mixed payment methods
- [ ] TC-PAY-006: Payment date validation
- [ ] TC-PAY-007: Delete payment record
- [ ] TC-PAY-008: Commission status on payment completion
- [ ] TC-PAY-009: Payment when effective total is zero
- [ ] TC-PAY-010: Concurrent payment submissions

### Delivery/Dispatch Module
- [ ] TC-DEL-001: Record full delivery from warehouse
- [ ] TC-DEL-002: Record partial deliveries
- [ ] TC-DEL-003: Deliver billable and free quantities
- [ ] TC-DEL-004: Deliver from DSR storage
- [ ] TC-DEL-005: Attempt over-delivery (error)

### Return & Refund Module
- [ ] TC-RET-001: Process full return
- [ ] TC-RET-002: Process partial returns
- [ ] TC-RET-003: Return billable and free items
- [ ] TC-RET-004: Attempt over-return (error)
- [ ] TC-RET-005: Return partially delivered items
- [ ] TC-RET-006: Verify batch allocation reversal
- [ ] TC-RET-007: Return after full payment
- [ ] TC-RET-008: Return date validation
- [ ] TC-RET-009: Process rejection (undelivered return)
- [ ] TC-RET-010: Concurrent return submissions

### Customer Management Module
- [ ] TC-CUST-001: Customer balance on SO creation
- [ ] TC-CUST-002: Credit limit enforcement
- [ ] TC-CUST-003: Apply store credit to SO
- [ ] TC-CUST-004: Phone number auto-suggestions
- [ ] TC-CUST-005: Customer beat filtering
- [ ] TC-CUST-006: Customer SR assignment validation
- [ ] TC-CUST-007: Multiple customer addresses
- [ ] TC-CUST-008: Balance adjustment on SO deletion
- [ ] TC-CUST-009: SO creation for inactive customer
- [ ] TC-CUST-010: Customer search and filtering

### Scheme Application Module
- [ ] TC-SCH-001: Scheme date range validation
- [ ] TC-SCH-002: Best scheme selection (not stacked)
- [ ] TC-SCH-003: Scheme threshold boundary testing
- [ ] TC-SCH-004: Manual scheme override
- [ ] TC-SCH-005: Variant-specific schemes
- [ ] TC-SCH-006: Claim log creation
- [ ] TC-SCH-007: Scheme with UOM conversion
- [ ] TC-SCH-008: Scheme expiry during SO lifecycle
- [ ] TC-SCH-009: Free item stock validation
- [ ] TC-SCH-010: Scheme applicability (purchase vs sale)

### DSR Operations Module
- [ ] TC-DSR-001: Assign SO to DSR
- [ ] TC-DSR-002: Load SO inventory to DSR storage

### Edge Cases & Error Scenarios
- [ ] TC-EDGE-001: Concurrent SO editing
- [ ] TC-EDGE-002: Delivery with deleted product
- [ ] TC-EDGE-003: Prevent negative inventory
- [ ] TC-EDGE-004: Missing UOM conversion
- [ ] TC-EDGE-005: Expired batch allocation
- [ ] TC-EDGE-006: Cross-company data isolation
- [ ] TC-EDGE-007: SO with 100+ line items
- [ ] TC-EDGE-008: Special characters handling
- [ ] TC-EDGE-009: Network interruption during SO creation
- [ ] TC-EDGE-010: Browser back button handling

### Data Consistency Verification
- [ ] Verify customer balance consistency
- [ ] Verify SO payment status consistency
- [ ] Verify SO delivery status consistency
- [ ] Verify batch allocation consistency
- [ ] Verify inventory transaction completeness

---

## Testing Sign-Off

**Tester Name:** ___________________________  
**Date:** ___________________________  
**Test Environment:** ___________________________  
**Total Test Cases:** 60+  
**Passed:** ___________________________  
**Failed:** ___________________________  
**Blocked:** ___________________________  
**Notes:** ___________________________

---

**Document End**
