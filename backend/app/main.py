from fastapi import FastAPI, UploadFile, File, HTTPException
from pathlib import Path
import uuid

from app.services.extract_text import extract_text_from_pdf
from app.services.parse_invoice import parse_invoice_fields
from app.services.generate_qr import generate_qr_code
from app.services.build_qr_payload import build_qr_payload



app = FastAPI(
    title="Invoice QR Generator",
    description="Upload Tally invoice PDF and get QR embedded PDF",
    version="1.0.0"
)

# temp folder for uploads
TEMP_DIR = Path("temp")
TEMP_DIR.mkdir(exist_ok=True)


@app.get("/")
def health_check():
    return {"status": "Backend is running"}


@app.post("/upload-invoice")
async def upload_invoice(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    file_id = str(uuid.uuid4())
    file_path = TEMP_DIR / f"{file_id}.pdf"

    # save uploaded PDF
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # extract + parse
    extracted_text = extract_text_from_pdf(str(file_path))
    parsed_data = parse_invoice_fields(extracted_text)

    # debug helper lines
    lines = [line.strip() for line in extracted_text.splitlines() if line.strip()]
    debug_lines = [
        line for line in lines
        if "Invoice" in line or "Dated" in line
    ]

    # build QR payload
    qr_payload = build_qr_payload(parsed_data)



    # generate QR
    qr_path = TEMP_DIR / f"{file_id}_qr.png"
    generate_qr_code(qr_payload, str(qr_path))

    return {
        "message": "Invoice processed and QR generated",
        "file_id": file_id,
        "parsed_data": parsed_data,
        "qr_payload": qr_payload,
        "qr_file": qr_path.name,
        "debug_lines": debug_lines
    }
