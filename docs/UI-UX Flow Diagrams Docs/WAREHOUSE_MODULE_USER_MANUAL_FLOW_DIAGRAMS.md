# Warehouse Module - User Manual Flow Diagrams

## Table of Contents
1. [Overview](#overview)
2. [Warehouse Module Entry Point](#1-warehouse-module-entry-point)
3. [Storage Location Management Workflow](#2-storage-location-management-workflow)
4. [Inventory Stock Management Workflow](#3-inventory-stock-management-workflow)
5. [Stock Transfer Workflow](#4-stock-transfer-workflow)
6. [DSR Storage Management Workflow](#5-dsr-storage-management-workflow)
7. [Data Models](#6-data-models)

---

## Overview

The Warehouse Module is the core inventory location management system of Shoudagor ERP. It manages physical storage locations, tracks inventory stock levels across locations, facilitates stock transfers between locations, and handles DSR (Delivery Sales Representative) storage operations.

### Key Entities
- **Warehouse**: Physical warehouse buildings with address information
- **Storage Location**: Specific storage areas within warehouses (bins, racks, zones)
- **Inventory Stock**: Stock levels tracked per product/variant per location
- **Stock Transfer**: Movement of stock between locations
- **DSR Storage**: Mobile storage locations assigned to Delivery Sales Representatives
- **DSR Stock Transfer**: Stock transfers between main warehouse and DSR storages

---

## 1. Warehouse Module Entry Point

### User Journey Overview

```mermaid
flowchart TD
    %% User Entry
    A["👤 User logs into Shoudagor ERP"] --> B{"📍 Where do you want to go?"}
    
    %% Navigation Options
    B -->|Click 'Warehouses'<br/>in main menu| C["🏭 Warehouses Page"]
    B -->|Click 'Storage Locations'<br/>in submenu| D["📦 Storage Locations Page"]
    B -->|Click 'Stock Transfer'<br/>in submenu| E["🔄 Stock Transfer Page"]
    B -->|Click 'DSR Storages'<br/>in submenu| F["🚚 DSR Storages Page"]
    
    %% Warehouses Page Components
    C --> C1["🏭 Warehouses Table"]
    C --> C2["🔍 Search & Filter Panel"]
    C --> C3["⚡ Quick Action Buttons"]
    
    %% Table Columns
    C1 --> C1a["Warehouse Name"]
    C1 --> C1b["Address"]
    C1 --> C1c["Country/State/City"]
    C1 --> C1d["Zip Code"]
    C1 --> C1e["Status<br/>Active/Inactive"]
    
    %% Storage Locations Page Components
    D --> D1["📦 Storage Locations Table"]
    D --> D2["🔍 Filter Panel"]
    D --> D3["⚡ Action Buttons"]
    
    %% Storage Table Columns
    D1 --> D1a["Location Name"]
    D1 --> D1b["Warehouse"]
    D1 --> D1c["Location Code"]
    D1 --> D1d["Location Type"]
    D1 --> D1e["Max Capacity"]
    D1 --> D1f["Status"]
    
    %% Stock Transfer Page
    E --> E1["🔄 Transfer Form"]
    E --> E2["📋 Transfer History"]
    
    %% DSR Storage Page
    F --> F1["🚚 DSR Storages Table"]
    F --> F2["📊 DSR Inventory"]
    
    %% Action Buttons
    C3 --> C3a["➕ Add Warehouse"]
    D3 --> D3a["➕ Add Storage Location"]
    E2 --> E2a["📤 Export Transfer History"]
    
    %% Row Actions
    D --> D4["⋮ Actions Menu (per row)"]
    D4 --> D4a["✏️ Edit Location"]
    D4 --> D4b["🗑️ Delete Location"]
    
    %% Styling
    classDef userAction fill:#e1f5ff,stroke:#01579b,stroke-width:2px
    classDef page fill:#fff8e1,stroke:#ff6f00,stroke-width:2px
    classDef component fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef data fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    
    class A,B,C,D,E,F userAction
    class C1,D1,E1,F1 page
    class C2,C3,D2,D3,E2,F2 component
    class C1a,C1b,C1c,C1d,C1e,D1a,D1b,D1c,D1d,D1e,D1f data
```

### How to Navigate the Warehouse Pages

1. **Getting There**: Click "Warehouses" in the left sidebar menu after logging in
2. **What You See**: Options to view Warehouses, Storage Locations, Stock Transfer, or DSR Storages
3. **Quick Actions**: Use the buttons at the top for common tasks (Add, Transfer)
4. **Row Actions**: Click the "⋮" (three dots) on any row to edit or delete that location

### UI Elements - Storage Locations List Page

| Component | Type | Description |
|-----------|------|-------------|
| Search Input | Text Field | Search by location name |
| Warehouse Filter | Dropdown | Filter by warehouse |
| Location Type Filter | Dropdown | Filter by type (e.g., Rack, Bin, Zone) |
| Status Filter | Dropdown | Active/Inactive filter |
| Max Capacity | Range | Min/Max capacity filter |
| Add Storage | Button | Navigate to creation page |
| Storage Table | Data Table | Paginated list with sorting |
| Actions Menu | Dropdown | Edit, Delete |

---

## 2. Storage Location Management Workflow

### 2.1 Step-by-Step: Creating a New Storage Location

**Overview**: This workflow guides you through creating a storage location within a warehouse.

```mermaid
flowchart TD
    %% Start
    A["🚀 Click 'New Storage' button"] --> B["📄 Storage Location Form Opens"]
    
    %% Form Fields
    B --> C["📋 Enter Storage Location Details"]
    C --> C1["🏷️ Location Name*<br/>Example: 'Rack A-1'"]
    C --> C2["🏷️ Location Code*<br/>Example: 'WH1-R-A1'"]
    C --> C3["📂 Location Type*<br/>Example: 'Rack', 'Bin', 'Zone'"]
    C --> C4["📊 Max Capacity<br/>Maximum items this location can hold"]
    
    %% Warehouse Assignment
    C --> D["🏭 Assign to Warehouse*"]
    D --> D1["Select from warehouse dropdown"]
    D --> D2["System auto-assigns company"]
    
    %% Status
    D --> E["✓ Set Active Status"]
    E --> E1["Toggle ON/OFF (default: ON)"]
    
    %% Validation
    E --> F["💾 Click 'Create' button"]
    F --> G{"🔍 Validation Check"}
    G -->|Duplicate Name/Code| G1["❌ Error: 'Storage location already exists'"]
    G1 --> C
    G -->|Invalid| G2["❌ Show field errors"]
    G2 --> C
    G -->|Valid| H["✅ Ready to save"]
    
    %% Backend Process
    H --> I["🌐 API Call: POST /warehouse/storage-locations"]
    I --> J["💾 Creating Storage Location Record"]
    J --> K["✅ Storage location saved successfully!"]
    K --> L["🏠 Redirecting to Storage Locations List..."]
    L --> M["🎉 Success message displayed"]
    
    %% Styling
    classDef start fill:#e3f2fd,stroke:#1565c0,stroke-width:3px
    classDef step fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef input fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef decision fill:#fff8e1,stroke:#f9a825,stroke-width:2px
    classDef error fill:#ffebee,stroke:#c62828,stroke-width:2px
    classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    classDef backend fill:#e0f2f1,stroke:#00695c,stroke-width:2px
    
    class A start
    class B,C,F,G step
    class C1,C2,C3,C4,D1,D2,E1 input
    class G1,G2 error
    class H,K,L,M success
    class I,J backend
```

### 💡 Tips for Storage Location Creation

1. **Naming Convention**: Use consistent naming (e.g., Building-Section-Number)
2. **Location Code**: Make it unique and scannable if using barcode systems
3. **Location Types**: Define standard types (Rack, Bin, Floor, Cold Storage, etc.)
4. **Max Capacity**: Set realistic capacity limits for capacity planning

### 2.2 Editing a Storage Location

```mermaid
flowchart TD
    A["📦 Storage Locations List"] --> B["⋮ Click Actions menu"]
    B --> C["✏️ Select 'Edit'"]
    C --> D["🪟 Edit Modal Opens"]
    
    D --> D1["📝 Location Name"]
    D --> D2["🏷️ Location Code"]
    D --> D3["📂 Location Type"]
    D --> D4["📊 Max Capacity"]
    D --> D5["✓ Active Status"]
    
    D --> E["💾 Click 'Update' button"]
    E --> F{"❓ Has associated stock?"}
    F -->|Yes| F1["⚠️ Warning: Changes may affect inventory"]
    F -->|No| G["✅ Update saved"]
    F1 --> G
    
    G --> H["🌐 API: PATCH /warehouse/storage-locations/{id}"]
    H --> I["🎉 Success: 'Location updated'"]
    
    %% Styling
    classDef userAction fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef form fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef system fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    classDef warning fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    
    class A,B,C,D,E userAction
    class D1,D2,D3,D4,D5 form
    class F1,G,H,I system
    class F warning
```

### 2.3 Deleting a Storage Location

```mermaid
flowchart TD
    A["📦 Storage Locations List"] --> B["⋮ Click Actions menu"]
    B --> C["🗑️ Select 'Delete'"]
    C --> D["⚠️ Confirm Delete Dialog"]
    D --> D1["⌨️ Type location name to confirm"]
    
    D --> E{"❓ Has associated stock?"}
    E -->|Yes| F["❌ Error: 'Cannot delete - location has inventory'"]
    E -->|No| G["✅ Confirm deletion"]
    
    G --> H["🌐 API: DELETE /warehouse/storage-locations/{id}"]
    H --> I["💾 Soft delete (marked as deleted)"]
    I --> J["🎉 Success: 'Location deleted'"]
    
    %% Styling
    classDef userAction fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef delete fill:#ffebee,stroke:#c62828,stroke-width:2px
    classDef system fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    
    class A,B,C,D,G userAction
    class D1,F delete
    class E,H,I,J system
```

### 2.4 Field Requirements & Validation

| Field | Required | Validation Rules |
|-------|----------|------------------|
| Location Name | Yes | Min 1 char, unique per company |
| Location Code | Yes | Min 1 char, unique per company |
| Location Type | Yes | Must not be empty |
| Warehouse ID | Yes | Must exist in system |
| Max Capacity | No | Number >= 0 |
| Is Active | No | Boolean (default: true) |

---

## 3. Inventory Stock Management Workflow

### 3.1 Viewing Inventory Stock

**What happens when you view inventory stock:**

```mermaid
flowchart TD
    %% Entry
    A["👤 User clicks 'Inventory' or 'Stock Report'"] --> B["🔐 System identifies your company"]
    
    %% Loading Data
    B --> C["📦 Loading inventory data..."]
    C --> C1["📊 Loading products list"]
    C --> C2["📍 Loading storage locations"]
    C --> C3["⚖️ Loading units of measure"]
    
    %% Stock Query
    C --> D["🔍 Querying stock levels..."]
    D --> D1["📡 API: GET /warehouse/inventory-stock"]
    D --> D2["💾 Database aggregates quantities"]
    D --> D3["📄 Returns stock per product/variant/location"]
    
    %% Display
    D3 --> E["🖥️ Displaying Stock Table"]
    E --> E1["📊 Product Name"]
    E --> E2["🎨 Variant (SKU)"]
    E --> E3["📍 Location"]
    E --> E4["📦 Quantity"]
    E --> E5["⚖️ Unit of Measure"]
    E --> E6["📅 Last Stock Take Date"]
    
    %% Filters
    E --> F["🔍 Available Filters"]
    F --> F1["Product filter"]
    F --> F2["Location filter"]
    F --> F3["Variant filter"]
    
    %% Styling
    classDef userAction fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef system fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    classDef data fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef api fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    
    class A userAction
    class B,C,D,E,F system
    class C1,C2,C3,E1,E2,E3,E4,E5,E6,F1,F2,F3 data
    class D1 api
```

### 3.2 Creating/Updating Inventory Stock

**⚠️ IMPORTANT**: When batch tracking is enabled, manual stock creation/update is blocked. Use batch operations instead.

```mermaid
flowchart TD
    A["👤 User attempts to create/update stock"] --> B{"🔍 Is batch tracking enabled?"}
    
    B -->|Yes| C["❌ BLOCKED: 'Manual stock mutation disabled in batch mode'"]
    C --> C1["💡 Use batch operations instead"]
    
    B -->|No| D["✅ Continue with stock operation"]
    
    %% Create Stock Flow
    D --> E["📝 Enter Stock Details"]
    E --> E1["📦 Select Product*"]
    E --> E2["🎨 Select Variant (optional)"]
    E --> E3["📍 Select Location*"]
    E --> E4["📊 Enter Quantity*"]
    E --> E5["⚖️ Unit of Measure (auto-filled from variant)"]
    
    E --> F["💾 Save Stock Record"]
    F --> G["🌐 API: POST/PATCH /warehouse/inventory-stock"]
    G --> H["💾 Database saves record"]
    H --> I["🎉 Success message"]
    
    %% Update Flow - Transaction Log
    D --> J["📝 Update Stock Quantity"]
    J --> K["💾 Save Changes"]
    K --> L["🌐 API: PATCH /warehouse/inventory-stock/{id}"]
    L --> M["📋 Create Inventory Transaction"]
    M --> M1["Transaction Type: ADJUSTMENT"]
    M --> M2["Reference: MANUAL_UPDATE"]
    M --> M3["Record quantity delta"]
    M --> N["💾 Update saved + Transaction logged"]
    
    %% Styling
    classDef blocked fill:#ffebee,stroke:#c62828,stroke-width:3px
    classDef allowed fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    classDef input fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef system fill:#e0f2f1,stroke:#00695c,stroke-width:2px
    
    class B decision
    class C,C1 blocked
    class D,E,F,G,H,I,J,K,L,M,N allowed
    class E1,E2,E3,E4,E5,M1,M2,M3 input
```

### 3.3 Deleting Inventory Stock

```mermaid
flowchart TD
    A["👤 User attempts to delete stock"] --> B{"🔍 Is batch tracking enabled?"}
    
    B -->|Yes| C["❌ BLOCKED: Manual deletion disabled"]
    
    B -->|No| D["✅ Check batch quantities"]
    D --> E{"❓ Are there batch quantities?"}
    
    E -->|Yes| F["❌ Error: 'Cannot delete - batches exist'"]
    F --> F1["💡 Delete/transfer batch quantities first"]
    
    E -->|No| G["✅ Proceed with deletion"]
    G --> H["🌐 API: DELETE /warehouse/inventory-stock/{id}"]
    H --> I["💾 Stock record soft-deleted"]
    I --> J["🎉 Success message"]
    
    %% Styling
    classDef blocked fill:#ffebee,stroke:#c62828,stroke-width:2px
    classDef allowed fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    
    class C,F,F1 blocked
    class D,E,G,H,I,J allowed
```

---

## 4. Stock Transfer Workflow

### 4.1 Creating a Stock Transfer

**Overview**: Transfer stock from one location to another with transaction logging.

```mermaid
flowchart TD
    %% Start
    A["🚀 Navigate to Stock Transfer page"] --> B["📄 Stock Transfer Form Opens"]
    
    %% Step 1: Source & Target
    B --> C["📍 STEP 1: Select Locations"]
    C --> C1["🏭 From Location*<br/>Source storage location"]
    C --> C2["🏭 Mother To Location<br/>Default target for all items (optional)"]
    
    %% Individual Override
    C2 --> D{"🤔 Override individual destinations?"}
    D -->|Yes| D1["✓ Show individual target locations per item"]
    D -->|No| E["📋 Continue to add items"]
    D1 --> E
    
    %% Step 2: Add Items
    E --> F["📦 STEP 2: Add Transfer Items"]
    F --> F1["➕ Click 'Add Product'"]
    F --> F2["📤 Or Import from Excel"]
    
    %% Item Details
    F1 --> G["📝 Item Details"]
    G --> G1["📦 Select Product*"]
    G --> G2["🎨 Select Variant (if applicable)"]
    G --> G3["📊 Enter Quantity*"]
    G --> G4["⚖️ Select Unit of Measure*"]
    G --> G5["📍 To Location*<br/>(if not using mother location)"]
    
    %% Validation
    G --> H{"✓ Sufficient stock?"}
    H -->|No| H1["⚠️ Warning: Insufficient stock"]
    H -->|Yes| I["✅ Item added to list"]
    
    %% More Items
    I --> J{"🤔 Add more items?"}
    J -->|Yes| F1
    J -->|No| K["📝 STEP 3: Add Notes (optional)"]
    
    %% Submit
    K --> L["💾 Click 'Transfer Stock'"]
    L --> M{"✓ All required fields valid?"}
    M -->|No| M1["❌ Show validation errors"]
    M1 --> G
    M -->|Yes| N["🌐 API: POST /warehouse/inventory-stock/transfer"]
    
    %% Backend Process
    N --> O["⚙️ SERVER PROCESSING"]
    O --> O1["🔍 Validate stock availability"]
    O --> O2["📉 Decrease source location stock"]
    O --> O3["📈 Increase target location stock"]
    O --> O4["📋 Create Inventory Transactions<br/>For audit trail"]
    O --> O5["📄 Create Stock Transfer Record"]
    
    %% Complete
    O5 --> P["✅ Transfer completed successfully!"]
    P --> Q["🎉 Success message displayed"]
    Q --> R["🏠 Redirect to inventory or stay on page"]
    
    %% Excel Import Path
    F2 --> S["📊 Excel Import Process"]
    S --> S1["📥 Download Template"]
    S --> S2["✏️ Fill Excel with SKU, Quantity, Target Location"]
    S --> S3["📤 Upload File"]
    S --> S4["⚙️ System validates and maps items"]
    S4 --> S5{"❓ Errors found?"}
    S5 -->|Yes| S6["📋 Show Import Report with skipped items"]
    S5 -->|No| G
    S6 --> G
    
    %% Styling
    classDef start fill:#e3f2fd,stroke:#1565c0,stroke-width:3px
    classDef step fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef input fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef decision fill:#fff8e1,stroke:#f9a825,stroke-width:2px
    classDef warning fill:#ffebee,stroke:#c62828,stroke-width:2px
    classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    classDef backend fill:#e0f2f1,stroke:#00695c,stroke-width:2px
    classDef import fill:#e1f5fe,stroke:#0288d1,stroke-width:2px
    
    class A start
    class B,C,F,K,L,M,O step
    class C1,C2,G1,G2,G3,G4,G5 input
    class D,H,J,M,S5 decision
    class H1,M1,S6 warning
    class I,N,P,Q,R success
    class O1,O2,O3,O4,O5 backend
    class S,S1,S2,S3,S4 import
```

### 4.2 Excel Import Format

| Column | Required | Description |
|----------|----------|-------------|
| **Variant SKU** | Yes | Product SKU to transfer |
| **Product Code** | Optional | Alternative product identifier |
| **Quantity** | Yes | Amount to transfer |
| **Unit Name** | Yes | Unit of measure (e.g., "Piece", "Box") |
| **Target Location** | Yes | Destination storage location name |

### 4.3 Viewing Transfer History

```mermaid
flowchart TD
    A["📋 Stock Transfer History Page"] --> B["🔍 Filter Options"]
    
    B --> B1["📅 Transfer Date Range"]
    B --> B2["📍 Source Location"]
    B --> B3["📍 Target Location"]
    B --> B4["📦 Product"]
    B --> B5["✓ Status"]
    
    A --> C["📊 Transfer History Table"]
    C --> C1["Transfer Code"]
    C --> C2["Transfer Date"]
    C --> C3["From Location"]
    C --> C4["To Location"]
    C --> C5["Product Count"]
    C --> C6["Total Quantity"]
    C --> C7["Status"]
    C --> C8["Notes"]
    
    C --> D["⋮ View Details"]
    D --> D1["📄 Transfer Detail Modal"]
    D1 --> D2["Item-by-item breakdown"]
    D1 --> D3["Product, Variant, Quantity per line"]
    
    %% Styling
    classDef userAction fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef data fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef view fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    
    class A,B,D userAction
    class B1,B2,B3,B4,B5,C1,C2,C3,C4,C5,C6,C7,C8 data
    class D1,D2,D3 view
```

---

## 5. DSR Storage Management Workflow

### 5.1 DSR Storage Overview

**DSR (Delivery Sales Representative) Storage**: Mobile storage locations assigned to each DSR. One-to-one relationship - each DSR has exactly one storage.

```mermaid
flowchart TD
    A["🚚 DSR Storage Management"] --> B{"🤔 What do you want to do?"}
    
    B -->|Create| C["➕ Create DSR Storage"]
    B -->|View/Edit| D["✏️ View/Edit DSR Storage"]
    B -->|Transfer Stock| E["🔄 DSR Stock Transfer"]
    B -->|View Inventory| F["📊 View DSR Inventory"]
    
    %% Create Flow
    C --> C1["📋 DSR Storage Form"]
    C1 --> C2["👤 Select DSR*<br/>Each DSR can have only one storage"]
    C2 --> C3{"❓ DSR already has storage?"}
    C3 -->|Yes| C4["❌ Error: 'DSR already has storage'"]
    C3 -->|No| C5["📝 Enter Storage Details"]
    C5 --> C6["🏷️ Storage Name*"]
    C5 --> C7["🏷️ Storage Code*"]
    C5 --> C8["📂 Storage Type*<br/>e.g., 'Van', 'Mobile', 'Temporary'"]
    C5 --> C9["📊 Max Capacity"]
    C5 --> C10["💾 Save DSR Storage"]
    
    %% View/Edit Flow
    D --> D1["📋 DSR Storages List"]
    D1 --> D2["🔍 Filter by DSR, Type, Status"]
    D1 --> D3["✏️ Click to edit"]
    D3 --> D4["Update Name, Code, Type, Capacity"]
    
    %% Transfer Flow
    E --> E1["🔄 DSR Stock Transfer Form"]
    E1 --> E2["📍 Source: Storage Location OR DSR Storage"]
    E1 --> E3["📍 Target: Storage Location OR DSR Storage"]
    E1 --> E4["🚫 Cannot transfer to same location type"]
    E1 --> E5["📦 Add Products to Transfer"]
    E1 --> E6["💾 Execute Transfer"]
    
    %% Inventory Flow
    F --> F1["📊 DSR Inventory Stock List"]
    F1 --> F2["🔍 Filter by DSR, Product"]
    F1 --> F3["📦 View Stock Levels per DSR"]
    
    %% Styling
    classDef userAction fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef error fill:#ffebee,stroke:#c62828,stroke-width:2px
    classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    classDef form fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    
    class A,B,C,D,E,F userAction
    class C3 error
    class C4 error
    class C5,C6,C7,C8,C9,C10,D4,E2,E3,E4,E5,E6 form
    class C10,D4,E6 success
```

### 5.2 DSR Stock Transfer

```mermaid
flowchart TD
    A["🔄 DSR Stock Transfer"] --> B["📍 Select Source"]
    B --> B1["🏭 Storage Location"]
    B --> B2["🚚 DSR Storage"]
    
    A --> C["📍 Select Target"]
    C --> C1["🏭 Storage Location"]
    C --> C2["🚚 DSR Storage"]
    
    %% Validation
    D{"❓ Source = Target?"}
    B --> D
    C --> D
    
    D -->|Yes| E["❌ Error: Source and Target cannot be same"]
    D -->|No| F["✅ Valid transfer path"]
    
    %% Valid Scenarios
    F --> F1["Scenario 1:<br/>Warehouse → DSR (Loading)"]
    F --> F2["Scenario 2:<br/>DSR → Warehouse (Return)"]
    F --> F3["Scenario 3:<br/>DSR → DSR (Not supported)"]
    
    F1 --> G["📦 Add Products"]
    F2 --> G
    
    G --> H["📝 Product, Quantity, Unit"]
    H --> I["💾 Execute Transfer"]
    I --> J["✅ Transfer Complete"]
    
    %% Styling
    classDef source fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef target fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef error fill:#ffebee,stroke:#c62828,stroke-width:2px
    classDef valid fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    
    class A,B,C source
    class C1,C2 target
    class D decision
    class E error
    class F,F1,F2,F3,G,H,I,J valid
```

### 5.3 DSR Storage Field Requirements

| Field | Required | Description |
|-------|----------|-------------|
| DSR | Yes | One-to-one relationship with DSR |
| Storage Name | Yes | Unique name for the storage |
| Storage Code | Yes | Unique code (e.g., DSR-VAN-001) |
| Storage Type | Yes | Type classification |
| Max Capacity | No | Maximum holding capacity |
| Is Active | No | Boolean status |

---

## 6. Data Models

### 6.1 Entity Relationship Diagram

```mermaid
erDiagram
    WAREHOUSE ||--o{ STORAGE_LOCATION : contains
    STORAGE_LOCATION ||--o{ INVENTORY_STOCK : tracks
    STORAGE_LOCATION ||--o{ STOCK_TRANSFER : sources
    STORAGE_LOCATION ||--o{ STOCK_TRANSFER_DETAILS : receives
    
    PRODUCT ||--o{ INVENTORY_STOCK : stocked_as
    PRODUCT_VARIANT ||--o{ INVENTORY_STOCK : stocked_as
    
    DSR_STORAGE ||--o{ DSR_INVENTORY_STOCK : tracks
    DSR_STORAGE ||--o{ DSR_STOCK_TRANSFER : sources_or_receives
    
    DELIVERY_SALES_REP ||--|| DSR_STORAGE : has_one
    
    WAREHOUSE {
        int warehouse_id PK
        string warehouse_name
        int company_id FK
        int country_id FK
        int state_id FK
        int city_id FK
        string address
        string zip_code
        boolean is_active
        timestamp cd
        timestamp md
    }
    
    STORAGE_LOCATION {
        int location_id PK
        int warehouse_id FK
        int company_id FK
        string location_name
        string location_code
        string location_type
        int max_capacity
        boolean is_active
        boolean is_deleted
        timestamp cd
        timestamp md
    }
    
    INVENTORY_STOCK {
        int stock_id PK
        int product_id FK
        int variant_id FK
        int location_id FK
        decimal quantity
        int uom_id FK
        timestamp last_stock_take_date
        int version
        boolean is_deleted
        timestamp cd
        timestamp md
    }
    
    STOCK_TRANSFER {
        int transfer_id PK
        string transfer_code UK
        timestamp transfer_date
        string status
        int source_location_id FK
        string notes
        int company_id FK
        boolean is_deleted
        timestamp cd
        timestamp md
    }
    
    STOCK_TRANSFER_DETAILS {
        int detail_id PK
        int transfer_id FK
        int target_location_id FK
        int product_id FK
        int variant_id FK
        decimal quantity
        int uom_id FK
        string notes
        boolean is_deleted
        timestamp cd
        timestamp md
    }
    
    DSR_STORAGE {
        int dsr_storage_id PK
        int dsr_id FK
        int company_id FK
        string storage_name
        string storage_code UK
        string storage_type
        int max_capacity
        boolean is_active
        boolean is_deleted
        timestamp cd
        timestamp md
    }
    
    DSR_INVENTORY_STOCK {
        int stock_id PK
        int product_id FK
        int variant_id FK
        int dsr_storage_id FK
        decimal quantity
        int uom_id FK
        timestamp last_stock_take_date
        boolean is_deleted
        timestamp cd
        timestamp md
    }
    
    DSR_STOCK_TRANSFER {
        int transfer_id PK
        string transfer_code UK
        timestamp transfer_date
        string status
        int source_location_id FK
        int source_dsr_storage_id FK
        int target_location_id FK
        int target_dsr_storage_id FK
        string notes
        int company_id FK
        boolean is_deleted
        timestamp cd
        timestamp md
    }
```

### 6.2 API Endpoints Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/warehouse/storage-locations` | GET | List storage locations with filters |
| `/warehouse/storage-locations` | POST | Create new storage location |
| `/warehouse/storage-locations/{id}` | PATCH | Update storage location |
| `/warehouse/storage-locations/{id}` | DELETE | Delete storage location |
| `/warehouse/inventory-stock` | GET | List inventory stock |
| `/warehouse/inventory-stock` | POST | Create inventory stock |
| `/warehouse/inventory-stock/{id}` | PATCH | Update inventory stock |
| `/warehouse/inventory-stock/{id}` | DELETE | Delete inventory stock |
| `/warehouse/inventory-stock/transfer` | POST | Transfer stock between locations |
| `/warehouse/stock-transfer` | GET | List stock transfers |
| `/warehouse/stock-transfer` | POST | Create stock transfer |
| `/warehouse/stock-transfer/{id}` | PATCH | Update stock transfer |
| `/warehouse/stock-transfer/{id}` | DELETE | Delete stock transfer |
| `/warehouse/dsr-storage` | GET | List DSR storages |
| `/warehouse/dsr-storage` | POST | Create DSR storage |
| `/warehouse/dsr-storage/{id}` | PATCH | Update DSR storage |
| `/warehouse/dsr-storage/{id}` | DELETE | Delete DSR storage |
| `/warehouse/dsr-storage/by-dsr/{dsr_id}` | GET | Get DSR storage by DSR ID |

### 6.3 Important Notes

#### Batch Tracking Mode
- When batch tracking is enabled for a company:
  - **Manual stock creation is BLOCKED** - use batch operations instead
  - **Manual stock updates are BLOCKED** - use batch adjustments instead
  - **Stock deletion is BLOCKED if batches exist** - delete batches first

#### Stock Transfer Rules
- Source and target locations **cannot be the same**
- Sufficient stock must exist at source location
- Transfer creates transaction records for audit trail
- Transfers are atomic operations (all succeed or all fail)

#### DSR Storage Constraints
- Each DSR can have **only ONE** storage location
- DSR storage code must be **unique**
- DSR storages are soft-deleted (not permanently removed)

---

## Quick Reference: Common Tasks

| Task | How To Do It |
|------|--------------|
| **Create new storage location** | Warehouses → Storage Locations → New Storage |
| **View stock levels** | Inventory → Stock Report or Stock by Location |
| **Transfer stock** | Warehouses → Stock Transfer → Fill form → Transfer |
| **Create DSR storage** | DSR → DSR Storages → New DSR Storage |
| **Load DSR van** | Stock Transfer → Source: Warehouse → Target: DSR Storage |
| **View transfer history** | Warehouses → Stock Transfer History |
| **Check batch tracking status** | Settings → Company Inventory Settings |
