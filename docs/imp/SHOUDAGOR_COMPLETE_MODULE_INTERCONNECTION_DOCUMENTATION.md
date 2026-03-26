# Shoudagor ERP - Complete Module Interconnection Documentation

**Document Version:** 2.0  
**Date:** 2026-03-26  
**Purpose:** Comprehensive documentation of all modules and their interconnections in workflow

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [System Architecture Overview](#system-architecture-overview)
3. [Core Modules](#core-modules)
4. [Module Interconnection Map](#module-interconnection-map)
5. [Workflow Integration Patterns](#workflow-integration-patterns)
6. [Data Flow Diagrams](#data-flow-diagrams)
7. [Cross-Module Dependencies](#cross-module-dependencies)
8. [API Integration Points](#api-integration-points)

---

## Executive Summary

Shoudagor is a comprehensive ERP system built with:
- **Backend**: FastAPI + SQLAlchemy + PostgreSQL (Multi-schema)
- **Frontend**: React + TypeScript + Vite
- **Search**: Elasticsearch for real-time product/customer/supplier search
- **Architecture**: Clean 5-layer architecture with strict separation of concerns

### Module Count Summary

| Layer | Module Count | Description |
|-------|--------------|-------------|
| **Business Domains** | 8 | Core business modules |
| **API Endpoints** | 50+ | RESTful API endpoints |
| **Database Schemas** | 8 | Multi-schema PostgreSQL |
| **Frontend Pages** | 40+ | React pages and components |
| **Services** | 60+ | Business logic services |
| **Models** | 50+ | Database ORM models |

---

## System Architecture Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SHOUDAGOR ERP ARCHITECTURE                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                        FRONTEND LAYER                                │  │
│  │  React + TypeScript + Vite + TanStack Query + Shadcn UI             │  │
│  └────────────────────────────┬─────────────────────────────────────────┘  │
│                               │ REST API (JSON)                            │
│  ┌────────────────────────────▼─────────────────────────────────────────┐  │
│  │                         API LAYER                                    │  │
│  │  FastAPI Endpoints + JWT Auth + Dependency Injection                │  │
│  └────────────────────────────┬─────────────────────────────────────────┘  │
│                               │                                            │
│  ┌────────────────────────────▼─────────────────────────────────────────┐  │
│  │                      SERVICE LAYER                                   │  │
│  │  Business Logic + Transaction Management + Orchestration             │  │
│  └────────────────────────────┬─────────────────────────────────────────┘  │
│                               │                                            │
│  ┌────────────────────────────▼─────────────────────────────────────────┐  │
│  │                    REPOSITORY LAYER                                  │  │
│  │  Data Access + Query Optimization + Multi-Schema Operations          │  │
│  └────────────────────────────┬─────────────────────────────────────────┘  │
│                               │                                            │
│  ┌────────────────────────────▼─────────────────────────────────────────┐  │
│  │                       DATABASE LAYER                                 │  │
│  │  PostgreSQL (8 Schemas) + SQLAlchemy ORM + Alembic Migrations       │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                    ELASTICSEARCH LAYER                               │  │
│  │  Real-time Search + Auto-indexing + Faceted Search                   │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Core Modules

### 1. AUTHENTICATION & SECURITY MODULE

**Purpose**: User authentication, authorization, and multi-tenancy management

**Database Schema**: `security`

**Key Models**:
- `User` - User accounts with authentication
- `AppClientCompany` - Multi-tenant company management
- `UserCategory` - Role-based access control
- `AppClient` - API client management

**API Endpoints**:
- `POST /api/v1/security/login` - User authentication
- `POST /api/v1/security/refresh` - Token refresh
- `GET /api/v1/users/` - User management
- `POST /api/v1/users/` - Create user

**Services**:
- `SecurityService` - Authentication and JWT management
- `UserService` - User CRUD operations

**Frontend Components**:
- `Login.tsx` - Login page
- `UserForm.tsx` - User management form
- `PrivateRoute.tsx` - Route protection
- `AdminRoute.tsx` - Admin-only routes
- `SuperAdminRoute.tsx` - Super admin routes

**Interconnections**:
- Provides authentication for ALL modules
- Company context filtering for ALL data operations
- Role-based access control for ALL endpoints

---

### 2. INVENTORY MANAGEMENT MODULE

**Purpose**: Product catalog, variants, pricing, categories, and stock tracking

**Database Schema**: `inventory`

**Key Models**:
- `Product` - Product master data
- `ProductVariant` - Product variations (size, color, etc.)
- `ProductCategory` - Hierarchical product categories
- `ProductPrice` - Time-based pricing with effective dates
- `UnitOfMeasure` - Unit conversion management
- `Batch` - Batch tracking with FIFO/LIFO costing
- `InventoryMovement` - All inventory transactions log
- `ProductGroup` - Product grouping for bulk operations
- `VariantGroup` - Variant grouping

**API Endpoints**:
- `GET/POST /api/v1/inventory/product/` - Product CRUD
- `GET/POST /api/v1/inventory/product-variant/` - Variant CRUD
- `GET/POST /api/v1/inventory/product-price/` - Pricing management
- `GET/POST /api/v1/inventory/batch/` - Batch management
- `GET/POST /api/v1/inventory/product-category/` - Category management
- `GET/POST /api/v1/inventory/unit-of-measure/` - UOM management

**Services**:
- `ProductService` - Product business logic
- `ProductVariantService` - Variant management
- `ProductPriceService` - Pricing logic with UOM conversion
- `BatchAllocationService` - FIFO/LIFO batch allocation
- `InventorySyncService` - Batch-to-stock synchronization
- `ProductElasticsearchService` - Product search indexing
- `UOMUtilsService` - Unit conversion utilities

**Frontend Components**:
- `Products.tsx` - Product listing page
- `ProductForm.tsx` - Product creation/edit
- `ProductStats.tsx` - Product analytics
- `CategoryForm.tsx` - Category management
- `UnitForm.tsx` - UOM management
- `ProductPriceForm.tsx` - Pricing management

**Interconnections**:
- **→ Procurement**: Products used in Purchase Orders
- **→ Sales**: Products sold in Sales Orders
- **→ Warehouse**: Stock levels tracked per location
- **→ SR Module**: Products assigned to Sales Representatives
- **→ Claims**: Products used in promotional schemes
- **← Elasticsearch**: Real-time product search

---

### 3. PROCUREMENT MODULE

**Purpose**: Supplier management, purchase orders, receiving, and payments

**Database Schema**: `procurement`

**Key Models**:
- `Supplier` - Supplier master data with balance tracking
- `PurchaseOrder` - Purchase order header
- `PurchaseOrderDetail` - PO line items with UOM
- `ProductOrderDeliveryDetail` - Receiving records
- `ProductOrderPaymentDetail` - Payment records

**API Endpoints**:
- `GET/POST /api/v1/procurement/supplier/` - Supplier CRUD
- `GET/POST /api/v1/procurement/purchase-order/` - PO CRUD
- `POST /api/v1/procurement/purchase-order/{id}/cancel` - Cancel PO
- `POST /api/v1/procurement/purchase-order/{id}/return` - Process returns
- `POST /api/v1/procurement/product-order-delivery-detail/` - Record delivery
- `POST /api/v1/procurement/product-order-payment-detail/` - Record payment

**Services**:
- `PurchaseOrderService` - PO lifecycle management
- `SupplierService` - Supplier management
- `ProductOrderDeliveryDetailService` - Receiving logic
- `ProductOrderPaymentDetailService` - Payment processing
- `SupplierElasticsearchService` - Supplier search

**Frontend Components**:
- `Purchases.tsx` - PO listing page
- `PurchaseForm.tsx` - PO creation with Excel import
- `PurchaseDeliveryForm.tsx` - Receiving form
- `PurchasePaymentForm.tsx` - Payment recording
- `PurchaseReturnForm.tsx` - Return processing
- `ViewPurchaseDetails.tsx` - PO details view
- `SupplierForm.tsx` - Supplier management

**Interconnections**:
- **→ Inventory**: Creates batches on delivery
- **→ Warehouse**: Updates inventory stock on receiving
- **→ Claims**: Evaluates promotional schemes on PO
- **→ Billing**: Creates expense records
- **← Supplier Balance**: Tracks payables

**Workflow**:
```
1. Create PO → Validate supplier → Apply schemes → Increase supplier balance
2. Receive Items → Create batches → Update inventory stock → Log movements
3. Record Payment → Decrease supplier balance → Update payment status
4. Process Returns → Reduce stock → Adjust supplier balance
```

---

### 4. SALES MODULE

**Purpose**: Customer management, sales orders, deliveries, payments, and beat management

**Database Schema**: `sales`

**Key Models**:
- `Customer` - Customer master with credit limit and balance
- `Beat` - Geographic sales territories
- `SalesOrder` - Sales order header with consolidation support
- `SalesOrderDetail` - SO line items with SR details
- `SalesOrderDeliveryDetail` - Delivery records
- `SalesOrderPaymentDetail` - Payment records
- `SalesRepresentative` - SR master data with commission tracking
- `SR_Order` - SR orders for consolidation
- `SR_Order_Detail` - SR order line items
- `SR_Product_Assignment` - Product-SR assignments with pricing
- `Customer_SR_Assignment` - Customer-SR assignments
- `DeliverySalesRepresentative` - DSR master data
- `DSRSOAssignment` - DSR-SO assignments

**API Endpoints**:
- `GET/POST /api/v1/sales/customer/` - Customer CRUD
- `GET/POST /api/v1/sales/beat/` - Beat management
- `GET/POST /api/v1/sales/sales-order/` - SO CRUD
- `POST /api/v1/sales/sales-order/{id}/cancel` - Cancel SO
- `POST /api/v1/sales/sales-order/{id}/return` - Process returns
- `POST /api/v1/sales/sales-order/{id}/rejection` - Process rejections
- `POST /api/v1/sales-order-delivery-detail/` - Record delivery
- `POST /api/v1/sales-order-payment-detail/` - Record payment
- `GET/POST /api/v1/sr/sales-representative/` - SR management
- `GET/POST /api/v1/sr/sr-order/` - SR order management
- `POST /api/v1/consolidation/consolidate` - Consolidate SR orders
- `GET/POST /api/v1/dsr/delivery-sales-representative/` - DSR management
- `POST /api/v1/dsr/dsr-so-assignment/load` - Load SO to DSR

**Services**:
- `SalesOrderService` - SO lifecycle management
- `CustomerService` - Customer management
- `BeatService` - Beat management
- `SalesOrderDeliveryDetailService` - Delivery processing
- `SalesOrderPaymentDetailService` - Payment processing
- `SROrderService` - SR order management
- `ConsolidationService` - SR order consolidation
- `DSRSOAssignmentService` - DSR assignment and loading
- `CustomerElasticsearchService` - Customer search

**Frontend Components**:
- `Sales.tsx` - SO listing page
- `SaleForm.tsx` - SO creation
- `SalesDeliveryForm.tsx` - Delivery form
- `SalesPaymentForm.tsx` - Payment form
- `SalesReturnForm.tsx` - Return processing
- `ViewSaleDetails.tsx` - SO details
- `CustomerForm.tsx` - Customer management
- `Customers.tsx` - Customer listing
- `BeatForm.tsx` - Beat management
- `SROrders.tsx` - SR order listing
- `ConsolidatedSROrders.tsx` - Consolidated orders
- `DSRSOAssignments.tsx` - DSR assignments

**Interconnections**:
- **→ Inventory**: Validates stock availability
- **→ Warehouse**: Reduces inventory stock on delivery
- **→ Batch**: Allocates batches using FIFO/LIFO
- **→ Claims**: Applies promotional schemes
- **→ SR Module**: Consolidates SR orders into SO
- **→ DSR Module**: Loads SO to DSR storage
- **← Customer Balance**: Tracks receivables

**Workflow**:
```
DIRECT SALES ORDER:
1. Create SO → Validate stock → Apply schemes → Increase customer balance
2. Deliver Items → Allocate batches → Reduce stock → Update delivery status
3. Record Payment → Decrease customer balance → Update payment status

SR CONSOLIDATION FLOW:
1. SR creates orders → Admin approves
2. Consolidate SR orders → Create SO with SR details preserved
3. Calculate commission = (negotiated_price - sale_price) × shipped_qty
4. Deliver and pay → Disburse commission to SR

DSR ASSIGNMENT FLOW:
1. Assign SO to DSR → Load to DSR storage
2. Transfer stock: Warehouse → DSR storage
3. DSR delivers to customer → Collects payment
4. Admin settles with DSR → Payment reconciliation
```

---

### 5. WAREHOUSE MODULE

**Purpose**: Storage location management, stock tracking, and transfers

**Database Schema**: `warehouse`

**Key Models**:
- `Warehouse` - Warehouse master data
- `StorageLocation` - Storage locations within warehouses
- `InventoryStock` - Stock levels per product/variant/location
- `StockTransfer` - Stock transfer header
- `StockTransferDetails` - Transfer line items
- `DSRStorage` - Virtual storage for DSR
- `DSRInventoryStock` - Stock in DSR possession

**API Endpoints**:
- `GET/POST /api/v1/warehouse/warehouse/` - Warehouse CRUD
- `GET/POST /api/v1/warehouse/storage-location/` - Location CRUD
- `GET /api/v1/warehouse/inventory-stock/` - Stock inquiry
- `POST /api/v1/warehouse/stock-transfer/` - Create transfer
- `GET/POST /api/v1/warehouse/dsr-storage/` - DSR storage management
- `GET /api/v1/warehouse/dsr-inventory-stock/` - DSR stock inquiry

**Services**:
- `WarehouseService` - Warehouse management
- `StorageLocationService` - Location management
- `InventoryStockRepository` - Stock data access
- `StockTransferService` - Transfer processing
- `DSRStorageService` - DSR storage management

**Frontend Components**:
- `Warehouses.tsx` - Warehouse listing
- `WarehouseForm.tsx` - Warehouse management
- `Storages.tsx` - Storage location listing
- `StorageLocationForm.tsx` - Location management
- `Inventory.tsx` - Stock inquiry page
- `InventoryStockTransfer.tsx` - Transfer page
- `StockTransferForm.tsx` - Transfer form
- `DSRStorages.tsx` - DSR storage listing
- `DSRInventoryStock.tsx` - DSR stock inquiry

**Interconnections**:
- **← Procurement**: Receives stock from PO deliveries
- **← Sales**: Reduces stock on SO deliveries
- **← Transaction**: Stock adjustments
- **→ Batch**: Parallel tracking system
- **→ DSR**: Transfers stock to DSR storage

**Workflow**:
```
STOCK TRANSFER:
1. Create transfer → Select source location
2. Add items with target locations
3. Execute transfer → Reduce source → Increase target
4. Log inventory movements

DSR LOADING:
1. Validate SO items have stock in warehouse
2. Allocate batches (if enabled)
3. Transfer: Warehouse InventoryStock → DSR InventoryStock
4. Mark SO as loaded
```

---

### 6. TRANSACTION MODULE

**Purpose**: Inventory adjustments and operational records

**Database Schema**: `transaction`

**Key Models**:
- `InventoryAdjustment` - Adjustment header
- `AdjustmentDetail` - Adjustment line items
- `InventoryTransaction` - All inventory movement log

**API Endpoints**:
- `GET/POST /api/v1/transaction/inventory-adjustment/` - Adjustment CRUD
- `GET /api/v1/transaction/inventory-transaction/` - Transaction log

**Services**:
- `InventoryAdjustmentService` - Adjustment processing

**Frontend Components**:
- `StockAdjustmentForm.tsx` - Adjustment form
- `AdjustmentHistory.tsx` - Adjustment history

**Interconnections**:
- **→ Warehouse**: Updates inventory stock
- **→ Batch**: Creates adjustment batches
- **← All Modules**: Logs all inventory movements

---

### 7. BILLING MODULE

**Purpose**: Invoicing and expense management

**Database Schema**: `billing`

**Key Models**:
- `Invoice` - Invoice header
- `InvoiceDetail` - Invoice line items
- `Expense` - Expense records

**API Endpoints**:
- `GET/POST /api/v1/billing/invoice/` - Invoice CRUD
- `GET/POST /api/v1/billing/expense/` - Expense CRUD

**Services**:
- `InvoiceService` - Invoice management
- `ExpenseService` - Expense tracking

**Frontend Components**:
- `Invoices.tsx` - Invoice listing
- `ExpenseForm.tsx` - Expense management
- `Expenses.tsx` - Expense listing

**Interconnections**:
- **← Sales**: Links to sales orders
- **← Procurement**: Links to purchase orders

---

### 8. CLAIMS & SCHEMES MODULE

**Purpose**: Promotional schemes and discount management

**Database Schema**: `sales` (claims tables)

**Key Models**:
- `ClaimScheme` - Scheme definition (buy_x_get_y, rebate_flat, rebate_percentage)
- `ClaimSlab` - Tiered scheme slabs
- `ClaimLog` - Applied scheme tracking

**API Endpoints**:
- `GET/POST /api/v1/claims/scheme/` - Scheme CRUD
- `GET /api/v1/claims/report/` - Claim reports

**Services**:
- `ClaimService` - Scheme evaluation and application
- `ClaimReportService` - Reporting

**Frontend Components**:
- `SchemeForm.tsx` - Scheme creation
- `SchemeList.tsx` - Scheme listing
- `ClaimReports.tsx` - Claim analytics

**Interconnections**:
- **→ Procurement**: Evaluates schemes on PO creation
- **→ Sales**: Evaluates schemes on SO creation
- **→ Inventory**: Links trigger and free products

**Workflow**:
```
1. Define scheme → Set trigger product → Set free product/discount
2. Create slabs with thresholds
3. On PO/SO creation → Evaluate applicable schemes
4. Apply free quantities or discounts
5. Log in ClaimLog for tracking
```

---

## Module Interconnection Map

### Complete System Data Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SHOUDAGOR ERP - MODULE INTERCONNECTIONS                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│                        ┌──────────────────┐                                │
│                        │   SECURITY &     │                                │
│                        │ AUTHENTICATION   │                                │
│                        └────────┬─────────┘                                │
│                                 │ (Provides auth for ALL modules)          │
│                                 ▼                                           │
│         ┌───────────────────────────────────────────────────┐              │
│         │                                                   │              │
│    ┌────▼─────┐    ┌──────────┐    ┌──────────┐    ┌──────▼────┐         │
│    │INVENTORY │◄───┤ CLAIMS & │───►│  SALES   │◄───┤ WAREHOUSE │         │
│    │          │    │ SCHEMES  │    │          │    │           │         │
│    └────┬─────┘    └────┬─────┘    └────┬─────┘    └─────┬─────┘         │
│         │               │               │                │               │
│         │               │               │                │               │
│         ▼               ▼               ▼                ▼               │
│    ┌─────────────────────────────────────────────────────────┐            │
│    │                    BATCH SYSTEM                          │            │
│    │  (FIFO/LIFO Costing + Allocation + Movement Tracking)   │            │
│    └─────────────────────────────────────────────────────────┘            │
│         │               │               │                │               │
│         ▼               ▼               ▼                ▼               │
│    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐         │
│    │PROCURE-  │    │    SR    │    │   DSR    │    │TRANS-    │         │
│    │  MENT    │    │  MODULE  │    │  MODULE  │    │ ACTION   │         │
│    └────┬─────┘    └────┬─────┘    └────┬─────┘    └────┬─────┘         │
│         │               │               │                │               │
│         └───────────────┴───────────────┴────────────────┘               │
│                                 │                                           │
│                                 ▼                                           │
│                        ┌──────────────────┐                                │
│                        │    BILLING &     │                                │
│                        │    REPORTING     │                                │
│                        └──────────────────┘                                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Detailed Module Dependency Matrix

| Module | Depends On | Provides To | Data Flow |
|--------|-----------|-------------|-----------|
| **Security** | None | ALL | Authentication, Company Context |
| **Inventory** | Security | Procurement, Sales, Warehouse, SR, Claims | Product catalog, Pricing |
| **Procurement** | Security, Inventory, Warehouse, Claims | Batch, Billing | Stock IN, Supplier balance |
| **Sales** | Security, Inventory, Warehouse, Claims, SR, DSR | Batch, Billing | Stock OUT, Customer balance |
| **Warehouse** | Security, Inventory | Procurement, Sales, Transaction | Stock levels, Locations |
| **Batch** | Inventory, Warehouse | Procurement, Sales | FIFO/LIFO costing, Allocation |
| **Transaction** | Security, Inventory, Warehouse | Batch | Stock adjustments |
| **SR Module** | Security, Inventory, Sales | Sales (Consolidation) | SR orders, Commission |
| **DSR Module** | Security, Sales, Warehouse | Sales | Delivery, Payment collection |
| **Claims** | Security, Inventory | Procurement, Sales | Promotional schemes |
| **Billing** | Security, Sales, Procurement | Reporting | Invoices, Expenses |

---

## Workflow Integration Patterns

### 1. Purchase Order Complete Workflow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PURCHASE ORDER COMPLETE WORKFLOW                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  USER ACTION                    SYSTEM MODULES INVOLVED                     │
│  ───────────                    ──────────────────────                     │
│                                                                             │
│  1. Login                       ┌──────────────┐                           │
│     └──────────────────────────►│  SECURITY    │                           │
│                                 │  - Validate  │                           │
│                                 │  - Get company│                           │
│                                 └──────┬───────┘                           │
│                                        │                                    │
│  2. Create PO                          ▼                                    │
│     - Select Supplier          ┌──────────────┐                           │
│     - Add Products             │ PROCUREMENT  │                           │
│     - Enter Quantities         │  - Validate  │◄────┐                     │
│     └──────────────────────────►│  - Calculate │     │                     │
│                                 └──────┬───────┘     │                     │
│                                        │             │                     │
│                                        ▼             │                     │
│                                 ┌──────────────┐    │                     │
│                                 │  INVENTORY   │────┘                     │
│                                 │  - Products  │                           │
│                                 │  - Pricing   │                           │
│                                 │  - UOM       │                           │
│                                 └──────┬───────┘                           │
│                                        │                                    │
│                                        ▼                                    │
│                                 ┌──────────────┐                           │
│                                 │   CLAIMS     │                           │
│                                 │  - Evaluate  │                           │
│                                 │  - Apply     │                           │
│                                 └──────┬───────┘                           │
│                                        │                                    │
│                                        ▼                                    │
│                                 ┌──────────────┐                           │
│                                 │ PROCUREMENT  │                           │
│                                 │  - Create PO │                           │
│                                 │  - Update    │                           │
│                                 │    Supplier  │                           │
│                                 │    Balance ↑ │                           │
│                                 └──────────────┘                           │
│                                                                             │
│  3. Receive Items                                                           │
│     - Enter Delivered Qty      ┌──────────────┐                           │
│     - Enter Rejected Qty       │ PROCUREMENT  │                           │
│     └──────────────────────────►│  - Validate  │                           │
│                                 └──────┬───────┘                           │
│                                        │                                    │
│                                        ▼                                    │
│                                 ┌──────────────┐                           │
│                                 │   BATCH      │                           │
│                                 │  - Create    │                           │
│                                 │    batch     │                           │
│                                 │  - Set cost  │                           │
│                                 └──────┬───────┘                           │
│                                        │                                    │
│                                        ▼                                    │
│                                 ┌──────────────┐                           │
│                                 │  WAREHOUSE   │                           │
│                                 │  - Update    │                           │
│                                 │    stock ↑   │                           │
│                                 └──────┬───────┘                           │
│                                        │                                    │
│                                        ▼                                    │
│                                 ┌──────────────┐                           │
│                                 │ TRANSACTION  │                           │
│                                 │  - Log       │                           │
│                                 │    movement  │                           │
│                                 └──────────────┘                           │
│                                                                             │
│  4. Record Payment                                                          │
│     - Enter Amount             ┌──────────────┐                           │
│     └──────────────────────────►│ PROCUREMENT  │                           │
│                                 │  - Update    │                           │
│                                 │    Supplier  │                           │
│                                 │    Balance ↓ │                           │
│                                 │  - Update    │                           │
│                                 │    Payment   │                           │
│                                 │    Status    │                           │
│                                 └──────────────┘                           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2. Sales Order Complete Workflow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     SALES ORDER COMPLETE WORKFLOW                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  USER ACTION                    SYSTEM MODULES INVOLVED                     │
│  ───────────                    ──────────────────────                     │
│                                                                             │
│  1. Login                       ┌──────────────┐                           │
│     └──────────────────────────►│  SECURITY    │                           │
│                                 └──────┬───────┘                           │
│                                        │                                    │
│  2. Create SO                          ▼                                    │
│     - Select Customer          ┌──────────────┐                           │
│     - Add Products             │    SALES     │                           │
│     - Enter Quantities         │  - Validate  │◄────┐                     │
│     └──────────────────────────►│    stock    │     │                     │
│                                 └──────┬───────┘     │                     │
│                                        │             │                     │
│                                        ▼             │                     │
│                                 ┌──────────────┐    │                     │
│                                 │  WAREHOUSE   │────┘                     │
│                                 │  - Check     │                           │
│                                 │    stock     │                           │
│                                 └──────┬───────┘                           │
│                                        │                                    │
│                                        ▼                                    │
│                                 ┌──────────────┐                           │
│                                 │  INVENTORY   │                           │
│                                 │  - Products  │                           │
│                                 │  - Pricing   │                           │
│                                 └──────┬───────┘                           │
│                                        │                                    │
│                                        ▼                                    │
│                                 ┌──────────────┐                           │
│                                 │   CLAIMS     │                           │
│                                 │  - Evaluate  │                           │
│                                 │  - Apply     │                           │
│                                 └──────┬───────┘                           │
│                                        │                                    │
│                                        ▼                                    │
│                                 ┌──────────────┐                           │
│                                 │    SALES     │                           │
│                                 │  - Create SO │                           │
│                                 │  - Update    │                           │
│                                 │    Customer  │                           │
│                                 │    Balance ↑ │                           │
│                                 └──────────────┘                           │
│                                                                             │
│  3. Deliver Items                                                           │
│     - Enter Delivered Qty      ┌──────────────┐                           │
│     └──────────────────────────►│    SALES     │                           │
│                                 │  - Validate  │                           │
│                                 └──────┬───────┘                           │
│                                        │                                    │
│                                        ▼                                    │
│                                 ┌──────────────┐                           │
│                                 │   BATCH      │                           │
│                                 │  - Allocate  │                           │
│                                 │    FIFO/LIFO │                           │
│                                 │  - Reduce    │                           │
│                                 │    qty_on_   │                           │
│                                 │    hand      │                           │
│                                 └──────┬───────┘                           │
│                                        │                                    │
│                                        ▼                                    │
│                                 ┌──────────────┐                           │
│                                 │  WAREHOUSE   │                           │
│                                 │  - Reduce    │                           │
│                                 │    stock ↓   │                           │
│                                 └──────┬───────┘                           │
│                                        │                                    │
│                                        ▼                                    │
│                                 ┌──────────────┐                           │
│                                 │ TRANSACTION  │                           │
│                                 │  - Log       │                           │
│                                 │    movement  │                           │
│                                 └──────────────┘                           │
│                                                                             │
│  4. Record Payment                                                          │
│     - Enter Amount             ┌──────────────┐                           │
│     └──────────────────────────►│    SALES     │                           │
│                                 │  - Update    │                           │
│                                 │    Customer  │                           │
│                                 │    Balance ↓ │                           │
│                                 │  - Update    │                           │
│                                 │    Payment   │                           │
│                                 │    Status    │                           │
│                                 └──────────────┘                           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3. SR Order Consolidation Workflow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                  SR ORDER CONSOLIDATION WORKFLOW                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ACTOR                         SYSTEM MODULES INVOLVED                      │
│  ─────                         ──────────────────────                      │
│                                                                             │
│  SR (Sales Rep)                                                             │
│  ───────────────                                                            │
│  1. Login                      ┌──────────────┐                           │
│     └──────────────────────────►│  SECURITY    │                           │
│                                 │  - SR Role   │                           │
│                                 └──────┬───────┘                           │
│                                        │                                    │
│  2. Create SR Order                    ▼                                    │
│     - Select Customer          ┌──────────────┐                           │
│       (from assigned)          │  SR MODULE   │                           │
│     - Add Products             │  - Validate  │◄────┐                     │
│       (from assigned)          │    customer  │     │                     │
│     - Negotiate Price          │    assignment│     │                     │
│     └──────────────────────────►│  - Validate  │     │                     │
│                                 │    product   │     │                     │
│                                 │    assignment│     │                     │
│                                 └──────┬───────┘     │                     │
│                                        │             │                     │
│                                        ▼             │                     │
│                                 ┌──────────────┐    │                     │
│                                 │  INVENTORY   │────┘                     │
│                                 │  - Get       │                           │
│                                 │    assigned  │                           │
│                                 │    price     │                           │
│                                 └──────┬───────┘                           │
│                                        │                                    │
│                                        ▼                                    │
│                                 ┌──────────────┐                           │
│                                 │  SR MODULE   │                           │
│                                 │  - Create    │                           │
│                                 │    SR_Order  │                           │
│                                 │  - Status:   │                           │
│                                 │    pending   │                           │
│                                 └──────────────┘                           │
│                                                                             │
│  ADMIN                                                                      │
│  ─────                                                                      │
│  3. Approve SR Orders          ┌──────────────┐                           │
│     └──────────────────────────►│  SR MODULE   │                           │
│                                 │  - Update    │                           │
│                                 │    status:   │                           │
│                                 │    approved  │                           │
│                                 └──────────────┘                           │
│                                                                             │
│  4. Consolidate Orders                                                      │
│     - Select multiple          ┌──────────────┐                           │
│       SR orders                │CONSOLIDATION │                           │
│     - Same customer            │   SERVICE    │                           │
│     └──────────────────────────►│  - Validate  │                           │
│                                 │    same      │                           │
│                                 │    customer  │                           │
│                                 │  - Validate  │                           │
│                                 │    all       │                           │
│                                 │    approved  │                           │
│                                 └──────┬───────┘                           │
│                                        │                                    │
│                                        ▼                                    │
│                                 ┌──────────────┐                           │
│                                 │  WAREHOUSE   │                           │
│                                 │  - Validate  │                           │
│                                 │    stock     │                           │
│                                 │    available │                           │
│                                 └──────┬───────┘                           │
│                                        │                                    │
│                                        ▼                                    │
│                                 ┌──────────────┐                           │
│                                 │    SALES     │                           │
│                                 │  - Create SO │                           │
│                                 │  - Each SR   │                           │
│                                 │    detail →  │                           │
│                                 │    separate  │                           │
│                                 │    SO line   │                           │
│                                 │  - Preserve  │                           │
│                                 │    SR details│                           │
│                                 │    in JSON   │                           │
│                                 └──────┬───────┘                           │
│                                        │                                    │
│                                        ▼                                    │
│                                 ┌──────────────┐                           │
│                                 │  SR MODULE   │                           │
│                                 │  - Update    │                           │
│                                 │    SR orders │                           │
│                                 │    status:   │                           │
│                                 │    consoli-  │                           │
│                                 │    dated     │                           │
│                                 └──────────────┘                           │
│                                                                             │
│  5. Deliver & Pay              ┌──────────────┐                           │
│     (Same as regular SO)       │    SALES     │                           │
│     └──────────────────────────►│  - Deliver   │                           │
│                                 │  - Pay       │                           │
│                                 └──────┬───────┘                           │
│                                        │                                    │
│                                        ▼                                    │
│                                 ┌──────────────┐                           │
│                                 │  SR MODULE   │                           │
│                                 │  - Calculate │                           │
│                                 │    commission│                           │
│                                 │  = (nego_    │                           │
│                                 │    price -   │                           │
│                                 │    sale_     │                           │
│                                 │    price) ×  │                           │
│                                 │    shipped_  │                           │
│                                 │    qty       │                           │
│                                 └──────┬───────┘                           │
│                                        │                                    │
│  6. Disburse Commission                ▼                                    │
│     └──────────────────────────►┌──────────────┐                           │
│                                 │  SR MODULE   │                           │
│                                 │  - Create    │                           │
│                                 │    disburse- │                           │
│                                 │    ment      │                           │
│                                 │  - Update SR │                           │
│                                 │    commission│                           │
│                                 │    balance   │                           │
│                                 └──────────────┘                           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4. DSR Assignment and Loading Workflow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                  DSR ASSIGNMENT AND LOADING WORKFLOW                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ADMIN ACTION                  SYSTEM MODULES INVOLVED                      │
│  ────────────                  ──────────────────────                      │
│                                                                             │
│  1. Assign SO to DSR           ┌──────────────┐                           │
│     - Select SO                │  DSR MODULE  │                           │
│     - Select DSR               │  - Create    │                           │
│     └──────────────────────────►│    DSR SO    │                           │
│                                 │    Assignment│                           │
│                                 │  - Status:   │                           │
│                                 │    assigned  │                           │
│                                 └──────────────┘                           │
│                                                                             │
│  2. Load SO to DSR Storage                                                  │
│     (All-or-Nothing)           ┌──────────────┐                           │
│     └──────────────────────────►│  DSR MODULE  │                           │
│                                 │  - Validate  │                           │
│                                 │    ALL items │                           │
│                                 └──────┬───────┘                           │
│                                        │                                    │
│                                        ▼                                    │
│                                 ┌──────────────┐                           │
│                                 │  WAREHOUSE   │                           │
│                                 │  - Check     │                           │
│                                 │    stock for │                           │
│                                 │    ALL items │                           │
│                                 └──────┬───────┘                           │
│                                        │                                    │
│                                        ▼                                    │
│                                 ┌──────────────┐                           │
│                                 │   BATCH      │                           │
│                                 │  - Allocate  │                           │
│                                 │    batches   │                           │
│                                 │    (if       │                           │
│                                 │    enabled)  │                           │
│                                 └──────┬───────┘                           │
│                                        │                                    │
│                                        ▼                                    │
│                                 ┌──────────────┐                           │
│                                 │  WAREHOUSE   │                           │
│                                 │  - Reduce    │                           │
│                                 │    Inventory │                           │
│                                 │    Stock ↓   │                           │
│                                 └──────┬───────┘                           │
│                                        │                                    │
│                                        ▼                                    │
│                                 ┌──────────────┐                           │
│                                 │  DSR MODULE  │                           │
│                                 │  - Increase  │                           │
│                                 │    DSR       │                           │
│                                 │    Inventory │                           │
│                                 │    Stock ↑   │                           │
│                                 └──────┬───────┘                           │
│                                        │                                    │
│                                        ▼                                    │
│                                 ┌──────────────┐                           │
│                                 │    SALES     │                           │
│                                 │  - Mark SO   │                           │
│                                 │    is_loaded │                           │
│                                 │    = True    │                           │
│                                 │  - Set       │                           │
│                                 │    loaded_by │                           │
│                                 │    _dsr_id   │                           │
│                                 └──────────────┘                           │
│                                                                             │
│  DSR (Delivery Rep)                                                         │
│  ───────────────                                                            │
│  3. Deliver to Customer        ┌──────────────┐                           │
│     └──────────────────────────►│    SALES     │                           │
│                                 │  - Create    │                           │
│                                 │    delivery  │                           │
│                                 │    detail    │                           │
│                                 └──────┬───────┘                           │
│                                        │                                    │
│                                        ▼                                    │
│                                 ┌──────────────┐                           │
│                                 │  DSR MODULE  │                           │
│                                 │  - Reduce    │                           │
│                                 │    DSR       │                           │
│                                 │    Inventory │                           │
│                                 │    Stock ↓   │                           │
│                                 └──────────────┘                           │
│                                                                             │
│  4. Collect Payment            ┌──────────────┐                           │
│     └──────────────────────────►│    SALES     │                           │
│                                 │  - Create    │                           │
│                                 │    payment   │                           │
│                                 │    detail    │                           │
│                                 └──────┬───────┘                           │
│                                        │                                    │
│                                        ▼                                    │
│                                 ┌──────────────┐                           │
│                                 │  DSR MODULE  │                           │
│                                 │  - Increase  │                           │
│                                 │    DSR       │                           │
│                                 │    payment_  │                           │
│                                 │    on_hand ↑ │                           │
│                                 └──────────────┘                           │
│                                                                             │
│  ADMIN                                                                      │
│  ─────                                                                      │
│  5. Settle with DSR            ┌──────────────┐                           │
│     - Collect payment          │  DSR MODULE  │                           │
│       from DSR                 │  - Create    │                           │
│     └──────────────────────────►│    DSR       │                           │
│                                 │    Payment   │                           │
│                                 │    Settlement│                           │
│                                 │  - Decrease  │                           │
│                                 │    DSR       │                           │
│                                 │    payment_  │                           │
│                                 │    on_hand ↓ │                           │
│                                 └──────────────┘                           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Cross-Module Dependencies

### Database Schema Relationships

```sql
-- Cross-schema foreign key relationships

-- Security → All Modules
security.app_client_company.company_id
  ← inventory.product.company_id
  ← sales.customer.company_id
  ← procurement.supplier.company_id
  ← warehouse.storage_location.company_id

-- Inventory → Multiple Modules
inventory.product.product_id
  ← procurement.purchase_order_detail.product_id
  ← sales.sales_order_detail.product_id
  ← warehouse.inventory_stock.product_id
  ← inventory.batch.product_id

inventory.product_variant.variant_id
  ← procurement.purchase_order_detail.variant_id
  ← sales.sales_order_detail.variant_id
  ← warehouse.inventory_stock.variant_id
  ← inventory.batch.variant_id

-- Warehouse → Sales & Procurement
warehouse.storage_location.location_id
  ← procurement.purchase_order.location_id
  ← sales.sales_order.location_id
  ← warehouse.inventory_stock.location_id

-- Sales → DSR Module
sales.sales_order.sales_order_id
  ← sales.dsr_so_assignment.sales_order_id

sales.delivery_sales_representative.dsr_id
  ← sales.sales_order.loaded_by_dsr_id
  ← sales.dsr_so_assignment.dsr_id

-- Sales → SR Module
sales.customer.customer_id
  ← sales.sr_order.customer_id
  ← sales.customer_sr_assignment.customer_id

sales.sales_representative.sr_id
  ← sales.sr_order.sr_id
  ← sales.sr_product_assignment.sr_id
```

### Service Layer Dependencies

```python
# Service dependency injection patterns

class SalesOrderService:
    def __init__(self, db: Session, company_id: int):
        self.db = db
        self.company_id = company_id
        # Dependencies on other services
        self.inventory_stock_repo = InventoryStockRepository(db)
        self.batch_service = BatchAllocationService(db, company_id)
        self.claim_service = ClaimService(db, company_id)
        self.customer_repo = CustomerRepository(db)

class PurchaseOrderService:
    def __init__(self, db: Session, company_id: int):
        self.db = db
        self.company_id = company_id
        # Dependencies on other services
        self.batch_service = BatchService(db, company_id)
        self.inventory_stock_repo = InventoryStockRepository(db)
        self.claim_service = ClaimService(db, company_id)
        self.supplier_repo = SupplierRepository(db)

class ConsolidationService:
    def __init__(self, db: Session, company_id: int):
        self.db = db
        self.company_id = company_id
        # Cross-module dependencies
        self.sr_order_repo = SROrderRepository(db)
        self.sales_order_service = SalesOrderService(db, company_id)
        self.inventory_stock_repo = InventoryStockRepository(db)
        self.customer_repo = CustomerRepository(db)
```

---

## API Integration Points

### Authentication Flow

```
1. Client → POST /api/v1/security/login
   Request: { username, password, company_id }
   Response: { access_token, refresh_token, user_info }

2. Client stores tokens

3. All subsequent requests include:
   Header: Authorization: Bearer <access_token>

4. Backend extracts:
   - user_id from token
   - company_id from token
   - Applies company context to all queries
```

### Typical API Call Flow

```
┌──────────┐
│  CLIENT  │
└────┬─────┘
     │
     │ 1. HTTP Request with JWT
     ▼
┌─────────────────────┐
│   API ENDPOINT      │
│  (FastAPI Router)   │
└────┬────────────────┘
     │
     │ 2. Dependency Injection
     ▼
┌─────────────────────┐
│  get_current_user   │
│  get_company_id     │
│  get_db             │
└────┬────────────────┘
     │
     │ 3. Call Service
     ▼
┌─────────────────────┐
│   SERVICE LAYER     │
│  (Business Logic)   │
└────┬────────────────┘
     │
     │ 4. Call Repository
     ▼
┌─────────────────────┐
│  REPOSITORY LAYER   │
│  (Data Access)      │
└────┬────────────────┘
     │
     │ 5. Query Database
     ▼
┌─────────────────────┐
│   DATABASE          │
│  (PostgreSQL)       │
└────┬────────────────┘
     │
     │ 6. Return Data
     ▼
┌──────────┐
│  CLIENT  │
└──────────┘
```

### Frontend-Backend Integration

```typescript
// Frontend API call pattern using TanStack Query

// 1. API function (lib/api/salesApi.ts)
export const createSalesOrder = async (data: SalesOrderCreate) => {
  const response = await api.post('/api/v1/sales/sales-order/', data);
  return response.data;
};

// 2. React Query hook (pages/sales/Sales.tsx)
const createMutation = useMutation({
  mutationFn: createSalesOrder,
  onSuccess: () => {
    queryClient.invalidateQueries(['sales-orders']);
    toast.success('Sales order created successfully');
  },
  onError: (error) => {
    toast.error(error.message);
  }
});

// 3. Form submission
const handleSubmit = (formData) => {
  createMutation.mutate(formData);
};
```

### Elasticsearch Integration

```python
# Automatic indexing on CRUD operations

# 1. Product created/updated
@product_router.post("/")
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    # Create in database
    db_product = product_service.create_product(product)
    
    # Auto-index in Elasticsearch
    product_es_service.index_product(db_product)
    
    return db_product

# 2. Frontend search
GET /api/v1/inventory/product/?search_query=laptop
  → Searches Elasticsearch index
  → Returns matching products with facets

# 3. Reindexing (admin operation)
POST /api/v1/admin/reindex/products
  → Rebuilds entire Elasticsearch index from database
```

---

## Data Flow Diagrams

### Complete Purchase-to-Sale Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    COMPLETE PURCHASE-TO-SALE DATA FLOW                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  SUPPLIER                                                                   │
│     │                                                                        │
│     │ 1. Purchase Order                                                     │
│     ▼                                                                        │
│  ┌──────────────┐                                                           │
│  │ PROCUREMENT  │                                                           │
│  │   MODULE     │                                                           │
│  └──────┬───────┘                                                           │
│         │                                                                    │
│         │ 2. Receive Items                                                  │
│         ▼                                                                    │
│  ┌──────────────┐         ┌──────────────┐                                 │
│  │   BATCH      │◄────────┤  WAREHOUSE   │                                 │
│  │   SYSTEM     │         │  Inventory   │                                 │
│  │              │         │  Stock       │                                 │
│  │ - Create     │         │              │                                 │
│  │   batch      │         │ - Update     │                                 │
│  │ - Set cost   │         │   quantity ↑ │                                 │
│  │ - FIFO queue │         │              │                                 │
│  └──────┬───────┘         └──────────────┘                                 │
│         │                                                                    │
│         │ 3. Stock Available                                                │
│         ▼                                                                    │
│  ┌──────────────┐                                                           │
│  │    SALES     │                                                           │
│  │   MODULE     │                                                           │
│  └──────┬───────┘                                                           │
│         │                                                                    │
│         │ 4. Create Sales Order                                             │
│         │    - Validate stock                                               │
│         │    - Apply schemes                                                │
│         ▼                                                                    │
│  ┌──────────────┐                                                           │
│  │   CLAIMS     │                                                           │
│  │   MODULE     │                                                           │
│  │ - Evaluate   │                                                           │
│  │ - Apply free │                                                           │
│  │   qty/disc   │                                                           │
│  └──────┬───────┘                                                           │
│         │                                                                    │
│         │ 5. Deliver Items                                                  │
│         ▼                                                                    │
│  ┌──────────────┐         ┌──────────────┐                                 │
│  │   BATCH      │────────►│  WAREHOUSE   │                                 │
│  │   SYSTEM     │         │  Inventory   │                                 │
│  │              │         │  Stock       │                                 │
│  │ - Allocate   │         │              │                                 │
│  │   FIFO       │         │ - Reduce     │                                 │
│  │ - Reduce     │         │   quantity ↓ │                                 │
│  │   qty_on_    │         │              │                                 │
│  │   hand       │         │              │                                 │
│  └──────┬───────┘         └──────────────┘                                 │
│         │                                                                    │
│         │ 6. Calculate COGS                                                 │
│         │    (from batch cost)                                              │
│         ▼                                                                    │
│  ┌──────────────┐                                                           │
│  │   BILLING    │                                                           │
│  │   MODULE     │                                                           │
│  │ - Invoice    │                                                           │
│  │ - COGS       │                                                           │
│  └──────┬───────┘                                                           │
│         │                                                                    │
│         │ 7. Payment                                                        │
│         ▼                                                                    │
│  CUSTOMER                                                                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Batch System Integration

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      BATCH SYSTEM INTEGRATION                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  PROCUREMENT DELIVERY                                                       │
│         │                                                                    │
│         │ 1. Receive Items                                                  │
│         ▼                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐          │
│  │                    BATCH CREATION                            │          │
│  │                                                              │          │
│  │  - product_id, variant_id                                   │          │
│  │  - location_id                                              │          │
│  │  - qty_received                                             │          │
│  │  - qty_on_hand = qty_received                               │          │
│  │  - unit_cost (from PO)                                      │          │
│  │  - source_type = "purchase"                                 │          │
│  │  - source_id = purchase_order_detail_id                     │          │
│  │  - batch_number (auto-generated)                            │          │
│  │  - expiry_date (if applicable)                              │          │
│  │                                                              │          │
│  └──────────────────────────┬───────────────────────────────────┘          │
│                             │                                               │
│                             │ 2. Batch Created                              │
│                             ▼                                               │
│  ┌──────────────────────────────────────────────────────────────┐          │
│  │                 INVENTORY MOVEMENT LOG                       │          │
│  │                                                              │          │
│  │  - movement_type = "IN"                                      │          │
│  │  - quantity = qty_received                                   │          │
│  │  - unit_cost_at_txn = unit_cost                             │          │
│  │  - batch_id                                                  │          │
│  │  - reference_type = "purchase_order"                         │          │
│  │  - reference_id = purchase_order_id                          │          │
│  │                                                              │          │
│  └──────────────────────────────────────────────────────────────┘          │
│                                                                             │
│  SALES ORDER DELIVERY                                                       │
│         │                                                                    │
│         │ 3. Deliver Items                                                  │
│         ▼                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐          │
│  │                  BATCH ALLOCATION (FIFO)                     │          │
│  │                                                              │          │
│  │  SELECT * FROM batch                                         │          │
│  │  WHERE product_id = ? AND variant_id = ?                     │          │
│  │    AND location_id = ?                                       │          │
│  │    AND qty_on_hand > 0                                       │          │
│  │    AND status = 'active'                                     │          │
│  │  ORDER BY created_date ASC  -- FIFO                          │          │
│  │  FOR UPDATE SKIP LOCKED     -- Concurrency                   │          │
│  │                                                              │          │
│  │  For each batch:                                             │          │
│  │    - Allocate qty from batch                                 │          │
│  │    - Create SalesOrderBatchAllocation                        │          │
│  │    - Reduce batch.qty_on_hand                                │          │
│  │    - Calculate COGS = allocated_qty × batch.unit_cost        │          │
│  │                                                              │          │
│  └──────────────────────────┬───────────────────────────────────┘          │
│                             │                                               │
│                             │ 4. Allocation Complete                        │
│                             ▼                                               │
│  ┌──────────────────────────────────────────────────────────────┐          │
│  │                 INVENTORY MOVEMENT LOG                       │          │
│  │                                                              │          │
│  │  - movement_type = "OUT"                                     │          │
│  │  - quantity = allocated_qty                                  │          │
│  │  - unit_cost_at_txn = batch.unit_cost                       │          │
│  │  - batch_id                                                  │          │
│  │  - reference_type = "sales_order"                            │          │
│  │  - reference_id = sales_order_id                             │          │
│  │                                                              │          │
│  └──────────────────────────────────────────────────────────────┘          │
│                                                                             │
│  RETURNS                                                                    │
│         │                                                                    │
│         │ 5. Return Items                                                   │
│         ▼                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐          │
│  │                    BATCH RETURN                              │          │
│  │                                                              │          │
│  │  If original batch exists:                                   │          │
│  │    - Increase batch.qty_on_hand                              │          │
│  │    - Update SalesOrderBatchAllocation                        │          │
│  │                                                              │          │
│  │  If original batch depleted/deleted:                         │          │
│  │    - Create synthetic batch                                  │          │
│  │    - source_type = "return"                                  │          │
│  │    - is_synthetic = True                                     │          │
│  │    - Use original batch cost                                 │          │
│  │                                                              │          │
│  └──────────────────────────────────────────────────────────────┘          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Summary of Module Interconnections

### Module Interaction Summary Table

| From Module | To Module | Interaction Type | Data Exchanged |
|-------------|-----------|------------------|----------------|
| Security | ALL | Authentication | user_id, company_id, permissions |
| Inventory | Procurement | Product Data | product_id, variant_id, pricing |
| Inventory | Sales | Product Data | product_id, variant_id, pricing |
| Inventory | Warehouse | Stock Reference | product_id, variant_id |
| Inventory | Batch | Product Reference | product_id, variant_id |
| Procurement | Inventory | Batch Creation | qty, cost, batch_number |
| Procurement | Warehouse | Stock Update | qty increase |
| Procurement | Claims | Scheme Evaluation | free_qty, discounts |
| Sales | Inventory | Stock Validation | availability check |
| Sales | Warehouse | Stock Reduction | qty decrease |
| Sales | Batch | Allocation | FIFO/LIFO allocation |
| Sales | Claims | Scheme Evaluation | free_qty, discounts |
| Sales | SR Module | Consolidation | SR orders → SO |
| Sales | DSR Module | Assignment | SO → DSR |
| Warehouse | Batch | Parallel Tracking | stock levels |
| Warehouse | Transaction | Adjustments | qty changes |
| SR Module | Sales | Order Creation | consolidated SO |
| SR Module | Inventory | Product Assignment | assigned products |
| DSR Module | Warehouse | Stock Transfer | warehouse → DSR |
| DSR Module | Sales | Delivery | DSR → customer |
| Batch | Transaction | Movement Logging | all movements |
| Claims | Procurement | Scheme Application | PO schemes |
| Claims | Sales | Scheme Application | SO schemes |

---

## Conclusion

The Shoudagor ERP system is a sophisticated, well-architected application with clear separation of concerns across 8 major business domains. The module interconnections follow consistent patterns:

1. **Authentication Layer** - Security module provides authentication and company context to all modules
2. **Inventory Core** - Inventory module serves as the central product catalog for all operations
3. **Procurement Flow** - Brings stock IN through batch creation and warehouse updates
4. **Sales Flow** - Moves stock OUT through batch allocation and warehouse reduction
5. **Batch System** - Provides FIFO/LIFO costing and traceability across procurement and sales
6. **SR/DSR Extensions** - Extend sales functionality with field sales and delivery management
7. **Claims Integration** - Cross-cuts procurement and sales for promotional schemes
8. **Transaction Logging** - Captures all inventory movements for audit and reporting

The system demonstrates mature software engineering practices including:
- Clean architecture with 5 distinct layers
- Multi-tenancy with company-based isolation
- Comprehensive audit trails
- Soft delete patterns
- Optimistic locking for concurrency
- Real-time search with Elasticsearch
- Type-safe frontend with TypeScript
- Reactive state management with TanStack Query

---

*End of Documentation*
