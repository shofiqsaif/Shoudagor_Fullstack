# SR & DSR Reports - Detailed Study and Implementation Plan

> **Created:** 2026-03-31  
> **Status:** Ready for Implementation  
> **Estimated Effort:** 8-12 hours (Full Stack)

---

## Table of Contents
1. [Feature Requirements](#1-feature-requirements)
2. [Data Model Study](#2-data-model-study)
3. [Existing Pattern Analysis](#3-existing-pattern-analysis)
4. [Backend Implementation](#4-backend-implementation)
5. [Frontend Implementation](#5-frontend-implementation)
6. [File-by-File Change List](#6-file-by-file-change-list)
7. [SQL Query Specifications](#7-sql-query-specifications)
8. [Schema Specifications](#8-schema-specifications)
9. [API Endpoint Specifications](#9-api-endpoint-specifications)
10. [Frontend Component Specifications](#10-frontend-component-specifications)
11. [Testing Checklist](#11-testing-checklist)
12. [Implementation Sequence](#12-implementation-sequence)

---

## 1. Feature Requirements

### 1.1 SR (Sales Representative) Reports

**User Story:** As an admin, I want to see what products each SR ordered, at what amounts, and calculate profit/loss so I can evaluate SR performance.

**Requirements:**
- Aggregated table showing each SR's total orders, revenue, cost, gross profit, commission, and net profit
- Date range filter (default: Yesterday to Today)
- Clicking an SR row opens a modal showing detailed breakdown:
  - Order-by-order details with customer, product, variant, quantities, prices
  - Per-line revenue, cost, profit, commission, net profit
  - Summary section at top of modal

**Key Metrics:**
```
Revenue     = SUM(quantity * negotiated_price)
Cost        = SUM(quantity * purchase_price)
Gross Profit = Revenue - Cost
Commission  = SUM(sr_order.commission_amount)
Net Profit  = Gross Profit - Commission
Margin %    = (Gross Profit / Revenue) * 100
```

### 1.2 DSR (Delivery Sales Representative) Reports

**User Story:** As an admin, I want to see what product-variants each DSR needs to load for their assigned SOs so I can plan warehouse picking.

**Requirements:**
- Aggregated table showing each DSR's assignments, pending/completed orders, total items to deliver
- Date range filter (default: Yesterday to Today)
- Clicking a DSR row opens a modal showing:
  - Product-variant summary: total qty needed, already loaded, remaining to load
  - Clicking a product-variant row opens a nested modal showing:
    - Which SOs contribute to that quantity
    - Per-SO: order number, customer, ordered qty, shipped qty, remaining qty

**Key Metrics:**
```
Total Qty Needed  = SUM(sod.quantity - sod.shipped_quantity) for all assigned SOs
Already Loaded    = dsr_inventory_stock.quantity for that product/variant
Remaining to Load = Total Qty Needed - Already Loaded
```

---

## 2. Data Model Study

### 2.1 SR-Related Models

#### SR_Order (`sales.sr_order`)
| Field | Type | Purpose |
|-------|------|---------|
| `sr_order_id` | Integer PK | Primary key |
| `sr_id` | Integer FK → sales_representative | Which SR placed this order |
| `customer_id` | Integer FK → customer | Target customer |
| `order_number` | String(50) | Human-readable: SR-YYYYMMDD-SRID-SEQ |
| `order_date` | TIMESTAMP | When order was placed |
| `status` | String(20) | draft/pending/approved/consolidated |
| `total_amount` | Numeric(18,2) | Order total |
| `commission_amount` | Numeric(18,4) | Commission for this order |
| `commission_disbursed` | String(20) | pending/ready/disbursed |
| `company_id` | Integer FK | Multi-tenant isolation |
| `is_deleted` | Boolean | Soft delete |

#### SR_Order_Detail (`sales.sr_order_detail`)
| Field | Type | Purpose |
|-------|------|---------|
| `sr_order_detail_id` | Integer PK | Primary key |
| `sr_order_id` | Integer FK → sr_order | Parent order |
| `product_id` | Integer FK → product | Product ordered |
| `variant_id` | Integer FK → product_variant | Variant (nullable) |
| `quantity` | Numeric(18,4) | Ordered quantity |
| `unit_price` | Numeric(18,4) | Standard unit price |
| `negotiated_price` | Numeric(18,4) | Price SR negotiated with customer |
| `sale_price` | Numeric(18,4) | Standard sale price (nullable) |
| `discount_amount` | Numeric(18,2) | Discount applied |
| `shipped_quantity` | Numeric(18,4) | Quantity already shipped |
| `returned_quantity` | Numeric(18,4) | Quantity returned |

#### SalesRepresentative (`sales.sales_representative`)
| Field | Type | Purpose |
|-------|------|---------|
| `sr_id` | Integer PK | Primary key |
| `sr_name` | String(200) | Display name |
| `sr_code` | String(50) UNIQUE | Unique code |
| `commission_amount` | Numeric(18,2) | Running commission balance |
| `company_id` | Integer FK | Multi-tenant |
| `is_active` | Boolean | Active status |

#### ProductPrice (`inventory.product_price`)
| Field | Type | Purpose |
|-------|------|---------|
| `price_id` | Integer PK | Primary key |
| `product_id` | Integer FK | Product |
| `variant_id` | Integer FK (nullable) | Variant |
| `effective_date` | TIMESTAMP | When price becomes effective |
| `purchase_price` | Numeric(18,4) | **COST PRICE** - used for P/L |
| `selling_price` | Numeric(18,4) | Standard selling price |
| `is_active` | Boolean | Active price flag |

**CRITICAL:** ProductPrice is time-effective. Multiple records exist per product/variant with different `effective_date`. For historical accuracy, we need the price that was active at the time of the order, not the current price.

### 2.2 DSR-Related Models

#### DeliverySalesRepresentative (`sales.delivery_sales_representative`)
| Field | Type | Purpose |
|-------|------|---------|
| `dsr_id` | Integer PK | Primary key |
| `dsr_name` | String(200) | Display name |
| `dsr_code` | String(50) UNIQUE | Unique code |
| `payment_on_hand` | Numeric(18,2) | Cash collected but not settled |
| `commission_amount` | Numeric(18,2) | Commission balance |
| `company_id` | Integer FK | Multi-tenant |
| `is_active` | Boolean | Active status |

#### DSRSOAssignment (`sales.dsr_so_assignment`)
| Field | Type | Purpose |
|-------|------|---------|
| `assignment_id` | Integer PK | Primary key |
| `dsr_id` | Integer FK → delivery_sales_representative | Assigned DSR |
| `sales_order_id` | Integer FK → sales_order | Sales Order to deliver |
| `assigned_date` | TIMESTAMP | When assignment was created |
| `status` | String(20) | assigned/in_progress/completed |
| `company_id` | Integer FK | Multi-tenant |

#### SalesOrder (`sales.sales_order`)
| Field | Type | Purpose |
|-------|------|---------|
| `sales_order_id` | Integer PK | Primary key |
| `order_number` | String(50) | Human-readable order number |
| `customer_id` | Integer FK → customer | Target customer |
| `order_date` | TIMESTAMP | When order was created |
| `total_amount` | Numeric(18,2) | Order total |
| `status` | String(20) | Pending/Confirmed/Partial/Completed/Cancelled |
| `delivery_status` | String(20) | Pending/Partial/Delivered/Completed |
| `is_loaded` | Boolean | Whether loaded into DSR storage |
| `loaded_by_dsr_id` | Integer FK → DSR | DSR who loaded |
| `location_id` | Integer FK → storage_location | Where stock is picked from |

#### SalesOrderDetail (`sales.sales_order_detail`)
| Field | Type | Purpose |
|-------|------|---------|
| `sales_order_detail_id` | Integer PK | Primary key |
| `sales_order_id` | Integer FK → sales_order | Parent order |
| `product_id` | Integer FK → product | Product |
| `variant_id` | Integer FK → product_variant | Variant (nullable) |
| `quantity` | Numeric(18,4) | Ordered quantity |
| `shipped_quantity` | Numeric(18,4) | Already delivered |
| `returned_quantity` | Numeric(18,4) | Returned by customer |
| `unit_price` | Numeric(18,4) | Price per unit |
| `discount_amount` | Numeric(18,2) | Discount |

#### DSRInventoryStock (`warehouse.dsr_inventory_stock`)
| Field | Type | Purpose |
|-------|------|---------|
| `stock_id` | Integer PK | Primary key |
| `product_id` | Integer FK → product | Product |
| `variant_id` | Integer FK → product_variant | Variant (nullable) |
| `dsr_storage_id` | Integer FK → dsr_storage | Which DSR's storage |
| `quantity` | Numeric(18,4) | Current quantity in DSR possession |

#### DSRStorage (`warehouse.dsr_storage`)
| Field | Type | Purpose |
|-------|------|---------|
| `dsr_storage_id` | Integer PK | Primary key |
| `dsr_id` | Integer FK → delivery_sales_representative | Linked DSR (one-to-one) |
| `storage_name` | String(100) | Display name |

#### DSRPaymentSettlement (`sales.dsr_payment_settlement`)
| Field | Type | Purpose |
|-------|------|---------|
| `settlement_id` | Integer PK | Primary key |
| `dsr_id` | Integer FK → delivery_sales_representative | DSR being settled |
| `settlement_date` | TIMESTAMP | When settlement occurred |
| `amount` | Numeric(18,2) | Amount collected |

### 2.3 Entity Relationships (for report queries)

```
SR Report Data Flow:
sales_representative
  └── sr_order (filter: sr_id, company_id, order_date, is_deleted)
        └── sr_order_detail (filter: sr_order_id, is_deleted)
              ├── product (join: product_id)
              ├── product_variant (left join: variant_id)
              └── product_price (lateral join: product_id, variant_id, effective_date <= order_date)

SR Detail Modal:
sr_order + sr_order_detail (as above)
  └── customer (join: customer_id)

DSR Report Data Flow:
delivery_sales_representative
  └── dsr_so_assignment (filter: dsr_id, company_id, assigned_date, is_deleted)
        └── sales_order (join: sales_order_id)
              └── sales_order_detail (join: sales_order_id)
                    ├── product (join: product_id)
                    ├── product_variant (left join: variant_id)
                    └── customer (join: via sales_order.customer_id)

DSR Loading Modal:
dsr_so_assignment + sales_order + sales_order_detail (as above)
  LEFT JOIN dsr_inventory_stock (on product_id, variant_id, dsr_storage_id)
    └── dsr_storage (join: dsr_storage_id = dsr.dsr_storage_id)

DSR SO Breakdown Modal:
dsr_so_assignment + sales_order + sales_order_detail (as above)
  └── customer (join: via sales_order.customer_id)
  Filter by: product_id, variant_id
```

---

## 3. Existing Pattern Analysis

### 3.1 Repository Pattern (from `sales_reports.py`)

```python
# Standard pattern used across all report repositories:
def get_team_performance_data(self, company_id: int, start_date: date, end_date: date):
    query = """
    SELECT
        sr.sr_id,
        sr.sr_name,
        COUNT(DISTINCT so.sales_order_id) as order_count,
        SUM(sod.shipped_quantity * sod.unit_price) as total_sales,
        AVG(so.total_amount) as avg_order_value
    FROM sales.sales_representative sr
    JOIN sales.sales_order_detail sod ON sr.sr_id = sod.sr_id
    JOIN sales.sales_order so ON sod.sales_order_id = so.sales_order_id
    WHERE sr.company_id = :company_id
    AND so.order_date::date BETWEEN :start_date AND :end_date
    GROUP BY sr.sr_id, sr.sr_name;
    """
    return self.db.execute(text(query), {
        "company_id": company_id,
        "start_date": start_date,
        "end_date": end_date,
    }).mappings().all()
```

**Key patterns observed:**
- All queries use `text()` with named parameters (`:param_name`)
- Results returned via `.mappings().all()` (list of dict-like rows) or `.mappings().first()` (single row)
- CTEs (`WITH` clauses) used for complex aggregations
- `COALESCE()` used for null safety
- Company isolation enforced on every query
- Date filtering uses `::date BETWEEN :start_date AND :end_date`
- Soft delete filtering: `is_deleted = FALSE` on all joined tables

### 3.2 Schema Pattern (from `reports.py` schemas)

```python
# Standard Pydantic pattern:
class SalesVelocityItem(BaseModel):
    sr_id: int
    sr_name: str
    quote_to_order_conversion: float
    average_deal_size: float
    velocity_score: float

class SalesTeamPerformanceReport(BaseModel):
    velocity_metrics: List[SalesVelocityItem]
    product_affinities: List[ProductAffinityItem]
```

**Key patterns:**
- Flat response models with `List[Item]` fields
- Optional fields use `Optional[type]` or `type | None`
- Numeric fields use `float` (Pydantic handles Decimal → float conversion)
- Date fields use `str` (formatted as ISO strings from SQL)

### 3.3 API Endpoint Pattern (from `reports.py`)

```python
@router.get("/sales/team-performance", response_model=SalesTeamPerformanceReport)
def get_sales_team_performance_report(
    start_date: date = Query(None, description="Start of date range (inclusive)"),
    end_date: date = Query(None, description="End of date range (inclusive)"),
    db: Session = Depends(get_db),
    current_user: dict = Security(get_current_user, scopes=["reports:read"]),
):
    if not (start_date and end_date):
        end_date = date.today()
        start_date = end_date - timedelta(days=30)

    if start_date > end_date:
        raise HTTPException(
            status_code=400, detail="start_date must be less than or equal to end_date"
        )

    service = ReportsService(db)
    try:
        return service.get_sales_team_performance_report(
            current_user.get("company_id"), start_date, end_date
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
```

**Key patterns:**
- Default date range: last 30 days (we'll use yesterday-today)
- Validation: `start_date > end_date` → 400 error
- Service instantiation per request (not singleton)
- Company ID from `current_user.get("company_id")`
- Simple try/except with 500 on failure

### 3.4 Frontend API Pattern (from `reportsApi.ts`)

```typescript
export interface SalesVelocityItem {
    sr_id: number;
    sr_name: string;
    quote_to_order_conversion: number;
    average_deal_size: number;
    velocity_score: number;
}

export const getSalesTeamPerformanceReportData = (
    startDate: string, endDate: string
): Promise<SalesTeamPerformanceReport> =>
    apiRequest(api, `/reports/sales/team-performance?start_date=${startDate}&end_date=${endDate}`);
```

**Key patterns:**
- TypeScript interface mirrors Pydantic schema exactly
- API function returns `Promise<ResponseInterface>`
- Query params built with template literals
- Date format: `yyyy-MM-dd` string

### 3.5 Frontend Page Pattern (from `SalesTeamAnalytics.tsx`)

```typescript
const [dateRange, setDateRange] = useState<DateRange | undefined>({
    from: subDays(new Date(), 30),
    to: new Date(),
});

const { data, isLoading, error } = useQuery({
    queryKey: ["sales-team-performance-report", dateRange?.from, dateRange?.to],
    queryFn: () => getSalesTeamPerformanceReportData(
        dateRange?.from ? format(dateRange.from, "yyyy-MM-dd") : format(subDays(new Date(), 30), "yyyy-MM-dd"),
        dateRange?.to ? format(dateRange.to, "yyyy-MM-dd") : format(new Date(), "yyyy-MM-dd"),
    ),
});
```

**Key patterns:**
- `useState<DateRange>` for date picker state
- `useQuery` with date values in query key (triggers refetch on change)
- `format(date, "yyyy-MM-dd")` for API calls
- `subDays(new Date(), N)` for default ranges
- Loading: `<Loader2 className="animate-spin" />` centered
- Error: `<Alert variant="destructive">` with message

---

## 4. Backend Implementation

### 4.1 New Files to Create

| File | Purpose | Lines (est.) |
|------|---------|-------------|
| `Shoudagor/app/repositories/reports/sr_reports.py` | SR report SQL queries | ~160 |
| `Shoudagor/app/repositories/reports/dsr_reports.py` | DSR report SQL queries | ~250 |
| `Shoudagor/app/schemas/reports/sr_reports.py` | SR report Pydantic schemas | ~80 |
| `Shoudagor/app/schemas/reports/dsr_reports.py` | DSR report Pydantic schemas | ~80 |

### 4.2 Files to Modify

| File | Changes |
|------|---------|
| `Shoudagor/app/repositories/reports/__init__.py` | Export new repositories |
| `Shoudagor/app/services/reports.py` | Add 5 new methods, import new repos |
| `Shoudagor/app/api/reports.py` | Add 5 new endpoints, import schemas |
| `Shoudagor/app/schemas/reports/__init__.py` | Export new schemas (if exists) |

---

## 5. Frontend Implementation

### 5.1 New Files to Create

| File | Purpose | Lines (est.) |
|------|---------|-------------|
| `shoudagor_FE/src/lib/api/srReportsApi.ts` | SR report API functions + types | ~120 |
| `shoudagor_FE/src/lib/api/dsrReportsApi.ts` | DSR report API functions + types | ~150 |
| `shoudagor_FE/src/components/modals/SRDetailModal.tsx` | SR detail drill-down modal | ~200 |
| `shoudagor_FE/src/components/modals/DSRLoadingModal.tsx` | DSR loading details modal | ~200 |
| `shoudagor_FE/src/components/modals/DSRSOBreakdownModal.tsx` | SO breakdown nested modal | ~150 |
| `shoudagor_FE/src/pages/reports/SRReports.tsx` | SR report page | ~250 |
| `shoudagor_FE/src/pages/reports/DSRReports.tsx` | DSR report page | ~250 |

### 5.2 Files to Modify

| File | Changes |
|------|---------|
| `shoudagor_FE/src/App.tsx` | Add 2 new routes under AdminRoute |

---

## 6. File-by-File Change List

### 6.1 `Shoudagor/app/repositories/reports/__init__.py`

**Current content:**
```python
from .procurement_reports import ProcurementReportsRepository
from .inventory_reports import InventoryReportsRepository
from .sales_reports import SalesReportsRepository
from .reports import ReportsRepository
```

**Add:**
```python
from .sr_reports import SRReportsRepository
from .dsr_reports import DSRReportsRepository
```

### 6.2 `Shoudagor/app/services/reports.py`

**Current `__init__`:**
```python
def __init__(self, db: AsyncSession):
    self.repo = ReportsRepository(db)
    self.sales_repo = SalesReportsRepository(db)
```

**Modify to:**
```python
def __init__(self, db: AsyncSession):
    self.repo = ReportsRepository(db)
    self.sales_repo = SalesReportsRepository(db)
    self.sr_repo = SRReportsRepository(db)
    self.dsr_repo = DSRReportsRepository(db)
```

**Add imports at top:**
```python
from app.repositories.reports.sr_reports import SRReportsRepository
from app.repositories.reports.dsr_reports import DSRReportsRepository
```

**Add 5 new methods to `ReportsService` class:**
```python
def get_sr_summary_report(self, company_id, start_date, end_date, sr_id=None, status=None):
    return self.sr_repo.get_sr_summary(company_id, start_date, end_date, sr_id, status)

def get_sr_detail_report(self, company_id, sr_id, start_date, end_date):
    return self.sr_repo.get_sr_details(company_id, sr_id, start_date, end_date)

def get_dsr_summary_report(self, company_id, start_date, end_date, dsr_id=None, status=None):
    return self.dsr_repo.get_dsr_summary(company_id, start_date, end_date, dsr_id, status)

def get_dsr_loading_report(self, company_id, dsr_id, start_date, end_date):
    return self.dsr_repo.get_dsr_loading_details(company_id, dsr_id, start_date, end_date)

def get_dsr_so_breakdown(self, company_id, dsr_id, product_id, variant_id, start_date, end_date):
    return self.dsr_repo.get_dsr_so_breakdown(company_id, dsr_id, product_id, variant_id, start_date, end_date)
```

### 6.3 `Shoudagor/app/api/reports.py`

**Add imports:**
```python
from app.schemas.reports.sr_reports import (
    SRSummaryResponse, SRDetailResponse
)
from app.schemas.reports.dsr_reports import (
    DSRSummaryResponse, DSRLoadingResponse, DSRSOBreakdownResponse
)
```

**Add 5 new endpoints** (see Section 9 for full specifications)

### 6.4 `shoudagor_FE/src/App.tsx`

**Add imports:**
```typescript
import SRReports from "./pages/reports/SRReports";
import DSRReports from "./pages/reports/DSRReports";
```

**Add routes** (under AdminRoute, near other report routes):
```typescript
<Route path="/reports/sr" element={<SRReports />} />
<Route path="/reports/dsr" element={<DSRReports />} />
```

---

## 7. SQL Query Specifications

### 7.1 SR Summary Query

**File:** `Shoudagor/app/repositories/reports/sr_reports.py`
**Method:** `get_sr_summary()`

```sql
WITH sr_metrics AS (
    SELECT
        sr.sr_id,
        sr.sr_name,
        sr.sr_code,
        COUNT(DISTINCT sro.sr_order_id) AS total_orders,
        COALESCE(SUM(srod.quantity), 0) AS total_quantity,
        COALESCE(SUM(srod.quantity * srod.negotiated_price), 0) AS total_revenue,
        COALESCE(SUM(srod.quantity * COALESCE(pp.purchase_price, 0)), 0) AS total_cost,
        COALESCE(SUM(sro.commission_amount), 0) AS total_commission
    FROM sales.sales_representative sr
    JOIN sales.sr_order sro ON sro.sr_id = sr.sr_id
    JOIN sales.sr_order_detail srod ON srod.sr_order_id = sro.sr_order_id
    LEFT JOIN LATERAL (
        SELECT purchase_price
        FROM inventory.product_price pp
        WHERE pp.product_id = srod.product_id
          AND (
              (pp.variant_id = srod.variant_id)
              OR (pp.variant_id IS NULL AND srod.variant_id IS NULL)
          )
          AND pp.effective_date <= sro.order_date
          AND pp.is_active = TRUE
        ORDER BY pp.effective_date DESC
        LIMIT 1
    ) pp ON TRUE
    WHERE sr.company_id = :company_id
      AND sr.is_deleted = FALSE
      AND sro.is_deleted = FALSE
      AND srod.is_deleted = FALSE
      AND sro.order_date::date BETWEEN :start_date AND :end_date
      AND (:sr_id IS NULL OR sr.sr_id = :sr_id)
      AND (:status IS NULL OR sro.status = :status)
    GROUP BY sr.sr_id, sr.sr_name, sr.sr_code
)
SELECT
    sr_id,
    sr_name,
    sr_code,
    total_orders,
    total_quantity,
    total_revenue,
    total_cost,
    (total_revenue - total_cost) AS gross_profit,
    CASE
        WHEN total_revenue > 0
        THEN ((total_revenue - total_cost) / total_revenue) * 100
        ELSE 0
    END AS profit_margin_percent,
    total_commission,
    (total_revenue - total_cost - total_commission) AS net_profit
FROM sr_metrics
ORDER BY net_profit DESC;
```

**Design Decisions:**
- **LATERAL JOIN** for product_price: Gets the price that was active at the time of the order, not the current price. This is critical for historical accuracy.
- **CTE pattern**: Separates aggregation from calculation for readability and potential optimization.
- **NULL-safe parameters**: `:sr_id IS NULL OR sr.sr_id = :sr_id` allows optional filtering without dynamic SQL.
- **Commission**: Uses `sr_order.commission_amount` directly (already calculated during consolidation).
- **Ordering**: By `net_profit DESC` so best performers appear first.

### 7.2 SR Detail Query

**File:** `Shoudagor/app/repositories/reports/sr_reports.py`
**Method:** `get_sr_details()`

```sql
SELECT
    sro.order_number,
    c.customer_name,
    p.product_name,
    CASE
        WHEN pv.attribute_name IS NOT NULL AND pv.attribute_value IS NOT NULL
        THEN pv.attribute_name || ' - ' || pv.attribute_value
        ELSE NULL
    END AS variant_name,
    srod.quantity,
    srod.shipped_quantity,
    srod.returned_quantity,
    COALESCE(pp.purchase_price, 0) AS unit_cost,
    srod.negotiated_price,
    srod.sale_price,
    (srod.quantity * srod.negotiated_price) AS revenue,
    (srod.quantity * COALESCE(pp.purchase_price, 0)) AS cost,
    (srod.quantity * srod.negotiated_price) - (srod.quantity * COALESCE(pp.purchase_price, 0)) AS profit,
    COALESCE(sro.commission_amount, 0) / NULLIF(COUNT(*) OVER (PARTITION BY sro.sr_order_id), 0) AS commission,
    ((srod.quantity * srod.negotiated_price) - (srod.quantity * COALESCE(pp.purchase_price, 0)))
      - (COALESCE(sro.commission_amount, 0) / NULLIF(COUNT(*) OVER (PARTITION BY sro.sr_order_id), 0)) AS net_profit,
    sro.status,
    sro.order_date
FROM sales.sr_order sro
JOIN sales.sr_order_detail srod ON srod.sr_order_id = sro.sr_order_id
JOIN sales.customer c ON c.customer_id = sro.customer_id
JOIN inventory.product p ON p.product_id = srod.product_id
LEFT JOIN inventory.product_variant pv ON pv.variant_id = srod.variant_id
LEFT JOIN LATERAL (
    SELECT purchase_price
    FROM inventory.product_price pp
    WHERE pp.product_id = srod.product_id
      AND (
          (pp.variant_id = srod.variant_id)
          OR (pp.variant_id IS NULL AND srod.variant_id IS NULL)
      )
      AND pp.effective_date <= sro.order_date
      AND pp.is_active = TRUE
    ORDER BY pp.effective_date DESC
    LIMIT 1
) pp ON TRUE
WHERE sro.sr_id = :sr_id
  AND sro.company_id = :company_id
  AND sro.is_deleted = FALSE
  AND srod.is_deleted = FALSE
  AND sro.order_date::date BETWEEN :start_date AND :end_date
ORDER BY sro.order_date DESC, sro.order_number;
```

**Design Decisions:**
- **Commission pro-rating**: Divides order-level commission by number of line items using window function. This is an approximation; for exact per-line commission, the commission calculation logic would need to be replicated.
- **Variant name formatting**: Combines `attribute_name` and `attribute_value` (e.g., "Size - Large") for display.
- **Ordering**: Most recent orders first.

### 7.3 DSR Summary Query

**File:** `Shoudagor/app/repositories/reports/dsr_reports.py`
**Method:** `get_dsr_summary()`

```sql
SELECT
    dsr.dsr_id,
    dsr.dsr_name,
    dsr.dsr_code,
    COUNT(DISTINCT dsa.assignment_id) AS total_assignments,
    COUNT(DISTINCT CASE WHEN dsa.status != 'completed' THEN dsa.assignment_id END) AS pending_orders,
    COUNT(DISTINCT CASE WHEN dsa.status = 'completed' THEN dsa.assignment_id END) AS completed_orders,
    COALESCE(SUM(
        GREATEST(sod.quantity - sod.shipped_quantity, 0)
    ), 0) AS total_items,
    COALESCE(SUM(
        GREATEST(sod.quantity - sod.shipped_quantity, 0) * sod.unit_price
    ), 0) AS total_value,
    dsr.payment_on_hand,
    (
        SELECT MAX(dps.settlement_date)
        FROM sales.dsr_payment_settlement dps
        WHERE dps.dsr_id = dsr.dsr_id
          AND dps.is_deleted = FALSE
    ) AS last_settlement_date
FROM sales.delivery_sales_representative dsr
LEFT JOIN sales.dsr_so_assignment dsa ON dsa.dsr_id = dsr.dsr_id
    AND dsa.is_deleted = FALSE
    AND dsa.assigned_date::date BETWEEN :start_date AND :end_date
LEFT JOIN sales.sales_order so ON so.sales_order_id = dsa.sales_order_id
    AND so.is_deleted = FALSE
LEFT JOIN sales.sales_order_detail sod ON sod.sales_order_id = so.sales_order_id
    AND sod.is_deleted = FALSE
WHERE dsr.company_id = :company_id
  AND dsr.is_deleted = FALSE
  AND dsr.is_active = TRUE
  AND (:dsr_id IS NULL OR dsr.dsr_id = :dsr_id)
  AND (:status IS NULL OR dsa.status = :status OR dsa.assignment_id IS NULL)
GROUP BY dsr.dsr_id, dsr.dsr_name, dsr.dsr_code, dsr.payment_on_hand
ORDER BY dsr.dsr_name;
```

**Design Decisions:**
- **LEFT JOIN** for assignments: Shows all active DSRs even if they have no assignments in the date range.
- **GREATEST(quantity - shipped, 0)**: Prevents negative quantities if shipped > ordered (data anomaly protection).
- **Subquery for last settlement**: Correlated subquery is cleaner than another JOIN for a single aggregate value.
- **Status filter**: `dsa.assignment_id IS NULL` ensures DSRs with no assignments still appear when filtering by status.

### 7.4 DSR Loading Details Query

**File:** `Shoudagor/app/repositories/reports/dsr_reports.py`
**Method:** `get_dsr_loading_details()`

```sql
WITH assigned_items AS (
    SELECT
        sod.product_id,
        sod.variant_id,
        SUM(GREATEST(sod.quantity - sod.shipped_quantity, 0)) AS total_qty_needed
    FROM sales.dsr_so_assignment dsa
    JOIN sales.sales_order so ON so.sales_order_id = dsa.sales_order_id
    JOIN sales.sales_order_detail sod ON sod.sales_order_id = so.sales_order_id
    WHERE dsa.dsr_id = :dsr_id
      AND dsa.is_deleted = FALSE
      AND so.is_deleted = FALSE
      AND sod.is_deleted = FALSE
      AND dsa.assigned_date::date BETWEEN :start_date AND :end_date
      AND dsa.status != 'completed'
    GROUP BY sod.product_id, sod.variant_id
),
loaded_stock AS (
    SELECT
        dis.product_id,
        dis.variant_id,
        COALESCE(SUM(dis.quantity), 0) AS already_loaded
    FROM warehouse.dsr_inventory_stock dis
    JOIN warehouse.dsr_storage ds ON ds.dsr_storage_id = dis.dsr_storage_id
    WHERE ds.dsr_id = :dsr_id
      AND dis.is_deleted = FALSE
      AND ds.is_deleted = FALSE
    GROUP BY dis.product_id, dis.variant_id
)
SELECT
    ai.product_id,
    p.product_name,
    ai.variant_id,
    CASE
        WHEN pv.attribute_name IS NOT NULL AND pv.attribute_value IS NOT NULL
        THEN pv.attribute_name || ' - ' || pv.attribute_value
        ELSE pv.sku
    END AS variant_name,
    pv.sku AS variant_sku,
    ai.total_qty_needed,
    COALESCE(ls.already_loaded, 0) AS already_loaded,
    GREATEST(ai.total_qty_needed - COALESCE(ls.already_loaded, 0), 0) AS remaining_to_load,
    u.unit_abbreviation,
    GREATEST(ai.total_qty_needed - COALESCE(ls.already_loaded, 0), 0) * COALESCE(
        (SELECT pp.selling_price FROM inventory.product_price pp
         WHERE pp.product_id = ai.product_id
           AND (pp.variant_id = ai.variant_id OR (pp.variant_id IS NULL AND ai.variant_id IS NULL))
           AND pp.is_active = TRUE
         ORDER BY pp.effective_date DESC LIMIT 1),
        0
    ) AS total_value
FROM assigned_items ai
JOIN inventory.product p ON p.product_id = ai.product_id
LEFT JOIN inventory.product_variant pv ON pv.variant_id = ai.variant_id
LEFT JOIN inventory.unit_of_measure u ON u.unit_id = pv.unit_id
LEFT JOIN loaded_stock ls ON ls.product_id = ai.product_id
    AND (ls.variant_id = ai.variant_id OR (ls.variant_id IS NULL AND ai.variant_id IS NULL))
ORDER BY remaining_to_load DESC;
```

**Design Decisions:**
- **Two CTEs**: `assigned_items` calculates what's needed, `loaded_stock` calculates what's already in the DSR's van.
- **Only non-completed assignments**: `dsa.status != 'completed'` ensures we only show what still needs to be loaded/delivered.
- **GREATEST for remaining**: Prevents negative "remaining to load" if DSR already has more stock than needed.
- **Ordering**: By `remaining_to_load DESC` so items needing most attention appear first.

### 7.5 DSR SO Breakdown Query

**File:** `Shoudagor/app/repositories/reports/dsr_reports.py`
**Method:** `get_dsr_so_breakdown()`

```sql
SELECT
    so.order_number,
    c.customer_name,
    dsa.status AS assignment_status,
    sod.quantity AS ordered_qty,
    sod.shipped_qty,
    GREATEST(sod.quantity - sod.shipped_quantity, 0) AS remaining_qty,
    sod.unit_price,
    GREATEST(sod.quantity - sod.shipped_quantity, 0) * sod.unit_price AS line_total,
    dsa.assigned_date
FROM sales.dsr_so_assignment dsa
JOIN sales.sales_order so ON so.sales_order_id = dsa.sales_order_id
JOIN sales.sales_order_detail sod ON sod.sales_order_id = so.sales_order_id
JOIN sales.customer c ON c.customer_id = so.customer_id
WHERE dsa.dsr_id = :dsr_id
  AND sod.product_id = :product_id
  AND (sod.variant_id = :variant_id OR (sod.variant_id IS NULL AND :variant_id IS NULL))
  AND dsa.is_deleted = FALSE
  AND so.is_deleted = FALSE
  AND sod.is_deleted = FALSE
  AND dsa.assigned_date::date BETWEEN :start_date AND :end_date
ORDER BY dsa.assigned_date DESC, so.order_number;
```

**Design Decisions:**
- **NULL-safe variant matching**: Handles cases where variant_id is NULL (product without variants).
- **Simple direct query**: No CTEs needed since this is a straightforward filtered join.
- **Ordering**: Most recently assigned orders first.

---

## 8. Schema Specifications

### 8.1 SR Report Schemas

**File:** `Shoudagor/app/schemas/reports/sr_reports.py`

```python
from pydantic import BaseModel
from typing import List, Optional


class SRSummaryItem(BaseModel):
    sr_id: int
    sr_name: str
    sr_code: str
    total_orders: int
    total_quantity: float
    total_revenue: float
    total_cost: float
    gross_profit: float
    profit_margin_percent: float
    total_commission: float
    net_profit: float


class SRSummaryResponse(BaseModel):
    items: List[SRSummaryItem]
    total_count: int
    date_range_start: str
    date_range_end: str
    total_revenue: float
    total_cost: float
    total_gross_profit: float
    total_commission: float
    total_net_profit: float


class SRDetailItem(BaseModel):
    order_number: str
    customer_name: str
    product_name: str
    variant_name: Optional[str]
    quantity: float
    shipped_quantity: float
    returned_quantity: float
    unit_cost: float
    negotiated_price: float
    sale_price: Optional[float]
    revenue: float
    cost: float
    profit: float
    commission: float
    net_profit: float
    status: str
    order_date: str


class SRDetailResponse(BaseModel):
    sr_name: str
    sr_code: str
    items: List[SRDetailItem]
    total_orders: int
    total_revenue: float
    total_cost: float
    gross_profit: float
    total_commission: float
    net_profit: float
```

### 8.2 DSR Report Schemas

**File:** `Shoudagor/app/schemas/reports/dsr_reports.py`

```python
from pydantic import BaseModel
from typing import List, Optional


class DSRSummaryItem(BaseModel):
    dsr_id: int
    dsr_name: str
    dsr_code: str
    total_assignments: int
    pending_orders: int
    completed_orders: int
    total_items: float
    total_value: float
    payment_on_hand: float
    last_settlement_date: Optional[str]


class DSRSummaryResponse(BaseModel):
    items: List[DSRSummaryItem]
    total_count: int
    date_range_start: str
    date_range_end: str


class DSRLoadingItem(BaseModel):
    product_id: int
    product_name: str
    variant_id: Optional[int]
    variant_name: Optional[str]
    variant_sku: Optional[str]
    total_qty_needed: float
    already_loaded: float
    remaining_to_load: float
    unit_abbreviation: Optional[str]
    total_value: float


class DSRLoadingResponse(BaseModel):
    dsr_name: str
    dsr_code: str
    items: List[DSRLoadingItem]
    total_items: int
    total_value: float


class DSRSOBreakdownItem(BaseModel):
    order_number: str
    customer_name: str
    assignment_status: str
    ordered_qty: float
    shipped_qty: float
    remaining_qty: float
    unit_price: float
    line_total: float
    assignment_date: str


class DSRSOBreakdownResponse(BaseModel):
    product_name: str
    variant_name: Optional[str]
    items: List[DSRSOBreakdownItem]
```

---

## 9. API Endpoint Specifications

### 9.1 SR Summary Endpoint

```
GET /api/company/reports/sr-summary

Query Parameters:
  - start_date: date (optional, default: yesterday)
  - end_date: date (optional, default: today)
  - sr_id: int (optional, filter by specific SR)
  - status: string (optional, filter by order status)

Response: SRSummaryResponse

Example:
GET /api/company/reports/sr-summary?start_date=2026-03-30&end_date=2026-03-31
```

### 9.2 SR Detail Endpoint

```
GET /api/company/reports/sr-details/{sr_id}

Path Parameters:
  - sr_id: int (required)

Query Parameters:
  - start_date: date (optional, default: yesterday)
  - end_date: date (optional, default: today)

Response: SRDetailResponse

Example:
GET /api/company/reports/sr-details/5?start_date=2026-03-30&end_date=2026-03-31
```

### 9.3 DSR Summary Endpoint

```
GET /api/company/reports/dsr-summary

Query Parameters:
  - start_date: date (optional, default: yesterday)
  - end_date: date (optional, default: today)
  - dsr_id: int (optional, filter by specific DSR)
  - status: string (optional, filter by assignment status)

Response: DSRSummaryResponse

Example:
GET /api/company/reports/dsr-summary?start_date=2026-03-30&end_date=2026-03-31
```

### 9.4 DSR Loading Endpoint

```
GET /api/company/reports/dsr-loading/{dsr_id}

Path Parameters:
  - dsr_id: int (required)

Query Parameters:
  - start_date: date (optional, default: yesterday)
  - end_date: date (optional, default: today)

Response: DSRLoadingResponse

Example:
GET /api/company/reports/dsr-loading/3?start_date=2026-03-30&end_date=2026-03-31
```

### 9.5 DSR SO Breakdown Endpoint

```
GET /api/company/reports/dsr-so-breakdown/{dsr_id}

Path Parameters:
  - dsr_id: int (required)

Query Parameters:
  - product_id: int (required)
  - variant_id: int (optional)
  - start_date: date (optional, default: yesterday)
  - end_date: date (optional, default: today)

Response: DSRSOBreakdownResponse

Example:
GET /api/company/reports/dsr-so-breakdown/3?product_id=10&variant_id=25&start_date=2026-03-30&end_date=2026-03-31
```

---

## 10. Frontend Component Specifications

### 10.1 SRReports Page

**File:** `shoudagor_FE/src/pages/reports/SRReports.tsx`

**Structure:**
```
┌─────────────────────────────────────────────────────────────┐
│ SR Performance Report              [DateRangePicker]        │
├─────────────────────────────────────────────────────────────┤
│ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐         │
│ │ Total Revenue │ │ Total Cost   │ │ Gross Profit │ ...     │
│ │    ৳ 45,230   │ │   ৳ 32,100   │ │   ৳ 13,130   │         │
│ └──────────────┘ └──────────────┘ └──────────────┘         │
├─────────────────────────────────────────────────────────────┤
│ Filters: [SR: All ▼] [Status: All ▼]                        │
├─────────────────────────────────────────────────────────────┤
│ SR Name  │ Code │ Orders │ Qty  │ Revenue │ Cost │ Profit  │
│──────────│──────│────────│──────│─────────│──────│─────────│
│ John Doe │ SR01 │   12   │ 450  │ ৳45,230 │ ৳32K │ ৳13,130 │ ← click
│ Jane Smith│SR02 │    8   │ 320  │ ৳28,500 │ ৳20K │ ৳8,500  │ ← click
└─────────────────────────────────────────────────────────────┘
```

**Key Implementation Details:**
- Uses `useState<DateRange>` with default `{ from: subDays(new Date(), 1), to: new Date() }`
- `useQuery` with queryKey: `["sr-summary-report", dateRange?.from, dateRange?.to, selectedSR, selectedStatus]`
- Table rows clickable: `onClick={() => setSelectedSRId(item.sr_id)}`
- KPI cards: 4 cards in a grid (Revenue, Cost, Gross Profit, Net Profit)
- Conditional rendering: `{selectedSRId && <SRDetailModal srId={selectedSRId} ... />}`

### 10.2 SRDetailModal Component

**File:** `shoudagor_FE/src/components/modals/SRDetailModal.tsx`

**Props:**
```typescript
interface SRDetailModalProps {
    srId: number;
    startDate: string;
    endDate: string;
    onClose: () => void;
}
```

**Structure:**
```
┌─────────────────────────────────────────────────────────────┐
│ SR Details: John Doe (SR01)                          [X]    │
├─────────────────────────────────────────────────────────────┤
│ Summary: 12 Orders | Revenue: ৳45,230 | Cost: ৳32,100      │
│          Gross Profit: ৳13,130 | Commission: ৳2,500        │
│          ★ Net Profit: ৳10,630                              │
├─────────────────────────────────────────────────────────────┤
│ Order#  │ Customer │ Product  │ Qty │ Price  │ Cost │ Profit│
│─────────│──────────│──────────│─────│────────│──────│───────│
│SR-0330-1│ ABC Corp │ Widget A │ 100 │ ৳450   │ ৳320 │ ৳130  │
│SR-0330-2│ XYZ Ltd  │ Widget B │  50 │ ৳280   │ ৳200 │ ৳80   │
└─────────────────────────────────────────────────────────────┘
```

**Key Implementation Details:**
- Uses `Dialog` from shadcn/ui
- `useQuery` with `enabled: !!srId` (only fetches when modal is open)
- QueryKey: `["sr-detail-report", srId, startDate, endDate]`
- Summary section at top with highlighted net profit
- Table with color-coded profit column (green for positive, red for negative)
- `max-h-[80vh] overflow-y-auto` for scrollable content

### 10.3 DSRReports Page

**File:** `shoudagor_FE/src/pages/reports/DSRReports.tsx`

**Structure:**
```
┌─────────────────────────────────────────────────────────────┐
│ DSR Loading Report                 [DateRangePicker]        │
├─────────────────────────────────────────────────────────────┤
│ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐         │
│ │ Total DSRs   │ │ Pending      │ │ Completed    │ ...     │
│ │      5       │ │     12       │ │      8       │         │
│ └──────────────┘ └──────────────┘ └──────────────┘         │
├─────────────────────────────────────────────────────────────┤
│ Filters: [DSR: All ▼] [Status: All ▼]                       │
├─────────────────────────────────────────────────────────────┤
│ DSR Name │ Code │ Assign │ Pending │ Done │ Items │ Value  │
│──────────│──────│────────│─────────│──────│───────│────────│
│ Mike DSR │ DSR1 │   8    │    5    │  3   │  245  │ ৳18,500│ ← click
│ Sara DSR │ DSR2 │   6    │    4    │  2   │  180  │ ৳12,300│ ← click
└─────────────────────────────────────────────────────────────┘
```

### 10.4 DSRLoadingModal Component

**File:** `shoudagor_FE/src/components/modals/DSRLoadingModal.tsx`

**Props:**
```typescript
interface DSRLoadingModalProps {
    dsrId: number;
    startDate: string;
    endDate: string;
    onClose: () => void;
}
```

**Structure:**
```
┌─────────────────────────────────────────────────────────────┐
│ DSR Loading Details: Mike DSR (DSR1)                 [X]    │
├─────────────────────────────────────────────────────────────┤
│ Product        │ Variant    │ Needed │ Loaded │ Remaining  │
│────────────────│────────────│────────│────────│────────────│
│ Widget A       │ Size - L   │  100   │   60   │     40     │ ← click
│ Widget B       │ Color - Red│   80   │   80   │      0     │
│ Gadget C       │ --         │   65   │   20   │     45     │ ← click
└─────────────────────────────────────────────────────────────┘
```

**Key Implementation Details:**
- Clicking a row opens `DSRSOBreakdownModal`
- State: `const [selectedItem, setSelectedItem] = useState<DSRLoadingItem | null>(null)`
- Conditional render: `{selectedItem && <DSRSOBreakdownModal ... />}`

### 10.5 DSRSOBreakdownModal Component

**File:** `shoudagor_FE/src/components/modals/DSRSOBreakdownModal.tsx`

**Props:**
```typescript
interface DSRSOBreakdownModalProps {
    dsrId: number;
    productId: number;
    variantId: number | null;
    productName: string;
    variantName: string | null;
    startDate: string;
    endDate: string;
    onClose: () => void;
}
```

**Structure:**
```
┌─────────────────────────────────────────────────────────────┐
│ SO Breakdown: Widget A (Size - L)                    [X]    │
├─────────────────────────────────────────────────────────────┤
│ SO Number  │ Customer   │ Status     │ Ordered │ Remaining │
│────────────│────────────│────────────│─────────│───────────│
│ SO-2026-045│ ABC Corp   │ assigned   │   50    │    50     │
│ SO-2026-048│ XYZ Ltd    │ in_progress│   50    │    20     │
└─────────────────────────────────────────────────────────────┘
```

---

## 11. Testing Checklist

### Backend Testing
- [ ] SR summary returns correct data for date range
- [ ] SR detail modal data matches summary totals
- [ ] DSR summary shows all active DSRs
- [ ] DSR loading correctly calculates remaining quantities
- [ ] DSR SO breakdown filters by product/variant correctly
- [ ] Company isolation works (user can only see their company's data)
- [ ] Date validation rejects start > end
- [ ] Default date range (yesterday-today) works when no dates provided
- [ ] Optional filters (sr_id, dsr_id, status) work correctly
- [ ] NULL variant_id handled correctly in all queries
- [ ] Soft-deleted records excluded from all queries

### Frontend Testing
- [ ] SR Reports page loads with data
- [ ] DSR Reports page loads with data
- [ ] Date range picker defaults to yesterday-today
- [ ] Changing date range triggers data refetch
- [ ] Clicking SR row opens detail modal
- [ ] SR detail modal shows correct data
- [ ] Clicking DSR row opens loading modal
- [ ] DSR loading modal shows correct product-variant quantities
- [ ] Clicking product-variant row opens SO breakdown modal
- [ ] SO breakdown modal shows correct SOs
- [ ] Loading states display correctly
- [ ] Error states display correctly
- [ ] Empty data shows "No data found" message
- [ ] Routes are accessible only to admin users

---

## 12. Implementation Sequence

### Phase 1: Backend Repositories (2-3 hours)

**Step 1:** Create `Shoudagor/app/repositories/reports/sr_reports.py`
- Implement `get_sr_summary()` with LATERAL JOIN for product_price
- Implement `get_sr_details()` with window function for commission pro-rating

**Step 2:** Create `Shoudagor/app/repositories/reports/dsr_reports.py`
- Implement `get_dsr_summary()` with LEFT JOINs and correlated subquery
- Implement `get_dsr_loading_details()` with two CTEs (assigned_items, loaded_stock)
- Implement `get_dsr_so_breakdown()` with simple filtered join

**Step 3:** Update `Shoudagor/app/repositories/reports/__init__.py`
- Add exports for new repositories

### Phase 2: Backend Schemas (30 min)

**Step 4:** Create `Shoudagor/app/schemas/reports/sr_reports.py`
- Define SRSummaryItem, SRSummaryResponse, SRDetailItem, SRDetailResponse

**Step 5:** Create `Shoudagor/app/schemas/reports/dsr_reports.py`
- Define DSRSummaryItem, DSRSummaryResponse, DSRLoadingItem, DSRLoadingResponse, DSRSOBreakdownItem, DSRSOBreakdownResponse

### Phase 3: Backend Service & API (1-2 hours)

**Step 6:** Update `Shoudagor/app/services/reports.py`
- Import new repositories
- Add to `__init__`
- Add 5 new methods

**Step 7:** Update `Shoudagor/app/api/reports.py`
- Import new schemas
- Add 5 new endpoints with date validation and error handling

**Step 8:** Test endpoints with curl/Postman
- Verify all 5 endpoints return correct data
- Test date validation
- Test company isolation

### Phase 4: Frontend API Layer (30 min)

**Step 9:** Create `shoudagor_FE/src/lib/api/srReportsApi.ts`
- Define TypeScript interfaces matching Pydantic schemas
- Implement `getSRSummaryReport()` and `getSRDetailReport()`

**Step 10:** Create `shoudagor_FE/src/lib/api/dsrReportsApi.ts`
- Define TypeScript interfaces matching Pydantic schemas
- Implement `getDSRSummaryReport()`, `getDSRLoadingReport()`, `getDSRSOBreakdown()`

### Phase 5: Frontend Components (2-3 hours)

**Step 11:** Create `shoudagor_FE/src/components/modals/SRDetailModal.tsx`
- Dialog component with useQuery, summary cards, detail table
- Color-coded profit/loss column
- Loading and error states

**Step 12:** Create `shoudagor_FE/src/components/modals/DSRLoadingModal.tsx`
- Dialog component with product-variant table
- Click handler to open SO breakdown modal

**Step 13:** Create `shoudagor_FE/src/components/modals/DSRSOBreakdownModal.tsx`
- Dialog component with SO breakdown table

### Phase 6: Frontend Pages (1-2 hours)

**Step 14:** Create `shoudagor_FE/src/pages/reports/SRReports.tsx`
- DateRangePicker, KPI cards, filter dropdowns, data table
- Modal trigger on row click

**Step 15:** Create `shoudagor_FE/src/pages/reports/DSRReports.tsx`
- DateRangePicker, KPI cards, filter dropdowns, data table
- Modal trigger on row click

**Step 16:** Update `shoudagor_FE/src/App.tsx`
- Add routes for `/reports/sr` and `/reports/dsr`

### Phase 7: Testing & Polish (1-2 hours)

**Step 17:** End-to-end testing
- Test full user flows for both reports
- Verify date filtering works correctly
- Test nested modal flow for DSR reports

**Step 18:** Edge case testing
- Empty data states
- Single record scenarios
- Large date ranges
- NULL variant handling

**Step 19:** UI/UX polish
- Consistent formatting (BDT currency, dates)
- Responsive design
- Loading states
- Error messages

---

## Appendix A: Key Technical Decisions

### A.1 Cost Basis Strategy

**Problem:** `ProductPrice.purchase_price` changes over time. Using current price for historical orders gives inaccurate P/L.

**Solution:** Use LATERAL JOIN to get the price that was active at the time of the order:
```sql
LEFT JOIN LATERAL (
    SELECT purchase_price
    FROM inventory.product_price pp
    WHERE pp.product_id = srod.product_id
      AND pp.effective_date <= sro.order_date
      AND pp.is_active = TRUE
    ORDER BY pp.effective_date DESC
    LIMIT 1
) pp ON TRUE
```

**Trade-offs:**
- ✅ Most accurate historical cost
- ✅ No schema changes needed
- ⚠️ Slightly more complex query
- ⚠️ Performance impact on large datasets (mitigated by indexes)

### A.2 Commission Pro-rating

**Problem:** Commission is stored at the order level, but detail modal needs per-line commission.

**Solution:** Divide order commission by number of line items using window function:
```sql
COALESCE(sro.commission_amount, 0) / NULLIF(COUNT(*) OVER (PARTITION BY sro.sr_order_id), 0)
```

**Trade-offs:**
- ✅ Simple approximation
- ✅ No additional data needed
- ⚠️ Not exact if commission varies by line item
- ⚠️ Future enhancement: store per-line commission

### A.3 Default Date Range

**Requirement:** "Default will be yesterday to Today"

**Implementation:**
- Backend: `if not (start_date and end_date): end_date = date.today(); start_date = end_date - timedelta(days=1)`
- Frontend: `useState<DateRange>({ from: subDays(new Date(), 1), to: new Date() })`

### A.4 Company Isolation

All queries include `WHERE company_id = :company_id` at the appropriate join level. This ensures:
- SRs from other companies are never visible
- DSR assignments are company-scoped
- Products/prices are company-scoped (via product_price joins)

---

## Appendix B: Performance Considerations

### B.1 Recommended Indexes

Check if these indexes exist; create if missing:
```sql
-- SR report indexes (likely already exist)
CREATE INDEX IF NOT EXISTS idx_sr_order_sr_date ON sales.sr_order(sr_id, order_date);
CREATE INDEX IF NOT EXISTS idx_sr_order_detail_order_product ON sales.sr_order_detail(sr_order_id, product_id, variant_id);

-- DSR report indexes (likely already exist)
CREATE INDEX IF NOT EXISTS idx_dsr_so_assignment_dsr_date ON sales.dsr_so_assignment(dsr_id, assigned_date, status);
CREATE INDEX IF NOT EXISTS idx_so_detail_order_product ON sales.sales_order_detail(sales_order_id, product_id, variant_id);

-- Product price index (critical for LATERAL JOIN performance)
CREATE INDEX IF NOT EXISTS idx_product_price_product_variant_date ON inventory.product_price(product_id, variant_id, effective_date DESC) WHERE is_active = TRUE;
```

### B.2 Query Performance

- **SR Summary:** Single query with LATERAL JOIN. Expected to be fast for < 1000 SR orders.
- **SR Detail:** Single query with LATERAL JOIN and window function. Expected to be fast for < 500 line items per SR.
- **DSR Summary:** Query with LEFT JOINs and correlated subquery. May need optimization if DSR has > 100 assignments.
- **DSR Loading:** Two CTEs with GROUP BY. Fast for typical DSR loads (< 50 product-variants).
- **DSR SO Breakdown:** Simple filtered join. Very fast.

### B.3 Caching Strategy

If performance becomes an issue:
- Cache summary responses for 5 minutes (Redis or in-memory)
- Invalidate cache when new orders are created
- Detail modals should not be cached (always fresh)

---

## Appendix C: Future Enhancements

1. **CSV Export:** Add export buttons for both reports
2. **Charts:** Add bar charts for SR performance comparison
3. **Per-line commission:** Store commission at detail level for exact P/L
4. **Batch cost tracking:** Use `SalesOrderBatchAllocation.unit_cost` for even more accurate cost basis
5. **Trend analysis:** Compare current period with previous period
6. **SR ranking:** Add rank column based on net profit
7. **DSR efficiency:** Calculate delivery completion rate and average delivery time
8. **Real-time updates:** WebSocket for live order updates
