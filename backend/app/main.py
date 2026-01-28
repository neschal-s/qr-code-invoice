from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.services.embed_qr_pdf import embed_qr_into_pdf


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



app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",   # Vite dev server
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/files", StaticFiles(directory="temp"), name="files")

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

    # 1️⃣ Save uploaded PDF
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # 2️⃣ Extract + parse
    extracted_text = extract_text_from_pdf(str(file_path))
    parsed_data = parse_invoice_fields(extracted_text)

    # 3️⃣ Build QR payload
    qr_payload = build_qr_payload(parsed_data)

    # 4️⃣ Generate QR image
    qr_path = TEMP_DIR / f"{file_id}_qr.png"
    generate_qr_code(qr_payload, str(qr_path))

    # 🔥 5️⃣ EMBED QR INTO PDF (THIS WAS MISSING)
    final_pdf = TEMP_DIR / f"{file_id}_final.pdf"

    embed_qr_into_pdf(
        input_pdf=str(file_path),
        qr_image=str(qr_path),
        output_pdf=str(final_pdf)
    )

    # 6️⃣ Return URLs
    return {
        "message": "Invoice processed and QR generated",
        "file_id": file_id,
        "parsed_data": parsed_data,
        "qr_payload": qr_payload,
        "qr_url": f"http://127.0.0.1:8000/files/{qr_path.name}",
        "pdf_url": f"http://127.0.0.1:8000/files/{final_pdf.name}",
    }