# DSR Module - User Manual Flow Diagrams

## Table of Contents
1. [Overview](#overview)
2. [DSR Module Entry Point](#1-dsr-module-entry-point)
3. [DSR Management Workflow](#2-dsr-management-workflow)
4. [DSR Storage Management](#3-dsr-storage-management)
5. [DSR SO Assignment Workflow](#4-dsr-so-assignment-workflow)
6. [DSR Load/Unload Workflow](#5-dsr-loadunload-workflow)
7. [DSR Delivery & Payment Collection](#6-dsr-delivery--payment-collection)
8. [DSR Settlement Workflow](#7-dsr-settlement-workflow)
9. [DSR Dashboard & Reporting](#8-dsr-dashboard--reporting)
10. [Data Models](#9-data-models)

---

## Overview

The DSR (Delivery Sales Representative) Module manages field sales operations, enabling delivery representatives to process orders, manage inventory in their vehicles/vans, collect payments, and handle returns on the go.

### Key Entities
- **DSR (Delivery Sales Representative)**: Field sales agent with van/storage
- **DSR Storage**: Physical storage location (van, warehouse, shop) linked to DSR
- **DSR SO Assignment**: Links Sales Orders to DSRs for delivery
- **DSR Inventory Stock**: Products currently loaded in DSR's van
- **DSR Payment Settlement**: Records of payment collection from DSRs

### User Roles
- **Admin**: Manages DSRs, assignments, and settlements
- **DSR User**: Field representative who loads orders, delivers, collects payments

---

## 1. DSR Module Entry Point

### User Journey Overview

```mermaid
flowchart TD
    %% User Entry
    A["👤 User logs into Shoudagor ERP"] --> B{"📍 User Role?"}
    
    %% Admin Navigation
    B -->|Admin User| C["📊 Admin Dashboard"]
    C --> C1["🚛 DSR Menu"]
    C1 --> C1a["DSR List"]
    C1 --> C1b["DSR Storage"]
    C1 --> C1c["SO Assignments"]
    C1 --> C1d["Settlement History"]
    
    %% DSR User Navigation
    B -->|DSR User| D["📱 DSR Dashboard"]
    D --> D1["My Assignments"]
    D --> D2["My Inventory"]
    D --> D3["Quick Actions"]
    
    %% DSR List Page Components
    C1a --> E["📋 DSR List Page"]
    E --> E1["DSR Table"]
    E --> E2["Search & Filter Panel"]
    E --> E3["Add DSR Button"]
    
    %% Table Columns
    E1 --> E1a["DSR Name"]
    E1 --> E1b["DSR Code"]
    E1 --> E1c["Email & Phone"]
    E1 --> E1d["Payment on Hand 💰"]
    E1 --> E1e["Commission Amount"]
    E1 --> E1f["Has Storage"]
    E1 --> E1g["Status"]
    
    %% Actions Menu
    E --> E4["⋮ Actions Menu (per row)"]
    E4 --> E4a["✏️ Edit DSR"]
    E4 --> E4b["🗑️ Delete DSR"]
    E4 --> E4c["💰 Settle Payment"]
    
    %% DSR Dashboard Components
    D --> F["📊 Statistics Cards"]
    F --> F1["Payment on Hand"]
    F --> F2["Total Outstanding"]
    F --> F3["Commission Earned"]
    F --> F4["Pending Deliveries"]
    F --> F5["Completed Today"]
    
    %% Styling
    classDef userAction fill:#e1f5ff,stroke:#01579b,stroke-width:2px
    classDef page fill:#fff8e1,stroke:#ff6f00,stroke-width:2px
    classDef component fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef data fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    
    class A,B,C,D,E userAction
    class C1,E1,F page
    class E2,E3,E4,D1,D2,D3 component
    class E1a,E1b,E1c,E1d,E1e,E1f,E1g,F1,F2,F3,F4,F5 data
```

### How to Navigate the DSR Module

**For Admin Users:**
1. **Getting There**: Click "DSR" in the left sidebar menu after logging in
2. **What You See**: DSR list with payment balances, storage status, and action menus
3. **Quick Actions**: Add new DSRs, view storage locations, manage assignments
4. **Row Actions**: Click "⋮" (three dots) on any DSR row to edit, delete, or settle payments

**For DSR Users:**
1. **Getting There**: Dashboard auto-loads with DSR-specific view
2. **What You See**: Summary of assignments, inventory, and financial status
3. **Quick Actions**: Access my assignments, view inventory, process deliveries

### UI Elements - DSR List Page (Admin View)

| Component | Type | Description |
|-----------|------|-------------|
| DSR Name | Text | Representative's name |
| DSR Code | Text | Unique identifier code |
| Payment on Hand | Currency | Cash collected, pending settlement |
| Commission Amount | Currency | Earned commission balance |
| Has Storage | Yes/No | Whether storage location is configured |
| Status | Badge | Active/Inactive indicator |
| Add DSR | Button | Navigate to creation page |
| Actions Menu | Dropdown | Edit, Delete, Settle Payment |

---

## 2. DSR Management Workflow

### 2.1 Creating a New DSR

**Overview**: Create a Delivery Sales Representative record with contact info and initial payment balance.

```mermaid
flowchart TD
    %% Start
    A["🚀 Click 'Add DSR' button"] --> B["📄 DSR Creation Form Opens"]
    
    %% Form Fields
    B --> C["📋 Enter DSR Information"]
    C --> C1["📝 DSR Name*<br/>Example: 'John Doe'"]
    C --> C2["🏷️ DSR Code*<br/>Example: 'DSR-001'"]
    C --> C3["📧 Contact Email<br/>Optional email address"]
    C --> C4["📱 Contact Phone<br/>Optional phone number"]
    
    %% Financial Fields
    C --> D["💰 Financial Information"]
    D --> D1["💵 Payment on Hand<br/>Initial cash amount (default: 0)"]
    D --> D2["✅ Active Status<br/>Toggle ON/OFF (default: ON)"]
    
    %% Validation
    C2 --> E{"🔍 Is DSR Code unique?"}
    E -->|No| E1["⚠️ Error: 'DSR code already exists'<br/>Use a different code"]
    E -->|Yes| F["✅ Validation passed"]
    
    %% Submit
    F --> G["💾 Click 'Create' button"]
    G --> H["🌐 API: POST /dsr"]
    H --> I["💾 Creating DSR record..."]
    I --> J["✅ DSR created successfully!"]
    J --> K["🏠 Redirecting to DSR List..."]
    
    %% Styling
    classDef start fill:#e3f2fd,stroke:#1565c0,stroke-width:3px
    classDef step fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef input fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef decision fill:#fff8e1,stroke:#f9a825,stroke-width:2px
    classDef error fill:#ffebee,stroke:#c62828,stroke-width:2px
    classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    classDef backend fill:#e0f2f1,stroke:#00695c,stroke-width:2px
    
    class A start
    class B,C,D,G step
    class C1,C2,C3,C4,D1,D2 input
    class E decision
    class E1 error
    class F,J,K success
    class H,I backend
```

### 2.2 Editing a DSR

```mermaid
flowchart TD
    A["📋 DSR List Page"] --> B["⋮ Click Actions menu"]
    B --> C["✏️ Select 'Edit'"]
    C --> D["🪟 Edit Dialog Opens"]
    D --> D1["Load current DSR data"]
    
    D --> E["📋 Edit Form"]
    E --> E1["Update DSR Name"]
    E --> E2["Update DSR Code"]
    E --> E3["Update Email"]
    E --> E4["Update Phone"]
    E --> E5["Update Payment on Hand"]
    E --> E6["Toggle Active Status"]
    
    E --> F["💾 Click 'Update' button"]
    F --> G["🌐 API: PATCH /dsr/{id}"]
    G --> H["✅ DSR updated successfully"]
    
    %% Styling
    classDef userAction fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef form fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef api fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    
    class A,B,C,F userAction
    class D,E,E1,E2,E3,E4,E5,E6 form
    class G api
    class H success
```

### 2.3 Field Requirements & Validation

| Field | Required | Validation Rules |
|-------|----------|------------------|
| DSR Name | Yes | Min 1 char, max 200 |
| DSR Code | Yes | Unique per company, max 50 chars |
| Contact Email | No | Valid email format |
| Contact Phone | No | Max 20 chars |
| Payment on Hand | No | Decimal number |
| Is Active | No | Boolean, default true |

---

## 3. DSR Storage Management

### 3.1 Creating DSR Storage

**Overview**: Each DSR needs a storage location (van, mini-warehouse, or shop) to hold inventory for deliveries.

```mermaid
flowchart TD
    A["🚀 Navigate to DSR Storage"] --> B["📋 DSR Storage List"]
    B --> C["➕ Click 'Add Storage'"]
    C --> D["🪟 Storage Form Opens"]
    
    D --> E["📋 Storage Information"]
    E --> E1["🏷️ Storage Name*<br/>Example: 'John Van - Toyota HiAce'"]
    E --> E2["🏷️ Storage Code*<br/>Example: 'VAN-001'"]
    E --> E3["👤 Select DSR*<br/>Dropdown of available DSRs"]
    E --> E4["📦 Storage Type*<br/>Van / Warehouse / Shop / Other"]
    E --> E5["📊 Max Capacity<br/>Optional max items limit"]
    E --> E6["✅ Active Status<br/>Toggle ON/OFF"]
    
    E3 --> F{"🔍 Is DSR already linked?"}
    F -->|Yes| F1["⚠️ Warning: DSR already has storage"]
    F -->|No| G["✅ Continue"]
    
    G --> H["💾 Click 'Save'"]
    H --> I["🌐 API: POST /dsr-storage"]
    I --> J["💾 Creating storage..."]
    J --> K["🔗 Linking to DSR..."]
    K --> L["✅ Storage created!"]
    
    %% Styling
    classDef start fill:#e3f2fd,stroke:#1565c0,stroke-width:3px
    classDef step fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef input fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef decision fill:#fff8e1,stroke:#f9a825,stroke-width:2px
    classDef error fill:#ffebee,stroke:#c62828,stroke-width:2px
    classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    classDef backend fill:#e0f2f1,stroke:#00695c,stroke-width:2px
    
    class A,C start
    class B,D,H step
    class E1,E2,E3,E4,E5,E6 input
    class F decision
    class F1 error
    class G,L success
    class I,J,K backend
```

### 3.2 Storage Types

| Type | Description | Use Case |
|------|-------------|----------|
| **Van** | Mobile vehicle storage | Field delivery reps |
| **Warehouse** | Fixed warehouse space | Mini distribution centers |
| **Shop** | Retail shop location | Store-within-store model |
| **Other** | Custom location type | Special arrangements |

---

## 4. DSR SO Assignment Workflow

### 4.1 Assigning Sales Order to DSR

**Overview**: Admin assigns a confirmed Sales Order to a DSR for delivery. The DSR must have storage configured.

```mermaid
flowchart TD
    A["📋 Sales Orders Page"] --> B["⋮ Find order to assign"]
    B --> C["🚛 Select 'Assign to DSR'"]
    C --> D["🪟 Assignment Dialog Opens"]
    
    D --> D0["📊 Display Order Info"]
    D0 --> D0a["Order Number"]
    D0 --> D0b["Customer Name"]
    D0 --> D0c["Total Amount"]
    D0 --> D0d["Effective Total"]
    
    D --> E["👤 Select DSR*"]
    E --> E1["Dropdown shows active DSRs"]
    E1 --> E2["Display DSR name + code"]
    
    D --> F["📝 Notes (Optional)"]
    F --> F1["Add assignment notes"]
    
    E --> G{"🔍 Validations"}
    G --> G1{"DSR active?"}
    G1 -->|No| G1a["❌ Error: DSR is inactive"]
    G --> G2{"DSR has storage?"}
    G2 -->|No| G2a["❌ Error: No storage configured"]
    G --> G3{"SO already assigned?"}
    G3 -->|Yes| G3a["❌ Error: Already assigned"]
    G --> G4{"Stock available?"}
    G4 -->|No| G4a["❌ Error: Insufficient stock"]
    
    G -->|All Pass| H["✅ Validation passed"]
    H --> I["💾 Click 'Assign to DSR'"]
    I --> J["🌐 API: POST /dsr-so-assignments"]
    J --> K["💾 Creating assignment..."]
    K --> L["📧 Assignment created!"]
    L --> M["🏠 SO list refreshed"]
    
    %% Styling
    classDef userAction fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef form fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef info fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    classDef decision fill:#fff8e1,stroke:#f9a825,stroke-width:2px
    classDef error fill:#ffebee,stroke:#c62828,stroke-width:2px
    classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:3px
    classDef api fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    
    class A,B,C,I userAction
    class D,E,F form
    class D0,D0a,D0b,D0c,D0d info
    class G,G1,G2,G3,G4 decision
    class G1a,G2a,G3a,G4a error
    class H,L,M success
    class J,K api
```

### 4.2 Assignment Status Flow

```mermaid
flowchart LR
    A["📋 Assigned"] -->|DSR Loads Order| B["🚚 In Progress"]
    B -->|Delivery Complete| C["✅ Completed"]
    B -->|Unload/Return| D["📦 Unloaded"]
    D -->|Re-assign| A
    
    %% Styling
    classDef assigned fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef progress fill:#fff8e1,stroke:#f9a825,stroke-width:2px
    classDef complete fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    classDef unloaded fill:#ffebee,stroke:#c62828,stroke-width:2px
    
    class A assigned
    class B progress
    class C complete
    class D unloaded
```

---

## 5. DSR Load/Unload Workflow

### 5.1 Loading Sales Order to Van

**Overview**: DSR transfers Sales Order items from warehouse to their van storage for delivery.

```mermaid
flowchart TD
    A["📱 DSR Dashboard"] --> B["My Assignments"]
    B --> C["📋 Assignment List"]
    C --> D{"Find order with status 'Assigned'"}
    
    D --> E["⋮ Click Actions menu"]
    E --> F["📦 Select 'Load to Van'"]
    F --> G["🪟 Load Dialog Opens"]
    
    G --> G1["📊 Order Details"]
    G1 --> G1a["Order Number"]
    G1 --> G1b["Customer Name"]
    G1 --> G1c["Items to Load"]
    
    G --> H["📝 Notes (Optional)"]
    H --> H1["Add loading notes"]
    
    G --> I["💾 Click 'Load to Van'"]
    I --> J["🌐 API: POST /dsr-so-assignments/{id}/load"]
    
    J --> K["⚙️ Backend Processing"]
    K --> K1["🔍 Validate stock in warehouse"]
    K --> K2["📦 Deduct from warehouse stock"]
    K --> K3["🚚 Add to DSR storage"]
    K --> K4["🏷️ Mark SO as 'is_loaded'"]
    
    K --> L["✅ Load successful!"]
    L --> M["📱 My Inventory updated"]
    M --> N["Order status: 'In Progress'"]
    
    %% Styling
    classDef userAction fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef dialog fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef info fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    classDef process fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:3px
    classDef api fill:#fff8e1,stroke:#f9a825,stroke-width:2px
    
    class A,B,E,F,I userAction
    class C,D,G dialog
    class G1,G1a,G1b,G1c,H,H1 info
    class K,K1,K2,K3,K4 process
    class L,M,N success
    class J api
```

### 5.2 Unloading Sales Order from Van

```mermaid
flowchart TD
    A["📱 My Assignments / Inventory"] --> B["Find loaded order"]
    B --> C["⋮ Click Actions menu"]
    C --> D["📦 Select 'Unload from Van'"]
    D --> E["🪟 Unload Dialog Opens"]
    
    E --> F["⚠️ Warning Displayed"]
    F --> F1["Items return to warehouse"]
    F --> F2["Assignment may be cancelled"]
    
    E --> G["📝 Notes (Optional)"]
    G --> G1["Reason for unloading"]
    
    E --> H["💾 Click 'Unload from Van'"]
    H --> I["🌐 API: POST /dsr-so-assignments/{id}/unload"]
    
    I --> J["⚙️ Backend Processing"]
    J --> J1["🔍 Check items in DSR storage"]
    J --> J2["📦 Deduct from DSR storage"]
    J --> J3["🏭 Return to warehouse stock"]
    J --> J4["🏷️ Mark SO as 'not loaded'"]
    
    J --> K["✅ Unload successful!"]
    K --> L["📱 Inventory updated"]
    L --> M["Assignment removed/reverted"]
    
    %% Styling
    classDef userAction fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef warning fill:#fff8e1,stroke:#f9a825,stroke-width:2px
    classDef process fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:3px
    classDef api fill:#fff8e1,stroke:#f9a825,stroke-width:2px
    
    class A,C,D,H userAction
    class E,F,F1,F2 warning
    class J,J1,J2,J3,J4 process
    class K,L,M success
    class I api
```

---

## 6. DSR Delivery & Payment Collection

### 6.1 Making Delivery

**Overview**: DSR delivers loaded items to customer, records accepted and rejected quantities.

```mermaid
flowchart TD
    A["📱 My Assignments"] --> B["Find 'In Progress' order"]
    B --> C["⋮ Click Actions menu"]
    C --> D["✅ Select 'Make Delivery'"]
    D --> E["🪟 Delivery Dialog Opens"]
    
    E --> F["📋 Delivery Form"]
    F --> F0["📅 Delivery Date"]
    F --> F1["📦 Items List"]
    
    F1 --> G["Per Item Entry"]
    G --> G1["✅ Delivered Qty<br/>Customer accepted"]
    G --> G2["❌ Rejected Qty<br/>Customer rejected"]
    G --> G3["📝 Remarks<br/>Reason for rejection"]
    
    G --> H{"🔍 Validation"}
    H -->|Invalid| H1["⚠️ Show errors<br/>e.g., Total > Order Qty"]
    H -->|Valid| I["✅ Continue"]
    
    I --> J["💾 Click 'Complete Delivery'"]
    J --> K["🌐 API: POST /delivery-batch"]
    
    K --> L["⚙️ Backend Processing"]
    L --> L1["💾 Create delivery records"]
    L --> L2["💾 Create rejection records"]
    L --> L3["📦 Deduct delivered from DSR storage"]
    L --> L4["📈 Update SO delivery status"]
    L --> L5["📊 Update assignment status"]
    
    L --> M["✅ Delivery recorded!"]
    M --> N["📱 Assignment status updated"]
    
    %% Styling
    classDef userAction fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef form fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef input fill:#fff8e1,stroke:#f9a825,stroke-width:2px
    classDef decision fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef error fill:#ffebee,stroke:#c62828,stroke-width:2px
    classDef process fill:#e0f2f1,stroke:#00695c,stroke-width:2px
    classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:3px
    
    class A,C,D,J userAction
    class E,F form
    class F0,F1,G,G1,G2,G3 input
    class H decision
    class H1 error
    class L,L1,L2,L3,L4,L5 process
    class I,M,N success
```

### 6.2 Collecting Payment

```mermaid
flowchart TD
    A["📱 My Assignments"] --> B["Find order with outstanding payment"]
    B --> C["⋮ Click Actions menu"]
    C --> D["💰 Select 'Collect Payment'"]
    D --> E["🪟 Payment Dialog Opens"]
    
    E --> F["📊 Order Balance Info"]
    F --> F1["Total Amount"]
    F --> F2["Already Paid"]
    F --> F3["Outstanding Balance"]
    
    E --> G["💳 Payment Details"]
    G --> G1["💵 Amount*<br/>Payment amount"]
    G --> G2["💳 Payment Method<br/>Cash / Check / Transfer"]
    G --> G3["🏷️ Reference<br/>Transaction reference"]
    G --> G4["📝 Notes<br/>Payment notes"]
    
    G1 --> H{"🔍 Valid amount?"}
    H -->|No| H1["⚠️ Error: Invalid amount"]
    H -->|Yes| I["✅ Continue"]
    
    I --> J["💾 Click 'Collect Payment'"]
    J --> K["🌐 API: POST /collect-payment"]
    
    K --> L["⚙️ Backend Processing"]
    L --> L1["💾 Create payment record"]
    L --> L2["💰 Update SO amount_paid"]
    L --> L3["📊 Update customer balance"]
    L --> L4["💵 Add to DSR payment_on_hand"]
    L --> L5["📈 Update payment status"]
    
    L --> M["✅ Payment recorded!"]
    M --> N["DSR balance updated"]
    
    %% Styling
    classDef userAction fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef form fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef info fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    classDef decision fill:#fff8e1,stroke:#f9a825,stroke-width:2px
    classDef error fill:#ffebee,stroke:#c62828,stroke-width:2px
    classDef process fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:3px
    
    class A,C,D,J userAction
    class E,G form
    class F,F1,F2,F3 info
    class H decision
    class H1 error
    class L,L1,L2,L3,L4,L5 process
    class I,M,N success
```

---

## 7. DSR Settlement Workflow

### 7.1 Recording Payment Settlement

**Overview**: Admin collects cash from DSR and records the settlement, reducing DSR's payment_on_hand balance.

```mermaid
flowchart TD
    A["📋 DSR List Page"] --> B["Find DSR with Payment on Hand > 0"]
    B --> C["⋮ Click Actions menu"]
    C --> D["💰 Select 'Settle Payment'"]
    D --> E["🪟 Settlement Dialog Opens"]
    
    E --> F["📊 DSR Financial Summary"]
    F --> F1["Current Payment on Hand"]
    F --> F2["Commission Balance"]
    F --> F3["Available to Settle"]
    
    E --> G["💳 Settlement Details"]
    G --> G1["💵 Settlement Amount*<br/>Amount being collected"]
    G --> G2["📅 Settlement Date*<br/>Date of collection"]
    G --> G3["💳 Payment Method<br/>Cash / Bank Transfer / Check"]
    G --> G4["🏷️ Reference Number<br/>Transaction reference"]
    G --> G5["📝 Notes<br/>Settlement notes"]
    
    G1 --> H{"🔍 Valid amount?"}
    H -->|Exceeds balance| H1["⚠️ Error: Amount exceeds payment on hand"]
    H -->|Invalid| H2["⚠️ Error: Invalid amount"]
    H -->|Valid| I["✅ Continue"]
    
    I --> J["💾 Click 'Record Settlement'"]
    J --> K["🌐 API: POST /sales/dsr/settlements"]
    
    K --> L["⚙️ Backend Processing"]
    L --> L1["💾 Create settlement record"]
    L --> L2["💵 Reduce DSR payment_on_hand"]
    L --> L3["📊 Update company cash position"]
    
    L --> M["✅ Settlement recorded!"]
    M --> N["📧 DSR balance updated"]
    N --> O["Settlement appears in history"]
    
    %% Styling
    classDef userAction fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef form fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef info fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    classDef decision fill:#fff8e1,stroke:#f9a825,stroke-width:2px
    classDef error fill:#ffebee,stroke:#c62828,stroke-width:2px
    classDef process fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:3px
    
    class A,C,D,J userAction
    class E,G form
    class F,F1,F2,F3 info
    class H decision
    class H1,H2 error
    class L,L1,L2,L3 process
    class I,M,N,O success
```

### 7.2 Settlement History

```mermaid
flowchart TD
    A["📋 Settlement History Page"] --> B["🔍 Filter Options"]
    B --> B1["Select DSR"]
    B --> B2["Date Range"]
    B --> B3["Reset Filters"]
    
    A --> C["📊 Settlement Table"]
    C --> C1["Date & Time"]
    C --> C2["DSR Name & Code"]
    C --> C3["Amount 💰"]
    C --> C4["Payment Method"]
    C --> C5["Reference Number"]
    C --> C6["Notes"]
    
    C --> D["📄 Pagination"]
    D --> D1["Items per page"]
    D --> D2["Page navigation"]
    
    %% Styling
    classDef page fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef filter fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef table fill:#fff8e1,stroke:#f9a825,stroke-width:2px
    classDef data fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    
    class A page
    class B,B1,B2,B3 filter
    class C,C1,C2,C3,C4,C5,C6 table
    class D,D1,D2 data
```

---

## 8. DSR Dashboard & Reporting

### 8.1 DSR Dashboard (DSR User View)

```mermaid
flowchart TD
    A["📱 DSR Dashboard"] --> B["📊 Statistics Cards"]
    B --> B1["💰 Payment on Hand<br/>Current cash holding"]
    B --> B2["💳 Total Outstanding<br/>Yet to collect"]
    B --> B3["✅ Commission Earned<br/>Commission balance"]
    
    A --> C["📈 Activity Summary"]
    C --> C1["Collection Today"]
    C --> C2["Pending Deliveries"]
    C --> C3["Completed Today"]
    C --> C4["Total Deliveries"]
    
    A --> D["📋 Recent Assignments"]
    D --> D1["Last 5 assignments"]
    D --> D2["Order number link"]
    D --> D3["Customer name"]
    D --> D4["Status badge"]
    
    A --> E["⚡ Quick Actions"]
    E --> E1["🔗 My Assignments"]
    E --> E2["📦 My Inventory"]
    E --> E3["🏢 DSR Storage"]
    
    A --> F["💵 Financial Summary"]
    F --> F1["Active Assignments"]
    F --> F2["Current Cash Hand"]
    F --> F3["Remaining to Collect"]
    F --> F4["Commission Balance"]
    
    %% Styling
    classDef dashboard fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef stats fill:#fff8e1,stroke:#f9a825,stroke-width:2px
    classDef activity fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    classDef table fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef actions fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef finance fill:#e0f2f1,stroke:#00695c,stroke-width:2px
    
    class A dashboard
    class B,B1,B2,B3 stats
    class C,C1,C2,C3,C4 activity
    class D,D1,D2,D3,D4 table
    class E,E1,E2,E3 actions
    class F,F1,F2,F3,F4 finance
```

### 8.2 My Inventory Page (DSR View)

```mermaid
flowchart TD
    A["📦 My Inventory Page"] --> B["🔍 Search Products"]
    B --> B1["Search by name/code"]
    B --> B2["Debounce 300ms"]
    
    A --> C["📋 Inventory Table"]
    C --> C1["Product Name & Code"]
    C --> C2["Variant Name"]
    C --> C3["Quantity<br/>Badge with color"]
    C --> C4["Unit"]
    C --> C5["Storage Name"]
    
    A --> D["📄 Pagination"]
    D --> D1["20 items per page"]
    D --> D2["Page navigation"]
    
    A --> E["⚠️ No Storage Alert"]
    E --> E1["Show if no storage assigned"]
    E --> E2["Contact admin message"]
    
    A --> F["📭 Empty State"]
    F --> F1["No stock message"]
    F --> F2["Link to My Assignments"]
    
    %% Styling
    classDef page fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef search fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef table fill:#fff8e1,stroke:#f9a825,stroke-width:2px
    classDef data fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    classDef alert fill:#ffebee,stroke:#c62828,stroke-width:2px
    classDef empty fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    
    class A page
    class B,B1,B2 search
    class C,C1,C2,C3,C4,C5 table
    class D,D1,D2 data
    class E,E1,E2 alert
    class F,F1,F2 empty
```

---

## 9. Data Models

### 9.1 Entity Relationship

```mermaid
erDiagram
    DSR ||--o{ DSR_STORAGE : has
    DSR ||--o{ DSR_SO_ASSIGNMENT : assigned_to
    DSR ||--o{ DSR_PAYMENT_SETTLEMENT : settled_by
    DSR_STORAGE ||--o{ DSR_INVENTORY_STOCK : contains
    SALES_ORDER ||--o{ DSR_SO_ASSIGNMENT : assigned
    
    DSR {
        int dsr_id PK
        string dsr_name
        string dsr_code UK
        string contact_email
        string contact_phone
        decimal payment_on_hand
        decimal commission_amount
        boolean is_active
        int company_id FK
    }
    
    DSR_STORAGE {
        int dsr_storage_id PK
        int dsr_id FK
        string storage_name
        string storage_code
        string storage_type
        decimal max_capacity
        boolean is_active
    }
    
    DSR_SO_ASSIGNMENT {
        int assignment_id PK
        int dsr_id FK
        int sales_order_id FK
        timestamp assigned_date
        string status
        text notes
    }
    
    DSR_PAYMENT_SETTLEMENT {
        int settlement_id PK
        int dsr_id FK
        timestamp settlement_date
        decimal amount
        string payment_method
        string reference_number
        text notes
    }
    
    DSR_INVENTORY_STOCK {
        int stock_id PK
        int dsr_storage_id FK
        int product_id FK
        int variant_id FK
        decimal quantity
        int unit_id FK
    }
```

### 9.2 Status Definitions

| Entity | Status Values | Description |
|--------|---------------|-------------|
| **DSR** | Active, Inactive | Whether DSR can be assigned orders |
| **DSR SO Assignment** | assigned, in_progress, completed | Assignment lifecycle |
| **Sales Order (is_loaded)** | true, false | Whether order is loaded to DSR van |
| **Sales Order (delivery_status)** | Pending, Partial, Delivered | Delivery progress |
| **Sales Order (payment_status)** | Unpaid, Partial, Paid | Payment collection progress |

---

## Quick Reference: Common Actions

| Action | Who | Path | Key Points |
|--------|-----|------|------------|
| **Create DSR** | Admin | DSR → Add DSR | Unique code required |
| **Create Storage** | Admin | DSR Storage → Add | Link to existing DSR |
| **Assign SO** | Admin | Sales → Assign to DSR | DSR must have storage |
| **Load Order** | DSR | My Assignments → Load | Transfers stock to van |
| **Make Delivery** | DSR | My Assignments → Deliver | Record accepted/rejected |
| **Collect Payment** | DSR | My Assignments → Payment | Updates DSR balance |
| **Settle Payment** | Admin | DSR → Settle Payment | Reduces DSR on-hand |
| **Process Return** | DSR | My Assignments → Return | Handle rejected items |

---

## API Endpoints Reference

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/dsr` | GET, POST | List/create DSRs |
| `/dsr/{id}` | GET, PATCH, DELETE | Manage single DSR |
| `/dsr-storage` | GET, POST | List/create storage |
| `/dsr-so-assignments` | GET, POST | List/create assignments |
| `/dsr-so-assignments/{id}/load` | POST | Load SO to DSR |
| `/dsr-so-assignments/{id}/unload` | POST | Unload SO from DSR |
| `/dsr-so-assignments/{id}/deliver` | POST | Mark delivered |
| `/dsr-so-assignments/{id}/collect-payment` | POST | Record payment |
| `/sales/dsr/settlements` | GET, POST | Settlement history |
| `/dsr-my-inventory-stock` | GET | DSR's current stock |
| `/dsr-summary` | GET | DSR dashboard stats |
| `/dsr-my-assignments` | GET | DSR's assignments |
