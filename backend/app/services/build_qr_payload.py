from datetime import datetime

def format_date(date_str):
    """
    Converts:
    3-Jan-26  →  03.01.2026
    """
    if not date_str:
        return ""

    try:
        dt = datetime.strptime(date_str, "%d-%b-%y")
        return dt.strftime("%d.%m.%Y")
    except:
        return ""

def normalize_amount(value):
    if value is None:
        return "0.00"
    value = str(value).replace(",", "").strip()
    try:
        return f"{float(value):.2f}"
    except:
        return "0.00"

def build_qr_payload(data: dict) -> str:
    fields = [
        data["po_number"] or "",                      # 1
        data["po_item_no"],                           # 2
        data["quantity"],                             # 3
        data["invoice_no"],                           # 4
        format_date(data["invoice_date"]),            # 5
        normalize_amount(data["basic_rate"]),         # 6
        normalize_amount(data["net_rate"]),           # 7
        data["vendor_internal_code"],                 # 8
        data["invoice_part_number"],                  # 9
        normalize_amount(data["cgst_value"]),         # 10
        normalize_amount(data["sgst_value"]),         # 11
        normalize_amount(data["igst_value"]),         # 12
        normalize_amount(data["ugst"]),               # 13
        normalize_amount(data["cgst_rate"]),          # 14
        normalize_amount(data["sgst_rate"]),          # 15
        normalize_amount(data["igst_rate"]),          # 16
        "0.00",                                       # 17 UGST %
        normalize_amount(data["cess"]),               # 18
        normalize_amount(data["total_value"]),        # 19
        data["hsn"]                                   # 20
    ]

    return ",".join(str(f) for f in fields)
