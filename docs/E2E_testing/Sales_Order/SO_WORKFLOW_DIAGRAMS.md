# Sales Order System - Workflow Diagrams

**Visual representation of SO workflows and data flows**

---

## 1. Complete SO Lifecycle

```
┌─────────────────────────────────────────────────────────────────────┐
│                    SALES ORDER LIFECYCLE                            │
└─────────────────────────────────────────────────────────────────────┘

    ┌──────────────┐
    │  SO Created  │ ◄─── User creates SO with products
    │ Status: Open │      Scheme auto-evaluated
    └──────┬───────┘      Stock validated
           │              Batch allocated
           │              Customer balance increased
           │
           ├──────────────┐
           │              │
           ▼              ▼
    ┌──────────┐   ┌──────────┐
    │ Payment  │   │ Delivery │
    │ Started  │   │ Started  │
    └──────┬───┘   └────┬─────┘
           │            │
           │            │
           ▼            ▼
    ┌──────────┐   ┌──────────┐
    │ Partial  │   │ Partial  │
    │ Payment  │   │ Delivery │
    └──────┬───┘   └────┬─────┘
           │            │
           │            │
           ▼            ▼
    ┌──────────┐   ┌──────────┐
    │ Payment  │   │ Delivery │
    │Completed │   │Completed │
    └──────┬───┘   └────┬─────┘
           │            │
           └──────┬─────┘
                  │
                  ▼
           ┌──────────────┐
           │ SO Completed │ ◄─── Both payment & delivery done
           │ Commission:  │      Commission status: Ready
           │    Ready     │      Can be invoiced
           └──────────────┘
```

---

## 2. SO Creation with Scheme Evaluation

```
┌─────────────────────────────────────────────────────────────────────┐
│                  SO CREATION WITH SCHEME                            │
└─────────────────────────────────────────────────────────────────────┘

User Selects Product
        │
        ▼
┌───────────────────┐
│ Scheme Evaluation │
│  - Check active   │
│  - Check dates    │
│  - Check threshold│
└────────┬──────────┘
         │
         ├─────────────────┬─────────────────┐
         │                 │                 │
         ▼                 ▼                 ▼
┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│ Buy X Get Y │   │ Flat Rebate │   │ % Discount  │
│  - Same     │   │  - Discount │   │  - Discount │
│    Product  │   │    Amount   │   │    %        │
│  - Different│   └─────────────┘   └─────────────┘
│    Product  │
└──────┬──────┘
       │
       ▼
┌───────────────────┐
│ Best Scheme       │ ◄─── Select highest value
│ Selected          │      NOT stacked
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│ Apply to SO       │
│  - Free quantity  │
│  - Discount amt   │
│  - Claim log      │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│ Stock Validation  │ ◄─── Billable + Free
│  - Billable qty   │
│  - Free qty       │
│  - Total required │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│ SO Created        │
└───────────────────┘
```

---

## 3. Payment Processing Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                    PAYMENT PROCESSING                               │
└─────────────────────────────────────────────────────────────────────┘

User Records Payment
        │
        ▼
┌───────────────────┐
│ Validate Amount   │
│  - Check > 0      │
│  - Check remarks  │
│    if overpayment │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│ Create Payment    │
│ Record            │
│  - Date           │
│  - Amount         │
│  - Method         │
│  - Reference      │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│ Update SO         │
│  amount_paid +=   │
│  payment_amount   │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│ Calculate Payment │
│ Status            │
│  - Pending        │
│  - Partial        │
│  - Completed      │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│ Update Unified    │
│ SO Status         │
│  - Open           │
│  - Partial        │
│  - Completed      │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│ Update Commission │
│ Status (if done)  │
│  pending → Ready  │
└───────────────────┘
```

---

## 4. Delivery Processing Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                    DELIVERY PROCESSING                              │
└─────────────────────────────────────────────────────────────────────┘

User Records Delivery
        │
        ▼
┌───────────────────┐
│ Validate Product  │
│  - Not deleted    │
│  - Active         │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│ Check Stock Source│
│  - DSR loaded?    │
│  - Warehouse      │
└────────┬──────────┘
         │
         ├─────────────────┬─────────────────┐
         │                 │                 │
         ▼                 ▼                 ▼
┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│ DSR Storage │   │  Warehouse  │   │   Error     │
│  - DSR stock│   │  - Main     │   │  - No stock │
│  - DSR batch│   │    stock    │   │  - Invalid  │
└──────┬──────┘   └──────┬──────┘   └─────────────┘
       │                 │
       └────────┬────────┘
                │
                ▼
┌───────────────────┐
│ Validate Stock    │
│  - Sufficient?    │
│  - Billable + Free│
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│ Create Delivery   │
│ Record            │
│  - Date           │
│  - Quantity       │
│  - Free Qty       │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│ Update SO Detail  │
│  shipped_qty +=   │
│  delivered_qty    │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│ Deduct Stock      │
│  - From source    │
│  - Update batches │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│ Consume Batch     │
│ Allocation        │
│  - FIFO/LIFO/WAC  │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│ Create Inventory  │
│ Transaction       │
│  - Type: Delivery │
│  - Quantity       │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│ Calculate Delivery│
│ Status            │
│  - Pending        │
│  - Partial        │
│  - Completed      │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│ Update Unified    │
│ SO Status         │
└───────────────────┘
```

---

## 5. Return Processing Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                    RETURN PROCESSING                                │
└─────────────────────────────────────────────────────────────────────┘

User Processes Return
        │
        ▼
┌───────────────────┐
│ Validate Return   │
│  - Qty <= shipped │
│  - Not over-return│
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│ Update SO Detail  │
│  returned_qty +=  │
│  return_qty       │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│ Recalculate       │
│ Effective Total   │
│  (Qty - Returned) │
│  × Unit Price     │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│ Restore Stock     │
│  - To warehouse   │
│  - Or DSR storage │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│ Reverse Batch     │
│ Allocation        │
│  - LIFO order     │
│  - Restore batches│
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│ Create Inventory  │
│ Transaction       │
│  - Type: Return   │
│  - Quantity       │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│ Adjust Customer   │
│ Balance           │
│  - Reduce by      │
│    return amount  │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│ Recalculate       │
│ Payment Status    │
│  - Based on       │
│    effective_total│
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│ Update Unified    │
│ SO Status         │
└───────────────────┘
```

---

## 6. DSR Loading and Delivery Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                  DSR LOADING & DELIVERY                             │
└─────────────────────────────────────────────────────────────────────┘

SO Created
    │
    ▼
┌───────────────────┐
│ Assign to DSR     │
│  - Select DSR     │
│  - Add notes      │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│ DSR Assignment    │
│ Created           │
│  - SO linked      │
│  - DSR notified   │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│ Load to DSR       │
│ Storage           │
│  - Transfer stock │
│  - From warehouse │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│ Deduct Warehouse  │
│ Stock             │
│  - Reduce qty     │
│  - Update batches │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│ Increase DSR      │
│ Storage Stock     │
│  - Add qty        │
│  - Create DSR     │
│    batches        │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│ Update SO         │
│  is_loaded = true │
│  loaded_by_dsr_id │
│  loaded_at        │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│ DSR Delivers      │
│  - From DSR stock │
│  - Record delivery│
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│ Deduct DSR Stock  │
│  - Reduce qty     │
│  - Consume DSR    │
│    batch alloc    │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│ DSR Collects      │
│ Payment           │
│  payment_on_hand  │
│  += SO amount     │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│ DSR Settles       │
│ Payment           │
│  - To company     │
│  - Clear balance  │
└───────────────────┘
```

---

## 7. Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                      DATA FLOW DIAGRAM                              │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────┐
│   Customer   │◄────────┐
│   - Balance  │         │
│   - Credit   │         │
└──────┬───────┘         │
       │                 │
       │ Creates         │ Updates Balance
       │                 │
       ▼                 │
┌──────────────┐         │
│ Sales Order  │─────────┘
│   - Total    │
│   - Paid     │◄────────┐
│   - Status   │         │
└──────┬───────┘         │
       │                 │
       │ Has             │ Updates
       │                 │
       ▼                 │
┌──────────────┐         │
│ SO Details   │         │
│   - Products │         │
│   - Quantity │         │
│   - Schemes  │         │
└──────┬───────┘         │
       │                 │
       ├─────────────────┼─────────────────┐
       │                 │                 │
       ▼                 ▼                 ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Payment    │  │   Delivery   │  │    Return    │
│   Details    │  │   Details    │  │   Details    │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                 │                 │
       │                 │                 │
       │                 ▼                 │
       │          ┌──────────────┐         │
       │          │  Inventory   │◄────────┘
       │          │   Stock      │
       │          │   - Deduct   │
       │          │   - Restore  │
       │          └──────┬───────┘
       │                 │
       │                 ▼
       │          ┌──────────────┐
       │          │    Batch     │
       │          │  Allocation  │
       │          │   - Allocate │
       │          │   - Consume  │
       │          │   - Reverse  │
       │          └──────┬───────┘
       │                 │
       │                 ▼
       │          ┌──────────────┐
       │          │  Inventory   │
       │          │ Transaction  │
       │          │   - Log all  │
       │          │     movements│
       │          └──────────────┘
       │
       ▼
┌──────────────┐
│  Claim Log   │
│   - Schemes  │
│   - Applied  │
└──────────────┘
```

---

## 8. Status Transition Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                  SO STATUS TRANSITIONS                              │
└─────────────────────────────────────────────────────────────────────┘

                    ┌──────────┐
                    │   Open   │ ◄─── Initial state
                    └────┬─────┘      No payment or delivery
                         │
                         │ Payment OR Delivery starts
                         │
                         ▼
                    ┌──────────┐
                    │ Partial  │ ◄─── Some payment or delivery
                    └────┬─────┘      Not both complete
                         │
                         │ Both payment AND delivery complete
                         │
                         ▼
                    ┌──────────┐
                    │Completed │ ◄─── Final state
                    └────┬─────┘      Both done
                         │
                         │ (Can still have returns)
                         │
                         ▼
                    ┌──────────┐
                    │Completed │ ◄─── Status remains
                    │(Returned)│      effective_total reduced
                    └──────────┘


PAYMENT STATUS:
Pending ──► Partial ──► Completed
   │           │            │
   │           │            │
   └───────────┴────────────┘
   (Based on amount_paid vs effective_total_amount)


DELIVERY STATUS:
Pending ──► Partial ──► Completed
   │           │            │
   │           │            │
   └───────────┴────────────┘
   (Based on shipped_quantity vs quantity)


COMMISSION STATUS:
pending ──► Ready ──► disbursed
   │          │          │
   │          │          │
   └──────────┴──────────┘
   (Ready when SO Completed)
```

---

## 9. Batch Allocation Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                  BATCH ALLOCATION FLOW                              │
└─────────────────────────────────────────────────────────────────────┘

SO Created
    │
    ▼
┌───────────────────┐
│ Get Available     │
│ Batches           │
│  - Not expired    │
│  - Has quantity   │
│  - Same product   │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│ Sort by Mode      │
│  - FIFO: Oldest   │
│  - LIFO: Newest   │
│  - WAC: Weighted  │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│ Allocate Batches  │
│  - Loop through   │
│  - Allocate qty   │
│  - Until fulfilled│
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│ Create Allocation │
│ Records           │
│  - Batch ID       │
│  - Allocated qty  │
│  - Consumed: 0    │
└────────┬──────────┘
         │
         │ On Delivery
         │
         ▼
┌───────────────────┐
│ Consume Allocation│
│  - Update consumed│
│  - Deduct stock   │
└────────┬──────────┘
         │
         │ On Return
         │
         ▼
┌───────────────────┐
│ Reverse Allocation│
│  - LIFO order     │
│  - Restore stock  │
│  - Update consumed│
└───────────────────┘
```

---

**End of Workflow Diagrams**
