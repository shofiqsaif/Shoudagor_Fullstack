# Shoudagor Fullstack Project Context

> **Last Updated:** 2026-02-14  
> **Purpose:** Comprehensive documentation for LLMs and developers to understand the Shoudagor ERP system architecture, codebase structure, and key implementation details.

---

## 📋 Table of Contents
1. [Project Overview](#project-overview)
2. [Technology Stack](#technology-stack)
3. [Backend Architecture](#backend-architecture)
4. [Frontend Architecture](#frontend-architecture)
5. [Database Design](#database-design)
6. [API Structure](#api-structure)
7. [Key Business Domains](#key-business-domains)
8. [Elasticsearch Integration](#elasticsearch-integration)
9. [Frontend Hooks](#frontend-hooks)
10. [Common Patterns](#common-patterns)
11. [Quick Reference - Where to Find What](#quick-reference---where-to-find-what)

---

## 🎯 Project Overview

**Shoudagor** is a comprehensive, multi-tenant business management system (ERP) built specifically for the **Bangladeshi market**. It manages core business operations including:

- **Inventory Management** - Products, variants, categories, product groups
- **Sales** - Orders, customers, beats, invoices, payments, deliveries, returns
- **Procurement** - Purchase orders, suppliers, deliveries, payments, returns, rejections
- **Warehouse Management** - Storage locations, stock tracking, transfers, adjustments
- **Billing** - Invoices, invoice details, expenses
- **Sales Representatives (SR)** - Mobile workforce management, SR orders, consolidation, commissions, disbursements
- **Delivery Sales Representatives (DSR)** - Delivery workforce management, SO assignments, stock transfers, payment settlements
- **Financial Reporting** - Inventory KPIs, FIFO aging, purchase order reports, business analytics

### Project Structure
```
Shoudagor_Fullstack/
├── Shoudagor/           # Backend (FastAPI + Python)
│   ├── app/             # Main application code
│   ├── alembic/         # Database migrations
│   └── tests/           # Test suite
│
└── shoudagor_FE/        # Frontend (React + TypeScript)
    └── src/             # Source code
```

---

## 🛠️ Technology Stack

### Backend (Shoudagor/app/)
| Component | Technology | Version/Notes |
|-----------|------------|---------------|
| **Language** | Python | 3.x |
| **Web Framework** | FastAPI | Async-ready |
| **Database** | PostgreSQL | Multi-schema architecture |
| **ORM** | SQLAlchemy | 2.0+ |
| **Migrations** | Alembic | Version-controlled schema changes |
| **Search Engine** | Elasticsearch | 8.x for product/customer/supplier search |
| **Validation** | Pydantic | Request/Response schemas |
| **Containerization** | Docker & Docker Compose | Production deployment |

### Frontend (shoudagor_FE/src/)
| Component | Technology | Version/Notes |
|-----------|------------|---------------|
| **Framework** | React | With TypeScript |
| **Build Tool** | Vite | Fast development server |
| **Routing** | React Router | v7 |
| **State Management** | TanStack Query | (React Query) for server state |
| **UI Components** | shadcn/ui | Radix-based components |
| **Styling** | Tailwind CSS | Utility-first CSS |
| **Forms** | React Hook Form + Zod | Form validation |
| **Notifications** | Sonner + React Hot Toast | Toast notifications |

---

## 🏗️ Backend Architecture

### 5-Layer Clean Architecture

The backend strictly follows a **5-Layer Clean Architecture**:

```
┌─────────────────────────────────────────────────────────────┐
│                      API Layer (app/api/)                   │
│   FastAPI endpoints - Request/Response handling & routing   │
├─────────────────────────────────────────────────────────────┤
│                  Service Layer (app/services/)              │
│        Business logic, orchestration, complex rules         │
├─────────────────────────────────────────────────────────────┤
│               Repository Layer (app/repositories/)          │
│          Data access abstractions & query building          │
├─────────────────────────────────────────────────────────────┤
│                   Models Layer (app/models/)                │
│           SQLAlchemy ORM models - DB structure              │
├─────────────────────────────────────────────────────────────┤
│                  Schemas Layer (app/schemas/)               │
│      Pydantic models - Validation & serialization           │
└─────────────────────────────────────────────────────────────┘
```

### Directory Details

| Directory | Purpose | Key Files |
|-----------|---------|-----------|
| `app/api/` | Route handlers organized by domain | `security.py`, `admin.py`, `consolidation.py`, subdirs for each domain |
| `app/api/dsr/` | DSR-specific routes | `delivery_sales_representative.py`, `dsr_payment_settlement.py`, `dsr_so_assignment.py` |
| `app/api/sr/` | SR-specific routes | SR management, SR orders, assignments |
| `app/services/` | Business logic services | Domain-specific service files |
| `app/services/dsr/` | DSR business logic | `delivery_sales_representative_service.py`, `dsr_payment_settlement_service.py`, `dsr_so_assignment_service.py` |
| `app/repositories/` | Database query abstractions | Mirror service structure |
| `app/models/` | SQLAlchemy models (DB tables) | `inventory.py`, `sales.py`, `procurement.py`, `warehouse.py`, `billing.py`, etc. |
| `app/schemas/` | Pydantic validation schemas | Create/Update/Read schemas per entity |
| `app/schemas/dsr/` | DSR-specific schemas | `delivery_sales_representative.py`, `dsr_payment_settlement.py`, `dsr_so_assignment.py` |
| `app/core/` | Core config, DB connection, security | `config.py`, `database.py`, `security.py` |
| `app/subscribers/` | Event listeners (SQLAlchemy events) | `inventory_subscriber.py`, `product_subscriber.py` |

### Entry Point
- **Main Application:** `app/main.py`
  - Configures FastAPI app
  - Sets up CORS (allows `app.bitoroni.xyz`, `localhost:5173`, `localhost:3000`)
  - Registers all routers
  - Global exception handlers for validation, integrity, and SQLAlchemy errors

---

## 🎨 Frontend Architecture

### Directory Structure

```
shoudagor_FE/src/
├── App.tsx              # Main app entry with routing
├── main.tsx             # Vite entry point
├── index.css            # Global styles
├── components/          # Reusable UI components
│   ├── ui/              # Base UI components (shadcn/ui)
│   ├── forms/           # Form components (53 files)
│   │   ├── DSRAssignmentForm.tsx
│   │   ├── DSRDeliveryForm.tsx
│   │   ├── DSRForm.tsx
│   │   ├── DSRPaymentForm.tsx
│   │   ├── DSRSettlementForm.tsx
│   │   ├── DSRStorageForm.tsx
│   │   ├── PurchaseDeliveryForm.tsx
│   │   ├── PurchaseForm.tsx
│   │   ├── PurchaseReturnForm.tsx
│   │   ├── SaleForm.tsx
│   │   ├── SalesDeliveryForm.tsx
│   │   ├── SalesReturnForm.tsx
│   │   └── ... (40+ more forms)
│   ├── charts/          # Chart components
│   ├── shared/          # Shared components
│   ├── modals/          # Modal dialogs
│   ├── PrivateRoute.tsx # Auth-required routes
│   ├── AdminRoute.tsx   # Admin role guard
│   ├── SuperAdminRoute.tsx # Super admin role guard
│   ├── SRRoute.tsx      # SR role guard
│   └── DSRRoute.tsx     # DSR role guard
├── pages/               # Page components
│   ├── dsr/             # DSR management pages
│   │   ├── DeliverySalesRepresentatives.tsx
│   │   ├── DSRMyAssignments.tsx
│   │   ├── DSRSOAssignments.tsx
│   │   ├── DSRStorages.tsx
│   │   ├── DSRInventoryStock.tsx
│   │   ├── DSRSettlementHistory.tsx
│   │   └── new/AddDSR.tsx
│   ├── sr-orders/       # SR Order management pages
│   ├── reports/         # Report pages
│   │   ├── Reports.tsx
│   │   ├── Inventory.tsx
│   │   └── PurchaseOrder.tsx
│   └── ... (other domain pages)
├── lib/                 # Utilities and API layer
│   ├── api/             # API client functions (31 files)
│   │   ├── dsrApi.ts
│   │   ├── dsrInventoryStockApi.ts
│   │   ├── dsrSettlementApi.ts
│   │   ├── dsrStorageApi.ts
│   │   ├── reportsApi.ts
│   │   └── ... (25+ more API files)
│   ├── schema/          # Zod validation schemas
│   └── utils.ts         # Utility functions
├── contexts/            # React Context providers
├── hooks/               # Custom React hooks
└── types/               # TypeScript type definitions
```

### Routing Structure (App.tsx)

The app uses nested routing with role-based access:

```
/login                    → Public
/                        → Dashboard (Admin)
├── PrivateRoute (protected)
│   ├── /sales/pos       → POS (standalone)
│   ├── AdminRoute
│   │   ├── /dashboard
│   │   ├── /products, /products/new
│   │   ├── /categories, /categories/new
│   │   ├── /units, /units/new
│   │   ├── /product-groups, /product-groups/new
│   │   ├── /customers, /customers/new, /customers/dues
│   │   ├── /customers/beats, /customers/beats/new
│   │   ├── /suppliers, /suppliers/new
│   │   ├── /purchases, /purchases/new
│   │   ├── /sales, /sales/new
│   │   ├── /invoices
│   │   ├── /sales-representatives/*
│   │   │   ├── /sales-representatives
│   │   │   ├── /sales-representatives/new
│   │   │   ├── /sales-representatives/:id
│   │   │   ├── /sales-representatives/all-orders
│   │   │   ├── /sales-representatives/consolidated
│   │   │   ├── /sales-representatives/unconsolidated
│   │   │   ├── /sales-representatives/commissions
│   │   │   └── /sales-representatives/disbursement-history
│   │   ├── /dsr/*  (DSR Admin Management)
│   │   │   ├── /dsr
│   │   │   ├── /dsr/new
│   │   │   ├── /dsr/so-assignments
│   │   │   ├── /dsr/storage
│   │   │   └── /dsr/settlements
│   │   ├── /warehouse/*
│   │   │   ├── /warehouses/storage-locations
│   │   │   ├── /warehouses/storage-locations/new
│   │   │   ├── /warehouse/inventory-stock/transfer
│   │   │   ├── /warehouse/inventory-stock/adjustment
│   │   │   └── /warehouse/inventory
│   │   ├── /expenses, /expenses/new
│   │   ├── /reports, /reports/inventory, /reports/purchaseorder
│   │   └── /settings/invoice
│   ├── SuperAdminRoute
│   │   ├── /super-admin/user-categories, /super-admin/user-categories/new
│   │   ├── /super-admin/users, /super-admin/users/new
│   │   └── /super-admin/dsr-storage, /super-admin/dsr-storage/new
│   ├── SRRoute (Sales Rep mobile)
│   │   ├── /sr/orders, /sr/orders/new
│   │   ├── /sr/products
│   │   ├── /sr/customers
│   │   └── /sr/phone-suggestions
│   └── DSRRoute (Delivery Rep mobile)
│       ├── /dsr/my-assignments
│       └── /dsr/my-inventory
```

### Context Providers

| Context | Purpose | File |
|---------|---------|------|
| `ThemeProvider` | Light/Dark mode | `components/ThemeProvider.tsx` |
| `QueryClientProvider` | TanStack Query | Configured in `App.tsx` |
| `UserProvider` | User authentication state | `contexts/UserContext.tsx` |
| `SettingsProvider` | Application settings | `contexts/SettingsContext.tsx` |
| `BookmarksProvider` | User bookmarks | `contexts/BookmarksContext.tsx` |
| `ProductSelectionProvider` | Product selection state | `contexts/ProductSelectionContext.tsx` |

---

## 🗄️ Database Design

### Multi-Schema Architecture

The database uses **PostgreSQL multi-schema architecture** to logically separate different domains:

| Schema | Purpose | Key Tables |
|--------|---------|------------|
| `security` | User auth, permissions, multi-tenancy | `app_client`, `app_client_company`, `app_user`, `user_category`, `screen`, `module` |
| `inventory` | Products and stock management | `product`, `product_variant`, `product_category`, `unit_of_measure`, `product_price`, `product_group`, `claim_scheme`, `claim_slab`, `claim_log` |
| `sales` | Sales orders, customers, SR, DSR | `customer`, `sales_order`, `sales_order_detail`, `sales_representative`, `sr_order`, `beat`, `delivery_sales_representative`, `dsr_so_assignment`, `dsr_payment_settlement`, `sr_disbursement` |
| `procurement` | Purchase orders and suppliers | `supplier`, `purchase_order`, `purchase_order_detail`, `product_order_delivery_detail`, `product_order_payment_detail` |
| `warehouse` | Storage and stock tracking | `warehouse`, `storage_location`, `inventory_stock`, `stock_transfer`, `dsr_storage`, `dsr_inventory_stock`, `dsr_stock_transfer`, `dsr_stock_transfer_detail` |
| `billing` | Invoices and expenses | `invoice`, `invoice_detail`, `expenses` |
| `transaction` | Inventory movements | `inventory_transaction`, `inventory_adjustment`, `adjustment_detail`, `stock_log`, `stock_log_batch` |
| `settings` | System configuration | `country`, `state`, `city`, `currency` |

### Common Mixins (app/models/mixins.py)

All models use standardized mixins for consistency:

| Mixin | Fields | Purpose |
|-------|--------|---------|
| `TimestampMixin` | `cb`, `cd`, `mb`, `md` | Created by/date, Modified by/date (audit trail) |
| `IsDeletedMixin` | `is_deleted` | Soft delete support |
| `CompanyMixin` | `company_id` | Multi-tenancy (FK to `app_client_company`) |
| `IsActiveMixin` | `is_active` | Active/inactive status |
| `AddressMixin` | `address`, `country_id`, `state_id`, `city_id`, `zip_code` | Location data |
| `ContactAddressMixin` | Extends `AddressMixin` + `contact_person`, `contact_email`, `contact_phone`, `balance_amount` | Contacts |
| `OrderBase` | Common order fields | Abstract base for PurchaseOrder, SalesOrder, SR_Order |
| `OrderDetailBase` | Common line item fields | Abstract base for order details |
| `PaymentDetailBase` | Payment tracking fields | Abstract base for payments |
| `DeliveryDetailBase` | Delivery tracking fields | Abstract base for deliveries |

### Key Relationships

```
AppClientCompany (Multi-tenant root)
├── Users
├── Products → Variants → Prices
│             └── ProductGroups
├── Customers → Beats
│            └── SR Assignments
├── SalesRepresentatives → SR_Orders → SR_Order_Details
│                       └── Product Assignments
│                       └── Customer Assignments
│                       └── SRDisbursements
├── DeliverySalesRepresentatives → DSR_SO_Assignments
│                               └── DSR_Storage → DSR_Inventory_Stock
│                               └── DSR_Payment_Settlements
├── SalesOrders → SalesOrderDetails
│              └── SalesOrderPaymentDetails
│              └── SalesOrderDeliveryDetails
│              └── DSR_Assignment (loaded_by_dsr)
│              └── Invoices
├── PurchaseOrders → PurchaseOrderDetails (with returned_quantity, rejected_quantity)
│                 └── Delivery/Payment Details
├── Suppliers
├── Warehouses → StorageLocations → InventoryStock
│             └── DSRStorage → DSRInventoryStock
└── Invoices → InvoiceDetails
```

### Sales Order Fields

Key fields on `SalesOrder`:
- `order_source` - 'direct' or 'sr' (consolidated from SR orders)
- `is_consolidated` - Boolean indicating if consolidated from SR orders
- `consolidated_sr_orders` - JSON array of consolidated SR order IDs
- `total_price_adjustment` - Price adjustment during consolidation
- `consolidation_date` - When SR orders were consolidated
- `consolidated_by` - User who performed consolidation
- `is_loaded` - Whether loaded into DSR storage
- `loaded_by_dsr_id` - FK to DSR who loaded the order
- `loaded_at` - Timestamp when loaded
- `commission_disbursed` - Status: 'pending', 'ready', 'disbursed'

### Sales Order Detail Fields

Key fields on `SalesOrderDetail`:
- `shipped_quantity` - Quantity shipped/delivered
- `returned_quantity` - Quantity returned by customer
- `sr_order_detail_id` - Link to original SR order detail
- `negotiated_price` - Price negotiated by SR
- `price_difference` - Difference from standard price
- `sr_id` - FK to SR who created original order
- `provided_sale_price_to_sr` - Sale price given to SR

### Purchase Order Detail Fields

Key fields on `PurchaseOrderDetail`:
- `received_quantity` - Quantity actually received
- `returned_quantity` - Quantity returned to supplier
- `rejected_quantity` - Quantity rejected on receipt

### Invoice Fields

Key fields on `Invoice`:
- `subtotal` - Sum before discounts
- `discount_amount` - Discount applied
- `discount_type` - 'percentage' or 'fixed'
- `total_amount` - Final amount
- `tax_amount` - Tax applied
- `status` - 'Draft', 'Issued', 'Paid', 'Cancelled'
- `payment_status` - 'Unpaid', 'Partial', 'Paid'

---

## 🔌 API Structure

### Backend API Organization

**Base Path:** `/api/company/` (company-scoped routes)

| Domain | Route Prefix | Key Endpoints |
|--------|--------------|---------------|
| **Authentication** | `/authentication/` | `POST /login`, `POST /refresh-token` |
| **Users** | `/users/` | CRUD operations |
| **Security** | `/security/` | Roles, permissions, screens |
| **Inventory** | `/inventory/` | Products, variants, categories, units, prices |
| **Sales** | `/sales/` | Orders, customers, beats |
| **SR (Sales Rep)** | `/sr/` | SR management, SR orders, assignments |
| **DSR (Delivery Rep)** | `/dsr/` | DSR management, SO assignments, settlements |
| **Procurement** | `/procurement/` | Suppliers, purchase orders, deliveries, payments |
| **Warehouse** | `/warehouse/` | Storage locations, inventory stock, DSR storage |
| **Billing** | `/billing/` | Invoices, expenses |
| **Reports** | `/reports/` | Inventory KPIs, FIFO aging, purchase order reports |
| **Consolidation** | `/sales/consolidation/` | SR order consolidation |
| **Settings** | `/settings/` | Currency, locations |

### API Endpoint Patterns

1. **List with Pagination:** `GET /{resource}/?start=0&limit=20&search=...`
2. **Get Single:** `GET /{resource}/{id}`
3. **Create:** `POST /{resource}/`
4. **Update:** `PATCH /{resource}/{id}`
5. **Delete:** `DELETE /{resource}/{id}` (soft delete)

### Frontend API Layer (lib/api/)

| File | Backend Domain | Key Functions |
|------|----------------|---------------|
| `authApi.ts` | Authentication | `login()`, `refreshToken()` |
| `productsApi.ts` | Inventory | `getProducts()`, `createProduct()`, `searchProducts()` |
| `productVariantApi.ts` | Inventory | `getVariants()`, `createVariant()` |
| `salesApi.ts` | Sales | `getSales()`, `createSale()`, `getConsolidatedSROrders()` |
| `customerApi.ts` | Sales | `getCustomers()`, `createCustomer()` |
| `purchaseApi.ts` | Procurement | `getPurchases()`, `createPurchase()`, `recordDelivery()`, `processReturn()` |
| `salesRepresentativeApi.ts` | SR | `getSRs()`, `getSROrders()` |
| `srOrderApi.ts` | SR | `createSROrder()`, `getSROrders()` |
| `dsrApi.ts` | DSR | `getDSRs()`, `createDSR()`, `getDSRAssignments()` |
| `dsrInventoryStockApi.ts` | DSR | `getDSRInventoryStock()` |
| `dsrSettlementApi.ts` | DSR | `getSettlements()`, `createSettlement()` |
| `dsrStorageApi.ts` | DSR | `getDSRStorages()`, `transferStock()` |
| `inventoryApi.ts` | Warehouse | `getInventoryStock()`, `transferStock()` |
| `storageLocationsApi.ts` | Warehouse | `getStorageLocations()` |
| `reportsApi.ts` | Reports | `getInventoryKPIs()`, `getFIFOAging()`, `getPurchaseOrderReport()` |
| `invoiceApi.ts` | Billing | `getInvoices()`, `createInvoice()` |

---

## 📦 Key Business Domains

### 1. Inventory Management

**Location:** `app/models/inventory.py`, `app/api/inventory/`, `app/services/inventory/`

| Entity | Description |
|--------|-------------|
| **Product** | Base product with name, category, description |
| **ProductVariant** | SKU variations (size, color) with barcode, unit |
| **ProductCategory** | Hierarchical categories (parent-child) |
| **UnitOfMeasure** | Units with conversions (base_unit_id, conversion_factor) |
| **ProductPrice** | Time-effective pricing per variant |
| **ProductGroup** | Bundled products for bulk operations |
| **VariantGroup** | Grouped variants for rapid selection |
| **ProductVariantImage** | S3-hosted product images |

**Key Fields:**
- `reorder_level` - Minimum stock level before reordering
- `safety_stock` - Buffer stock to prevent stockouts

**Frontend Pages:**
- `/products` - Product list with search (Elasticsearch)
- `/products/new` - Add product with variants
- `/categories`, `/units`, `/product-groups`
- `/schemes` - Manage purchase and sales schemes

### 1.1 Claims & Schemes
**Location:** `app/models/claims.py`, `app/services/claims/claim_service.py`
- **ClaimScheme**: Defines promotional rules like `buy_x_get_y`, `rebate_flat`, or `rebate_percentage`.
- **ClaimSlab**: Tiers for schemes (e.g., Buy 5 Get 1, Buy 10 Get 3).
- **ClaimLog**: Audit trail of scheme applications linked to specific orders.
- **Workflow**: `ClaimService.evaluate_pre_claim` calculates benefits during order entry, which are then persisted as `ClaimLog` entries upon order finalization.

### 2. Sales Management

**Location:** `app/models/sales.py`, `app/api/sales/`, `app/services/sales/`

| Entity | Description |
|--------|-------------|
| **Customer** | Customer with balance tracking, beat assignment, credit limit, store credit |
| **Beat** | Geographic/route grouping for customers |
| **SalesOrder** | Sales transaction with status tracking, consolidation support, DSR loading |
| **SalesOrderDetail** | Line items with shipped_quantity, returned_quantity, SR pricing |
| **SalesOrderDeliveryDetail** | Delivery tracking |
| **SalesOrderPaymentDetail** | Payment tracking |
| **ClaimLog** | Promotional benefits applied to sales (captured in SalesOrderDetail) |

**Frontend Pages:**
- `/sales` - Sales orders list with DSR info, consolidation status
- `/sales/new` - Create sales order with automated scheme evaluation
- `/sales/pos` - Point of Sale interface
- `/customers`, `/customers/beats`, `/customers/dues`
- `/sales/deliveries` - Process deliveries via `UnifiedDeliveryForm`

### 3. Sales Representative (SR) Module

**Location:** `app/models/sales.py` (SR_Order, SR_Order_Detail), `app/api/sr/`, `app/services/sr/`

This is a **key differentiator** - manages mobile sales force:

| Entity | Description |
|--------|-------------|
| **SalesRepresentative** | Field sales person with user link, commission tracking |
| **SR_Order** | Order placed by SR (not yet converted to sales) |
| **SR_Order_Detail** | Line items with negotiated_price, sale_price, shipped/returned quantities |
| **SR_Product_Assignment** | Products an SR can sell |
| **Customer_SR_Assignment** | Customers assigned to SRs |
| **CustomerPhoneSuggestion** | SR-submitted customer phone updates (pending/approved/rejected) |
| **SRDisbursement** | Commission payment records |

**SR Order Flow:**
```
SR_Order (Draft) → Validation → Consolidation → SalesOrder (Finalized)
                                    ↓
                              Stock Deduction
                                    ↓
                              Invoice Generation
```

**Key Service:** `ConsolidationService` (`app/services/consolidation_service.py`)
- Validates SR orders for consolidation
- Checks stock availability at selected location
- Creates consolidated sales order
- Links SR order details to sales order details
- Handles transaction rollback on errors

**Frontend Pages (SR Role):**
- `/sr/orders` - SR's orders
- `/sr/orders/new` - Create SR order
- `/sr/products` - Assigned products
- `/sr/customers` - Assigned customers
- `/sr/phone-suggestions` - Submit phone number corrections

**Frontend Pages (Admin):**
- `/sales-representatives` - Manage SRs
- `/sales-representatives/all-orders` - View all SR orders
- `/sales-representatives/consolidated` - Consolidated orders
- `/sales-representatives/unconsolidated` - Pending consolidation
- `/sales-representatives/commissions` - Undisbursed commissions
- `/sales-representatives/disbursement-history` - Disbursement records

### 4. Delivery Sales Representative (DSR) Module

**Location:** `app/models/sales.py`, `app/models/warehouse.py`, `app/api/dsr/`, `app/services/dsr/`

This module manages the **delivery workforce** who physically deliver goods:

| Entity | Description |
|--------|-------------|
| **DeliverySalesRepresentative** | Delivery person with user link, payment_on_hand, commission |
| **DSRSOAssignment** | Links Sales Orders to DSRs for delivery (assigned/in_progress/completed) |
| **DSRPaymentSettlement** | Records when admin collects payments from DSR |
| **DSRStorage** | Virtual storage location for DSR (one-to-one with DSR) |
| **DSRInventoryStock** | Stock held in DSR's storage/van |
| **DSRStockTransfer** | Transfers between warehouse and DSR storage |
| **DSRStockTransferDetail** | Line items in DSR stock transfers |

**DSR Workflow:**
```
SalesOrder (Created) → DSR Assignment → Load Stock (DSRStorage)
                            ↓
                    DSR Delivers to Customer
                            ↓
                    Collect Payment (payment_on_hand increases)
                            ↓
                    Admin Settlement (payment_on_hand decreases)
```

**Frontend Pages (Admin):**
- `/dsr` - Manage DSRs
- `/dsr/new` - Add new DSR
- `/dsr/so-assignments` - Assign SOs to DSRs
- `/dsr/storage` - View DSR storages
- `/dsr/settlements` - Payment settlement history

**Super Admin Pages:**
- `/super-admin/dsr-storage` - Manage all DSR storages
- `/super-admin/dsr-storage/new` - Create DSR storage

**Frontend Pages (DSR Role):**
- `/dsr/my-assignments` - DSR's assigned orders
- `/dsr/my-inventory` - DSR's current inventory stock

### 5. Procurement Management

**Location:** `app/models/procurement.py`, `app/api/procurement/`, `app/services/procurement/`

| Entity | Description |
|--------|-------------|
| **Supplier** | Vendor with contact, payment terms |
| **PurchaseOrder** | Procurement transaction with delivery/payment status |
| **PurchaseOrderDetail** | Line items with quantity, received_quantity, returned_quantity, rejected_quantity |
| **ProductOrderDeliveryDetail** | Receiving tracking |
| **ProductOrderPaymentDetail** | Vendor payment tracking |

**Procurement Workflow:**
```
PurchaseOrder (Created) → Partial/Full Delivery → Payment
           ↓                      ↓
      Rejection            Stock Addition
           ↓
       Return
```

**Key computed property:** `effective_total_amount` calculates:
```python
effective_qty = quantity - returned_quantity - rejected_quantity
total = sum(effective_qty * unit_price for each detail)
```

**Frontend Pages:**
- `/purchases`, `/purchases/new` - Includes automated scheme evaluation for purchases
- `/suppliers`, `/suppliers/new`

**Frontend Forms:**
- `PurchaseForm.tsx` - Create/edit purchase orders
- `UnifiedDeliveryForm.tsx` - Handles both Billable and Free quantities for deliveries and rejections
- `PurchaseReturnForm.tsx` - Process returns including free quantity reconciliation
- `PurchasePaymentForm.tsx` - Record payments

### 6. Warehouse & Inventory Stock

**Location:** `app/models/warehouse.py`, `app/api/warehouse/`, `app/services/warehouse/`

| Entity | Description |
|--------|-------------|
| **Warehouse** | Physical warehouse location |
| **StorageLocation** | Specific storage area within warehouse |
| **InventoryStock** | Current stock level per product/variant/location |
| **StockTransfer** | Movement between storage locations |
| **StockTransferDetails** | Transfer line items |
| **DSRStorage** | Virtual storage for DSR (linked one-to-one) |
| **DSRInventoryStock** | Stock in DSR storage |
| **DSRStockTransfer** | Transfers to/from DSR storage |
| **DSRStockTransferDetail** | DSR transfer line items |
| **StockLog** | Comprehensive movement log with EPP and running balance |
| **StockLogBatch** | FIFO-based cost batches for inventory valuation |

**Inventory Stock Log & EPP Tracking:**
**Location:** `app/services/transaction/stock_log_service.py`
- **StockLog**: Captures every movement (IN/OUT) with a mandatory `unit_cost` (EPP).
- **Effective Purchase Price (EPP)**: The net cost basis for an item, factoring in discounts and free quantities.
- **FIFO Logic**: `StockLogBatch` ensures that stock is consumed in the order it was received for accurate COGS (Cost of Goods Sold) calculation.

**Inventory Transactions** (`app/models/transaction.py`):
- `InventoryTransaction` - All stock movements logged
- `InventoryAdjustment` - Stock corrections with approval

**Frontend Pages:**
- `/warehouse/inventory` - Stock levels
- `/warehouse/inventory-stock/transfer` - Transfer stock
- `/warehouse/inventory-stock/adjustment` - Adjust stock
- `/warehouses/storage-locations`

### 7. Billing & Invoices

**Location:** `app/models/billing.py`, `app/api/billing/`, `app/services/billing/`

| Entity | Description |
|--------|-------------|
| **Invoice** | Generated from sales order with subtotal, discounts, taxes, payment status |
| **InvoiceDetail** | Invoice line items with original_unit_price, unit_price, discount, tax |
| **Expense** | Business expense tracking with category, payment method |

**Invoice Fields:**
- `subtotal` - Sum before discounts
- `discount_amount`, `discount_type` - Discount tracking
- `total_amount` - Final amount
- `tax_amount` - Tax applied
- `status` - Draft/Issued/Paid/Cancelled
- `payment_status` - Unpaid/Partial/Paid

**Frontend Pages:**
- `/invoices` - Invoice list
- `/expenses`, `/expenses/new`

### 8. Reports Module

**Location:** `app/services/reports.py`, `app/api/reports.py`, `app/schemas/reports.py`

| Report | Description |
|--------|-------------|
| **Inventory KPI Ribbon** | Aggregated inventory metrics using LIFO costing |
| **FIFO Aging** | Inventory aging buckets (0-30, 31-60, 61-90, 90+ days) with COGS data |
| **Current Stock** | Stock with timeline, financial metrics per product/variant |
| **Purchase Order Report** | Comprehensive PO analytics by year or date range |

**Report Methods in `ReportsService`:**
- `get_inventory_kpi_ribbon_data()` - LIFO-based inventory metrics
- `calculate_fifo_aging()` - FIFO aging buckets and COGS
- `get_current_stock()` - Stock with financial timeline
- `get_purchase_order_report()` - PO analytics

**Frontend Pages:**
- `/reports` - Reports dashboard
- `/reports/inventory` - Inventory reports
- `/reports/purchaseorder` - Purchase order reports

### 9. Security & Multi-Tenancy

**Location:** `app/models/security.py`, `app/api/security.py`, `app/services/security.py`

| Entity | Description |
|--------|-------------|
| **AppClient** | Top-level tenant (business) |
| **AppClientCompany** | Company under a client (multi-company support) |
| **User** | System user (linked to SR or DSR if applicable) |
| **UserCategory** | Role/permission group |
| **Module/SubModule/Section/Screen** | Navigation hierarchy |
| **UserCategoryWiseScreen** | Permission per role |
| **UserWiseScreen** | Per-user permission overrides |
| **UserCompanyAccess** | Multi-company access per user |

**Authentication Flow:**
1. Login → Get token + user info + company context
2. All requests include company_id context
3. All queries filter by company_id (tenant isolation)

**Role Guards (Frontend):**
- `PrivateRoute` - Requires authentication
- `AdminRoute` - Requires admin role
- `SuperAdminRoute` - Requires super admin role
- `SRRoute` - Requires SR role
- `DSRRoute` - Requires DSR role

---

## 🔍 Elasticsearch Integration

**Location:** `app/services/product_elasticsearch_service.py`, `app/services/customer_elasticsearch_service.py`, `app/services/supplier_elasticsearch_service.py`

### Purpose

Elasticsearch provides **fast, fuzzy search** for:
- **Products & Variants** - Including nested variants, prices, and stock levels
- **Customers** - For quick customer lookup
- **Suppliers** - For procurement workflows

### Key Service: `ProductElasticsearchService`

| Method | Purpose |
|--------|---------|
| `search_products()` | Full-text search with nested field filtering |
| `search_by_sku()` | Dedicated SKU search with fuzzy/partial matching |
| `index_product()` | Index single product with all nested data |
| `index_all_products()` | Bulk reindex all products |
| `delete_product()` | Remove from index |
| `delete_index()` | Delete entire index (reindex scenario) |

### Index Structure

The `products` index uses **nested mappings** for:
- `variants` - Variant details, SKU, barcode
- `prices` - Price history with effective dates
- `stocks` - Inventory levels per location

### Usage Pattern

```python
# In API endpoint
service = ProductElasticsearchService.get_instance()
results = service.search_products(
    query="laptop",
    limit=20,
    filters={"company_id": 1, "category_id": 5}
)
```

### Configuration

Elasticsearch connection configured in `app/core/elasticsearch_config.py`

---

## 🔔 Notification System

**Location:** `app/models/notification.py`, `app/api/notification.py`, `app/services/notification/`

### Overview
A comprehensive notification system to alert users about critical events (e.g., low stock, pending approvals, order status changes).

### key Components
- **Backend:**
    - `Notification`: Stores notification data, status (read/unread), and priority.
    - `NotificationType`: Defines templates and categories for notifications.
    - `NotificationService`: Handles creation and retrieval of notifications.
- **Frontend:**
    - `NotificationDropdown`: UI component for viewing and managing notifications.
    - `useNotifications`: Hook for fetching and managing notification state.
    - `notificationApi.ts`: API client for notification endpoints.

---

## 📊 Dashboard & Activity Feed

**Location:** `app/services/dashboard_service.py`, `app/api/dashboard.py`

### Recent Activity Feed
Tracks and displays key business actions in real-time, providing visibility into user operations.

- **Captured Activities:**
    - Sales Orders (Created, Payment, Delivery)
    - Purchase Orders (Created, Payment, Receipt)
    - SR Disbursements & DSR Settlements
    - Stock Movements (Transfers, Adjustments, DSR Load/Unload)
    - Master Data Changes (Product, Customer, Supplier, etc.)
    
- **Features:**
    - **Performed By:** Tracks the specific user who performed the action.
    - **Pagination:** Supports infinite scroll/pagination for traversing history.
    - **Filtering:** Aggregated view of all major system events.

---

## 🪝 Frontend Hooks

**Location:** `src/hooks/`

| Hook | Purpose | File |
|------|---------|------|
| `useAuth` | Access auth context | `useAuth.ts` |
| `useDebounce` | Debounce inputs for search | `useDebounce.ts` |
| `usePagination` | Pagination state management | `use-pagination.ts` |
| `usePaginationHook` | Alternative pagination | `use-pagination-hook.ts` |
| `useFilter` | Filter state management | `use-filter.ts` |
| `useMobile` | Mobile viewport detection | `use-mobile.ts` |
| `useDevice` | Device type detection | `use-device.ts` |
| `useSliderWithInput` | Slider + input sync | `use-slider-with-input.ts` |
| `useBookmarks` | Access bookmarks context | `useBookmarks.ts` |
| `useSettings` | Access settings context | `useSettings.ts` |
| `useFreezeRefresh` | Prevent query refetch | `useFreezeRefresh.ts` |

### Common Hook Usage

```typescript
// Debounced search
const [search, setSearch] = useState('');
const debouncedSearch = useDebounce(search, 300);

// Pagination
const { page, limit, setPage, offset } = usePagination();

// Mobile detection
const isMobile = useMobile();
```

---

## 🔄 Common Patterns

### Backend Development Patterns

#### 1. Creating a New Feature (Full Stack)

```
1. Model (app/models/{domain}.py)
   └── Define SQLAlchemy class with mixins
   
2. Schema (app/schemas/{domain}/)
   └── Create Pydantic schemas: {Entity}Create, {Entity}Update, {Entity}Read
   
3. Repository (app/repositories/{domain}/)
   └── Implement data access methods
   
4. Service (app/services/{domain}/)
   └── Implement business logic
   
5. API (app/api/{domain}/)
   └── Define FastAPI router with endpoints
   
6. Migration (alembic/)
   └── alembic revision --autogenerate -m "description"
```

#### 2. Effective Trading Price (Eff. TP)
**Used in Sales/Procurement Details** to calculate the net price per item:
```python
@property
def effective_tp(self):
    total_qty = (self.quantity or 0) + (self.free_quantity or 0)
    gross_price = (self.quantity or 0) * (self.unit_price or 0)
    discount = (self.discount_amount or 0)
    return float((gross_price - discount) / total_qty) if total_qty > 0 else 0.0
```

#### 3. Stock Movement Logging (FIFO)
**Location:** `app/services/transaction/stock_log_service.py`
- **IN movements**: Create a new `StockLogBatch` with `remaining_quantity = original_quantity` and `unit_cost = EPP`.
- **OUT movements**: Allocate the quantity across existing batches in chronological order (FIFO), reducing their `remaining_quantity`.
- **Audit**: Every `StockLog` entry contains `quantity_after` for point-in-time reconciliation.

#### 4. Pagination Pattern
# Repository
def get_all(self, start: int = 0, limit: int = 20, company_id: int = None):
    query = self.db.query(Model).filter(Model.is_deleted == False)
    if company_id:
        query = query.filter(Model.company_id == company_id)
    total = query.count()
    items = query.offset(start).limit(limit).all()
    return items, total
```

**Frontend:**
```typescript
const { data } = useQuery({
    queryKey: ['items', start, limit],
    queryFn: () => getItems(start, limit)
});
```

#### 5. Soft Delete Pattern

```python
# Never hard delete - always filter by is_deleted
def delete(self, id: int):
    item = self.db.query(Model).get(id)
    item.is_deleted = True
    self.db.commit()

# All queries must filter
query.filter(Model.is_deleted == False)
```

#### 6. Multi-Tenant Query Pattern

```python
# ALWAYS filter by company_id
def get_items(self, company_id: int):
    return self.db.query(Model).filter(
        Model.company_id == company_id,
        Model.is_deleted == False
    ).all()
```

### Frontend Development Patterns

#### 1. API Call Pattern

```typescript
// lib/api/exampleApi.ts
import { api } from '../api';
import { apiRequest } from '../queryClient';

export const getItems = (start?: number, limit?: number): Promise<ItemsResponse> => {
    const params = new URLSearchParams();
    if (start !== undefined) params.append("start", String(start));
    if (limit !== undefined) params.append("limit", String(limit));
    return apiRequest(api, `/items/?${params.toString()}`);
};

export const createItem = (data: InsertItem): Promise<Item> => 
    apiRequest(api, "/items/", { method: "POST", body: data });
```

#### 2. React Query Usage

```typescript
// List query
const { data, isLoading } = useQuery({
    queryKey: ['items', filters],
    queryFn: () => getItems(start, limit, filters)
});

// Mutation
const mutation = useMutation({
    mutationFn: createItem,
    onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: ['items'] });
        toast.success('Item created');
    }
});
```

#### 3. Form Pattern (React Hook Form + Zod)

```typescript
// Schema
const formSchema = z.object({
    name: z.string().min(1, "Required"),
    price: z.coerce.number().min(0)
});

// Form
const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: { name: "", price: 0 }
});

const onSubmit = (values: z.infer<typeof formSchema>) => {
    mutation.mutate(values);
};
```

#### 4. Protected Route Pattern

```typescript
// components/PrivateRoute.tsx
const PrivateRoute = () => {
    const { user, isLoading } = useUser();
    if (isLoading) return <Loading />;
    if (!user) return <Navigate to="/login" />;
    return <Outlet />;
};
```

#### 5. Error Boundary Pattern

**Location:** `src/components/RouteErrorBoundary.tsx`

```typescript
// Catches routing and rendering errors
const RouteErrorBoundary = () => {
    const error = useRouteError();
    return (
        <div className="error-container">
            <h2>Something went wrong</h2>
            <Button onClick={() => window.location.reload()}>Try Again</Button>
        </div>
    );
};
```
```

---

## 📍 Quick Reference - Where to Find What

### Backend Locations

| To Find... | Look In |
|------------|---------|
| Database table definition | `app/models/{domain}.py` |
| API endpoint | `app/api/{domain}/` + check `app/main.py` for router registration |
| Business logic | `app/services/{domain}/` |
| Database queries | `app/repositories/{domain}/` |
| Input/Output validation | `app/schemas/{domain}/` |
| DB connection & session | `app/core/database.py` |
| App configuration | `app/core/config.py` |
| JWT authentication | `app/core/security.py` |
| Event listeners (auto-update stock) | `app/subscribers/` |
| Database migrations | `alembic/versions/` |
| DSR logic | `app/api/dsr/`, `app/services/dsr/`, `app/schemas/dsr/` |
| SR logic | `app/api/sr/`, `app/services/sr/`, `app/schemas/sr/` |
| Reports logic | `app/services/reports.py`, `app/schemas/reports.py` |
| Consolidation logic | `app/services/consolidation_service.py` |
| Claim/Scheme logic | `app/services/claims/claim_service.py` |
| Stock Logging / FIFO | `app/services/transaction/stock_log_service.py` |

### Frontend Locations

| To Find... | Look In |
|------------|---------|
| Page component | `src/pages/{domain}/` |
| DSR pages | `src/pages/dsr/` |
| SR order pages | `src/pages/sr-orders/` |
| Report pages | `src/pages/reports/` |
| Reusable form | `src/components/forms/` |
| UI building blocks | `src/components/ui/` (shadcn/ui) |
| API functions | `src/lib/api/{domain}Api.ts` |
| DSR API | `src/lib/api/dsrApi.ts`, `dsrInventoryStockApi.ts`, `dsrSettlementApi.ts`, `dsrStorageApi.ts` |
| TypeScript types | `src/types/` or `src/lib/schema/` |
| React Context | `src/contexts/` |
| Custom hooks | `src/hooks/` |
| Route definitions | `src/App.tsx` |
| Global styles | `src/index.css` |
| API base config | `src/lib/api.ts` |
| Query client config | `src/lib/queryClient.ts` |
| Unified Delivery Form | `src/components/forms/UnifiedDeliveryForm.tsx` |
| Onboarding Cache | `src/components/auth/TestAccountOnboardingGate.tsx` |

### Common Search Patterns

| To Find... | Search For |
|------------|------------|
| All endpoints for a resource | `@router.get`, `@router.post` in `app/api/` |
| Where an API is called from FE | Function name in `src/lib/api/` |
| Database constraint | `UniqueConstraint`, `ForeignKey` in `app/models/` |
| Pydantic validation rules | Class name in `app/schemas/` |
| Route guard/protection | `PrivateRoute`, `AdminRoute`, `SRRoute`, `DSRRoute` in `src/components/` |

### Key Files to Know

| File | Importance |
|------|------------|
| `Shoudagor/app/main.py` | App entry, all routers registered here |
| `Shoudagor/app/models/__init__.py` | All model imports for Alembic |
| `Shoudagor/app/core/database.py` | DB engine, session factory |
| `Shoudagor/alembic/env.py` | Migration configuration |
| `shoudagor_FE/src/App.tsx` | All routes, providers, app structure |
| `shoudagor_FE/src/lib/api.ts` | Base API client with auth headers |
| `shoudagor_FE/src/contexts/UserContext.tsx` | User auth state |
| `Shoudagor/app/services/consolidation_service.py` | SR order consolidation logic |
| `Shoudagor/app/services/reports.py` | Reporting business logic |

---

## 🛡️ Important Conventions

### Naming Conventions

| Item | Convention | Example |
|------|------------|---------|
| Python files | snake_case | `sales_order.py` |
| Python classes | PascalCase | `SalesOrder` |
| Python functions | snake_case | `get_sales_orders()` |
| Database tables | snake_case | `sales_order` |
| TypeScript files | camelCase or PascalCase | `salesApi.ts`, `SaleForm.tsx` |
| React components | PascalCase | `<SalesOrderList />` |
| API endpoints | kebab-case | `/sales-order/` |

### Timezone

- All dates use **Asia/Dhaka (UTC+6)** timezone
- Configured in `app/core/config.py`

### Error Handling

- Backend: Raise `HTTPException` in API layer
- Frontend: Toasts via `sonner` and `react-hot-toast` for user feedback
- Global exception handlers in `app/main.py`

---

*This context document should be updated as the project evolves.*
