## 6. SO Return & Refund Testing

### 6.1 Full Return Processing

**Test Case: TC-RET-001 - Process Full Return**

**Objective:** Verify complete return of all items

**Prerequisites:**
- SO fully delivered (shipped_quantity = quantity for all items)
- SO fully paid (amount_paid = total_amount)
- status: "Completed"

**Test Steps:**

1. **Navigate to Return Form**
   - Open SO details
   - Click "Process Return" button
   - Verify return form opens with all items

2. **Fill Return Details**
   - Return Date: Today
   - Item 1: Return Quantity: 10 (full quantity)
   - Item 2: Return Quantity: 5 (full quantity)
   - Remarks: "Customer dissatisfied with quality"

3. **Submit Return**
   - Click "Process Return" button
   - Verify confirmation dialog
   - Confirm return

4. **Verify SO Updates**
   - Item 1: returned_quantity: 10
   - Item 2: returned_quantity: 5
   - effective_total_amount: 0.00
   - payment_status: "Completed" (auto-set when effective_total = 0)
   - delivery_status: "Completed" (remains completed)
   - status: "Completed"

5. **Verify Stock Restoration**
   - Warehouse stock increased by returned quantities
   - Batch allocations reversed
   - Inventory transaction created (type: return)

6. **Verify Customer Balance**
   - Customer balance reduced by returned amount
   - Or store_credit increased

**Expected Results:**
- ✅ Return records created for all items
- ✅ returned_quantity updated
- ✅ effective_total_amount recalculated (0.00)
- ✅ payment_status auto-set to "Completed"
- ✅ Stock restored to warehouse
- ✅ Batch allocations reversed
- ✅ Customer balance adjusted
- ✅ Inventory transactions logged

**Data Verification:**
```sql
-- Verify return records
SELECT * FROM sales.sales_order_detail 
WHERE sales_order_id = <so_id>;

-- Verify effective total
SELECT total_amount, effective_total_amount 
FROM sales.sales_order 
WHERE sales_order_id = <so_id>;

-- Verify stock restoration
SELECT quantity FROM warehouse.inventory_stock 
WHERE product_id = <product_id> AND location_id = <location_id>;

-- Verify batch reversal
SELECT * FROM warehouse.batch_allocation 
WHERE sales_order_detail_id = <detail_id>;

-- Verify customer balance
SELECT balance_amount, store_credit FROM sales.customer 
WHERE customer_id = <customer_id>;
```

---

### 6.2 Partial Return Processing

**Test Case: TC-RET-002 - Process Partial Return**

**Objective:** Verify partial return handling

**Prerequisites:**
- SO with Item: Widget A, Qty: 100, Shipped: 100, Returned: 0

**Test Steps:**

1. **Record First Partial Return**
   - Return Quantity: 20
   - Remarks: "20 units damaged"
   - Submit return

2. **Verify After First Return**
   - returned_quantity: 20
   - Effective quantity: 80
   - effective_total_amount: 80 × unit_price
   - Stock restored: 20 units

3. **Record Second Partial Return**
   - Return Quantity: 30
   - Remarks: "30 units wrong specification"
   - Submit return

4. **Verify After Second Return**
   - returned_quantity: 50
   - Effective quantity: 50
   - effective_total_amount: 50 × unit_price
   - Stock restored: 50 units total

5. **Verify Payment Status**
   - If amount_paid > effective_total_amount:
     - payment_status: "Completed"
     - Excess becomes customer credit
   - If amount_paid < effective_total_amount:
     - payment_status: "Partial"

**Expected Results:**
- ✅ Multiple return records created
- ✅ returned_quantity accumulates
- ✅ effective_total_amount recalculated after each return
- ✅ Stock restored incrementally
- ✅ payment_status updated based on effective total

---

### 6.3 Return with Free Items

**Test Case: TC-RET-003 - Return Billable and Free Items**

**Objective:** Verify return of both billable and free quantities

**Prerequisites:**
- SO with Item: Widget A, Qty: 10, Free Qty: 2
- All delivered (shipped_quantity: 10, shipped_free_quantity: 2)

**Test Steps:**

1. **Return Both Billable and Free**
   - Return Quantity: 5 (billable)
   - Return Free Quantity: 1 (free)
   - Submit return

2. **Verify Return Records**
   - returned_quantity: 5
   - returned_free_quantity: 1
   - Effective billable: 5
   - Effective free: 1

3. **Verify Stock Restoration**
   - Stock restored: 6 units total (5 billable + 1 free)
   - Batch allocations reversed for 6 units

4. **Verify Amount Calculation**
   - effective_total_amount reduced by: 5 × unit_price
   - Free items don't affect amount

**Expected Results:**
- ✅ Both billable and free quantities returned
- ✅ Stock restored for total (billable + free)
- ✅ Amount calculation excludes free items
- ✅ Batch reversals handle combined quantity

---

### 6.4 Return Exceeding Delivered Quantity

**Test Case: TC-RET-004 - Attempt Over-Return (Error Case)**

**Objective:** Verify validation prevents returning more than delivered

**Prerequisites:**
- SO with Item: Widget A, Qty: 10, Shipped: 10, Returned: 0

**Test Steps:**

1. **Attempt Over-Return**
   - Return Quantity: 15 (exceeds shipped 10)
   - Click "Process Return"

2. **Verify Validation Error**
   - Error message: "Return quantity cannot exceed shipped quantity"
   - Return not processed
   - Form data preserved

3. **Correct and Retry**
   - Update Return Quantity: 10
   - Submit successfully

**Expected Results:**
- ✅ Validation prevents over-return
- ✅ Clear error message
- ✅ Form data not lost
- ✅ User can correct and resubmit

---

### 6.5 Return Before Full Delivery

**Test Case: TC-RET-005 - Return Partially Delivered Items**

**Objective:** Verify return of partially delivered items

**Prerequisites:**
- SO with Item: Widget A, Qty: 100, Shipped: 60, Returned: 0

**Test Steps:**

1. **Return Partial Shipped Quantity**
   - Return Quantity: 20 (out of 60 shipped)
   - Submit return

2. **Verify Return Processing**
   - returned_quantity: 20
   - Effective shipped: 40
   - Remaining to ship: 40 (100 - 60)

3. **Continue Delivery**
   - Deliver remaining: 40
   - Total shipped: 100
   - Total returned: 20
   - Effective quantity: 80

**Expected Results:**
- ✅ Can return before full delivery
- ✅ Return only from shipped quantity
- ✅ Remaining quantity still deliverable
- ✅ Effective quantity calculated correctly

---

### 6.6 Return with Batch Reversal

**Test Case: TC-RET-006 - Verify Batch Allocation Reversal**

**Objective:** Verify batch allocations reversed on return

**Prerequisites:**
- SO delivered using FIFO batch allocation
- Batches: Batch A (50 units), Batch B (50 units)
- Delivered: 60 units (50 from Batch A, 10 from Batch B)

**Test Steps:**

1. **Return 30 Units**
   - Return Quantity: 30
   - Submit return

2. **Verify Batch Reversal**
   - Batch B: 10 units restored (LIFO reversal)
   - Batch A: 20 units restored
   - Batch allocations updated

3. **Verify Stock Restoration**
   - Batch A: +20 units
   - Batch B: +10 units
   - Total: +30 units

**Expected Results:**
- ✅ Batch allocations reversed in LIFO order
- ✅ Stock restored to correct batches
- ✅ Batch quantities updated
- ✅ Allocation records maintained

---

### 6.7 Return After Payment

**Test Case: TC-RET-007 - Return After Full Payment**

**Objective:** Verify return handling when order fully paid

**Prerequisites:**
- SO fully paid (amount_paid: 1000.00)
- Total amount: 1000.00
- payment_status: "Completed"

**Test Steps:**

1. **Return Items Worth 300.00**
   - Return items reducing effective_total to 700.00
   - Submit return

2. **Verify Payment Status**
   - amount_paid: 1000.00 (unchanged)
   - effective_total_amount: 700.00
   - payment_status: "Completed" (paid > effective_total)
   - Overpayment: 300.00

3. **Verify Customer Credit**
   - Customer store_credit increased by 300.00
   - Or balance_amount becomes -300.00

**Expected Results:**
- ✅ payment_status remains "Completed"
- ✅ Overpayment credited to customer
- ✅ Customer can use credit for future orders
- ✅ Balance reflects overpayment

---

### 6.8 Return Date Validation

**Test Case: TC-RET-008 - Return Date Scenarios**

**Objective:** Verify return date validation

**Test Steps:**

1. **Return with Past Date**
   - Return Date: 7 days ago
   - Verify accepted (backdated return)

2. **Return with Future Date**
   - Return Date: Tomorrow
   - Verify validation (should warn or prevent)

3. **Return Before Delivery Date**
   - Return Date: Before delivery date
   - Verify validation (should prevent)

**Expected Results:**
- ✅ Past dates allowed (backdated returns)
- ✅ Future dates validated/prevented
- ✅ Return date must be >= delivery date

---

### 6.9 Return with Rejection

**Test Case: TC-RET-009 - Process Rejection (Undelivered Return)**

**Objective:** Verify rejection of undelivered items

**Prerequisites:**
- SO with Item: Widget A, Qty: 100, Shipped: 60, Returned: 0

**Test Steps:**

1. **Reject Undelivered Items**
   - Rejected Quantity: 40 (from unshipped)
   - Remarks: "Customer cancelled remaining order"
   - Submit rejection

2. **Verify Rejection Processing**
   - rejected_quantity: 40
   - Effective quantity: 60 (shipped - returned)
   - No stock restoration (never left warehouse)

3. **Verify Batch Allocation**
   - Batch allocation for 40 units released
   - Stock remains in warehouse

**Expected Results:**
- ✅ Rejection reduces effective quantity
- ✅ No stock restoration (never shipped)
- ✅ Batch allocations released
- ✅ effective_total_amount recalculated

---

### 6.10 Concurrent Return Processing

**Test Case: TC-RET-010 - Concurrent Return Submissions**

**Objective:** Verify race condition handling in return processing

**Test Steps:**

1. **Simulate Concurrent Returns**
   - Open SO in 2 browser tabs
   - Tab 1: Return 20 units
   - Tab 2: Return 30 units (simultaneously)
   - Submit both

2. **Verify Data Integrity**
   - Both returns processed OR one fails with error
   - returned_quantity correct (not double-counted)
   - Stock restoration accurate
   - No data corruption

**Expected Results:**
- ✅ Row-level locking prevents race conditions
- ✅ Returns processed sequentially
- ✅ returned_quantity calculated correctly
- ✅ Stock restoration accurate

---

## 7. Customer Management in SO Context

### 7.1 Customer Balance Tracking

**Test Case: TC-CUST-001 - Customer Balance on SO Creation**

**Objective:** Verify customer balance increases on SO creation

**Prerequisites:**
- Customer "ABC Store" with balance_amount: 500.00

**Test Steps:**

1. **Create SO for Customer**
   - Customer: ABC Store
   - Total Amount: 1000.00
   - Submit SO

2. **Verify Customer Balance**
   - balance_amount: 1500.00 (500 + 1000)
   - Balance increased by SO total

3. **Record Payment**
   - Amount Paid: 600.00
   - Submit payment

4. **Verify Balance After Payment**
   - balance_amount: 1500.00 (unchanged)
   - Payment offsets order, doesn't reduce balance directly

**Expected Results:**
- ✅ Balance increases on SO creation
- ✅ Balance = previous balance + SO total
- ✅ Payment doesn't directly reduce balance
- ✅ Balance represents total outstanding

---

### 7.2 Customer Credit Limit Validation

**Test Case: TC-CUST-002 - Credit Limit Enforcement**

**Objective:** Verify credit limit validation on SO creation

**Prerequisites:**
- Customer "ABC Store" with:
  - credit_limit: 5000.00
  - balance_amount: 4500.00

**Test Steps:**

1. **Attempt SO Exceeding Credit Limit**
   - Customer: ABC Store
   - Total Amount: 1000.00
   - Total exposure: 5500.00 (4500 + 1000)
   - Click "Create Sales Order"

2. **Verify Credit Limit Warning**
   - Warning message: "Customer credit limit exceeded"
   - Shows: Limit: 5000, Current: 4500, New: 5500
   - Option to proceed with override (if authorized)

3. **Test Within Credit Limit**
   - Update Total Amount: 500.00
   - Total exposure: 5000.00 (within limit)
   - SO created successfully

**Expected Results:**
- ✅ Credit limit validated on SO creation
- ✅ Warning shown when limit exceeded
- ✅ Authorized users can override
- ✅ Within-limit orders proceed normally

---

### 7.3 Customer Store Credit Usage

**Test Case: TC-CUST-003 - Apply Store Credit to SO**

**Objective:** Verify store credit application

**Prerequisites:**
- Customer "ABC Store" with store_credit: 300.00
- SO with total_amount: 1000.00

**Test Steps:**

1. **Apply Store Credit**
   - Open payment form
   - Option to apply store credit
   - Apply: 300.00
   - Record additional payment: 700.00

2. **Verify Credit Application**
   - store_credit: 0.00 (fully used)
   - amount_paid: 1000.00
   - payment_status: "Completed"

3. **Verify Payment Records**
   - Payment 1: 300.00 (method: "Store Credit")
   - Payment 2: 700.00 (method: "Cash")

**Expected Results:**
- ✅ Store credit applied to payment
- ✅ Credit deducted from customer account
- ✅ Separate payment record for credit
- ✅ Remaining amount paid by other method

---

### 7.4 Customer Phone Number Suggestions

**Test Case: TC-CUST-004 - Phone Number Auto-Suggestions**

**Objective:** Verify phone number suggestion feature

**Prerequisites:**
- Customer "ABC Store" with phone: "01712345678"
- Phone suggestions: "01812345678", "01912345678"

**Test Steps:**

1. **Create SO for Customer**
   - Select Customer: ABC Store
   - Verify primary phone displayed

2. **View Phone Suggestions**
   - Click phone number field
   - Verify suggestions dropdown
   - Shows all associated phone numbers

3. **Select Alternative Phone**
   - Select "01812345678" from suggestions
   - Verify selected phone used for SO

**Expected Results:**
- ✅ Primary phone auto-populated
- ✅ Suggestions dropdown shows all phones
- ✅ Can select alternative phone
- ✅ Selected phone saved with SO

---

### 7.5 Customer Beat Assignment

**Test Case: TC-CUST-005 - Customer Beat Filtering**

**Objective:** Verify beat-based customer filtering

**Prerequisites:**
- Beat "North Zone" with 5 customers
- Beat "South Zone" with 3 customers

**Test Steps:**

1. **Filter Customers by Beat**
   - Open customer dropdown
   - Filter by Beat: "North Zone"
   - Verify only 5 customers shown

2. **Create SO for Beat Customer**
   - Select customer from filtered list
   - Verify beat information displayed
   - Create SO successfully

**Expected Results:**
- ✅ Customers filtered by beat
- ✅ Beat information displayed
- ✅ SO creation works with beat context

---

### 7.6 Customer SR Assignment

**Test Case: TC-CUST-006 - Customer SR Assignment Validation**

**Objective:** Verify SR-customer assignment in SO context

**Prerequisites:**
- Customer "ABC Store" assigned to SR "John Doe"
- SR "John Doe" has product assignments

**Test Steps:**

1. **Create SO for SR-Assigned Customer**
   - Select Customer: ABC Store
   - Verify SR information displayed
   - Add products from SR's assignment

2. **Verify SR Context**
   - SR name shown in SO details
   - Commission calculation considers SR
   - SR can view SO in their dashboard

**Expected Results:**
- ✅ SR assignment displayed
- ✅ SR context maintained in SO
- ✅ Commission linked to SR

---

### 7.7 Customer Address Management

**Test Case: TC-CUST-007 - Multiple Customer Addresses**

**Objective:** Verify multiple address handling

**Prerequisites:**
- Customer "ABC Store" with:
  - Primary Address: "123 Main St"
  - Delivery Address: "456 Warehouse Rd"

**Test Steps:**

1. **Create SO with Delivery Address**
   - Select Customer: ABC Store
   - Choose Delivery Address: "456 Warehouse Rd"
   - Create SO

2. **Verify Address Selection**
   - SO shows delivery address
   - Delivery documents use correct address

**Expected Results:**
- ✅ Multiple addresses supported
- ✅ Can select delivery address
- ✅ Correct address used for delivery

---

### 7.8 Customer Balance Adjustment on SO Deletion

**Test Case: TC-CUST-008 - Balance Adjustment on SO Deletion**

**Objective:** Verify balance adjustment when SO deleted

**Prerequisites:**
- Customer balance: 1500.00
- SO with total_amount: 1000.00

**Test Steps:**

1. **Delete SO**
   - Open SO details
   - Click "Delete" button
   - Confirm deletion

2. **Verify Balance Adjustment**
   - balance_amount: 500.00 (1500 - 1000)
   - Balance reduced by SO total

**Expected Results:**
- ✅ Balance adjusted on SO deletion
- ✅ Balance = previous balance - SO total
- ✅ Customer balance accurate

---

### 7.9 Customer Inactive Status

**Test Case: TC-CUST-009 - SO Creation for Inactive Customer**

**Objective:** Verify validation for inactive customers

**Prerequisites:**
- Customer "ABC Store" with is_active: false

**Test Steps:**

1. **Attempt SO for Inactive Customer**
   - Try to select inactive customer
   - Verify customer not in dropdown OR
   - Warning shown if selected

2. **Activate Customer**
   - Activate customer
   - Retry SO creation
   - SO created successfully

**Expected Results:**
- ✅ Inactive customers filtered/warned
- ✅ Cannot create SO for inactive customer
- ✅ Activation enables SO creation

---

### 7.10 Customer Search and Filtering

**Test Case: TC-CUST-010 - Customer Search in SO Creation**

**Objective:** Verify customer search functionality

**Test Steps:**

1. **Search by Customer Name**
   - Type "ABC" in customer field
   - Verify matching customers shown
   - Select from results

2. **Search by Customer Code**
   - Type "CUST-001" in customer field
   - Verify customer found by code
   - Select customer

3. **Search by Phone Number**
   - Type "01712345678"
   - Verify customer found by phone
   - Select customer

**Expected Results:**
- ✅ Search by name works
- ✅ Search by code works
- ✅ Search by phone works
- ✅ Fast and responsive search

---

