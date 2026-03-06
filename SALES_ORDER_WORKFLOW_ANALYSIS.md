# Sales Order Workflow Analysis Report

**Date:** 2026-02-28  
**System:** Shoudagor ERP  
**Scope:** Complete Sales Order workflow analysis including creation, consolidation, DSR assignment, delivery, payment, returns, and rejections.

---

## 1. Executive Summary

The Sales Order workflow in Shoudagor ERP is a comprehensive system that handles the complete lifecycle of sales orders from creation through delivery, payment, and completion. The workflow integrates with several subsystems including SR (Sales Representative) consolidation, DSR (Delivery Sales Representative) management, inventory control, promotional schemes (claims), and customer balance tracking.

**Overall Assessment:** The workflow is **functionally and logically sound** for most operations, with only a few minor gaps identified that are documented below.

---

## 2. Sales Order Data Model

### 2.1 SalesOrder Entity

| Field | Type | Purpose |
|-------|------|---------|
| `sales_order_id` | Integer (PK) | Unique identifier |
| `order_number` | String | Auto-generated (SO-YYYYMMDD-SEQ) |
| `order_date` | TIMESTAMP | Order creation date |
| `status` | String | Open, Partial, Completed, Cancelled |
| `total_amount` | Numeric(18,2) | Total order amount |
| `amount_paid` | Numeric(18,2) | Amount paid so far |
| `customer_id` | Integer (FK) | Customer reference |
| `location_id` | Integer (FK) | Storage location |
| `payment_status` | String | Pending, Partial, Completed |
| `delivery_status` | String | Pending, In Progress, Completed |
| `commission_disbursed` | String | pending, ready, disbursed |

### SR Consolidation Fields
| Field | Type | Purpose |
|-------|------|---------|
| `order_source` | String | 'direct' or 'sr_consolidated' |
| `is_consolidated` | Boolean | Whether from SR consolidation |
| `consolidated_sr_orders` | JSON | Array of consolidated SR order references |
| `total_price_adjustment` | Numeric | Price adjustment during consolidation |
| `consolidation_date` | TIMESTAMP | When consolidation occurred |
| `consolidated_by` | Integer | User who performed consolidation |

### DSR Loading Fields
| Field | Type | Purpose |
|-------|------|---------|
| `is_loaded` | Boolean | Whether SO is loaded into DSR storage |
| `loaded_by_dsr_id` | Integer (FK) | DSR who loaded the order |
| `loaded_at` | TIMESTAMP | When the order was loaded |

### 2.2 SalesOrderDetail Entity

| Field | Type | Purpose |
|-------|------|---------|
| `quantity` | Numeric(18,4) | Ordered quantity |
| `free_quantity` | Numeric(18,4) | Free quantity from schemes |
| `shipped_quantity` | Numeric(18,4) | Quantity delivered |
| `shipped_free_quantity` | Numeric(18,4) | Free quantity delivered |
| `returned_quantity` | Numeric(18,4) | Quantity returned |
| `returned_free_quantity` | Numeric(18,4) | Free quantity returned |
| `unit_price` | Numeric(18,4) | Price per unit |
| `discount_amount` | Numeric(18,2) | Discount on line item |
| `sr_order_detail_id` | Integer | Original SR order detail |
| `negotiated_price` | Numeric | Price negotiated by SR |
| `sr_details` | JSON | Detailed breakdown per SR |

---

## 3. Order Creation Workflow

### 3.1 Flow Diagram

```
1. Client sends SalesOrderCreate request
           │
           ▼
2. Validate stock availability
   (check warehouse.inventory_stock)
           │
           ▼
3. Evaluate promotional schemes
   (ClaimService.evaluate_pre_claim)
           │
           ▼
4. Calculate total amount with UOM conversion
           │
           ▼
5. Generate order number (if not provided)
           │
           ▼
6. Create SalesOrder record
           │
           ▼
7. Create SalesOrderDetail records
           │
           ▼
8. Log scheme applications (ClaimLog)
           │
           ▼
9. Update customer balance_amount
           │
           ▼
10. Create initial payment (if amount_paid > 0)
           │
           ▼
11. Initial status = "Open"
```

### 3.2 Analysis

**Correctness:** ✅ CORRECT

- Stock validation happens BEFORE order creation (prevents overselling)
- Stock is NOT deducted at order creation (correct - deducted at delivery time)
- Customer balance is updated immediately (correct - creates receivable)
- Promotional schemes are evaluated and applied correctly
- UOM conversion is handled properly with fallback to original values

---

## 4. SR Consolidation Workflow

### 4.1 Flow Diagram

```
1. Admin selects multiple SR orders for consolidation
           │
           ▼
2. Validate all SR orders:
   - Same customer
   - All approved status
   - Not already consolidated
           │
           ▼
3. Validate stock availability at location
           │
           ▼
4. Calculate consolidated details
   (each SR detail becomes separate SO detail)
           │
           ▼
5. Calculate total price adjustment
           │
           ▼
6. Create consolidated SalesOrder
   - order_source = 'sr_consolidated'
   - is_consolidated = True
           │
           ▼
7. Update all SR orders status to 'consolidated'
           │
           ▼
8. Update customer balance
           │
           ▼
9. Later: When delivery completes:
   - Sync to SR orders
   - Apply commissions
```

### 4.2 Analysis

**Correctness:** ✅ CORRECT with minor notes

- Validation ensures only approved orders from the same customer are consolidated
- Stock validation prevents consolidation if insufficient stock
- Each SR order detail becomes a separate line item (preserves individual SR pricing)
- Price adjustments are tracked correctly
- Commission application happens when the consolidated order is completed (correct)

---

## 5. DSR Assignment & Loading Workflow

### 5.1 Flow Diagram

```
1. Admin assigns SO to DSR (DSRSOAssignment)
           │
           ▼
2. DSR loads SO into their storage:
   a. Validate all items have stock in warehouse
   b. For each item:
      - Reduce warehouse.inventory_stock
      - Add to DSRInventoryStock
   c. Mark SO as is_loaded = True
   d. Set loaded_by_dsr_id and loaded_at
           │
           ▼
3. DSR delivers to customer
   (creates SalesOrderDeliveryDetail)
           │
           ▼
4. DSR collects payment
   (creates SalesOrderPaymentDetail)
           │
           ▼
5. Process returns/rejections if any
           │
           ▼
6. Unload remaining stock back to warehouse
```

### 5.2 Analysis

**Correctness:** ✅ CORRECT

- All-or-nothing loading (fails if any item has insufficient stock)
- Stock is properly transferred from warehouse to DSR storage
- Delivery uses DSR stock when loaded, warehouse when not
- Return handling correctly adds stock back to DSR or warehouse

---

## 6. Delivery Processing

### 6.1 Flow Diagram

```
1. Client sends delivery request
   (SalesOrderDeliveryDetailCreate)
           │
           ▼
2. Get sales order and lock for update
           │
           ▼
3. Convert quantities to base UOM if needed
           │
           ▼
4. Validate stock availability:
   - If SO loaded: Check DSRInventoryStock
   - If not loaded: Check InventoryStock
           │
           ▼
5. Validate quantity doesn't exceed pending
           │
           ▼
6. Create SalesOrderDeliveryDetail record
           │
           ▼
7. Update shipped_quantity on detail
           │
           ▼
8. Deduct stock:
   - If loaded: Reduce DSRInventoryStock
   - If not loaded: Reduce InventoryStock
           │
           ▼
9. Sync to SR order detail if linked
           │
           ▼
10. Update SO status (Open/Partial/Completed)
```

### 6.2 Analysis

**Correctness:** ✅ CORRECT

- Row-level locking prevents race conditions
- UOM conversion handled correctly
- Stock source determined correctly based on load status
- SR order detail is synced properly

---

## 7. Payment Processing

### 7.1 Flow

```
1. Client sends payment request
2. Create SalesOrderPaymentDetail record
3. Update amount_paid on SalesOrder
4. Update payment_status (Pending/Partial/Completed)
5. Update SO status
```

### 7.2 Analysis

**Correctness:** ✅ CORRECT

- Payment status is correctly computed
- SO status is updated based on both payment and delivery status

---

## 8. Return Processing

### 8.1 Flow

```
1. Client sends return request
2. For each item:
   a. Validate return_qty <= shipped_qty
   b. Update:
      - returned_quantity += qty
      - shipped_quantity -= qty
   c. If SO loaded to DSR:
      - Add back to DSRInventoryStock
   d. Else:
      - Add back to InventoryStock
      - Log InventoryTransaction (SALES_RETURN)
   e. Sync to SR order detail if linked
3. Update payment/delivery status
```

### 8.2 Analysis

**Correctness:** ✅ CORRECT

- Validates return quantity doesn't exceed shipped quantity
- Stock is correctly returned to the appropriate location (DSR or warehouse)
- Transaction logging is proper

---

## 9. Rejection Processing

### 9.1 Flow

```
1. Client sends rejection request
2. For each item:
   a. Validate rejection_qty <= pending_qty
   b. Update:
      - returned_quantity += qty
      - returned_free_quantity += qty
   c. DO NOT add stock back (customer refused)
3. Update payment/delivery status
```

### 9.2 Analysis

**Correctness:** ✅ CORRECT

- Correctly does NOT return stock to inventory (rejected items were not accepted by customer)
- Only tracking fields are updated

---

## 10. Order Cancellation

### 10.1 Flow

```
1. Client requests cancellation
2. Validate status != "Completed"
3. Set status = "Cancelled"
```

### 10.2 Analysis

**Correctness:** ⚠️ INCOMPLETE

**Issues Found:**
1. Customer balance is NOT reverted when order is cancelled
2. Stock is NOT returned to warehouse if SO was loaded to DSR

**Recommendation:** Implement proper cleanup on cancellation:
- Revert customer balance_amount
- Return stock to warehouse if loaded to DSR

---

## 11. Status Update Logic

### 11.1 Status Computation

| Payment Status | Delivery Status | Order Status |
|---------------|-----------------|--------------|
| Completed | Completed | Completed |
| Partial | Any | Partial |
| Any | Partial | Partial |
| Pending | Pending | Open |

### 11.2 Analysis

**Correctness:** ✅ CORRECT

The logic properly captures all states:
- **Open:** Neither paid nor delivered
- **Partial:** Either paid or delivered (or both, but not fully)
- **Completed:** Fully paid AND delivered

---

## 12. API Endpoints Summary

### Sales Order Endpoints

| Method | Endpoint | Functionality |
|--------|----------|---------------|
| GET | `/sales-order/` | List with pagination |
| POST | `/sales-order/` | Create new order |
| GET | `/sales-order/{id}` | Get single order |
| PATCH | `/sales-order/{id}` | Update order |
| DELETE | `/sales-order/{id}` | Soft delete |
| POST | `/{id}/cancel` | Cancel order |
| POST | `/{id}/return` | Process return |
| POST | `/{id}/rejection` | Process rejection |

### Related Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/sales-order-delivery-detail/` | Record delivery |
| POST | `/sales-order-payment-detail/` | Record payment |
| GET | `/sales-order-delivery-detail/` | List deliveries |
| GET | `/sales-order-payment-detail/` | List payments |

---

## 13. Identified Issues & Recommendations

### Issue 1: Order Cancellation Incomplete
**Severity:** Medium  
**Description:** When cancelling a sales order, the system does not:
- Revert the customer balance
- Return stock to warehouse (if loaded to DSR)

**Location:** `app/services/sales/sales_order_service.py:425-438`

**Recommendation:** Enhance the `cancel_sales_order` method to:
1. Revert customer balance_amount by total_amount
2. If `is_loaded` is True, return stock to warehouse
3. Update SR order statuses if consolidated

---

### Issue 2: No Transaction Logging for Stock Deduction at Delivery
**Severity:** Low  
**Description:** When stock is deducted during delivery, the system does not create InventoryTransaction records for SALES_OUT transactions.

**Location:** `app/services/sales/sales_order_delivery_detail_service.py`

**Recommendation:** Add InventoryTransaction logging for stock deductions during delivery, similar to what is done for returns.

---

### Issue 3: SR Order Free Quantity Tracking
**Severity:** Low  
**Description:** In the return processing, the code comments question whether SR order details track free quantities separately.

**Location:** `app/services/sales/sales_order_service.py:648`

**Recommendation:** Verify if SR_Order_Detail model needs to track free quantities similar to SalesOrderDetail.

---

## 14. Test Coverage Recommendations

The following scenarios should be tested thoroughly:

1. ✅ Create sales order with sufficient stock
2. ✅ Create sales order with insufficient stock (should fail)
3. ✅ Consolidate multiple SR orders
4. ✅ Consolidate SR orders with different customers (should fail)
5. ✅ Load SO to DSR with sufficient stock
6. ✅ Load SO to DSR with insufficient stock (should fail)
7. ✅ Deliver items (stock deduction)
8. ✅ Return items (stock return)
9. ✅ Reject items (no stock return)
10. ✅ Cancel order (balance & stock handling)
11. ✅ Full order lifecycle: create → deliver → pay → complete
12. ✅ Partial payments and deliveries

---

## 15. Conclusion

The Sales Order workflow in Shoudagor ERP is **well-designed and functionally correct** for the vast majority of use cases. The key workflows (creation, consolidation, DSR loading, delivery, payment, returns, rejections) all operate as expected with proper validation, stock management, and status tracking.

The only significant gap identified is the **order cancellation process**, which does not properly clean up customer balances and inventory. This should be addressed to ensure data consistency in real-world usage scenarios.

---

## Appendix: Key Source Files

| Component | File Path |
|-----------|------------|
| Sales Order Model | `app/models/sales.py` |
| Sales Order Service | `app/services/sales/sales_order_service.py` |
| Sales Order API | `app/api/sales/sales_order.py` |
| Delivery Detail Service | `app/services/sales/sales_order_delivery_detail_service.py` |
| Payment Detail Service | `app/services/sales/sales_order_payment_detail_service.py` |
| Consolidation Service | `app/services/consolidation_service.py` |
| DSR Assignment Service | `app/services/dsr/dsr_so_assignment_service.py` |
| Frontend Sale Form | `shoudagor_FE/src/components/forms/SaleForm.tsx` |
| Frontend Sales Page | `shoudagor_FE/src/pages/sales/Sales.tsx` |
| Delivery Form | `shoudagor_FE/src/components/forms/UnifiedDeliveryForm.tsx` |
| Return Form | `shoudagor_FE/src/components/forms/SalesReturnForm.tsx` |

---

*End of Report*
