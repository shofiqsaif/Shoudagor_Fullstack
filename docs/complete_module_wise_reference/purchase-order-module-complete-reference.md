# Purchase Order (Procurement) Module — Complete Operations & UI Walkthrough

> **Generated:** 2026-04-16  
> **Scope:** Full-stack analysis of the Purchase Order Module in Shoudagor ERP  
> **Coverage:** Backend API, Frontend UI, Interconnected Workflows, Special Features

---

## Table of Contents

1. [Module Architecture Overview](#1-module-architecture-overview)
2. [Entity Inventory](#2-entity-inventory)
3. [Backend Operations Reference](#3-backend-operations-reference)
4. [Frontend UI Walkthrough](#4-frontend-ui-walkthrough)
5. [Interconnected Workflows](#5-interconnected-workflows)
6. [Special Features Deep-Dive](#6-special-features-deep-dive)
7. [API Quick Reference](#7-api-quick-reference)
8. [File Map](#8-file-map)
9. [Appendix: Operation Counts](#9-appendix-operation-counts)

---

## 1. Module Architecture Overview

### 1.1 Layer Structure

```
┌─────────────────────────────────────────────────────────────────┐
│                    Frontend (React + TypeScript)                │
│  Pages → Forms/Modals → Shared Components → API Layer → Types  │
├─────────────────────────────────────────────────────────────────┤
│                    Backend (FastAPI + Python)                   │
│  API Routes → Services → Repositories → Models → Schemas       │
├─────────────────────────────────────────────────────────────────┤
│                    Database (PostgreSQL)                        │
│  procurement schema: purchase_order, purchase_order_detail,     │
│  supplier, product_order_delivery_detail,                       │
│  product_order_payment_detail                                   │
├─────────────────────────────────────────────────────────────────┤
│                    External Services                            │
│  Claims/Schemes Engine, Inventory Stock, Batch Tracking        │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Entity Relationships

```
Supplier (1:N)
    │
    └── PurchaseOrder (1:N)
            │
            ├── PurchaseOrderDetail (1:N)
            │       │
            │       ├── Product (N:1)
            │       ├── ProductVariant (N:1)
            │       ├── UnitOfMeasure (N:1)
            │       ├── Batch (1:N, back_populates)
            │       └── ProductOrderDeliveryDetail (1:N)
            │
            └── ProductOrderPaymentDetail (1:N)

StorageLocation (1:N) ←── PurchaseOrder.location_id
AppClientCompany (1:N) ←── PurchaseOrder.company_id
User (1:N) ←── PurchaseOrder.cb/mb (created_by/modified_by)

ClaimScheme (N:M via evaluation) → PurchaseOrderDetail
  - applied_scheme_id (FK to claims scheme)
  - free_quantity, discount_amount (calculated benefits)
```

### 1.3 Technology Stack

| Layer | Technology |
|-------|------------|
| **Backend Framework** | FastAPI (Python) |
| **ORM** | SQLAlchemy 2.0+ |
| **Validation** | Pydantic |
| **Database** | PostgreSQL (multi-schema: `procurement`) |
| **Claims Engine** | Internal service (`ClaimService.evaluate_pre_claim`) |
| **Inventory Integration** | Batch tracking, Stock updates |
| **Frontend Framework** | React 19 + TypeScript 5.8 |
| **State Management** | TanStack Query v5 |
| **Forms** | React Hook Form + Zod |
| **UI Components** | shadcn/ui (Radix-based) |
| **Tables** | TanStack Table |
| **Charts** | Recharts |

---

## 2. Entity Inventory

### 2.1 PurchaseOrder

**Table:** `procurement.purchase_order`

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `purchase_order_id` | Integer | PK, index | Primary key |
| `order_number` | String(50) | NOT NULL | Unique PO number (auto: PO-YYYYMMDD-SEQ) |
| `supplier_id` | Integer | FK → supplier, NOT NULL | Supplier reference |
| `order_date` | TIMESTAMP | NOT NULL | Date order placed |
| `expected_delivery_date` | TIMESTAMP | nullable | Expected delivery date |
| `status` | String(20) | NOT NULL, default "Open" | Open/Partial/Completed/Cancelled |
| `total_amount` | Numeric(18,2) | NOT NULL | Total PO amount |
| `amount_paid` | Numeric(18,2) | NOT NULL, default 0 | Amount already paid |
| `payment_status` | String(20) | NOT NULL, default "Pending" | Pending/Partial/Completed |
| `delivery_status` | String(20) | NOT NULL, default "Pending" | Pending/Partial/Completed |
| `location_id` | Integer | FK → storage_location | Delivery location |
| `company_id` | Integer | FK → app_client_company | Multi-tenant company |
| `cb` | Integer | NOT NULL | Created by user |
| `cd` | DateTime | NOT NULL, default now | Created date |
| `mb` | Integer | NOT NULL | Modified by user |
| `md` | DateTime | NOT NULL, default now | Modified date |
| `is_deleted` | Boolean | NOT NULL, default False | Soft delete flag |

**Relationships:**
- `supplier` → `Supplier` (back_populates="purchase_orders")
- `company` → `AppClientCompany` (back_populates="purchase_orders")
- `location` → `StorageLocation` (back_populates="purchase_orders")
- `details` → `PurchaseOrderDetail` (1:N, cascade="all, delete-orphan")
- `payment_details` → `ProductOrderPaymentDetail` (1:N, cascade="all, delete-orphan")
- `creator` → `User` (FK via cb)

**Properties:**
- `created_by_name` → Returns creator.user_name
- `effective_total_amount` → Calculates: Σ((quantity - returned - rejected) × unit_price - discount)

---

### 2.2 PurchaseOrderDetail

**Table:** `procurement.purchase_order_detail`

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `purchase_order_detail_id` | Integer | PK, index | Primary key |
| `purchase_order_id` | Integer | FK → purchase_order, NOT NULL | Parent PO |
| `product_id` | Integer | FK → product, NOT NULL | Product reference |
| `variant_id` | Integer | FK → product_variant | Variant reference |
| `unit_of_measure_id` | Integer | FK → unit_of_measure | UOM for quantity |
| `quantity` | Numeric(18,4) | NOT NULL | Ordered quantity |
| `unit_price` | Numeric(18,4) | NOT NULL | Price per unit |
| `received_quantity` | Numeric(18,4) | NOT NULL, default 0 | Quantity received |
| `free_quantity` | Numeric(18,4) | NOT NULL, default 0 | Free items promised |
| `received_free_quantity` | Numeric(18,4) | NOT NULL, default 0 | Free items received |
| `returned_quantity` | Numeric(18,4) | NOT NULL, default 0 | Quantity returned |
| `rejected_quantity` | Numeric(18,4) | NOT NULL, default 0 | Quantity rejected |
| `discount_amount` | Numeric(18,2) | NOT NULL, default 0 | Discount applied |
| `applied_scheme_id` | Integer | nullable | Claim scheme applied |
| `is_free_item` | Boolean | nullable, default False | Is this a free item line |
| `parent_detail_id` | Integer | FK → self | Link to base detail (buy_x_get_y) |
| `cb` | Integer | NOT NULL | Created by |
| `cd` | DateTime | NOT NULL | Created date |
| `mb` | Integer | NOT NULL | Modified by |
| `md` | DateTime | NOT NULL | Modified date |
| `is_deleted` | Boolean | NOT NULL, default False | Soft delete flag |

**Relationships:**
- `purchase_order` → `PurchaseOrder` (back_populates="details")
- `product` → `Product` (back_populates="purchase_order_details")
- `variant` → `ProductVariant` (back_populates="purchase_order_details")
- `unit_of_measure` → `UnitOfMeasure` (back_populates="purchase_order_details")
- `delivery_details` → `ProductOrderDeliveryDetail` (1:N)
- `batches` → `Batch` (back_populates="purchase_order_detail")

**Properties:**
- `effective_tp` → (quantity × unit_price - discount) / (quantity + free_quantity)

---

### 2.3 ProductOrderDeliveryDetail

**Table:** `procurement.product_order_delivery_detail`

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `delivery_detail_id` | Integer | PK, index | Primary key |
| `purchase_order_detail_id` | Integer | FK → purchase_order_detail, NOT NULL | Parent detail |
| `delivery_date` | TIMESTAMP | NOT NULL | Date of delivery |
| `delivered_quantity` | Numeric(18,4) | NOT NULL | Quantity delivered in this batch |
| `delivered_free_quantity` | Numeric(18,4) | NOT NULL, default 0 | Free items delivered |
| `received_by` | Integer | nullable | User who received |
| `rejected_quantity` | Numeric(18,4) | NOT NULL, default 0 | Quantity rejected |
| `rejected_free_quantity` | Numeric(18,4) | NOT NULL, default 0 | Free items rejected |
| `remarks` | String(500) | nullable | Notes |
| `cb` | Integer | NOT NULL | Created by |
| `cd` | DateTime | NOT NULL | Created date |
| `mb` | Integer | NOT NULL | Modified by |
| `md` | DateTime | NOT NULL | Modified date |
| `is_deleted` | Boolean | NOT NULL, default False | Soft delete flag |

**Relationships:**
- `purchase_order_detail` → `PurchaseOrderDetail` (back_populates="delivery_details")

---

### 2.4 ProductOrderPaymentDetail

**Table:** `procurement.product_order_payment_detail`

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `payment_detail_id` | Integer | PK, index | Primary key |
| `purchase_order_id` | Integer | FK → purchase_order, NOT NULL | Parent PO |
| `payment_date` | TIMESTAMP | NOT NULL | Date of payment |
| `amount_paid` | Numeric(18,2) | NOT NULL | Amount paid |
| `payment_method` | String(50) | nullable | Cash/Card/Transfer/etc |
| `transaction_reference` | String(100) | nullable | Reference number |
| `remarks` | String(500) | nullable | Notes |
| `cb` | Integer | NOT NULL | Created by |
| `cd` | DateTime | NOT NULL | Created date |
| `mb` | Integer | NOT NULL | Modified by |
| `md` | DateTime | NOT NULL | Modified date |
| `is_deleted` | Boolean | NOT NULL, default False | Soft delete flag |

**Relationships:**
- `purchase_order` → `PurchaseOrder` (back_populates="payment_details")

---

### 2.5 Supplier

**Table:** `procurement.supplier`

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `supplier_id` | Integer | PK, index | Primary key |
| `supplier_name` | String(200) | NOT NULL | Display name |
| `supplier_code` | String(50) | nullable, index | Short code |
| `contact_person` | String(100) | nullable | Contact name |
| `contact_email` | String(100) | nullable | Email |
| `contact_phone` | String(20) | nullable | Phone |
| `address` | String(200) | nullable | Address |
| `country_id` | Integer | FK → country | Country |
| `state_id` | Integer | FK → state | State |
| `city_id` | Integer | FK → city | City |
| `zip_code` | String(20) | nullable | Postal code |
| `payment_terms` | String(50) | nullable | Payment terms |
| `balance_amount` | Numeric(18,2) | NOT NULL, default 0 | Outstanding balance |
| `is_active` | Boolean | NOT NULL, default True | Active flag |
| `version` | Integer | NOT NULL, default 1 | Optimistic locking |
| `company_id` | Integer | FK → app_client_company | Multi-tenant |
| `cb`, `cd`, `mb`, `md` | - | Audit fields | Standard audit |
| `is_deleted` | Boolean | Soft delete flag | Standard |

**Relationships:**
- `purchase_orders` → `PurchaseOrder` (1:N)
- `batches` → `Batch` (1:N)
- `country`, `state`, `city` → Geographic entities

---

## 3. Backend Operations Reference

### 3.1 PurchaseOrder Operations

| Operation | Method | Endpoint | Service Method | Description |
|-----------|--------|----------|----------------|-------------|
| **List** | GET | `/api/company/procurement/purchase-order/` | `PurchaseOrderService.list_purchase_orders()` | Paginated list with filters |
| **Get Single** | GET | `/api/company/procurement/purchase-order/{id}` | `PurchaseOrderService.get_purchase_order()` | Full PO with details |
| **Create** | POST | `/api/company/procurement/purchase-order/` | `PurchaseOrderService.create_purchase_order()` | Creates PO with claim evaluation |
| **Update** | PATCH | `/api/company/procurement/purchase-order/{id}` | `PurchaseOrderService.update_purchase_order()` | Updates PO fields |
| **Delete** | DELETE | `/api/company/procurement/purchase-order/{id}` | `PurchaseOrderService.delete_purchase_order()` | Soft delete with validation |
| **Cancel** | POST | `/api/company/procurement/purchase-order/{id}/cancel` | `PurchaseOrderService.cancel_purchase_order()` | Cancel PO, reverse supplier balance |
| **Return** | POST | `/api/company/procurement/purchase-order/{id}/return` | `PurchaseOrderService.process_return()` | Process return to supplier |
| **Reject** | POST | `/api/company/procurement/purchase-order/{id}/rejection` | `PurchaseOrderService.process_rejection()` | Reject items during delivery |

**List Query Parameters:**
- `order_date_start`, `order_date_end` - Date range filter
- `delivery_date_start`, `delivery_date_end` - Delivery date filter
- `status` - PO status filter
- `location_id` - Location filter
- `supplier_id` - Supplier filter
- `min_amount`, `max_amount` - Amount range filter
- `sort_by` - Options: `order_date_asc`, `order_date_desc`, `amount_asc`, `amount_desc`, `supplier_asc`, `supplier_desc`
- `start`, `limit` - Pagination

---

### 3.2 PurchaseOrderDetail Operations

| Operation | Method | Endpoint | Service Method | Description |
|-----------|--------|----------|----------------|-------------|
| **List** | GET | `/api/company/procurement/purchase-order-detail/` | `PurchaseOrderDetailService.list_purchase_order_details()` | List with filters |
| **Get Single** | GET | `/api/company/procurement/purchase-order-detail/{id}` | `PurchaseOrderDetailService.get_purchase_order_detail()` | Single detail |
| **Create** | POST | `/api/company/procurement/purchase-order-detail/` | `PurchaseOrderDetailService.create_purchase_order_detail()` | Add detail to PO |
| **Update** | PATCH | `/api/company/procurement/purchase-order-detail/{id}` | `PurchaseOrderDetailService.update_purchase_order_detail()` | Update detail |
| **Delete** | DELETE | `/api/company/procurement/purchase-order-detail/{id}` | `PurchaseOrderDetailService.delete_purchase_order_detail()` | Soft delete detail |

**List Query Parameters:**
- `purchase_order_id` - Filter by PO
- `product_id`, `variant_id` - Product filters
- `quantity_min`, `quantity_max` - Quantity range
- `cd_start`, `cd_end` - Creation date range
- `sort_by` - Sort options: `cd_desc`, `cd_asc`, `quantity_asc`, `quantity_desc`

---

### 3.3 Repository Methods (PurchaseOrderRepository)

| Method | Purpose |
|--------|---------|
| `generate_order_number(company_id)` | Generates PO-YYYYMMDD-SEQ format |
| `list(...)` | Full filtered, paginated query with metadata |
| `get(purchase_order_id)` | Single PO with all relationships |
| `create(purchase_order_obj)` | Insert new PO |
| `update(purchase_order_obj)` | Update existing PO |
| `delete(purchase_order_obj)` | Soft delete |
| `get_dashboard_summary_metrics(...)` | Dashboard KPI aggregation |
| `get_top_suppliers(...)` | Top suppliers by spend |
| `get_recent_orders(...)` | Recent POs list |
| `get_monthly_trends(...)` | Monthly PO trends |

---

## 4. Frontend UI Walkthrough

### 4.1 Pages Inventory

| Page | Route | Status | Description |
|------|-------|--------|-------------|
| **Purchase List** | `/purchases` | ✅ | Main listing with filters, table, actions |
| **Add Purchase** | `/purchases/new` | ✅ | Create new PO with multi-line form |
| **Reports** | `/reports/purchase-order/*` | ✅ | 8 report types (see below) |

**Report Pages (`/src/pages/reports/purchaseorder/`):**
| Report | File | Description |
|--------|------|-------------|
| ABC/XYZ Classification | `ABCXYZClassification.tsx` | Product classification analysis |
| Cash Flow Projection | `CashFlowProjection.tsx` | Payment projections |
| Emergency Orders | `EmergencyOrders.tsx` | Urgent order analysis |
| Maverick Spend | `MaverickSpend.tsx` | Unusual spending patterns |
| PO Progress | `POProgress.tsx` | Order progress tracking |
| Supplier Consolidation | `SupplierConsolidation.tsx` | Supplier spend analysis |
| Uninvoiced Receipts | `UninvoicedReceipts.tsx` | Receipts without invoices |
| Variance Report | `VarianceReport.tsx` | PO vs receipt variances |

### 4.2 Forms & Modals

| Component | File Path | Purpose |
|-----------|-----------|---------|
| `PurchaseForm` | `src/components/forms/PurchaseForm.tsx` | Main PO creation/editing (1900+ lines) |
| `PurchasePaymentForm` | `src/components/forms/PurchasePaymentForm.tsx` | Record payment against PO |
| `PurchaseDeliveryForm` | `src/components/forms/PurchaseDeliveryForm.tsx` | Record delivery/receipt |
| `PurchaseReturnForm` | `src/components/forms/PurchaseReturnForm.tsx` | Process returns to supplier |
| `PurchaseOrderStatusForm` | `src/components/forms/PurchaseOrderStatusForm.tsx` | Update PO status |

### 4.3 Shared Components

| Component | File Path | Purpose |
|-----------|-----------|---------|
| `PurchaseFilter` | `src/components/PurchaseFilter.tsx` | Filter panel for list page |
| `PurchaseOperationsWidget` | `src/components/dashboard/PurchaseOperationsWidget.tsx` | Dashboard widget |
| `ViewPurchaseDetails` | `src/pages/purchases/ViewPurchaseDetails.tsx` | View payments/deliveries dialog |
| `ViewOrderDetails` | `src/components/shared/ViewOrderDetails.tsx` | Generic order detail viewer |
| `OrderStatus` | `src/components/shared/OrderStatus.tsx` | Status badge component |

### 4.4 Report Components

| Component | File Path | Purpose |
|-----------|-----------|---------|
| `MonthlyVolumeChart` | `src/components/purchaseOrderReports/MonthlyVolumeChart.tsx` | Volume trends |
| `OpenPOTable` | `src/components/purchaseOrderReports/OpenPOTable.tsx` | Open orders table |
| `POAgingTable` | `src/components/purchaseOrderReports/POAgingTable.tsx` | Aging analysis |
| `POKPISummary` | `src/components/purchaseOrderReports/POKPISummary.tsx` | KPI cards |
| `POProgressTable` | `src/components/purchaseOrderReports/POProgressTable.tsx` | Progress tracking |
| `POStatusDistributionChart` | `src/components/purchaseOrderReports/POStatusDistributionChart.tsx` | Status pie chart |
| `SupplierLeadTimeChart` | `src/components/purchaseOrderReports/SupplierLeadTimeChart.tsx` | Lead time analysis |
| `SupplierPerformanceTable` | `src/components/purchaseOrderReports/SupplierPerformanceTable.tsx` | Supplier metrics |
| `TopSuppliersBySpendChart` | `src/components/purchaseOrderReports/TopSuppliersBySpendChart.tsx` | Spend ranking |
| `UninvoicedReceiptsTable` | `src/components/purchaseOrderReports/UninvoicedReceiptsTable.tsx` | Uninvoiced tracking |

### 4.5 API Layer

**File:** `src/lib/api/purchaseApi.ts`

| Function | HTTP | Endpoint |
|----------|------|----------|
| `getPurchases()` | GET | `/procurement/purchase-order/` |
| `getPurchaseById(id)` | GET | `/procurement/purchase-order/{id}` |
| `createPurchase(data)` | POST | `/procurement/purchase-order/` |
| `updatePurchase(data)` | PATCH | `/procurement/purchase-order/{id}` |
| `deletePurchase(id)` | DELETE | `/procurement/purchase-order/{id}` |
| `returnPurchaseOrder(id, data)` | POST | `/procurement/purchase-order/{id}/return` |
| `rejectPurchaseOrder(id, data)` | POST | `/procurement/purchase-order/{id}/rejection` |
| `getPurchasePayments(id)` | GET | `/procurement/product-order-payment-detail/?purchase_order_id={id}` |
| `createPurchasePayment(data)` | POST | `/procurement/product-order-payment-detail/` |
| `updatePurchasePayment(id, data)` | PATCH | `/procurement/product-order-payment-detail/{id}` |
| `deletePurchasePayment(id)` | DELETE | `/procurement/product-order-payment-detail/{id}` |
| `getPurchaseDeliveries(id)` | GET | `/procurement/product-order-delivery-detail/?purchase_order_id={id}` |
| `createPurchaseDelivery(data)` | POST | `/procurement/product-order-delivery-detail/` |
| `updatePurchaseDelivery(id, data)` | PATCH | `/procurement/product-order-delivery-detail/{id}` |
| `deletePurchaseDelivery(id)` | DELETE | `/procurement/product-order-delivery-detail/{id}` |

### 4.6 Types & Zod Schemas

**File:** `src/lib/schema/purchases.ts`

| Schema/Type | Fields |
|-------------|--------|
| `insertPurchaseItemSchema` | product_id, variant_id, quantity, unit_of_measure_id, unit_price, received_quantity, free_quantity, received_free_quantity, returned_quantity, rejected_quantity, discount_amount, applied_scheme_id, from_group, is_free_item, parent_detail_id |
| `insertPurchaseSchema` | order_number, supplier_id, order_date, expected_delivery_date, status, total_amount, amount_paid, company_id, location_id, payment_status, delivery_status, details[] |
| `purchasePaymentSchema` | payment_date, amount_paid, payment_method, transaction_reference, remarks |
| `purchaseDeliverySchema` | delivery_date, delivered_quantity, delivered_free_quantity, remarks |
| `PurchaseDetail` | All detail fields + product_name, variant_name, variant_sku, unit_name, effective_tp |
| `Purchase` | All PO fields + supplier_name, company_name, location_name, effective_total_amount, details[] |
| `PurchaseResponse` | total_count, data[] |

---

## 5. Interconnected Workflows

### 5.1 Purchase Order Creation Flow

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. User navigates to /purchases/new                             │
│    → AddPurchase.tsx renders PurchaseForm                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. PurchaseForm loads dependencies via useQuery                   │
│    → Suppliers: getSuppliers()                                  │
│    → Variants: getAllVariants()                                  │
│    → Locations: getStorageLocations()                           │
│    → Schemes: getSchemes() (for claim evaluation)               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. User fills PO header:                                         │
│    → Supplier (searchable dropdown)                             │
│    → Order Date, Expected Delivery Date                           │
│    → Delivery Location                                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. User adds line items:                                         │
│    → Product/Variant selection (searchable)                   │
│    → Quantity, Unit Price                                       │
│    → UOM selection (auto-populated from variant)                │
│    → Manual scheme selection (optional)                         │
│    → OR: Product Group selection for bulk add                 │
│    → OR: Excel import (validated)                               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. Real-time calculations:                                       │
│    → Amount = Quantity × Unit Price                             │
│    → Scheme benefits calculated (free_qty, discount)            │
│    → Free item lines auto-created for buy_x_get_y               │
│    → Total = Σ(line amounts - discounts)                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 6. Submit: createPurchase(data)                                  │
│    → POST /procurement/purchase-order/                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 7. Backend processing:                                            │
│    → Validate supplier belongs to company                       │
│    → Generate order_number: PO-YYYYMMDD-SEQ                     │
│    → ClaimService.evaluate_pre_claim() for each line            │
│    → Create free item lines for cross-product schemes           │
│    → Validate all products/variants/UOMs exist                  │
│    → Calculate total with UOM-aware pricing                     │
│    → Update supplier balance += total_amount                    │
│    → Create payment detail if amount_paid > 0                   │
│    → Log claim applications                                     │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 Delivery/Receipt Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. User clicks "Get Delivery" from Purchases list               │
│    → Opens PurchaseDeliveryForm modal                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. Form displays all PO line items with quantities:             │
│    → Ordered, Received, Rejected, Returned, Pending            │
│    → Free Qty, Received Free, Pending Free                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. User enters delivery quantities:                              │
│    → Accept Billable Quantity                                     │
│    → Accept Free Quantity                                         │
│    → Reject Billable Quantity (optional)                        │
│    → Reject Free Quantity (optional)                            │
│    → Remarks                                                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. Validation:                                                    │
│    → accepted + rejected ≤ pending for each line              │
│    → Cannot exceed ordered quantities                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. Submit processing:                                            │
│    → Receipts: createPurchaseDelivery() → POST delivery-detail  │
│    → Rejections: rejectPurchaseOrder() → POST /rejection        │
│    → Inventory stock updated (quantity += received)             │
│    → InventoryTransaction created (PURCHASE_RECEIPT)            │
│    → Batch created (if batch tracking enabled)                │
│    → PO delivery_status updated (Pending/Partial/Completed)     │
│    → PO overall status updated (Open/Partial/Completed)         │
└─────────────────────────────────────────────────────────────────┘
```

### 5.3 Payment Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. User clicks "Make Payment" from Purchases list               │
│    → Opens PurchasePaymentForm modal                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. Form displays PO summary:                                    │
│    → Total Amount, Effective Total, Amount Paid, Remaining      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. User enters payment details:                                 │
│    → Payment Date                                                 │
│    → Amount Paid (with "Full Payment" button)                    │
│    → Payment Method                                               │
│    → Transaction Reference                                        │
│    → Remarks                                                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. Validation:                                                  │
│    → If overpayment, remarks required                            │
│    → Overpayment confirmation dialog                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. Submit: createPurchasePayment()                               │
│    → POST /procurement/product-order-payment-detail/            │
│    → Updates PO amount_paid                                      │
│    → Updates PO payment_status (Pending/Partial/Completed)      │
│    → If overpayment: adds to supplier balance                   │
└─────────────────────────────────────────────────────────────────┘
```

### 5.4 Return Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. User clicks "Return Purchase" from Purchases list            │
│    → Opens PurchaseReturnForm modal                             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. Form displays returnable quantities:                         │
│    → Only items with received_quantity > 0 are returnable        │
│    → Shows Received, Returned, Available for Return            │
│    → Batch-level stock availability checked                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. User enters return quantities:                               │
│    → Quantity to return (cannot exceed available)               │
│    → Return Date                                                  │
│    → Remarks                                                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. Submit: returnPurchaseOrder(id, data)                         │
│    → POST /procurement/purchase-order/{id}/return               │
│    → Pre-validation: Check batch quantity on hand               │
│    → Update: detail.returned_quantity += qty                     │
│    → Update: detail.received_quantity -= qty                   │
│    → Update: inventory_stock.quantity -= qty                    │
│    → Create: InventoryTransaction (PURCHASE_RETURN)               │
│    → Update: batch.qty_on_hand -= qty (FIFO from batches)      │
│    → Create: batch_movement (RETURN_OUT)                        │
│    → Update: supplier.balance_amount -= (qty × effective_tp)    │
│    → Update: PO.delivery_status and PO.status                   │
└─────────────────────────────────────────────────────────────────┘
```

### 5.5 Delete/Cancel Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│ DELETE (Soft Delete) - Only allowed if:                         │
│    → No deliveries recorded (received/rejected = 0)              │
│    → No payments recorded                                        │
│ Effects:                                                        │
│    → Soft delete PO and all details                             │
│    → Soft delete all payment_details                            │
│    → Soft delete all delivery_details                           │
│    → Reverse supplier balance -= total_amount                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ CANCEL - Only allowed if:                                       │
│    → Status is not "Completed"                                  │
│    → No deliveries or payments recorded                          │
│ Effects:                                                        │
│    → Set status = "Cancelled"                                   │
│    → Reverse supplier balance -= total_amount                   │
│    → Record user and timestamp                                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 6. Special Features Deep-Dive

### 6.1 Claims/Schemes Integration

The Purchase Order module integrates with the Claims module for automatic scheme evaluation.

**How it works:**

```python
# During PO creation (PurchaseOrderService.create_purchase_order)
items_to_evaluate = [
    {
        "product_id": d.get("product_id"),
        "variant_id": d.get("variant_id"),
        "quantity": d.get("quantity"),
        "unit_price": d.get("unit_price"),
        "applied_scheme_id": d.get("applied_scheme_id"),
    }
    for d in purchase_order_data["details"]
    if not d.get("is_free_item", False)
]

evaluated_items = claim_service.evaluate_pre_claim(
    company_id, items_to_evaluate, target_module="purchase"
)
```

**Scheme Types Supported:**
- `buy_x_get_y` - Buy quantity X, get Y free (same or different product)
- `rebate_flat` - Flat discount amount based on quantity tiers
- `rebate_percentage` - Percentage discount on qualifying quantity

**Benefits Applied:**
- `free_quantity` - Additional free items
- `discount_amount` - Monetary discount
- `applied_scheme_id` - Reference to the applied scheme

**Free Item Line Creation:**
For `buy_x_get_y` schemes with different free products:
```python
# Backend creates separate free item lines
free_line = {
    "product_id": free_product_id,
    "variant_id": free_variant_id,
    "quantity": free_quantity,
    "unit_price": 0,  # Free!
    "is_free_item": True,
    "parent_detail_id": base_detail_id,
    "applied_scheme_id": scheme_id,
}
```

---

### 6.2 UOM-Aware Pricing

The module supports Unit of Measure conversions for consistent pricing.

**Base Conversion Logic:**
```python
from app.services.uom_utils import convert_to_base, convert_price_to_base

# Convert quantity to base UOM
base_quantity = convert_to_base(db, detail.quantity, detail.unit_of_measure_id)

# Convert price to base UOM equivalent
base_unit_price = convert_price_to_base(db, detail.unit_price, detail.unit_of_measure_id)

# Calculate total in base UOM
detail_total = (base_quantity * base_unit_price) - discount
```

**Example:**
- Product base UOM: `Piece` (1)
- Order UOM: `Box` (12 pieces)
- Order quantity: 5 Boxes
- Order unit price: $120/Box
- Calculation:
  - Base quantity: 5 × 12 = 60 pieces
  - Base unit price: $120 / 12 = $10/piece
  - Total: 60 × $10 = $600

---

### 6.3 Batch Tracking Integration

Purchase orders integrate with batch inventory for tracking:

**On Delivery:**
- Batch created with `purchase_order_detail_id` link
- Batch quantity = delivered quantity
- Supplier linked to batch

**On Return:**
- Batch quantity decremented (FIFO from batches)
- `RETURN_OUT` movement recorded
- Only available batch quantity can be returned

**Code Example:**
```python
# Return validation
batches = self.batch_repo.get_batches_by_po_detail(
    company_id, detail.purchase_order_detail_id
)
total_on_hand = sum(b.qty_on_hand for b in batches)
if total_on_hand < qty:
    raise ValueError(f"Insufficient batch quantity to process return")

# Return execution
for batch in sorted(batches, key=lambda b: b.batch_id):
    batch_return_qty = min(remaining_to_return, batch.qty_on_hand)
    self.batch_repo.decrement_qty_on_hand(batch.batch_id, batch_return_qty, user_id)
    self.movement_repo.create_movement(
        company_id=company_id,
        batch_id=batch.batch_id,
        qty=-batch_return_qty,
        movement_type="RETURN_OUT",
        ref_type="PURCHASE_RETURN",
        ref_id=purchase_order_id,
    )
```

---

### 6.4 Multi-Status Tracking

Each PO has three status dimensions:

1. **Status** (Overall): `Open` → `Partial` → `Completed` | `Cancelled`
   - Derived from payment_status + delivery_status
   - Auto-updated via `_update_po_status()`

2. **Payment Status**: `Pending` → `Partial` → `Completed`
   - Based on `amount_paid` vs `effective_total_amount`

3. **Delivery Status**: `Pending` → `Partial` → `Completed`
   - Based on received + rejected + returned vs ordered
   - Also considers free items separately

**Status Update Logic:**
```python
def _update_po_status(self, purchase_order):
    if purchase_order.status == "Cancelled":
        return

    payment_complete = purchase_order.payment_status == "Completed"
    delivery_complete = purchase_order.delivery_status == "Completed"

    if payment_complete and delivery_complete:
        new_status = "Completed"
    elif (purchase_order.payment_status != "Pending" or 
          purchase_order.delivery_status != "Pending"):
        new_status = "Partial"
    else:
        new_status = "Open"

    purchase_order.status = new_status
```

---

### 6.5 Excel Import with Validation

The frontend supports importing PO lines from Excel with comprehensive validation:

**Template Columns:**
- `VariantSKU` or `ProductCode` (required)
- `VariantAttribute` (optional, for disambiguation)
- `Quantity` (required)
- `UnitPrice` (required)
- `UnitName` (optional)

**Validation Rules (ISSUE-021 FIX):**
1. File type: Only `.xlsx`, `.xls` allowed
2. File size: Max 5MB
3. Required columns must be present
4. All rows validated before any import (atomic)
5. Numeric validation for quantity/price
6. Range validation (0 < qty ≤ 1,000,000)
7. Product/variant existence validation
8. UOM name matching

**Error Display:**
```typescript
const errorMessage = (
  <div className="max-w-md">
    <p className="font-semibold mb-2">Import failed with {validationErrors.length} error(s):</p>
    <ul className="text-sm list-disc pl-4 max-h-60 overflow-y-auto">
      {validationErrors.slice(0, 10).map((err, idx) => <li key={idx}>{err}</li>)}
      {validationErrors.length > 10 && <li className="italic">...and more errors</li>}
    </ul>
  </div>
);
toast.error(errorMessage, { duration: 10000 });
```

---

### 6.6 Soft Delete with Cascade

Purchase orders use soft delete with validation:

**Delete Validation:**
```python
def delete_purchase_order(self, purchase_order_id, company_id):
    # Cannot delete if deliveries recorded
    has_deliveries = any(
        (detail.received_quantity or 0) > 0
        or (detail.received_free_quantity or 0) > 0
        or (detail.rejected_quantity or 0) > 0
        for detail in db_purchase_order.details
    )
    
    # Cannot delete if payments recorded
    has_payments = len([p for p in db_purchase_order.payment_details if not p.is_deleted]) > 0
    
    if has_deliveries:
        raise ValueError("Cannot delete: deliveries have been recorded")
    
    if has_payments:
        raise ValueError("Cannot delete: payments have been recorded")
```

**Cascade Delete:**
- Soft delete all `delivery_details` on each detail
- Soft delete all `payment_details` on PO
- Soft delete all `purchase_order_details`
- Soft delete `purchase_order`
- Reverse supplier balance

---

### 6.7 Supplier Balance Management

Purchase orders automatically update supplier balances:

**On Create:**
```python
supplier.balance_amount += Decimal(str(total_amount))
```

**On Update (amount changed):**
```python
balance_diff = Decimal(str(new_total)) - Decimal(str(old_total))
supplier.balance_amount += balance_diff
```

**On Delete/Cancel:**
```python
supplier.balance_amount -= Decimal(str(total_amount))
```

**On Return:**
```python
returned_amount = qty * Decimal(str(detail.effective_tp))
supplier.balance_amount -= returned_amount
```

---

## 7. API Quick Reference

### 7.1 Endpoint Summary by Entity

| Entity | List | Get | Create | Update | Delete | Special |
|--------|------|-----|--------|--------|--------|---------|
| **PurchaseOrder** | ✅ GET / | ✅ GET /{id} | ✅ POST / | ✅ PATCH /{id} | ✅ DELETE /{id} | Cancel, Return, Reject |
| **PurchaseOrderDetail** | ✅ GET / | ✅ GET /{id} | ✅ POST / | ✅ PATCH /{id} | ✅ DELETE /{id} | - |
| **ProductOrderPaymentDetail** | ✅ GET / | ✅ GET /{id} | ✅ POST / | ✅ PATCH /{id} | ✅ DELETE /{id} | - |
| **ProductOrderDeliveryDetail** | ✅ GET / | ✅ GET /{id} | ✅ POST / | ✅ PATCH /{id} | ✅ DELETE /{id} | - |

### 7.2 Frontend API Function Map

| Operation | Frontend Function | Backend Endpoint |
|-----------|-------------------|------------------|
| List POs | `getPurchases(params)` | `GET /procurement/purchase-order/` |
| Get PO | `getPurchaseById(id)` | `GET /procurement/purchase-order/{id}` |
| Create PO | `createPurchase(data)` | `POST /procurement/purchase-order/` |
| Update PO | `updatePurchase(data)` | `PATCH /procurement/purchase-order/{id}` |
| Delete PO | `deletePurchase(id)` | `DELETE /procurement/purchase-order/{id}` |
| Return PO | `returnPurchaseOrder(id, data)` | `POST /procurement/purchase-order/{id}/return` |
| Reject PO | `rejectPurchaseOrder(id, data)` | `POST /procurement/purchase-order/{id}/rejection` |
| List Payments | `getPurchasePayments(id)` | `GET /procurement/product-order-payment-detail/` |
| Create Payment | `createPurchasePayment(data)` | `POST /procurement/product-order-payment-detail/` |
| List Deliveries | `getPurchaseDeliveries(id)` | `GET /procurement/product-order-delivery-detail/` |
| Create Delivery | `createPurchaseDelivery(data)` | `POST /procurement/product-order-delivery-detail/` |

---

## 8. File Map

### 8.1 Backend Files

| Layer | File Path | Purpose |
|-------|-----------|---------|
| **Models** | `Shoudagor/app/models/procurement.py` | PurchaseOrder, PurchaseOrderDetail, Supplier, ProductOrderDeliveryDetail, ProductOrderPaymentDetail |
| **Models** | `Shoudagor/app/models/mixins.py` | OrderBase, OrderDetailBase, PaymentDetailBase, DeliveryDetailBase (shared base classes) |
| **Schemas** | `Shoudagor/app/schemas/procurement/purchase_order.py` | Pydantic schemas for PO and details |
| **API** | `Shoudagor/app/api/procurement/purchase_order.py` | PO endpoints (8 routes) |
| **API** | `Shoudagor/app/api/procurement/purchase_order_detail.py` | Detail endpoints (5 routes) |
| **Services** | `Shoudagor/app/services/procurement/purchase_order_service.py` | Main PO business logic (1156 lines) |
| **Services** | `Shoudagor/app/services/procurement/purchase_order_detail_service.py` | Detail CRUD + inventory updates |
| **Repositories** | `Shoudagor/app/repositories/procurement/purchase_order.py` | PO data access + dashboard queries |
| **Repositories** | `Shoudagor/app/repositories/procurement/purchase_order_detail.py` | Detail data access |

### 8.2 Frontend Files

| Layer | File Path | Purpose |
|-------|-----------|---------|
| **Pages** | `shoudagor_FE/src/pages/purchases/Purchases.tsx` | Main listing page |
| **Pages** | `shoudagor_FE/src/pages/purchases/new/AddPurchase.tsx` | Create PO wrapper |
| **Pages** | `shoudagor_FE/src/pages/purchases/ViewPurchaseDetails.tsx` | View payments/deliveries |
| **Pages** | `shoudagor_FE/src/pages/reports/purchaseorder/*.tsx` | 8 report pages |
| **Forms** | `shoudagor_FE/src/components/forms/PurchaseForm.tsx` | Main PO form (1900+ lines) |
| **Forms** | `shoudagor_FE/src/components/forms/PurchasePaymentForm.tsx` | Payment form |
| **Forms** | `shoudagor_FE/src/components/forms/PurchaseDeliveryForm.tsx` | Delivery/receipt form |
| **Forms** | `shoudagor_FE/src/components/forms/PurchaseReturnForm.tsx` | Return form |
| **Components** | `shoudagor_FE/src/components/PurchaseFilter.tsx` | Filter panel |
| **Components** | `shoudagor_FE/src/components/purchaseOrderReports/*.tsx` | 10 report components |
| **API** | `shoudagor_FE/src/lib/api/purchaseApi.ts` | All purchase API calls |
| **Schemas** | `shoudagor_FE/src/lib/schema/purchases.ts` | Zod schemas and types |

---

## 9. Appendix: Operation Counts

| Entity | Backend CRUD Ops | Backend Special Ops | Frontend API Functions | Frontend Components |
|--------|-----------------|---------------------|----------------------|---------------------|
| **PurchaseOrder** | 5 (List, Get, Create, Update, Delete) | 5 (Cancel, Return, Reject, Dashboard metrics, Status updates) | 6 | 4 (List, Add, View, Reports index) |
| **PurchaseOrderDetail** | 5 (List, Get, Create, Update, Delete) | 2 (Inventory update on create, Cascade delete) | 0 (embedded in PO API) | 1 (embedded in PurchaseForm) |
| **ProductOrderPaymentDetail** | 5 | 2 (Status update trigger, Overpayment handling) | 4 (List, Create, Update, Delete) | 2 (PaymentForm, ViewPayments) |
| **ProductOrderDeliveryDetail** | 5 | 3 (Status update trigger, Batch creation, Movement logging) | 4 (List, Create, Update, Delete) | 2 (DeliveryForm, ViewDeliveries) |
| **Supplier** | 5 | 1 (Balance management) | 1 (getSuppliers) | 1 (select dropdown) |
| **Reports/Dashboard** | 5 | 0 | 0 | 18 (10 components + 8 pages) |
| **TOTAL** | **30** | **18** | **15** | **29** |

---

## Summary Statistics

- **Database Tables:** 5 (purchase_order, purchase_order_detail, supplier, product_order_delivery_detail, product_order_payment_detail)
- **Backend API Routes:** 18 endpoints across 4 routers
- **Backend Service Methods:** 48+ methods
- **Frontend Pages:** 3 main + 8 reports = 11 pages
- **Frontend Components:** 29 components
- **Lines of Code:** ~6,000+ (backend) + ~8,000+ (frontend)

---

*End of Document*
