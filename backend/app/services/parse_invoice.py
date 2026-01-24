import re
def extract_po_number(text: str) -> str:
    """
    Extracts PO Number from lines like:
    'Buyer’s Order No. 4500123456 Dated'
    """
    for line in text.splitlines():
        if "Order No" in line or "PO No" in line:
            parts = line.split()
            for part in parts:
                if part.isdigit() and len(part) >= 8:
                    return part
    return ""


def parse_invoice_fields(text: str) -> dict:
    data = {
    # --- HEADER ---
    "seller_gstin": None,
    "buyer_gstin": None,
    "invoice_no": None,
    "invoice_date": None,
    "po_number": None,

    # --- ITEM IDENTIFIERS ---
    "po_item_no": "10",                  # fixed
    "invoice_part_number": None,          # from description
    "vendor_internal_code": "W60120",     # fixed

    # --- QUANTITY & PRICES ---
    "quantity": None,
    "basic_rate": None,
    "net_rate": None,                     # ✅ ADD THIS
    "taxable_value": None,

    # --- TAX RATES ---
    "cgst_rate": None,
    "sgst_rate": None,
    "igst_rate": "0.00",

    # --- TAX AMOUNTS ---
    "cgst_value": None,
    "sgst_value": None,
    "igst_value": "0.00",
    "cess": "0.00",
    "ugst": "0.00",

    # --- CLASSIFICATION ---
    "hsn": None,

    # --- TOTALS ---
    "total_value": None
}




    # ---------- GSTIN ----------
    gstins = re.findall(
        r"\b\d{2}[A-Z]{5}\d{4}[A-Z][A-Z\d]Z[A-Z\d]\b",
        text
    )
    if len(gstins) > 0:
        data["seller_gstin"] = gstins[0]
    if len(gstins) > 1:
        data["buyer_gstin"] = gstins[1]

    # ---------- INVOICE NUMBER ----------
    # Example: WH/25-26/0986
    inv_match = re.search(
        r"\b[A-Z]{1,5}/\d{2}-\d{2}/\d{3,5}\b",
        text
    )
    if inv_match:
        data["invoice_no"] = inv_match.group(0)

    # ---------- INVOICE DATE ----------
    # Example: 3-Jan-26
    date_match = re.search(
        r"\b\d{1,2}-[A-Za-z]{3}-\d{2}\b",
        text
    )
    if date_match:
        data["invoice_date"] = date_match.group(0)

    # ---------- TOTAL VALUE ----------
    total_match = re.search(
        r"Rs\.\s*([\d,]+\.\d{2})",
        text
    )
    if total_match:
        data["total_value"] = total_match.group(1)

    # ---------- HSN ----------
    hsn_match = re.search(r"\b(\d{8})\b", text)
    if hsn_match:
        data["hsn"] = hsn_match.group(1)

    data["po_number"] = extract_po_number(text)

    return data
