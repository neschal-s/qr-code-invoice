import re
def extract_po_number(text: str) -> str:
    lines = [l.strip() for l in text.splitlines() if l.strip()]

    for i, line in enumerate(lines):
        # Anchor line
        if "Buyer" in line and "Order" in line and "No" in line:
            # Look ahead up to 5 lines
            for j in range(i + 1, min(i + 6, len(lines))):
                candidate = lines[j]

                # Skip known noise
                if candidate.startswith("Contact"):
                    continue
                if "Dispatch" in candidate:
                    continue
                if "Dated" in candidate and not any(ch.isdigit() for ch in candidate):
                    continue

                # Case: "5430017659 26-Dec-25"
                parts = candidate.split()
                if parts and parts[0].isdigit() and 8 <= len(parts[0]) <= 12:
                    return parts[0]

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
    hsn_match = re.search(r"\b\d{4,8}\b", line)
    if hsn_match:
        result["hsn"] = hsn_match.group(0)

    data["po_number"] = extract_po_number(text)
    print("✅ EXTRACTED PO NUMBER:", data["po_number"])


    item_data = extract_item_row(text)
    
    data["invoice_part_number"] = item_data["invoice_part_number"]
    data["quantity"] = item_data["quantity"]
    data["basic_rate"] = item_data["basic_rate"]
    data["net_rate"] = item_data["net_rate"]
    data["taxable_value"] = item_data["taxable_value"]
    data["hsn"] = item_data["hsn"]


    # ---------- GST CALCULATION ----------
    try:
        taxable = float(data["taxable_value"].replace(",", ""))

        if data["seller_gstin"] and data["buyer_gstin"]:
            seller_state = data["seller_gstin"][:2]
            buyer_state = data["buyer_gstin"][:2]

            # ✅ Intra-state → CGST + SGST
            if seller_state == buyer_state:
                data["cgst_rate"] = "9.00"
                data["sgst_rate"] = "9.00"

                cgst_val = taxable * 0.09
                sgst_val = taxable * 0.09

                data["cgst_value"] = f"{cgst_val:.2f}"
                data["sgst_value"] = f"{sgst_val:.2f}"

                data["igst_rate"] = "0.00"
                data["igst_value"] = "0.00"

            # ✅ Inter-state → IGST
            else:
                data["igst_rate"] = "18.00"
                igst_val = taxable * 0.18
                data["igst_value"] = f"{igst_val:.2f}"

                data["cgst_rate"] = "0.00"
                data["sgst_rate"] = "0.00"
                data["cgst_value"] = "0.00"
                data["sgst_value"] = "0.00"
    except:
        pass


    return data

def extract_item_row(text: str) -> dict:
    result = {
        "invoice_part_number": None,
        "quantity": None,
        "basic_rate": None,
        "net_rate": None,
        "taxable_value": None,
        "hsn": None
    }

    lines = [l.strip() for l in text.splitlines() if l.strip()]

    for idx, line in enumerate(lines):
        # Anchor: must contain HSN and Amount
        hsn_match = re.search(r"\b\d{4,8}\b", line)
        amount_match = re.search(r"[\d,]+\.\d{2}$", line)

        if not hsn_match or not amount_match:
            continue

        # 🔹 Work ONLY on the right side of HSN
        rhs = line[hsn_match.end():]

        # ✅ Quantity (number + unit)
        qty_match = re.search(
            r"(\d+(?:\.\d+)?)\s*(KG|EA|NOS|PCS|BOX)",
            rhs,
            re.IGNORECASE
        )
        if qty_match:
            result["quantity"] = qty_match.group(1)

        # ✅ Rate (number before unit, AFTER quantity)
        rate_match = re.search(
            r"(KG|EA|NOS|PCS|BOX)\s+(\d+(?:\.\d{2})?)",
            rhs,
            re.IGNORECASE
        )
        if rate_match:
            result["basic_rate"] = rate_match.group(2)
            result["net_rate"] = rate_match.group(2)

        # ✅ Amount (rightmost)
        result["taxable_value"] = amount_match.group(0)

        # ✅ Part number usually in next line
        if idx + 1 < len(lines):
            part_match = re.search(r"\b[A-Z0-9]{8,}\b", lines[idx + 1])
            if part_match:
                result["invoice_part_number"] = part_match.group(0)

        break  # single item invoice

    return result
