# Shoudagor KPI Implementation Strategy & Study

**Document Version:** 1.0  
**Created:** April 7, 2026  
**Target Implementation:** Multi-Phase (4-6 weeks)  
**Scope:** Dashboard-Integrated KPI Reporting System

---

## Executive Summary

This document provides a comprehensive strategy for implementing a **KPI (Key Performance Indicator) Dashboard** for Shoudagor ERP system. The KPIs are designed to provide **real-time business insights**, **operational visibility**, and **strategic decision-making support** across sales, procurement, inventory, and financial domains.

### Strategic Objectives

1. **Real-Time Business Visibility** - Understand operations as they happen
2. **Performance Measurement** - Track business progress against targets
3. **Operational Excellence** - Identify bottlenecks and optimization opportunities
4. **Financial Health** - Monitor revenue, costs, profitability, and cash flow
5. **Strategic Decision Support** - Data-driven insights for business planning
6. **Workforce Accountability** - Track SR/DSR performance and productivity
7. **Risk Management** - Early warning indicators for business risks

---

## Part 1: Current System Analysis

### 1.1 Existing Infrastructure Assessment

#### ✅ Strengths

| Capability | Details |
|-----------|---------|
| **Advanced Reporting** | 28 existing reports across sales, procurement, inventory covering various analytical needs |
| **Batch-Level Tracking** | Full cost traceability through batch allocation and movement ledger |
| **Multi-Domain Data** | Comprehensive business data across sales, procurement, inventory, DSR, SR, warehouse |
| **Financial Tracking** | Invoice, payment, cost, and expenses tracking with FIFO/LIFO/WAC valuation methods |
| **Time-Series Data** | All operations timestamped with audit trails for trend analysis |
| **Distributed Workforce** | SR and DSR data with individual performance metrics |
| **Real-Time Activity Feed** | Dashboard activity tracking for operational insights |

#### 🎯 Current Gaps for KPI System

| Gap | Impact | Priority |
|-----|--------|----------|
| **No KPI Dashboard** | No single-screen business health view | **HIGH** |
| **Fragmented Metrics** | KPIs scattered across 28 reports, no consolidated view | **HIGH** |
| **Missing Targets** | No baseline or target comparison for performance | **HIGH** |
| **No Trend Analysis** | Period-over-period comparison missing | **MEDIUM** |
| **Limited Alerts** | No proactive warnings for out-of-range metrics | **MEDIUM** |
| **No Predictive Analytics** | No forecasting or trend projection | **MEDIUM** |
| **Missing SR ROI** | No clear SR individual ROI calculation | **HIGH** |
| **Inventory Health Gaps** | Limited stock adequacy and turnover insights | **MEDIUM** |

#### 📊 Existing Report Coverage

The system has strong foundational reports:

**Sales Reports (10):** Fulfillment, Financial, Inventory Performance, Team Analytics, Product Analysis, Territory, Customer Activity, Pipeline, Demand Forecast, Advanced Insights

**Procurement Reports (8):** Maverick Spend, Variance, Emergency Orders, Cash Flow, ABC/XYZ Classification, Supplier Consolidation, PO Progress, Uninvoiced Receipts

**Inventory Reports (10):** Warehouse Summary, Valuation, DSI/GMROI, Dead Stock, Safety Stock, Stock by Batch, Aging, COGS, Margin, Batch P&L

**SR Reports (7):** Damage, Cost-Profit, Daily, Budget, Reconciliation, DO Tracking, Slow Moving, Group Analytics

### 1.2 Business Domain Mapping

#### Sales Domain
- **Entities:** SalesOrder, Customer, SalesRepresentative, DeliverySalesRepresentative, SalesOrderDetail, Invoice
- **Metrics Available:** Order volume, revenue, customer count, SR performance, DSR efficiency
- **Business Questions:** Who are top customers? Which products sell best? What's DSR productivity? Which SRs need support?

#### Procurement Domain
- **Entities:** PurchaseOrder, Supplier, PurchaseOrderDetail, ProductOrderDelivery/Payment
- **Metrics Available:** Purchase volume, supplier performance, order cycle time, payment terms
- **Business Questions:** Which suppliers deliver on-time? What are lead times? Are there supply challenges?

#### Inventory Domain
- **Entities:** Batch, InventoryMovement, InventoryStock, Product, ProductVariant, Warehouse
- **Metrics Available:** Stock levels, batch age, turnover, valuation, COGS, dead stock
- **Business Questions:** Do we have right stock levels? What's inventory health? Are items moving?

#### Financial Domain
- **Entities:** Invoice, Expenses, SRDisbursement, DSRPaymentSettlement
- **Metrics Available:** Revenue, COGS, margins, expenses, profitability, cash flow
- **Business Questions:** How profitable are we? What's our cash position? Where's money being spent?

#### Workforce Domain
- **Entities:** SalesRepresentative, DeliverySalesRepresentative, SROrder
- **Metrics Available:** Individual sales, performance, ROI, targets, costs
- **Business Questions:** Who are top performers? What's productivity? Are costs justified by results?

---

## Part 2: KPI Framework Design

### 2.1 KPI Hierarchy & Categories

The KPI system is organized as a **4-Level Hierarchy**:

```
LEVEL 1: Executive Dashboard (5-7 Key Metrics)
    ↓
LEVEL 2: Domain KPIs (Business-specific metrics)
    ├── Sales KPIs (12-15 metrics)
    ├── Procurement KPIs (8-10 metrics)
    ├── Inventory KPIs (10-12 metrics)
    ├── Financial KPIs (8-10 metrics)
    └── Workforce KPIs (8-10 metrics)
    ↓
LEVEL 3: Detailed Reports (Drill-down analysis)
    ├── Customer Segmentation
    ├── Product Performance
    ├── Supplier Analysis
    └── Warehouse Analysis
    ↓
LEVEL 4: Operational Metrics (Real-time dashboards)
    ├── Daily Sales
    ├── Inventory Movement
    ├── Order Status
    └── SR/DSR Activity
```

### 2.2 KPI Characteristics

Every KPI should have:

```typescript
interface KPI {
  id: string;                    // Unique identifier
  name: string;                  // Display name
  description: string;           // Business context
  category: string;              // Sales, Procurement, Inventory, Financial, Workforce
  level: 1 | 2 | 3 | 4;         // Hierarchy level
  metric_type: string;           // Revenue, Count, Percentage, Days, Ratio
  calculation_formula: string;   // How to calculate
  data_source: string;           // Which tables/queries
  unit: string;                  // $, %, units, days
  frequency: string;             // Real-time, Daily, Weekly, Monthly
  target_value?: number;         // Target benchmark
  warning_threshold?: number;    // Alert threshold (%)
  critical_threshold?: number;   // Critical alert threshold (%)
  trend_period?: string;         // Period for trend: MTD, QTD, YTD, 12M
  owner: string;                 // Responsible stakeholder
  responsible_team: string;      // Sales, Ops, Procurement, Finance
  impact: string;                // Strategic, Operational, Tactical
}
```

---

## Part 3: Comprehensive KPI Definitions

### 3.1 LEVEL 1: Executive Dashboard KPIs (Business Health Overview)

These 6 KPIs provide a high-level snapshot of overall business health suitable for C-suite monitoring:

#### KPI 1.1: Total Revenue (MTD)
- **Definition:** Total sales revenue for current month-to-date
- **Calculation:** `SUM(Invoice.total_amount WHERE invoice.status = 'Issued' AND invoice.type = 'sale')`
- **Data Source:** `billing.invoice`, `sales.sales_order`
- **Unit:** Currency ($)
- **Frequency:** Real-time (updated on invoice creation/payment)
- **Target:** Company annual revenue / 12 * 1.1 (10% above monthly avg)
- **Display:** 
  - Current value
  - vs Target (%)
  - vs Previous Month (%)
  - vs YTD Average
- **Business Insight:** Is revenue on track? Are we beating/missing targets?
- **Actions Triggered:**
  - ⚠️ If MTD < 80% target → Sales team alert
  - 🔴 If MTD < 60% target → Executive review required

#### KPI 1.2: Gross Profit Margin (%)
- **Definition:** (Revenue - COGS) / Revenue * 100
- **Calculation:** `(SUM(SO.total_price) - SUM(BatchAllocation.unit_cost * allocated_qty)) / SUM(SO.total_price) * 100`
- **Data Source:** `sales.sales_order_batch_allocation`, `transaction.inventory_movement`
- **Unit:** Percentage (%)
- **Frequency:** Daily
- **Target:** 25-35% (industry standard for wholesale)
- **Display:**
  - Current margin %
  - Trend vs last 3 months
  - Margin by product category
  - Margin by top 5 customers
- **Business Insight:** Are we maintaining healthy margins? Which products are profitable?
- **Actions Triggered:**
  - ⚠️ If margin < 20% → Cost review required
  - 🔴 If margin < 15% → Emergency pricing review

#### KPI 1.3: Inventory Turnover Ratio
- **Definition:** COGS / Average Inventory Value
- **Calculation:** `SUM(COGS_monthly) / ((Inventory_BOMonth + Inventory_EOMonth) / 2)`
- **Data Source:** `inventory.inventory_movement`, `inventory.batch`
- **Unit:** Times (times per month)
- **Frequency:** Monthly
- **Target:** 4-6 times per month (vary by product category)
- **Display:**
  - Overall turnover
  - Turnover by warehouse
  - Turnover by product category
  - Comparison with industry benchmark
- **Business Insight:** Is inventory moving fast enough? Do we have excess stock?
- **Actions Triggered:**
  - ⚠️ If turnover < 2x → Dead stock investigation
  - 📈 If turnover > 8x → Stock adequacy review (stockout risk)

#### KPI 1.4: Days Sales Outstanding (DSO)
- **Definition:** (Average Accounts Receivable / Revenue) * Number of Days
- **Calculation:** `(SUM(Invoice.outstanding_amount) / SUM(Monthly_Revenue)) * 30`
- **Data Source:** `billing.invoice`, `sales.customer`
- **Unit:** Days
- **Frequency:** Daily
- **Target:** 15-20 days (standard for B2B wholesale)
- **Display:**
  - Current DSO
  - Trend over last 3 months
  - DSO by customer segment
  - Aging of outstanding invoices
- **Business Insight:** How quickly are we collecting payments? Is liquidity at risk?
- **Actions Triggered:**
  - ⚠️ If DSO > 30 days → Collection follow-up required
  - 🔴 If DSO > 45 days → Escalation for customer payment review

#### KPI 1.5: Operational Cash Flow (Monthly)
- **Definition:** Net cash from operations (Revenue - COGS - Expenses - Payables)
- **Calculation:** `Revenue - COGS - SUM(Expenses) - PO_Payment_Obligations`
- **Data Source:** `billing.invoice`, `billing.expenses`, `procurement.purchase_order`
- **Unit:** Currency ($)
- **Frequency:** Daily
- **Target:** Positive and > 10% of monthly revenue
- **Display:**
  - Current month cash flow
  - 3-month trend
  - Cash flow components breakdown
  - Forecast for next 30 days
- **Business Insight:** Do we have cash to operate? Are we cash positive?
- **Actions Triggered:**
  - 🔴 If cash flow < 0 → Immediate management review
  - ⚠️ If forecast shows negative → Proactive interventions needed

#### KPI 1.6: Overall Equipment Effectiveness (OEE) / SR ROI Index
- **Definition:** (Revenue per SR - Average SR Cost) / Average SR Cost * 100
- **Calculation:** `(AVG(SR_Revenue) - AVG(SR_Cost)) / AVG(SR_Cost) * 100`
- **Data Source:** `sales.sales_representative`, `sr_reports.daily_cost_expense`, `sales.sr_order`
- **Unit:** Percentage (%)
- **Frequency:** Weekly
- **Target:** > 150% (150% ROI on SR costs)
- **Display:**
  - Overall SR portfolio ROI
  - Individual SR ROI ranking
  - Cost vs Revenue by SR
  - Target vs Actual
- **Business Insight:** Is our distributed workforce economically viable? Who are high/low performers?
- **Actions Triggered:**
  - ⚠️ If ROI < 100% → Performance improvement plan
  - 🔴 If ROI < 50% → SR efficiency review or off-boarding

---

### 3.2 LEVEL 2: Domain-Specific KPIs

#### A. SALES KPIs (12 Metrics)

##### KPI 2.1: Order Fulfillment Rate (%)
- **Definition:** (Orders delivered on time / Total orders placed) * 100
- **Calculation:** `COUNT(SO WHERE delivery_date <= promise_date) / COUNT(SO) * 100`
- **Data Source:** `sales.sales_order`, `sales.sales_order_detail`
- **Unit:** Percentage
- **Frequency:** Daily
- **Target:** > 95%
- **Business Impact:** High - Customer satisfaction and loyalty

##### KPI 2.2: Average Order Value (AOV)
- **Definition:** Total revenue / Number of orders
- **Calculation:** `SUM(SO.total_price) / COUNT(SO)`
- **Data Source:** `sales.sales_order`
- **Unit:** Currency
- **Frequency:** Daily
- **Target:** Baseline + 5% YoY growth
- **Business Impact:** Revenue effectiveness

##### KPI 2.3: Customer Acquisition Cost (CAC)
- **Definition:** Total marketing/sales expenses / New customers acquired
- **Calculation:** `SUM(Marketing_Costs) / COUNT(New_Customers_This_Month)`
- **Data Source:** `sales.customer`, `billing.expenses`
- **Unit:** Currency per customer
- **Frequency:** Monthly
- **Target:** < 15% of first-year revenue per customer
- **Business Impact:** Sustainable growth
- **Components:**
  - SR recruitment & training costs
  - Sales enablement expenses
  - Channel development costs

##### KPI 2.4: Customer Lifetime Value (CLV)
- **Definition:** Average revenue per customer over entire relationship
- **Calculation:** `SUM(Customer_Revenue) / COUNT(Customers)`
- **Data Source:** `sales.customer`, `sales.sales_order`
- **Unit:** Currency
- **Frequency:** Monthly
- **Target:** CLV > 5x CAC ratio
- **Business Impact:** Strategic - sustainable profitability
- **Detailed Breakdown:** CLV by customer segment, category, channel

##### KPI 2.5: Product Category Performance Index
- **Definition:** Revenue growth and margin by category
- **Calculation:** `Category_Revenue_MTD / Sum_All_Revenue * 100`
- **Data Source:** `inventory.product_category`, `sales.sales_order_detail`
- **Unit:** Percentage, weighted score
- **Frequency:** Weekly
- **Components:**
  - Revenue contribution
  - Margin (%
  - Growth rate (vs prior period)
  - Volume trend
- **Business Impact:** Portfolio optimization

##### KPI 2.6: SR Sales Effectiveness (Revenue per SR, Daily)
- **Definition:** Average revenue generated per SR per day
- **Calculation:** `SUM(SR_Revenue) / COUNT(Active_SRs) / Business_Days_This_Month`
- **Data Source:** `sales.sales_representative`, `sales.sr_order`
- **Unit:** Currency per day
- **Frequency:** Daily
- **Target:** By SR experience level (1yr=$X, 2yr=$Y, 3+yr=$Z)
- **Business Impact:** High - Direct workforce productivity
- **Drill-downs:**
  - Revenue by individual SR
  - SR comparison matrix
  - New vs experienced SR performance
  - SR territory performance

##### KPI 2.7: Peak-to-Average Sales Ratio
- **Definition:** Identify demand seasonality and volatility
- **Calculation:** `Peak_Day_Sales / Average_Daily_Sales`
- **Data Source:** `sales.sales_order`
- **Unit:** Ratio
- **Frequency:** Weekly
- **Target:** < 2.0 (stable demand preferred)
- **Business Impact:** Demand planning and inventory management
- **Use Case:** If >2.5, suggests promotional spikes or seasonal patterns

##### KPI 2.8: Customer Retention Rate (%)
- **Definition:** (Customers at period-end who bought in prior period) / (Customers at period-start) * 100
- **Calculation:** `COUNT(Repeat_Customers) / COUNT(Customers_Last_Period) * 100`
- **Data Source:** `sales.customer`, `sales.sales_order`
- **Unit:** Percentage
- **Frequency:** Monthly
- **Target:** > 80% (high-value customers > 90%)
- **Business Impact:** Recurring revenue and profitability
- **Segments:**
  - Overall retention
  - By customer tier (high/medium/low value)
  - By SR

##### KPI 2.9: Returns & Refunds Rate (%)
- **Definition:** (Returned units / Delivered units) * 100
- **Calculation:** `SUM(SalesOrderDetail.returned_quantity) / SUM(SalesOrderDetail.shipped_quantity) * 100`
- **Data Source:** `sales.sales_order_detail`
- **Unit:** Percentage
- **Frequency:** Weekly
- **Target:** < 3% (good quality standard)
- **Business Impact:** Quality, customer satisfaction
- **Analysis:**
  - Returns by product category
  - Returns by customer
  - Root cause analysis (quality, wrong item, etc.)

##### KPI 2.10: Sales Order Cycle Time
- **Definition:** Average days from order placement to delivery
- **Calculation:** `AVG(Delivery_Date - Order_Date)`
- **Data Source:** `sales.sales_order`
- **Unit:** Days
- **Frequency:** Weekly
- **Target:** 3-5 days (standard for wholesale)
- **Business Impact:** Operational efficiency, customer satisfaction
- **Components:**
  - Order processing time
  - Picking & packing time
  - Delivery time
  - By DSR/Route efficiency

##### KPI 2.11: Customer Concentration Risk
- **Definition:** Revenue from top 5 customers as % of total
- **Calculation:** `SUM(Top5_Customers_Revenue) / SUM(Total_Revenue) * 100`
- **Data Source:** `sales.customer`, `sales.sales_order`
- **Unit:** Percentage
- **Frequency:** Monthly
- **Target:** < 30% (diversified portfolio)
- **Business Impact:** Risk management
- **Alert:** If >40%, heightened risk of revenue volatility

##### KPI 2.12: Sales Territory Performance Index
- **Definition:** Sales performance indexed by geographic territory/beat
- **Components:**
  - Revenue per beat
  - Orders per beat
  - Customers per beat
  - Forecast vs actual
- **Data Source:** `sales.beat`, `sales.sales_order`
- **Unit:** Index score
- **Frequency:** Weekly
- **Business Impact:** Territory planning, SR assignment optimization

---

#### B. PROCUREMENT KPIs (10 Metrics)

##### KPI 3.1: Procurement Cost Variance (%)
- **Definition:** (Actual cost - Budgeted cost) / Budgeted cost * 100
- **Calculation:** `(SUM(Actual_PO_Cost) - SUM(Budgeted_PO_Cost)) / SUM(Budgeted_PO_Cost) * 100`
- **Data Source:** `procurement.purchase_order`, `procurement.purchase_order_detail`
- **Unit:** Percentage
- **Frequency:** Weekly
- **Target:** ±3% (tight variance control)
- **Business Impact:** Cost control, budget management
- **Drill-downs:**
  - Variance by supplier
  - Variance by product category
  - Variance by cost center

##### KPI 3.2: Supplier On-Time Delivery Rate (%)
- **Definition:** (Deliveries received on or before promise date) / Total deliveries * 100
- **Calculation:** `COUNT(POD WHERE delivery_date <= promise_date) / COUNT(POD) * 100`
- **Data Source:** `procurement.product_order_delivery_detail`
- **Unit:** Percentage
- **Frequency:** Weekly
- **Target:** > 90% per supplier, >85% overall
- **Business Impact:** Supply chain reliability
- **Metrics by supplier:** Ranking, trend, reliability score

##### KPI 3.3: Purchase Order Lead Time (Days)
- **Definition:** Average days from PO creation to goods receipt
- **Calculation:** `AVG(Delivery_Date - PO_Creation_Date)`
- **Data Source:** `procurement.purchase_order`, `procurement.product_order_delivery_detail`
- **Unit:** Days
- **Frequency:** Weekly
- **Target:** By supplier (domestic <7 days, imported <30 days)
- **Business Impact:** Supply chain planning
- **Components:**
  - Lead time by supplier
  - Lead time by product category
  - Lead time trend (improving/worsening)

##### KPI 3.4: Supplier Quality Score
- **Definition:** Rejection and return rate per supplier
- **Calculation:** `(Rejected_Qty + Returned_Qty) / Received_Qty * 100`
- **Data Source:** `procurement.purchase_order_detail`
- **Unit:** Percentage (lower is better)
- **Frequency:** Monthly
- **Target:** < 2% rejection rate
- **Business Impact:** Quality assurance
- **Scoring:** 
  - On-time delivery (40% weight)
  - Rejection rate (40% weight)
  - Documentation accuracy (20% weight)

##### KPI 3.5: Inventory-to-Purchase Ratio
- **Definition:** Inventory value / Monthly procurement value
- **Calculation:** `Inventory_Value / (SUM(Monthly_PO_Cost) / 12)`
- **Data Source:** `inventory.batch`, `inventory.inventory_stock`, `procurement.purchase_order`
- **Unit:** Ratio (months of inventory)
- **Frequency:** Weekly
- **Target:** 2-3 months (just-in-time balancing)
- **Business Impact:** Inventory optimization, working capital efficiency
- **Alert:** If >4 months, excess inventory; If <1 month, stockout risk

##### KPI 3.6: Maverick Spend Rate (%)
- **Definition:** Off-contract purchases as % of total procurement
- **Calculation:** `SUM(Off_Contract_PO) / SUM(Total_PO) * 100`
- **Data Source:** `procurement.purchase_order`
- **Unit:** Percentage
- **Frequency:** Weekly
- **Target:** < 5% (controlled exceptions)
- **Business Impact:** Cost control, compliance
- **Analysis:** Reasons for maverick spend, cost impact

##### KPI 3.7: Days Payable Outstanding (DPO)
- **Definition:** Average days to pay suppliers after receipt
- **Calculation:** `(SUM(Outstanding_PO_Invoices) / Total_Monthly_Expenses) * 30`
- **Data Source:** `procurement.purchase_order`, `procurement.product_order_payment_detail`
- **Unit:** Days
- **Frequency:** Daily
- **Target:** Company payment terms (e.g., 45 days standard)
- **Business Impact:** Working capital management, supplier relationships
- **Monitoring:** Maintain terms, flag early/late payments

##### KPI 3.8: Supplier Concentration Risk
- **Definition:** Spend from top 3 suppliers as % of total
- **Calculation:** `SUM(Top3_Supplier_Cost) / SUM(Total_PO_Cost) * 100`
- **Data Source:** `procurement.supplier`, `procurement.purchase_order`
- **Unit:** Percentage
- **Frequency:** Monthly
- **Target:** < 40% (diversified supplier base)
- **Business Impact:** Risk management, supply chain resilience
- **Alert:** If >50%, single supplier dependency risk

##### KPI 3.9: Purchase Order Accuracy
- **Definition:** PO line items correctly fulfilled vs total line items
- **Calculation:** `COUNT(Correct_Deliveries) / COUNT(Total_POD_Lines) * 100`
- **Data Source:** `procurement.purchase_order_detail`, `procurement.product_order_delivery_detail`
- **Unit:** Percentage
- **Frequency:** Weekly
- **Target:** > 98% (high accuracy)
- **Business Impact:** Operational efficiency, waste reduction
- **Tracking:** By supplier, product category

##### KPI 3.10: Procurement Cycle Efficiency Index
- **Definition:** Composite index of procurement process efficiency
- **Components (weighted):**
  - Approval cycle time: 25%
  - PO-to-delivery time: 25%
  - Invoice-to-payment time: 25%
  - Exception rate: 25%
- **Unit:** Index (0-100)
- **Frequency:** Monthly
- **Target:** > 85
- **Business Impact:** Procurement effectiveness

---

#### C. INVENTORY KPIs (12 Metrics)

##### KPI 4.1: Inventory Turnover by Category
- **Definition:** COGS / Average Inventory (by product category)
- **Calculation:** `SUM(Category_COGS) / ((Category_BOMonth_Inventory + Category_EOMonth_Inventory) / 2)`
- **Data Source:** `inventory.batch`, `inventory.product_category`, `transaction.inventory_movement`
- **Unit:** Times per month
- **Frequency:** Monthly
- **Target:** By category (fast-moving: 6-8x, medium: 3-4x, slow: 1-2x)
- **Business Impact:** Category-level inventory health
- **Action Items:**
  - Fast movers: Ensure adequate stock, prevent stockouts
  - Slow movers: Reduce quantities, audit demand

##### KPI 4.2: Days Inventory Outstanding (DIO)
- **Definition:** Average days inventory is held before sale
- **Calculation:** `(Average_Inventory_Value / COGS) * 30`
- **Data Source:** `inventory.batch`, `transaction.inventory_movement`
- **Unit:** Days
- **Frequency:** Weekly
- **Target:** 15-25 days (optimal balance)
- **Business Impact:** Working capital efficiency
- **Benchmarking:** By warehouse, location, category

##### KPI 4.3: Dead Stock Inventory (%)
- **Definition:** Value of items with zero movement (>60 days) / Total inventory
- **Calculation:** `SUM(DeadStock_Value) / SUM(Total_Inventory_Value) * 100`
- **Data Source:** `inventory.batch`, `inventory.inventory_movement`
- **Unit:** Percentage
- **Frequency:** Weekly
- **Target:** < 5%
- **Business Impact:** Working capital and storage optimization
- **Actions:**
  - List dead stock items
  - Mark-down strategy
  - Donation or disposal

##### KPI 4.4: Stock Adequacy Ratio
- **Definition:** Ratio of current stock to safety stock level
- **Calculation:** `Current_Stock / Safety_Stock_Level`
- **Data Source:** `inventory.inventory_stock`, `inventory.product`
- **Unit:** Ratio
- **Frequency:** Daily
- **Target:** 1.5 - 2.5x safety stock (avoid stockouts while minimizing excess)
- **Business Impact:** Service level management
- **Alerts:**
  - ⚠️ If <1.0 → Stockout risk
  - 🔴 If <0.5 → Emergency reorder

##### KPI 4.5: Warehouse Utilization Rate (%)
- **Definition:** Actual storage used / Available storage capacity
- **Calculation:** `SUM(Used_Locations) / SUM(Total_Locations) * 100`
- **Data Source:** `warehouse.warehouse`, `warehouse.storage_location`, `warehouse.inventory_stock`
- **Unit:** Percentage
- **Frequency:** Weekly
- **Target:** 70-85% (balanced utilization)
- **Business Impact:** Facility efficiency, expansion planning
- **Drill-downs:**
  - Utili by warehouse
  - By storage location type
  - Space available for growth

##### KPI 4.6: Batch Cost Variance
- **Definition:** Variance between actual and expected unit cost per batch
- **Calculation:** `(Actual_Unit_Cost - Expected_Unit_Cost) / Expected_Unit_Cost * 100`
- **Data Source:** `inventory.batch`
- **Unit:** Percentage
- **Frequency:** Weekly
- **Target:** ±5% variance
- **Business Impact:** Cost accuracy for margin calculations
- **Tracking:** By supplier, product category

##### KPI 4.7: Inventory Shrinkage Rate (%)
- **Definition:** Unaccounted for inventory loss / Starting inventory
- **Calculation:** `(Expected_Inventory - Actual_Inventory) / Expected_Inventory * 100`
- **Data Source:** `inventory.batch`, `transaction.inventory_adjustment`
- **Unit:** Percentage
- **Frequency:** Monthly
- **Target:** < 1%
- **Business Impact:** Fraud prevention, operational integrity
- **Alerts:**
  - ⚠️ If >1% → Audit investigation
  - 🔴 If >2% → Management review + corrective action

##### KPI 4.8: Batch Allocation Efficiency
- **Definition:** Batch matches to sales orders vs fragmented allocations
- **Calculation:** `Orders_With_<2_Batch_Splits / Total_Orders * 100`
- **Data Source:** `sales.sales_order_batch_allocation`
- **Unit:** Percentage
- **Frequency:** Weekly
- **Target:** > 80% (minimize batch fragmentation)
- **Business Impact:** Picking efficiency, shipping optimization
- **Components:**
  - Orders with 1 batch: Best case
  - Orders with 2-3 batches: Acceptable
  - Orders with >3 batches: Flag for optimization

##### KPI 4.9: Aged Inventory Percentage By Bucket
- **Definition:** Inventory breakdown by age buckets
- **Buckets:**
  - 0-30 days: %
  - 31-60 days: %
  - 61-90 days: %
  - 91-180 days: %
  - 180+ days: %
- **Data Source:** `inventory.batch`
- **Unit:** Percentage breakdown
- **Frequency:** Weekly
- **Target:** 
  - 0-30 days: 50%+
  - 31-60 days: 25-30%
  - 180+ days: <5%
- **Business Impact:** Inventory freshness, COGS management
- **Actions:** Move old stock first (FIFO), mark-down old batches

##### KPI 4.10: COGS Accuracy (Variance %)
- **Definition:** Batch-allocated COGS vs standard/expected COGS
- **Calculation:** `ABS(Actual_COGS - Standard_COGS) / Standard_COGS * 100`
- **Data Source:** `sales.sales_order_batch_allocation`, `inventory.batch`
- **Unit:** Percentage
- **Frequency:** Weekly
- **Target:** ±3% variance
- **Business Impact:** Financial accuracy, margin calculation reliability
- **Audit:** Regular reconciliation with standard costing system

##### KPI 4.11: Reorder Frequency & Costs
- **Definition:** Efficiency of replenishment cycle
- **Components:**
  - Reorder point hits per month
  - Average reorder cycle time
  - Reorder processing cost per order
- **Data Source:** `inventory.inventory_movement`, `procurement.purchase_order`
- **Unit:** Times/month, days, currency
- **Frequency:** Monthly
- **Target:** Minimize reorder cost while maintaining service level
- **Business Impact:** Procurement efficiency

##### KPI 4.12: Inventory Write-Off Rate (%)
- **Definition:** Value of inventory adjustments (damage, expiration) / Starting inventory
- **Calculation:** `SUM(Write_Off_Adjustments) / Starting_Inventory_Value * 100`
- **Data Source:** `transaction.inventory_adjustment`
- **Unit:** Percentage
- **Frequency:** Monthly
- **Target:** < 0.5%
- **Business Impact:** Asset protection, quality control
- **Alerts:** Flag unusually high rates for investigation

---

#### D. FINANCIAL KPIs (10 Metrics)

##### KPI 5.1: Gross Profit Margin (%) - By Category
- **Definition:** (Category Revenue - Category COGS) / Category Revenue * 100
- **Calculation:** Per-category breakdown
- **Data Source:** `sales.sales_order_detail`, `inventory.batch`
- **Unit:** Percentage
- **Frequency:** Daily
- **Target:** 
  - Premium items: 35-40%
  - Standard items: 25-30%
  - Economy items: 15-20%
- **Business Impact:** Portfolio optimization, pricing strategy
- **Actions:**
  - Identify low-margin categories
  - Pricing or cost reduction strategies
  - Product mix optimization

##### KPI 5.2: Operating Margin (%)
- **Definition:** (Revenue - COGS - Operating Expenses) / Revenue * 100
- **Calculation:** `(Revenue - COGS - Expenses) / Revenue * 100`
- **Data Source:** `billing.invoice`, `inventory.batch`, `billing.expenses`
- **Unit:** Percentage
- **Frequency:** Weekly
- **Target:** 10-15% (healthy business)
- **Business Impact:** Bottom-line profitability
- **Components:**
  - Raw margin
  - Less: Overhead
  - Less: Labor
  - Less: Distribution
  - Equals: Operating profit

##### KPI 5.3: Return on Assets (ROA) %
- **Definition:** Net Profit / Average Total Assets * 100
- **Calculation:** `Net_Profit / ((Assets_BOMonth + Assets_EOMonth) / 2) * 100`
- **Data Source:** All accounting records
- **Unit:** Percentage
- **Frequency:** Monthly
- **Target:** > 8% (asset utilization)
- **Business Impact:** Asset efficiency
- **Benchmarking:** Industry comparison

##### KPI 5.4: Return on Equity (ROE) %
- **Definition:** Net Profit / Shareholders Equity * 100
- **Calculation:** `Net_Profit / Shareholders_Equity * 100`
- **Unit:** Percentage
- **Frequency:** Monthly
- **Target:** > 15% (shareholder return)
- **Business Impact:** Strategic - Shareholder value
- **Tracking:** Quarterly, vs plan

##### KPI 5.5: Break-Even Point (Monthly Revenue)
- **Definition:** Fixed costs / Contribution Margin %
- **Calculation:** `Fixed_Costs / ((Revenue - Variable_Costs) / Revenue)`
- **Data Source:** `billing.expenses`, `sales.sales_order`
- **Unit:** Currency
- **Frequency:** Monthly
- **Target:** < 50% of actual monthly revenue
- **Business Impact:** Risk management
- **Days to break-even:** Current revenue run-rate vs break-even

##### KPI 5.6: Budget Variance Analysis (%)
- **Definition:** (Actual - Budget) / Budget for major cost categories
- **Categories:**
  - COGS variance
  - Labor variance
  - Distribution variance
  - Overhead variance
- **Unit:** Percentage
- **Frequency:** Weekly
- **Target:** ±5% variance per category
- **Business Impact:** Cost control accountability
- **Root cause:** Investigation of significant variances

##### KPI 5.7: Cash Conversion Cycle (Days)
- **Definition:** DSI + DSO - DPO
  - DSI: Days Sales of Inventory
  - DSO: Days Sales Outstanding
  - DPO: Days Payable Outstanding
- **Calculation:** `(Inventory_Days + Receivable_Days - Payable_Days)`
- **Data Source:** All operational records
- **Unit:** Days
- **Frequency:** Weekly
- **Target:** 0-10 days (negative is excellent - suppliers finance growth)
- **Business Impact:** Working capital efficiency, cash flow
- **Components:** Breakdown of each element
- **Benchmarking:** Industry standard

##### KPI 5.8: Debt-to-Equity Ratio
- **Definition:** Total Liabilities / Total Equity
- **Calculation:** `Total_Liabilities / Shareholders_Equity`
- **Unit:** Ratio
- **Frequency:** Monthly
- **Target:** < 1.5 (moderate leverage)
- **Business Impact:** Financial leverage, solvency
- **Trend:** Tracking over quarters

##### KPI 5.9: Current Ratio (Liquidity)
- **Definition:** Current Assets / Current Liabilities
- **Calculation:** `(Cash + Receivables + Inventory) / (Payables + Current_Portion_Debt)`
- **Unit:** Ratio
- **Frequency:** Weekly
- **Target:** 1.5 - 2.5 (healthy liquidity)
- **Business Impact:** Short-term solvency
- **Alert:** If <1.0, working capital crisis

##### KPI 5.10: Expense Ratio By Category (%)
- **Definition:** Each expense category as % of revenue
- **Categories:**
  - Personnel costs
  - Transportation & logistics
  - Storage & utilities
  - Technology & communications
  - Professional services
- **Data Source:** `billing.expenses`
- **Unit:** Percentage (% of revenue)
- **Frequency:** Weekly
- **Target:** Industry benchmarks (varies by category)
- **Business Impact:** Cost structure optimization
- **Trending:** YoY comparison

---

#### E. WORKFORCE KPIs (10 Metrics)

##### KPI 6.1: Sales Per SR (Daily Average)
- **Definition:** Average daily revenue generated per active SR
- **Calculation:** `SUM(SR_Revenue_MTD) / COUNT(Active_SRs) / Business_Days_MTD`
- **Data Source:** `sales.sales_representative`, `sales.sr_order`
- **Unit:** Currency per day
- **Frequency:** Daily
- **Target:** Segmented by experience level
  - New SR (<1 year): $X/day
  - Experienced SR (1-3 years): $Y/day
  - Senior SR (3+ years): $Z/day
- **Business Impact:** Workforce productivity
- **Individual dashboard:** Each SR sees own performance

##### KPI 6.2: SR Cost-to-Revenue Ratio
- **Definition:** Total SR costs / SR-generated revenue
- **Calculation:** `(Base_Salary + Commission + Daily_Costs) / SR_Revenue`
- **Data Source:** `sr_reports.daily_cost_expense`, `sales.sr_order`, `sales.sr_disbursement`
- **Unit:** Ratio or Percentage
- **Frequency:** Monthly
- **Target:** 20-30% (profitable SR operations)
- **Business Impact:** Economic viability of SR
- **Components:**
  - Fixed cost ratio
  - Variable cost ratio
  - ROI calculation

##### KPI 6.3: SR Target Achievement (%)
- **Definition:** Actual sales / Set target * 100
- **Calculation:** `Actual_Revenue / Target_Revenue * 100`
- **Data Source:** `sr_reports.sales_budget`, `sales.sr_order`
- **Unit:** Percentage
- **Frequency:** Daily, Weekly, Monthly
- **Target:** > 100% (meet target)
- **Business Impact:** Performance management, accountability
- **Components:**
  - Individual SR achievement
  - Team achievement (by region)
  - Category-wise achievement

##### KPI 6.4: SR Order Quality Metrics
- **Definition:** Quality of orders booked by SR
- **Components:**
  - Average order value per SR
  - Customer credit worthiness (credit score)
  - Order acceptance rate (not cancelled)
  - Return rate from SR orders
- **Unit:** Currency, score, percentage
- **Frequency:** Weekly
- **Target:** 
  - AOV > avg by 5%
  - Return rate < 2%
- **Business Impact:** Order quality, sales quality
- **Alerts:** SRs with unusually high returns or low-quality orders

##### KPI 6.5: Customer Visits & Coverage
- **Definition:** Number of customer visits per SR, territory coverage
- **Calculation:**
  - Visits per day: Calls made / working days
  - Territory coverage: Customers visited / total customers in territory
- **Data Source:** `sales.sr_order`, `sales.customer`
- **Unit:** Visits/day, percentage
- **Frequency:** Daily
- **Target:**
  - Visits/day: 10-15
  - Territory coverage: > 80%/month
- **Business Impact:** Market coverage, engagement
- **Analysis:**
  - High visit rate but low sales → Engagement issue
  - Low visit rate → Capacity issue

##### KPI 6.6: DSR Delivery Efficiency
- **Definition:** Orders delivered on time / Total assignments
- **Calculation:** `Count(On_Time_Deliveries) / Count(Total_Assignments) * 100`
- **Data Source:** `sales.dsr_so_assignment`, `sales.sales_order`
- **Unit:** Percentage
- **Frequency:** Daily
- **Target:** > 95%
- **Business Impact:** Customer satisfaction
- **Components:**
  - Timeliness of delivery
  - Order completeness (no short-shipments)
  - Condition of goods on delivery

##### KPI 6.7: Product Damage by SR / DSR
- **Definition:** High-value damage incidents per SR
- **Calculation:** `SUM(Damage_Cost) / Count(Orders_Handled)`
- **Data Source:** `sr_reports.product_damage`
- **Unit:** Currency per order, or incident rate
- **Frequency:** Weekly
- **Target:** < 1% of order value
- **Business Impact:** Quality, cost control
- **Action:** SRs with high damage rates need training or equipment support

##### KPI 6.8: SR Daily Cost Breakdown
- **Definition:** Detailed daily costs for SR operations
- **Components:**
  - Van/fuel costs
  - Oil/maintenance
  - Labour
  - Office costs
  - Other costs
- **Data Source:** `sr_reports.daily_cost_expense`
- **Unit:** Currency, % of revenue
- **Frequency:** Daily tracking, weekly analysis
- **Target:** Total daily cost < 40% of daily revenue
- **Business Impact:** Cost control, profitability
- **Optimization:** Identify cost-reduction opportunities

##### KPI 6.9: New Customer Acquisition by SR
- **Definition:** New customers acquired per SR per month
- **Calculation:** `Count(New_Customers_Assigned_to_SR) / COUNT(SRs)`
- **Data Source:** `sales.customer`, `sales.sr_order`
- **Unit:** Count per month
- **Frequency:** Monthly
- **Target:** > 5 new customers/month/SR
- **Business Impact:** Growth driver
- **Tracking:**
  - By SR (ranking)
  - By region
  - New customer retention rate

##### KPI 6.10: Workforce Turnover Rate (%)
- **Definition:** Exited SRs / Average workforce * 100
- **Calculation:** `Count(Exited_SRs) / Avg_Active_SRs * 100`
- **Data Source:** `sales.sales_representative`
- **Unit:** Percentage (monthly/annually)
- **Frequency:** Monthly
- **Target:** < 5% monthly (< 60% annually acceptable for field)
- **Business Impact:** Stability, morale, continuity
- **Analysis:**
  - Involuntary vs voluntary
  - By tenure (new vs experienced)
  - Cost impact of turnover

---

### 3.3 LEVEL 3: Detailed Analytical Reports (Drill-Down)

These provide deeper analysis and context for Level 2 KPIs:

#### 3.3.1 Customer Segmentation Report
- **RFM Analysis** (Recency, Frequency, Monetary)
  - Recent customers (ordered last 30 days)
  - Loyal customers (>10 orders)
  - High-value customers (top 20% by revenue)
- **Customer Tiers:** Premium, Gold, Silver, Bronze
- **Customer Health Score:** (Payment history + engagement + growth) / 3
- **Churn Risk:** Customers showing declining purchases

#### 3.3.2 Product Performance Drill-Down
- **Sales Velocity Report:** By product, by category, by warehouse
- **Margin Analysis:** By product, by batch, by customer
- **Inventory Movement:** Fast movers vs slow movers
- **Seasonality:** Demand patterns and peaks

#### 3.3.3 Supplier Performance Scorecard
- **On-time delivery tracking**
- **Quality metrics** (rejection/return rate)
- **Cost compliance** vs negotiated rates
- **Communication score** (responsiveness)
- **Overall supplier rating**

#### 3.3.4 Warehouse & Location Analysis
- **Stock distribution** across warehouses
- **Picking efficiency** metrics
- **Space utilization** trends
- **Slow-moving inventory** by location

---

### 3.4 LEVEL 4: Operational Metrics (Real-Time Dashboards)

These update in real-time as transactions occur:

#### 3.4.1 Daily Sales Dashboard
- **Today's sales** (running total)
- **Top sellers today** (by product, by SR)
- **Orders in process** (pending delivery, payment)
- **Critical issues** (out-of-stock, quality issues)
- **Forecast vs actual** (day-to-date vs target)

#### 3.4.2 Inventory Movement Monitor
- **Inbound today** (PO receipts)
- **Outbound today** (SO shipments)
- **Stock adjustments** (removals, transfers)
- **Movement by category**
- **Critical stock levels** (below safety stock)

#### 3.4.3 Order Status Tracker
- **NEW orders** (last hour)
- **IN PROCESS** (waiting for picking/delivery)
- **DELIVERED** (just completed)
- **ISSUES** (quality, incomplete, damaged)

#### 3.4.4 SR Activity Monitor (For Managers)
- **Active SRs** (in field today)
- **Orders booked today**
- **Customer visits today**
- **Performance vs daily target**
- **Issues reported**

---

## Part 4: KPI Dashboard UI/UX Design

### 4.1 Dashboard Hierarchy

```
┌─────────────────────────────────────────────────────────────┐
│ SHOUDAGOR KPI DASHBOARD                  [Filters] [Export]  │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  LEVEL 1: Executive Dashboard (6 KPI Cards)                 │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐        │
│  │ Revenue      │ │ Gross Margin │ │ Inventory    │        │
│  │ $2.5M        │ │ 28.5%        │ │ Turnover     │        │
│  │ +12% vs MTD  │ │ ±2% vs trend │ │ 4.2x         │        │
│  └──────────────┘ └──────────────┘ └──────────────┘        │
│                                                               │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐        │
│  │ DSO (Days)   │ │ Cash Flow    │ │ SR ROI       │        │
│  │ 18           │ │ $156K        │ │ 175%         │        │
│  │ Trend ↓      │ │ Healthy      │ │ Above avg ↑  │        │
│  └──────────────┘ └──────────────┘ └──────────────┘        │
│                                                               │
│  [View Details] [Domain Selection: Sales|Procurement| ...]  │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  LEVEL 2: Domain KPIs (Selectable - Sales/Proc/Inv/Fin/HR)  │
│  ┌─ SALES METRICS ────────────────────────────────────────┐ │
│  │ Order Fulfillment │ AOV    │ CAC    │ CLV    │ SR Eff. │ │
│  │ 96.2%            │ $450  │ $32   │ $8,400│ $340/day │ │
│  │ ✓ Above target   │ ↑5% YoY│ ω  │ 260x CAC│ +8% MoM │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                               │
│  [Charts/Detailed Views Below - Expandable]                 │
│                                                               │
│  LEVEL 3: Detailed Analysis                                 │
│  [Drill-Down Report: Select KPI from above for detailed ...]│
│                                                               │
│  LEVEL 4: Real-Time Operations                              │
│  [Activity Feed: Orders, Inventory, SR Activity Real-time]  │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 Dashboard Components

#### 4.2.1 KPI Card Component
```typescript
// Components/KPI/KPICard.tsx
interface KPICardProps {
  kpiId: string;
  title: string;
  value: number;
  unit: string;
  target: number;
  previousValue?: number;
  trend?: 'up' | 'down' | 'flat';
  status: 'healthy' | 'warning' | 'critical';
  sparklineData?: number[]; // 30-day trend
  onClick?: () => void;
}

// Visual Elements:
// - Large value display (prominent typography)
// - Color coding: Green (healthy), Orange (warning), Red (critical)
// - VS Target: % difference with arrow indicator
// - Sparkline chart showing 30-day trend
// - Compare period selector (MTD vs last period)
```

#### 4.2.2 KPI Comparison Table
```typescript
// For comparing multiple KPIs in one view
// Columns: KPI Name, Current, Target, Status, Trend, Action
// Rows: Each KPI
// Color-coded status rows
// Click row for drill-down
```

#### 4.2.3 KPI Trend Chart
```typescript
// Line chart showing 12-month (or daily/weekly) trend
// Dual axis: Value + Target line
// Shaded zones: Healthy, Warning, Critical
// Hover shows specific values
// Download CSV option
```

#### 4.2.4 KPI Waterfall Chart (for compositional metrics)
```typescript
// Breaks down composite metrics
// Example: Gross Margin = Revenue - COGS
// Shows contribution of each component
```

#### 4.2.5 KPI Status Badge
```typescript
// Visual status indicator
// ✓ Target Achieved (Green)
// ⚠ Warning - Below Target (Orange)
// ✗ Critical - Far Below Target (Red)
// With % deviation displayed
```

### 4.3 Filter & Control Panel
```typescript
// Filters applicable across all dashboards:
// - Date Range (Today, MTD, QTD, YTD, Last 30/90 days, Custom)
// - Company (if multi-tenant)
// - Territory/Region (for SR analysis)
// - Product Category
// - Warehouse/Location
// - SR/DSR filter
// - Customer Segment
// - Supplier
//
// Save Filter: Allow users to save favorite filter combinations
// Export: PDF, Excel, CSVformat
// Refresh Rate: Auto-refresh options (real-time, 1 min, 5 min, hourly)
```

---

## Part 5: Technical Implementation Plan

### 5.1 Backend Architecture

#### 5.1.1 New Database Schema (KPI Configuration)
```sql
-- KPI Master Configuration
CREATE TABLE kpi.kpi_definition (
  id UUID PRIMARY KEY,
  kpi_code VARCHAR UNIQUE,           -- e.g., "REVENUE_MTD"
  name VARCHAR,                       -- e.g., "Total Revenue (MTD)"
  description TEXT,
  category VARCHAR,                   -- Sales, Procurement, Inventory, Financial, Workforce
  level INTEGER,                      -- 1, 2, 3, or 4
  metric_type VARCHAR,                -- Count, Revenue, Percentage, Days, Ratio
  unit VARCHAR,                       -- $, %, units, days
  calculation_formula JSONB,          -- SQL template or calculation logic
  data_source JSONB,                 -- Tables and joins needed
  frequency VARCHAR,                  -- Real-time, Daily, Weekly, Monthly
  created_by UUID,
  created_at TIMESTAMP,
  updated_by UUID,
  updated_at TIMESTAMP
);

-- KPI Targets & Benchmarks
CREATE TABLE kpi.kpi_target (
  id UUID PRIMARY KEY,
  kpi_id UUID FK kpi_definition.id,
  company_id UUID FK security.app_client.id,
  target_value DECIMAL,
  warning_threshold_percent DECIMAL,    -- % below target
  critical_threshold_percent DECIMAL,   -- % below target
  period VARCHAR,                        -- Monthly, Quarterly, Annual
  year INTEGER,
  effective_from DATE,
  effective_to DATE,
  created_by UUID,
  created_at TIMESTAMP
);

-- KPI Actual Values (Time-Series)
CREATE TABLE kpi.kpi_value (
  id UUID PRIMARY KEY,
  kpi_id UUID FK kpi_definition.id,
  company_id UUID FK security.app_client.id,
  period_date DATE,                   -- For daily/weekly/monthly aggregation
  period_type VARCHAR,                -- daily, weekly, monthly
  actual_value DECIMAL,
  target_value DECIMAL,
  variance_percent DECIMAL,           -- (actual - target) / target * 100
  status VARCHAR,                      -- healthy, warning, critical
  calculated_at TIMESTAMP,
  refresh_count INTEGER DEFAULT 0,    -- For cache invalidation
  created_at TIMESTAMP,
  UNIQUE (kpi_id, company_id, period_date, period_type)
);

-- KPI Alert History
CREATE TABLE kpi.kpi_alert (
  id UUID PRIMARY KEY,
  kpi_id UUID FK kpi_definition.id,
  company_id UUID FK security.app_client.id,
  alert_status VARCHAR,               -- warning, critical
  alert_value DECIMAL,
  alert_date TIMESTAMP,
  acknowledged_by UUID FK security.app_user.id,
  acknowledged_at TIMESTAMP,
  created_at TIMESTAMP
);
```

#### 5.1.2 New Services Layer

```python
# app/services/kpi/kpi_service.py
class KPIService:
    def get_kpi_definition(self, kpi_code: str) -> KPI:
        pass
    
    def calculate_kpi(self, kpi_code: str, company_id: str, period_date: date) -> KPIValue:
        """Calculate KPI based on definition"""
        pass
    
    def get_kpi_value(self, kpi_code: str, company_id: str, period: str) -> KPIValue:
        """Get cached Or calculated KPI value"""
        pass
    
    def get_kpi_trend(self, kpi_code: str, company_id: str, days: int = 90) -> List[KPIValue]:
        """Get historical trend"""
        pass
    
    def get_dashboard_kpis(self, level: int, domain: str, company_id: str) -> List[KPIValue]:
        """Get all KPIs for a dashboard"""
        pass
    
    def check_kpi_alerts(self, company_id: str) -> List[KPIAlert]:
        """Check which KPIs are in warning/critical"""
        pass

# app/services/kpi/kpi_calculation_engine.py
class KPICalculationEngine:
    def calculate_revenue_mtd(self, company_id: str) -> Decimal:
        query = """
        SELECT SUM(total_amount) 
        FROM billing.invoice 
        WHERE company_id = %s 
          AND EXTRACT(MONTH FROM invoice_date) = EXTRACT(MONTH FROM NOW())
          AND status = 'Issued'
        """
        pass
    
    def calculate_gross_margin(self, company_id: str, period: str) -> Decimal:
        # (Revenue - COGS) / Revenue * 100
        pass
    
    def calculate_inventory_turnover(self, company_id: str) -> Decimal:
        # COGS / Average Inventory
        pass
    
    # ... 50+ calculation methods for each KPI
```

#### 5.1.3 API Endpoints

```python
# app/api/kpi.py
@router.get("/kpi/definitions")
async def list_kpi_definitions(
    level: int = None,
    category: str = None,
) -> List[KPIDefinition]:
    """List KPI definitions"""

@router.get("/kpi/{kpi_code}")
async def get_kpi(
    kpi_code: str,
    period: str = "MTD",  # MTD, QTD, YTD, 30D, 90D
    company_id: str = Header(...)
) -> KPIValue:
    """Get current KPI value"""

@router.get("/kpi/{kpi_code}/trend")
async def get_kpi_trend(
    kpi_code: str,
    days: int = 90,
    company_id: str = Header(...)
) -> List[KPIValue]:
    """Get KPI trend"""

@router.get("/kpi/dashboard/{level}")
async def get_dashboard(
    level: int,  # 1, 2, 3, 4
    domain: str = None,
    company_id: str = Header(...)
) -> KPIDashboard:
    """Get complete dashboard for a level"""

@router.get("/kpi/alerts")
async def get_kpi_alerts(
    company_id: str = Header(...)
) -> List[KPIAlert]:
    """Get all active KPI alerts"""

@router.post("/kpi/targets")
async def set_kpi_targets(
    kpi_id: str,
    targets: KPITargetInput,
    company_id: str = Header(...)
):
    """Set KPI targets for company"""
```

### 5.2 Frontend Architecture

#### 5.2.1 New Pages Structure

```
shoudagor_FE/src/pages/kpi/
├── Dashboard.tsx              # Main KPI dashboard (selector for levels)
├── Level1ExecutiveDashboard.tsx  # 6 KPI cards
├── Level2DomainDashboards/
│   ├── SalesKPIs.tsx         # Sales domain KPIs
│   ├── ProcurementKPIs.tsx   # Procurement KPIs
│   ├── InventoryKPIs.tsx     # Inventory KPIs
│   ├── FinancialKPIs.tsx     # Financial KPIs
│   └── WorkforceKPIs.tsx     # Workforce KPIs
├── Level3DetailedAnalysis/
│   ├── CustomerSegmentation.tsx
│   ├── ProductPerformance.tsx
│   ├── SupplierScorecard.tsx
│   └── WarehouseAnalysis.tsx
├── Level4RealTimeOps/
│   ├── DailySalesDashboard.tsx
│   ├── InventoryMonitor.tsx
│   ├── OrderStatusTracker.tsx
│   └── SRActivityMonitor.tsx
├── KPISettings.tsx          # Configure targets, thresholds
└── KPIReports.tsx          # Export, scheduled reports
```

#### 5.2.2 New Components

```
shoudagor_FE/src/components/kpi/
├── KPICard.tsx              # Reusable KPI display card
├── KPITrendChart.tsx        # Trend visualization
├── KPIComparisonTable.tsx   # Multi-KPI table view
├── KPIWaterfallChart.tsx    # Component breakdown
├── KPIAlertBar.tsx          # Alert notification
├── KPIFilterPanel.tsx       # Date, category, territory filters
├── KPIDashboardGrid.tsx     # Responsive grid layout
└── KPIExportButton.tsx      # Export functionality
```

#### 5.2.3 Hooks

```typescript
// shoudagor_FE/src/hooks/useKPI.ts
export function useKPI(kpiCode: string, period: string) {
  const [kpi, setKpi] = useState<KPIValue>(null);
  const [loading, setLoading] = useState(false);
  
  useEffect(() => {
    // Fetch KPI value
  }, [kpiCode, period]);
  
  return { kpi, loading };
}

// shoudagor_FE/src/hooks/useKPIDashboard.ts
export function useKPIDashboard(level: number, domain?: string) {
  // Fetch all KPIs for a dashboard
}

// shoudagor_FE/src/hooks/useKPITrend.ts
export function useKPITrend(kpiCode: string, days: number = 90) {
  // Fetch historical trend
}
```

#### 5.2.4 API Client

```typescript
// shoudagor_FE/src/lib/api/kpiApi.ts
export const kpiApi = {
  getDefinitions: (level?: number, category?: string) => 
    api.get('/kpi/definitions', { params: { level, category } }),
  
  getKPI: (kpiCode: string, period: string) =>
    api.get(`/kpi/${kpiCode}`, { params: { period } }),
  
  getKPITrend: (kpiCode: string, days: number) =>
    api.get(`/kpi/${kpiCode}/trend`, { params: { days } }),
  
  getDashboard: (level: number, domain?: string) =>
    api.get(`/kpi/dashboard/${level}`, { params: { domain } }),
  
  getAlerts: () =>
    api.get('/kpi/alerts'),
  
  setTargets: (kpiId: string, targets: KPITargetInput) =>
    api.post(`/kpi/targets`, { kpi_id: kpiId, ...targets }),
};
```

---

## Part 6: Implementation Roadmap

### Phase 1: Foundation (Weeks 1-2)

#### Week 1: Database & Core Services
- ✅ Design KPI configuration schema
- ✅ Create KPI definition table with 10 sample KPIs
- ✅ Create KPI value (time-series) table
- ✅ Create KPI target & alert tables
- ✅ Implement KPIService core methods
- ✅ Implement KPICalculationEngine base

**Deliverable:** Database schema, core Python services

#### Week 2: API & Calculation Engine
- ✅ Implement 10 core KPI calculations (Revenue, Margin, Turnover, DSO, Cash Flow, SR ROI, etc.)
- ✅ Create KPI API endpoints (get, trend, dashboard)
- ✅ Build KPI caching/refresh mechanism
- ✅ Implement alert logic

**Deliverable:** Working API endpoints, calculation engine for Phase 1 KPIs

---

### Phase 2: Frontend UI (Weeks 3-4)

#### Week 3: Dashboard Components
- ✅ Create KPICard component
- ✅ Create KPITrendChart component
- ✅ Create filter panel
- ✅ Create Level 1 Executive Dashboard
- ✅ Build main dashboard page with level selection

**Deliverable:** Functional Level 1 dashboard with 6 KPIs

#### Week 4: Domain Dashboards
- ✅ Create Sales KPI dashboard (12 metrics)
- ✅ Create Procurement KPI dashboard (10 metrics)
- ✅ Create Inventory KPI dashboard (12 metrics)
- ✅ Create Financial KPI dashboard (10 metrics)
- ✅ Create Workforce KPI dashboard (10 metrics)

**Deliverable:** All Level 2 domain dashboards functional

---

### Phase 3: Advanced Features (Weeks 5-6)

#### Week 5: Drill-Down & Analysis
- ✅ Customer Segmentation drill-down
- ✅ Product Performance analysis
- ✅ Supplier Scorecard
- ✅ Warehouse analysis
- ✅ Real-time operational dashboards (Level 3 & 4)

**Deliverable:** Complete Level 3 & 4 dashboards

#### Week 6: Configuration & Reporting
- ✅ KPI target management page
- ✅ Alert configuration
- ✅ Export functionality (PDF, Excel)
- ✅ Scheduled reports
- ✅ Performance testing & optimization
- ✅ Documentation & user guide

**Deliverable:** Production-ready KPI system

---

## Part 7: Success Metrics & ROI

### 7.1 Implementation Success Metrics

| Metric | Target | Timeline |
|--------|--------|----------|
| **Dashboard Load Time** | < 2 seconds | Phase 2 |
| **KPI Calculation Accuracy** | 100% vs manual | Phase 1 |
| **Alert Generation** | <1 minute latency | Phase 2 |
| **Data Refresh Frequency** | Real-time sales, hourly inventory | Phase 3 |
| **User Adoption Rate** | >70% of management | Month 2 |
| **Dashboard Customization** | 80% of users save filters | Month 2 |

### 7.2 Business Impact Metrics

| Impact Area | Expected Benefit | Measurement |
|------------|------------------|-------------|
| **Decision Speed** | Reduce decision time by 60% | Time to insight vs reports |
| **Financial Performance** | Improve margin by 2-3% | Gross margin tracking |
| **Inventory Optimization** | Reduce carrying cost by 10% | Inventory turnover ratio |
| **DR Collection** | Reduce DSO by 5 days | Days Sales Outstanding trend |
| **Workforce Productivity** | Identify top 20% SRs, improve bottom 20% | SR ROI improvement |
| **Risk Mitigation** | Early warning for cash flow issues | Alerts triggered per month |

### 7.3 User Adoption Plan

- **Week 1:** KPI overview webinar for management
- **Week 2:** Executive dashboard demo & hands-on training
- **Week 3:** Domain dashboard training (sales, procurement, etc.)
- **Week 4:** Advanced features & customization training
- **Ongoing:** Monthly KPI review meetings (use as discuss platform)

---

## Part 8: FAQ & Use Cases

### 8.1 Common Questions

**Q: How frequently are KPIs calculated?**
A: Real-time for transaction-based KPIs (revenue, orders), daily overnight for aggregated KPIs (inventory, margins), weekly for trend analysis.

**Q: Can I customize KPIs for my company?**
A: Yes. Admin section allows creation of custom KPIs with custom calculation formulas.

**Q: What about historical data? Can I see YTD comparison?**
A: Yes. The system stores historical KPI values. You can compare MTD vs LM vs YTD.

**Q: Can I set different targets for different regions/SRs?**
A: Yes. KPI targets are company + kpi + period specific, allowing regional customization.

**Q: What if a KPI calculation fails or takes too long?**
A: Failed calculations trigger alerts. Async calculation jobs with fallback to cached values.

---

## Part 9: Maintenance & Future Enhancements

### 9.1 Ongoing Maintenance
- **Weekly:** Review alert accuracy, adjust thresholds
- **Monthly:** Review KPI relevance vs business strategy
- **Quarterly:** Industry benchmark comparison

### 9.2 Future Enhancements
- **Phase 7:** Predictive analytics (forecast KPIs using ML)
- **Phase 8:** Anomaly detection for outlier KPIs
- **Phase 9:** Mobile KPI app for field teams
- **Phase 10:** AI-powered insights & recommendations
- **Phase 11:** Slack/Teams integration for alerts
- **Phase 12:** Inter-company KPI benchmarking

---

## Conclusion

This comprehensive KPI strategy transforms Shoudagor ERP from a transactional system into a **business intelligence powerhouse**. The 4-level hierarchy ensures both executive visibility and operational depth, while the phased implementation approach minimizes disruption and ensures thorough testing.

**By implementing this KPI system, Shoudagor will achieve:**

1. ✅ Real-time business visibility
2. ✅ Data-driven decision making
3. ✅ Proactive issue identification (alerts)
4. ✅ Performance accountability (individual & team)
5. ✅ Strategic business planning support
6. ✅ Competitive advantage through operational excellence

---

**Document Prepared By:** AI Assistant  
**Last Updated:** April 7, 2026  
**Next Review:** Upon implementation completion  
**Status:** READY FOR IMPLEMENTATION

