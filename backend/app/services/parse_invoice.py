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

    return data
