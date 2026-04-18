# Batch Management (Inventory Batch) Module - Complete Reference

---

## Document Metadata

| Field | Value |
|-------|-------|
| **Generated** | April 16, 2026 |
| **Module Name** | Batch Management (Inventory Batch) |
| **Scope** | Full-stack analysis of the Batch Management Module |
| **Coverage** | Backend API, Frontend UI, Interconnected Workflows, Special Features |
| **Version** | Phase 3 Implementation (with Phase 4 Consistency Checks) |

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
┌─────────────────────────────────────────────────────────────────────────────┐
│                           4-LAYER STACK ARCHITECTURE                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ LAYER 1: FRONTEND (React + TypeScript)                              │   │
│  │ • React 18 with TypeScript                                           │   │
│  │ • TanStack Query for state management                                │   │
│  │ • shadcn/ui component library                                        │   │
│  │ • React Router for navigation                                        │   │
│  │ • Lucide React for icons                                             │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ LAYER 2: BACKEND API (FastAPI)                                       │   │
│  │ • FastAPI 0.104+ with async support                                 │   │
│  │ • Pydantic for request/response validation                          │   │
│  │ • SQLAlchemy ORM for database operations                             │   │
│  │ • JWT authentication via dependencies                                │   │
│  │ • Custom exception handlers                                          │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ LAYER 3: DATABASE (PostgreSQL)                                       │   │
│  │ • PostgreSQL 14+                                                     │   │
│  │ • Multi-schema architecture (inventory, sales, settings)              │   │
│  │ • JSON/JSONB for flexible data                                        │   │
│  │ • Decimal (18,4) for financial precision                              │   │
│  │ • Optimized indexes for batch queries                                │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ LAYER 4: EXTERNAL SERVICES                                           │   │
│  │ • Elasticsearch (for product search - future integration)             │   │
│  │ • Redis (for caching - future integration)                          │   │
│  │ • Background job queue (Celery - future integration)                │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Entity Relationships

```
ENTITY RELATIONSHIP DIAGRAM
══════════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────────────┐
│                              CORE ENTITIES                                   │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────┐         ┌──────────────────┐         ┌──────────────────┐
│   Product    │◄────────┤      Batch       ├────────►│  ProductVariant  │
│  (inventory) │    1:N  │   (inventory)    │  N:1    │    (inventory)   │
└──────────────┘         └──────────────────┘         └──────────────────┘
        ▲                        │    ▲                          │
        │                        │    │                          │
        │                        │    │                          │
   1:N  │                        │    │                          │
        │                   1:N  │    │  1:N                     │
        │                        ▼    │                          ▼
┌──────────────────┐         ┌──────────────────┐         ┌──────────────────┐
│ InventoryMovement│◄────────┤  SalesOrderBatch │         │    Supplier      │
│   (inventory)    │   N:1   │   Allocation     │         │  (procurement)   │
└──────────────────┘         │    (sales)       │         └──────────────────┘
                             └──────────────────┘                  ▲
                                    │                               │
                                    │  N:1                          │
                                    ▼                               │
                             ┌──────────────────┐                 │
                             │  SalesOrderDetail│                 │
                             │     (sales)      │─────────────────┘
                             └──────────────────┘            N:1
                                    │
                                    │ N:1
                                    ▼
                             ┌──────────────────┐
                             │   SalesOrder     │
                             │     (sales)      │
                             └──────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                            SUPPORTING ENTITIES                               │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────┐         ┌──────────────────────────┐
│ CompanyInventorySetting  │         │   DSRBatchAllocation     │
│       (settings)         │         │      (inventory)         │
│  • valuation_mode        │         │  • Tracks DSR inventory  │
│  • batch_tracking_enabled│         │  • Links to assignments  │
│  • consistency_tolerance │         │  • Unit cost tracking    │
└──────────────────────────┘         └──────────────────────────┘

┌──────────────────────────┐         ┌──────────────────────────┐
│   DSRStockMovement       │         │  StockMutationAudit      │
│     (warehouse)          │         │     (inventory)          │
│  • LOAD/UNLOAD tracking  │         │  • Audit trail           │
│  • Audit timestamps      │         │  • Before/after snapshots│
│  • JSON details field    │         │  • Error logging         │
└──────────────────────────┘         └──────────────────────────┘

┌──────────────────────────┐
│   BatchQtyAuditLog       │
│     (inventory)          │
│  • qty change history    │
│  • Actor tracking        │
│  • Soft delete tracking  │
└──────────────────────────┘

CARDINALITY SUMMARY:
═══════════════════
• Product → Batch: 1:N (One product has many batches)
• Batch → ProductVariant: N:1 (Many batches belong to one variant)
• Batch → InventoryMovement: 1:N (One batch has many movements)
• Batch → SalesOrderBatchAllocation: 1:N (One batch allocated to many orders)
• SalesOrderDetail → SalesOrderBatchAllocation: 1:N (One line item has many allocations)
• Batch → Supplier: N:1 (Many batches from one supplier)
• StorageLocation → Batch: 1:N (One location stores many batches)
```

### 1.3 Technology Stack

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| **Frontend Framework** | React | 18.x | UI component library |
| **Frontend Language** | TypeScript | 5.x | Type-safe development |
| **Frontend Routing** | React Router | 6.x | SPA navigation |
| **State Management** | TanStack Query | 5.x | Server state caching |
| **UI Components** | shadcn/ui | Latest | Pre-built accessible components |
| **Styling** | Tailwind CSS | 3.x | Utility-first CSS |
| **Icons** | Lucide React | Latest | Icon library |
| **Backend Framework** | FastAPI | 0.104+ | High-performance API framework |
| **Backend Language** | Python | 3.10+ | Server-side logic |
| **ORM** | SQLAlchemy | 2.x | Database abstraction |
| **Validation** | Pydantic | 2.x | Request/response schemas |
| **Database** | PostgreSQL | 14+ | Relational data storage |
| **Migrations** | Alembic | Latest | Schema versioning |
| **Decimal Precision** | Python Decimal | Built-in | Financial calculations |

---

## 2. Entity Inventory

### 2.1 batch (inventory.batch)

**Table Name:** `inventory.batch`

**Purpose:** Core entity representing a group of inventory units received together with a common cost.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `batch_id` | Integer | PK, Auto-increment | Unique batch identifier |
| `company_id` | Integer | FK, NOT NULL | Multi-tenant company reference |
| `product_id` | Integer | FK, NOT NULL | Product reference |
| `variant_id` | Integer | FK, NULLABLE | Product variant reference |
| `qty_received` | Numeric(18,4) | NOT NULL | Total quantity received |
| `qty_on_hand` | Numeric(18,4) | NOT NULL, DEFAULT 0 | Current available quantity |
| `unit_cost` | Numeric(18,4) | NOT NULL | Cost per unit at receipt |
| `received_date` | TIMESTAMP | NOT NULL | Date/time of receipt |
| `supplier_id` | Integer | FK, NULLABLE | Supplier reference |
| `lot_number` | VARCHAR(100) | NULLABLE | Supplier lot/batch number |
| `status` | VARCHAR(20) | NOT NULL, DEFAULT 'active' | active/depleted/expired/returned/quarantined |
| `expiry_date` | TIMESTAMP | NULLABLE | Product expiration date |
| `location_id` | Integer | FK, NULLABLE | Storage location reference |
| `purchase_order_detail_id` | Integer | FK, NULLABLE | Source PO detail |
| `delivery_detail_id` | Integer | FK, NULLABLE | For partial deliveries |
| `source_type` | VARCHAR(30) | NOT NULL, DEFAULT 'purchase' | purchase/return/adjustment/transfer/synthetic |
| `is_synthetic` | Boolean | NOT NULL, DEFAULT FALSE | TRUE if created during backfill |
| `notes` | VARCHAR(500) | NULLABLE | Additional notes |
| `version` | Integer | NOT NULL, DEFAULT 0 | Optimistic locking version |
| `is_deleted` | Boolean | NOT NULL, DEFAULT FALSE | Soft delete flag |
| `cd` | TIMESTAMP | NOT NULL | Created date |
| `md` | TIMESTAMP | NULLABLE | Modified date |
| `cb` | Integer | NOT NULL | Created by user ID |
| `mb` | Integer | NULLABLE | Modified by user ID |

**Indexes:**
- `idx_batch_lot_number` (lot_number) - Unique lot searches
- `idx_batch_product_variant_location` (product_id, variant_id, location_id) - Composite lookups
- `idx_batch_status_company` (status, company_id) - Active batch queries
- `idx_batch_received_date` (received_date) - FIFO/LIFO ordering

**Relationships:**
- `product` → Product (N:1)
- `variant` → ProductVariant (N:1)
- `supplier` → Supplier (N:1)
- `location` → StorageLocation (N:1)
- `purchase_order_detail` → PurchaseOrderDetail (N:1)
- `movements` → InventoryMovement (1:N, cascade delete)
- `sales_allocations` → SalesOrderBatchAllocation (1:N, cascade delete)
- `dsr_allocations` → DSRBatchAllocation (1:N, cascade delete)

---

### 2.2 inventory_movement (inventory.inventory_movement)

**Table Name:** `inventory.inventory_movement`

**Purpose:** Immutable ledger recording every stock change with locked cost at transaction time.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `movement_id` | Integer | PK, Auto-increment | Unique movement identifier |
| `company_id` | Integer | FK, NOT NULL | Multi-tenant company reference |
| `batch_id` | Integer | FK, NOT NULL | Associated batch |
| `product_id` | Integer | FK, NOT NULL | Product reference |
| `variant_id` | Integer | FK, NULLABLE | Variant reference |
| `qty` | Numeric(18,4) | NOT NULL | Quantity (+inbound, -outbound) |
| `movement_type` | VARCHAR(20) | NOT NULL | IN/OUT/RETURN_IN/RETURN_OUT/ADJUSTMENT/TRANSFER_IN/TRANSFER_OUT |
| `ref_type` | VARCHAR(50) | NOT NULL | PURCHASE_DELIVERY/SALES_DELIVERY/SALES_RETURN/PURCHASE_RETURN/ADJUSTMENT/STOCK_TRANSFER/DSR_TRANSFER/OPENING_BALANCE/BACKFILL |
| `ref_id` | Integer | NULLABLE | FK to source document |
| `unit_cost_at_txn` | Numeric(18,4) | NOT NULL | Locked cost at transaction time |
| `actor` | Integer | FK, NOT NULL | User who performed action |
| `txn_timestamp` | TIMESTAMP | NOT NULL | Transaction timestamp |
| `notes` | VARCHAR(500) | NULLABLE | Additional notes |
| `location_id` | Integer | FK, NULLABLE | Location reference |
| `related_movement_id` | Integer | FK, NULLABLE | Links return to original sale |
| `is_deleted` | Boolean | NOT NULL, DEFAULT FALSE | Soft delete flag |
| `cd` | TIMESTAMP | NOT NULL | Created date |
| `md` | TIMESTAMP | NULLABLE | Modified date |
| `cb` | Integer | NOT NULL | Created by user ID |
| `mb` | Integer | NULLABLE | Modified by user ID |

**Indexes:**
- `idx_inventory_movement_batch_id` (batch_id)
- `idx_inventory_movement_product_variant` (product_id, variant_id)
- `idx_inventory_movement_company_id` (company_id)
- `idx_inventory_movement_type_ref` (movement_type, ref_type)
- `idx_inventory_movement_txn_timestamp` (txn_timestamp)
- `idx_inventory_movement_location_id` (location_id)

**Relationships:**
- `batch` → Batch (N:1)
- `product` → Product (N:1)
- `variant` → ProductVariant (N:1)
- `location` → StorageLocation (N:1)
- `actor_user` → User (N:1)
- `related_movement` → InventoryMovement (self-referential, 1:1)
- `reverse_related_movement` → InventoryMovement (self-referential, 1:N)
- `sales_allocations` → SalesOrderBatchAllocation (1:N)

---

### 2.3 company_inventory_setting (settings.company_inventory_setting)

**Table Name:** `settings.company_inventory_setting`

**Purpose:** Company-level inventory configuration controlling valuation mode and batch tracking.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `setting_id` | Integer | PK, Auto-increment | Unique setting identifier |
| `company_id` | Integer | FK, NOT NULL, UNIQUE | Company reference |
| `valuation_mode` | VARCHAR(20) | NOT NULL, DEFAULT 'FIFO' | FIFO/LIFO/WEIGHTED_AVG |
| `batch_tracking_enabled` | Boolean | NOT NULL, DEFAULT FALSE | Feature flag for batch mode |
| `strict_consistency_check` | Boolean | NOT NULL, DEFAULT TRUE | Raise exception on invariant violation |
| `auto_repair_on_violation` | Boolean | NOT NULL, DEFAULT FALSE | Auto-repair (always FALSE - manual only) |
| `consistency_tolerance` | Numeric(15,4) | NOT NULL, DEFAULT 0.0001 | Allowable batch-stock difference |
| `check_interval_minutes` | Integer | NOT NULL, DEFAULT 60 | Scheduled check interval |
| `is_deleted` | Boolean | NOT NULL, DEFAULT FALSE | Soft delete flag |
| `cd` | TIMESTAMP | NOT NULL | Created date |
| `md` | TIMESTAMP | NULLABLE | Modified date |
| `cb` | Integer | NOT NULL | Created by user ID |
| `mb` | Integer | NULLABLE | Modified by user ID |

**Indexes:**
- `idx_company_inventory_setting_company_id` (company_id)

**Relationships:**
- `company` → AppClientCompany (1:1)

---

### 2.4 sales_order_batch_allocation (sales.sales_order_batch_allocation)

**Table Name:** `sales.sales_order_batch_allocation`

**Purpose:** Links sales order details to allocated batches for COGS tracking and returns.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `allocation_id` | Integer | PK, Auto-increment | Unique allocation identifier |
| `sales_order_detail_id` | Integer | FK, NOT NULL | Sales order line item |
| `batch_id` | Integer | FK, NOT NULL | Allocated batch |
| `qty_allocated` | Numeric(18,4) | NOT NULL | Quantity allocated from batch |
| `unit_cost_at_allocation` | Numeric(18,4) | NOT NULL | Batch cost at allocation time |
| `movement_id` | Integer | FK, NULLABLE | Associated OUT movement |
| `is_deleted` | Boolean | NOT NULL, DEFAULT FALSE | Soft delete flag |
| `cd` | TIMESTAMP | NOT NULL | Created date |
| `md` | TIMESTAMP | NULLABLE | Modified date |
| `cb` | Integer | NOT NULL | Created by user ID |
| `mb` | Integer | NULLABLE | Modified by user ID |

**Indexes:**
- `idx_sales_order_batch_allocation_so_detail_id` (sales_order_detail_id)
- `idx_sales_order_batch_allocation_batch_id` (batch_id)
- `idx_sales_order_batch_allocation_movement_id` (movement_id)

**Relationships:**
- `sales_order_detail` → SalesOrderDetail (N:1)
- `batch` → Batch (N:1)
- `movement` → InventoryMovement (N:1)

---

### 2.5 dsr_batch_allocation (inventory.dsr_batch_allocation)

**Table Name:** `inventory.dsr_batch_allocation`

**Purpose:** Tracks batch inventory currently in DSR (Delivery Sales Representative) storage.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `dsr_allocation_id` | Integer | PK, Auto-increment | Unique allocation identifier |
| `assignment_id` | Integer | FK, NOT NULL | DSR SO assignment reference |
| `batch_id` | Integer | FK, NOT NULL | Allocated batch |
| `qty_allocated` | Numeric(18,4) | NOT NULL | Quantity transferred to DSR |
| `unit_cost_at_transfer` | Numeric(18,4) | NOT NULL | Cost at transfer time |
| `movement_id` | Integer | FK, NULLABLE | Associated TRANSFER_OUT movement |
| `is_deleted` | Boolean | NOT NULL, DEFAULT FALSE | Soft delete flag |
| `cd` | TIMESTAMP | NOT NULL | Created date |
| `md` | TIMESTAMP | NULLABLE | Modified date |

**Indexes:**
- `idx_dsr_batch_allocation_assignment_id` (assignment_id)
- `idx_dsr_batch_allocation_batch_id` (batch_id)
- `idx_dsr_batch_allocation_movement_id` (movement_id)

**Relationships:**
- `assignment` → DSRSOAssignment (N:1)
- `batch` → Batch (N:1)
- `movement` → InventoryMovement (N:1)

---

### 2.6 dsr_stock_movement (warehouse.dsr_stock_movement)

**Table Name:** `warehouse.dsr_stock_movement`

**Purpose:** Audit trail for DSR load/unload operations.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `movement_id` | Integer | PK, Auto-increment | Unique movement identifier |
| `dsr_id` | Integer | FK, NOT NULL | DSR reference |
| `sales_order_id` | Integer | FK, NULLABLE | Associated sales order |
| `assignment_id` | Integer | FK, NULLABLE | DSR assignment reference |
| `movement_type` | VARCHAR(20) | NOT NULL | LOAD/UNLOAD/ADJUSTMENT |
| `movement_date` | TIMESTAMP | NOT NULL, DEFAULT NOW | Operation timestamp |
| `performed_by` | Integer | FK, NOT NULL | User who performed action |
| `from_location_id` | Integer | NULLABLE | Source location |
| `to_location_id` | Integer | NULLABLE | Destination location |
| `notes` | VARCHAR(500) | NULLABLE | Additional notes |
| `details` | TEXT | NULLABLE | JSON string of items moved |

**Indexes:**
- `idx_dsr_stock_movement_dsr_id` (dsr_id)
- `idx_dsr_stock_movement_sales_order_id` (sales_order_id)
- `idx_dsr_stock_movement_assignment_id` (assignment_id)
- `idx_dsr_stock_movement_type_date` (movement_type, movement_date)

---

### 2.7 stock_mutation_audit (inventory.stock_mutation_audit)

**Table Name:** `inventory.stock_mutation_audit`

**Purpose:** Tracks all stock mutations for traceability and debugging.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | Integer | PK, Auto-increment | Unique audit ID |
| `company_id` | Integer | FK, NOT NULL | Company reference |
| `product_id` | Integer | FK, NOT NULL | Product reference |
| `variant_id` | Integer | FK, NULLABLE | Variant reference |
| `location_id` | Integer | FK, NOT NULL | Location reference |
| `operation` | VARCHAR(50) | NOT NULL | Operation type (CREATE_BATCH, ALLOCATE, etc.) |
| `qty_delta` | Numeric(18,4) | NOT NULL | Quantity change |
| `user_id` | Integer | FK, NULLABLE | User who performed action |
| `ref_type` | VARCHAR(50) | NULLABLE | Reference document type |
| `ref_id` | Integer | NULLABLE | Reference document ID |
| `success` | Boolean | NOT NULL | Whether operation succeeded |
| `error_message` | TEXT | NULLABLE | Error details if failed |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW | Audit timestamp |

**Indexes:**
- `idx_stock_mutation_audit_product_variant_location` (product_id, variant_id, location_id)
- `idx_stock_mutation_audit_operation` (operation)
- `idx_stock_mutation_audit_created_at` (created_at)

---

### 2.8 batch_qty_audit_log (inventory.batch_qty_audit_log)

**Table Name:** `inventory.batch_qty_audit_log`

**Purpose:** Tracks changes to batch quantities for reconciliation.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | Integer | PK, Auto-increment | Unique log ID |
| `batch_id` | Integer | FK, NOT NULL | Batch reference |
| `old_qty` | Numeric(18,4) | NULLABLE | Previous quantity |
| `new_qty` | Numeric(18,4) | NULLABLE | New quantity |
| `changed_at` | TIMESTAMP | NOT NULL, DEFAULT NOW | Change timestamp |
| `change_type` | VARCHAR(10) | NULLABLE | UPDATE/DELETE |
| `actor_id` | Integer | FK, NULLABLE | User who made change |

**Indexes:**
- `idx_batch_qty_audit_log_batch_id` (batch_id)
- `idx_batch_qty_audit_log_changed_at` (changed_at)

---

## 3. Backend Operations Reference

### 3.1 Batch Entity Operations

| Operation | Method | Endpoint | Service Method | Description |
|-----------|--------|----------|----------------|-------------|
| **List Batches** | GET | `/api/company/inventory/batches/` | `BatchRepository.list()` | List with filtering and pagination |
| **Get Single Batch** | GET | `/api/company/inventory/batches/{batch_id}` | `BatchRepository.get()` | Get batch with movement history |
| **Create Batch** | POST | `/api/company/inventory/batches/` | `BatchRepository.create()` | Create new inbound batch |
| **Update Batch** | PATCH | `/api/company/inventory/batches/{batch_id}` | `BatchRepository.update()` | Update metadata (lot, notes, status) |
| **Delete Batch** | DELETE | `/api/company/inventory/batches/{batch_id}` | `BatchRepository.delete()` | Soft delete batch |
| **Get Product Batches** | GET | `/api/company/products/{product_id}/batches` | `BatchRepository.list(product_id=)` | Batch drill-down for product |

### 3.2 Inventory Movement Operations

| Operation | Method | Endpoint | Service Method | Description |
|-----------|--------|----------|----------------|-------------|
| **List Movements** | GET | `/api/company/inventory/movements/` | `InventoryMovementRepository.list()` | List with filtering |
| **Get Movement** | GET | `/api/company/inventory/movements/{id}` | `InventoryMovementRepository.get()` | Get single movement |
| **Create Movement** | POST | Internal only | `InventoryMovementRepository.create_movement()` | Create movement record |
| **Get Batch Movements** | GET | Via batch detail | `InventoryMovementRepository.get_movements_for_batch()` | All movements for batch |

### 3.3 Company Inventory Settings Operations

| Operation | Method | Endpoint | Service Method | Description |
|-----------|--------|----------|----------------|-------------|
| **Get Settings** | GET | `/api/company/inventory/settings/` | `CompanyInventorySettingRepository.get_by_company()` | Get company settings |
| **Create/Update Settings** | POST | `/api/company/inventory/settings/` | `CompanyInventorySettingRepository.create_or_update()` | Enable/configure batch tracking |
| **Update Consistency Settings** | PATCH | `/api/company/inventory/settings/consistency` | Direct SQLAlchemy | Update consistency check params |
| **Get Consistency Settings** | GET | `/api/company/inventory/settings/consistency` | Direct SQLAlchemy | Get consistency settings |
| **Enable with Migration** | POST | `/api/company/inventory/settings/enable-with-migration` | `CompanyInventorySettingService.enable_batch_tracking()` | Enable and run migration |

### 3.4 Batch Allocation Operations

| Operation | Method | Endpoint | Service Method | Description |
|-----------|--------|----------|----------------|-------------|
| **Allocate for Sales** | POST | `/api/company/sales/{sales_order_id}/allocate` | `BatchAllocationService.allocate()` | Server-side batch allocation |
| **Process Return** | POST | `/api/company/sales/{sales_order_id}/returns` | `BatchAllocationService.process_return()` | Handle sales returns |
| **Get Allocations** | GET | `/api/company/inventory/batches/allocations/` | `SalesOrderBatchAllocationRepository.get_all()` | List all allocations |

### 3.5 Consistency & Reconciliation Operations

| Operation | Method | Endpoint | Service Method | Description |
|-----------|--------|----------|----------------|-------------|
| **Consistency Check** | GET | `/api/company/inventory/batches/consistency-check` | `InventorySyncService.verify_all_invariants()` | Check batch-stock alignment |
| **Sync Stock to Batch** | POST | `/api/company/inventory/batches/consistency-check/sync` | `InventorySyncService.sync_inventory_to_batch()` | Reconcile stock to match batches |
| **Manual Consistency Check** | GET | `/api/company/inventory/batches/consistency/manual-check` | `InventorySyncService.verify_invariant()` | Check specific product/location |
| **Approve Repair** | POST | `/api/company/inventory/batches/consistency/repair` | `InventorySyncService.sync_inventory_to_batch()` | Repair specific discrepancy |
| **Bulk Repair** | POST | `/api/company/inventory/batches/consistency/repair/bulk` | Multiple `sync_inventory_to_batch()` | Bulk repair operation |
| **Get Reconciliation** | GET | `/api/company/inventory/reconciliation/` | Custom query | Full reconciliation report |
| **Run Backfill** | POST | `/api/company/inventory/reconciliation/backfill` | Migration service | Historical data backfill |
| **Sales Backfill** | POST | `/api/company/inventory/reconciliation/backfill-sales` | Migration service | Sales order backfill |

### 3.6 Stock-to-Batch Operations

| Operation | Method | Endpoint | Service Method | Description |
|-----------|--------|----------|----------------|-------------|
| **Preview Consolidation** | GET | `/api/company/inventory/reconciliation/stock-to-batch` | `StockToBatchService.preview_consolidation()` | Dry-run preview |
| **Execute Consolidation** | POST | `/api/company/inventory/reconciliation/stock-to-batch` | `StockToBatchService.execute_consolidation()` | Run consolidation |

### 3.7 Report Operations

| Operation | Method | Endpoint | Service Method | Description |
|-----------|--------|----------|----------------|-------------|
| **Stock by Batch** | GET | `/api/company/reports/stock-by-batch` | `BatchRepository.list()` | All batch stock with value |
| **Inventory Aging** | GET | `/api/company/reports/inventory-aging` | Custom aggregation | Age-based inventory analysis |
| **COGS by Period** | GET | `/api/company/reports/cogs-by-period` | Movement aggregation | Period-based COGS |
| **Batch P&L** | GET | `/api/company/reports/batch-pnl` | Batch + movement aggregation | Per-batch profit/loss |
| **Margin Analysis** | GET | `/api/company/reports/margin-analysis` | Allocation aggregation | Product margin analysis |

---

## 4. Frontend UI Walkthrough

### 4.1 Pages Inventory

| Page | Route | Status | Description |
|------|-------|--------|-------------|
| **Batch Drill-Down** | `/inventory/batch-drilldown` | ✅ Complete | Main batch management interface with filters and detail modal |
| **Movement Ledger** | `/inventory/movement-ledger` | ✅ Complete | Complete inventory movement history with filtering |
| **Batch Reconciliation** | `/inventory/reconciliation` | ✅ Complete | Batch vs stock reconciliation report |
| **Backfill** | `/inventory/backfill` | ⚠️ Partial | Historical data migration interface |
| **Stock to Batch** | `/inventory/stock-to-batch` | ✅ Complete | Legacy stock consolidation tool |
| **Allocations** | `/inventory/allocations` | ✅ Complete | Sales order batch allocations view |
| **Drift Approvals** | `/inventory/drift-approvals` | ⚠️ Partial | Consistency repair approval workflow |
| **Stock by Batch Report** | `/reports/inventory/stock-by-batch` | ✅ Complete | Inventory valuation by batch |
| **Inventory Aging (Batch)** | `/reports/inventory/inventory-aging-batch` | ✅ Complete | Age-based inventory analysis |
| **COGS by Period** | `/reports/inventory/cogs-by-period` | ✅ Complete | Period-based cost of goods sold |
| **Margin Analysis** | `/reports/inventory/margin-analysis` | ✅ Complete | Product profitability analysis |
| **Batch P&L** | `/reports/inventory/batch-pnl` | ✅ Complete | Per-batch profit and loss report |

### 4.2 Forms & Modals

| Component | File Path | Purpose |
|-----------|-----------|---------|
| **Batch Detail Modal** | `BatchDrillDown.tsx` (inline) | Display batch info + movement history |
| **Allocation Detail Modal** | `SalesOrderBatchAllocations.tsx` (inline) | Show allocation + batch details |
| **Stock to Batch Confirmation** | `StockToBatch.tsx` (AlertDialog) | Execute confirmation dialog |

### 4.3 Shared Components

| Component | File Path | Purpose |
|-----------|-----------|---------|
| **BatchDeleteButton** | `src/components/shared/BatchDeleteButton.tsx` | Batch deletion with confirmation |
| **Status Badge** | `src/pages/inventory/BatchDrillDown.tsx` | Status color mapping (active/depleted/expired) |
| **Movement Type Badge** | `src/pages/inventory/MovementLedger.tsx` | Movement type colors and icons |

### 4.4 Context Providers

| Context | File Path | Purpose |
|-----------|-----------|---------|
| **Auth Context** | `src/hooks/useAuth.ts` | User authentication and company context |
| **Query Client** | `src/lib/queryClient.ts` | TanStack Query configuration |
| **API Client** | `src/lib/api.ts` | Base API configuration |

### 4.5 API Layer

| API File | Key Functions |
|----------|---------------|
| `src/lib/api/batchApi.ts` | `getBatches()`, `getBatch()`, `createBatch()`, `updateBatch()`, `getCompanyInventorySettings()`, `getStockByBatchReport()`, `getInventoryAgingReport()`, `getCOGSByPeriodReport()`, `getBatchPNLReport()`, `getMarginAnalysisReport()`, `getMovementLedger()`, `getReconciliationReport()`, `runBackfill()`, `previewStockToBatch()`, `executeStockToBatch()`, `getSalesOrderBatchAllocations()`, `getConsistencyCheck()`, `approveRepair()`, `syncStockToBatch()` |

### 4.6 Types & Zod Schemas

| Schema | File | Fields |
|--------|------|--------|
| **Batch** | `src/lib/schema/batch.ts` | `batch_id`, `product_id`, `variant_id`, `qty_received`, `qty_on_hand`, `unit_cost`, `received_date`, `supplier_id`, `lot_number`, `status`, `location_id`, `is_synthetic`, `source_type` |
| **BatchListItem** | `src/lib/schema/batch.ts` | `batch_id`, `product_id`, `product_name`, `variant_id`, `variant_sku`, `qty_received`, `qty_on_hand`, `unit_cost`, `received_date`, `supplier_name`, `lot_number`, `status`, `location_name`, `age_days` |
| **BatchDetailResponse** | `src/lib/schema/batch.ts` | Extends Batch + `product_name`, `variant_sku`, `source_type`, `purchase_order_detail_id`, `movements` |
| **BatchCreate** | `src/lib/schema/batch.ts` | `product_id`, `variant_id`, `qty_received`, `unit_cost`, `received_date`, `supplier_id`, `lot_number`, `location_id`, `purchase_order_detail_id`, `source_type` |
| **BatchUpdate** | `src/lib/schema/batch.ts` | `lot_number`, `notes` |
| **InventoryMovement** | `src/lib/schema/batch.ts` | `movement_id`, `batch_id`, `product_id`, `product_name`, `variant_id`, `variant_sku`, `qty`, `movement_type`, `ref_type`, `ref_id`, `unit_cost_at_txn`, `actor`, `actor_name`, `txn_timestamp`, `location_name`, `notes`, `related_movement_id` |
| **CompanyInventorySetting** | `src/lib/schema/batch.ts` | `setting_id`, `company_id`, `valuation_mode`, `batch_tracking_enabled` |
| **SalesOrderBatchAllocation** | `src/lib/schema/batch.ts` | `allocation_id`, `sales_order_detail_id`, `batch_id`, `qty_allocated`, `unit_cost_at_allocation`, `movement_id` |
| **SalesOrderBatchAllocationResponse** | `src/lib/schema/batch.ts` | `allocation_id`, `sales_order_id`, `sales_order_number`, `sales_order_detail_id`, `product_id`, `product_name`, `variant_id`, `variant_sku`, `batch_id`, `batch_number`, `qty_allocated`, `unit_cost_at_allocation`, `total_cogs`, `movement_id`, `allocated_at`, `allocated_by` |
| **BatchStockReportItem** | `src/lib/schema/batch.ts` | `batch_id`, `product_id`, `product_name`, `variant_sku`, `qty_on_hand`, `unit_cost`, `total_value`, `location_name`, `received_date`, `age_days`, `status` |
| **InventoryAgingItem** | `src/lib/schema/batch.ts` | `product_id`, `product_name`, `variant_sku`, `location_id`, `location_name`, `total_qty`, `avg_cost`, `total_value`, `aging_buckets` (0-30, 31-60, 61-90, 91-180, 180+) |
| **BatchPNLItem** | `src/lib/schema/batch.ts` | `batch_id`, `product_name`, `variant_sku`, `qty_sold`, `unit_cost`, `total_cost`, `revenue`, `profit`, `margin_percent` |
| **StockToBatchPreviewResponse** | `src/lib/schema/batch.ts` | `to_create`, `to_update`, `to_skip`, `total_products`, `details`, `warnings` |
| **StockToBatchExecuteResponse** | `src/lib/schema/batch.ts` | `to_create`, `to_update`, `to_skip`, `batches_created`, `movements_created`, `errors`, `warnings` |
| **ConsistencyCheckResponse** | `src/lib/api/batchApi.ts` (inline) | `message`, `company_id`, `batch_tracking_enabled`, `valuation_mode`, `consistency`, `discrepancies` |
| **RepairResponse** | `src/lib/api/batchApi.ts` (inline) | `success`, `message`, `product_id`, `variant_id`, `location_id`, `repair_type`, `old_quantity`, `new_quantity` |

**CRITICAL-030 FIX:** All numeric fields (quantities, costs) use `DecimalField = string | number` type to handle Python Decimal serialization to JSON strings.

---

## 5. Interconnected Workflows

### 5.1 Purchase Receipt Batch Creation Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ PURCHASE ORDER DELIVERY → BATCH CREATION FLOW                                │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ Step 1: Purchase Order Delivery Created            │
│ → PO Delivery service receives delivery completion │
│ → Creates delivery_detail records for each item    │
└─────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────┐
│ Step 2: Batch Creation Triggered                   │
│ → PO service calls BatchAllocationService          │
│ → Method: create_batch_for_purchase_receipt()      │
└─────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────┐
│ Step 3: Validation                                   │
│ → Check qty_received > 0                             │
│ → Check unit_cost >= 0                               │
│ → Validate lot_number uniqueness (optional)        │
│ → Check for existing batch (delivery_detail_id)      │
└─────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────┐
│ Step 4: Batch Record Created                         │
│ → Insert into inventory.batch                        │
│ → Set qty_on_hand = qty_received                     │
│ → Set status = 'active'                              │
│ → Set source_type = 'purchase'                       │
│ → Link to purchase_order_detail_id                   │
│ → Link to delivery_detail_id (for partial)         │
└─────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────┐
│ Step 5: Inventory Movement Created                   │
│ → Insert into inventory.inventory_movement         │
│ → movement_type = 'IN'                               │
│ → ref_type = 'PURCHASE_DELIVERY'                     │
│ → qty = positive (received quantity)                 │
│ → unit_cost_at_txn = batch unit_cost                 │
└─────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────┐
│ Step 6: Inventory Stock Updated (Phase 1)            │
│ → InventorySyncService.mutate_stock() called       │
│ → Updates inventory_stock.quantity                   │
│ → Maintains batch-stock invariant                    │
└─────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────┐
│ Step 7: Response                                     │
│ → Return BatchCreationResult                         │
│   {batch_id, movement_id}                            │
└─────────────────────────────────────────────────────┘
```

### 5.2 Sales Order Batch Allocation Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ SALES ORDER DELIVERY → BATCH ALLOCATION FLOW                                │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ Step 1: Sales Order Delivery Initiated             │
│ → Sales order status = 'delivering'                │
│ → User selects location for fulfillment            │
│ → System checks batch_tracking_enabled             │
└─────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────┐
│ Step 2: Allocation Request                           │
│ → Frontend calls: POST /sales/{id}/allocate        │
│ → Body: {sales_order_detail_id, qty_to_allocate,  │
│          location_id}                                │
│ → BatchAllocationService.allocate() invoked        │
└─────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────┐
│ Step 3: Valuation Mode Determination                 │
│ → Get company valuation_mode (FIFO/LIFO/WAC)       │
│ → Call appropriate allocation method                 │
└─────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────┐
│ Step 4: Batch Selection (FIFO Example)               │
│ → Query: active batches with qty_on_hand > 0       │
│ → Filter: product_id, variant_id, location_id      │
│ → Order: received_date ASC (oldest first)            │
│ → Exclude: expired batches (expiry_date > now)     │
│ → Lock: SELECT FOR UPDATE SKIP LOCKED                │
└─────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────┐
│ Step 5: Allocation Execution                         │
│ FOR each batch in ordered list:                     │
│   → Calculate alloc_qty = min(needed, on_hand)     │
│   → Decrement batch.qty_on_hand                      │
│   → Create OUT movement (negative qty)               │
│   → Create sales_order_batch_allocation record       │
│   → Reduce remaining_needed                          │
│   → IF remaining_needed = 0: break                   │
└─────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────┐
│ Step 6: Stock Update                                 │
│ → InventorySyncService.mutate_stock()              │
│ → Decrement inventory_stock.quantity                 │
│ → Verify invariant: batch_total == stock_qty       │
└─────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────┐
│ Step 7: Response                                     │
│ → Return AllocationResponse                          │
│   {allocations[], total_qty_allocated, total_cogs,   │
│    valuation_mode}                                   │
└─────────────────────────────────────────────────────┘
```

### 5.3 Sales Return Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ SALES RETURN → BATCH REVERSAL FLOW                                          │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ Step 1: Return Initiated                             │
│ → User creates sales return                          │
│ → Specifies qty_returned per line item               │
│ → System retrieves original allocations              │
└─────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────┐
│ Step 2: Process Return                               │
│ → Call: BatchAllocationService.process_return()    │
│ → Get original allocations (reverse order)         │
└─────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────┐
│ Step 3: Return to Original Batches                   │
│ FOR each original allocation:                       │
│   → Check: batch still active and not deleted        │
│   → Calculate: return_capacity = allocated - already_returned │
│   → IF return_capacity > 0:                         │
│     → Increment batch.qty_on_hand                    │
│     → Create RETURN_IN movement (positive qty)       │
│     → Link to original OUT movement                  │
│     → Update allocation.qty_allocated (reduce)       │
│     → IF allocation.qty_allocated <= 0: soft delete  │
└─────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────┐
│ Step 4: Synthetic Batch Creation (if needed)       │
│ → IF original batch deleted/depleted:               │
│   → Create new batch with is_synthetic = TRUE       │
│   → Set source_type = 'return'                       │
│   → Use original unit_cost_at_allocation             │
│   → Create RETURN_IN movement for synthetic batch    │
└─────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────┐
│ Step 5: Stock Update                                 │
│ → InventorySyncService.mutate_stock()              │
│ → Increment inventory_stock.quantity                 │
└─────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────┐
│ Step 6: Response                                     │
│ → Return ReturnResponse                              │
│   {return_movements[], total_returned, credit_amount}│
└─────────────────────────────────────────────────────┘
```

### 5.4 Stock-to-Batch Consolidation Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ STOCK TO BATCH CONSOLIDATION FLOW                                           │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ Step 1: Preview Request                              │
│ → User clicks "Run Preview" on StockToBatch page   │
│ → API: GET /inventory/reconciliation/stock-to-batch │
│ → Service: StockToBatchService.preview_consolidation()│
└─────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────┐
│ Step 2: Aggregate Stock                              │
│ → Query inventory_stock grouped by:                 │
│   (product_id, variant_id, location_id)             │
│ → SUM(quantity) for each group                       │
│ → Filter: quantity > 0                               │
└─────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────┐
│ Step 3: Get Purchase Prices                          │
│ → For each product/variant:                         │
│   → Query ProductPrice table                         │
│   → Priority: variant-specific > product-level     │
│   → Order: effective_date DESC (most recent)       │
│   → IF no price found: use 0, add warning            │
└─────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────┐
│ Step 4: Determine Action per Item                    │
│ FOR each (product, variant, location) aggregate:  │
│   → Check existing batch                             │
│   → IF no batch exists: action = 'create'            │
│   → IF synthetic batch exists: action = 'update'     │
│   → IF non-synthetic batch exists: action = 'skip'   │
│     → Add warning: "Non-synthetic batch exists"      │
└─────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────┐
│ Step 5: Preview Response                             │
│ → Return ConsolidationResult                         │
│   {to_create, to_update, to_skip, total_products,   │
│    details[], warnings[]}                             │
└─────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────┐
│ Step 6: Execute (User Confirms)                      │
│ → User switches to "Execute" mode                    │
│ → Clicks "Execute Consolidation"                     │
│ → Confirmation dialog shown                          │
│ → API: POST /inventory/reconciliation/stock-to-batch │
└─────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────┐
│ Step 7: Execution (Per-Item Transactions)            │
│ FOR each item with action = 'create':                │
│   → BEGIN nested transaction (savepoint)            │
│   → Create synthetic batch                           │
│   → Create OPENING_BALANCE movement                  │
│   → COMMIT savepoint                                 │
│   → Increment counters                                 │
│   
│ FOR each item with action = 'update':                │
│   → BEGIN nested transaction                         │
│   → Update existing synthetic batch qty/unit_cost    │
│   → COMMIT savepoint                                 │
│   
│ IF error on any item:                               │
│   → ROLLBACK savepoint (only affects current item)  │
│   → Add to errors[]                                    │
│   → Continue to next item                              │
└─────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────┐
│ Step 8: Execution Response                           │
│ → Return ConsolidationResult                         │
│   {batches_created, movements_created, errors[],     │
│    warnings[], to_create, to_update, to_skip}        │
└─────────────────────────────────────────────────────┘
```

### 5.5 Consistency Check & Repair Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ CONSISTENCY CHECK & REPAIR FLOW                                           │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ Step 1: Manual Check Triggered                       │
│ → User navigates to Reconciliation page            │
│ → Clicks "Refresh" or "Run Consistency Check"      │
│ → API: GET /inventory/batches/consistency-check    │
└─────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────┐
│ Step 2: Verify All Invariants                        │
│ → InventorySyncService.verify_all_invariants()     │
│ → For each (product, variant, location) combo:    │
│   → Get batch_total = SUM(qty_on_hand)             │
│   → Get stock_qty from inventory_stock               │
│   → Calculate difference = ABS(batch_total - stock_qty)│
│   → IF difference > tolerance: mark invalid        │
└─────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────┐
│ Step 3: Check Response                               │
│ → Return ConsistencyCheckResponse                    │
│   {                                                   │
│     message: "Found X discrepancies",               │
│     consistency: {total_checked, valid_count,      │
│                     invalid_count, all_valid},        │
│     discrepancies: [                                │
│       {product_id, variant_id, location_id,          │
│        batch_total, stock_quantity, difference,       │
│        product_name, location_name}                   │
│     ]                                                 │
│   }                                                   │
└─────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────┐
│ Step 4: Review Discrepancies (if any)                │
│ → UI displays mismatches table                       │
│ → Shows: product name, batch qty, stock qty,        │
│          difference, status                           │
│ → User reviews each discrepancy                      │
└─────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────┐
│ Step 5: Approve Repair                               │
│ → User clicks "Approve Repair" on specific item      │
│ → Or "Bulk Approve" for multiple items               │
│ → API: POST /inventory/batches/consistency/repair  │
│   Params: product_id, location_id, variant_id,      │
│             repair_type (default: sync_to_batch)    │
└─────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────┐
│ Step 6: Execute Repair                               │
│ → InventorySyncService.sync_inventory_to_batch()     │
│ → Strategy: sync_to_batch (update stock to match)    │
│   → Update inventory_stock.quantity = batch_total    │
│   → Log the repair operation                         │
│   → IF strict mode: verify after repair              │
└─────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────┐
│ Step 7: Repair Response                                │
│ → Return RepairResponse                                │
│   {                                                   │
│     success: true/false,                              │
│     message: "Stock synced successfully",             │
│     product_id, variant_id, location_id,             │
│     repair_type: "sync_to_batch",                     │
│     old_quantity: X,                                  │
│     new_quantity: Y                                   │
│   }                                                   │
└─────────────────────────────────────────────────────┘
```

---

## 6. Special Features Deep-Dive

### 6.1 FIFO/LIFO/Weighted Average Valuation

**Overview:** The system supports three inventory valuation methods configured per company via `CompanyInventorySetting.valuation_mode`.

**FIFO (First In First Out):**
```python
# Oldest batches are allocated first
batches = query.order_by(
    Batch.received_date.asc(),  # Oldest first
    Batch.batch_id.asc()
).all()
```

**LIFO (Last In First Out):**
```python
# Newest batches are allocated first
batches = query.order_by(
    Batch.received_date.desc(),  # Newest first
    Batch.batch_id.desc()
).all()
```

**Weighted Average (WEIGHTED_AVG):**
```sql
-- Calculate average cost across all batches
SELECT 
    SUM(qty_on_hand * unit_cost) / NULLIF(SUM(qty_on_hand), 0) as avg_cost,
    SUM(qty_on_hand) as total_on_hand
FROM inventory.batch
WHERE company_id = :company_id
  AND product_id = :product_id
  AND variant_id <=> :variant_id  -- NULL-safe equals
  AND location_id = :location_id
  AND qty_on_hand > 0
  AND status = 'active'
```

**Allocation with Cost Override:**
```python
def _allocate_batches_with_cost(
    self,
    company_id: int,
    product_id: int,
    variant_id: Optional[int],
    location_id: int,
    qty_needed: Decimal,
    sales_order_detail_id: int,
    user_id: int,
    order_by_fifo: bool,
    override_cost: Optional[Decimal] = None,  # WAC uses this
):
    for batch in batches:
        alloc_qty = min(remaining, batch.qty_on_hand)
        unit_cost = override_cost if override_cost is not None else batch.unit_cost
        # Create allocation with computed/average cost
```

### 6.2 Optimistic Locking & Concurrency Control

**Version Column:**
```python
class Batch(Base):
    version = Column(Integer, nullable=False, default=0)
    __mapper_args__ = {"version_id_col": version}
```

**SELECT FOR UPDATE SKIP LOCKED:**
```python
def lock_and_get_batches_for_allocation(
    self, company_id, product_id, variant_id, location_id, order_by_fifo
):
    # PostgreSQL: Skip already-locked rows
    sql = """
        SELECT batch_id FROM inventory.batch 
        WHERE company_id = :company_id
          AND product_id = :product_id
          AND variant_id = :variant_id
          AND location_id = :location_id
          AND qty_on_hand > 0
          AND status = 'active'
          AND is_deleted = FALSE
          AND (expiry_date IS NULL OR expiry_date > NOW())
        ORDER BY received_date ASC, batch_id ASC
        FOR UPDATE SKIP LOCKED  -- Key: skip locked rows
    """
```

**Nested Transactions (Savepoints):**
```python
def _allocate_batches_with_cost(self, ...):
    savepoint = self.db.begin_nested()  # Create savepoint
    try:
        # Perform all allocations
        for batch in batches:
            self.batch_repo.decrement_qty_on_hand(...)
            self.movement_repo.create_movement(...)
            self.allocation_repo.create_allocation(...)
        # Savepoint automatically committed if no exception
        return allocations
    except Exception as e:
        savepoint.rollback()  # Rollback only this allocation
        raise e
```

### 6.3 Batch-Stock Invariant Enforcement

**Phase 0 Invariant:** When batch tracking is enabled, `batch` is the source of truth and `inventory_stock` is a denormalized mirror.

```python
class InventorySyncService:
    def verify_invariant(
        self, company_id, product_id, variant_id, location_id, tolerance
    ):
        batch_total = self.get_batch_total_qty(...)
        stock_qty = self.get_inventory_stock_qty(...)
        
        difference = abs(batch_total - stock_qty)
        is_valid = difference <= tolerance
        
        return is_valid, {
            "batch_total": batch_total,
            "stock_quantity": stock_qty,
            "difference": difference,
            "is_valid": is_valid
        }
```

**Mutation Guard:**
```python
def block_stock_mutation_in_batch_mode(db, company_id, operation):
    """Block direct inventory_stock mutations when batch tracking is enabled."""
    sync_service = InventorySyncService(db)
    
    # Check if migration is in progress
    sync_service.validate_no_migration_lock(company_id)
    
    # Check batch mode
    if sync_service.is_batch_tracking_enabled(company_id):
        raise BatchModeViolationError(
            f"Cannot {operation} directly. "
            f"Batch tracking is enabled - use batch operations instead."
        )
```

### 6.4 Expiry Date Tracking

**Model Properties:**
```python
class Batch(Base):
    expiry_date = Column(TIMESTAMP, nullable=True)
    
    @property
    def is_expired(self) -> bool:
        if not self.expiry_date:
            return False
        return datetime.now() > self.expiry_date
    
    @property
    def is_near_expiry(self, days_threshold: int = 30) -> bool:
        if not self.expiry_date:
            return False
        return datetime.now() + timedelta(days=days_threshold) > self.expiry_date
```

**Allocation Filter:**
```python
query = query.filter(
    or_(
        Batch.expiry_date == None,  # No expiry
        Batch.expiry_date > datetime.now()  # Not expired
    )
)
```

### 6.5 Soft Delete Pattern

**All batch entities implement soft delete:**

```python
class Batch(Base, IsDeletedMixin):
    is_deleted = Column(Boolean, nullable=False, default=False)
    
    def delete(self, batch_obj):
        """Soft delete - never hard delete."""
        batch_obj.is_deleted = True
        batch_obj.md = func.now()
        self.db.flush()
```

**Query Filtering:**
```python
# All queries automatically filter out deleted records
query = self.db.query(Batch).filter(
    Batch.is_deleted == False  # Never show deleted
)
```

### 6.6 Decimal Precision Handling

**Frontend CRITICAL-030 Fix:**
```typescript
// Python Decimal serializes to string in JSON
export type DecimalField = string | number;

// Helper function for safe number parsing
export const getBatchQtyOnHand = (batch: { qty_on_hand?: DecimalField }): number => {
    const { parseSafeNumber } = require('../utils/numberUtils');
    return parseSafeNumber(batch.qty_on_hand, 0);
};

// Usage in components
const qty = parseSafeNumber(batch.qty_on_hand, 0);
const cost = parseSafeNumber(batch.unit_cost, 0);
const total = qty * cost;  // Safe calculation
```

### 6.7 JSON Field Storage

**DSR Stock Movement Details:**
```python
class DSRStockMovement(Base):
    # Changed from String(2000) to Text for large orders
    details = Column(Text, nullable=True)  # JSON string of items
    
    # Example JSON structure:
    # {
    #   "items": [
    #     {"product_id": 1, "variant_id": 2, "qty": 10, "batch_id": 5},
    #     {"product_id": 3, "variant_id": null, "qty": 5, "batch_id": 8}
    #   ],
    #   "total_items": 2,
    #   "total_qty": 15
    # }
```

### 6.8 Multi-Tenancy Implementation

**Company ID Filtering:**
```python
# Every batch query includes company_id filter
query = self.db.query(Batch).filter(
    Batch.company_id == company_id,  # Multi-tenant isolation
    Batch.is_deleted == False
)

# Settings are per-company with unique constraint
class CompanyInventorySetting(Base):
    company_id = Column(
        Integer, 
        ForeignKey("security.app_client_company.company_id"),
        nullable=False,
        unique=True  # One setting per company
    )
```

---

## 7. API Quick Reference

### 7.1 Endpoint Summary by Entity

| Entity | List | Get | Create | Update | Delete | Special |
|--------|------|-----|--------|--------|--------|---------|
| **Batch** | `GET /inventory/batches/` | `GET /inventory/batches/{id}` | `POST /inventory/batches/` | `PATCH /inventory/batches/{id}` | Soft delete internal | `GET /inventory/batches/allocations/` |
| **Movement** | `GET /inventory/movements/` | `GET /inventory/movements/{id}` | Internal only | N/A | N/A | Via batch detail |
| **Settings** | N/A | `GET /inventory/settings/` | `POST /inventory/settings/` | `PATCH /inventory/settings/consistency` | N/A | `POST /inventory/settings/enable-with-migration` |
| **Allocation** | `GET /inventory/batches/allocations/` | N/A | `POST /sales/{id}/allocate` | N/A | N/A | `POST /sales/{id}/returns` |
| **Reports** | Various | N/A | N/A | N/A | N/A | See 3.7 |
| **Reconciliation** | `GET /inventory/batches/consistency-check` | N/A | `POST /inventory/batches/consistency-check/sync` | `POST /inventory/batches/consistency/repair` | N/A | `GET /inventory/reconciliation/` |
| **Stock-to-Batch** | `GET /inventory/reconciliation/stock-to-batch` (preview) | N/A | `POST /inventory/reconciliation/stock-to-batch` (execute) | N/A | N/A | N/A |

### 7.2 Frontend API Function Map

| Operation | Frontend Function | Backend Endpoint |
|-----------|-----------------|------------------|
| List batches | `getBatches(params)` | `GET /inventory/batches/` |
| Get batch detail | `getBatch(batchId)` | `GET /inventory/batches/{id}` |
| Create batch | `createBatch(data)` | `POST /inventory/batches/` |
| Update batch | `updateBatch(batchId, data)` | `PATCH /inventory/batches/{id}` |
| Get settings | `getCompanyInventorySettings()` | `GET /inventory/settings/` |
| Update settings | `updateCompanyInventorySettings(data)` | `POST /inventory/settings/` |
| Get allocations | `getSalesOrderBatchAllocations(params)` | `GET /inventory/batches/allocations/` |
| Get movements | `getMovementLedger(params)` | `GET /inventory/movements/` |
| Stock by batch report | `getStockByBatchReport(params)` | `GET /reports/stock-by-batch` |
| Inventory aging | `getInventoryAgingReport(params)` | `GET /reports/inventory-aging` |
| COGS report | `getCOGSByPeriodReport(params)` | `GET /reports/cogs-by-period` |
| Batch P&L | `getBatchPNLReport(params)` | `GET /reports/batch-pnl` |
| Margin analysis | `getMarginAnalysisReport(params)` | `GET /reports/margin-analysis` |
| Reconciliation | `getReconciliationReport()` | `GET /inventory/reconciliation/` |
| Preview stock-to-batch | `previewStockToBatch()` | `GET /inventory/reconciliation/stock-to-batch` |
| Execute stock-to-batch | `executeStockToBatch(userId)` | `POST /inventory/reconciliation/stock-to-batch` |
| Consistency check | `getConsistencyCheck()` | `GET /inventory/batches/consistency-check` |
| Approve repair | `approveRepair(productId, locationId, variantId)` | `POST /inventory/batches/consistency/repair` |
| Sync stock to batch | `syncStockToBatch(productId, locationId, variantId)` | `POST /inventory/batches/consistency/repair` |
| Bulk repair | `bulkApproveRepair(repairs[])` | `POST /inventory/batches/consistency/repair/bulk` |

---

## 8. File Map

### 8.1 Backend Files

| Layer | File Path | Purpose |
|-------|-----------|---------|
| **Models** | `Shoudagor/app/models/batch_models.py` | All batch-related entities: Batch, InventoryMovement, CompanyInventorySetting, SalesOrderBatchAllocation, DSRBatchAllocation, DSRStockMovement, StockMutationAudit, BatchQtyAuditLog |
| **Schemas** | `Shoudagor/app/schemas/inventory/batch.py` | Pydantic schemas: BatchCreate, BatchUpdate, BatchResponse, BatchListItem, InventoryMovementCreate, InventoryMovementResponse, AllocationRequest, AllocationResponse, ReturnRequest, ReturnResponse, all report schemas |
| **API - Batch** | `Shoudagor/app/api/inventory/batch.py` | Batch CRUD, settings, consistency checks, stock-to-batch, allocations |
| **API - Allocation** | `Shoudagor/app/api/sales/batch_allocation.py` | Sales order allocation, returns, all report endpoints |
| **Repository** | `Shoudagor/app/repositories/inventory/batch.py` | BatchRepository, InventoryMovementRepository, SalesOrderBatchAllocationRepository, CompanyInventorySettingRepository |
| **Service - Allocation** | `Shoudagor/app/services/inventory/batch_allocation_service.py` | Core allocation logic: FIFO, LIFO, WAC, batch creation, returns |
| **Service - Stock-to-Batch** | `Shoudagor/app/services/inventory/stock_to_batch_service.py` | Legacy stock consolidation service |
| **Service - Sync** | `Shoudagor/app/services/inventory/inventory_sync_service.py` | Stock mutation, invariant verification, consistency checks |
| **Service - Guard** | `Shoudagor/app/services/inventory/batch_guard.py` | Batch mode enforcement utilities |
| **Dependencies** | `Shoudagor/app/dependencies.py` | get_current_user, get_current_company_id for multi-tenancy |

### 8.2 Frontend Files

| Layer | File Path | Purpose |
|-------|-----------|---------|
| **Pages - Main** | `shoudagor_FE/src/pages/inventory/BatchDrillDown.tsx` | Main batch management with filters and detail modal |
| **Pages - Main** | `shoudagor_FE/src/pages/inventory/MovementLedger.tsx` | Complete movement history with filtering |
| **Pages - Main** | `shoudagor_FE/src/pages/inventory/BatchReconciliation.tsx` | Batch vs stock reconciliation view |
| **Pages - Main** | `shoudagor_FE/src/pages/inventory/StockToBatch.tsx` | Legacy stock consolidation interface |
| **Pages - Main** | `shoudagor_FE/src/pages/inventory/SalesOrderBatchAllocations.tsx` | Sales order allocations view |
| **Pages - Main** | `shoudagor_FE/src/pages/inventory/BatchBackfill.tsx` | Historical data migration |
| **Pages - Main** | `shoudagor_FE/src/pages/inventory/DriftApprovals.tsx` | Consistency repair approvals |
| **Pages - Reports** | `shoudagor_FE/src/pages/reports/inventory/StockByBatch.tsx` | Stock valuation by batch report |
| **Pages - Reports** | `shoudagor_FE/src/pages/reports/inventory/InventoryAgingBatch.tsx` | Age-based inventory analysis |
| **Pages - Reports** | `shoudagor_FE/src/pages/reports/inventory/BatchPnL.tsx` | Per-batch P&L report |
| **Pages - Reports** | `shoudagor_FE/src/pages/reports/inventory/COGSByPeriod.tsx` | Period-based COGS report |
| **Pages - Reports** | `shoudagor_FE/src/pages/reports/inventory/MarginAnalysis.tsx` | Product margin analysis |
| **API Layer** | `shoudagor_FE/src/lib/api/batchApi.ts` | All batch API functions: CRUD, reports, reconciliation, consistency |
| **Types/Schemas** | `shoudagor_FE/src/lib/schema/batch.ts` | TypeScript interfaces: Batch, InventoryMovement, CompanyInventorySetting, all report types, helper functions |
| **Shared Components** | `shoudagor_FE/src/components/shared/BatchDeleteButton.tsx` | Batch deletion component |
| **Navigation** | `shoudagor_FE/src/data/navigation.ts` | Sidebar navigation menu entries for batch inventory |
| **Routing** | `shoudagor_FE/src/App.tsx` | Route definitions for all batch pages |

---

## 9. Appendix: Operation Counts

### 9.1 Entity Operation Summary

| Entity | Backend CRUD Ops | Backend Special Ops | Frontend API Functions | Frontend Components |
|--------|-----------------|---------------------|------------------------|---------------------|
| **Batch** | 5 (List, Get, Create, Update, Delete) | 4 (allocations, consistency check, sync, product drill-down) | 11 (getBatches, getBatch, createBatch, updateBatch, getProductBatches, etc.) | 5 (BatchDrillDown + modal, BatchDeleteButton, filters) |
| **InventoryMovement** | 3 (List, Get, Create) | 1 (get for batch) | 1 (getMovementLedger) | 1 (MovementLedger) |
| **CompanyInventorySetting** | 3 (Get, Create/Update, Patch) | 2 (consistency settings, enable with migration) | 2 (getCompanyInventorySettings, updateCompanyInventorySettings) | 0 (embedded in other pages) |
| **SalesOrderBatchAllocation** | 2 (List, Create) | 2 (process return, get by SO detail) | 1 (getSalesOrderBatchAllocations) | 1 (SalesOrderBatchAllocations + modal) |
| **Reconciliation/Consistency** | 0 | 6 (check, sync, repair, bulk repair, backfill, stock-to-batch) | 6 (getReconciliationReport, getConsistencyCheck, approveRepair, etc.) | 2 (BatchReconciliation, StockToBatch) |
| **Reports** | 0 | 6 (stock-by-batch, aging, COGS, P&L, margin, allocations) | 6 (getStockByBatchReport, getInventoryAgingReport, etc.) | 5 (StockByBatch, InventoryAgingBatch, BatchPnL, COGSByPeriod, MarginAnalysis) |
| **TOTAL** | **13** | **21** | **27** | **14** |

### 9.2 Valuation Method Support Matrix

| Feature | FIFO | LIFO | WEIGHTED_AVG |
|---------|------|------|---------------|
| Sales Allocation | ✅ Full | ✅ Full | ✅ Full |
| COGS Calculation | ✅ Accurate | ✅ Accurate | ✅ Average |
| Return Processing | ✅ Full | ✅ Full | ✅ Full |
| Report Support | ✅ All | ✅ All | ✅ All |
| Default Setting | ✅ Yes | ⚠️ Optional | ⚠️ Optional |

### 9.3 Status Workflow

```
BATCH STATUS LIFECYCLE
═══════════════════════

┌─────────┐     ┌─────────┐     ┌─────────┐
│  CREATED│────►│  ACTIVE │────►│DEPLETED │
│(implicit)│     │         │     │         │
└─────────┘     └────┬────┘     └─────────┘
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
   ┌─────────┐  ┌─────────┐  ┌─────────┐
   │ EXPIRED │  │RETURNED │  │QUARANTINED│
   │(auto)   │  │(manual) │  │ (manual)  │
   └─────────┘  └─────────┘  └─────────┘

Status Transitions:
• CREATED → ACTIVE: Automatic on batch creation
• ACTIVE → DEPLETED: Automatic when qty_on_hand = 0
• ACTIVE → EXPIRED: Automatic when expiry_date < now
• ACTIVE → RETURNED: Manual for returned-to-supplier
• ACTIVE → QUARANTINED: Manual for quality hold
• Any → ACTIVE: Manual reactivation possible
```

---

## Document End

**Note:** This documentation reflects the Batch Management module as of April 2026. For the most current implementation details, always refer to the source code in:
- Backend: `Shoudagor/app/` directory
- Frontend: `shoudagor_FE/src/` directory

**Key Implementation Phases:**
- **Phase 0:** Batch tracking foundation with FIFO/LIFO/WAC support
- **Phase 1:** Centralized stock mutation via InventorySyncService
- **Phase 2:** Partial delivery support with delivery_detail_id
- **Phase 3:** Consistency checking and repair workflows
- **Phase 4:** Enhanced reconciliation and drift approval workflows
