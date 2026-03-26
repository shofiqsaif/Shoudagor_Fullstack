## 8. Scheme Application in SO Testing

### 8.1 Scheme Eligibility Validation

**Test Case: TC-SCH-001 - Verify Scheme Date Range Validation**

**Objective:** Verify schemes only apply within active date range

**Prerequisites:**
- Scheme A: Active (start: yesterday, end: tomorrow)
- Scheme B: Expired (start: 30 days ago, end: yesterday)
- Scheme C: Future (start: tomorrow, end: next week)

**Test Steps:**

1. **Create SO with Active Scheme Product**
   - Add product eligible for Scheme A
   - Verify scheme applied automatically

2. **Create SO with Expired Scheme Product**
   - Add product eligible for Scheme B
   - Verify scheme NOT applied
   - No free items or discounts

3. **Create SO with Future Scheme Product**
   - Add product eligible for Scheme C
   - Verify scheme NOT applied

**Expected Results:**
- ✅ Only active schemes applied
- ✅ Expired schemes ignored
- ✅ Future schemes ignored
- ✅ Date validation accurate

---

### 8.2 Multiple Schemes on Same Product

**Test Case: TC-SCH-002 - Best Scheme Selection**

**Objective:** Verify best scheme selected, not stacked

**Prerequisites:**
- Product "Widget A" eligible for:
  - Scheme A: Buy 10 Get 2 Free
  - Scheme B: Buy 10 Get 5% Discount
  - Scheme C: Buy 10 Get 1 Free

**Test Steps:**

1. **Create SO with Qty 10**
   - Add Widget A, Qty: 10
   - Verify only ONE scheme applied
   - Verify BEST scheme selected (highest value)

2. **Verify Scheme Selection Logic**
   - Calculate value of each scheme
   - Scheme A value: 2 × unit_price
   - Scheme B value: 5% of total
   - Best scheme applied

**Expected Results:**
- ✅ Only one scheme applied per product
- ✅ Best scheme selected automatically
- ✅ Schemes not stacked
- ✅ Value-based selection

---

### 8.3 Scheme Threshold Testing

**Test Case: TC-SCH-003 - Threshold Boundary Testing**

**Objective:** Verify scheme threshold boundaries

**Prerequisites:**
- Scheme: Buy 10 Get 2 Free (threshold: 10)

**Test Steps:**

1. **Test Below Threshold (Qty: 9)**
   - Add product, Qty: 9
   - Verify scheme NOT applied
   - free_quantity: 0

2. **Test At Threshold (Qty: 10)**
   - Update Qty: 10
   - Verify scheme applied
   - free_quantity: 2

3. **Test Above Threshold (Qty: 11)**
   - Update Qty: 11
   - Verify scheme applied
   - free_quantity: 2 (not 2.2)

4. **Test Multiple Threshold (Qty: 20)**
   - Update Qty: 20
   - Verify scheme applied twice
   - free_quantity: 4 (2 × 2)

**Expected Results:**
- ✅ Scheme not applied below threshold
- ✅ Scheme applied at exact threshold
- ✅ Scheme applied above threshold
- ✅ Multiple applications for higher quantities

---

### 8.4 Scheme Manual Override

**Test Case: TC-SCH-004 - Manual Scheme Override**

**Objective:** Verify manual scheme selection/override

**Test Steps:**

1. **Auto-Applied Scheme**
   - Add product with auto-applied scheme
   - Verify scheme applied

2. **Override with Different Scheme**
   - Click "Change Scheme" button
   - Select different scheme from dropdown
   - Verify new scheme applied
   - Previous scheme removed

3. **Remove Scheme**
   - Click "Remove Scheme" button
   - Verify scheme removed
   - No free items or discounts

4. **Submit SO with Override**
   - Create SO with manual override
   - Verify override preserved
   - Claim log shows manual override

**Expected Results:**
- ✅ Can override auto-applied scheme
- ✅ Can remove scheme manually
- ✅ Override preserved on submission
- ✅ Claim log tracks manual changes

---

### 8.5 Scheme with Product Variant

**Test Case: TC-SCH-005 - Variant-Specific Schemes**

**Objective:** Verify schemes specific to product variants

**Prerequisites:**
- Product "Widget A" with variants: Small, Medium, Large
- Scheme applies only to "Large" variant

**Test Steps:**

1. **Add Small Variant**
   - Select Widget A - Small
   - Qty: 10
   - Verify scheme NOT applied

2. **Add Large Variant**
   - Select Widget A - Large
   - Qty: 10
   - Verify scheme applied

3. **Mixed Variants in Same SO**
   - Line 1: Small, Qty: 10 (no scheme)
   - Line 2: Large, Qty: 10 (scheme applied)
   - Verify correct application

**Expected Results:**
- ✅ Variant-specific schemes work
- ✅ Non-eligible variants excluded
- ✅ Mixed variants handled correctly

---

### 8.6 Scheme Claim Log Verification

**Test Case: TC-SCH-006 - Claim Log Creation**

**Objective:** Verify claim log entries for scheme application

**Test Steps:**

1. **Create SO with Scheme**
   - Add product with scheme
   - Submit SO

2. **Verify Claim Log Entry**
   - Check inventory.claim_log table
   - Verify entry created with:
     - sales_order_id
     - scheme_id
     - product_id, variant_id
     - quantity_claimed
     - free_quantity or discount_amount
     - claim_date

3. **Verify Log Immutability**
   - Attempt to modify claim log
   - Verify log is read-only

**Expected Results:**
- ✅ Claim log entry created
- ✅ All details captured
- ✅ Log is immutable
- ✅ Audit trail maintained

---

### 8.7 Scheme with UOM Conversion

**Test Case: TC-SCH-007 - Scheme with Different UOMs**

**Objective:** Verify scheme application with UOM conversion

**Prerequisites:**
- Scheme: Buy 120 Pieces Get 12 Free
- Product has UOMs: Piece (base), Box (12 pieces)

**Test Steps:**

1. **Order in Box UOM**
   - Add product, UOM: Box, Qty: 10
   - System converts: 10 boxes = 120 pieces
   - Verify scheme applied
   - free_quantity: 12 pieces (or 1 box)

2. **Verify Free Quantity UOM**
   - Free quantity displayed in same UOM as ordered
   - If ordered in boxes, free shown in boxes

**Expected Results:**
- ✅ UOM conversion for threshold check
- ✅ Scheme applied correctly
- ✅ Free quantity in consistent UOM

---

### 8.8 Scheme Expiry During SO Lifecycle

**Test Case: TC-SCH-008 - Scheme Expires After SO Creation**

**Objective:** Verify scheme remains applied even after expiry

**Prerequisites:**
- Scheme expires tomorrow
- SO created today with scheme applied

**Test Steps:**

1. **Create SO Today**
   - Add product with scheme
   - Scheme applied
   - Submit SO

2. **Wait Until Tomorrow (Scheme Expired)**
   - Scheme now expired

3. **Edit SO After Expiry**
   - Open SO for editing
   - Verify scheme still applied
   - Scheme preserved from creation

4. **Verify New SO Cannot Use Expired Scheme**
   - Create new SO tomorrow
   - Same product
   - Scheme NOT applied (expired)

**Expected Results:**
- ✅ Scheme preserved on existing SO
- ✅ Expired scheme not applied to new SOs
- ✅ Historical data integrity maintained

---

### 8.9 Scheme with Insufficient Free Stock

**Test Case: TC-SCH-009 - Free Item Stock Validation**

**Objective:** Verify stock validation includes free items

**Prerequisites:**
- Scheme: Buy 10 Widget A Get 5 Widget B Free
- Widget A stock: 100 units
- Widget B stock: 3 units (insufficient for free items)

**Test Steps:**

1. **Attempt SO with Insufficient Free Stock**
   - Add Widget A, Qty: 10
   - Scheme requires 5 Widget B free
   - Available Widget B: 3 units
   - Click "Create Sales Order"

2. **Verify Stock Validation Error**
   - Error: "Insufficient stock for free item Widget B"
   - Shows: Required: 5, Available: 3
   - SO not created

3. **Adjust or Remove Scheme**
   - Option 1: Reduce quantity to match available free stock
   - Option 2: Remove scheme manually
   - Create SO successfully

**Expected Results:**
- ✅ Stock validated for free items
- ✅ Clear error message
- ✅ User can adjust or remove scheme
- ✅ Prevents overselling free items

---

### 8.10 Scheme Applicable To (Purchase vs Sale)

**Test Case: TC-SCH-010 - Scheme Applicability Validation**

**Objective:** Verify schemes only apply to correct transaction type

**Prerequisites:**
- Scheme A: applicable_to = "sale"
- Scheme B: applicable_to = "purchase"

**Test Steps:**

1. **Create Sales Order**
   - Add product eligible for Scheme A (sale)
   - Verify Scheme A applied
   - Scheme B NOT applied (purchase-only)

2. **Create Purchase Order**
   - Add same product
   - Verify Scheme B applied (purchase)
   - Scheme A NOT applied (sale-only)

**Expected Results:**
- ✅ Sale schemes only apply to SOs
- ✅ Purchase schemes only apply to POs
- ✅ Correct filtering by applicable_to

---

## 9. DSR Assignment & Loading Testing

### 9.1 DSR Assignment to SO

**Test Case: TC-DSR-001 - Assign SO to DSR**

**Objective:** Verify DSR assignment process

**Prerequisites:**
- SO created with status "Open"
- DSR "John Doe" active and available

**Test Steps:**

1. **Open DSR Assignment Form**
   - Open SO details
   - Click "Assign to DSR" button
   - Verify assignment form opens

2. **Select DSR**
   - Select DSR: John Doe
   - Add Notes: "Deliver by end of day"
   - Submit assignment

3. **Verify Assignment Created**
   - DSRSOAssignment record created
   - SO shows DSR assignment
   - DSR can see SO in their dashboard

4. **Verify SO Status**
   - SO status remains "Open"
   - is_loaded: false (not yet loaded)

**Expected Results:**
- ✅ Assignment created successfully
- ✅ SO linked to DSR
- ✅ DSR can view assigned SO
- ✅ Notes captured

**Data Verification:**
```sql
-- Verify assignment
SELECT * FROM sales.dsr_so_assignment 
WHERE sales_order_id = <so_id>;

-- Verify DSR can see SO
SELECT * FROM sales.sales_order so
JOIN sales.dsr_so_assignment dsa ON so.sales_order_id = dsa.sales_order_id
WHERE dsa.dsr_id = <dsr_id>;
```

---

### 9.2 DSR Loading Process

**Test Case: TC-DSR-002 - Load SO Inventory to DSR Storage**

**Objective:** Verify inventory loading from warehouse to DSR storage

**Prerequisites:**
- SO assigned to DSR
- SO has 2 items: Widget A (10 units), Widget B (5 units)
- Warehouse has sufficient stock

**Test Steps:**

1. **Initiate Loading Process**
   - Login as warehouse user
   - Open DSR loading interface
   - Select DSR: John Doe
   - Select SO to load

2. **Verify Loading Details**
   - Shows all SO items
   - Shows warehouse stock availability
   - Shows DSR current stock

3. **Execute Loading**
   - Click "Load to DSR" button
   - Confirm loading

4. **Verify Stock Transfer**
   - Warehouse stock reduced: Widget A (-10), Widget B (-5)
   - DSR storage stock increased: Widget A (+10), Widget B (+5)
   - Stock transfer record created

5. **Verify SO Update**
   - is_loaded: true
   - loaded_by_dsr_id: <dsr_id>
   - loaded_at: <timestamp>

6. **Verify DSR Batch Allocation**
   - DSR batch allocations created
   - Linked to SO details

**Expected Results:**
- ✅ Stock transferred from warehouse to DSR storage
- ✅ SO marked as loaded
- ✅ DSR batch allocations created
- ✅ Stock transfer logged

**Data Verification:**
```sql
-- Verify warehouse stock deduction
SELECT quantity FROM warehouse.inventory_stock 
WHERE location_id = <warehouse_location> AND product_id = <product_id>;

-- Verify DSR stock increase
SELECT quantity FROM warehouse.dsr_inventory_stock 
WHERE dsr_storage_id = <dsr_storage_id> AND product_id = <product_id>;

-- Verify SO loading status
SELECT is_loaded, loaded_by_dsr_id, loaded_at 
FROM sales.sales_order 
WHERE sales_order_id = <so_id>;

-- Verify DSR batch allocation
SELECT * FROM warehouse.dsr_batch_allocation 
WHERE sales_order_detail_id IN (
    SELECT sales_order_detail_id 
    FROM sales.sales_order_detail 
    WHERE sales_order_id = <so_id>
);
```

---

**End of Part 4**
