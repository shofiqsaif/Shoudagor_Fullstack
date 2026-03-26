from playwright.sync_api import sync_playwright
import time
import random
import string

def generate_random_code(prefix, length=4):
    """Generate random code with prefix and numeric suffix"""
    return f"{prefix}-{''.join(random.choices(string.digits, k=length))}"

def create_product_variant():
    # Generate random names
    product_code = generate_random_code("TP")
    product_name = f"Product-{product_code}"
    variant_sku = generate_random_code("TPV")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        # Login
        print("Logging in...")
        page.goto("http://192.168.1.7:5173/login")
        page.fill('input[placeholder*="admin"]', "admin@complex.com")
        page.fill('input[placeholder*="********"]', "1234")
        page.click('button:has-text("Login")')
        page.wait_for_url("**/dashboard**", timeout=10000)
        time.sleep(2)
        print("Login successful")
        
        # Navigate to product creation
        print("Navigating to product creation page...")
        page.goto("http://192.168.1.7:5173/products/new")
        time.sleep(2)
        
        # Click "Create new product" button in the modal
        print("Clicking 'Create new product' button...")
        page.locator('button:has-text("Create new product")').first.click()
        time.sleep(2)
        
        # STEP 1: Fill product name and code only
        print("Step 1: Filling product name and code...")
        
        # Wait for modal to be visible
        page.wait_for_selector('text="Create a New Product"', timeout=5000)
        time.sleep(1)
        
        # Fill Product Name field
        product_name_input = page.locator('input[placeholder="Product name"]').first
        if product_name_input.is_visible(timeout=3000):
            product_name_input.clear()
            product_name_input.fill(product_name)
            print(f"Product name filled: {product_name}")
            time.sleep(0.3)
        
        # Fill Product Code field - use Tab to move to next field
        page.keyboard.press("Tab")
        time.sleep(0.3)
        product_code_input = page.locator('input[placeholder="Product code"]').first
        if product_code_input.is_visible(timeout=3000):
            product_code_input.clear()
            product_code_input.fill(product_code)
            print(f"Product code filled: {product_code}")
            time.sleep(0.5)
        
        # Click first Continue button (to show additional fields)
        print("Clicking first Continue button...")
        page.locator('button:has-text("Continue")').first.click()
        time.sleep(2)
        
        # STEP 2: Fill additional fields (description, category)
        print("Step 2: Filling additional fields...")
        
        # Fill description (optional, but let's add it)
        try:
            desc_field = page.locator('textarea[placeholder*="description"]').first
            if desc_field.is_visible(timeout=3000):
                desc_field.fill(f"Auto-generated test product {product_code}")
                print("Description filled")
        except Exception as e:
            print(f"Description field not found or not required: {e}")
        
        # Select category (required)
        print("Selecting category...")
        page.locator('input[placeholder*="Select a category"]').first.click()
        time.sleep(1)
        page.locator('[role="option"]').first.click()
        time.sleep(1)
        print("Category selected")
        
        # Click second Continue button (to proceed to variant section)
        print("Clicking second Continue button...")
        page.locator('button:has-text("Continue")').first.click()
        time.sleep(2)
        
        # STEP 3: Add variant
        print("Step 3: Adding variant...")
        page.locator('button:has-text("Add Variant")').first.scroll_into_view_if_needed()
        time.sleep(0.5)
        page.locator('button:has-text("Add Variant")').first.click(force=True)
        time.sleep(2)
        
        # Fill variant details in modal
        print("Filling variant details...")
        
        # SKU is already pre-filled, clear and fill with our variant SKU
        sku_field = page.locator('input[placeholder*="SKU"]').first
        if sku_field.is_visible(timeout=3000):
            sku_field.clear()
            sku_field.fill(variant_sku)
            print(f"SKU filled: {variant_sku}")
        
        # Attribute Name
        attr_name_field = page.locator('input[placeholder*="e.g. Size"]').first
        if attr_name_field.is_visible(timeout=3000):
            attr_name_field.clear()
            attr_name_field.fill("Size")
            print("Attribute Name filled: Size")
        
        # Attribute Value
        attr_value_field = page.locator('input[placeholder*="e.g. Medium"]').first
        if attr_value_field.is_visible(timeout=3000):
            attr_value_field.clear()
            attr_value_field.fill("Medium")
            print("Attribute Value filled: Medium")
        
        # Select unit - should be "Piece"
        print("Selecting unit...")
        # The unit field is a text input with placeholder "Select a unit"
        unit_input = page.locator('input[placeholder="Select a unit"]').first
        if unit_input.is_visible(timeout=3000):
            unit_input.click()
            time.sleep(0.5)
            # Wait for dropdown options to appear
            page.wait_for_selector('[role="option"]', timeout=3000)
            time.sleep(0.3)
            # Find and click "Piece" option
            piece_option = page.locator('[role="option"]:has-text("Piece")').first
            if piece_option.is_visible(timeout=3000):
                piece_option.click()
                print("Unit selected: Piece")
                time.sleep(0.5)
            else:
                # If Piece not found, select first option
                page.locator('[role="option"]').first.click()
                print("Unit selected: First option")
                time.sleep(0.5)
        
        # Reorder Level and Safety Stock
        # These are number inputs that appear after the unit dropdown
        number_inputs = page.locator('input[type="number"]').all()
        
        if len(number_inputs) >= 1:
            # Reorder Level (first number input)
            number_inputs[0].clear()
            number_inputs[0].fill("10")
            print("Reorder Level filled: 10")
            time.sleep(0.3)
        
        if len(number_inputs) >= 2:
            # Safety Stock (second number input)
            number_inputs[1].clear()
            number_inputs[1].fill("5")
            print("Safety Stock filled: 5")
            time.sleep(0.3)
        
        # Pricing Information
        print("Filling pricing information...")
        
        # Get all input fields in the modal and find pricing fields by their position
        # Purchase Price is the first price field after "Pricing Information" section
        price_inputs = page.locator('input[type="number"]').all()
        
        # Find pricing inputs by looking for the ones after reorder/safety stock
        # Typically: Reorder Level (index 0), Safety Stock (index 1), Purchase Price (index 2), etc.
        if len(price_inputs) >= 3:
            # Purchase Price (index 2)
            price_inputs[2].clear()
            price_inputs[2].fill("100")
            print("Purchase Price filled: 100")
            time.sleep(0.3)
        
        if len(price_inputs) >= 4:
            # Selling Price (index 3)
            price_inputs[3].clear()
            price_inputs[3].fill("150")
            print("Selling Price filled: 150")
            time.sleep(0.3)
        
        if len(price_inputs) >= 5:
            # Damage Price (index 4)
            price_inputs[4].clear()
            price_inputs[4].fill("50")
            print("Damage Price filled: 50")
            time.sleep(0.3)
        
        if len(price_inputs) >= 6:
            # Retail Price (index 5)
            price_inputs[5].clear()
            price_inputs[5].fill("160")
            print("Retail Price filled: 160")
            time.sleep(0.3)
        
        # Scroll down to see inventory stocks section
        page.locator('text="Inventory Stocks"').scroll_into_view_if_needed()
        time.sleep(1)
        
        # Fill Stock data
        print("Filling stock data...")
        
        # Wait for inventory stocks section to be visible
        page.wait_for_selector('text="Inventory Stocks"', timeout=3000)
        time.sleep(0.5)
        
        # Select location - it's a text input with placeholder "Select a location"
        # Find all text inputs with this placeholder
        location_inputs = page.locator('input[placeholder="Select a location"]').all()
        if len(location_inputs) > 0:
            # Click the first location input (in Inventory Stocks section)
            location_inputs[0].click()
            time.sleep(0.5)
            # Wait for dropdown options to appear
            page.wait_for_selector('[role="option"]', timeout=3000)
            time.sleep(0.3)
            # Click the first option
            page.locator('[role="option"]').first.click()
            print("Location selected")
            time.sleep(0.5)
        
        # Fill quantity - find the quantity field in Inventory Stocks section
        # Get all number inputs and find the one for quantity (should be after pricing fields)
        all_number_inputs = page.locator('input[type="number"]').all()
        if len(all_number_inputs) > 6:  # After pricing fields
            quantity_field = all_number_inputs[6]
            quantity_field.clear()
            quantity_field.fill("100")
            print("Stock Quantity filled: 100")
            time.sleep(0.3)
        
        # Select unit for inventory - it's a text input with placeholder "Select unit"
        # Find all text inputs with this placeholder
        unit_inputs = page.locator('input[placeholder="Select unit"]').all()
        if len(unit_inputs) > 0:
            # Click the unit input (in Inventory Stocks section)
            unit_inputs[0].click()
            time.sleep(0.5)
            # Wait for dropdown options to appear
            page.wait_for_selector('[role="option"]', timeout=3000)
            time.sleep(0.3)
            # Find and click "Piece" option
            piece_option = page.locator('[role="option"]:has-text("Piece")').first
            if piece_option.is_visible(timeout=3000):
                piece_option.click()
                print("Inventory unit selected: Piece")
                time.sleep(0.5)
            else:
                # If Piece not found, select first option
                page.locator('[role="option"]').first.click()
                print("Inventory unit selected: First option")
                time.sleep(0.5)
        
        time.sleep(1)
        
        # Submit variant (Add Variant button at the bottom of the modal)
        print("Submitting variant...")
        # Scroll to the bottom of the modal to ensure the button is visible
        page.locator('button:has-text("Add Variant")').last.scroll_into_view_if_needed()
        time.sleep(0.5)
        
        # Click the last "Add Variant" button (the submit button in the modal)
        submit_btn = page.locator('button:has-text("Add Variant")').last
        submit_btn.wait_for(state="visible", timeout=5000)
        submit_btn.click()
        print("Variant submitted")
        
        time.sleep(2)
        
        # STEP 4: Submit product form (Create Product button)
        print("Step 4: Creating product...")
        create_button = page.locator('button:has-text("Create Product")').first
        if create_button.is_visible(timeout=3000):
            create_button.click()
            print("Clicked 'Create Product' button")
        else:
            print("Create Product button not found, trying alternative...")
            page.locator('button:has-text("Save"), button[type="submit"]').first.click()
        
        time.sleep(3)
        
        print("\n" + "="*60)
        print("Product created successfully!")
        print(f"  Product Name: {product_name}")
        print(f"  Product Code: {product_code}")
        print(f"  Variant SKU: {variant_sku}")
        print("="*60)
        
        browser.close()

if __name__ == "__main__":
    create_product_variant()
