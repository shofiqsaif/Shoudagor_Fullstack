# Claims, SR/SO/DSR, Commission Workflow Fix Plan

**Date:** 2026-03-13

## Overview
This plan addresses functional and logical issues across Claims & Schemes, SR Orders, Sales Orders, DSR flows, and Commission handling. It includes backend and frontend changes, schema adjustments, edge-case handling, and a test plan. The goal is to make scheme application consistent, ensure stock correctness, prevent data drift in DSR operations, and keep commissions accurate through returns and disbursements.

## Scope and Goals
- Persist applied schemes on order details and align evaluation logic across backend and frontend.
- Support buy_x_get_y schemes with different free products via separate free lines.
- Ensure stock validation and DSR load/delivery flows account for free items.
- Fix delivery update/delete handling for free quantities and DSR-loaded orders.
- Ensure commissions are recalculated and adjusted on returns/cancellations with auditability.

## Key Findings Summary
- Auto-evaluated scheme selection is not persisted on SO/PO details.
- Percentage rebate uses full quantity instead of threshold-multiplier logic.
- Claim logs can duplicate on retries; no idempotency guard.
- Overlap validation ignores `applicable_to` and slab validation is weak on update.
- SO stock validation runs before scheme evaluation, missing free quantities.
- DSR assignment/load/delivery/unload ignore free quantities and can drift.
- Delivery update/delete do not handle `delivered_free_quantity` or DSR stock paths.
- DSR collect-payment bypasses SO payment service and customer balance updates.
- SR commission is not adjusted for returns/cancellations; disbursement recalculates differently.

## Assumptions and Decisions
- For buy_x_get_y where free product/variant differs from trigger, create separate free lines.
- For buy_x_get_y where free item matches trigger, keep free quantity on the base line.
- Commission adjustments are automatic for returns/cancellations. If already disbursed, record a negative disbursement.
- Overlap check treats `applicable_to="all"` as overlapping with both purchase and sale schemes, but allows purchase-only and sale-only overlaps.

## Data Model and Schema Changes
1. Sales Order Detail
1. Add `is_free_item: bool` to `sales.sales_order_detail`.
1. Add `parent_detail_id: int | null` to link free lines to the triggering line.
1. Expose these fields in `SalesOrderDetailCreate`, `SalesOrderDetailRead`, and FE schemas.

2. Purchase Order Detail
1. Add `is_free_item: bool` and `parent_detail_id: int | null` to `procurement.purchase_order_detail`.
1. Expose in PO detail schemas and FE types.

3. Claim Log
1. Add `free_product_id` and `free_variant_id` to `inventory.claim_log`.
1. Use these fields to report freebies by their actual product/variant.

4. SR Order Commission
1. Add `commission_amount` to `sales.sr_order` to persist computed commission at Ready time.
1. Use this stored amount for disbursement and adjustments.

## Backend Plan
### A. Claim Evaluation and Logging
1. Update `ClaimService.evaluate_pre_claim` to return a richer result per line with:
1. `applied_scheme_id`
1. `free_quantity`, `discount_amount`
1. `free_product_id`, `free_variant_id`
1. `applied_slab_id`
1. `benefit_type` and `is_free_item_line_needed`
1. Persist `applied_scheme_id` on SO/PO base details when evaluation runs.
1. Fix percentage rebate calculation to use threshold-multiplier logic.
1. Add idempotency guard to `log_claim_applications` by checking existing logs by (ref_id, ref_type, order_detail_id, scheme_id) before insert.
1. Add `applicable_to` awareness to `find_overlapping_schemes`.
1. On scheme update, re-validate slabs and ensure trigger/free product and variant consistency.
1. Enforce that trigger and free variants belong to the selected products.

### B. Sales Order Creation and Update
1. Move scheme evaluation before stock validation in `SalesOrderService.create_sales_order`.
1. For buy_x_get_y with different free product/variant:
1. Create a separate detail line with `is_free_item=true`, `unit_price=0`, `discount_amount=0`, `parent_detail_id` referencing base line.
1. Ensure stock validation includes free lines.
1. Update total_amount calculation to exclude free lines or rely on unit_price=0.
1. Ensure `effective_total_amount` excludes free lines as well.

### C. Purchase Order Creation
1. Apply same scheme evaluation and free-line creation logic in `PurchaseOrderService`.
1. Ensure PO total excludes free lines or relies on unit_price=0.
1. Ensure receiving logic accepts free lines without invoice impact.

### D. DSR Assignment and Load/Unload
1. Include free lines in:
1. DSR assignment stock validation.
1. DSR load operations.
1. DSR unload operations.
1. For free lines, quantity to load should mirror base line scheme free quantity.
1. Ensure batch allocations include free quantities when batch tracking is enabled.

### E. Delivery Create/Update/Delete
1. Update delivery create to enforce delivered_free_quantity <= free_quantity for the detail.
1. Update delivery update and delete to adjust shipped_free quantities and inventory for free items.
1. For DSR-loaded orders, adjust DSR inventory stock when delivered_free_quantity changes.
1. For non-DSR orders, adjust warehouse stock and batch allocations for free quantities.

### F. Returns and Rejections
1. For returns, if the line is `is_free_item=true`:
1. Return affects stock only, not discounts or totals.
1. Claim log adjustment should reference parent line and scheme.
1. Ensure claim adjustment uses returned billable quantity for proportional discount reversal.

### G. Commission Adjustments
1. When SR order is marked Ready:
1. Compute commission and persist to `SR_Order.commission_amount`.
1. Add commission to SR balance once, idempotently.
1. On return or cancellation:
1. Recompute commission delta per SR detail.
1. Reduce SR balance by delta.
1. If already Disbursed, create a negative SRDisbursement to keep audit trail.
1. Ensure disbursement uses stored commission_amount instead of recomputing.

### H. Payment Handling in DSR Collect Flow
1. Replace direct payment updates in `DSRSOAssignmentService.collect_payment` with `SalesOrderPaymentDetailService` usage.
1. Ensure customer balance updates and payment status sync run consistently.

## Frontend Plan
1. Update FE schemas for sales and purchases to include `is_free_item` and `parent_detail_id`.
1. SaleForm and PurchaseForm
1. Display auto-created free lines as read-only.
1. Prevent manual editing of free line unit_price, discount, and quantity.
1. Ensure totals ignore free lines or rely on unit_price=0.
1. Align percent rebate calculation to backend threshold-multiplier logic.
1. Delivery UI
1. Show free lines with separate delivered_free_quantity handling.
1. Prevent over-delivery of free quantities.
1. Returns UI
1. Allow returning free items from free lines.
1. Ensure refund totals ignore free lines.

## Edge Cases to Handle
- Scheme applied with `applied_scheme_id=-1` should preserve manual free/discount inputs.
- Scheme becomes inactive between evaluation and save; preserve manual override values and log warning.
- Returns after commission Disbursed must create negative disbursement entry.
- DSR unload with partial deliveries must not over-return beyond remaining DSR stock.
- Multiple free lines per base line should aggregate correctly in stock validation and DSR load.

## Migration and Data Backfill
1. Add Alembic migrations for new columns in SO/PO details and ClaimLog.
1. Backfill existing SO/PO details:
1. Set `is_free_item=false` for all existing lines.
1. Leave `parent_detail_id` null.
1. For ClaimLog, backfill `free_product_id/free_variant_id` as trigger product/variant if scheme type is buy_x_get_y and no better data exists.

## Test Plan
1. Claims
1. buy_x_get_y with different free product creates separate free line and logs free product correctly.
1. percentage rebate uses threshold multiplier.
1. Duplicate order creation does not duplicate ClaimLogs.

2. Sales Orders
1. Stock validation includes free items.
1. Applied scheme is persisted on detail.
1. Total amount excludes free lines.

3. DSR Flow
1. Assignment/load/unload include free items.
1. Delivery update/delete adjusts DSR inventory for free items.
1. DSR collect-payment updates customer balance and SO status.

4. Commission
1. Ready marks store commission_amount and updates SR balance once.
1. Disbursement uses stored commission_amount.
1. Return after disbursement creates negative disbursement and reduces SR balance.

5. Frontend
1. Free lines shown read-only and not included in totals.
1. Delivery/return forms include free quantities correctly.

## Rollout Steps
1. Apply DB migrations.
1. Deploy backend changes and run targeted API tests.
1. Deploy frontend updates.
1. Monitor claim logs and commission balances for anomalies.

## Files Likely Impacted
- `Shoudagor/app/services/claims/claim_service.py`
- `Shoudagor/app/models/sales.py`
- `Shoudagor/app/models/procurement.py`
- `Shoudagor/app/models/claims.py`
- `Shoudagor/app/services/sales/sales_order_service.py`
- `Shoudagor/app/services/sales/sales_order_delivery_detail_service.py`
- `Shoudagor/app/services/dsr/dsr_so_assignment_service.py`
- `Shoudagor/app/services/sr/sr_order_service.py`
- `shoudagor_FE/src/components/forms/SaleForm.tsx`
- `shoudagor_FE/src/components/forms/PurchaseForm.tsx`
- `shoudagor_FE/src/components/forms/UnifiedDeliveryForm.tsx`
- `shoudagor_FE/src/lib/schema/sales.ts`
- `shoudagor_FE/src/lib/schema/purchases.ts`

## Acceptance Criteria
- Free items are represented correctly in orders and stock flows.
- Scheme application is consistent, persisted, and logged without duplicates.
- DSR stock and deliveries are accurate for both billable and free items.
- Commission balances remain correct through returns, cancellations, and disbursements.
