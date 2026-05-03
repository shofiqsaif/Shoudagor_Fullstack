# Sale Module - User Manual Flow Diagrams

## Table of Contents
1. [Overview](#overview)
2. [Sale Module Entry Point](#1-sale-module-entry-point)
3. [Sales Order Creation Workflow](#2-sales-order-creation-workflow)
4. [Sales Order Listing & Search](#3-sales-order-listing--search)
5. [Sales Order Edit/Update Workflow](#4-sales-order-editupdate-workflow)
6. [Customer Management Workflow](#5-customer-management-workflow)
7. [Payment Management Workflow](#6-payment-management-workflow)
8. [Delivery Management Workflow](#7-delivery-management-workflow)
9. [Returns & Rejections Workflow](#8-returns--rejections-workflow)
10. [DSR Assignment Workflow](#9-dsr-assignment-workflow)
11. [SR Order Workflow](#10-sr-order-workflow)
12. [Data Models](#11-data-models)

---

## Overview

The Sale Module is the central order management system of Shoudagor ERP. It manages the complete sales lifecycle including customer management, sales orders, payments, deliveries, returns, and SR (Sales Representative) operations.

### Key Entities
- **Customer**: Master customer data with credit limits and beat assignments
- **Sales Order**: Main order document with header and line items
- **Sales Order Detail**: Individual line items with products, quantities, and pricing
- **Sales Order Payment Detail**: Payment records linked to orders
- **Sales Order Delivery Detail**: Delivery/shipment records
- **SR Order**: Orders created by Sales Representatives
- **Sales Representative**: Field sales staff with customer assignments
- **DSR (Delivery Sales Representative)**: Delivery personnel with SO assignments
- **Beat**: Geographic sales territories/routes

---

## 1. Sale Module Entry Point

### User Journey Overview

```mermaid
flowchart TD
    %% User Entry
    A["👤 User logs into Shoudagor ERP"] --> B{"📍 Where do you want to go?"}
    
    %% Navigation Options
    B -->|Click 'Sales'<br/>in main menu| C["🛒 Sales Orders Listing Page"]
    B -->|Click 'Customers'<br/>in main menu| D["👥 Customers Page"]
    B -->|Click 'SR Orders'<br/>in main menu| E["📋 SR Orders Page"]
    B -->|Click 'Sales Reps'<br/>in main menu| F["🧑‍💼 Sales Representatives Page"]
    B -->|Click 'DSR'<br/>in main menu| G["🚚 Delivery Sales Representatives Page"]
    B -->|Click 'Beats'<br/>in main menu| H["🗺️ Beats/Routes Page"]
    
    %% Sales Page Components
    C --> C1["📊 Sales Orders Table"]
    C --> C2["🔍 Search & Filter Panel"]
    C --> C3["⚡ Quick Action Buttons"]
    
    %% Table Columns
    C1 --> C1a["Order Number<br/>Unique identifier"]
    C1 --> C1b["Customer<br/>Name & Code"]
    C1 --> C1c["Location<br/>Storage/Warehouse"]
    C1 --> C1d["Order Date<br/>Creation date"]
    C1 --> C1e["Shipment Date<br/>Expected delivery"]
    C1 --> C1f["Status<br/>Open/Delivered/Cancelled"]
    C1 --> C1g["Payment Status<br/>Pending/Partial/Paid"]
    C1 --> C1h["Delivery Status<br/>Pending/Shipped/Delivered"]
    C1 --> C1i["DSR Info<br/>Assigned delivery rep"]
    C1 --> C1j["Total Amount<br/>Order value"]
    C1 --> C1k["Effective Total<br/>After returns"]
    C1 --> C1l["Paid/Unpaid<br/>Payment tracking"]
    
    %% Search & Filters
    C2 --> C2a["🔎 Search by order number"]
    C2 --> C2b["👤 Filter by Customer"]
    C2 --> C2c["📍 Filter by Location"]
    C2 --> C2d["📊 Filter by Status"]
    C2 --> C2e["💰 Filter by Amount Range"]
    C2 --> C2f["📅 Order Date Range"]
    C2 --> C2g["📅 Shipment Date Range"]
    
    %% Action Buttons
    C3 --> C3a["➕ New Sale"]
    C3 --> C3b["📥 Download Report"]
    
    %% Row Actions
    C --> C4["⋮ Actions Menu (per row)"]
    C4 --> C4a["🖨️ Quick Print Invoice"]
    C4 --> C4b["📄 Generate Formal Invoice"]
    C4 --> C4c["💰 Make Payment"]
    C4 --> C4d["🚚 Make Delivery"]
    C4 --> C4e["↩️ Process Return"]
    C4 --> C4f["🚚 Add to DSR"]
    C4 --> C4g["👁️ View Payments"]
    C4 --> C4h["👁️ View Deliveries"]
    
    %% Customers Page
    D --> D1["👥 Customers Table"]
    D --> D2["➕ Add Customer Button"]
    D --> D3["📤 Import/Export"]
    
    %% Styling
    classDef userAction fill:#e1f5ff,stroke:#01579b,stroke-width:2px
    classDef page fill:#fff8e1,stroke:#ff6f00,stroke-width:2px
    classDef component fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef data fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    
    class A,B,C,D,E,F,G,H userAction
    class C1,D1 page
    class C2,C3,C4,D2,D3 component
    class C1a,C1b,C1c,C1d,C1e,C1f,C1g,C1h,C1i,C1j,C1k,C1l,C2a,C2b,C2c,C2d,C2e,C2f,C2g,C3a,C3b,C4a,C4b,C4c,C4d,C4e,C4f,C4g,C4h data
```

### How to Navigate the Sales Page

1. **Getting There**: Click "Sales" in the left sidebar menu after logging in
2. **What You See**: A table listing all sales orders with filtering options above
3. **Quick Actions**: Use the buttons at the top for common tasks (New Sale, Download Report)
4. **Row Actions**: Click the "⋮" (three dots) on any row to access order-specific actions

### UI Elements - Sales List Page

| Component | Type | Description |
|-----------|------|-------------|
| Customer Filter | Dropdown | Select from available customers |
| Location Filter | Dropdown | Filter by storage location |
| Status Filter | Dropdown | Order status (Open, Delivered, Cancelled) |
| Payment Status | Dropdown | Paid, Partial, Pending, Unpaid |
| Delivery Status | Dropdown | Pending, Shipped, Delivered, Received |
| Order Date Range | Date Picker | From/To date selection |
| Shipment Date Range | Date Picker | Expected shipment dates |
| Amount Range | Slider | Min/Max order amount filter |
| New Sale | Button | Navigate to creation page |
| Download Report | Button | PDF report generation |
| Sales Table | Data Table | Paginated list with sorting |
| Actions Menu | Dropdown | Print, Invoice, Payment, Delivery, Return, DSR |

---

## 2. Sales Order Creation Workflow

### 2.1 Step-by-Step: Creating a New Sales Order

**Overview**: This workflow guides you through creating a sales order with customer selection, product lines, pricing, and stock validation.

```mermaid
flowchart TD
    %% Start
    A["🚀 Click 'New Sale' button"] --> B["📄 Sale Order Form Opens"]
    
    %% Step 1: Header Information
    B --> C["📋 STEP 1: Order Header"]
    C --> C1["📅 Order Date*<br/>Defaults to today"]
    C --> C2["📅 Expected Shipment Date<br/>When to deliver"]
    C --> C3["🏭 Select Location*<br/>Storage/Warehouse"]
    C --> C4["👤 Select Customer*<br/>Search & select"]
    
    %% Customer Selection Detail
    C4 --> C4a["🔍 Type customer name<br/>Search suggestions appear"]
    C4a --> C4b["📋 Customer details loaded<br/>Code, Address, Credit Limit"]
    C4b --> C4c["⚠️ Credit check performed<br/>Available credit calculated"]
    
    %% Step 2: Add Order Lines
    C4 --> D["📦 STEP 2: Add Order Lines"]
    D --> D1["➕ Click 'Add Product' button"]
    D1 --> D2["🪟 Product Selection Modal Opens"]
    
    %% Product Selection
    D2 --> E["🔍 Search & Select Products"]
    E --> E1["Type product name<br/>Live search"]
    E --> E2["Select Variant<br/>Size, Color, etc."]
    E --> E3["View Stock Info<br/>Available quantity"]
    
    %% Line Details
    E --> F["📋 Enter Line Details"]
    F --> F1["🔢 Enter Quantity*<br/>Amount to order"]
    F --> F2["⚖️ Select Unit of Measure<br/>Piece, Box, KG, etc."]
    F --> F3["💵 Unit Price*<br/>Auto-filled from product price"]
    F --> F4["💰 Discount Amount<br/>Optional reduction"]
    F --> F5["🎁 Free Quantity<br/>From scheme/promotion"]
    
    %% Scheme Evaluation
    F --> G["🎁 Scheme/Promotion Evaluation"]
    G --> G1["System checks active schemes<br/>Based on product & quantity"]
    G --> G2["Auto-apply benefits<br/>Free items, discounts"]
    G --> G3["Show applied scheme<br/>Name & details"]
    
    %% Stock Validation
    F --> H["📦 Stock Validation"]
    H --> H1{"❓ Sufficient stock?"}
    H1 -->|No| H2["⚠️ Warning: Insufficient stock<br/>Show available quantity"]
    H2 --> F1
    H1 -->|Yes| H3["✅ Stock reserved"]
    
    %% Add to Order
    H3 --> I["💾 Click 'Add to Order'"]
    I --> J["📋 Line added to order<br/>Shown in table below"]
    
    %% Add More or Continue
    J --> K{"🤔 Need more products?"}
    K -->|Yes, add more| D1
    K -->|No, I'm done| L["📊 STEP 3: Review Order"]
    
    %% Review
    L --> L1["📋 Order Summary Displayed"]
    L1 --> L2["💰 Total Amount<br/>Sum of all lines"]
    L2 --> L3["🎁 Free Items<br/>Separate display"]
    L3 --> L4["💵 Discounts Applied<br/>Scheme savings"]
    
    %% Validation
    L --> M{"✓ Order valid?"}
    M -->|No lines| M1["❌ Error: Add at least one product"]
    M -->|Credit exceeded| M2["⚠️ Warning: Credit limit exceeded"]
    M1 --> D1
    M2 --> L
    M -->|Valid| N["🌐 Submit to API"]
    
    %% Backend Process
    N --> O["🌐 API: POST /sales/sales-order/"]
    O --> P["💾 Creating Sales Order Header"]
    P --> Q["💾 Creating Order Detail Lines"]
    Q --> R["💾 Processing Scheme Applications"]
    R --> S["📦 Reserving Inventory Stock"]
    S --> T["✅ Order created successfully!"]
    T --> U["🏠 Redirecting to Sales List..."]
    U --> V["🎉 Success! 'Sale created successfully'"]
    
    %% Invoice Generation
    T --> W["📄 Auto-generate Invoice<br/>Optional based on settings"]
    
    %% Styling
    classDef start fill:#e3f2fd,stroke:#1565c0,stroke-width:3px
    classDef step fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef input fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef decision fill:#fff8e1,stroke:#f9a825,stroke-width:2px
    classDef error fill:#ffebee,stroke:#c62828,stroke-width:2px
    classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    classDef backend fill:#e0f2f1,stroke:#00695c,stroke-width:2px
    
    class A start
    class C,D,L step
    class C1,C2,C3,C4,E1,E2,E3,F1,F2,F3,F4,F5 input
    class H,K,M decision
    class H2,M1,M2 error
    class J,L,L1,L2,L3,L4,T,U,V,W success
    class N,O,P,Q,R,S backend
```

### 💡 Tips for Sales Order Creation

1. **Customer Selection**: Search by customer name - credit limit is checked automatically
2. **Stock Check**: System validates available stock before allowing order submission
3. **UOM Conversion**: Quantities are automatically converted to base units for stock tracking
4. **Schemes**: Active promotions are automatically applied based on products and quantities
5. **Free Items**: Scheme-generated free items appear as separate order lines

### 2.2 Order Line Item Structure

```mermaid
flowchart TD
    A[Order Line Item] --> B[Product Information]
    A --> C[Quantity Information]
    A --> D[Pricing Information]
    A --> E[Scheme Information]
    A --> F[Tracking Fields]
    
    B --> B1["product_id<br/>Product reference"]
    B --> B2["variant_id<br/>Variant reference"]
    B --> B3["product_name<br/>Display name"]
    B --> B4["variant_name<br/>Display variant"]
    
    C --> C1["quantity<br/>Ordered amount"]
    C --> C2["unit_of_measure_id<br/>UOM reference"]
    C --> C3["free_quantity<br/>Bonus items"]
    C --> C4["shipped_quantity<br/>Delivered amount"]
    C --> C5["returned_quantity<br/>Returned amount"]
    
    D --> D1["unit_price<br/>Price per unit"]
    D --> D2["discount_amount<br/>Line discount"]
    D --> D3["total_price<br/>quantity × unit_price"]
    
    E --> E1["applied_scheme_id<br/>Scheme reference"]
    E --> E2["scheme_name<br/>Display name"]
    E --> E3["is_free_item<br/>Flag for free lines"]
    E --> E4["parent_detail_id<br/>Link to parent line"]
    
    F --> F1["shipped_free_quantity<br/>Delivered free items"]
    F --> F2["returned_free_quantity<br/>Returned free items"]
    F --> F3["sr_order_detail_id<br/>Link to SR order"]
```

### 2.3 Field Requirements & Validation

| Field | Required | Validation Rules |
|-------|----------|------------------|
| Order Date | Yes | Valid date, defaults to today |
| Expected Shipment Date | No | Must be >= Order Date |
| Location | Yes | Must exist in system |
| Customer | Yes | Must exist in system |
| Product | Yes | Must exist in system |
| Variant | Yes | Must belong to product |
| Quantity | Yes | Number > 0 |
| Unit of Measure | Yes | Valid UOM for product |
| Unit Price | Yes | Number >= 0 |
| Discount Amount | No | Number >= 0, < line total |

---

## 3. Sales Order Listing & Search

### 3.1 How the Sales Page Loads

**What happens when you open the Sales page:**

```mermaid
flowchart TD
    %% Page Load
    A["🏠 User clicks 'Sales' menu"] --> B["🔐 System identifies your company"]
    
    %% Loading Supporting Data
    B --> C["📦 Loading helper data..."]
    C --> C1["🏭 Loading locations list<br/>For location filter"]
    C --> C2["👤 Loading customers list<br/>For customer filter"]
    C --> C3["📊 Loading status options<br/>For status filters"]
    
    %% Loading Sales Orders
    C --> D["🔍 Loading sales orders..."]
    D --> D1["📡 API: GET /sales/sales-order/"]
    D1 --> D2["⚙️ Applying your filters"]
    D2 --> D3["📄 Orders returned in pages"]
    
    %% Data Processing
    D3 --> E["⚙️ Preparing data for display..."]
    E --> E1["🧮 Calculating effective totals<br/>Accounting for returns"]
    E --> E2["💰 Calculating unpaid amounts<br/>Total - Paid"]
    E --> E3["📊 Formatting order data<br/>Dates, amounts, status"]
    E --> E4["🔗 Loading related data<br/>Customer names, DSR info"]
    
    %% Display
    E4 --> F["🖥️ Displaying Sales Table"]
    F --> F1["📊 Showing all columns<br/>Order #, Customer, Status, etc."]
    F --> F2["⋮ Actions menu on each row<br/>Print, Payment, Delivery, etc."]
    F --> F3["📄 Pagination controls<br/>Navigate pages"]
    
    %% User Interactions
    F --> G["👤 Now you can interact:"]
    G --> G1["🔎 Use filters<br/>Customer, Location, Status, Date"]
    G --> G2["📄 Change page<br/>Click pagination numbers"]
    G --> G3["🔃 Sort columns<br/>Click column headers"]
    G --> G4["🖨️ Print invoice<br/>Click actions menu"]
    G --> G5["💰 Record payment<br/>Click actions menu"]
    
    %% System Response
    G1 --> H["🔄 Table refreshes<br/>With filtered results"]
    G2 --> I["📄 New page loads<br/>More orders shown"]
    G3 --> J["🔃 Re-sorts data<br/>Ascending/descending toggle"]
    
    %% Styling
    classDef userAction fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef system fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    classDef data fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef api fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    
    class A,G,G1,G2,G3,G4,G5 userAction
    class B,C,D,E,F system
    class C1,C2,C3,E1,E2,E3,E4,F1,F2,F3 data
    class D1,D2,D3 api
```

### 📱 Quick Guide: Finding Sales Orders

| What you want to do | How to do it |
|---------------------|--------------|
| **Filter by customer** | Use the "Customer" dropdown filter |
| **Show pending orders** | Use "Status" filter and select "Open" |
| **Find unpaid orders** | Use "Payment Status" filter and select "Pending" |
| **View orders by date** | Use Order Date or Shipment Date range pickers |
| **Sort by amount** | Click the "Total Amount" column header |
| **Quick print invoice** | Click ⋮ on row → "Quick Print Invoice" |
| **Record a payment** | Click ⋮ on row → "Make Payment" |
| **Process delivery** | Click ⋮ on row → "Make Delivery" |

### 3.2 Sales Order Status Workflow

```mermaid
flowchart LR
    A[Order Created] --> B[Open]
    B --> C[Delivered]
    B --> D[Cancelled]
    C --> E[Partially Paid]
    C --> F[Fully Paid]
    E --> F
    
    B -->|DSR Assignment| G[Assigned to DSR]
    G -->|Loading| H[Loaded to DSR]
    H -->|Delivery| C
    
    C -->|Return Request| I[Partial Return]
    I --> J[Fully Returned]
    
    style A fill:#e3f2fd
    style B fill:#fff3e0
    style C fill:#e8f5e9
    style D fill:#ffebee
    style F fill:#e8f5e9
    style G fill:#f3e5f5
    style H fill:#e1f5fe
```

### 3.3 Table Columns Display

```mermaid
flowchart TD
    A[Table Rendered] --> B[Order Number]
    A --> C[Customer Name]
    A --> D[Customer Code]
    A --> E[Location]
    A --> F[Order Date]
    A --> G[Shipment Date]
    A --> H[Status Badge]
    A --> I[Payment Status]
    A --> J[Delivery Status]
    A --> K[DSR Info]
    A --> L[Source Badge]
    A --> M[Consolidated Badge]
    A --> N[Loaded Badge]
    A --> O[Total Amount]
    A --> P[Effective Total]
    A --> Q[Amount Paid]
    A --> R[Amount Unpaid]
    A --> S[Actions Column]
    
    H --> H1{Status Value}
    H1 -->|Open| H1a["Orange Badge"]
    H1 -->|Delivered| H1b["Green Badge"]
    H1 -->|Cancelled| H1c["Red Badge"]
    
    I --> I1{Payment Value}
    I1 -->|Paid| I1a["Green Badge"]
    I1 -->|Pending| I1b["Orange Badge"]
    I1 -->|Partial| I1c["Yellow Badge"]
    
    K --> K1{Has DSR?}
    K1 -->|Yes| K1a["DSR Name + Code"]
    K1 -->|No| K1b["--"]
    
    L --> L1{Source Value}
    L1 -->|Direct| L1a["Blue Badge"]
    L1 -->|Consolidated| L1b["Purple Badge"]
    
    S --> S1[Dropdown Menu]
    S1 --> S1a["Print Invoice"]
    S1 --> S1b["Generate Invoice"]
    S1 --> S1c["Make Payment"]
    S1 --> S1d["Make Delivery"]
    S1 --> S1e["Process Return"]
    S1 --> S1f["Add to DSR"]
    S1 --> S1g["View Payments"]
    S1 --> S1h["View Deliveries"]
```

---

## 4. Sales Order Edit/Update Workflow

### 4.1 Editing a Sales Order

**Modify existing order details before delivery:**

```mermaid
flowchart TD
    %% Start
    A["👤 User wants to update order"] --> B["⋮ Click 'Actions' menu<br/>on the order row"]
    
    %% Action Menu
    B --> C["📋 Select action from dropdown"]
    
    %% Edit Options
    C --> D["✏️ Edit Order Details"]
    C --> E["💰 Make Payment"]
    C --> F["🚚 Make Delivery"]
    C --> G["↩️ Process Return"]
    
    %% Edit Flow
    D --> D1["🪟 Edit Dialog Opens"]
    D1 --> D2["📋 Load current order data"]
    D2 --> D3["✏️ Modify editable fields"]
    D3 --> D4["💾 Click 'Save Changes'"]
    D4 --> D5["🌐 API: PATCH /sales/sales-order/{id}"]
    D5 --> D6["🔄 Refresh order list"]
    
    %% Validation
    D3 --> V{"✓ Changes valid?"}
    V -->|No| V1["❌ Show field errors"]
    V1 --> D3
    V -->|Yes| D4
    
    %% Styling
    classDef userAction fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef form fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef system fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    classDef error fill:#ffebee,stroke:#c62828,stroke-width:2px
    
    class A,B,C,D,E,F,G userAction
    class D1,D2,D3,V form
    class D4,D5,D6 system
    class V1 error
```

### 4.2 Order Cancellation Flow

```mermaid
flowchart TD
    A["📋 Select Order to Cancel"] --> B["⋮ Open Actions Menu"]
    B --> C["❌ Click 'Cancel Order'"]
    C --> D["⚠️ Confirmation Dialog"]
    D --> D1["Show order details"]
    D --> D2["Warning: Irreversible action"]
    D --> E{"🤔 Confirm cancellation?"}
    E -->|No| F["🛑 Cancel aborted<br/>Dialog closes"]
    E -->|Yes| G["🌐 API: POST /sales/sales-order/{id}/cancel"]
    G --> H["💾 Update order status<br/>status = 'Cancelled'"]
    H --> I["📦 Release stock reservations"]
    I --> J["🔄 Refresh order list"]
    J --> K["🎉 Order cancelled successfully"]
    
    style A fill:#e3f2fd
    style C fill:#ffebee
    style G fill:#e0f2f1
    style K fill:#e8f5e9
```

---

## 5. Customer Management Workflow

### 5.1 Customer List & Search

```mermaid
flowchart TD
    A["👤 Navigate to Customers"] --> B["📊 Customer List Loads"]
    B --> C["📋 Display Columns"]
    
    C --> C1["Customer Code<br/>Unique identifier"]
    C --> C2["Customer Name<br/>Business/Contact name"]
    C --> C3["Contact Info<br/>Phone, Email"]
    C --> C4["Address<br/>State, City, Zip"]
    C --> C5["Beat<br/>Assigned route"]
    C --> C6["Credit Limit<br/>Maximum credit"]
    C --> C7["Balance Amount<br/>Current balance"]
    C --> C8["Store Credit<br/>Available credit"]
    C --> C9["Status<br/>Active/Inactive"]
    
    B --> D["🔍 Filter Options"]
    D --> D1["State dropdown"]
    D --> D2["City dropdown"]
    D --> D3["Zip code"]
    D --> D4["Beat dropdown"]
    D --> D5["Status dropdown"]
    D --> D6["Date range<br/>Creation/sales date"]
    
    B --> E["⚡ Quick Actions"]
    E --> E1["➕ Add Customer"]
    E --> E2["📤 Import/Export"]
    E --> E3["🗑️ Batch Delete"]
    
    B --> F["⋮ Row Actions"]
    F --> F1["✏️ Edit Customer"]
    F --> F2["🗑️ Delete Customer"]
    F --> F3["🧑‍💼 Assign SR"]
    
    style A fill:#e3f2fd
    style B fill:#fff8e1
```

### 5.2 Creating a New Customer

```mermaid
flowchart TD
    A["➕ Click 'Add Customer'"] --> B["🪟 Customer Form Opens"]
    
    B --> C["📋 Basic Information"]
    C --> C1["Customer Name*<br/>Business/Company name"]
    C --> C2["Customer Code<br/>Optional unique code"]
    C --> C3["Contact Person<br/>Primary contact name"]
    C --> C4["Contact Phone*<br/>Primary phone number"]
    C --> C5["Contact Email<br/>Email address"]
    
    B --> D["📍 Address Information"]
    D --> D1["Street Address"]
    D --> D2["Country<br/>Dropdown select"]
    D --> D3["State/Division<br/>Dropdown select"]
    D --> D4["City<br/>Dropdown select"]
    D --> D5["Zip/Postal Code"]
    
    B --> E["💰 Credit Settings"]
    E --> E1["Credit Limit<br/>Maximum allowed credit"]
    E --> E2["Opening Balance<br/>Starting balance"]
    E --> E3["Store Credit<br/>Prepaid credit"]
    
    B --> F["🗺️ Sales Assignment"]
    F --> F1["Beat Assignment<br/>Select sales route"]
    F --> F2["SR Assignment<br/>Assign sales rep"]
    
    F --> G{"✓ All required fields?"}
    G -->|No| G1["❌ Highlight missing fields"]
    G1 --> C1
    G -->|Yes| H["🌐 API: POST /sales/customer/"]
    
    H --> I["🔍 Check for duplicates"]
    I --> I1{"❓ Duplicate found?"}
    I1 -->|Yes| I2["❌ Error: Customer exists"]
    I2 --> C4
    I1 -->|No| J["💾 Save customer"]
    
    J --> K["🔍 Index in Elasticsearch"]
    K --> L["🎉 Customer created successfully"]
    L --> M["🔄 Refresh customer list"]
    
    style A fill:#e3f2fd
    style C fill:#fff3e0
    style D fill:#fff3e0
    style E fill:#fff3e0
    style F fill:#fff3e0
    style H fill:#e0f2f1
    style L fill:#e8f5e9
```

### 5.3 Customer Import via Excel

```mermaid
flowchart TD
    A["📤 Click 'Import/Export'"] --> B["📋 Select 'Import Excel'"]
    B --> C["📖 Instructions Modal"]
    C --> C1["📄 Required columns shown"]
    C --> C2["⬇️ Download template option"]
    C --> C3["📋 Validation rules explained"]
    
    C --> D["📁 Upload File"]
    D --> D1["Select .xlsx file"]
    D1 --> D2{"✓ Valid format?"}
    D2 -->|No| D3["❌ Error: Invalid format"]
    D3 --> D
    D2 -->|Yes| E["⚙️ Server Processing"]
    
    E --> F["📊 PHASE 1: Parse Excel"]
    F --> G["🔍 PHASE 2: Validate Data"]
    G --> G1["✓ Check required fields"]
    G --> G2["✓ Validate locations"]
    G --> G3["✓ Check for duplicates"]
    
    G --> H{"✓ All valid?"}
    H -->|No| I["❌ Generate Error Report"]
    I --> I1["Show row-level errors"]
    I1 --> D
    
    H -->|Yes| J["💾 PHASE 3: Import Customers"]
    J --> K["📊 Success Report"]
    K --> L["🎉 Import complete"]
    
    style A fill:#e3f2fd
    style C fill:#fff8e1
    style E fill:#e0f2f1
    style I fill:#ffebee
    style L fill:#e8f5e9
```

---

## 6. Payment Management Workflow

### 6.1 Recording a Payment

```mermaid
flowchart TD
    A["💰 Click 'Make Payment'"] --> B["🪟 Payment Dialog Opens"]
    
    B --> C["📊 Load Order Summary"]
    C --> C1["Total Amount<br/>Original order value"]
    C --> C2["Effective Total<br/>After returns/adjustments"]
    C --> C3["Amount Paid<br/>Already paid"]
    C --> C4["Remaining Balance<br/>Amount due"]
    
    C --> D["📝 Enter Payment Details"]
    D --> D1["📅 Payment Date*<br/>Defaults to today"]
    D --> D2["💵 Amount Paid*<br/>Payment amount"]
    D --> D3["💳 Payment Method*<br/>Cash, Card, Bank, etc."]
    D --> D4["📋 Transaction Reference<br/>Receipt/Ref number"]
    D --> D5["📝 Remarks<br/>Notes/comments"]
    
    D2 --> E["💡 Quick Actions"]
    E --> E1["'Full Payment' button<br/>Auto-fill remaining balance"]
    
    D --> F{"💭 Overpayment?"}
    F -->|Yes| F1["⚠️ Confirmation Dialog<br/>Excess will be store credit"]
    F -->|No| G["🌐 API: POST /sales/sales-order-payment-detail/"]
    F1 --> F2{"🤔 Confirm overpayment?"}
    F2 -->|No| D2
    F2 -->|Yes| G
    
    G --> H["💾 Save payment record"]
    H --> I["🔄 Update order payment_status"]
    I --> J["📊 Refresh order list"]
    J --> K["🎉 Payment recorded successfully"]
    
    style A fill:#e3f2fd
    style B fill:#f3e5f5
    style C fill:#e8f5e9
    style D fill:#fff3e0
    style G fill:#e0f2f1
    style K fill:#e8f5e9
```

### 6.2 Viewing Payment History

```mermaid
flowchart TD
    A["👁️ Click 'View Payments'"] --> B["🪟 Payment History Dialog"]
    
    B --> C["📊 Load Payment Data"]
    C --> C1["🌐 API: GET /sales/sales-order-payment-detail/"]
    C --> C2["📋 Display payment list"]
    
    C2 --> D["📄 Payment Table Columns"]
    D --> D1["Payment Date<br/>When paid"]
    D --> D2["Amount Paid<br/>Payment amount"]
    D --> D3["Payment Method<br/>Cash, Card, etc."]
    D --> D4["Transaction Ref<br/>Reference number"]
    D --> D5["Remarks<br/>Notes"]
    
    D --> E["⚡ Actions (per row)"]
    E --> E1["✏️ Edit Payment<br/>Modify details"]
    E --> E2["🗑️ Delete Payment<br/>Remove record"]
    
    style A fill:#e3f2fd
    style B fill:#f3e5f5
    style C fill:#e8f5e9
```

### 6.3 Payment Status Flow

```mermaid
flowchart LR
    A[Unpaid] -->|Partial Payment| B[Partial]
    A -->|Full Payment| C[Fully Paid]
    B -->|Additional Payment| C
    
    style A fill:#ffebee
    style B fill:#fff3e0
    style C fill:#e8f5e9
```

---

## 7. Delivery Management Workflow

### 7.1 Recording a Delivery

```mermaid
flowchart TD
    A["🚚 Click 'Make Delivery'"] --> B["🪟 Delivery Dialog Opens"]
    
    B --> C["📊 Load Order Details"]
    C --> C1["Product lines<br/>Ordered quantities"]
    C --> C2["Already shipped<br/>Previously delivered"]
    C --> C3["Remaining<br/>Still to deliver"]
    
    C --> D["📋 Delivery Form"]
    D --> D1["📅 Delivery Date*<br/>Defaults to today"]
    D --> D2["📦 Per Product Line:"]
    
    D2 --> E["🔢 Delivered Quantity*<br/>Amount being shipped"]
    E --> E1{"❓ Valid quantity?"}
    E1 -->|No| E2["❌ Error: Exceeds remaining"]
    E2 --> E
    E1 -->|Yes| F["🎁 Delivered Free Quantity<br/>Bonus items shipped"]
    
    D --> G["📝 Remarks<br/>Delivery notes"]
    
    G --> H["💾 Submit Delivery"]
    H --> I["🌐 API: POST /sales/sales-order-delivery-detail/"]
    I --> J["📦 Update inventory stock"]
    J --> K["🔄 Update order delivery_status"]
    K --> L["📊 Refresh order list"]
    L --> M["🎉 Delivery recorded"]
    
    K --> N{"📦 All items delivered?"}
    N -->|Yes| N1["Update status<br/>'Delivered'"]
    N -->|No| N2["Update status<br/>'Partial'"]
    
    style A fill:#e3f2fd
    style B fill:#f3e5f5
    style C fill:#e8f5e9
    style D fill:#fff3e0
    style I fill:#e0f2f1
    style M fill:#e8f5e9
```

### 7.2 Delivery Status Flow

```mermaid
flowchart LR
    A[Pending] -->|Partial Delivery| B[Partial]
    A -->|Full Delivery| C[Delivered]
    B -->|Complete Delivery| C
    C -->|Customer Confirmation| D[Received]
    
    style A fill:#fff3e0
    style B fill:#e1f5fe
    style C fill:#e8f5e9
    style D fill:#c8e6c9
```

---

## 8. Returns & Rejections Workflow

### 8.1 Processing a Return

```mermaid
flowchart TD
    A["↩️ Click 'Return'"] --> B["🪟 Return Dialog Opens"]
    
    B --> C["📊 Load Delivered Items"]
    C --> C1["Show delivered products"]
    C --> C2["Show delivered quantities"]
    C --> C3["Show already returned (if any)"]
    
    C --> D["📋 Return Form"]
    D --> D1["Select Product Line"]
    D --> D2["🔢 Return Quantity*<br/>Amount being returned"]
    
    D2 --> E{"❓ Valid return qty?"}
    E -->|No| E1["❌ Error: Exceeds delivered"]
    E1 --> D2
    E -->|Yes| F["📝 Return Reason<br/>Why returning"]
    
    F --> G["💾 Submit Return"]
    G --> H["🌐 API: POST /sales/sales-order/{id}/return"]
    H --> I["📦 Update stock<br/>Add back to inventory"]
    I --> J["💰 Adjust financials<br/>Update effective total"]
    J --> K["🔄 Sync with SR Order<br/>If from SR consolidation"]
    K --> L["🔄 Refresh order list"]
    L --> M["🎉 Return processed"]
    
    style A fill:#e3f2fd
    style B fill:#f3e5f5
    style C fill:#e8f5e9
    style D fill:#fff3e0
    style H fill:#e0f2f1
    style M fill:#e8f5e9
```

### 8.2 Processing Rejections (at Delivery)

```mermaid
flowchart TD
    A["🚚 During Delivery<br/>Items Rejected"] --> B["📋 Record Rejection"]
    B --> B1["Rejected Quantity<br/>Amount customer rejected"]
    B --> B2["Rejection Reason<br/>Damaged, Wrong item, etc."]
    
    B --> C["🌐 API: POST /sales/sales-order/{id}/rejection"]
    C --> D["📦 Update stock<br/>Return to inventory"]
    D --> E["💰 Update order totals<br/>Exclude rejected items"]
    E --> F["🔄 Sync with SR Order"]
    F --> G["📝 Generate adjustment record"]
    
    style A fill:#fff3e0
    style C fill:#e0f2f1
```

---

## 9. DSR Assignment Workflow

### 9.1 Assigning Sales Order to DSR

```mermaid
flowchart TD
    A["🚚 Click 'Add to DSR'"] --> B["🪟 DSR Assignment Dialog"]
    
    B --> C["📊 Load Order Info"]
    C --> C1["Order number<br/>Customer details"]
    C --> C2["Products to deliver<br/>Quantities"]
    
    B --> D["🧑‍💼 Select DSR"]
    D --> D1["Dropdown of available DSRs"]
    D1 --> D2["Show DSR code<br/>Contact info"]
    
    D --> E["📝 Assignment Details"]
    E --> E1["Assignment Date<br/>Defaults to today"]
    E --> E2["Notes<br/>Special instructions"]
    
    E --> F["💾 Assign to DSR"]
    F --> G["🌐 API: POST /dsr/assign-order"]
    G --> H["💾 Create DSR-SO Assignment"]
    H --> I["📧 Notify DSR<br/>If notifications enabled"]
    I --> J["🔄 Refresh order list"]
    J --> K["🎉 Order assigned to DSR"]
    
    K --> L["📱 DSR View<br/>Order appears in DSR's list"]
    
    style A fill:#e3f2fd
    style B fill:#f3e5f5
    style C fill:#e8f5e9
    style D fill:#fff3e0
    style G fill:#e0f2f1
    style K fill:#e8f5e9
```

### 9.2 DSR Loading Process

```mermaid
flowchart TD
    A["📦 DSR Prepares for Route"] --> B["🖥️ DSR Loads Order"]
    B --> C["🔍 Select Orders to Load"]
    C --> D["💾 Confirm Loading"]
    D --> E["🌐 API: POST /dsr/load-orders"]
    E --> F["📦 Transfer stock<br/>From warehouse to DSR storage"]
    F --> G["📝 Update SO status<br/>is_loaded = true"]
    G --> H["📱 Orders ready<br/>For delivery route"]
    
    style A fill:#e3f2fd
    style B fill:#f3e5f5
    style E fill:#e0f2f1
    style H fill:#e8f5e9
```

---

## 10. SR Order Workflow

### 10.1 SR Order Creation (Field Sales)

```mermaid
flowchart TD
    A["🧑‍💼 SR Logs into Mobile/App"] --> B["📋 SR Order Form"]
    
    B --> C["👤 Select Customer"]
    C --> C1["Show assigned customers<br/>Based on SR territory"]
    C1 --> C2["Validate customer assignment"]
    
    B --> D["📅 Order Details"]
    D --> D1["Order Date<br/>Defaults to today"]
    D --> D2["Location<br/>Delivery location"]
    
    B --> E["📦 Add Products"]
    E --> E1["Show SR-assigned products<br/>With prices"]
    E1 --> E2["Select product/variant"]
    E2 --> E3["Enter quantity"]
    E3 --> E4["💵 Negotiated Price<br/>May differ from standard"]
    
    E --> F["📊 Order Summary"]
    F --> F1["Calculate total<br/>Sum of (qty × negotiated_price)"]
    
    F --> G["💾 Submit SR Order"]
    G --> H["🌐 API: POST /sr/orders"]
    H --> I["💾 Create SR Order<br/>status = 'pending'"]
    I --> J["📧 Notify Admin<br/>For review/approval"]
    J --> K["🎉 SR Order submitted"]
    
    style A fill:#e3f2fd
    style B fill:#f3e5f5
    style C fill:#fff3e0
    style D fill:#fff3e0
    style E fill:#fff3e0
    style H fill:#e0f2f1
    style K fill:#e8f5e9
```

### 10.2 SR Order Approval & Consolidation

```mermaid
flowchart TD
    A["📋 Admin Views SR Orders"] --> B["📊 SR Order List"]
    B --> C{"🤔 Review Order"}
    
    C -->|Reject| D["❌ Reject Order"]
    D --> D1["Enter rejection reason"]
    D1 --> D2["🌐 API: Update status<br/>status = 'rejected'"]
    D2 --> D3["📧 Notify SR"]
    
    C -->|Approve| E["✅ Approve Order"]
    E --> E1["🌐 API: Update status<br/>status = 'approved'"]
    E1 --> E2["📧 Notify SR<br/>Order approved"]
    
    C -->|Consolidate| F["📦 Consolidate to SO"]
    F --> F1["Select multiple SR orders<br/>Same customer"]
    F1 --> F2["Select target location<br/>For stock allocation"]
    F2 --> F3["🌐 API: POST /consolidation/consolidate"]
    F3 --> F4["📦 Validate stock availability"]
    F4 --> F5{"✓ Sufficient stock?"}
    F5 -->|No| F6["❌ Show shortage details"]
    F6 --> F2
    F5 -->|Yes| F7["💾 Create Sales Order<br/>From SR orders"]
    F7 --> F8["📦 Reserve stock<br/>At selected location"]
    F8 --> F9["📝 Update SR orders<br/>status = 'consolidated'"]
    F9 --> F10["🔗 Link to parent SO"]
    F10 --> F11["🎉 Consolidation complete"]
    
    style A fill:#e3f2fd
    style B fill:#f3e5f5
    style D fill:#ffebee
    style E fill:#e8f5e9
    style F fill:#fff3e0
    style F7 fill:#e0f2f1
    style F11 fill:#e8f5e9
```

### 10.3 SR Order Status Flow

```mermaid
flowchart LR
    A[Pending] -->|Admin Review| B{Decision}
    B -->|Approve| C[Approved]
    B -->|Reject| D[Rejected]
    C -->|Consolidate| E[Consolidated]
    E -->|Create| F[Sales Order]
    
    style A fill:#fff3e0
    style B fill:#fff8e1
    style C fill:#e1f5fe
    style D fill:#ffebee
    style E fill:#f3e5f5
    style F fill:#e8f5e9
```

---

## 11. Data Models

### 11.1 Entity Relationship Diagram

```mermaid
erDiagram
    CUSTOMER ||--o{ SALES_ORDER : places
    CUSTOMER ||--o{ SR_ORDER : places_via_sr
    CUSTOMER }o--o{ BEAT : belongs_to
    CUSTOMER }o--o{ SALES_REPRESENTATIVE : assigned_to
    
    SALES_ORDER ||--o{ SALES_ORDER_DETAIL : contains
    SALES_ORDER ||--o{ SALES_ORDER_PAYMENT_DETAIL : has_payments
    SALES_ORDER ||--o{ SALES_ORDER_DELIVERY_DETAIL : has_deliveries
    SALES_ORDER }o--|| STORAGE_LOCATION : from_location
    SALES_ORDER }o--o{ DSR : assigned_to
    
    SALES_ORDER_DETAIL }o--|| PRODUCT : references
    SALES_ORDER_DETAIL }o--|| PRODUCT_VARIANT : references
    SALES_ORDER_DETAIL }o--o{ SR_ORDER_DETAIL : consolidated_from
    
    SR_ORDER ||--o{ SR_ORDER_DETAIL : contains
    SR_ORDER }o--|| SALES_REPRESENTATIVE : created_by
    SR_ORDER }o--|| CUSTOMER : for_customer
    
    SALES_REPRESENTATIVE ||--o{ SR_PRODUCT_ASSIGNMENT : has_products
    SALES_REPRESENTATIVE ||--o{ CUSTOMER_SR_ASSIGNMENT : has_customers
    
    DSR ||--o{ DSR_SO_ASSIGNMENT : has_assignments
    DSR ||--o{ DSR_PAYMENT_SETTLEMENT : has_settlements
    
    BEAT ||--o{ CUSTOMER : contains
    
    CUSTOMER {
        int customer_id PK
        string customer_name
        string customer_code
        string contact_phone
        string contact_email
        decimal credit_limit
        decimal store_credit
        decimal balance_amount
        int beat_id FK
    }
    
    SALES_ORDER {
        int sales_order_id PK
        string order_number
        int customer_id FK
        int location_id FK
        date order_date
        date expected_shipment_date
        string status
        string payment_status
        string delivery_status
        decimal total_amount
        decimal amount_paid
        boolean is_consolidated
        boolean is_loaded
        int loaded_by_dsr_id FK
    }
    
    SALES_ORDER_DETAIL {
        int sales_order_detail_id PK
        int sales_order_id FK
        int product_id FK
        int variant_id FK
        decimal quantity
        decimal unit_price
        decimal discount_amount
        decimal free_quantity
        decimal shipped_quantity
        decimal returned_quantity
        boolean is_free_item
        int applied_scheme_id FK
    }
    
    SALES_ORDER_PAYMENT_DETAIL {
        int payment_detail_id PK
        int sales_order_id FK
        date payment_date
        decimal amount_paid
        string payment_method
        string transaction_reference
    }
    
    SALES_ORDER_DELIVERY_DETAIL {
        int delivery_detail_id PK
        int sales_order_detail_id FK
        date delivery_date
        decimal delivered_quantity
        decimal delivered_free_quantity
        string remarks
    }
    
    SR_ORDER {
        int sr_order_id PK
        string order_number
        int sr_id FK
        int customer_id FK
        string status
        decimal total_amount
        decimal commission_amount
    }
    
    SR_ORDER_DETAIL {
        int sr_order_detail_id PK
        int sr_order_id FK
        int product_id FK
        int variant_id FK
        decimal quantity
        decimal negotiated_price
        decimal shipped_quantity
        decimal returned_quantity
    }
    
    SALES_REPRESENTATIVE {
        int sr_id PK
        string sr_name
        string sr_code
        string contact_phone
        string contact_email
        decimal commission_amount
    }
    
    DSR {
        int dsr_id PK
        string dsr_name
        string dsr_code
        decimal payment_on_hand
        decimal commission_amount
    }
    
    BEAT {
        int beat_id PK
        string beat_name
        string beat_code
        string description
    }
```

### 11.2 API Endpoints Reference

```mermaid
flowchart LR
    subgraph SalesOrders["Sales Orders"]
        A1["GET /sales/sales-order/"]
        A2["POST /sales/sales-order/"]
        A3["GET /sales/sales-order/{id}"]
        A4["PATCH /sales/sales-order/{id}"]
        A5["DELETE /sales/sales-order/{id}"]
        A6["POST /sales/sales-order/{id}/cancel"]
        A7["POST /sales/sales-order/{id}/return"]
        A8["POST /sales/sales-order/{id}/rejection"]
    end
    
    subgraph SalesOrderDetails["Order Details"]
        B1["GET /sales/sales-order-detail/"]
        B2["POST /sales/sales-order-detail/"]
        B3["PATCH /sales/sales-order-detail/{id}"]
        B4["DELETE /sales/sales-order-detail/{id}"]
    end
    
    subgraph Payments["Payments"]
        C1["GET /sales/sales-order-payment-detail/"]
        C2["POST /sales/sales-order-payment-detail/"]
        C3["PATCH /sales/sales-order-payment-detail/{id}"]
        C4["DELETE /sales/sales-order-payment-detail/{id}"]
    end
    
    subgraph Deliveries["Deliveries"]
        D1["GET /sales/sales-order-delivery-detail/"]
        D2["POST /sales/sales-order-delivery-detail/"]
        D3["PATCH /sales/sales-order-delivery-detail/{id}"]
        D4["DELETE /sales/sales-order-delivery-detail/{id}"]
    end
    
    subgraph Customers["Customers"]
        E1["GET /sales/customer/"]
        E2["POST /sales/customer/"]
        E3["PATCH /sales/customer/{id}"]
        E4["DELETE /sales/customer/{id}"]
        E5["POST /sales/customer/batch-delete"]
    end
    
    subgraph SROrders["SR Orders"]
        F1["GET /sr/sr-order/"]
        F2["POST /sr/sr-order/"]
        F3["PATCH /sr/sr-order/{id}"]
        F4["DELETE /sr/sr-order/{id}"]
    end
    
    subgraph Consolidation["Consolidation"]
        G1["POST /consolidation/consolidate"]
        G2["GET /consolidation/sr-consolidated-orders"]
    end
    
    subgraph DSR["DSR Management"]
        H1["GET /dsr/delivery-sales-representative/"]
        H2["POST /dsr/assign-order"]
        H3["POST /dsr/load-orders"]
    end
```

---

## Appendix: UI Component Mapping

### Frontend Page Structure

```
/src/pages/sales/
├── Sales.tsx                 # Main sales orders listing
├── ViewSaleDetails.tsx       # View payments/deliveries
└── new/
    └── AddSale.tsx           # Wrapper for new sale

/src/pages/customers/
├── Customers.tsx             # Customer listing
└── new/
    └── AddCustomer.tsx       # New customer form

/src/pages/sr-orders/
├── SROrders.tsx              # SR order listing
└── new/
    └── NewSROrder.tsx        # SR order creation

/src/pages/sales-representatives/
└── SalesRepresentatives.tsx  # SR management

/src/pages/dsr/
└── DeliverySalesRepresentatives.tsx  # DSR management

/src/components/forms/
├── SaleForm.tsx              # Main sales order form
├── SalesPaymentForm.tsx      # Payment recording
├── SalesDeliveryForm.tsx     # Delivery recording
├── SalesReturnForm.tsx       # Return processing
├── DSRAssignmentForm.tsx     # DSR assignment
├── CustomerForm.tsx          # Customer management
└── UnifiedDeliveryForm.tsx   # Combined delivery

/src/components/
├── SalesFilter.tsx           # Sales list filters
├── CustomerFilter.tsx        # Customer list filters
└── shared/
    ├── OrderStatus.tsx       # Status badge component
    └── ViewOrderDetails.tsx  # Order details dialog

/src/lib/api/
├── salesApi.ts               # Sales order APIs
├── customerApi.ts            # Customer APIs
├── srOrderApi.ts             # SR order APIs
└── salesRepresentativeApi.ts # SR management APIs

/src/lib/schema/
├── sales.ts                  # Sales order schemas
├── salesRepresentative.ts    # SR schemas
└── srOrder.ts                # SR order schemas
```

---

## Summary

The Sale Module provides a comprehensive order management solution with the following key capabilities:

1. **Complete Sales Lifecycle**: Create, manage, deliver, and track sales orders end-to-end
2. **Multi-Channel Orders**: Support for direct sales, SR orders, and consolidated orders
3. **Flexible Payments**: Record multiple payments with various methods, track balances
4. **Delivery Management**: Assign to DSRs, track loading, deliveries, and returns
5. **Customer Management**: Full customer master with credit limits, beats, and SR assignments
6. **Scheme/Promotion Integration**: Automatic application of discounts and free items
7. **Stock Integration**: Real-time stock validation and reservation
8. **Mobile/Field Sales**: SR mobile ordering with approval workflows
9. **DSR Operations**: Delivery tracking with payment collection and settlements

All workflows follow a consistent pattern: **List → Select → Action → Form → Validate → Submit → Feedback → Refresh**.
