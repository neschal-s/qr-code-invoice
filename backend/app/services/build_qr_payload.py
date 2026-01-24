import re
from datetime import datetime

def normalize_amount(value):
    if value is None or value == "":
        return "0.00"

    value = str(value).replace(",", "").strip()

    try:
        return f"{float(value):.2f}"
    except ValueError:
        return "0.00"

def normalize_text(value):
    if value is None:
        return ""
    return str(value).strip()



def normalize_date(date_str: str) -> str:
    """
    Converts dates like '3-Jan-26' → '03.01.2026'
    """
    dt = datetime.strptime(date_str, "%d-%b-%y")
    return dt.strftime("%d.%m.%Y")


def extract_part_number(description: str) -> str:
    """
    Extracts part number like 8851BQ000028 from description
    """
    match = re.search(r"\b[A-Z0-9]{10,15}\b", description)
    return match.group(0) if match else ""


def build_qr_payload(parsed_data: dict, raw_text: str) -> str:
    lines = [l.strip() for l in raw_text.splitlines() if l.strip()]

    description_block = " ".join(lines)

    part_number = extract_part_number(description_block)

    qr_fields = [
    normalize_text(parsed_data["po_number"]),            # 1
    normalize_text(parsed_data["po_item_no"]),            # 2
    normalize_text(parsed_data["quantity"]),              # 3
    normalize_text(parsed_data["invoice_part_number"]),   # 4
    normalize_text(parsed_data["vendor_internal_code"]),  # 5

    normalize_amount(parsed_data["basic_rate"]),          # 6
    normalize_amount(parsed_data["net_rate"]),            # 7
    normalize_amount(parsed_data["taxable_value"]),       # 8

    normalize_amount(parsed_data["cgst_rate"]),           # 9
    normalize_amount(parsed_data["cgst_value"]),          # 10
    normalize_amount(parsed_data["sgst_rate"]),           # 11
    normalize_amount(parsed_data["sgst_value"]),          # 12
    normalize_amount(parsed_data["igst_rate"]),           # 13
    normalize_amount(parsed_data["igst_value"]),          # 14
    normalize_amount(parsed_data["cess"]),                # 15
    normalize_amount(parsed_data["ugst"]),                # 16

    normalize_text(parsed_data["seller_gstin"]),           # 17
    normalize_text(parsed_data["buyer_gstin"]),           # 18
    normalize_text(parsed_data["invoice_no"]),             # 19
    normalize_text(parsed_data["invoice_date"]),           # 20
    normalize_text(parsed_data["hsn"])                     # 21 (if included)
]


    return ",".join(qr_fields)
