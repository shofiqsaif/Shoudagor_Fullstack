# DSR Lifecycle Overview - System Architecture & Business Rules

**Document Version:** 2.0  
**Created:** March 26, 2026  
**Purpose:** System architecture, data models, and business rules for DSR lifecycle

---

## 1. System Architecture

### 1.1 Core Data Models

**Sales Representative (SR)**
```python
class SalesRepresentative:
    sr_id: int
    sr_name: str
    sr_code: str
    commission_amount: Decimal  # Accumulated commission balance
    is_active: bool
```

**SR Order**
```python
class SR_Order:
    sr_order_id: int
    sr_id: int
    customer_id: int
    order_number: str  # Format: SR-YYYYMMDD-SRID-SEQ
    order_date: datetime
    status: str  # pending, approved, rejected, consolidated, Completed
    total_amount: Decimal
    commission_disbursed: str  # pending, Ready, Disbursed
    commission_amount: Decimal
    details: List[SR_Order_Detail]
```

**SR Order Detail**
```python
class SR_Order_Detail:
    sr_order_detail_id: int
    sr_order_id: int
    product_id: int
    variant_id: int
    quantity: Decimal
    unit_of_measure_id: int
    negotiated_price: Decimal  # Price SR negotiated with customer
    sale_price: Decimal  # Standard/assigned sale price
    shipped_quantity: Decimal  # Actual delivered quantity
    returned_quantity: Decimal
```

**Sales Order (SO)**
```python
class SalesOrder:
    sales_order_id: int
    order_number: str  # Format: SO-YYYYMMDD-XXXX
    customer_id: int
    location_id: int
    order_date: datetime
    expected_shipment_date: datetime
    status: str  # Open, Partial, Completed, Cancelled
    payment_status: str  # Pending, Partial, Completed
    delivery_status: str  # Pending, Partial, Completed, Delivered
    total_amount: Decimal
    effective_total_amount: Decimal  # After returns
    amount_paid: Decimal
    is_consolidated: bool  # True if from SR orders
    order_source: str  # "sr_consolidated" or "direct"
    consolidated_sr_orders: JSON  # List of SR order IDs
    is_loaded: bool  # True if loaded to DSR van
    loaded_by_dsr_id: int
    loaded_at: datetime
    details: List[SalesOrderDetail]
```

**Delivery Sales Representative (DSR)**
```python
class DeliverySalesRepresentative:
    dsr_id: int
    dsr_name: str
    dsr_code: str
    payment_on_hand: Decimal  # Cash collected from customers
    commission_amount: Decimal
    is_active: bool
    dsr_storage: DSRStorage  # One-to-one relationship
```

**DSR Storage**
```python
class DSRStorage:
    dsr_storage_id: int
    dsr_id: int  # Unique constraint
    storage_name: str
    storage_code: str
    storage_type: str  # "DSR_VAN"
    max_capacity: int
```

**DSR SO Assignment**
```python
class DSRSOAssignment:
    assignment_id: int
    dsr_id: int
    sales_order_id: int
    assigned_date: datetime
    status: str  # assigned, in_progress, completed
    notes: str
```

**DSR Payment Settlement**
```python
class DSRPaymentSettlement:
    settlement_id: int
    dsr_id: int
    settlement_date: datetime
    amount: Decimal  # Amount collected from DSR
    payment_method: str  # Cash, Bank Transfer, Check, etc.
    reference_number: str
    notes: str
```

**SR Disbursement**
```python
class SRDisbursement:
    disbursement_id: int
    sr_id: int
    sr_order_id: int
    disbursement_date: datetime
    amount: Decimal
    payment_method: str
    reference_number: str
    notes: str
```

### 1.2 Inventory Models

**Inventory Stock (Warehouse)**
```python
class InventoryStock:
    stock_id: int
    product_id: int
    variant_id: int
    location_id: int  # Storage location
    quantity: Decimal
    uom_id: int
```

**DSR Inventory Stock**
```python
class DSRInventoryStock:
    stock_id: int
    product_id: int
    variant_id: int
    dsr_storage_id: int  # DSR's storage
    quantity: Decimal
    uom_id: int
```

**Batch Allocation**
```python
class BatchAllocation:
    allocation_id: int
    batch_id: int
    sales_order_detail_id: int
    allocated_quantity: Decimal
    delivered_quantity: Decimal
    returned_quantity: Decimal
```

**DSR Batch Allocation**
```python
class DSRBatchAllocation:
    allocation_id: int
    batch_id: int
    sales_order_id: int
    dsr_storage_id: int
    allocated_quantity: Decimal
    delivered_quantity: Decimal
```

---

## 2. Business Rules

### 2.1 SR Order Rules

**Creation Rules:**
- SR can only create orders for assigned customers
- SR can only select assigned products
- Negotiated price can be any value (including < sale price)
- Commission = (Negotiated Price - Sale Price) × Quantity
- Negative commission is allowed
- Order number format: `SR-YYYYMMDD-SRID-SEQ`

**Approval Rules:**
- Only Admin/Manager can approve SR orders
- Approved orders cannot be edited or deleted
- Bulk approval supported
- Approval changes status from "pending" to "approved"

**Consolidation Rules:**
- Only approved SR orders can be consolidated
- All orders must belong to same customer
- Stock validation performed before consolidation
- Multiple SR orders → Single Sales Order
- Price difference tracked: `negotiated_price - sale_price`
- SR information preserved in SO details

### 2.2 Sales Order Rules

**Status Management:**
- `Open`: Payment=Pending AND Delivery=Pending
- `Partial`: Payment≠Pending OR Delivery≠Pending (but not both complete)
- `Completed`: Payment=Completed AND Delivery=Completed

**Payment Status:**
- `Pending`: amount_paid = 0
- `Partial`: 0 < amount_paid < effective_total_amount
- `Completed`: amount_paid ≥ effective_total_amount

**Delivery Status:**
- `Pending`: All shipped_quantity = 0
- `Partial`: Some shipped_quantity > 0, but not all complete
- `Completed`: All shipped_quantity = quantity - returned_quantity

### 2.3 DSR Assignment Rules

**Assignment Validation:**
- DSR must be active (`is_active = true`)
- DSR must have storage configured
- SO cannot be already loaded (`is_loaded = false`)
- Stock must be available at SO location
- One SO can have only one DSR assignment

**Assignment Status:**
- `assigned`: Initial state after assignment
- `in_progress`: DSR has started delivery
- `completed`: All deliveries and payments complete

### 2.4 DSR Load Rules

**Load Validation:**
- SO must be assigned to DSR
- SO must not be already loaded
- Stock must be available at SO location
- DSR storage must exist

**Load Process:**
1. Validate stock availability
2. Create DSR batch allocations
3. Transfer inventory:
   - Decrease `inventory_stock` at SO location
   - Increase `dsr_inventory_stock` at DSR storage
4. Update SO:
   - `is_loaded = true`
   - `loaded_by_dsr_id = dsr_id`
   - `loaded_at = current_timestamp`
5. Log inventory movements

**Inventory Transfer:**
```
For each SO detail:
  - Calculate total quantity = quantity + free_quantity
  - Convert to base UOM
  - Allocate batches (FIFO/LIFO/WAC)
  - Transfer from warehouse to DSR storage
```

### 2.5 DSR Delivery Rules

**Delivery Validation:**
- SO must be loaded to DSR
- Delivered quantity ≤ allocated quantity
- DSR inventory must have sufficient stock

**Delivery Process:**
1. Update `shipped_quantity` on SO detail
2. Decrease `dsr_inventory_stock`
3. Update batch allocations (`delivered_quantity`)
4. Update delivery status
5. Handle returns if any

**Return Handling:**
- Returned items increase `returned_quantity`
- Returned items restore DSR inventory
- Effective total recalculated
- Delivery status updated

### 2.6 DSR Payment Collection Rules

**Payment Validation:**
- Amount must be > 0
- Payment method required
- Reference number required for non-cash methods

**Payment Process:**
1. Create payment detail record
2. Increase SO `amount_paid`
3. Decrease customer `balance_amount`
4. Increase DSR `payment_on_hand`
5. Update payment status

**Overpayment:**
- Allowed with remarks
- Customer balance becomes negative
- Payment status = "Completed"

### 2.7 DSR Unload Rules

**Unload Validation:**
- SO must be loaded
- Can unload partially delivered orders
- Only undelivered items returned

**Unload Process:**
1. Calculate undelivered quantity per item
2. Transfer inventory:
   - Decrease `dsr_inventory_stock`
   - Increase `inventory_stock` at target location
3. Reverse batch allocations
4. Update SO:
   - `is_loaded = false`
   - Clear `loaded_by_dsr_id` and `loaded_at`
5. Log inventory movements

### 2.8 DSR Settlement Rules

**Settlement Validation:**
- DSR must be active
- Settlement amount ≤ DSR `payment_on_hand`
- Settlement amount > 0
- Reference number must be unique (if provided)

**Settlement Process:**
1. Lock DSR record (optimistic locking)
2. Validate amount ≤ payment_on_hand
3. Create settlement record
4. Decrease DSR `payment_on_hand`
5. Commit transaction

**Concurrent Settlement Protection:**
- Uses optimistic locking (version column)
- Prevents double settlement
- Transaction rollback on conflict

### 2.9 Commission Rules

**Commission Calculation:**
```
Commission = Σ (Negotiated Price - Sale Price) × Shipped Quantity
```

**Commission Status Lifecycle:**
1. **pending**: Initial state when SR order created
2. **Ready**: When consolidated SO is completed (payment + delivery)
3. **Disbursed**: When commission paid to SR

**Commission Process:**
1. SO completes → SR Order status = "Completed"
2. SR Order `commission_disbursed` = "Ready"
3. SR `commission_amount` increased by commission
4. Admin disburses commission
5. SR Order `commission_disbursed` = "Disbursed"
6. SR `commission_amount` decreased by disbursed amount
7. Disbursement record created

**Negative Commission:**
- Allowed (when negotiated < sale price)
- SR commission_amount can go negative
- Disbursement still processes

---

## 3. Data Flow Diagrams

### 3.1 SR Order to SO Flow

```
SR Order (pending)
    ↓
Admin Approval
    ↓
SR Order (approved)
    ↓
Consolidation Validation
    ↓
Sales Order Creation
    ├─ SO Header (is_consolidated=true)
    ├─ SO Details (with SR mapping)
    └─ SR Orders (status=consolidated)
```

### 3.2 DSR Load/Delivery Flow

```
SO Assignment to DSR
    ↓
DSR Load Operation
    ├─ Inventory Transfer (Warehouse → DSR)
    ├─ Batch Allocation
    └─ SO.is_loaded = true
    ↓
DSR Delivery
    ├─ Update shipped_quantity
    ├─ Decrease DSR inventory
    └─ Update delivery status
    ↓
DSR Payment Collection
    ├─ Increase DSR.payment_on_hand
    ├─ Decrease Customer.balance
    └─ Update payment status
    ↓
DSR Unload (if needed)
    ├─ Inventory Transfer (DSR → Warehouse)
    ├─ Reverse Batch Allocation
    └─ SO.is_loaded = false
```

### 3.3 Settlement & Commission Flow

```
DSR Payment Collection
    ↓
DSR.payment_on_hand increased
    ↓
Admin Settlement
    ├─ Create Settlement Record
    └─ Decrease DSR.payment_on_hand
    
SO Completion
    ↓
SR Order.commission_disbursed = "Ready"
    ↓
SR.commission_amount increased
    ↓
Admin Disbursement
    ├─ Create Disbursement Record
    ├─ Decrease SR.commission_amount
    └─ SR Order.commission_disbursed = "Disbursed"
```

---

## 4. Key Validation Points

### 4.1 Stock Validation

**At SR Order Consolidation:**
- Validate stock at selected location
- Include free quantities from schemes
- Check batch availability

**At DSR Load:**
- Re-validate stock (may have changed)
- Ensure sufficient quantity for all items
- Validate batch expiry dates

**At DSR Delivery:**
- Validate DSR inventory
- Check delivered ≤ allocated
- Handle partial deliveries

### 4.2 Balance Validation

**Customer Balance:**
- Increases on SO creation
- Decreases on payment
- Can be negative (overpayment)

**DSR Payment On Hand:**
- Increases on payment collection
- Decreases on settlement
- Must be ≥ 0

**SR Commission Amount:**
- Increases when commission Ready
- Decreases on disbursement
- Can be negative

### 4.3 Status Consistency

**SO Status:**
- Must match payment + delivery status
- Auto-calculated, not manually set
- Triggers commission status update

**SR Order Status:**
- Syncs with consolidated SO status
- Cannot revert after consolidation
- Commission status independent

**DSR Assignment Status:**
- Tracks delivery progress
- Updated on delivery operations
- Completed when all delivered

---

## 5. Testing Prerequisites

### 5.1 Master Data Setup

**Required Entities:**
- 1 Company (active)
- 3 Users: Admin, SR, DSR
- 10+ Products with variants
- 5+ Customers assigned to SR
- 3+ DSRs with storage configured
- 3+ Storage locations
- 5+ Active claim schemes
- Sufficient inventory stock

**SR Setup:**
- SR user with login credentials
- Product assignments (SR_Product_Assignment)
- Customer assignments (Customer_SR_Assignment)
- Assigned sale prices

**DSR Setup:**
- DSR user with login credentials
- DSR storage created and linked
- DSR is active
- Initial payment_on_hand = 0

**Inventory Setup:**
- Products with stock at multiple locations
- Batches with different expiry dates
- Batch tracking enabled for products

### 5.2 Environment Configuration

**Backend (.env):**
```
DATABASE_URL=postgresql://user:pass@localhost:5432/shoudagor
ELASTICSEARCH_URL=http://localhost:9200
JWT_SECRET_KEY=your-secret-key
TIMEZONE=Asia/Dhaka
BATCH_ALLOCATION_MODE=FIFO
```

**Frontend (.env):**
```
VITE_API_BASE_URL=http://localhost:8000
```

### 5.3 Test Data Requirements

**Minimum Test Data:**
- 5 SR Orders (pending status)
- 3 SR Orders (approved status)
- 2 Sales Orders (Open status)
- 1 Sales Order (loaded to DSR)
- 1 DSR with payment_on_hand > 0
- 1 SR with commission Ready

---

## 6. Testing Tools & Techniques

### 6.1 Manual Testing
- Primary method for UI validation
- Step-by-step test case execution
- Visual verification of UI elements

### 6.2 Database Verification
- SQL queries to verify data consistency
- Balance reconciliation
- Audit trail validation

### 6.3 API Testing (Optional)
- Postman/Insomnia for endpoint testing
- Payload validation
- Response verification

### 6.4 Browser DevTools
- Network tab for API calls
- Console for JavaScript errors
- Application tab for local storage

---

**Next Document**: [SR_ORDER_TO_SO_TESTING.md](./SR_ORDER_TO_SO_TESTING.md)
