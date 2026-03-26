## 4. SO Payment Processing Testing

### 4.1 Standard Payment Recording

**Test Case: TC-PAY-001 - Record Full Payment**

**Objective:** Verify full payment recording and status updates

**Prerequisites:**
- SO exists with total_amount: 1000.00
- amount_paid: 0.00
- payment_status: "Pending"
- status: "Open"

**Test Steps:**

1. **Navigate to Payment Form**
   - Open SO details page
   - Click "Record Payment" button
   - Verify payment form opens

2. **Fill Payment Details**
   - Payment Date: Today
   - Amount Paid: 1000.00
   - Payment Method: "Cash"
   - Transaction Reference: "CASH-001"
   - Remarks: "Full payment received"

3. **Submit Payment**
   - Click "Record Payment" button
   - Verify success message
   - Verify form closes

4. **Verify SO Updates**
   - amount_paid: 1000.00
   - payment_status: "Completed"
   - status: "Partial" (if delivery pending) or "Completed" (if delivered)

5. **Verify Customer Balance**
   - Customer balance unchanged (payment offsets order amount)

**Expected Results:**
- ✅ Payment record created
- ✅ SO amount_paid updated to 1000.00
- ✅ payment_status changed to "Completed"
- ✅ Unified status updated based on delivery status
- ✅ Customer balance remains correct
- ✅ Payment appears in payment history

**Data Verification:**
```sql
-- Verify payment record
SELECT * FROM sales.sales_order_payment_detail 
WHERE sales_order_id = <so_id>;

-- Verify SO updated
SELECT amount_paid, payment_status, status 
FROM sales.sales_order 
WHERE sales_order_id = <so_id>;

-- Verify customer balance
SELECT balance_amount FROM sales.customer 
WHERE customer_id = <customer_id>;
```

---

### 4.2 Partial Payment Recording

**Test Case: TC-PAY-002 - Record Partial Payment**

**Objective:** Verify partial payment handling

**Prerequisites:**
- SO with total_amount: 1000.00
- amount_paid: 0.00

**Test Steps:**

1. **Record First Partial Payment**
   - Amount Paid: 400.00
   - Payment Method: "Cash"
   - Submit payment

2. **Verify Status After First Payment**
   - amount_paid: 400.00
   - payment_status: "Partial"
   - status: "Partial"

3. **Record Second Partial Payment**
   - Amount Paid: 300.00
   - Payment Method: "Bank Transfer"
   - Submit payment

4. **Verify Status After Second Payment**
   - amount_paid: 700.00
   - payment_status: "Partial" (still not complete)
   - status: "Partial"

5. **Record Final Payment**
   - Amount Paid: 300.00
   - Payment Method: "Cash"
   - Submit payment

6. **Verify Final Status**
   - amount_paid: 1000.00
   - payment_status: "Completed"
   - status: "Partial" or "Completed" (based on delivery)

**Expected Results:**
- ✅ Multiple payment records created
- ✅ amount_paid accumulates correctly
- ✅ payment_status transitions: Pending → Partial → Completed
- ✅ Each payment method tracked separately
- ✅ Payment history shows all transactions

---

### 4.3 Overpayment Handling

**Test Case: TC-PAY-003 - Record Overpayment**

**Objective:** Verify overpayment handling and customer credit

**Prerequisites:**
- SO with total_amount: 1000.00
- amount_paid: 0.00

**Test Steps:**

1. **Attempt Overpayment Without Remarks**
   - Amount Paid: 1200.00 (exceeds total by 200)
   - Remarks: (leave empty)
   - Click "Record Payment"
   - Verify error: "Remarks required for overpayment"

2. **Record Overpayment With Remarks**
   - Amount Paid: 1200.00
   - Remarks: "Customer advance payment for future orders"
   - Click "Record Payment"
   - Verify confirmation dialog appears
   - Confirm overpayment

3. **Verify SO Updates**
   - amount_paid: 1200.00
   - payment_status: "Completed"
   - status: "Partial" or "Completed"

4. **Verify Customer Credit**
   - Customer store_credit increased by 200.00
   - Or balance_amount becomes negative (-200.00)

**Expected Results:**
- ✅ Overpayment requires remarks
- ✅ Confirmation dialog for overpayment
- ✅ Overpayment recorded successfully
- ✅ Excess amount credited to customer
- ✅ payment_status marked "Completed"

---

### 4.4 Payment with Returns (Effective Total)

**Test Case: TC-PAY-004 - Payment After Partial Return**

**Objective:** Verify payment status based on effective total

**Prerequisites:**
- SO with total_amount: 1000.00
- 2 items returned, reducing effective_total to 800.00
- amount_paid: 0.00

**Test Steps:**

1. **Record Payment Equal to Effective Total**
   - Amount Paid: 800.00
   - Submit payment

2. **Verify Payment Status**
   - amount_paid: 800.00
   - effective_total_amount: 800.00
   - payment_status: "Completed" (paid = effective total)
   - status: "Completed" (if delivered)

3. **Verify Customer Balance**
   - Balance reflects effective total, not original total

**Expected Results:**
- ✅ Payment status based on effective_total, not total_amount
- ✅ payment_status "Completed" when paid >= effective_total
- ✅ Customer balance calculated correctly
- ✅ Returns reduce payment requirement

---

### 4.5 Multiple Payment Methods

**Test Case: TC-PAY-005 - Mixed Payment Methods**

**Objective:** Verify tracking of different payment methods

**Test Steps:**

1. **Record Cash Payment**
   - Amount: 300.00
   - Method: "Cash"
   - Reference: "CASH-001"

2. **Record Bank Transfer**
   - Amount: 400.00
   - Method: "Bank Transfer"
   - Reference: "TXN-123456"

3. **Record Credit Card Payment**
   - Amount: 300.00
   - Method: "Credit Card"
   - Reference: "CC-789012"

4. **Verify Payment History**
   - 3 payment records with different methods
   - Each with unique reference
   - Total: 1000.00

**Expected Results:**
- ✅ Each payment method tracked separately
- ✅ Transaction references stored
- ✅ Payment history shows all methods
- ✅ Total amount calculated correctly

---

### 4.6 Payment Date Validation

**Test Case: TC-PAY-006 - Payment Date Scenarios**

**Objective:** Verify payment date handling

**Test Steps:**

1. **Payment with Past Date**
   - Payment Date: 7 days ago
   - Amount: 500.00
   - Verify accepted (backdated payment)

2. **Payment with Future Date**
   - Payment Date: Tomorrow
   - Amount: 500.00
   - Verify validation (should warn or prevent)

3. **Payment with Today's Date**
   - Payment Date: Today
   - Amount: 500.00
   - Verify accepted (standard case)

**Expected Results:**
- ✅ Past dates allowed (backdated payments)
- ✅ Future dates validated/prevented
- ✅ Today's date is default

---

### 4.7 Payment Deletion/Reversal

**Test Case: TC-PAY-007 - Delete Payment Record**

**Objective:** Verify payment deletion and status rollback

**Prerequisites:**
- SO with 2 payments: 400.00 and 600.00
- amount_paid: 1000.00
- payment_status: "Completed"

**Test Steps:**

1. **Delete Second Payment**
   - Open payment history
   - Click delete on 600.00 payment
   - Confirm deletion

2. **Verify SO Updates**
   - amount_paid: 400.00
   - payment_status: "Partial"
   - status: "Partial"

3. **Verify Customer Balance**
   - Balance adjusted for deleted payment

**Expected Results:**
- ✅ Payment record deleted
- ✅ amount_paid recalculated
- ✅ payment_status rolled back
- ✅ Customer balance adjusted
- ✅ Status updated correctly

---

### 4.8 Commission Status on Payment Completion

**Test Case: TC-PAY-008 - Commission Status Update**

**Objective:** Verify commission status changes on payment completion

**Prerequisites:**
- SO with commission_disbursed: "pending"
- Delivery completed
- Payment pending

**Test Steps:**

1. **Complete Payment**
   - Record full payment
   - Verify payment_status: "Completed"

2. **Verify Commission Status**
   - commission_disbursed: "Ready" (changed from "pending")
   - SO eligible for commission calculation

3. **Verify SR Order Sync**
   - If consolidated from SR orders
   - SR order commission_disbursed also updated

**Expected Results:**
- ✅ commission_disbursed changes to "Ready" on completion
- ✅ Only when both payment and delivery completed
- ✅ SR orders synced if applicable

---

### 4.9 Payment with Zero Effective Total

**Test Case: TC-PAY-009 - Payment When Effective Total is Zero**

**Objective:** Verify automatic completion when all items returned

**Prerequisites:**
- SO with total_amount: 1000.00
- All items returned
- effective_total_amount: 0.00

**Test Steps:**

1. **Check Payment Status**
   - Verify payment_status: "Completed" (auto-set)
   - No payment required

2. **Attempt to Record Payment**
   - Payment form should show effective total: 0.00
   - Remaining balance: 0.00
   - Payment not needed

**Expected Results:**
- ✅ payment_status auto-set to "Completed" when effective_total = 0
- ✅ No payment recording needed
- ✅ Status reflects completion

---

### 4.10 Concurrent Payment Recording

**Test Case: TC-PAY-010 - Concurrent Payment Submissions**

**Objective:** Verify race condition handling in payment recording

**Test Steps:**

1. **Simulate Concurrent Payments**
   - Open SO in 2 browser tabs
   - Tab 1: Record payment 600.00
   - Tab 2: Record payment 500.00 (simultaneously)
   - Submit both

2. **Verify Data Integrity**
   - Both payments recorded OR one fails with error
   - amount_paid correct (not double-counted)
   - No data corruption

**Expected Results:**
- ✅ Row-level locking prevents race conditions
- ✅ Payments processed sequentially
- ✅ amount_paid calculated correctly
- ✅ No lost updates

---

## 5. SO Delivery/Dispatch Testing

### 5.1 Standard Warehouse Delivery

**Test Case: TC-DEL-001 - Record Full Delivery from Warehouse**

**Objective:** Verify standard delivery recording and stock deduction

**Prerequisites:**
- SO with 2 items:
  - Item 1: Widget A, Qty: 10, Shipped: 0
  - Item 2: Widget B, Qty: 5, Shipped: 0
- Warehouse stock sufficient
- delivery_status: "Pending"

**Test Steps:**

1. **Navigate to Delivery Form**
   - Open SO details
   - Click "Record Delivery" button
   - Verify delivery form opens

2. **Fill Delivery Details**
   - Delivery Date: Today
   - Item 1 Delivered Quantity: 10
   - Item 2 Delivered Quantity: 5
   - Remarks: "Delivered via company truck"

3. **Submit Delivery**
   - Click "Record Delivery" button
   - Verify success message

4. **Verify SO Updates**
   - Item 1: shipped_quantity: 10
   - Item 2: shipped_quantity: 5
   - delivery_status: "Completed"
   - status: "Partial" or "Completed" (based on payment)

5. **Verify Stock Deduction**
   - Warehouse stock reduced by delivered quantities
   - Batch allocations consumed
   - Inventory transaction created

**Expected Results:**
- ✅ Delivery records created for both items
- ✅ shipped_quantity updated
- ✅ delivery_status changed to "Completed"
- ✅ Warehouse stock deducted
- ✅ Batch allocations consumed
- ✅ Inventory transactions logged

**Data Verification:**
```sql
-- Verify delivery records
SELECT * FROM sales.sales_order_delivery_detail 
WHERE sales_order_id = <so_id>;

-- Verify shipped quantities
SELECT product_id, quantity, shipped_quantity 
FROM sales.sales_order_detail 
WHERE sales_order_id = <so_id>;

-- Verify stock deduction
SELECT quantity FROM warehouse.inventory_stock 
WHERE product_id = <product_id> AND location_id = <location_id>;

-- Verify batch consumption
SELECT * FROM warehouse.batch_allocation 
WHERE sales_order_detail_id = <detail_id>;

-- Verify inventory transaction
SELECT * FROM warehouse.inventory_transaction 
WHERE reference_type = 'sales_order' AND reference_id = <so_id>;
```

---

### 5.2 Partial Delivery

**Test Case: TC-DEL-002 - Record Partial Delivery**

**Objective:** Verify partial delivery handling

**Prerequisites:**
- SO with Item: Widget A, Qty: 100, Shipped: 0

**Test Steps:**

1. **Record First Partial Delivery**
   - Delivered Quantity: 40
   - Submit delivery

2. **Verify Status After First Delivery**
   - shipped_quantity: 40
   - Remaining: 60
   - delivery_status: "Partial"

3. **Record Second Partial Delivery**
   - Delivered Quantity: 30
   - Submit delivery

4. **Verify Status After Second Delivery**
   - shipped_quantity: 70
   - Remaining: 30
   - delivery_status: "Partial"

5. **Record Final Delivery**
   - Delivered Quantity: 30
   - Submit delivery

6. **Verify Final Status**
   - shipped_quantity: 100
   - Remaining: 0
   - delivery_status: "Completed"

**Expected Results:**
- ✅ Multiple delivery records created
- ✅ shipped_quantity accumulates correctly
- ✅ delivery_status transitions: Pending → Partial → Completed
- ✅ Stock deducted incrementally
- ✅ Batch allocations consumed progressively

---

### 5.3 Delivery with Free Items

**Test Case: TC-DEL-003 - Deliver Billable and Free Quantities**

**Objective:** Verify delivery of both billable and free items

**Prerequisites:**
- SO with Item: Widget A, Qty: 10, Free Qty: 2
- Total to deliver: 12 units

**Test Steps:**

1. **Record Delivery**
   - Delivered Quantity: 10 (billable)
   - Delivered Free Quantity: 2 (free)
   - Submit delivery

2. **Verify Delivery Records**
   - delivered_quantity: 10
   - delivered_free_quantity: 2
   - Total stock deducted: 12 units

3. **Verify Stock Deduction**
   - Warehouse stock reduced by 12 units
   - Batch allocation consumed for 12 units

**Expected Results:**
- ✅ Both billable and free quantities delivered
- ✅ Stock deducted for total (billable + free)
- ✅ Delivery record tracks both separately
- ✅ Batch allocation handles combined quantity

---

### 5.4 DSR Delivery

**Test Case: TC-DEL-004 - Deliver from DSR Storage**

**Objective:** Verify delivery from DSR-loaded stock

**Prerequisites:**
- SO assigned to DSR
- SO inventory loaded into DSR storage
- DSR has sufficient stock

**Test Steps:**

1. **Verify DSR Assignment**
   - SO has dsr_assignment record
   - is_loaded: true
   - DSR storage has stock

2. **Record DSR Delivery**
   - Login as DSR user
   - Open assigned SO
   - Record delivery: Qty 10
   - Submit delivery

3. **Verify Stock Source**
   - DSR storage stock deducted (not warehouse)
   - DSR batch allocation consumed
   - Warehouse stock unchanged

4. **Verify DSR Payment Tracking**
   - DSR payment_on_hand increased by SO amount
   - DSR responsible for collecting payment

**Expected Results:**
- ✅ Delivery from DSR storage, not warehouse
- ✅ DSR stock deducted correctly
- ✅ DSR batch allocations consumed
- ✅ DSR payment_on_hand updated
- ✅ Warehouse stock unchanged

---

### 5.5 Delivery Exceeding Ordered Quantity

**Test Case: TC-DEL-005 - Attempt Over-Delivery (Error Case)**

**Objective:** Verify validation prevents over-delivery

**Prerequisites:**
- SO with Item: Widget A, Qty: 10, Shipped: 0

**Test Steps:**

1. **Attempt Over-Delivery**
   - Delivered Quantity: 15 (exceeds ordered 10)
   - Click "Record Delivery"

2. **Verify Validation Error**
   - Error message: "Delivered quantity cannot exceed ordered quantity"
   - Delivery not recorded
   - Form data preserved

3. **Correct and Retry**
   - Update Delivered Quantity: 10
   - Submit successfully

**Expected Results:**
- ✅ Validation prevents over-delivery
- ✅ Clear error message
- ✅ Form data not lost
- ✅ User can correct and resubmit

---

