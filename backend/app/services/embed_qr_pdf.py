import fitz  # PyMuPDF

QR_SIZE = 60  # ≈ 2 cm

def embed_qr_into_pdf(input_pdf: str, qr_image: str, output_pdf: str):
    doc = fitz.open(input_pdf)
    page = doc[0]

    blocks = page.get_text("blocks")

    desc_col_x0 = None
    desc_col_x1 = Nonea
    last_item_y = None
    total_row_y = None

    # 1️⃣ Identify column + anchors
    for b in blocks:
        x0, y0, x1, y1, text = b

        if "Description of Goods" in text:
            desc_col_x0 = x0
            desc_col_x1 = x1

        # Item description lines (product names)
        if any(k in text for k in ["EA", "KG", "BOX"]) and last_item_y is None:
            last_item_y = y1

        # Total row
        if text.strip().startswith("Total"):
            total_row_y = y0

    # Safety fallback
    if desc_col_x0 is None or total_row_y is None:
        doc.save(output_pdf)
        doc.close()
        return

    # 2️⃣ Compute QR position
    available_height = total_row_y - (last_item_y or desc_col_x0)
    qr_y = (last_item_y or total_row_y - QR_SIZE - 20) + (available_height - QR_SIZE) / 2

    qr_x = desc_col_x0 + 10  # left padding inside description column

    rect = fitz.Rect(
        qr_x,
        qr_y,
        qr_x + QR_SIZE,
        qr_y + QR_SIZE
    )

    # 3️⃣ Insert QR
    page.insert_image(rect, filename=qr_image)

    doc.save(output_pdf)
    doc.close()
