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
    

    data["po_number"] = extract_po_number(text)
    print("✅ EXTRACTED PO NUMBER:", data["po_number"])


    item_data = extract_quantity_and_rate(text)
    
    data["invoice_part_number"] = item_data["invoice_part_number"]
    data["quantity"] = item_data["quantity"]
    data["basic_rate"] = item_data["basic_rate"]
    data["net_rate"] = item_data["net_rate"]
    data["taxable_value"] = item_data["taxable_value"]
    data["hsn"] = extract_hsn_from_summary(text)


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

def extract_hsn_from_summary(text: str) -> str:
    lines = [l.strip() for l in text.splitlines() if l.strip()]

    summary_started = False

    for line in lines:
        if "HSN/SAC" in line and "Taxable" in line:
            summary_started = True
            continue

        if summary_started:
            match = re.match(r"^(\d{4,8})\s+[\d,]+\.\d{2}", line)
            if match:
                return match.group(1)

    return None



def extract_quantity_and_rate(text: str) -> dict:
    result = {
        "quantity": None,
        "basic_rate": None,
        "net_rate": None,
        "taxable_value": None,
        "invoice_part_number": None
    }

    lines = [l.strip() for l in text.splitlines() if l.strip()]
    UNITS = {"EA", "KG", "NOS", "PCS", "BOX"}

    for i, line in enumerate(lines):
        tokens = line.split()

        unit_positions = [idx for idx, t in enumerate(tokens) if t.upper() in UNITS]
        if len(unit_positions) < 2:
            continue

        try:
            first_unit = unit_positions[0]
            second_unit = unit_positions[1]

            # Quantity = number before first unit
            qty = tokens[first_unit - 1]

            # Rate = number after first unit
            rate = tokens[first_unit + 1]

            # Amount = number after second unit
            amount = tokens[second_unit + 1]

            # Validate numeric sanity
            if not re.match(r"\d+(?:\.\d+)?", qty):
                continue

            result["quantity"] = qty
            result["basic_rate"] = rate
            result["net_rate"] = rate
            result["taxable_value"] = amount

            # Part number usually next line
            if i + 1 < len(lines):
                part_match = re.search(r"\b[A-Z0-9]{8,}\b", lines[i + 1])
                if part_match:
                    result["invoice_part_number"] = part_match.group(0)

            break

        except IndexError:
            continue

    return result
