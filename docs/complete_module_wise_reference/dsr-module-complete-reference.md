# DSR Module - Full-Stack Reference Documentation

> **Document Purpose:** Comprehensive operations and UI walkthrough for the Delivery Sales Representative (DSR) module in the Shoudagor ERP system.
> 
> **Scope:** Backend API, frontend UI, database entities, interconnected workflows, and special features.
> 
> **Last Updated:** 2025

---

## 1. Module Architecture Overview

### 1.1 Layer Structure

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                    FRONTEND LAYER                                        │
│  ┌─────────────────┐  ┌──────────────────┐  ┌─────────────────┐  ┌─────────────────────┐ │
│  │  DSR Pages      │  │  DSR Forms       │  │  Shared UI      │  │  React Query Hooks  │ │
│  │  (React/TSX)    │  │  (Zod Schemas)   │  │  Components     │  │  (API Layer)        │ │
│  └────────┬────────┘  └────────┬───────┘  └────────┬────────┘  └──────────┬──────────┘ │
└───────────┼──────────────────────┼───────────────────┼──────────────────────┼────────────┘
            │                      │                   │                      │
            ▼                      ▼                   ▼                      ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                    API LAYER                                             │
│  ┌───────────────────────────────────────────────────────────────────────────────────┐ │
│  │                     RESTful Endpoints (FastAPI)                                    │ │
│  │  /api/company/sales/dsr/*                                                        │ │
│  │  /api/company/warehouse/dsr-storage/*                                              │ │
│  │  /api/company/warehouse/dsr-inventory-stock/*                                    │ │
│  └───────────────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────────────┘
                                          │
                                          ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                  SERVICE LAYER                                           │
│  ┌──────────────────────────┐  ┌────────────────────────┐  ┌──────────────────────────┐ │
│  │ DeliverySalesRepService  │  │ DSRSOAssignmentService   │  │ DSRPaymentSettlementSvc  │ │
│  │ (CRUD + Validation)      │  │ (Load/Unload/Delivery)   │  │ (Payment Processing)     │ │
│  └──────────────────────────┘  └────────────────────────┘  └──────────────────────────┘ │
│  ┌──────────────────────────┐  ┌────────────────────────┐                              │
│  │ DSRStorageService        │  │ DSRInventoryStockSvc   │                              │
│  │ (Storage Management)     │  │ (Stock Tracking)       │                              │
│  └──────────────────────────┘  └────────────────────────┘                              │
└─────────────────────────────────────────────────────────────────────────────────────────┘
                                          │
                                          ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                REPOSITORY LAYER                                          │
│  ┌──────────────────────────┐  ┌────────────────────────┐  ┌──────────────────────────┐ │
│  │ DeliverySalesRepRepo     │  │ DSRSOAssignmentRepo    │  │ DSRPaymentSettlementRepo │ │
│  │ (SQLAlchemy Queries)     │  │ (Complex Joins)          │  │ (Aggregation)            │ │
│  └──────────────────────────┘  └────────────────────────┘  └──────────────────────────┘ │
│  ┌──────────────────────────┐  ┌────────────────────────┐                              │
│  │ DSRStorageRepo           │  │ DSRInventoryStockRepo  │                              │
│  └──────────────────────────┘  └────────────────────────┘                              │
└─────────────────────────────────────────────────────────────────────────────────────────┘
                                          │
                                          ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                DATABASE LAYER (PostgreSQL)                               │
│  ┌───────────────────────────────────────────────────────────────────────────────────┐ │
│  │  Schema: sales                    │  Schema: warehouse                              │ │
  │  - delivery_sales_representative  │  - dsr_storage                                  │ │
│  - dsr_so_assignment                │  - dsr_inventory_stock                          │ │
│  - dsr_payment_settlement           │  - dsr_stock_transfer                           │ │
│  └───────────────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Backend Framework** | FastAPI (Python) | REST API, dependency injection, auto OpenAPI |
| **ORM** | SQLAlchemy 2.0 | Database abstraction, relationship management |
| **Validation** | Pydantic v2 | Request/response schemas, data validation |
| **Database** | PostgreSQL 15+ | Primary data store with schema separation |
| **Frontend Framework** | React 18 (Vite) | UI components, state management |
| **Data Fetching** | TanStack Query v5 | Server state management, caching |
| **Forms/Validation** | React Hook Form + Zod | Form handling, client-side validation |
| **UI Components** | shadcn/ui + Radix | Accessible, composable UI primitives |
| **Tables** | TanStack Table v8 | Sorting, filtering, pagination |

### 1.3 Entity Relationships

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              ENTITY RELATIONSHIP DIAGRAM                                │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│  ┌──────────────────────────────┐         1:1          ┌──────────────────────────────┐  │
│  │  AppClientCompany          │──────────────────────▶│  DeliverySalesRepresentative │  │
│  │  (Multi-tenant context)      │                      │  ├─ dsr_id (PK)              │  │
│  └──────────────────────────────┘                      │  ├─ dsr_name, dsr_code       │  │
│           │                    1:N                       │  ├─ contact_email/phone      │  │
│           │                                              │  ├─ payment_on_hand         │  │
│           ▼                                              │  ├─ commission_amount       │  │
│  ┌──────────────────────────────┐                      └──────────────┬───────────────┘  │
│  │  User                        │                                       │                 │
│  │  ├─ dsr_id (FK, nullable)    │◀─────────────────────────────────────┘                 │
│  │  └─ role (dsr/admin/etc)    │                      1:N (via user.dsr_id)            │
│  └──────────────────────────────┘                                                      │
│                                                                                         │
│  DeliverySalesRepresentative (1) ───────┬─────── (N) DSRSOAssignment                    │
│                                          │                                               │
│  ┌──────────────────────────────┐      │      ┌──────────────────────────────┐       │
│  │  DSRSOAssignment             │◀─────┘      │  SalesOrder                    │       │
│  │  ├─ assignment_id (PK)       │    N:1      │  ├─ sales_order_id (PK)        │       │
│  │  ├─ dsr_id (FK)              │────────────▶│  ├─ order_number               │       │
│  │  ├─ sales_order_id (FK)      │             │  └─ order_status               │       │
│  │  ├─ assignment_status        │             └────────────────────────────────┘       │
│  │  ├─ loading_status            │                                                    │
│  │  ├─ delivery_status          │      ┌──────────────────────────────┐               │
│  │  ├─ payment_status            │      │  Customer                    │               │
│  │  ├─ amount_paid              │      │  └─ customer_id (PK)           │               │
│  │  └─ assigned_date            │◀─────│                              │               │
│  └──────────────────────────────┘  N:1  └──────────────────────────────┘               │
│           │                                                                              │
│           │ 1:N                                                                          │
│           ▼                                                                              │
│  ┌──────────────────────────────┐                                                      │
│  │  DSRPaymentSettlement          │                                                      │
│  │  ├─ settlement_id (PK)         │                                                      │
│  │  ├─ dsr_id (FK)              │                                                      │
│  │  ├─ amount                   │                                                      │
│  │  ├─ payment_method            │                                                      │
│  │  ├─ reference_number          │                                                      │
│  │  └─ settlement_date            │                                                      │
│  └──────────────────────────────┘                                                      │
│                                                                                         │
│  ┌──────────────────────────────┐         1:1          ┌──────────────────────────────┐│
│  │  DeliverySalesRepresentative │──────────────────────▶│  DSRStorage                  ││
│  │                              │                      │  ├─ dsr_storage_id (PK)      ││
│  └──────────────────────────────┘                      │  ├─ dsr_id (FK, unique)      ││
│                                                         │  ├─ storage_name/code         ││
│                                                         │  ├─ storage_type              ││
│                                                         │  └─ max_capacity             ││
│                                                         └──────────────┬───────────────┘│
│                                                                        │ 1:N            │
│                                                                        ▼                │
│                                                         ┌──────────────────────────────┐│
│                                                         │  DSRInventoryStock           ││
│                                                         │  ├─ stock_id (PK)            ││
│                                                         │  ├─ dsr_storage_id (FK)      ││
│                                                         │  ├─ product_id (FK)          ││
│                                                         │  ├─ variant_id (FK)            ││
│                                                         │  ├─ quantity                 ││
│                                                         │  └─ uom_id (FK)              ││
│                                                         └──────────────────────────────┘│
│                                                                                         │
│  ┌──────────────────────────────┐                                                      │
│  │  DSRStockTransfer            │◀────── Tracks inventory movement                    │
│  │  ├─ transfer_id (PK)         │         between StorageLocation <-> DSRStorage      │
│  │  ├─ source_location_id (FK)  │                                                      │
│  │  ├─ source_dsr_storage_id    │                                                      │
│  │  ├─ target_location_id (FK)  │                                                      │
│  │  ├─ target_dsr_storage_id    │                                                      │
│  │  └─ transfer_code            │                                                      │
│  └──────────────────────────────┘                                                      │
│           │ 1:N                                                                          │
│           ▼                                                                              │
│  ┌──────────────────────────────┐                                                      │
│  │  DSRStockTransferDetail      │                                                      │
│  │  ├─ product_id, variant_id   │                                                      │
│  │  └─ quantity                 │                                                      │
│  └──────────────────────────────┘                                                      │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘

RELATIONSHIP SUMMARY:
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ Entity A                    │ Relationship │ Entity B              │ Cardinality          │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ AppClientCompany            │ owns         │ DeliverySalesRep      │ 1:N (company_id FK)  │
│ DeliverySalesRepresentative │ has          │ DSRStorage            │ 1:1 (unique dsr_id)  │
│ DeliverySalesRepresentative │ receives     │ DSRSOAssignment       │ 1:N (dsr_id FK)      │
│ DeliverySalesRepresentative │ receives     │ DSRPaymentSettlement  │ 1:N (dsr_id FK)      │
│ DeliverySalesRepresentative │ linked to    │ User                  │ 1:1 via user.dsr_id  │
│ DSRSOAssignment             │ assigned to  │ SalesOrder            │ N:1 (sales_order_id) │
│ DSRSOAssignment             │ for customer │ Customer              │ N:1 (customer_id)    │
│ DSRStorage                  │ holds        │ DSRInventoryStock     │ 1:N (dsr_storage_id) │
│ DSRInventoryStock           │ tracks       │ Product               │ N:1 (product_id)     │
│ DSRInventoryStock           │ tracks       │ ProductVariant        │ N:1 (variant_id)     │
│ DSRStockTransfer            │ moves from   │ StorageLocation       │ N:1 (source)         │
│ DSRStockTransfer            │ moves to     │ StorageLocation       │ N:1 (target)         │
│ DSRStockTransfer            │ moves from   │ DSRStorage            │ N:1 (source)         │
│ DSRStockTransfer            │ moves to     │ DSRStorage            │ N:1 (target)         │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Entity Inventory

### 2.1 Core DSR Entities

#### 2.1.1 DeliverySalesRepresentative

**Location:** `app/models/sales.py`

**Purpose:** Represents a delivery sales representative who handles order fulfillment, customer deliveries, and payment collection.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `dsr_id` | `Integer` | PK, Auto-increment | Unique identifier |
| `dsr_name` | `String(200)` | Not null | Full name of the DSR |
| `dsr_code` | `String(50)` | Not null, Unique | Employee/identification code |
| `contact_email` | `String(100)` | Nullable | Business email address |
| `contact_phone` | `String(20)` | Nullable | Contact phone number |
| `payment_on_hand` | `Numeric(18,4)` | Default: 0 | Cash held by DSR from collections |
| `commission_amount` | `Numeric(18,4)` | Default: 0 | Current commission balance |
| `is_active` | `Boolean` | Default: True | Whether DSR can receive assignments |
| `company_id` | `Integer` | FK → AppClientCompany | Multi-tenant isolation |
| `cb` | `Integer` | Not null | Created by user ID |
| `cd` | `TIMESTAMP` | Default: now() | Creation timestamp |
| `mb` | `Integer` | Not null | Modified by user ID |
| `md` | `TIMESTAMP` | Default: now() | Modification timestamp |
| `is_deleted` | `Boolean` | Default: False | Soft delete flag |

**Relationships:**
- `dsr_storage` → `DSRStorage` (1:1, back_populates="dsr")
- `so_assignments` → `DSRSOAssignment[]` (1:N, back_populates="dsr")
- `payment_settlements` → `DSRPaymentSettlement[]` (1:N)
- `company` → `AppClientCompany` (N:1)

**Indexes:**
- `idx_dsr_company_id` on `company_id`
- `idx_dsr_code` on `dsr_code`

---

#### 2.1.2 DSRSOAssignment

**Location:** `app/models/sales.py`

**Purpose:** Links Sales Orders to DSRs for delivery fulfillment with tracking for loading, delivery, and payment statuses.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `assignment_id` | `Integer` | PK, Auto-increment | Unique identifier |
| `dsr_id` | `Integer` | FK, Not null | Assigned DSR |
| `sales_order_id` | `Integer` | FK, Not null, Unique | Linked sales order |
| `customer_id` | `Integer` | FK, Not null | Customer for delivery |
| `assignment_status` | `String(20)` | Default: 'assigned' | assigned, in_progress, completed, cancelled |
| `loading_status` | `String(20)` | Default: 'not_loaded' | not_loaded, partially_loaded, fully_loaded |
| `delivery_status` | `String(20)` | Default: 'Pending' | Pending, Delivered, Partial |
| `payment_status` | `String(20)` | Default: 'Unpaid' | Unpaid, Paid, Partial |
| `amount_paid` | `Numeric(18,4)` | Default: 0 | Amount collected by DSR |
| `assigned_date` | `TIMESTAMP` | Not null | When assignment was created |
| `target_delivery_date` | `TIMESTAMP` | Nullable | Scheduled delivery date |
| `completion_date` | `TIMESTAMP` | Nullable | When fully delivered/paid |
| `notes` | `Text` | Nullable | Internal notes |
| `company_id` | `Integer` | FK, Not null | Multi-tenant |
| `cb`, `cd`, `mb`, `md` | Audit fields | Standard timestamps | Audit trail |
| `is_deleted` | `Boolean` | Default: False | Soft delete |

**Relationships:**
- `dsr` → `DeliverySalesRepresentative` (N:1)
- `sales_order` → `SalesOrder` (N:1)
- `customer` → `Customer` (N:1)
- `company` → `AppClientCompany` (N:1)
- `batch_allocations` → `DSRBatchAllocation[]` (1:N)

**Constraints:**
- Unique constraint on `sales_order_id` (one assignment per order)

---

#### 2.1.3 DSRPaymentSettlement

**Location:** `app/models/sales.py`

**Purpose:** Records payments collected from DSRs when they deposit cash held from customer collections.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `settlement_id` | `Integer` | PK, Auto-increment | Unique identifier |
| `dsr_id` | `Integer` | FK, Not null | DSR making settlement |
| `amount` | `Numeric(18,4)` | Not null, ≥0 | Amount being deposited |
| `payment_method` | `String(50)` | Nullable | cash, bank_transfer, check, etc. |
| `reference_number` | `String(100)` | Nullable | Transaction/cheque reference |
| `settlement_date` | `TIMESTAMP` | Not null | When settlement occurred |
| `notes` | `String(500)` | Nullable | Additional information |
| `company_id` | `Integer` | FK, Not null | Multi-tenant |
| `cb`, `cd`, `mb`, `md` | Audit fields | Standard timestamps | Audit trail |
| `is_deleted` | `Boolean` | Default: False | Soft delete |

**Relationships:**
- `dsr` → `DeliverySalesRepresentative` (N:1)
- `company` → `AppClientCompany` (N:1)

---

### 2.2 DSR Storage & Inventory Entities

#### 2.2.1 DSRStorage

**Location:** `app/models/warehouse.py`

**Purpose:** Represents a storage location (van, shop, warehouse) assigned to a single DSR for holding inventory.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `dsr_storage_id` | `Integer` | PK, Auto-increment | Unique identifier |
| `dsr_id` | `Integer` | FK, Not null, Unique | Linked DSR (1:1) |
| `storage_name` | `String(100)` | Not null | Display name |
| `storage_code` | `String(50)` | Not null | Unique code |
| `storage_type` | `String(20)` | Not null | vehicle, shop, warehouse, other |
| `max_capacity` | `Integer` | Nullable | Maximum item capacity |
| `is_active` | `Boolean` | Default: True | Whether storage is usable |
| `company_id` | `Integer` | FK, Not null | Multi-tenant |
| `cb`, `cd`, `mb`, `md` | Audit fields | Standard timestamps | Audit trail |
| `is_deleted` | `Boolean` | Default: False | Soft delete |

**Relationships:**
- `dsr` → `DeliverySalesRepresentative` (1:1, back_populates="dsr_storage")
- `inventory_stocks` → `DSRInventoryStock[]` (1:N)
- `company` → `AppClientCompany` (N:1)

**Constraints:**
- `uq_dsr_storage_dsr_id` - One storage per DSR
- `idx_dsr_storage_code` - Index on storage_code

---

#### 2.2.2 DSRInventoryStock

**Location:** `app/models/warehouse.py`

**Purpose:** Tracks product inventory held in DSR storages separately from main warehouse inventory.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `stock_id` | `Integer` | PK, Auto-increment | Unique identifier |
| `product_id` | `Integer` | FK, Not null | Linked product |
| `variant_id` | `Integer` | FK, Nullable | Product variant (optional) |
| `dsr_storage_id` | `Integer` | FK, Not null | Storage location |
| `quantity` | `Numeric(18,4)` | Not null | Current stock quantity |
| `last_stock_take_date` | `TIMESTAMP` | Nullable | Last physical count |
| `uom_id` | `Integer` | FK, Nullable | Unit of measure |
| `cb`, `cd`, `mb`, `md` | Audit fields | Standard timestamps | Audit trail |
| `is_deleted` | `Boolean` | Default: False | Soft delete |

**Relationships:**
- `product` → `Product` (N:1)
- `variant` → `ProductVariant` (N:1)
- `dsr_storage` → `DSRStorage` (N:1)
- `uom` → `UnitOfMeasure` (N:1)

**Indexes:**
- `idx_dsr_inventory_stock_product_variant_storage` - Composite index for lookups

---

#### 2.2.3 DSRStockTransfer

**Location:** `app/models/warehouse.py`

**Purpose:** Records inventory movements between StorageLocations and DSRStorages (loading/unloading vans).

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `transfer_id` | `Integer` | PK, Auto-increment | Unique identifier |
| `transfer_code` | `String(50)` | Unique, Not null | Reference code |
| `transfer_date` | `TIMESTAMP` | Not null | When transfer occurred |
| `status` | `String(20)` | Default: 'COMPLETED' | Transfer status |
| `source_location_id` | `Integer` | FK, Nullable | Source warehouse location |
| `source_dsr_storage_id` | `Integer` | FK, Nullable | Source DSR storage |
| `target_location_id` | `Integer` | FK, Nullable | Target warehouse location |
| `target_dsr_storage_id` | `Integer` | FK, Nullable | Target DSR storage |
| `notes` | `Text` | Nullable | Transfer notes |
| `company_id` | `Integer` | FK, Not null | Multi-tenant |
| `cb`, `cd`, `mb`, `md` | Audit fields | Standard timestamps | Audit trail |
| `is_deleted` | `Boolean` | Default: False | Soft delete |

**Constraints:**
- Mutually exclusive: source must be location XOR dsr_storage
- Mutually exclusive: target must be location XOR dsr_storage

**Indexes:**
- `idx_dsr_stock_transfer_code`, `idx_dsr_stock_transfer_date`
- Source/target indexes for queries

---

#### 2.2.4 DSRStockTransferDetail

**Location:** `app/models/warehouse.py`

**Purpose:** Line items for stock transfers - products moved in each transfer.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `detail_id` | `Integer` | PK, Auto-increment | Unique identifier |
| `transfer_id` | `Integer` | FK, Not null | Parent transfer |
| `product_id` | `Integer` | FK, Not null | Product moved |
| `variant_id` | `Integer` | FK, Nullable | Variant moved |
| `quantity` | `Numeric(18,4)` | Not null | Amount transferred |
| `notes` | `Text` | Nullable | Line item notes |
| `cb`, `cd`, `mb`, `md` | Audit fields | Standard timestamps | Audit trail |
| `is_deleted` | `Boolean` | Default: False | Soft delete |

**Relationships:**
- `transfer` → `DSRStockTransfer` (N:1, cascade delete)
- `product` → `Product` (N:1)
- `variant` → `ProductVariant` (N:1)

---

## 3. Backend Operations Reference

### 3.1 Delivery Sales Representative Operations

#### 3.1.1 CRUD Operations

| Operation | HTTP Method | Endpoint | Service Method | Description | Status |
|-----------|-------------|----------|----------------|-------------|--------|
| **List** | `GET` | `/api/company/sales/dsr/` | `list_dsr()` | Paginated list with filters | ✅ Complete |
| **Get** | `GET` | `/api/company/sales/dsr/{dsr_id}` | `get_dsr()` | Single DSR by ID | ✅ Complete |
| **Create** | `POST` | `/api/company/sales/dsr/` | `create_dsr()` | Create new DSR | ✅ Complete |
| **Update** | `PATCH` | `/api/company/sales/dsr/{dsr_id}` | `update_dsr()` | Partial update | ✅ Complete |
| **Delete** | `DELETE` | `/api/company/sales/dsr/{dsr_id}` | `delete_dsr()` | Soft delete with stock check | ✅ Complete |

#### 3.1.2 Special Operations

| Operation | HTTP Method | Endpoint | Service Method | Description | Status |
|-----------|-------------|----------|----------------|-------------|--------|
| **Update Payment** | `PATCH` | `/api/company/sales/dsr/{dsr_id}/payment-on-hand` | `update_payment_on_hand()` | Adjust cash on hand | ✅ Complete |
| **Check Code** | `GET` | `/api/company/sales/dsr/check-code/{code}` | `check_dsr_code_exists()` | Validate code uniqueness | ✅ Complete |
| **Get Summary** | `GET` | `/api/company/sales/dsr/{dsr_id}/summary` | `get_dsr_summary()` | Assignment/settlement summary | ✅ Complete |

**Service Layer Details (`app/services/dsr/delivery_sales_representative_service.py`):**

```python
class DeliverySalesRepresentativeService:
    # Core CRUD
    def list_dsr(self, company_id, filters, pagination) -> PaginatedResult
    def get_dsr(self, dsr_id: int) -> DeliverySalesRepresentative | None
    def create_dsr(self, data: DeliverySalesRepresentativeCreate, user_id: int, company_id: int)
    def update_dsr(self, dsr_id: int, data: DeliverySalesRepresentativeUpdate, user_id: int, company_id: int)
    
    # Delete with validation - checks for existing inventory stock
    def delete_dsr(self, dsr_id: int, company_id: int) -> bool
    
    # Special operations
    def update_payment_on_hand(self, dsr_id: int, amount: Decimal, user_id: int, company_id: int)
    def check_dsr_code_exists(self, code: str, company_id: int, exclude_id: int | None) -> bool
```

**Delete Validation Logic:**
```python
# Cannot delete DSR if they have inventory stock
def delete_dsr(self, dsr_id: int, company_id: int) -> bool:
    dsr = self.get_dsr(dsr_id)
    if not dsr or dsr.company_id != company_id:
        return False
    
    # Check for existing DSRInventoryStock records
    has_stock = self.db.query(DSRInventoryStock).filter(
        DSRInventoryStock.dsr_storage.has(dsr_id=dsr_id),
        DSRInventoryStock.is_deleted == False
    ).first()
    
    if has_stock:
        raise HTTPException(400, "Cannot delete DSR with existing inventory stock")
    
    # Soft delete
    dsr.is_deleted = True
    dsr.md = datetime.now()
    self.db.commit()
    return True
```

---

### 3.2 DSR SO Assignment Operations

#### 3.2.1 CRUD Operations

| Operation | HTTP Method | Endpoint | Service Method | Description | Status |
|-----------|-------------|----------|----------------|-------------|--------|
| **List** | `GET` | `/api/company/sales/dsr/so-assignments/` | `list_assignments()` | Paginated with filters | ✅ Complete |
| **Get** | `GET` | `/api/company/sales/dsr/so-assignments/{id}` | `get_assignment()` | Single assignment | ✅ Complete |
| **Create** | `POST` | `/api/company/sales/dsr/so-assignments/` | `create_assignment()` | Assign SO to DSR | ✅ Complete |
| **Update** | `PATCH` | `/api/company/sales/dsr/so-assignments/{id}` | `update_assignment()` | Update assignment | ✅ Complete |
| **Delete** | `DELETE` | `/api/company/sales/dsr/so-assignments/{id}` | `delete_assignment()` | Remove assignment | ✅ Complete |

#### 3.2.2 Business Operations

| Operation | HTTP Method | Endpoint | Service Method | Description | Status |
|-----------|-------------|----------|----------------|-------------|--------|
| **Mark Delivered** | `POST` | `/api/company/sales/dsr/so-assignments/{id}/mark-delivered` | `mark_delivered()` | Record delivery | ✅ Complete |
| **Collect Payment** | `POST` | `/api/company/sales/dsr/so-assignments/{id}/collect-payment` | `collect_payment()` | Record partial/full payment | ✅ Complete |
| **Load SO** | `POST` | `/api/company/sales/dsr/so-assignments/{id}/load-so` | `load_sales_order()` | Transfer stock to DSR | ✅ Complete |
| **Unload SO** | `POST` | `/api/company/sales/dsr/so-assignments/{id}/unload-so` | `unload_sales_order()` | Return stock to warehouse | ✅ Complete |
| **Batch Delivery** | `POST` | `/api/company/sales/dsr/so-assignments/batch-deliver` | `process_batch_delivery()` | Multi-order delivery | ✅ Complete |

**Service Layer Details (`app/services/dsr/dsr_so_assignment_service.py`):**

```python
class DSRSOAssignmentService:
    # Core CRUD
    def list_assignments(self, company_id, filters, pagination) -> dict
    def get_assignment(self, assignment_id: int) -> DSRSOAssignment | None
    
    # Create with validation
    def create_assignment(self, data: DSRSOAssignmentCreate, user_id: int, company_id: int)
    
    # Update with status transitions
    def update_assignment(self, assignment_id: int, data: DSRSOAssignmentUpdate, user_id: int, company_id: int)
    
    # Delete with restrictions
    def delete_assignment(self, assignment_id: int, company_id: int, user_id: int) -> bool
    
    # Business operations
    def mark_delivered(self, assignment_id: int, data: DeliveryRequest, user_id: int, company_id: int)
    def collect_payment(self, assignment_id: int, data: PaymentCollectionRequest, user_id: int, company_id: int)
    
    # Inventory operations with batch tracking
    def load_sales_order(self, assignment_id: int, user_id: int, company_id: int, notes: str | None)
    def unload_sales_order(self, assignment_id: int, user_id: int, company_id: int, notes: str | None)
    
    # Batch processing
    def process_batch_delivery(self, batch_data: DeliveryBatchRequest, user_id: int, company_id: int)
```

**Load Sales Order Logic (Inventory Transfer):**
```python
def load_sales_order(self, assignment_id: int, user_id: int, company_id: int, notes: str | None):
    """
    Transfers inventory from warehouse to DSR storage:
    1. Validate assignment exists and is assigned
    2. Get DSR's storage location
    3. Get SO details with batch information
    4. For each batch allocation:
       - Reduce InventoryStock at source location
       - Create InventoryMovement (OUT)
       - Increase DSRInventoryStock at DSR storage
       - Create InventoryMovement (IN)
    5. Create DSRStockTransfer record
    6. Update assignment.loading_status = 'fully_loaded'
    7. Update sales_order.order_status = 'shipped'
    """
```

---

### 3.3 DSR Payment Settlement Operations

#### 3.3.1 CRUD Operations

| Operation | HTTP Method | Endpoint | Service Method | Description | Status |
|-----------|-------------|----------|----------------|-------------|--------|
| **List** | `GET` | `/api/company/sales/dsr/settlements/` | `list_settlements()` | Paginated with filters | ✅ Complete |
| **Create** | `POST` | `/api/company/sales/dsr/settlements/` | `create_settlement()` | Record new settlement | ✅ Complete |
| **DSR Summary** | `GET` | `/api/company/sales/dsr/settlements/summary/{dsr_id}` | `get_dsr_summary()` | Settlement totals | ✅ Complete |

**Service Layer Details (`app/services/dsr/dsr_payment_settlement_service.py`):**

```python
class DSRPaymentSettlementService:
    def list_settlements(self, company_id, dsr_id, date_range, pagination) -> dict
    
    # Creates settlement with optimistic locking and balance update
    def create_settlement(self, data: DSRPaymentSettlementCreate, user_id: int, company_id: int)
    
    def get_dsr_summary(self, dsr_id: int, company_id: int) -> dict
```

**Settlement Creation with Optimistic Locking:**
```python
def create_settlement(self, data, user_id, company_id):
    # 1. Lock DSR record for update (prevents race conditions)
    dsr = self.db.query(DeliverySalesRepresentative)\
        .filter_by(dsr_id=data.dsr_id, company_id=company_id)\
        .with_for_update()\
        .first()
    
    # 2. Validation checks
    if not dsr.is_active:
        raise HTTPException(400, "Cannot settle for inactive DSR")
    
    if data.reference_number:
        # Check reference uniqueness within company
        existing = self.db.query(DSRPaymentSettlement)\
            .filter_by(reference_number=data.reference_number, company_id=company_id)\
            .first()
        if existing:
            raise HTTPException(400, "Reference number already exists")
    
    # 3. Validate amount
    current_on_hand = dsr.payment_on_hand or Decimal("0")
    if data.amount > current_on_hand:
        raise HTTPException(400, 
            f"Settlement amount ({data.amount}) exceeds payment on hand ({current_on_hand})")
    
    # 4. Create settlement record
    settlement = DSRPaymentSettlement(...)
    self.repo.create(settlement)
    
    # 5. Reduce DSR payment_on_hand
    dsr.payment_on_hand = current_on_hand - data.amount
    dsr.mb = user_id
    
    # 6. Commit (releases lock)
    self.db.commit()
```

---

### 3.4 DSR Storage Operations

#### 3.4.1 CRUD Operations

| Operation | HTTP Method | Endpoint | Service Method | Description | Status |
|-----------|-------------|----------|----------------|-------------|--------|
| **List** | `GET` | `/api/company/warehouse/dsr-storage/` | `list_dsr_storages()` | Paginated with filters | ✅ Complete |
| **Get** | `GET` | `/api/company/warehouse/dsr-storage/{id}` | `get_dsr_storage()` | Single storage | ✅ Complete |
| **Get by DSR** | `GET` | `/api/company/warehouse/dsr-storage/by-dsr/{dsr_id}` | `get_dsr_storage_by_dsr()` | Storage for specific DSR | ✅ Complete |
| **Create** | `POST` | `/api/company/warehouse/dsr-storage/` | `create_dsr_storage()` | Create storage | ✅ Complete |
| **Update** | `PATCH` | `/api/company/warehouse/dsr-storage/{id}` | `update_dsr_storage()` | Partial update | ✅ Complete |
| **Delete** | `DELETE` | `/api/company/warehouse/dsr-storage/{id}` | `delete_dsr_storage()` | Soft delete | ✅ Complete |

**Service Layer Details (`app/services/warehouse/dsr_storage.py`):**

```python
class DSRStorageService:
    def list_dsr_storages(self, company_id, filters, pagination) -> dict
    def get_dsr_storage(self, dsr_storage_id: int, company_id: int) -> DSRStorage
    def get_dsr_storage_by_dsr(self, dsr_id: int, company_id: int) -> DSRStorage
    
    # Create enforces one storage per DSR
    def create_dsr_storage(self, data: DSRStorageCreate, user_id: int)
    
    def update_dsr_storage(self, storage_id: int, data: DSRStorageUpdate, 
                          user_id: int, company_id: int)
    
    # Delete prevents removal if stock exists
    def delete_dsr_storage(self, dsr_storage_id: int, company_id: int) -> bool
```

---

### 3.5 DSR Inventory Stock Operations

| Operation | HTTP Method | Endpoint | Service Method | Description | Status |
|-----------|-------------|----------|----------------|-------------|--------|
| **List by Storage** | `GET` | `/api/company/warehouse/dsr-inventory-stock/by-storage/{storage_id}` | `get_by_storage()` | Stock for specific storage | ✅ Complete |
| **List by DSR** | `GET` | `/api/company/warehouse/dsr-inventory-stock/by-dsr/{dsr_id}` | `get_by_dsr()` | Stock for DSR | ✅ Complete |
| **My Stock** | `GET` | `/api/company/warehouse/dsr-inventory-stock/my-stock` | `get_my_stock()` | Current user's DSR stock | ✅ Complete |
| **Search** | `GET` | `/api/company/warehouse/dsr-inventory-stock/search` | `search_stock()` | Search by product name | ✅ Complete |

---

## 4. Frontend UI Walkthrough

### 4.1 Page Inventory

| Page | File Path | Purpose | User Role | Status |
|------|-----------|---------|-----------|--------|
| **DSR List** | `src/pages/dsr/DeliverySalesRepresentatives.tsx` | Manage DSRs (CRUD) | Admin/Sales Manager | ✅ Complete |
| **SO Assignments** | `src/pages/dsr/DSRSOAssignments.tsx` | Assign orders to DSRs | Admin/Sales Manager | ✅ Complete |
| **My Assignments** | `src/pages/dsr/DSRMyAssignments.tsx` | DSR's assigned orders | DSR Only | ✅ Complete |
| **Settlement History** | `src/pages/dsr/DSRSettlementHistory.tsx` | View all settlements | Admin/Sales Manager | ✅ Complete |
| **DSR Storages** | `src/pages/dsr/DSRStorages.tsx` | Manage DSR storages | Admin/Sales Manager | ✅ Complete |
| **My Inventory** | `src/pages/dsr/DSRInventoryStock.tsx` | DSR's current stock | DSR Only | ✅ Complete |

### 4.2 Forms & Modals

| Form | File Path | Purpose | Used By | Status |
|------|-----------|---------|---------|--------|
| **DSRForm** | `src/components/forms/DSRForm.tsx` | Create/edit DSR | DSR List | ✅ Complete |
| **DSRStorageForm** | `src/components/forms/DSRStorageForm.tsx` | Create/edit storage | DSR Storages | ✅ Complete |
| **DSRAssignmentForm** | `src/components/forms/DSRAssignmentForm.tsx` | Assign SO to DSR | SO Assignments | ✅ Complete |
| **DSRSettlementForm** | `src/components/forms/DSRSettlementForm.tsx` | Record settlement | DSR List | ✅ Complete |
| **DSRPaymentForm** | `src/components/forms/DSRPaymentForm.tsx` | Collect payment | My Assignments | ✅ Complete |
| **UnifiedDeliveryForm** | `src/components/forms/UnifiedDeliveryForm.tsx` | Mark delivered | My Assignments | ✅ Complete |
| **DSRLoadingModal** | `src/components/modals/DSRLoadingModal.tsx` | Load/unload UI | My Assignments | ✅ Complete |
| **DSRSOBreakdownModal** | `src/components/modals/DSRSOBreakdownModal.tsx` | Batch breakdown | SO Assignments | ✅ Complete |

### 4.3 Shared Components

| Component | File Path | Purpose | Status |
|-----------|-----------|---------|--------|
| **DSRSettlementFilter** | `src/components/DSRSettlementFilter.tsx` | Filter settlements by DSR/date | ✅ Complete |
| **ViewOrderDetails** | `src/components/shared/ViewOrderDetails.tsx` | Display order details dialog | ✅ Complete |
| **OrderStatus** | `src/components/shared/OrderStatus.tsx` | Status badge component | ✅ Complete |
| **ConfirmDeleteDialog** | `src/components/shared/ConfirmDeleteDialog.tsx` | Delete confirmation | ✅ Complete |
| **VariantDisplay** | `src/components/shared/VariantDisplay.tsx` | Product variant display | ✅ Complete |

### 4.4 API Layer (Frontend)

**DSR Core API (`src/lib/api/dsrApi.ts`):**

```typescript
// DSR CRUD
export const getDSRs = (start?: number, limit?: number, params?: FilterParams): Promise<DSRResponse>
export const getDSR = (dsrId: number): Promise<DSR>
export const createDSR = (dsr: InsertDSR): Promise<DSR>
export const updateDSR = (dsrId: number, dsr: Partial<InsertDSR>): Promise<DSR>
export const deleteDSR = (dsrId: number): Promise<void>

// Special operations
export const updateDSRPaymentOnHand = (dsrId: number, amount: number): Promise<DSR>
export const getDSRSummary = (dsrId: number): Promise<DSRSummary>

// DSR SO Assignment
export const getDSRSOAssignments = (start?: number, limit?: number, params?: FilterParams): Promise<DSRSOAssignmentResponse>
export const createDSRSOAssignment = (assignment: InsertDSRSOAssignment): Promise<DSRSOAssignment>
export const updateDSRSOAssignment = (id: number, assignment: Partial<InsertDSRSOAssignment>): Promise<DSRSOAssignment>
export const deleteDSRSOAssignment = (id: number): Promise<void>

// Business operations
export const collectPayment = (assignmentId: number, data: PaymentCollectionData): Promise<PaymentResult>
export const markDelivered = (assignmentId: number, data: DeliveryData): Promise<DeliveryResult>
export const loadSalesOrder = (assignmentId: number, data: LoadUnloadData): Promise<LoadUnloadResult>
export const unloadSalesOrder = (assignmentId: number, data: LoadUnloadData): Promise<LoadUnloadResult>
export const processBatchDelivery = (batchData: BatchDeliveryData): Promise<BatchResult>
```

**DSR Storage API (`src/lib/api/dsrStorageApi.ts`):**

```typescript
export const getDSRStorages = (start?: number, limit?: number, params?: FilterParams): Promise<DSRStorageResponse>
export const getDSRStorage = (id: number): Promise<DSRStorage>
export const getDSRStorageByDSR = (dsrId: number): Promise<DSRStorage>
export const createDSRStorage = (storage: InsertDSRStorage): Promise<DSRStorage>
export const updateDSRStorage = (id: number, storage: Partial<InsertDSRStorage>): Promise<DSRStorage>
export const deleteDSRStorage = (id: number): Promise<void>
```

**DSR Settlement API (`src/lib/api/dsrSettlementApi.ts`):**

```typescript
export const getDSRSettlements = (start?: number, limit?: number, params?: FilterParams): Promise<DSRPaymentSettlementResponse>
export const createDSRSettlement = (settlement: InsertDSRPaymentSettlement): Promise<DSRPaymentSettlement>
export const getDSRSettlementSummary = (dsrId: number): Promise<DSRSettlementSummary>
```

**DSR Inventory Stock API (`src/lib/api/dsrInventoryStockApi.ts`):**

```typescript
export const getMyDSRInventoryStock = (start?: number, limit?: number, params?: FilterParams): Promise<DSRInventoryStockResponse>
export const getDSRInventoryStockByStorage = (storageId: number, params?: FilterParams): Promise<DSRInventoryStockResponse>
export const searchDSRInventoryStock = (searchTerm: string, params?: FilterParams): Promise<DSRInventoryStockResponse>
```

### 4.5 Types & Schemas

**DSR Core Schema (`src/lib/schema/dsr.ts`):**

```typescript
// Base DSR
export type DSR = {
  dsr_id: number
  dsr_name: string
  dsr_code: string
  contact_email: string | null
  contact_phone: string | null
  payment_on_hand: number
  commission_amount: number
  is_active: boolean
  company_id: number
  company_name: string | null
  has_storage: boolean | null
  cb: number
  cd: string
  mb: number
  md: string
}

// DSR SO Assignment
export type DSRSOAssignment = {
  assignment_id: number
  dsr_id: number
  dsr_name: string | null
  sales_order_id: number
  order_number: string | null
  customer_id: number
  customer_name: string | null
  assignment_status: string
  loading_status: string
  delivery_status: string | null
  payment_status: string | null
  amount_paid: number | null
  assigned_date: string
  target_delivery_date: string | null
  completion_date: string | null
  is_loaded: boolean | null
  effective_total_amount: number | null
  location_name: string | null
}

// Validation schemas (Zod)
export const insertDSRSchema = z.object({
  dsr_name: z.string().min(1).max(200),
  dsr_code: z.string().min(1).max(50),
  contact_email: z.string().email().optional(),
  contact_phone: z.string().max(20).optional(),
  is_active: z.boolean().default(true)
})
```

---

## 5. Interconnected Workflows

### 5.1 DSR Creation Workflow

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              DSR CREATION WORKFLOW                                      │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│  USER (Admin)                                                                           │
│     │                                                                                   │
│     ▼                                                                                   │
│  ┌──────────────────────────────────┐                                                   │
│  │ 1. Navigate to DSR List Page     │  ◀── src/pages/dsr/DeliverySalesRepresentatives.tsx │
│  └──────────────────────────────────┘                                                   │
│     │                                                                                   │
│     ▼                                                                                   │
│  ┌──────────────────────────────────┐                                                   │
│  │ 2. Click "Add New DSR" Button    │                                                   │
│  └──────────────────────────────────┘                                                   │
│     │                                                                                   │
│     ▼                                                                                   │
│  ┌──────────────────────────────────┐                                                   │
│  │ 3. DSRForm Modal Opens           │  ◀── src/components/forms/DSRForm.tsx             │
│  │    - Enter dsr_name              │         Zod validation: insertDSRSchema            │
│  │    - Enter dsr_code (unique)     │                                                   │
│  │    - Optional: email, phone      │                                                   │
│  └──────────────────────────────────┘                                                   │
│     │                                                                                   │
│     ▼                                                                                   │
│  ┌──────────────────────────────────┐                                                   │
│  │ 4. Frontend Validation (Zod)     │                                                   │
│  │    - Required fields check     │                                                   │
│  │    - Email format validation   │                                                   │
│  │    - Max length constraints    │                                                   │
│  └──────────────────────────────────┘                                                   │
│     │                                                                                   │
│     ▼                                                                                   │
│  ┌──────────────────────────────────┐                                                   │
│  │ 5. API Call: createDSR()         │  ◀── src/lib/api/dsrApi.ts                        │
│  │    POST /api/company/sales/dsr/  │                                                   │
│  └──────────────────────────────────┘                                                   │
│     │                                                                                   │
│     ▼                                                                                   │
│  BACKEND (FastAPI)                                                                      │
│  ┌──────────────────────────────────┐                                                   │
│  │ 6. Endpoint Handler              │  ◀── app/api/dsr/delivery_sales_representative.py│
│  │    - Parse DeliverySalesRepresentativeCreate schema                               │
│  │    - Inject company_id from auth │                                                   │
│  └──────────────────────────────────┘                                                   │
│     │                                                                                   │
│     ▼                                                                                   │
│  ┌──────────────────────────────────┐                                                   │
│  │ 7. Service Layer                 │  ◀── app/services/dsr/delivery_sales_representative_service.py
│  │    - Check dsr_code uniqueness   │         Within company scope                     │
│  │    - Create DSR record             │                                                   │
│  └──────────────────────────────────┘                                                   │
│     │                                                                                   │
│     ▼                                                                                   │
│  DATABASE (PostgreSQL)                                                                  │
│  ┌──────────────────────────────────┐                                                   │
│  │ 8. Insert Record                 │  ◀── sales.delivery_sales_representative table    │
│  │    - Set cb/cd/mb/md timestamps  │                                                   │
│  │    - is_deleted = false          │                                                   │
│  │    - is_active = true            │                                                   │
│  └──────────────────────────────────┘                                                   │
│     │                                                                                   │
│     ▼                                                                                   │
│  RESPONSE                                                                               │
│  ┌──────────────────────────────────┐                                                   │
│  │ 9. Return DSRRead schema         │  ◀── With joined company_name                      │
│  └──────────────────────────────────┘                                                   │
│     │                                                                                   │
│     ▼                                                                                   │
│  FRONTEND                                                                               │
│  ┌──────────────────────────────────┐                                                   │
│  │ 10. Invalidate cache & refetch   │  ◀── queryClient.invalidateQueries(['/dsr'])      │
│  │     Close modal, show success    │         toast.success("DSR created")               │
│  └──────────────────────────────────┘                                                   │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

### 5.2 Sales Order Assignment Workflow

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                         SALES ORDER ASSIGNMENT WORKFLOW                                 │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│  PREREQUISITES:                                                                         │
│  ✅ SalesOrder exists with status = 'pending'                                           │
│  ✅ DSR exists and is_active = true                                                   │
│  ✅ SalesOrder has StorageLocation with available stock                                 │
│                                                                                         │
│  USER (Sales Manager)                                                                   │
│     │                                                                                   │
│     ▼                                                                                   │
│  ┌──────────────────────────────────┐                                                   │
│  │ 1. Navigate to SO Assignments    │  ◀── src/pages/dsr/DSRSOAssignments.tsx           │
│  └──────────────────────────────────┘                                                   │
│     │                                                                                   │
│     ▼                                                                                   │
│  ┌──────────────────────────────────┐                                                   │
│  │ 2. Click "Assign Order"          │                                                   │
│  └──────────────────────────────────┘                                                   │
│     │                                                                                   │
│     ▼                                                                                   │
│  ┌──────────────────────────────────┐                                                   │
│  │ 3. DSRAssignmentForm Modal       │  ◀── src/components/forms/DSRAssignmentForm.tsx │
│  │    - Select DSR (dropdown)       │         Fetches available DSRs                   │
│  │    - Select Sales Order          │         Validates order not already assigned       │
│  │    - Select/confirm Customer     │                                                   │
│  │    - Optional: target date       │                                                   │
│  └──────────────────────────────────┘                                                   │
│     │                                                                                   │
│     ▼                                                                                   │
│  ┌──────────────────────────────────┐                                                   │
│  │ 4. API Call: createDSRSOAssignment│  ◀── src/lib/api/dsrApi.ts                       │
│  │    POST /api/company/sales/dsr/so-assignments/                                       │
│  └──────────────────────────────────┘                                                   │
│     │                                                                                   │
│     ▼                                                                                   │
│  BACKEND VALIDATION                                                                     │
│  ┌──────────────────────────────────┐                                                   │
│  │ 5. Service Layer Checks          │  ◀── DSRSOAssignmentService.create_assignment()   │
│  │    ✓ DSR exists and is active    │                                                   │
│  │    ✓ SalesOrder exists           │                                                   │
│  │    ✓ SalesOrder not already      │         Unique constraint on sales_order_id     │
│  │      assigned                      │                                                   │
│  │    ✓ Customer match              │         SalesOrder.customer_id == provided        │
│  │    ✓ Company scope match         │                                                   │
│  └──────────────────────────────────┘                                                   │
│     │                                                                                   │
│     ▼                                                                                   │
│  DATABASE INSERT                                                                        │
│  ┌──────────────────────────────────┐                                                   │
│  │ 6. Create Assignment Record      │  ◀── sales.dsr_so_assignment table               │
│  │    - dsr_id = selected DSR       │                                                   │
│  │    - sales_order_id = order      │                                                   │
│  │    - assignment_status =         │                                                   │
│  │      'assigned'                  │                                                   │
│  │    - loading_status =            │                                                   │
│  │      'not_loaded'                │                                                   │
│  │    - delivery/payment status     │         Default: 'Pending'/'Unpaid'             │
│  └──────────────────────────────────┘                                                   │
│     │                                                                                   │
│     ▼                                                                                   │
│  FRONTEND UPDATE                                                                        │
│  ┌──────────────────────────────────┐                                                   │
│  │ 7. Table Refreshes               │  ◀── Assignment appears in list                   │
│  │    - Order number linkable       │         Click → ViewOrderDetails                  │
│  │    - Status badges visible       │         assigned / not_loaded / Pending          │
│  └──────────────────────────────────┘                                                   │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

### 5.3 Load Sales Order to DSR Van Workflow

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                    LOAD SALES ORDER TO DSR VAN WORKFLOW                               │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│  PREREQUISITES:                                                                         │
│  ✅ DSRSOAssignment exists with status = 'assigned'                                   │
│  ✅ DSR has DSRStorage configured                                                       │
│  ✅ SalesOrder items have batch allocations                                               │
│  ✅ Source StorageLocation has sufficient stock                                           │
│                                                                                         │
│  USER (DSR)                                                                             │
│     │                                                                                   │
│     ▼                                                                                   │
│  ┌──────────────────────────────────┐                                                   │
│  │ 1. Navigate to My Assignments    │  ◀── src/pages/dsr/DSRMyAssignments.tsx           │
│  │    (requires user.dsr_id)        │         Access restricted to DSR role          │
│  └──────────────────────────────────┘                                                   │
│     │                                                                                   │
│     ▼                                                                                   │
│  ┌──────────────────────────────────┐                                                   │
│  │ 2. Find Unloaded Order           │  ◀── is_loaded = false badge shown               │
│  │    Click "Load to Van"           │                                                   │
│  └──────────────────────────────────┘                                                   │
│     │                                                                                   │
│     ▼                                                                                   │
│  ┌──────────────────────────────────┐                                                   │
│  │ 3. Load Dialog Opens             │                                                   │
│  │    - Shows order details         │                                                   │
│  │    - Optional notes field        │                                                   │
│  │    - Confirm/Cancel              │                                                   │
│  └──────────────────────────────────┘                                                   │
│     │                                                                                   │
│     ▼                                                                                   │
│  ┌──────────────────────────────────┐                                                   │
│  │ 4. API Call: loadSalesOrder()    │  ◀── POST /api/company/sales/dsr/so-assignments/  │
│  │    Assignment ID in URL path     │         {id}/load-so                            │
│  └──────────────────────────────────┘                                                   │
│     │                                                                                   │
│     ▼                                                                                   │
│  BACKEND PROCESSING (CRITICAL SECTION)                                                  │
│  ┌──────────────────────────────────┐                                                   │
│  │ 5. Validation                    │  ◀── DSRSOAssignmentService.load_sales_order()   │
│  │    ✓ Assignment exists           │                                                   │
│  │    ✓ DSR storage configured      │         get_dsr_storage_by_dsr()                 │
│  │    ✓ Order not already loaded    │         loading_status check                     │
│  └──────────────────────────────────┘                                                   │
│     │                                                                                   │
│     ▼                                                                                   │
│  ┌──────────────────────────────────┐                                                   │
│  │ 6. Fetch Batch Allocations       │  ◀── Get DSRBatchAllocation records             │
│  │    For each batch:                 │         Linked to assignment                     │
│  │    - batch_id                    │                                                   │
│  │    - quantity                    │                                                   │
│  │    - source location             │                                                   │
│  └──────────────────────────────────┘                                                   │
│     │                                                                                   │
│     ▼                                                                                   │
│  DATABASE TRANSACTION (Atomic)                                                          │
│  ┌──────────────────────────────────┐                                                   │
│  │ 7. For Each Batch Allocation:    │                                                   │
│  │                                  │                                                   │
│  │    A. REDUCE source stock        │  ◀── InventoryStock.quantity -= batch_qty       │
│  │       (warehouse location)       │         Optimistic locking (version column)     │
│  │                                  │                                                   │
│  │    B. CREATE InventoryMovement   │  ◀── Type: 'OUT'                                │
│  │       (out from warehouse)       │         Records: product, variant, batch, qty   │
│  │                                  │                                                   │
│  │    C. INCREASE DSR stock         │  ◀── DSRInventoryStock.quantity += batch_qty     │
│  │       (DSR storage)              │         Insert or update per product/variant     │
│  │                                  │                                                   │
│  │    D. CREATE InventoryMovement   │  ◀── Type: 'IN'                                 │
│  │       (into DSR storage)         │         Completes audit trail                   │
│  │                                  │                                                   │
│  │    E. CREATE DSRStockTransfer    │  ◀── warehouse.dsr_stock_transfer              │
│  │       Record                     │         + DSRStockTransferDetail records         │
│  └──────────────────────────────────┘                                                   │
│     │                                                                                   │
│     ▼                                                                                   │
│  ┌──────────────────────────────────┐                                                   │
│  │ 8. Update Assignment Status      │  ◀── sales.dsr_so_assignment                     │
│  │    - loading_status =            │                                                   │
│  │      'fully_loaded'              │                                                   │
│  │    - assignment_status =         │                                                   │
│  │      'in_progress'               │                                                   │
│  └──────────────────────────────────┘                                                   │
│     │                                                                                   │
│     ▼                                                                                   │
│  ┌──────────────────────────────────┐                                                   │
│  │ 9. Update Sales Order            │  ◀── sales.sales_order                           │
│  │    - order_status = 'shipped'    │                                                   │
│  └──────────────────────────────────┘                                                   │
│     │                                                                                   │
│     ▼                                                                                   │
│  ┌──────────────────────────────────┐                                                   │
│  │ 10. COMMIT TRANSACTION           │  ◀── All-or-nothing atomic commit               │
│  └──────────────────────────────────┘                                                   │
│     │                                                                                   │
│     ▼                                                                                   │
│  FRONTEND SUCCESS                                                                       │
│  ┌──────────────────────────────────┐                                                   │
│  │ 11. Toast: "Loaded Successfully" │  ◀── Refresh assignments list                    │
│  │     Badge changes to "Loaded"    │         Green badge with Package icon           │
│  │     Inventory updated            │                                                   │
│  └──────────────────────────────────┘                                                   │
│                                                                                         │
│  FAILURE HANDLING:                                                                      │
│  ❌ Insufficient stock → HTTP 400 with specific product details                       │
│  ❌ No DSR storage → HTTP 400 "No storage assigned"                                     │
│  ❌ Already loaded → HTTP 400 "Already loaded"                                          │
│  ❌ Database error → HTTP 500, full rollback                                          │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

### 5.4 Payment Collection & Settlement Workflow

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                    PAYMENT COLLECTION & SETTLEMENT WORKFLOW                             │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│  SCENARIO 1: DSR Collects Payment from Customer                                         │
│                                                                                         │
│  ┌──────────────────────────────────┐                                                   │
│  │ 1. DSR visits customer           │  ◀── Physical delivery of goods                │
│  │    Delivers order                │                                                   │
│  │    Collects payment              │         Cash/Check/Transfer                     │
│  └──────────────────────────────────┘                                                   │
│     │                                                                                   │
│     ▼                                                                                   │
│  ┌──────────────────────────────────┐                                                   │
│  │ 2. DSR opens My Assignments      │  ◀── Click "Collect Payment"                     │
│  │    Finds delivered order           │                                                   │
│  └──────────────────────────────────┘                                                   │
│     │                                                                                   │
│     ▼                                                                                   │
│  ┌──────────────────────────────────┐                                                   │
│  │ 3. DSRPaymentForm Opens          │  ◀── src/components/forms/DSRPaymentForm.tsx       │
│  │    - Shows order amount          │                                                   │
│  │    - Shows amount already paid   │                                                   │
│  │    - Input: amount to collect    │         Validation: <= remaining balance        │
│  │    - Select: payment method        │                                                   │
│  │    - Optional: reference #       │                                                   │
│  └──────────────────────────────────┘                                                   │
│     │                                                                                   │
│     ▼                                                                                   │
│  ┌──────────────────────────────────┐                                                   │
│  │ 4. API: collectPayment()         │  ◀── POST .../collect-payment                   │
│  │    assignment_id in path         │                                                   │
│  └──────────────────────────────────┘                                                   │
│     │                                                                                   │
│     ▼                                                                                   │
│  BACKEND                                                                                │
│  ┌──────────────────────────────────┐                                                   │
│  │ 5. Service Layer Processing      │  ◀── DSRSOAssignmentService.collect_payment()    │
│  │                                  │                                                   │
│  │    A. Validate assignment          │                                                   │
│  │    B. Update amount_paid          │  ◀── Increment by collected amount             │
│  │    C. Update DSR payment_on_hand  │  ◀── Increment (DSR now holds cash)            │
│  │    D. Check payment_status         │  ◀── 'Paid' if fully paid, else 'Partial'       │
│  │    E. Update SalesOrder            │  ◀── Sync payment status                       │
│  │    F. Create Payment record        │  ◀── If tracking individual payments            │
│  └──────────────────────────────────┘                                                   │
│                                                                                         │
│  SCENARIO 2: DSR Deposits Cash to Company (Settlement)                                │
│                                                                                         │
│  ┌──────────────────────────────────┐                                                   │
│  │ 6. Manager opens DSR List        │  ◀── View DSR payment_on_hand amounts            │
│  │    Sees DSR with cash to settle    │                                                   │
│  └──────────────────────────────────┘                                                   │
│     │                                                                                   │
│     ▼                                                                                   │
│  ┌──────────────────────────────────┐                                                   │
│  │ 7. Click "Record Settlement"     │                                                   │
│  └──────────────────────────────────┘                                                   │
│     │                                                                                   │
│     ▼                                                                                   │
│  ┌──────────────────────────────────┐                                                   │
│  │ 8. DSRSettlementForm Opens       │  ◀── src/components/forms/DSRSettlementForm.tsx  │
│  │    - Shows current on-hand      │                                                   │
│  │    - Input: settlement amount    │         Max = payment_on_hand                     │
│  │    - Select: payment method      │                                                   │
│  │    - Input: reference number     │         Must be unique within company             │
│  │    - Optional: notes             │                                                   │
│  └──────────────────────────────────┘                                                   │
│     │                                                                                   │
│     ▼                                                                                   │
│  ┌──────────────────────────────────┐                                                   │
│  │ 9. API: createDSRSettlement()    │  ◀── POST /api/company/sales/dsr/settlements/    │
│  └──────────────────────────────────┘                                                   │
│     │                                                                                   │
│     ▼                                                                                   │
│  BACKEND (CRITICAL - Optimistic Locking)                                              │
│  ┌──────────────────────────────────┐                                                   │
│  │ 10. DSRPaymentSettlementService  │  ◀── create_settlement()                         │
│  │                                  │                                                   │
│  │    A. LOCK DSR record            │  ◀── SELECT ... FOR UPDATE                      │
│  │       (prevents race condition)    │                                                   │
│  │                                  │                                                   │
│  │    B. Validate:                  │                                                   │
│  │       - DSR is active            │                                                   │
│  │       - Reference unique         │                                                   │
│  │       - Amount <= payment_on_hand│                                                   │
│  │       - Amount > 0               │                                                   │
│  │                                  │                                                   │
│  │    C. Create settlement record   │  ◀── sales.dsr_payment_settlement                │
│  │                                  │                                                   │
│  │    D. REDUCE payment_on_hand     │  ◀── dsr.payment_on_hand -= amount               │
│  │                                  │                                                   │
│  │    E. COMMIT (releases lock)     │                                                   │
│  └──────────────────────────────────┘                                                   │
│     │                                                                                   │
│     ▼                                                                                   │
│  ┌──────────────────────────────────┐                                                   │
│  │ 11. Settlement History Updated   │  ◀── Visible in DSRSettlementHistory.tsx         │
│  │     DSR balance reduced            │                                                   │
│  └──────────────────────────────────┘                                                   │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

### 5.5 Delivery Workflow

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              DELIVERY WORKFLOW                                          │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│  PREREQUISITES:                                                                         │
│  ✅ Order loaded to DSR van (is_loaded = true)                                        │
│  ✅ DSR at customer location                                                            │
│                                                                                         │
│  ┌──────────────────────────────────┐                                                   │
│  │ 1. DSR opens My Assignments      │  ◀── Finds loaded order                          │
│  │    Click "Make Delivery"           │                                                   │
│  └──────────────────────────────────┘                                                   │
│     │                                                                                   │
│     ▼                                                                                   │
│  ┌──────────────────────────────────┐                                                   │
│  │ 2. UnifiedDeliveryForm Opens     │  ◀── src/components/forms/UnifiedDeliveryForm.tsx │
│  │                                  │                                                   │
│  │    Shows:                          │                                                   │
│  │    - Order items with batches    │  ◀── From SalesOrder details                     │
│  │    - For each item:                │                                                   │
│  │      • Batch number              │                                                   │
│  │      • Ordered quantity          │                                                   │
│  │      • Delivered quantity        │  ◀── Default: full quantity                     │
│  │      • Notes field               │                                                   │
│  │                                  │                                                   │
│  │    Validation:                     │                                                   │
│  │    - delivered <= ordered        │                                                   │
│  │    - At least 1 item delivered   │                                                   │
│  └──────────────────────────────────┘                                                   │
│     │                                                                                   │
│     ▼                                                                                   │
│  ┌──────────────────────────────────┐                                                   │
│  │ 3. DSR Adjusts Quantities      │  ◀── For partial deliveries                       │
│  │    (if needed)                   │                                                   │
│  └──────────────────────────────────┘                                                   │
│     │                                                                                   │
│     ▼                                                                                   │
│  ┌──────────────────────────────────┐                                                   │
│  │ 4. API: markDelivered()          │  ◀── POST .../mark-delivered                     │
│  │    Payload: batch items          │                                                   │
│  │    with delivered quantities     │                                                   │
│  └──────────────────────────────────┘                                                   │
│     │                                                                                   │
│     ▼                                                                                   │
│  BACKEND                                                                                │
│  ┌──────────────────────────────────┐                                                   │
│  │ 5. DSRSOAssignmentService        │  ◀── mark_delivered()                             │
│  │                                  │                                                   │
│  │    A. Validate:                    │                                                   │
│  │       - Assignment exists        │                                                   │
│  │       - Order loaded               │                                                   │
│  │       - Not already delivered    │                                                   │
│  │                                  │                                                   │
│  │    B. Process Deliveries:        │                                                   │
│  │       For each batch item:         │                                                   │
│  │       • Validate stock exists    │  ◀── Check DSRInventoryStock                     │
│  │       • Reduce DSR stock         │  ◀── Delivered qty removed from DSR             │
│  │       • Create InventoryMovement │  ◀── Track delivery with reason='delivery'        │
│  │                                  │                                                   │
│  │    C. Update Status:             │                                                   │
│  │       - delivery_status =        │  ◀── 'Delivered' or 'Partial'                    │
│  │         'Delivered'/'Partial'    │                                                   │
│  │       - assignment_status =      │  ◀── 'completed' if fully delivered & paid       │
│  │         (conditional)            │                                                   │
│  │       - completion_date = now()  │         If fully completed                       │
│  │                                  │                                                   │
│  │    D. Update SalesOrder:           │                                                   │
│  │       - delivery_status synced   │                                                   │
│  └──────────────────────────────────┘                                                   │
│     │                                                                                   │
│     ▼                                                                                   │
│  FRONTEND                                                                               │
│  ┌──────────────────────────────────┐                                                   │
│  │ 6. Table Updates                 │  ◀── Badge: "Delivered" (green)                  │
│  │    If partial:                     │         or "Partial" (yellow)                    │
│  │    - Remaining items in DSR      │                                                   │
│  │    - Can process return later    │                                                   │
│  └──────────────────────────────────┘                                                   │
│                                                                                         │
│  EDGE CASE: Partial Delivery with Returns                                              │
│  ┌──────────────────────────────────┐                                                   │
│  │ 7. If customer rejects items   │  ◀── Use SalesReturnForm                          │
│  │    DSR processes return          │  ◀── src/components/forms/SalesReturnForm.tsx     │
│  │    Items return to DSR stock    │         (Return to van, not warehouse)           │
│  └──────────────────────────────────┘                                                   │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 6. Special Features Deep-Dive

### 6.1 Batch Tracking Integration

**Feature:** Full batch/lot tracking during load/unload and delivery operations.

**Implementation:**

```python
# From DSRSOAssignmentService.load_sales_order()
for batch_allocation in batch_allocations:
    # 1. Validate source stock at specific batch level
    source_stock = self.db.query(InventoryStock).filter(
        InventoryStock.product_id == batch_allocation.product_id,
        InventoryStock.variant_id == batch_allocation.variant_id,
        InventoryStock.location_id == source_location_id,
        InventoryStock.is_deleted == False
    ).with_for_update().first()
    
    if not source_stock or source_stock.quantity < batch_allocation.quantity:
        raise HTTPException(400, f"Insufficient stock for batch {batch_allocation.batch_id}")
    
    # 2. Reduce source batch stock
    source_stock.quantity -= batch_allocation.quantity
    
    # 3. Record outbound movement with batch reference
    outbound_movement = InventoryMovement(
        product_id=batch_allocation.product_id,
        variant_id=batch_allocation.variant_id,
        batch_id=batch_allocation.batch_id,  # <-- Batch tracking
        from_location_id=source_location_id,
        to_location_id=None,  # To DSR (special handling)
        to_dsr_storage_id=dsr_storage.dsr_storage_id,
        quantity=batch_allocation.quantity,
        movement_type='OUT',
        reason='dsr_load',
        reference_type='dsr_so_assignment',
        reference_id=assignment_id,
        # ... audit fields
    )
    
    # 4. Increase DSR stock (aggregate by product/variant)
    dsr_stock = self.db.query(DSRInventoryStock).filter(
        DSRInventoryStock.dsr_storage_id == dsr_storage.dsr_storage_id,
        DSRInventoryStock.product_id == batch_allocation.product_id,
        DSRInventoryStock.variant_id == batch_allocation.variant_id
    ).with_for_update().first()
    
    if dsr_stock:
        dsr_stock.quantity += batch_allocation.quantity
    else:
        dsr_stock = DSRInventoryStock(
            dsr_storage_id=dsr_storage.dsr_storage_id,
            product_id=batch_allocation.product_id,
            variant_id=batch_allocation.variant_id,
            quantity=batch_allocation.quantity,
            # ...
        )
        self.db.add(dsr_stock)
```

**Key Points:**
- Batch allocations are stored when SalesOrder is created (via `DSRBatchAllocation`)
- During load: Batch-level stock reduced at warehouse, aggregated in DSR storage
- During delivery: DSR stock reduced (batch info preserved in movements)
- Full audit trail via `InventoryMovement` records

---

### 6.2 Optimistic Locking for Payment Settlement

**Problem:** Race conditions when multiple users try to settle payments for the same DSR simultaneously.

**Solution:** Database row-level locking with `SELECT ... FOR UPDATE`

```python
def create_settlement(self, data, user_id, company_id):
    try:
        # Step 1: Lock the DSR record
        dsr = (
            self.db.query(DeliverySalesRepresentative)
            .filter(
                DeliverySalesRepresentative.dsr_id == data.dsr_id,
                DeliverySalesRepresentative.company_id == company_id,
                DeliverySalesRepresentative.is_deleted == False,
            )
            .with_for_update()  # <-- ROW-LEVEL LOCK ACQUIRED
            .first()
        )
        
        if not dsr:
            raise HTTPException(404, "DSR not found")
        
        # Step 2: Validate settlement amount against CURRENT payment_on_hand
        # (No other transaction can modify this until we commit)
        current_on_hand = dsr.payment_on_hand or Decimal("0")
        
        if data.amount > current_on_hand:
            raise HTTPException(400, 
                f"Settlement amount exceeds payment on hand")
        
        # Step 3: Create settlement record
        settlement = DSRPaymentSettlement(
            dsr_id=data.dsr_id,
            amount=data.amount,
            # ...
        )
        self.repo.create(settlement)
        
        # Step 4: Atomically reduce payment_on_hand
        dsr.payment_on_hand = current_on_hand - data.amount
        dsr.mb = user_id
        
        # Step 5: Commit (releases lock)
        self.db.commit()
        
    except HTTPException:
        self.db.rollback()
        raise
    except Exception as e:
        self.db.rollback()
        raise HTTPException(500, f"Failed to create settlement: {str(e)}")
```

**What this prevents:**
- Double-spending of payment_on_hand
- Over-settlement when concurrent requests arrive
- Data inconsistency in financial records

---

### 6.3 Soft Delete with Cascade Checks

**Pattern:** All entities use `is_deleted` boolean for soft deletion. Hard deletion is prevented by business logic checks.

**DSR Deletion with Stock Check:**

```python
def delete_dsr(self, dsr_id: int, company_id: int) -> bool:
    """
    Soft delete DSR with validation.
    Prevents deletion if DSR has inventory stock.
    """
    dsr = self.get_dsr(dsr_id)
    if not dsr or dsr.company_id != company_id:
        return False
    
    # CRITICAL: Check for existing stock
    # Query through DSRStorage relationship
    has_stock = (
        self.db.query(DSRInventoryStock)
        .join(DSRStorage)
        .filter(
            DSRStorage.dsr_id == dsr_id,
            DSRInventoryStock.is_deleted == False,
            DSRInventoryStock.quantity > 0
        )
        .first()
    )
    
    if has_stock:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete DSR with existing inventory stock. "
                   "Please unload all stock first."
        )
    
    # Soft delete
    dsr.is_deleted = True
    dsr.md = datetime.now()
    self.db.commit()
    return True
```

**Storage Deletion Check:**

```python
def delete_dsr_storage(self, storage_id: int, company_id: int) -> bool:
    storage = self.get_dsr_storage(storage_id, company_id)
    
    # Check for stock
    has_stock = self.db.query(DSRInventoryStock).filter(
        DSRInventoryStock.dsr_storage_id == storage_id,
        DSRInventoryStock.quantity > 0,
        DSRInventoryStock.is_deleted == False
    ).first()
    
    if has_stock:
        raise HTTPException(400, "Cannot delete storage with stock")
    
    storage.is_deleted = True
    # ... commit
```

---

### 6.4 Multi-Tenancy Implementation

**Pattern:** All queries are scoped by `company_id` from authenticated user context.

**Backend (FastAPI Dependency):**

```python
# app/dependencies.py
def get_current_company_id(
    current_user: dict = Depends(get_current_user)
) -> int:
    """Extract company_id from JWT token claims"""
    company_id = current_user.get("company_id")
    if not company_id:
        raise HTTPException(401, "Company context required")
    return int(company_id)

# API Endpoint usage
@dsr_router.get("/")
def list_dsrs(
    company_id: int = Depends(get_current_company_id),  # Injected
    db: Session = Depends(get_db)
):
    return service.list_dsr(company_id=company_id)  # Scoped query
```

**Repository Layer (Automatic Filtering):**

```python
class DeliverySalesRepresentativeRepository:
    def list(self, company_id: int, filters, pagination):
        query = self.db.query(DeliverySalesRepresentative).filter(
            DeliverySalesRepresentative.company_id == company_id,  # Scoped
            DeliverySalesRepresentative.is_deleted == False
        )
        # ... apply filters, pagination
```

**Frontend (Implicit):**

```typescript
// No explicit company_id needed - backend derives from auth token
const { data } = useQuery({
    queryKey: ['/dsr'],
    queryFn: () => getDSRs(start, limit, filters)  // No company_id param
})
```

**Security Model:**
- JWT token contains `company_id`, `user_id`, `role`, `dsr_id` (if applicable)
- All repository queries filter by `company_id`
- Service layer validates ownership before operations
- 403 returned if resource belongs to different company

---

### 6.5 Complex Validation Rules

#### Assignment Creation Validation

```python
def create_assignment(self, data, user_id, company_id):
    # 1. DSR must exist and be active
    dsr = self.dsr_repo.get(data.dsr_id)
    if not dsr or dsr.company_id != company_id:
        raise HTTPException(404, "DSR not found")
    if not dsr.is_active:
        raise HTTPException(400, "Cannot assign to inactive DSR")
    
    # 2. SalesOrder must exist and be pending
    sales_order = self.sales_order_repo.get(data.sales_order_id)
    if not sales_order or sales_order.company_id != company_id:
        raise HTTPException(404, "Sales order not found")
    if sales_order.order_status != 'pending':
        raise HTTPException(400, "Can only assign pending orders")
    
    # 3. SalesOrder must not already be assigned
    existing = self.repo.get_by_sales_order(data.sales_order_id)
    if existing:
        raise HTTPException(400, "Sales order already assigned to a DSR")
    
    # 4. Customer must match SalesOrder's customer
    if data.customer_id != sales_order.customer_id:
        raise HTTPException(400, "Customer must match sales order customer")
    
    # 5. DSR must have storage configured
    storage = self.dsr_storage_repo.get_by_dsr(data.dsr_id)
    if not storage:
        raise HTTPException(400, "DSR does not have storage configured")
    
    # Create assignment...
```

#### Payment Collection Validation

```python
def collect_payment(self, assignment_id, data, user_id, company_id):
    assignment = self.get_assignment(assignment_id)
    
    # 1. Validate ownership
    if assignment.company_id != company_id:
        raise HTTPException(403, "Access denied")
    
    # 2. Check assignment status
    if assignment.is_deleted:
        raise HTTPException(400, "Assignment has been deleted")
    
    # 3. Amount validation
    total_amount = assignment.sales_order.effective_total_amount or 0
    already_paid = assignment.amount_paid or 0
    remaining = total_amount - already_paid
    
    if data.amount > remaining:
        raise HTTPException(400, 
            f"Payment amount ({data.amount}) exceeds remaining balance ({remaining})")
    
    if data.amount <= 0:
        raise HTTPException(400, "Payment amount must be greater than 0")
    
    # 4. Process payment...
```

---

## 7. API Quick Reference

### 7.1 Endpoint Summary by Entity

#### DeliverySalesRepresentative

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/api/company/sales/dsr/` | List DSRs | Any |
| `GET` | `/api/company/sales/dsr/{id}` | Get DSR | Any |
| `POST` | `/api/company/sales/dsr/` | Create DSR | Admin/Manager |
| `PATCH` | `/api/company/sales/dsr/{id}` | Update DSR | Admin/Manager |
| `DELETE` | `/api/company/sales/dsr/{id}` | Delete DSR | Admin/Manager |
| `PATCH` | `/api/company/sales/dsr/{id}/payment-on-hand` | Update payment | Admin/Manager |
| `GET` | `/api/company/sales/dsr/{id}/summary` | Get summary | Any |
| `GET` | `/api/company/sales/dsr/check-code/{code}` | Check code | Any |

#### DSRSOAssignment

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/api/company/sales/dsr/so-assignments/` | List assignments | Any |
| `GET` | `/api/company/sales/dsr/so-assignments/{id}` | Get assignment | Any |
| `POST` | `/api/company/sales/dsr/so-assignments/` | Create assignment | Admin/Manager |
| `PATCH` | `/api/company/sales/dsr/so-assignments/{id}` | Update assignment | Admin/Manager |
| `DELETE` | `/api/company/sales/dsr/so-assignments/{id}` | Delete assignment | Admin/Manager |
| `POST` | `/api/company/sales/dsr/so-assignments/{id}/mark-delivered` | Mark delivered | DSR/Manager |
| `POST` | `/api/company/sales/dsr/so-assignments/{id}/collect-payment` | Collect payment | DSR/Manager |
| `POST` | `/api/company/sales/dsr/so-assignments/{id}/load-so` | Load to van | DSR |
| `POST` | `/api/company/sales/dsr/so-assignments/{id}/unload-so` | Unload from van | DSR |
| `POST` | `/api/company/sales/dsr/so-assignments/batch-deliver` | Batch delivery | DSR |

#### DSRPaymentSettlement

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/api/company/sales/dsr/settlements/` | List settlements | Admin/Manager |
| `POST` | `/api/company/sales/dsr/settlements/` | Create settlement | Admin/Manager |
| `GET` | `/api/company/sales/dsr/settlements/summary/{dsr_id}` | DSR summary | Admin/Manager |

#### DSRStorage

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/api/company/warehouse/dsr-storage/` | List storages | Admin/Manager |
| `GET` | `/api/company/warehouse/dsr-storage/{id}` | Get storage | Admin/Manager |
| `GET` | `/api/company/warehouse/dsr-storage/by-dsr/{dsr_id}` | Get by DSR | Any |
| `POST` | `/api/company/warehouse/dsr-storage/` | Create storage | Admin/Manager |
| `PATCH` | `/api/company/warehouse/dsr-storage/{id}` | Update storage | Admin/Manager |
| `DELETE` | `/api/company/warehouse/dsr-storage/{id}` | Delete storage | Admin/Manager |

#### DSRInventoryStock

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/api/company/warehouse/dsr-inventory-stock/by-storage/{id}` | By storage | Admin/Manager |
| `GET` | `/api/company/warehouse/dsr-inventory-stock/by-dsr/{dsr_id}` | By DSR | Any |
| `GET` | `/api/company/warehouse/dsr-inventory-stock/my-stock` | Current user's | DSR |
| `GET` | `/api/company/warehouse/dsr-inventory-stock/search` | Search | Any |

### 7.2 Frontend API Function Map

| Function | File | Backend Endpoint |
|----------|------|------------------|
| `getDSRs()` | `dsrApi.ts` | `GET /api/company/sales/dsr/` |
| `createDSR()` | `dsrApi.ts` | `POST /api/company/sales/dsr/` |
| `updateDSR()` | `dsrApi.ts` | `PATCH /api/company/sales/dsr/{id}` |
| `deleteDSR()` | `dsrApi.ts` | `DELETE /api/company/sales/dsr/{id}` |
| `getDSRSOAssignments()` | `dsrApi.ts` | `GET /api/company/sales/dsr/so-assignments/` |
| `createDSRSOAssignment()` | `dsrApi.ts` | `POST /api/company/sales/dsr/so-assignments/` |
| `collectPayment()` | `dsrApi.ts` | `POST .../so-assignments/{id}/collect-payment` |
| `markDelivered()` | `dsrApi.ts` | `POST .../so-assignments/{id}/mark-delivered` |
| `loadSalesOrder()` | `dsrApi.ts` | `POST .../so-assignments/{id}/load-so` |
| `unloadSalesOrder()` | `dsrApi.ts` | `POST .../so-assignments/{id}/unload-so` |
| `getDSRSettlements()` | `dsrSettlementApi.ts` | `GET /api/company/sales/dsr/settlements/` |
| `createDSRSettlement()` | `dsrSettlementApi.ts` | `POST /api/company/sales/dsr/settlements/` |
| `getDSRStorages()` | `dsrStorageApi.ts` | `GET /api/company/warehouse/dsr-storage/` |
| `getMyDSRInventoryStock()` | `dsrInventoryStockApi.ts` | `GET /api/company/warehouse/dsr-inventory-stock/my-stock` |

---

## 8. File Map

### 8.1 Backend Files

| File | Layer | Purpose |
|------|-------|---------|
| `app/models/sales.py` | Model | DeliverySalesRepresentative, DSRSOAssignment, DSRPaymentSettlement |
| `app/models/warehouse.py` | Model | DSRStorage, DSRInventoryStock, DSRStockTransfer, DSRStockTransferDetail |
| `app/api/dsr/__init__.py` | API | Router composition and prefix setup |
| `app/api/dsr/delivery_sales_representative.py` | API | DSR CRUD and special endpoints |
| `app/api/dsr/dsr_so_assignment.py` | API | Assignment CRUD and business operations |
| `app/api/dsr/dsr_payment_settlement.py` | API | Settlement endpoints |
| `app/api/warehouse/dsr_storage.py` | API | Storage CRUD endpoints |
| `app/api/warehouse/dsr_inventory_stock.py` | API | Inventory stock endpoints |
| `app/services/dsr/delivery_sales_representative_service.py` | Service | DSR business logic |
| `app/services/dsr/dsr_so_assignment_service.py` | Service | Assignment business logic, load/unload |
| `app/services/dsr/dsr_payment_settlement_service.py` | Service | Settlement with optimistic locking |
| `app/services/warehouse/dsr_storage.py` | Service | Storage management |
| `app/repositories/dsr/delivery_sales_representative.py` | Repository | DSR data access |
| `app/repositories/dsr/dsr_so_assignment.py` | Repository | Assignment data access |
| `app/repositories/dsr/dsr_payment_settlement.py` | Repository | Settlement data access |
| `app/schemas/dsr/delivery_sales_representative.py` | Schema | DSR Pydantic models |
| `app/schemas/dsr/dsr_so_assignment.py` | Schema | Assignment Pydantic models |
| `app/schemas/dsr/dsr_payment_settlement.py` | Schema | Settlement Pydantic models |
| `app/schemas/warehouse/dsr_storage.py` | Schema | Storage Pydantic models |

### 8.2 Frontend Files

| File | Category | Purpose |
|------|----------|---------|
| `src/pages/dsr/DeliverySalesRepresentatives.tsx` | Page | DSR management list |
| `src/pages/dsr/DSRSOAssignments.tsx` | Page | Assignment management |
| `src/pages/dsr/DSRMyAssignments.tsx` | Page | DSR's order view |
| `src/pages/dsr/DSRSettlementHistory.tsx` | Page | Settlement records |
| `src/pages/dsr/DSRStorages.tsx` | Page | Storage management |
| `src/pages/dsr/DSRInventoryStock.tsx` | Page | DSR's stock view |
| `src/components/forms/DSRForm.tsx` | Form | Create/edit DSR |
| `src/components/forms/DSRStorageForm.tsx` | Form | Create/edit storage |
| `src/components/forms/DSRAssignmentForm.tsx` | Form | Assign order to DSR |
| `src/components/forms/DSRSettlementForm.tsx` | Form | Record settlement |
| `src/components/forms/DSRPaymentForm.tsx` | Form | Collect payment |
| `src/components/forms/UnifiedDeliveryForm.tsx` | Form | Mark delivery |
| `src/components/modals/DSRLoadingModal.tsx` | Modal | Load/unload dialog |
| `src/components/modals/DSRSOBreakdownModal.tsx` | Modal | Batch breakdown |
| `src/components/DSRSettlementFilter.tsx` | Component | Settlement filtering |
| `src/lib/api/dsrApi.ts` | API | Core DSR API functions |
| `src/lib/api/dsrStorageApi.ts` | API | Storage API functions |
| `src/lib/api/dsrSettlementApi.ts` | API | Settlement API functions |
| `src/lib/api/dsrInventoryStockApi.ts` | API | Inventory API functions |
| `src/lib/schema/dsr.ts` | Schema | DSR/assignment types |
| `src/lib/schema/dsrStorage.ts` | Schema | Storage types |
| `src/lib/schema/dsrSettlement.ts` | Schema | Settlement types |
| `src/lib/schema/dsrInventoryStock.ts` | Schema | Inventory types |

---

## 9. Appendix: Operation Counts

### 9.1 Backend CRUD Operations

| Entity | Create | Read | Update | Delete | Special | Total |
|--------|--------|------|--------|--------|---------|-------|
| DeliverySalesRepresentative | 1 | 2 | 1 | 1 | 3 | **8** |
| DSRSOAssignment | 1 | 2 | 1 | 1 | 5 | **10** |
| DSRPaymentSettlement | 1 | 1 | 0 | 0 | 1 | **3** |
| DSRStorage | 1 | 3 | 1 | 1 | 0 | **6** |
| DSRInventoryStock | 0 | 4 | 0 | 0 | 0 | **4** |
| **TOTAL** | **4** | **12** | **3** | **3** | **9** | **31** |

### 9.2 Frontend API Functions

| API File | Functions |
|----------|-----------|
| `dsrApi.ts` | **13** |
| `dsrStorageApi.ts` | **7** |
| `dsrSettlementApi.ts` | **3** |
| `dsrInventoryStockApi.ts` | **3** |
| **TOTAL** | **26** |

### 9.3 Frontend Pages & Components

| Category | Count |
|----------|-------|
| Pages | 6 |
| Forms | 6 |
| Modals | 2 |
| Shared Components | 4 |
| **TOTAL** | **18** |

### 9.4 Database Entities

| Schema | Entity | Fields | Relationships |
|--------|--------|--------|---------------|
| sales | DeliverySalesRepresentative | 15 | 4 |
| sales | DSRSOAssignment | 18 | 4 |
| sales | DSRPaymentSettlement | 12 | 2 |
| warehouse | DSRStorage | 13 | 3 |
| warehouse | DSRInventoryStock | 11 | 4 |
| warehouse | DSRStockTransfer | 16 | 4 |
| warehouse | DSRStockTransferDetail | 10 | 3 |
| **TOTAL** | **7 entities** | **95 fields** | **24 relationships** |

---

## Document Summary

This reference documentation provides comprehensive coverage of the Shoudagor DSR module:

- **7 Core Entities** documented with complete field specifications
- **31 Backend Operations** including CRUD and special business logic
- **26 Frontend API Functions** mapped to backend endpoints
- **18 UI Components** covering pages, forms, and shared components
- **5 Complete Workflows** illustrated with ASCII flow diagrams
- **5 Special Features** deep-dives on batch tracking, optimistic locking, soft delete, multi-tenancy, and validation

**Key Files for Implementation:**
- Backend API: `app/api/dsr/*.py`, `app/api/warehouse/dsr_*.py`
- Backend Services: `app/services/dsr/*.py`
- Frontend Pages: `src/pages/dsr/*.tsx`
- Frontend API: `src/lib/api/dsr*.ts`

**Status Legend:**
- ✅ Complete - Feature implemented and tested
- ⚠️ Partial - Feature incomplete or has known issues
- ❌ Missing - Feature not yet implemented

All features in this document are marked ✅ Complete as of the last update.

---

*End of DSR Module Reference Documentation*
