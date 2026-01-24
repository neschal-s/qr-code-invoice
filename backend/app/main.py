from fastapi import FastAPI, UploadFile, File, HTTPException
from pathlib import Path
import uuid
from app.services.extract_text import extract_text_from_pdf
from app.services.parse_invoice import parse_invoice_fields


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

    with open(file_path, "wb") as f:
        f.write(await file.read())

    extracted_text = extract_text_from_pdf(str(file_path))
    parsed_data = parse_invoice_fields(extracted_text)

    return {
        "message": "Invoice processed successfully",
        "file_id": file_id,
        "parsed_data": parsed_data
    }