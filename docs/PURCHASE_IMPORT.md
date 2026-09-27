# Purchase Import

The Purchases screen supports:

- **+ NEW PRODUCT** beside the product list. Add a product without leaving the purchase screen.
- **IMPORT PURCHASE EXCEL** for bulk purchase entry.
- **PURCHASE TEMPLATE** to create an Excel template.

## Excel columns

Required: `Bill No`, `SKU / Barcode` or `Product Name`, `Qty`, `Unit Cost`.

Optional: `Date`, `Selling Price`, `Supplier`, `Payment Type`, `Paid`, `Category`, `Brand`, `Unit`, `Reorder Level`.

If a product is not already in the product master, the importer creates it from the Excel row. Existing products are matched by SKU/Barcode first, then Product Name.

For a bill with multiple product rows, enter the **Paid** amount only once for that bill (or leave it blank/0 for credit/due). The importer groups rows by Bill No and creates one purchase transaction per bill.

Duplicate Bill/Invoice numbers already in the database are rejected to prevent double posting.
