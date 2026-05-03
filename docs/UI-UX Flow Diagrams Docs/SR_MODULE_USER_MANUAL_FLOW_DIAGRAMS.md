# SR Module - User Manual Flow Diagrams

## Table of Contents
1. [Overview](#overview)
2. [SR Module Entry Point](#1-sr-module-entry-point)
3. [Sales Representative Management](#2-sales-representative-management)
4. [Customer Assignment Workflow](#3-customer-assignment-workflow)
5. [Product Assignment Workflow](#4-product-assignment-workflow)
6. [SR Order Workflow](#5-sr-order-workflow)
7. [Commission Disbursement Workflow](#6-commission-disbursement-workflow)
8. [Pending Customer Workflow](#7-pending-customer-workflow)
9. [SR Dashboard & Reports](#8-sr-dashboard--reports)
10. [Data Models](#9-data-models)

---

## Overview

The SR (Sales Representative) Module manages field sales operations in Shoudagor ERP. It provides comprehensive tools for managing sales representatives, their customer assignments, product portfolios, order processing, and commission tracking.

### Key Entities
- **Sales Representative (SR)**: Field sales staff who create orders and manage customers
- **Customer Assignment**: Links customers to specific SRs for territory management
- **Product Assignment**: Products allocated to SRs with custom pricing
- **SR Order**: Orders created by SRs on behalf of customers
- **Commission**: Earnings calculated on SR orders
- **Disbursement**: Commission payments to SRs
- **Pending Customer**: New customers added by SRs awaiting admin approval
- **Beat**: Geographic sales territory for efficient route planning

---

## 1. SR Module Entry Point

### User Journey Overview

```mermaid
flowchart TD
    %% User Entry
    A["👤 User logs into Shoudagor ERP"] --> B{"📍 Where do you want to go?"}
    
    %% Navigation Options
    B -->|Click 'Sales Reps'<br/>in main menu| C["🧑‍💼 Sales Representatives Listing Page"]
    B -->|Click 'SR Orders'<br/>in main menu| D["📋 SR Orders Page"]
    B -->|Click 'Pending Customers'<br/>in main menu| E["⏳ Pending Customers Page"]
    B -->|Click 'Beats'<br/>in main menu| F["🗺️ Beats/Routes Page"]
    
    %% Sales Reps Page Components
    C --> C1["📊 Sales Representatives Table"]
    C --> C2["🔍 Search & Filter Panel"]
    C --> C3["⚡ Quick Action Buttons"]
    
    %% Table Columns
    C1 --> C1a["SR Code<br/>Unique identifier"]
    C1 --> C1b["SR Name<br/>Full name"]
    C1 --> C1c["Contact Info<br/>Email & Phone"]
    C1 --> C1d["Status<br/>Active/Inactive"]
    C1 --> C1e["Commission Balance<br/>Current earnings"]
    C1 --> C1f["Total Orders<br/>Order count"]
    C1 --> C1g["Total Sales<br/>Sales amount"]
    C1 --> C1h["Created Date<br/>When added"]
    
    %% Search & Filters
    C2 --> C2a["🔎 Search by name/code"]
    C2 --> C2b["✓ Filter by Status"]
    C2 --> C2c["📅 Creation Date Range"]
    C2 --> C2d["🔢 Sort by name/code/date"]
    
    %% Action Buttons
    C3 --> C3a["➕ Add Sales Rep"]
    C3 --> C3b["📤 Import / 📥 Export"]
    
    %% Row Actions
    C --> C4["⋮ Actions Menu (per row)"]
    C4 --> C4a["✏️ Edit SR"]
    C4 --> C4b["🗑️ Delete SR"]
    C4 --> C4c["👥 Manage Customers"]
    C4 --> C4d["📦 Manage Products"]
    C4 --> C4e["📊 View Orders"]
    C4 --> C4f["💰 Disburse Commission"]
    
    %% SR Orders Page
    D --> D1["📋 SR Orders Table"]
    D --> D2["🔍 Filter by Status/Date/SR"]
    D --> D3["📊 Consolidation Actions"]
    
    %% Pending Customers Page
    E --> E1["⏳ Pending Approval Table"]
    E --> E2["✅ Approve/Reject Actions"]
    
    %% Styling
    classDef userAction fill:#e1f5ff,stroke:#01579b,stroke-width:2px
    classDef page fill:#fff8e1,stroke:#ff6f00,stroke-width:2px
    classDef component fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef data fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    
    class A,B,C,D,E,F userAction
    class C1,D1,E1 page
    class C2,C3,C4,D2,D3,E2 component
    class C1a,C1b,C1c,C1d,C1e,C1f,C1g,C1h,C2a,C2b,C2c,C2d,C3a,C3b,C4a,C4b,C4c,C4d,C4e,C4f data
```

### How to Navigate the SR Module

1. **Getting There**: Click "Sales Reps" in the left sidebar menu after logging in
2. **What You See**: A table listing all sales representatives with filtering options above
3. **Quick Actions**: Use the buttons at the top for common tasks (Add, Import/Export)
4. **Row Actions**: Click the "⋮" (three dots) on any row to manage that specific SR

### UI Elements - Sales Reps List Page

| Component | Type | Description |
|-----------|------|-------------|
| Search Input | Text Field | Search by SR name or code |
| Status Filter | Dropdown | Active/Inactive filter |
| Date Range | Date Picker | Creation date range filter |
| Sort Dropdown | Dropdown | Sort by name, code, or date |
| Add Sales Rep | Button | Navigate to creation page |
| Import/Export | Button | Excel import/export functionality |
| SR Table | Data Table | Paginated list with sorting |
| Actions Menu | Dropdown | Edit, Delete, Manage Customers, Manage Products, View Orders, Disburse Commission |

---

## 2. Sales Representative Management

### 2.1 Step-by-Step: Creating a New Sales Representative

**Overview**: This workflow guides you through creating a sales representative with all necessary details.

```mermaid
flowchart TD
    %% Start
    A["🚀 Click 'Add Sales Rep' button"] --> B["📄 SR Creation Form Opens"]
    
    %% Step 1: Basic Information
    B --> C["📋 STEP 1: Basic Information"]
    C --> C1["📝 Enter SR Name*<br/>Example: 'John Smith'"]
    C --> C2["🏷️ Enter SR Code*<br/>Example: 'SR-001' or click '🎲 Generate'"]
    C --> C3["💡 Optional: Click 'Generate Code' button<br/>Auto-creates unique code"]
    C --> C4["🔍 System checks for duplicate SR code"]
    
    %% Duplicate Check
    C2 --> D{"❓ SR code already exists?"}
    D -->|Yes| D1["⚠️ Warning: 'SR code already exists'<br/>Please use a different code"]
    D -->|No| E["✅ Continue to next step"]
    
    %% Additional Fields
    E --> E1["📧 Enter Contact Email<br/>Optional email address"]
    E --> E2["📱 Enter Contact Phone<br/>Optional phone number"]
    E --> E3["✓ Set Active Status<br/>Toggle ON/OFF (default: ON)"]
    E --> E4["➡️ Click 'Create Sales Rep' button"]
    
    %% Validation
    E4 --> F{"🔍 Validation Check"}
    F -->|Invalid| F1["❌ Show field errors<br/>Red highlights on required fields"]
    F1 --> C
    F -->|Valid| G["✅ Ready to save"]
    
    %% API Call
    G --> H["🌐 API: POST /sr/sales-representative"]
    H --> I["💾 Creating SR Record"]
    I --> J["✅ SR saved successfully!"]
    J --> K["🏠 Redirecting to SR List..."]
    K --> L["🎉 Success! 'Sales Representative created successfully'"]
    
    %% Styling
    classDef start fill:#e3f2fd,stroke:#1565c0,stroke-width:3px
    classDef step fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef input fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef decision fill:#fff8e1,stroke:#f9a825,stroke-width:2px
    classDef error fill:#ffebee,stroke:#c62828,stroke-width:2px
    classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    classDef backend fill:#e0f2f1,stroke:#00695c,stroke-width:2px
    
    class A start
    class C step
    class C1,C2,C3,E1,E2,E3 input
    class D,F decision
    class D1,F1 error
    class G,L success
    class H,I,J backend
```

### 💡 Tips for SR Creation

1. **SR Code**: Use a consistent format (e.g., 'SR-' + number: SR-001)
2. **Unique Codes**: SR codes must be unique across your entire company
3. **Active Status**: New SRs are active by default; deactivate for temporary leave
4. **Contact Info**: Email and phone are optional but recommended for communication

### 2.2 Field Requirements & Validation

| Field | Required | Validation Rules |
|-------|----------|------------------|
| SR Name | Yes | Min 1 char, max 200 |
| SR Code | Yes | Min 1 char, max 50, unique per company |
| Contact Email | No | Valid email format, max 100 chars |
| Contact Phone | No | Max 20 chars |
| Is Active | Yes | Boolean, default true |

### 2.3 Editing a Sales Representative

```mermaid
flowchart TD
    A["👤 User wants to update an SR"] --> B["⋮ Click 'Actions' menu<br/>on the SR row"]
    B --> C["📋 Select 'Edit'<br/>from dropdown menu"]
    C --> D["🪟 SR Edit Form Opens"]
    
    %% Loading Data
    D --> D0["⏳ Loading current data..."]
    D0 --> D1["📊 Fetching SR details"]
    
    %% Form Display
    D --> E["📋 Edit Form Displayed"]
    E --> E1["📝 SR Name<br/>Editable"]
    E --> E2["🏷️ SR Code<br/>Editable with duplicate check"]
    E --> E3["📧 Contact Email<br/>Editable"]
    E --> E4["📱 Contact Phone<br/>Editable"]
    E --> E5["✓ Active Status<br/>Toggle ON/OFF"]
    
    %% Current Values Shown
    E --> F["👀 Current values pre-filled"]
    
    %% User Input
    F --> G["✏️ User makes changes"]
    G --> H["💾 Click 'Update' button"]
    
    %% Validation
    H --> I{"🔍 Validation Check"}
    I -->|Invalid| I1["❌ Show field errors"]
    I1 --> G
    I -->|Valid| J["✅ Ready to save"]
    
    %% API Decision
    J --> K["🌐 API: PATCH /sr/sales-representative/{id}"]
    
    %% Backend
    K --> L["💾 Updating SR in database"]
    
    %% Completion
    L --> M["🔄 Refreshing SR list"]
    M --> N["🎉 Success message:<br/>'SR updated successfully!'"]
    
    %% Styling
    classDef userAction fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef form fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef system fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    classDef api fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef error fill:#ffebee,stroke:#c62828,stroke-width:2px
    classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:3px
    
    class A,B,C,D,G,H userAction
    class E,E1,E2,E3,E4,E5,F,I form
    class D0,D1,L,M system
    class K api
    class I1 error
    class N success
```

### 2.4 Deleting a Sales Representative

```mermaid
flowchart TD
    A["🗑️ User wants to delete an SR"] --> B["⋮ Click 'Actions' menu<br/>on the SR row"]
    B --> C["❌ Select 'Delete' from dropdown"]
    C --> D["⚠️ Confirm Delete Dialog"]
    D --> E{"🔍 Check business rules"}
    E -->|Has active orders| E1["❌ Error: 'Cannot delete SR with active orders'"]
    E -->|No active orders| F["⌨️ Type SR name to confirm"]
    F --> G["✅ Click 'Confirm Delete'"]
    G --> H["🌐 API: DELETE /sr/sales-representative/{id}"]
    H --> I["💾 Soft delete SR record"]
    I --> J["🎉 Success: SR deleted"]
    
    %% Styling
    classDef action fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef warning fill:#fff8e1,stroke:#ff6f00,stroke-width:2px
    classDef error fill:#ffebee,stroke:#c62828,stroke-width:2px
    classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    classDef system fill:#e0f2f1,stroke:#00695c,stroke-width:2px
    
    class A,B,C,F,G action
    class D,E,E1 warning
    class H,I system
    class J success
```

---

## 3. Customer Assignment Workflow

### 3.1 Assigning Customers to an SR

**Overview**: Manage which customers belong to each sales representative for territory management.

```mermaid
flowchart TD
    %% Entry Points
    A["📍 Start Customer Assignment"] --> B{"🤔 How do you want to assign?"}
    
    %% Individual Assignment
    B -->|Individual| C["👤 Individual Assignment"]
    C --> C1["📋 Go to SR → Manage Customers"]
    C1 --> C2["➕ Click 'Assign Customer'"]
    C2 --> C3["🔍 Search & Select Customer"]
    C3 --> C4["✅ Click 'Assign'"]
    C4 --> C5["🌐 API: POST /sr/{id}/customer-assignments"]
    C5 --> C6["💾 Create Assignment Record"]
    C6 --> C7["🎉 Customer assigned to SR"]
    
    %% Bulk Assignment by Beat
    B -->|Bulk by Beat| D["🗺️ Bulk Assignment by Beat"]
    D --> D1["📋 Go to Beats Page"]
    D1 --> D2["🗺️ Select Beat (Territory)"]
    D2 --> D3["👥 View All Customers in Beat"]
    D3 --> D4["🧑‍💼 Select Target SR"]
    D4 --> D5["⚡ Click 'Assign All to SR'"]
    D5 --> D6{"🔍 Confirmation"}
    D6 -->|Cancel| D7["❌ Cancelled"]
    D6 -->|Confirm| D8["🌐 API: POST /sr/customer-assignments/bulk-by-beat"]
    D8 --> D9["💾 Create Multiple Assignments"]
    D9 --> D10["📊 Return Result:<br/>Success: X, Failed: Y"]
    D10 --> D11["🎉 Customers assigned to SR"]
    
    %% Styling
    classDef start fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef method fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef process fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef decision fill:#fff8e1,stroke:#f9a825,stroke-width:2px
    classDef system fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    
    class A,B start
    class C,D method
    class C1,C2,C3,C4,D1,D2,D3,D4,D5 process
    class D6 decision
    class C5,C6,D8,D9,D10 system
```

### 3.2 Customer Assignment Management

```mermaid
flowchart TD
    A["📊 Managing Customer Assignments"] --> B{"🤔 What do you want to do?"}
    
    %% View Assigned Customers
    B -->|View| C["👁️ View Assigned Customers"]
    C --> C1["📋 Navigate to SR → Manage Customers"]
    C1 --> C2["📊 Table shows:"]
    C2 --> C2a["Customer Name"]
    C2 --> C2b["Customer Code"]
    C2 --> C2c["Beat Name"]
    C2 --> C2d["Contact Phone"]
    C2 --> C2e["Assignment Date"]
    
    %% Reassign Customer
    B -->|Reassign| D["🔄 Reassign to Different SR"]
    D --> D1["⋮ Click Actions on Customer"]
    D1 --> D2["✏️ Select 'Reassign'"]
    D2 --> D3["🧑‍💼 Select New SR"]
    D3 --> D4["💾 Save Reassignment"]
    
    %% Unassign Customer
    B -->|Unassign| E["❌ Unassign Customer"]
    E --> E1["⋮ Click Actions on Customer"]
    E1 --> E2["🗑️ Select 'Unassign'"]
    E2 --> E3["⚠️ Confirm Removal"]
    E3 --> E4["💾 Remove Assignment"]
    
    %% Styling
    classDef action fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef view fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    classDef modify fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef remove fill:#ffebee,stroke:#c62828,stroke-width:2px
    
    class A,B,D,D1,D2,D3,D4 action
    class C,C1,C2,C2a,C2b,C2c,C2d,C2e view
    class E,E1,E2,E3,E4 remove
```

### 3.3 Field Requirements for Customer Assignment

| Field | Required | Description |
|-------|----------|-------------|
| SR ID | Yes | Sales Representative to assign to |
| Customer ID | Yes | Customer to be assigned |
| Assignment Date | Auto | Set to current timestamp |

---

## 4. Product Assignment Workflow

### 4.1 Assigning Products to an SR

**Overview**: Manage which products each SR can sell, with custom pricing and price override permissions.

```mermaid
flowchart TD
    %% Start
    A["📦 Assign Products to SR"] --> B["📋 Navigate to SR → Manage Products"]
    B --> C["📊 Current Assignments Table"]
    C --> D["➕ Click 'Assign Product'"]
    
    %% Product Selection
    D --> E["🔍 Product Selection Modal"]
    E --> E1["📂 Select Product*<br/>Search by name/code"]
    E --> E2["🎨 Select Variant<br/>Optional specific variant"]
    E --> E3["📊 View Current Stock"]
    E --> E4["💰 View Standard Sale Price"]
    
    %% Pricing Configuration
    E --> F["💰 Pricing Configuration"]
    F --> F1["💵 Assigned Sale Price<br/>Custom price for this SR"]
    F --> F2["📅 Effective Date<br/>When price becomes active"]
    F --> F3["📅 Expiry Date<br/>Optional end date"]
    F --> F4["🔓 Allow Price Override?<br/>Can SR negotiate?"]
    F --> F5["📉 Min Override Price<br/>Lowest allowed price"]
    F --> F6["📈 Max Override Price<br/>Highest allowed price"]
    F --> F7["📝 Price Notes<br/>Internal comments"]
    
    %% Save
    F --> G["💾 Click 'Save Assignment'"]
    G --> H{"🔍 Validation Check"}
    H -->|Invalid| H1["❌ Show validation errors"]
    H1 --> F
    H -->|Valid| I["🌐 API: POST /sr/{id}/product-assignments"]
    
    %% Backend Processing
    I --> J["💾 Create Assignment Record"]
    J --> K{"💰 Price defined?"}
    K -->|Yes| L["📝 Create Price History Entry"]
    K -->|No| M["⏭️ Continue"]
    L --> N["✅ Assignment Complete"]
    M --> N
    N --> O["🎉 Product assigned to SR"]
    
    %% Styling
    classDef start fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef selection fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef pricing fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef decision fill:#fff8e1,stroke:#f9a825,stroke-width:2px
    classDef error fill:#ffebee,stroke:#c62828,stroke-width:2px
    classDef system fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    
    class A,B,C,D,G start
    class E,E1,E2,E3,E4 selection
    class F,F1,F2,F3,F4,F5,F6,F7 pricing
    class H,K decision
    class H1 error
    class I,J,K,L,M,N,O system
```

### 4.2 Updating Product Assignment Price

```mermaid
flowchart TD
    A["💰 Update SR Product Price"] --> B["📋 Go to SR → Manage Products"]
    B --> C["⋮ Click Actions on Product"]
    C --> D["✏️ Select 'Update Price'"]
    
    %% Price Update Form
    D --> E["📋 Price Update Form"]
    E --> E1["👀 View Current Price"]
    E --> E2["💵 Enter New Sale Price*"]
    E --> E3["📅 Effective Date*<br/>When new price starts"]
    E --> E4["📅 Expiry Date<br/>Optional end date"]
    E --> E5["🔓 Update Override Permissions"]
    E --> E6["📝 Add Change Reason"]
    
    %% Save
    E --> F["💾 Click 'Update Price'"]
    F --> G["🌐 API: PATCH /sr/{id}/product-assignments/{assignment_id}/price"]
    
    %% Backend
    G --> H["💾 Update Assignment Price"]
    H --> I["📝 Create Price History Record"]
    I --> J["📊 Track: Old → New Price"]
    J --> K["✅ Price Updated"]
    K --> L["🎉 Success: Price updated"]
    
    %% Styling
    classDef action fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef form fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef system fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    
    class A,B,C,D,F action
    class E,E1,E2,E3,E4,E5,E6 form
    class G,H,I,J,K,L system
```

### 4.3 Product Assignment Field Reference

| Field | Required | Description |
|-------|----------|-------------|
| Product ID | Yes | Product to assign |
| Variant ID | No | Specific variant (optional) |
| Assigned Sale Price | No | Custom price for SR |
| Price Effective Date | No | When price starts |
| Price Expiry Date | No | When price ends |
| Allow Price Override | Yes | Can SR negotiate? Default: true |
| Min Override Price | No | Floor price for negotiation |
| Max Override Price | No | Ceiling price for negotiation |
| Price Notes | No | Internal comments |

---

## 5. SR Order Workflow

### 5.1 Creating an SR Order

**Overview**: SRs create orders for their assigned customers with negotiated pricing.

```mermaid
flowchart TD
    %% Start
    A["📋 Create SR Order"] --> B{"🤔 Entry Point?"}
    B -->|From SR Menu| C1["🧑‍💼 SR → Create Order"]
    B -->|From SR Orders| C2["📋 SR Orders → New Order"]
    
    %% Order Header
    C1 --> D["📝 Step 1: Order Header"]
    C2 --> D
    D --> D1["🧑‍💼 Select SR*<br/>Auto-filled if from SR menu"]
    D --> D2["👤 Select Customer*<br/>From SR's assigned customers"]
    D --> D3["📅 Order Date*<br/>Default: today"]
    D --> D4["📍 Select Location<br/>Where to fulfill from"]
    D --> D5["📝 Order Number<br/>Auto-generated"]
    
    %% Add Line Items
    D5 --> E["📦 Step 2: Add Line Items"]
    E --> E1["➕ Click 'Add Product'"]
    E1 --> E2["🔍 Product Selection Modal"]
    
    %% Product Selection
    E2 --> F["📋 Select Products"]
    F --> F1["🔍 Search Products<br/>SR's assigned products only"]
    F --> F2["📊 View Stock Levels"]
    F --> F3["💰 View Assigned Price"]
    F --> F4["📊 View Override Range<br/>If negotiation allowed"]
    
    %% Line Item Details
    F --> G["📝 Line Item Details"]
    G --> G1["📦 Select Product/Variant*"]
    G --> G2["⚖️ Select Unit of Measure"]
    G --> G3["📊 Enter Quantity*<br/>Greater than 0"]
    G --> G4["💰 Negotiated Price*<br/>Within allowed range"]
    G --> G5["💵 Sale Price<br/>Standard price reference"]
    
    %% Validation
    G --> H{"🔍 Price Validation"}
    H -->|Within Range| I["✅ Price Accepted"]
    H -->|Below Min| I1["❌ Error: Below minimum allowed"]
    H -->|Above Max| I2["❌ Error: Above maximum allowed"]
    I1 --> G4
    I2 --> G4
    
    %% Add More or Continue
    I --> J{"🤔 Add more items?"}
    J -->|Yes| E1
    J -->|No| K["💾 Click 'Create Order'"]
    
    %% Save Order
    K --> L["🌐 API: POST /sr/sr-orders"]
    L --> M["💾 Create Order Header"]
    M --> N["💾 Create Order Details"]
    N --> O["📊 Calculate Totals"]
    O --> P["✅ Order Created"]
    P --> Q["🎉 Success: SR Order created"]
    
    %% Styling
    classDef start fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef header fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef items fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef decision fill:#fff8e1,stroke:#f9a825,stroke-width:2px
    classDef error fill:#ffebee,stroke:#c62828,stroke-width:2px
    classDef system fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    
    class A,B,C1,C2,K,L start
    class D,D1,D2,D3,D4,D5 header
    class E,E1,E2,F,F1,F2,F3,F4,G,G1,G2,G3,G4,G5 items
    class H,J decision
    class I1,I2 error
    class I,M,N,O,P,Q system
```

### 5.2 SR Order Consolidation

**Overview**: Multiple SR orders from the same customer can be consolidated into a single Sales Order.

```mermaid
flowchart TD
    %% Start
    A["📊 Consolidate SR Orders"] --> B["📋 Go to SR Orders Page"]
    B --> C["🔍 Filter: Unconsolidated Orders"]
    C --> D["📊 View Grouped by Customer"]
    
    %% Customer Selection
    D --> E["👤 Select Customer with Orders"]
    E --> F["📋 View Their SR Orders"]
    F --> F1["📄 Order 1: #SR-001<br/>Total: 5,000"]
    F --> F2["📄 Order 2: #SR-002<br/>Total: 3,000"]
    F --> F3["📄 Order 3: #SR-003<br/>Total: 2,000"]
    
    %% Select Orders
    F --> G["☑️ Select Orders to Consolidate"]
    G --> H["⚡ Click 'Consolidate'"]
    
    %% Preview
    H --> I["📋 Consolidation Preview"]
    I --> I1["👤 Customer: ABC Store"]
    I --> I2["🧑‍💼 Consolidating SR: John Smith"]
    I --> I3["📊 Total Orders: 3"]
    I --> I4["💰 Combined Total: 10,000"]
    I --> I5["📦 Line Items Summary"]
    
    %% Confirm
    I --> J{"🤔 Confirm Consolidation?"}
    J -->|Cancel| K["❌ Cancelled"]
    J -->|Confirm| L["🌐 API: POST /sr/sr-orders/consolidate"]
    
    %% Backend
    L --> M["💾 Create Sales Order"]
    M --> N["💾 Create Sales Order Details"]
    N --> O["🔗 Link SR Orders to SO"]
    O --> P["📊 Mark SR Orders as Consolidated"]
    P --> Q["✅ Consolidation Complete"]
    Q --> R["🎉 Success: SO created from SR orders"]
    
    %% Styling
    classDef start fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef view fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef preview fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef decision fill:#fff8e1,stroke:#f9a825,stroke-width:2px
    classDef system fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    
    class A,B,C,D,E,G,H,J start
    class F,F1,F2,F3 view
    class I,I1,I2,I3,I4,I5 preview
    class L,M,N,O,P,Q,R system
```

### 5.3 SR Order Status Management

| Status | Description | Actions Available |
|--------|-------------|-------------------|
| **Pending** | New order, not yet processed | Edit, Delete, Consolidate |
| **Approved** | Order approved for processing | View, Consolidate |
| **Consolidated** | Merged into a Sales Order | View only |
| **Cancelled** | Order cancelled | View only |

---

## 6. Commission Disbursement Workflow

### 6.1 Disbursing Commission to SR

**Overview**: Process commission payments to sales representatives based on their orders.

```mermaid
flowchart TD
    %% Start
    A["💰 Commission Disbursement"] --> B["🧑‍💼 Navigate to SR List"]
    B --> C["⋮ Click Actions on SR"]
    C --> D["💰 Select 'Disburse Commission'"]
    
    %% View Orders Ready
    D --> E["📊 Orders Ready for Disbursement"]
    E --> E1["📋 Table of Orders:"]
    E1 --> E1a["Order #SR-001<br/>Commission: 500"]
    E1 --> E1b["Order #SR-002<br/>Commission: 300"]
    E1 --> E1c["Order #SR-003<br/>Commission: 200"]
    
    %% Calculate
    E --> F["🧮 Auto-Calculate Total"]
    F --> F1["💰 Total Commission: 1,000"]
    F --> F2["💵 Current Commission Balance"]
    
    %% Disbursement Form
    F --> G["📝 Disbursement Form"]
    G --> G1["💵 Disbursement Amount*<br/>Total or Partial"]
    G --> G2["📅 Disbursement Date*<br/>Default: today"]
    G --> G3["💳 Payment Method<br/>Cash, Bank, Check"]
    G --> G4["📝 Reference Number<br/>Receipt/Transaction ID"]
    G --> G5["📋 Notes<br/>Internal comments"]
    
    %% Select Orders (Optional)
    G --> H{"🤔 Link to Specific Orders?"}
    H -->|Yes| H1["☑️ Select Orders for Disbursement"]
    H -->|No| H2["💰 General Disbursement"]
    H1 --> I
    H2 --> I
    
    %% Save
    I --> I1["💾 Click 'Record Disbursement'"]
    I1 --> J["🌐 API: POST /sr/sr-orders/disbursements"]
    
    %% Backend
    J --> K["💾 Create Disbursement Record"]
    K --> L["📉 Deduct from Commission Balance"]
    L --> M["📊 Update Order Status<br/>commission_disbursed = 'Disbursed'"]
    M --> N["✅ Disbursement Recorded"]
    N --> O["🎉 Success: Commission disbursed"]
    
    %% Styling
    classDef start fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef view fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef form fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef decision fill:#fff8e1,stroke:#f9a825,stroke-width:2px
    classDef system fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    
    class A,B,C,D,I1,J start
    class E,E1,E1a,E1b,E1c,F,F1,F2 view
    class G,G1,G2,G3,G4,G5,H,H1,H2 form
    class K,L,M,N,O system
```

### 6.2 Bulk Commission Disbursement

```mermaid
flowchart TD
    A["⚡ Bulk Disbursement"] --> B["📋 Go to SR Orders"]
    B --> C["🔍 Filter: Ready for Disbursement"]
    C --> D["☑️ Select Multiple Orders"]
    D --> E["💰 Click 'Bulk Disburse'"]
    
    %% Summary
    E --> F["📊 Disbursement Summary"]
    F --> F1["🧑‍💼 Selected SRs: X"]
    F --> F2["📋 Selected Orders: Y"]
    F --> F3["💰 Total Commission: Z"]
    
    %% Confirm
    F --> G["⚡ Confirm Bulk Disburse"]
    G --> H["🌐 API: POST /sr/sr-orders/bulk-disburse"]
    
    %% Backend
    H --> I["💾 Process Each SR"]
    I --> I1["Create Disbursement Records"]
    I --> I2["Update Commission Balances"]
    I --> I3["Update Order Statuses"]
    I --> J["📊 Return Results:<br/>Success: X, Failed: Y"]
    J --> K["🎉 Bulk disbursement complete"]
    
    %% Styling
    classDef action fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef summary fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef system fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    
    class A,B,C,D,E,G,H action
    class F,F1,F2,F3 summary
    class I,I1,I2,I3,J,K system
```

### 6.3 Commission Status Reference

| Status | Description | Next Action |
|--------|-------------|-------------|
| **Pending** | Order created, commission not yet calculated | System auto-calculates |
| **Ready** | Commission calculated, ready for disbursement | Process disbursement |
| **Disbursed** | Commission paid to SR | None |

---

## 7. Pending Customer Workflow

### 7.1 SR Adding a New Customer

**Overview**: SRs can add new customers that require admin approval before becoming active.

```mermaid
flowchart TD
    %% Start
    A["➕ SR Adds New Customer"] --> B["📱 SR Mobile/Web App"]
    B --> C["👤 Navigate to Customers"]
    C --> D["➕ Click 'Add Customer'"]
    
    %% Customer Form
    D --> E["📝 Customer Information Form"]
    E --> E1["📝 Customer Name*<br/>Business name"]
    E --> E2["📝 Customer Code<br/>Optional unique code"]
    E --> E3["👤 Contact Person<br/>Primary contact"]
    E --> E4["📱 Contact Phone*<br/>Primary phone"]
    E --> E5["📧 Contact Email<br/>Email address"]
    E --> E6["📍 Address<br/>Full address"]
    
    %% Location
    E --> F["🗺️ Location Details"]
    F --> F1["🌍 Country<br/>Select from list"]
    F --> F2["🏛️ State/Province<br/>Select from list"]
    F --> F3["🏙️ City<br/>Select from list"]
    F --> F4["📮 ZIP Code<br/>Postal code"]
    
    %% Business Details
    F --> G["💼 Business Details"]
    G --> G1["💰 Credit Limit<br/>If known"]
    G --> G2["🗺️ Beat/Territory<br/>Assign to route"]
    
    %% Submit
    G --> H["📤 Click 'Submit for Approval'"]
    H --> I{"🔍 Validation Check"}
    I -->|Invalid| I1["❌ Show errors"]
    I1 --> E
    I -->|Valid| J["🌐 API: POST /sr/pending-customers"]
    
    %% Backend
    J --> K["💾 Create Pending Customer"]
    K --> L["📊 Status: Pending"]
    L --> M["🔔 Notify Admin<br/>New customer awaiting approval"]
    M --> N["✅ Submission Complete"]
    N --> O["🎉 Success: Customer submitted for approval"]
    
    %% Styling
    classDef start fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef form fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef location fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef decision fill:#fff8e1,stroke:#f9a825,stroke-width:2px
    classDef error fill:#ffebee,stroke:#c62828,stroke-width:2px
    classDef system fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    
    class A,B,C,D,H,J start
    class E,E1,E2,E3,E4,E5,E6,form
    class F,F1,F2,F3,F4 location
    class G,G1,G2 form
    class I decision
    class I1 error
    class K,L,M,N,O system
```

### 7.2 Admin Approving/Rejecting Pending Customer

```mermaid
flowchart TD
    %% Admin Entry
    A["✅ Admin Review"] --> B["📋 Go to Pending Customers"]
    B --> C["📊 View Pending Approval List"]
    
    %% Review Customer
    C --> D["👁️ Click to Review Customer"]
    D --> E["📋 Customer Details View"]
    E --> E1["📝 Name: ABC Store"]
    E --> E2["📱 Phone: +8801XXXXXXXX"]
    E --> E3["📍 Address: Full address"]
    E --> E4["🧑‍💼 Added by: SR John Smith"]
    E --> E5["📅 Submitted: 2024-01-15"]
    
    %% Decision
    E --> F{"🤔 Decision?"}
    
    %% Approve Path
    F -->|Approve| G["✅ Approve Customer"]
    G --> G1["✏️ Optional: Edit Details"]
    G1 --> G2["🗺️ Assign to Beat"]
    G2 --> G3["🧑‍💼 Auto-assign to Adding SR?<br/>Default: Yes"]
    G3 --> G4["💾 Confirm Approval"]
    G4 --> G5["🌐 API: POST /admin/pending-customers/{id}/approve"]
    G5 --> G6["💾 Create Active Customer"]
    G6 --> G7["🔗 Create SR Assignment<br/>(if configured)"]
    G7 --> G8["📊 Update Status: Approved"]
    G8 --> G9["🔔 Notify SR:<br/>'Customer approved'"]
    G9 --> G10["🎉 Customer is now active"]
    
    %% Reject Path
    F -->|Reject| H["❌ Reject Customer"]
    H --> H1["📝 Enter Rejection Reason*<br/>Required"]
    H1 --> H2["💾 Confirm Rejection"]
    H2 --> H3["🌐 API: POST /admin/pending-customers/{id}/reject"]
    H3 --> H4["📊 Update Status: Rejected"]
    H4 --> H5["🔔 Notify SR:<br/>'Customer rejected: [reason]'"]
    H5 --> H6["⚠️ Customer rejected"]
    
    %% Styling
    classDef start fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef view fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef decision fill:#fff8e1,stroke:#f9a825,stroke-width:2px
    classDef approve fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    classDef reject fill:#ffebee,stroke:#c62828,stroke-width:2px
    
    class A,B,C,D,F start
    class E,E1,E2,E3,E4,E5 view
    class G,G1,G2,G3,G4,G5,G6,G7,G8,G9,G10 approve
    class H,H1,H2,H3,H4,H5,H6 reject
```

### 7.3 Pending Customer Status Reference

| Status | Description | Actions |
|--------|-------------|---------|
| **Pending** | Awaiting admin review | SR can edit, Admin can approve/reject |
| **Approved** | Customer activated | Available for orders, Assigned to SR |
| **Rejected** | Not approved | SR can see reason, Can resubmit if needed |

---

## 8. SR Dashboard & Reports

### 8.1 SR Dashboard Overview

```mermaid
flowchart TD
    A["📊 SR Dashboard"] --> B["🎯 Key Metrics"]
    
    %% Metrics
    B --> C1["📋 Today's Orders<br/>Count & Amount"]
    B --> C2["📊 Month-to-Date Sales<br/>vs Target"]
    B --> C3["👥 My Customers<br/>Total assigned"]
    B --> C4["📦 Products Assigned<br/>Portfolio size"]
    B --> C5["💰 Commission Balance<br/>Current earnings"]
    
    %% Recent Activity
    A --> D["📈 Recent Activity"]
    D --> D1["📝 Recent Orders<br/>Last 5 orders"]
    D --> D2["⏳ Pending Approvals<br/>Customer submissions"]
    D --> D3["📦 Low Stock Alerts<br/>Assigned products"]
    
    %% Quick Actions
    A --> E["⚡ Quick Actions"]
    E --> E1["➕ New Order"]
    E --> E2["➕ Add Customer"]
    E --> E3["📋 View My Orders"]
    E --> E4["👥 View My Customers"]
    
    %% Styling
    classDef dashboard fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef metrics fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    classDef activity fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef actions fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    
    class A dashboard
    class B,C1,C2,C3,C4,C5 metrics
    class D,D1,D2,D3 activity
    class E,E1,E2,E3,E4 actions
```

### 8.2 Admin SR Dashboard

```mermaid
flowchart TD
    A["📊 Admin SR Dashboard"] --> B["🎯 Company-Wide Metrics"]
    
    %% Metrics
    B --> C1["🧑‍💼 Total SRs<br/>Active/Inactive count"]
    B --> C2["📊 Total SR Orders<br/>Today/This Month"]
    B --> C3["💰 Total Commission Due<br/>Pending disbursement"]
    B --> C4["⏳ Pending Customers<br/>Awaiting approval"]
    
    %% SR Performance
    A --> D["🏆 SR Performance"]
    D --> D1["📊 Top Performing SRs<br/>By sales amount"]
    D --> D2["📈 SR Order Trends<br/>Weekly/Monthly"]
    D --> D3["🗺️ Sales by Beat/Territory"]
    
    %% Actions
    A --> E["⚡ Administrative Actions"]
    E --> E1["✅ Review Pending Customers"]
    E --> E2["💰 Process Commission Disbursements"]
    E --> E3["📊 Generate SR Reports"]
    
    %% Styling
    classDef dashboard fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef metrics fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    classDef performance fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef actions fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    
    class A dashboard
    class B,C1,C2,C3,C4 metrics
    class D,D1,D2,D3 performance
    class E,E1,E2,E3 actions
```

---

## 9. Data Models

### 9.1 Entity Relationship Diagram

```mermaid
erDiagram
    SALES_REPRESENTATIVE ||--o{ CUSTOMER_SR_ASSIGNMENT : has
    SALES_REPRESENTATIVE ||--o{ SR_PRODUCT_ASSIGNMENT : has
    SALES_REPRESENTATIVE ||--o{ SR_ORDER : creates
    SALES_REPRESENTATIVE ||--o{ PENDING_CUSTOMER : adds
    SALES_REPRESENTATIVE ||--o{ SR_DISBURSEMENT : receives
    
    CUSTOMER ||--o{ CUSTOMER_SR_ASSIGNMENT : assigned_to
    CUSTOMER ||--o{ SR_ORDER : places
    
    PRODUCT ||--o{ SR_PRODUCT_ASSIGNMENT : assigned_to
    PRODUCT_VARIANT ||--o{ SR_PRODUCT_ASSIGNMENT : assigned_as
    
    SR_ORDER ||--o{ SR_ORDER_DETAIL : contains
    SR_ORDER ||--o{ SR_DISBURSEMENT : generates
    
    BEAT ||--o{ CUSTOMER : contains
    
    SR_PRODUCT_ASSIGNMENT ||--o{ PRICE_HISTORY : tracks
    
    SALES_REPRESENTATIVE {
        int sr_id PK
        string sr_code UK
        string sr_name
        string contact_email
        string contact_phone
        decimal commission_amount
        bool is_active
    }
    
    CUSTOMER_SR_ASSIGNMENT {
        int assignment_id PK
        int sr_id FK
        int customer_id FK
        timestamp assigned_date
    }
    
    SR_PRODUCT_ASSIGNMENT {
        int assignment_id PK
        int sr_id FK
        int product_id FK
        int variant_id FK
        timestamp assigned_date
        decimal assigned_sale_price
        timestamp price_effective_date
        timestamp price_expiry_date
        bool allow_price_override
        decimal min_override_price
        decimal max_override_price
    }
    
    SR_ORDER {
        int sr_order_id PK
        int sr_id FK
        int customer_id FK
        string order_number UK
        timestamp order_date
        string status
        decimal total_amount
        decimal amount_paid
        string commission_disbursed
    }
    
    SR_ORDER_DETAIL {
        int sr_order_detail_id PK
        int sr_order_id FK
        int product_id FK
        int variant_id FK
        decimal quantity
        decimal negotiated_price
        decimal sale_price
    }
    
    PENDING_CUSTOMER {
        int pending_customer_id PK
        string customer_name
        string contact_phone
        int added_by_sr_id FK
        string status
        timestamp submitted_at
        int approved_by FK
        timestamp approved_at
    }
    
    SR_DISBURSEMENT {
        int disbursement_id PK
        int sr_id FK
        int sr_order_id FK
        decimal amount
        timestamp disbursement_date
        string payment_method
    }
    
    BEAT {
        int beat_id PK
        string beat_code UK
        string beat_name
    }
```

### 9.2 API Endpoints Reference

#### Sales Representative Management
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/sr/sales-representative` | GET | List all SRs with filters |
| `/sr/sales-representative` | POST | Create new SR |
| `/sr/sales-representative/{id}` | GET | Get SR by ID |
| `/sr/sales-representative/{id}` | PATCH | Update SR |
| `/sr/sales-representative/{id}` | DELETE | Soft delete SR |
| `/sr/sales-representative/search/{code}` | GET | Get SR by code |

#### Customer Assignment
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/sr/{id}/customer-assignments` | GET | List SR's assigned customers |
| `/sr/{id}/customer-assignments` | POST | Assign customer to SR |
| `/sr/{id}/customer-assignments/bulk-by-beat` | POST | Bulk assign by beat |
| `/sr/{id}/customer-assignments/{assignment_id}` | DELETE | Unassign customer |

#### Product Assignment
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/sr/{id}/product-assignments` | GET | List SR's assigned products |
| `/sr/{id}/product-assignments` | POST | Assign product to SR |
| `/sr/{id}/product-assignments/{assignment_id}/price` | PATCH | Update assignment price |
| `/sr/{id}/product-assignments/{assignment_id}` | DELETE | Unassign product |

#### SR Orders
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/sr/sr-orders` | GET | List SR orders |
| `/sr/sr-orders` | POST | Create SR order |
| `/sr/sr-orders/unconsolidated-by-customer` | GET | Get unconsolidated orders grouped |
| `/sr/sr-orders/consolidate` | POST | Consolidate orders into SO |
| `/sr/sr-orders/disbursements` | GET | List disbursements |
| `/sr/sr-orders/disbursements` | POST | Record disbursement |
| `/sr/sr-orders/bulk-disburse` | POST | Bulk disburse commission |

#### Pending Customers
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/sr/pending-customers` | GET | List pending customers |
| `/sr/pending-customers` | POST | Submit new customer |
| `/admin/pending-customers/{id}/approve` | POST | Approve customer |
| `/admin/pending-customers/{id}/reject` | POST | Reject customer |

---

## Quick Reference Guide

### Common Tasks

| Task | Path | Key Action |
|------|------|------------|
| **Add Sales Rep** | Sales Reps → Add Sales Rep | Fill form, click Create |
| **Assign Customer** | SR → Manage Customers → Assign | Search and select customer |
| **Assign Product** | SR → Manage Products → Assign | Set price and override rules |
| **Create SR Order** | SR Orders → New Order | Select customer, add items |
| **Consolidate Orders** | SR Orders → Filter Unconsolidated → Select → Consolidate | Review and confirm |
| **Disburse Commission** | SR → Actions → Disburse Commission | Enter amount and method |
| **Approve Customer** | Pending Customers → Review → Approve | Verify details, assign SR |

### Status Meanings

**SR Order Status:**
- `pending` → New order, editable
- `approved` → Ready for consolidation
- `consolidated` → Merged into Sales Order
- `cancelled` → Order cancelled

**Commission Status:**
- `pending` → Not yet calculated
- `ready` → Ready for disbursement
- `disbursed` → Paid to SR

**Pending Customer Status:**
- `pending` → Awaiting admin review
- `approved` → Active customer
- `rejected` → Not approved

---

*Document Version: 1.0*  
*Last Updated: May 2026*  
*For: Shoudagor ERP SR Module*
