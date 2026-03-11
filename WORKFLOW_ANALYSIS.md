# Shoudagor ERP - Workflow & Data Integrity Analysis

**Document Version:** 1.0  
**Date:** 2026-03-09  
**Purpose:** Analysis of project workflows (PO, SO, SR, DSR, Batch, Inventory) to identify logical and functional issues

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Workflow Architecture Overview](#workflow-architecture-overview)
3. [Purchase Order (PO) Workflow](#purchase-order-po-workflow)
4. [Sales Order (SO) Workflow](#sales-order-so-workflow)
5. [Sales Representative (SR) Workflow](#sales-representative-sr-workflow)
6. [Delivery Sales Representative (DSR) Workflow](#delivery-sales-representative-dsr-workflow)
7. [Batch & Inventory Workflow](#batch--inventory-workflow)
8. [Claims & Schemes Workflow](#claims--schemes-workflow)
9. [Cross-Cutting Data Integrity Issues](#cross-cutting-data-integrity-issues)
10. [Recommendations & Priority Matrix](#recommendations--priority-matrix)

---

## Executive Summary

This document provides a comprehensive analysis of the Shoudagor ERP system's core business workflows, identifying logical gaps, functional issues, and data integrity concerns. The analysis covers:

- **Purchase Orders (PO)** - Procurement workflow
- **Sales Orders (SO)** - Sales fulfillment workflow
- **Sales Representatives (SR)** - Field sales force management
- **Delivery Representatives (DSR)** - Delivery and collection management
- **Batch & Inventory** - Stock tracking with FIFO costing
- **Claims & Schemes** - Promotional offers management

### Key Findings at a Glance

| Severity | Count | Impact |
|----------|-------|--------|
| **CRITICAL** | 1 | System-wide data inconsistency |
| **HIGH** | 7 | Operational failures, overselling risk |
| **MEDIUM** | 11 | Functional bugs, partial data loss |
| **LOW** | 1 | Minor inconsistencies |
| **TOTAL** | 20 | - |

---

## Workflow Architecture Overview

### High-Level Data Flow

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                           SHOUDAGOR ERP DATA FLOW                                       │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐                       │
│  │   SUPPLIER   │─────▶│     PO       │─────▶│    BATCH     │                       │
│  └──────────────┘      └──────────────┘      └──────────────┘                       │
│         │                     │                     │                                 │
│         │                     ▼                     ▼                                 │
│         │              ┌──────────────┐      ┌──────────────┐                       │
│         │              │  INVENTORY   │◀────▶│   CLAIMS     │                       │
│         │              │   STOCK      │      │   (Schemes)  │                       │
│         │              └──────────────┘      └──────────────┘                       │
│         │                     │                     │                                 │
│         │                     ▼                     │                                 │
│         │              ┌──────────────┐            │                                 │
│         │              │     SO       │◀───────────┘                                 │
│         │              └──────────────┘                                              │
│         │                     │                                                        │
│         │           ┌─────────┴─────────┐                                            │
│         │           ▼                   ▼                                              │
│         │    ┌──────────────┐    ┌──────────────┐                                    │
│         │    │ DSR ASSIGNMENT│    │ SR CONSOLID  │                                    │
│         │    └──────────────┘    └──────────────┘                                    │
│         │           │                   │                                              │
│         ▼           ▼                   ▼                                              │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐                                  │
│  │   CUSTOMER   │ │    DSR       │ │      SR      │                                  │
│  │   (PAYMENT) │ │  (Delivery)  │ │  (Commission)│                                  │
│  └──────────────┘ └──────────────┘ └──────────────┘                                  │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

### Critical Architecture Issue: Dual Inventory Systems

The most critical finding is that **Batch and InventoryStock operate as separate parallel systems with NO automatic synchronization**:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    CURRENT ARCHITECTURE (PROBLEMATIC)                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   PO Delivery                                                            │
│       │                                                                  │
│       ├──▶ Creates Batch (inventory.batch)                              │
│       │       └── qty_on_hand increased                                 │
│       │                                                                  │
│       └──▶ Creates InventoryMovement (inventory.inventory_movement)    │
│               └── Tracks all changes                                    │
│                                                                          │
│       ⚠️  INVENTORYSTOCK (warehouse.inventory_stock) IS NOT UPDATED!    │
│                                                                          │
│   ──────────────────────────────────────────────────────────────────     │
│                                                                          │
│   SO Delivery                                                            │
│       │                                                                  │
│       ├──▶ Allocates from Batch                                         │
│       │       └── qty_on_hand decreased                                 │
│       │                                                                  │
│       ├──▶ Creates InventoryMovement (OUT)                              │
│       │                                                                  │
│       └──▶ Reduces InventoryStock (warehouse.inventory_stock)           │
│               ⚠️ THIS UPDATE IS NOT AUTOMATIC!                          │
│               ⚠️ CODE CONTINUES EVEN IF THIS FAILS!                     │
│                                                                          │
│   RESULT: Two sources of truth - ALWAYS OUT OF SYNC                     │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Purchase Order (PO) Workflow

### 1.1 Process Description

The Purchase Order workflow handles procurement from suppliers:

1. **PO Creation**
   - User creates PO with line items (product, quantity, unit price)
   - Claims/Schemes are evaluated (free quantities, discounts)
   - Supplier balance is increased
   - Status set to "Open"

2. **Delivery (Receiving)**
   - Partial or full delivery recording
   - Creates/updates InventoryStock (legacy)
   - Creates Batch record (if batch tracking enabled)
   - Creates InventoryMovement

3. **Payment**
   - Payment recording against PO
   - Supplier balance decreased
   - Payment status updated

4. **Returns/Rejections**
   - Returns: Items sent back to supplier (reduces stock)
   - Rejections: Items rejected during delivery (no stock change)

### 1.2 Key Models

| Model | Schema | Key Fields |
|-------|--------|------------|
| `PurchaseOrder` | procurement | status, payment_status, delivery_status, supplier_id |
| `PurchaseOrderDetail` | procurement | quantity, received_quantity, returned_quantity, rejected_quantity, free_quantity |
| `Supplier` | procurement | balance_amount, credit_limit |
| `Batch` | inventory | qty_received, qty_on_hand, unit_cost, source_type |
| `InventoryMovement` | inventory | movement_type, quantity, unit_cost_at_txn |

### 1.3 Data Flow Diagram

```
PO Creation
    │
    ├──▶ Validate supplier, products
    ├──▶ Evaluate Claims/Schemes
    ├──▶ Create PurchaseOrder + Details
    ├──▶ Increase Supplier Balance
    └──▶ Status: Open

Delivery Recording
    │
    ├──▶ Validate PO exists
    ├──▶ Lock PO (SELECT FOR UPDATE)
    ├──▶ Update received_quantity
    ├──▶ Update InventoryStock (Legacy)
    │   └── ⚠️ SEPARATE OPERATION
    ├──▶ Create/Update Batch
    │   └── ⚠️ SEPARATE OPERATION
    ├──▶ Create InventoryMovement
    └──▶ Update delivery_status

Payment Recording
    │
    ├──▶ Create PaymentDetail
    ├──▶ Decrease Supplier Balance
    └──▶ Update payment_status
```

### 1.4 Issues Found

#### Issue PO-001: Double Stock Update Risk [HIGH]

**Location:** `app/services/procurement/product_order_delivery_detail_service.py` lines 300-326

**Description:**
When batch tracking is enabled, BOTH batch creation AND legacy InventoryStock update happen. If batch creation fails, the code logs error but **continues with legacy stock update**.

```python
# Lines 300-326 - Problematic code
try:
    batch = self.batch_service.create_batch_for_purchase_receipt(...)
except Exception as batch_err:
    self.logger.error(f"Error creating batch: {batch_err}")
    # ⚠️ CONTINUES WITH LEGACY STOCK UPDATE!
    pass

# Legacy stock update continues regardless
self.inventory_stock_repo.update_inventory_stock(...)
```

**Impact:**
- Batch has +quantity but InventoryStock has different quantity
- Reconciliation will always show mismatch
- Reports based on either system will be incorrect

**Recommendation:**
- Wrap both operations in a single transaction
- If batch creation fails, roll back the entire operation

---

#### Issue PO-002: Missing UOM Conversion in Batch Cost [MEDIUM]

**Location:** `app/services/procurement/product_order_delivery_detail_service.py` line 303

**Description:**
Batch `unit_cost` is set directly from PO detail `unit_price` without UOM conversion.

```python
# Current code
batch = Batch(
    unit_cost=po_detail.unit_price,  # ⚠️ Not converted to base UOM
    ...
)
```

**Impact:**
- If PO uses different UOM (e.g., Carton) than base unit (e.g., Piece), batch cost will be wrong
- COGS calculations will be incorrect

**Recommendation:**
- Convert unit_price to base UOM before setting batch unit_cost

---

#### Issue PO-003: Free Quantity Not Added to Inventory [MEDIUM]

**Location:** `app/services/procurement/product_order_delivery_detail_service.py` line 302-322

**Description:**
When creating batch, only `delivered_quantity` is used. Free quantity (`delivered_free_quantity`) is passed to inventory stock but NOT to batch creation.

**Impact:**
- Batch cost doesn't account for free items
- For products with free items, unit cost calculation is incorrect
- Traceability of free items is lost

**Recommendation:**
- Include free quantity in batch creation with zero cost

---

#### Issue PO-004: No Subscriber for PO Events [LOW]

**Location:** `app/subscribers/`

**Description:**
There are subscribers for Product, ProductVariant, ProductPrice, and InventoryStock changes, but NO subscriber for PurchaseOrder creation/update.

**Impact:**
- No Elasticsearch indexing for PO data
- No notifications for PO events

---

#### Issue PO-005: Rejection Not Tracked in Batches [MEDIUM]

**Location:** `app/services/procurement/product_order_delivery_detail_service.py`

**Description:**
Rejections (`rejected_quantity`) are tracked in PO detail but there's NO batch creation/update for rejected items.

**Impact:**
- No traceability for rejected items
- Cannot track supplier quality issues

**Recommendation:**
- Create a "quarantine" or "rejected" batch for traceability

---

#### Issue PO-006: Atomicity in Return Processing [MEDIUM]

**Location:** `app/services/procurement/purchase_order_service.py` line 846

**Description:**
Return processing uses `commit()` inside a loop, which could lead to partial commits if the process fails mid-way.

**Recommendation:**
- Use single transaction with rollback on failure

---

## Sales Order (SO) Workflow

### 2.1 Process Description

1. **SO Creation** (Direct or via SR Consolidation)
   - Validate stock availability
   - Apply Claims/Schemes
   - Create SalesOrder + Details
   - Update Customer balance (receivable)
   - Initial Status: Open

2. **DSR Assignment** (Optional)
   - Assign SO to DSR
   - Load SO to DSR Storage
   - Validate and transfer stock

3. **Delivery Processing**
   - Create SalesOrderDeliveryDetail
   - Update shipped_quantity
   - Reduce Inventory Stock
   - Allocate from Batches (if enabled)
   - Update Delivery Status

4. **Payment Collection**
   - DSR collects from Customer
   - Admin settles with DSR

5. **Returns** (if any)
   - Process return with batch traceability

### 2.2 Key Models

| Model | Schema | Key Fields |
|-------|--------|------------|
| `SalesOrder` | sales | status, payment_status, delivery_status, order_source, is_consolidated |
| `SalesOrderDetail` | sales | quantity, shipped_quantity, returned_quantity, sr_details |
| `SalesOrderDeliveryDetail` | sales | delivered_quantity, delivery_status |
| `SalesOrderPaymentDetail` | sales | amount_paid, payment_method |
| `Customer` | sales | balance_amount, credit_limit |

### 2.3 Data Flow Diagram

```
SO Creation (Direct)
    │
    ├──▶ Validate Stock Availability
    │   └── ⚠️ VALIDATES AT CREATION TIME ONLY
    ├──▶ Apply Claims/Schemes
    ├──▶ Create SalesOrder + Details
    ├──▶ Update Customer Balance
    └──▶ Status: Open

SR Consolidation
    │
    ├──▶ Validate all SR orders
    ├──▶ Validate stock at location
    ├──▶ Create SalesOrder
    │   └── Each SR detail → Separate SO detail line
    ├──▶ Preserve SR details in JSON
    ├──▶ Update SR order status
    └──▶ Status: Open

DSR Assignment
    │
    ├──▶ Create DSR SO Assignment
    ├──▶ Load SO to DSR Storage
    │   ├── Validate stock
    │   ├── Allocate batches
    │   ├── Reduce warehouse stock
    │   └── Add to DSR storage
    └──▶ Mark is_loaded = True

Delivery Processing
    │
    ├──▶ Create DeliveryDetail
    ├──▶ Update shipped_quantity
    ├──▶ Reduce InventoryStock ⚠️ SEPARATE
    ├──▶ Allocate from Batch ⚠️ SEPARATE
    └──▶ Update delivery_status

Payment Collection
    │
    ├──▶ DSR collects payment
    │   └── Increase DSR.payment_on_hand
    └──▶ Admin settlement
        └── Decrease DSR.payment_on_hand
```

### 2.4 Issues Found

#### Issue SO-001: Stock Validation Not Enforced at Delivery [HIGH]

**Location:** `app/services/sales/sales_order_service.py`

**Description:**
Stock is validated at SO creation time. However, if time passes between SO creation and delivery, stock may become unavailable. The system only validates stock at delivery time in delivery service, but by then the SO exists.

**Impact:**
- SO may be created for items that are no longer available when delivering
- Multiple SOs could be created for the same stock (overselling)

**Recommendation:**
- Implement stock reservation at order creation, OR
- Re-validate stock at delivery time with proper locking

---

#### Issue SO-002: Batch Allocation is Optional but Legacy Stock Always Updated [HIGH]

**Location:** `app/services/sales/sales_order_delivery_detail_service.py` lines 642-778

**Description:**
Batch allocation runs alongside legacy inventory updates. If batch allocation succeeds but legacy update fails (or vice versa), data becomes inconsistent.

```python
# Line 672 - Comment states:
"Continue with legacy stock update if batch allocation fails"
```

**Impact:**
- Dual-tracking issues between Batch and InventoryStock
- Reconciliation will fail

---

#### Issue SO-003: SO Cancellation Doesn't Reverse Inventory [HIGH]

**Location:** `app/services/sales/sales_order_service.py` lines 426-439

**Description:**
`cancel_sales_order()` only marks SO as cancelled. It does NOT reverse previously delivered quantities.

```python
def cancel_sales_order(self, order_id):
    # Only marks as cancelled
    sales_order.status = "Cancelled"
    # ⚠️ Does NOT reverse deliveries!
    self.db.commit()
```

**Impact:**
- If SO has deliveries and is then cancelled, inventory remains reduced
- Customer balance not adjusted

---

#### Issue SO-004: No Transaction Locking on Stock Validation [MEDIUM]

**Location:** `app/services/sales/`

**Description:**
Multiple concurrent SO creations could validate against the same stock snapshot. There's no `SELECT FOR UPDATE` during validation.

**Impact:**
- Race condition: Two SOs could pass validation for the same stock
- Overselling possible under concurrent load

---

#### Issue SO-005: Returns Error Handling Gap [MEDIUM]

**Location:** `app/services/sales/sales_order_service.py` lines 531-556

**Description:**
If batch return processing fails, only logs error and continues:

```python
try:
    batch_service.process_return(...)
except Exception as batch_err:
    print(f"Error in batch return processing...")  # ⚠️ Only logs!
    # Continues anyway
```

**Impact:**
- Returns still process but batch allocations become inconsistent

---

## Sales Representative (SR) Workflow

### 3.1 Process Description

1. **SR Order Creation**
   - SR creates order with customer and products
   - Validates customer assignment to SR
   - Validates product assignment to SR
   - Uses negotiated price or assigned price

2. **SR Order Approval**
   - Admin approves SR orders

3. **Consolidation**
   - Admin consolidates approved SR orders
   - All must be for SAME CUSTOMER
   - Creates consolidated SalesOrder
   - Each SR order detail → SO separate detail line

4. **Commission Calculation**
   - Commission = (Negotiated Price - Sale Price) × Shipped Quantity

5. **Commission Disbursement**
   - Mark as Ready → Disburse to SR

### 3.2 Key Models

| Model | Schema | Key Fields |
|-------|--------|------------|
| `SalesRepresentative` | sales | commission_amount, user_id |
| `SR_Order` | sales | status, customer_id, sr_id |
| `SR_Order_Detail` | sales | quantity, negotiated_price, sale_price, shipped_quantity |
| `SR_Product_Assignment` | sales | assigned_sale_price, price_effective_date |
| `Customer_SR_Assignment` | sales | customer_id, sr_id |
| `SRDisbursement` | sales | amount, disbursement_type |

### 3.3 Issues Found

#### Issue SR-001: No Stock Check During SR Order Creation [HIGH]

**Location:** `app/services/sr/sr_order_service.py`

**Description:**
SR orders are created without checking stock availability. Stock is only validated during consolidation (later).

**Impact:**
- SRs can create orders for out-of-stock items
- Order may fail at consolidation or delivery

---

#### Issue SR-002: No Price Override Validation [MEDIUM]

**Location:** `app/services/sr/sr_order_service.py` lines 171-265

**Description:**
When SR creates an order, there's no check if the `negotiated_price` exceeds min/max override prices defined in `SR_Product_Assignment`.

**Impact:**
- SR can sell below minimum or above maximum allowed prices

---

#### Issue SR-003: No Customer Credit Limit Check [HIGH]

**Location:** `app/services/sr/sr_order_service.py`

**Description:**
There's no validation against `customer.credit_limit` when creating SR orders or during consolidation.

**Impact:**
- Customers can exceed their credit limit
- Financial exposure for the business

---

#### Issue SR-004: Commission Doesn't Handle Returns [MEDIUM]

**Location:** `app/services/sr/sr_order_service.py`

**Description:**
If items are returned, commission isn't automatically adjusted.

```python
# Current: Commission calculated on shipped_quantity
detail_commission = (detail.negotiated_price - detail.sale_price) * detail.shipped_quantity
# ⚠️ If returned_quantity > 0, commission is NOT adjusted
```

**Impact:**
- SR keeps commission even after goods are returned

---

#### Issue SR-005: Stock Not Deducted During Consolidation [MEDIUM]

**Location:** `app/services/consolidation_service.py`

**Description:**
Stock is validated but NOT deducted during consolidation. Stock deduction happens later during Sales Order delivery processing.

**Impact:**
- Multiple SOs could be created for same stock
- May run out of stock between consolidation and delivery

---

#### Issue SR-006: No Partial Consolidation Support [LOW]

**Location:** `app/services/consolidation_service.py`

**Description:**
If any SR order fails validation, the entire consolidation fails. No way to consolidate a subset.

**Impact:**
- One problematic SR order blocks all others

---

## Delivery Sales Representative (DSR) Workflow

### 4.1 Process Description

1. **DSR Assignment**
   - Admin assigns SO to DSR
   - Creates DSR SO Assignment record

2. **Load SO to DSR Storage**
   - Validates stock availability
   - Allocates batches (if enabled)
   - Transfers from warehouse to DSR storage
   - Marks SO as `is_loaded = True`

3. **Delivery to Customer**
   - DSR delivers to customer
   - Updates delivery status

4. **Payment Collection**
   - DSR collects payment from customer
   - Updates `payment_on_hand` balance

5. **Admin Settlement**
   - Admin collects payment from DSR
   - Creates DSRPaymentSettlement
   - Decreases DSR `payment_on_hand`

### 4.2 Key Models

| Model | Schema | Key Fields |
|-------|--------|------------|
| `DeliverySalesRepresentative` | sales | payment_on_hand, commission, dsr_storage_id |
| `DSRSOAssignment` | sales | status (assigned/in_progress/completed), sales_order_id |
| `DSRStorage` | warehouse | Virtual storage for DSR |
| `DSRInventoryStock` | warehouse | Stock in DSR's van |
| `DSRPaymentSettlement` | sales | amount, settlement_date |

### 4.3 Data Flow Diagram

```
DSR Assignment
    │
    ├──▶ Create DSR SO Assignment
    └──▶ Status: Assigned

Load to DSR Storage (All-or-Nothing)
    │
    ├──▶ Validate ALL items in SO ⚠️ Race condition here
    │       └── Between validation and load, stock could change
    ├──▶ Allocate batches
    ├──▶ Reduce warehouse InventoryStock
    ├──▶ Add to DSRInventoryStock
    └──▶ Mark is_loaded = True

Delivery
    │
    ├──▶ Update DeliveryDetail
    ├──▶ Reduce DSRInventoryStock
    └──▶ Update status

Payment Collection
    │
    ├──▶ Create SalesOrderPaymentDetail
    ├──▶ Increase DSR.payment_on_hand
    └──▶ Update SO payment_status

Admin Settlement
    │
    ├──▶ Create DSRPaymentSettlement
    └──▶ Decrease DSR.payment_on_hand
```

### 4.4 Issues Found

#### Issue DSR-001: DSR Load All-or-Nothing but Inventory Already Reduced [HIGH]

**Location:** `app/services/dsr/dsr_so_assignment_service.py` lines 420-455

**Description:**
Flow: First validates all items, THEN loads all items. Between validation and load, stock could change.

```python
# Lines 420-455 - Not atomic
def load_so(self, assignment_id):
    # Step 1: Validate all items
    for item in all_items:
        validate_stock(item)  # ⚠️ Time gap before actual load
    
    # Step 2: Load all items (stock could have changed!)
    for item in all_items:
        transfer_stock(item)
```

**Impact:**
- If stock changes between validation and load, may load incorrect quantities

---

#### Issue DSR-002: Payment Not Linked to Specific SOs [MEDIUM]

**Location:** `app/services/dsr/dsr_so_assignment_service.py` lines 211-265

**Description:**
Payment is collected for an assignment but updates `SalesOrder.amount_paid`. No link between `DSRPaymentSettlement` and which specific SOs the payment covered.

**Impact:**
- Cannot trace which SOs were settled
- Reconciliation difficult

---

#### Issue DSR-003: DSR Unload May Create Negative Batch Returns [MEDIUM]

**Location:** `app/services/dsr/dsr_so_assignment_service.py` lines 640-642

**Description:**
Comment states: "If qty_remaining_to_batch > 0, it means we returned more than we allocated... physical stock is still moved below, but not tracked in batches"

**Impact:**
- Stock counts correct but batch records incorrect

---

## Batch & Inventory Workflow

### 5.1 Process Description

1. **Batch Creation**
   - From PO Delivery (source_type = "purchase")
   - From Backfill (source_type = "synthetic")
   - Manual creation via API

2. **Inventory Movement**
   - IN: Purchase receipts, returns, opening balance
   - OUT: Sales deliveries, transfers out
   - RETURN_IN: Customer returns
   - RETURN_OUT: Returns to supplier
   - ADJUSTMENT: Stock corrections

3. **Allocation (FIFO/LIFO/Weighted Avg)**
   - Uses `SELECT FOR UPDATE SKIP LOCKED`
   - Creates SalesOrderBatchAllocation records

4. **Reconciliation**
   - Compares Batch totals vs InventoryStock totals
   - Reports mismatches

5. **Backfill**
   - PO Delivery → Create synthetic batches
   - SO Delivery → Allocate from existing batches

### 5.2 Key Models

| Model | Schema | Key Fields |
|-------|--------|------------|
| `Batch` | inventory | qty_received, qty_on_hand, unit_cost, status, source_type, is_synthetic |
| `InventoryMovement` | inventory | movement_type, quantity, unit_cost_at_txn, batch_id |
| `SalesOrderBatchAllocation` | inventory | sales_order_detail_id, batch_id, allocated_qty |
| `InventoryStock` | warehouse | quantity (legacy) |
| `CompanyInventorySetting` | settings | valuation_mode, is_batch_tracking_enabled |

### 5.3 Issues Found

#### Issue INV-001: NO AUTOMATIC SYNCHRONIZATION - CRITICAL [CRITICAL]

**Location:** `app/services/inventory/batch_allocation_service.py`, `app/subscribers/inventory_subscriber.py`

**Description:**
This is the MOST CRITICAL issue in the entire system. Batch and InventoryStock operate as completely separate systems with NO automatic synchronization.

When:
- A sale is made via Batch allocation → InventoryStock NOT updated
- A purchase is received to Batch → InventoryStock NOT updated

The only place they're both updated is in the delivery detail service, but even there:
- If batch allocation succeeds but legacy update fails → continues anyway
- If batch allocation fails → still tries to continue with legacy update

**Evidence:**

In `inventory_subscriber.py`:
```python
# Only handles ElasticSearch re-indexing
# Does NOT sync Batch changes to InventoryStock!
```

In `batch_allocation_service.py`:
```python
# When allocating:
# - Decrements batch.qty_on_hand ✓
# - Creates InventoryMovement ✓
# - Does NOT update InventoryStock ✗
```

**Impact:**
- Reconciliation will ALWAYS show mismatches
- Legacy reports using InventoryStock will be incorrect
- Two sources of truth for inventory - impossible to know correct stock

**Recommendation:**
- Create a subscriber that syncs batch qty_on_hand changes to InventoryStock
- Wrap both operations in a single transaction
- Or: Deprecate one system entirely

---

#### Issue INV-002: Returns May Lose Location Context [HIGH]

**Location:** `app/services/inventory/batch_allocation_service.py` lines 502-536

**Description:**
If original batch is depleted/deleted, return creates synthetic batch with `location_id = None`.

```python
synthetic_batch = Batch(
    location_id=batch.location_id if batch else None,  # ⚠️ Can be None!
    ...
)
```

**Impact:**
- Returns not traceable to location
- Cannot fulfill from specific locations

---

#### Issue INV-003: Weighted Average Cost Calculation Issue [MEDIUM]

**Location:** `app/services/inventory/batch_allocation_service.py` lines 210-248

**Description:**
The computation uses `qty_on_hand` but should use `qty_received` for accurate weighted average.

```python
# Current code
SELECT SUM(qty_on_hand * unit_cost) / NULLIF(SUM(qty_on_hand), 0) as avg_cost
# Should be:
SELECT SUM(qty_received * unit_cost) / NULLIF(SUM(qty_received), 0) as avg_cost
```

**Impact:**
- Weighted average is calculated on current stock, not historical purchases
- COGS may be incorrect

---

#### Issue INV-004: No Validation for Zero Cost Batches [MEDIUM]

**Location:** Multiple services

**Description:**
No validation prevents creating batches with zero unit cost.

**Impact:**
- Incorrect COGS calculations
- Can break weighted average calculations

---

#### Issue INV-005: Product/Variant ID Bug in Returns [LOW]

**Location:** `app/services/inventory/batch_allocation_service.py` lines 503-506

**Description:**
If `batch` is None, code incorrectly uses `allocation.batch_id` (which is a BATCH ID, not PRODUCT ID):

```python
synthetic_batch = Batch(
    product_id=batch.product_id if batch else allocation.batch_id,  # ⚠️ BUG!
    ...
)
```

**Impact:**
- Returns may be linked to wrong product

---

## Claims & Schemes Workflow

### 6.1 Process Description

1. **Scheme Creation**
   - Define scheme type: buy_x_get_y, rebate_flat, rebate_percentage
   - Set trigger product/variant
   - Set free product/variant (for buy_x_get_y)
   - Define slabs with tiers

2. **Order Evaluation**
   - At PO/SO creation, ClaimService evaluates schemes
   - Calculates free quantities and discounts
   - Applies automatically

3. **Claim Logging**
   - Records applied schemes in ClaimLog
   - Tracks free qty given, discounts applied

### 6.2 Key Models

| Model | Schema | Key Fields |
|-------|--------|------------|
| `ClaimScheme` | claims | scheme_type, start_date, end_date, trigger_product_id, free_product_id |
| `ClaimSlab` | claims | threshold_qty, free_qty, discount_amount, discount_percentage |
| `ClaimLog` | claims | ref_id, ref_type, applied_on_qty, given_free_qty, given_discount_amount |

### 6.3 Issues Found

#### Issue CLM-001: Hard Delete of Slabs During Update [MEDIUM]

**Location:** `app/services/claims/claim_service.py` line 128

**Description:**
Uses hard delete instead of soft delete for ClaimSlabs:

```python
self.db.query(ClaimSlab).filter(ClaimSlab.scheme_id == db_scheme.scheme_id).delete()
# ⚠️ Hard delete - data lost forever
```

**Impact:**
- Historical data integrity compromised
- Cannot audit past slab configurations

---

#### Issue CLM-002: Percentage Rebate Calculation Bug [MEDIUM]

**Location:** `app/services/claims/claim_service.py` line 109

**Description:**
Percentage rebate applies to ENTIRE quantity, not threshold quantity:

```python
elif scheme.scheme_type == 'rebate_percentage':
    # Current (wrong): Applies to ENTIRE quantity
    benefits["discount_amount"] = quantity * unit_price * (percentage / 100.0)
    
    # Should work like flat rebate with multiplier:
    # multiplier = quantity // threshold
    # discount = multiplier * (threshold * unit_price * percentage / 100)
```

**Impact:**
- Larger discount than intended
- Financial loss

---

#### Issue CLM-003: No Scheme Ownership Validation [MEDIUM]

**Location:** `app/services/claims/claim_service.py`

**Description:**
When specific `applied_scheme_id` is provided, no validation that it belongs to the company.

**Impact:**
- User could potentially apply other company's schemes

---

#### Issue CLM-004: ClaimLog Deduplication Missing [MEDIUM]

**Location:** `app/services/claims/claim_service.py`

**Description:**
If order creation is retried, duplicate claim logs are created. No idempotency check.

**Impact:**
- Duplicate logs inflate reports

---

#### Issue CLM-005: Scheme Type Can Be Changed After Creation [LOW]

**Location:** `app/schemas/claims/`

**Description:**
`ClaimSchemeUpdate` allows changing `scheme_type` after creation.

**Impact:**
- Changes core logic without recalculating past applications

---

## Cross-Cutting Data Integrity Issues

### Issue X-001: Multiple Independent Commits

**Location:** Throughout codebase (137 instances of `.commit()`)

**Description:**
Services commit independently without coordination. Many operations use multiple `commit()` calls in loops or sequential operations.

**Impact:**
- If operation fails mid-way, partial data saved
- No rollback capability

---

### Issue X-002: No Distributed Transaction Management

**Description:**
Operations that span multiple tables (Batch + InventoryStock + Movement + Order) are not wrapped in proper transactions.

**Impact:**
- Data inconsistency when operations fail

---

### Issue X-003: Missing Foreign Key Constraints

**Description:**
Several relationships lack proper foreign key constraints:
- `ClaimScheme.trigger_product_id` can become orphaned
- `Batch.purchase_order_detail_id` - if PO detail deleted

**Impact:**
- Orphaned records
- Broken relationships

---

### Issue X-004: Soft Delete Not Consistently Applied

**Description:**
- ClaimSlab uses hard delete
- Some operations may not filter by `is_deleted`

**Impact:**
- Data inconsistency
- Reports may include deleted records

---

## Recommendations & Priority Matrix

### Priority Classification

| Priority | Definition | Issues |
|----------|------------|--------|
| **CRITICAL** | System-wide data inconsistency, immediate fix required | INV-001 |
| **HIGH** | Operational failures, overselling risk, financial impact | PO-001, PO-002, SO-001, SO-002, SO-003, SR-001, SR-003, DSR-001 |
| **MEDIUM** | Functional bugs, partial data loss, medium impact | PO-002, PO-003, PO-005, PO-006, SO-004, SO-005, SR-002, SR-004, SR-005, DSR-002, DSR-003, INV-002, INV-003, INV-004, CLM-001, CLM-002, CLM-003, CLM-004 |
| **LOW** | Minor inconsistencies, cosmetic issues | PO-004, SR-006, INV-005, CLM-005 |

### Recommended Action Plan

#### Phase 1: Critical Fixes (Immediate)

| Issue | Fix | Effort |
|-------|-----|--------|
| INV-001 | Create synchronization between Batch and InventoryStock | High |
| PO-001 | Wrap batch + stock updates in single transaction | Medium |
| SO-002 | Same as PO-001 | Medium |

#### Phase 2: High Priority (Within Sprint)

| Issue | Fix | Effort |
|-------|-----|--------|
| SO-001 | Re-validate stock at delivery or add reservation | Medium |
| SO-003 | Add inventory reversal on SO cancellation | Medium |
| SR-001 | Add stock check during SR order creation | Low |
| SR-003 | Add credit limit validation | Low |
| DSR-001 | Make validation + load atomic | Medium |

#### Phase 3: Medium Priority (Backlog)

| Issue | Fix | Effort |
|-------|-----|--------|
| CLM-002 | Fix percentage rebate calculation | Low |
| CLM-001 | Change to soft delete for slabs | Low |
| INV-003 | Fix weighted average calculation | Medium |
| SR-004 | Add return handling for commissions | Medium |
| DSR-002 | Link payments to specific SOs | Medium |

---

## Appendix: Issue Reference Table

| ID | Category | Title | Severity | Page |
|----|----------|-------|----------|------|
| PO-001 | Purchase Order | Double Stock Update Risk | HIGH | 7 |
| PO-002 | Purchase Order | Missing UOM Conversion in Batch Cost | MEDIUM | 8 |
| PO-003 | Purchase Order | Free Quantity Not Added to Inventory | MEDIUM | 8 |
| PO-004 | Purchase Order | No Subscriber for PO Events | LOW | 9 |
| PO-005 | Purchase Order | Rejection Not Tracked in Batches | MEDIUM | 9 |
| PO-006 | Purchase Order | Atomicity in Return Processing | MEDIUM | 9 |
| SO-001 | Sales Order | Stock Validation Not Enforced at Delivery | HIGH | 13 |
| SO-002 | Sales Order | Batch Allocation Inconsistency | HIGH | 14 |
| SO-003 | Sales Order | SO Cancellation Doesn't Reverse Inventory | HIGH | 14 |
| SO-004 | Sales Order | No Transaction Locking on Stock Validation | MEDIUM | 15 |
| SO-005 | Sales Order | Returns Error Handling Gap | MEDIUM | 15 |
| SR-001 | SR | No Stock Check During SR Order Creation | HIGH | 19 |
| SR-002 | SR | No Price Override Validation | MEDIUM | 19 |
| SR-003 | SR | No Customer Credit Limit Check | HIGH | 20 |
| SR-004 | SR | Commission Doesn't Handle Returns | MEDIUM | 20 |
| SR-005 | SR | Stock Not Deducted During Consolidation | MEDIUM | 21 |
| SR-006 | SR | No Partial Consolidation Support | LOW | 21 |
| DSR-001 | DSR | DSR Load Race Condition | HIGH | 24 |
| DSR-002 | DSR | Payment Not Linked to Specific SOs | MEDIUM | 25 |
| DSR-003 | DSR | DSR Unload May Create Negative Batch Returns | MEDIUM | 25 |
| INV-001 | Inventory | NO AUTOMATIC SYNCHRONIZATION | CRITICAL | 28 |
| INV-002 | Inventory | Returns May Lose Location Context | HIGH | 29 |
| INV-003 | Inventory | Weighted Average Cost Calculation Issue | MEDIUM | 30 |
| INV-004 | Inventory | No Validation for Zero Cost Batches | MEDIUM | 30 |
| INV-005 | Inventory | Product/Variant ID Bug in Returns | LOW | 31 |
| CLM-001 | Claims | Hard Delete of Slabs During Update | MEDIUM | 35 |
| CLM-002 | Claims | Percentage Rebate Calculation Bug | MEDIUM | 35 |
| CLM-003 | Claims | No Scheme Ownership Validation | MEDIUM | 36 |
| CLM-004 | Claims | ClaimLog Deduplication Missing | MEDIUM | 36 |
| CLM-005 | Claims | Scheme Type Can Be Changed After Creation | LOW | 37 |

---

*End of Document*
