import re


def parse_invoice_fields(text: str) -> dict:
    data = {
        "seller_gstin": None,
        "buyer_gstin": None,
        "invoice_no": None,
        "invoice_date": None,
        "total_value": None,
        "hsn": None
    }

    lines = [line.strip() for line in text.splitlines() if line.strip()]

    # ---------- GSTIN ----------
    gstins = re.findall(
        r"\b\d{2}[A-Z]{5}\d{4}[A-Z][A-Z\d]Z[A-Z\d]\b",
        text
    )
    if len(gstins) > 0:
        data["seller_gstin"] = gstins[0]
    if len(gstins) > 1:
        data["buyer_gstin"] = gstins[1]

    # ---------- Invoice No & Date (line-based) ----------
    for i, line in enumerate(lines):
        if line.startswith("Invoice No"):
            if i + 1 < len(lines):
                data["invoice_no"] = lines[i + 1]

        if line.startswith("Dated"):
            if i + 1 < len(lines):
                data["invoice_date"] = lines[i + 1]

    # ---------- Total Value ----------
    for line in lines:
        match = re.search(r"Rs\.\s*([\d,]+\.\d{2})", line)
        if match:
            data["total_value"] = match.group(1)
            break

    # ---------- HSN ----------
    for line in lines:
        match = re.search(r"\b(\d{8})\b", line)
        if match:
            data["hsn"] = match.group(1)
            break

    return data
