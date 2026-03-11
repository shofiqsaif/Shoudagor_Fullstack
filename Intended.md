(1) User can do CRUD operation from UI of Unit (unit of measure), variant group, Product Category, Storage Location

(2) User can add product. Upon invoking 'Add Product', user can create New Product with variant, or can add new variant to existing product.

* **$\rightarrow$** While adding product-variant information is saved such as 'unit, reorder level, safety stock, different price' and importantly Inventory stocks info such as * storage_location, quantity, unit*
* **$\rightarrow$** This create initial 'inventory_stock' at specified location.
* **$\rightarrow$** If *Batch Tracking* is enabled, this initial stock will create a batch with specified price (eg. Purchase price)

(3) User can enable / disable 'Batch Tracking' from settings **$\rightarrow$** Inventory (FE)

(4) User can do CRUD operation related to 'Customer' and 'Supplier'

(5) User can import 'Product' with excel file. It will create Product-variant, assign products to specified category, set reorder level and safety stock, add variants to specified groups, save pricing info, and create initial 'inventory_stock' at specified location at specified quantity.

* **$\rightarrow$** if 'Batch Tracking' is enabled, the 'Product Import' should create batch with specified quantity and with (eg. purchase price)

(6) All operations supports Base UOM and derived UOM. UOM and pricing is converted into base UOM and pricing and calculation and function are done in base UOM. UI is shown in the user’s specified UOM.

7. We can do CRUD operation on Claim & Scheme. Scheme can be generated of type 'Purchase/Sale/Both'.

* **$\rightarrow$** Scheme can be of 'Buy X Get Y', Flat Rebate or percentage Rebate.
* **$\rightarrow$** We add other details of scheme and different slabs.
* **$\rightarrow$** Scheme have start and end date.
* **$\rightarrow$** When doing PO or SO, if a scheme is applicable, apply the best slab. Scheme are also manually override able in UI


### **Stock Transfer Logic**

(Icon: Square/Transfer)

'Stock Transfer' can be done from source location to destination location.

* **$\rightarrow$** we select 'Source Location' and 'Another To Location'
* **$\rightarrow$** Add Transfer Details : Product variant, Unit, Quantity.
* **$\rightarrow$** For each transfer Details, source location's **inventory_stock** decreases, and ' **To Location** ' inventory-stock increases by specified quantity.
* **$\rightarrow$** If ' **Batch Tracking** ' is enabled, source Locations batches will keep allocating / decreasing to fulfill specified quantity.
* **$\rightarrow$** To destination location, **New batches** will create with similar batches consumed from source location.


### **Stock Adjustment**

(Icon: Square/Adjustment)

" **Stock Adjustment** " can be done at specific storage location.

* **$\rightarrow$** Multi Adjustment Details can be added containing: Product, variant, unit, Adjustment quantity, unit cost.
* **$\rightarrow$** At specific location, specified ' **inventory_stock** ' is adjusted by 'adjustment quantity'.
* **$\rightarrow$** If batch tracking is enabled, For positive adjustment, new 'batch' will be created. For negative adjustment, older batches will be consumed until 'adjustment quantity' is satisfied.


### **Purchase Order**

* For PO, we select Location, supplier, other necessary info.
* For PO, Multi PO detail is added. PO detail contain info on product-variant, unit, amount, quantity, unit price, scheme, Received Qty, Free qty, Rec. Qty, Discount.
* PO detail also contain  **Eff. TP** .
* PO Effective Total is added to the balance of supplier.
* We can do Payment and delivery against PO.
* Upon payment against PO, balance of supplier will decrease.
* Upon reject or return against PO, the supplier balance will decrease, taking consideration of  **Effective Trading Price** .
* Upon Taking Delivery against PO, for each delivery against PO, new batch will be generated for specified Product-variant. Also **'inventory_stock'** will increase at PO location.
* Upon Return against PO, **'inventory_stock'** will decrease by qty, and specified qty will be consumed from the batch created by receiving delivery against this PO. Consumption will be from older to new batch.


### **Sale Order (SO)**

* **Header Selection:** For SO, we select **Location** (Warehouse/Store),  **Customer** , and other necessary info (Salesperson, Due Date).
* **SO Details:** Multi SO detail is added. Each detail line contains:
  * Product-variant, unit, quantity, unit price, scheme/promotion, Shipped Qty, Free qty, Tax, and Discount.
* **Effective Pricing:** SO detail contains **Eff. SP** (Effective Sales Price) after all discounts and schemes are applied.
* **Financial Impact:** The SO Effective Total is added to the **balance of the Customer** (Accounts Receivable).
* **Workflow:** We can process **Payment (Receipt)** and **Delivery (Shipment)** against the SO.
* **Customer Balance:** * Upon receiving **Payment** against the SO, the balance of the Customer will  **decrease** .
  * Upon a **Sales Return** against the SO, the Customer balance will  **decrease** , taking into consideration the  **Effective Sales Price** .
* **Inventory Depletion:** * Upon **Delivery** against the SO, **'inventory_stock'** will **decrease** at the SO location for the specified Product-variant.
  * Stock must be **consumed from existing batches** at that location. Following the **FIFO** (First-In, First-Out) method, consumption will move from the  **older batch to the newer batch** .
* **Sales Returns (Stock):** * Upon **Return** against the SO, **'inventory_stock'** will **increase** by the returned quantity.
  * The returned quantity is typically restored to the specific batch it was originally shipped from to maintain accurate tracking.
