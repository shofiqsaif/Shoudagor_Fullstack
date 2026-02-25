/**
 * PostgreSQL script to delete all Products and Variants for a specific Company.
 * Company ID: 15 (Editable)
 */

DO $$
DECLARE
    target_company_id INTEGER := 15; -- <--- CHANGE THIS ID AS NEEDED
BEGIN
    -- STEP 1: DELETE Grandchildren (Tables that depend on detail tables)
    
    -- Delete Delivery Details for Purchase Orders
    DELETE FROM procurement.product_order_delivery_detail
    WHERE purchase_order_detail_id IN (
        SELECT purchase_order_detail_id FROM procurement.purchase_order_detail
        WHERE product_id IN (SELECT product_id FROM inventory.product WHERE company_id = target_company_id)
    );

    -- Delete Delivery Details for Sales Orders
    DELETE FROM sales.sales_order_delivery_detail
    WHERE sales_order_detail_id IN (
        SELECT sales_order_detail_id FROM sales.sales_order_detail
        WHERE product_id IN (SELECT product_id FROM inventory.product WHERE company_id = target_company_id)
    );

    -- STEP 2: DELETE Children (Tables that depend directly on product_id or variant_id)

    -- NEW: Claim and Schemes Dependencies
    -- Claim Logs
    DELETE FROM inventory.claim_log
    WHERE company_id = target_company_id;

    -- Claim Slabs (Cascade from scheme would work if set, but we'll be explicit)
    DELETE FROM inventory.claim_slab
    WHERE scheme_id IN (SELECT scheme_id FROM inventory.claim_scheme WHERE company_id = target_company_id);

    -- Claim Schemes
    DELETE FROM inventory.claim_scheme
    WHERE company_id = target_company_id;

    -- Invoices Details
    DELETE FROM billing.invoice_detail
    WHERE product_id IN (SELECT product_id FROM inventory.product WHERE company_id = target_company_id);

    -- Sales Order Details
    DELETE FROM sales.sales_order_detail
    WHERE product_id IN (SELECT product_id FROM inventory.product WHERE company_id = target_company_id);

    -- SR Order Details
    DELETE FROM sales.sr_order_detail
    WHERE product_id IN (SELECT product_id FROM inventory.product WHERE company_id = target_company_id);

    -- SR Product Assignments
    DELETE FROM sales.sr_product_assignment
    WHERE product_id IN (SELECT product_id FROM inventory.product WHERE company_id = target_company_id);

    -- Purchase Order Details
    DELETE FROM procurement.purchase_order_detail
    WHERE product_id IN (SELECT product_id FROM inventory.product WHERE company_id = target_company_id);

    -- Inventory Adjustment Details
    DELETE FROM transaction.adjustment_detail
    WHERE product_id IN (SELECT product_id FROM inventory.product WHERE company_id = target_company_id);

    -- Inventory Transactions
    DELETE FROM transaction.inventory_transaction
    WHERE product_id IN (SELECT product_id FROM inventory.product WHERE company_id = target_company_id);

    -- Inventory Stock Records
    DELETE FROM warehouse.inventory_stock
    WHERE product_id IN (SELECT product_id FROM inventory.product WHERE company_id = target_company_id);

    -- Stock Transfer Details
    DELETE FROM warehouse.stock_transfer_details
    WHERE product_id IN (SELECT product_id FROM inventory.product WHERE company_id = target_company_id);

    -- Product Pricing History
    DELETE FROM inventory.product_price
    WHERE product_id IN (SELECT product_id FROM inventory.product WHERE company_id = target_company_id);

    -- Product Group Items
    DELETE FROM inventory.product_group_items
    WHERE product_id IN (SELECT product_id FROM inventory.product WHERE company_id = target_company_id);

    -- Variant Group Items
    DELETE FROM inventory.variant_group_items
    WHERE variant_id IN (
        SELECT variant_id FROM inventory.product_variant
        WHERE product_id IN (SELECT product_id FROM inventory.product WHERE company_id = target_company_id)
    );

    -- Product Variant Images
    DELETE FROM inventory.product_variant_image
    WHERE company_id = target_company_id;

    -- STEP 3: DELETE Variants
    DELETE FROM inventory.product_variant
    WHERE product_id IN (SELECT product_id FROM inventory.product WHERE company_id = target_company_id);

    -- STEP 4: DELETE Products
    DELETE FROM inventory.product
    WHERE company_id = target_company_id;

    -- Final Output
    RAISE NOTICE 'Successfully deleted all products and variants for Company ID %', target_company_id;
END $$;
