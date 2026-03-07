# Batch Inventory API Reference

## Base URLs

- Production: `https://api.yourdomain.com`
- Development: `http://localhost:8000`

## Authentication

All endpoints require Bearer token authentication:
```
Authorization: Bearer <token>
```

## Endpoints

### Batch Management

#### Create Batch

```
POST /api/company/inventory/batches
```

**Request Body:**
```json
{
  "product_id": 1,
  "variant_id": null,
  "qty_received": 100.00,
  "unit_cost": 10.50,
  "received_date": "2026-01-15T00:00:00",
  "supplier_id": 1,
  "lot_number": "LOT-001",
  "location_id": 1,
  "purchase_order_detail_id": 1,
  "source_type": "purchase"
}
```

**Response:**
```json
{
  "batch_id": 1,
  "product_id": 1,
  "qty_received": 100.00,
  "qty_on_hand": 100.00,
  "unit_cost": 10.50,
  ...
}
```

#### List Batches

```
GET /api/company/inventory/batches
```

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| product_id | int | Filter by product |
| variant_id | int | Filter by variant |
| location_id | int | Filter by location |
| supplier_id | int | Filter by supplier |
| status | string | Filter by status |
| include_depleted | bool | Include depleted batches |
| start | int | Pagination start |
| limit | int | Page size (max 100) |

#### Get Batch

```
GET /api/company/inventory/batches/{batch_id}
```

Returns batch details with movement history.

#### Update Batch

```
PATCH /api/company/inventory/batches/{batch_id}
```

**Request Body:**
```json
{
  "lot_number": "NEW-LOT",
  "notes": "Updated notes"
}
```

**Note:** Cannot modify `unit_cost` if batch has OUT movements.

---

### Movement Ledger

#### List Movements

```
GET /api/company/inventory/movements
```

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| batch_id | int | Filter by batch |
| product_id | int | Filter by product |
| movement_type | string | Filter by type |
| start | datetime | Start date filter |
| end | datetime | End date filter |

---

### Settings

#### Get Settings

```
GET /api/company/inventory/settings
```

**Response:**
```json
{
  "setting_id": 1,
  "company_id": 1,
  "valuation_mode": "FIFO",
  "batch_tracking_enabled": true
}
```

#### Update Settings

```
POST /api/company/inventory/settings
```

**Request Body:**
```json
{
  "valuation_mode": "FIFO",
  "batch_tracking_enabled": true
}
```

---

### Reconciliation

#### Get Reconciliation Report

```
GET /api/company/inventory/reconciliation
```

**Response:**
```json
{
  "company_id": 1,
  "total_items": 100,
  "matched": 95,
  "mismatched": 5,
  "items": [...]
}
```

#### Run Backfill

```
POST /api/company/inventory/reconciliation/backfill
```

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| dry_run | bool | true | Preview without committing |
| chunk_size | int | 500 | Records per chunk |

**Response:**
```json
{
  "dry_run": false,
  "batches_created": 50,
  "movements_created": 50,
  "errors": [],
  "warnings": []
}
```

---

### Reports

#### Stock by Batch

```
GET /api/company/inventory/reports/stock-by-batch
```

#### Inventory Aging

```
GET /api/company/inventory/reports/inventory-aging
```

#### COGS by Period

```
GET /api/company/reports/cogs-by-period
```

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| start_date | string | Start date (YYYY-MM-DD) |
| end_date | string | End date (YYYY-MM-DD) |

#### Margin Analysis

```
GET /api/company/reports/margin-analysis
```

#### Batch P&L

```
GET /api/company/reports/batch-pnl
```

---

### Allocation

#### Allocate Batch

```
POST /api/company/inventory/allocations
```

**Request Body:**
```json
{
  "sales_order_detail_id": 1,
  "quantity": 10.00
}
```

#### Process Return

```
POST /api/company/inventory/returns
```

**Request Body:**
```json
{
  "sales_order_detail_id": 1,
  "quantity": 5.00,
  "return_to_original_batch": true
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid request body"
}
```

### 404 Not Found
```json
{
  "detail": "Batch not found"
}
```

### 409 Conflict
```json
{
  "detail": "Cannot modify unit cost for a batch that has been used in sales"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## Rate Limits

- Standard: 100 requests/minute
- Batch operations: 20 requests/minute

---

## Versioning

Current API version: `v1`

Include in request header:
```
Accept: application/json; version=v1
```
