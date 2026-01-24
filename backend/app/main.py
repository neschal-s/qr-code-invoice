from fastapi import FastAPI, UploadFile, File, HTTPException
from pathlib import Path
import uuid

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
    # allow only PDF
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    file_id = str(uuid.uuid4())
    file_path = TEMP_DIR / f"{file_id}.pdf"

    with open(file_path, "wb") as f:
        f.write(await file.read())

    return {
        "message": "Invoice uploaded successfully",
        "file_id": file_id,
        "saved_as": file_path.name
    }
