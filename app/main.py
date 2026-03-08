import json
import uuid
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, HTTPException, UploadFile
from pdf2image import convert_from_bytes
from PIL import Image, UnidentifiedImageError
from paddleocr import PaddleOCR

from .db import Base, SessionLocal, engine
from .models import OCRJob
from .storage import UPLOAD_DIR, PAGE_DIR, RESULT_DIR, TEXT_DIR, ensure_storage_dirs

app = FastAPI(title="ATGDocuTrace", version="1.0.0")

ocr_engine = None


def get_ocr_engine() -> PaddleOCR:
    global ocr_engine
    if ocr_engine is None:
        ocr_engine = PaddleOCR(use_angle_cls=True, lang="en", use_gpu=False)
    return ocr_engine


def serialize_ocr_result(result: Any) -> list:
    return json.loads(json.dumps(result))


def extract_text_from_result(result: list) -> str:
    lines = []
    for page in result:
        if not page:
            continue
        for item in page:
            if not item or len(item) < 2:
                continue
            text_data = item[1]
            if isinstance(text_data, (list, tuple)) and len(text_data) >= 1:
                lines.append(str(text_data[0]))
    return "\n".join(lines)


@app.on_event("startup")
def startup_event() -> None:
    ensure_storage_dirs()
    Base.metadata.create_all(bind=engine)
    get_ocr_engine()


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "ATGDocuTrace"}


@app.get("/jobs")
def list_jobs() -> list[dict]:
    db = SessionLocal()
    try:
        jobs = db.query(OCRJob).order_by(OCRJob.created_at.desc()).all()
        return [
            {
                "job_id": job.job_id,
                "filename": job.original_filename,
                "status": job.status,
                "page_count": job.page_count,
                "created_at": job.created_at.isoformat(),
            }
            for job in jobs
        ]
    finally:
        db.close()


@app.get("/jobs/{job_id}")
def get_job(job_id: str) -> dict:
    db = SessionLocal()
    try:
        job = db.query(OCRJob).filter(OCRJob.job_id == job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        return {
            "job_id": job.job_id,
            "filename": job.original_filename,
            "original_file_path": job.original_file_path,
            "result_json_path": job.result_json_path,
            "text_file_path": job.text_file_path,
            "page_count": job.page_count,
            "status": job.status,
            "created_at": job.created_at.isoformat(),
        }
    finally:
        db.close()


@app.post("/ocr")
async def ocr_upload(file: UploadFile = File(...)) -> dict:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing filename")

    job_id = str(uuid.uuid4())
    suffix = Path(file.filename).suffix.lower()
    file_bytes = await file.read()

    original_path = UPLOAD_DIR / f"{job_id}_{file.filename}"
    original_path.write_bytes(file_bytes)

    ocr = get_ocr_engine()
    all_results = []
    text_outputs = []
    page_count = 0

    try:
        if suffix == ".pdf":
            images = convert_from_bytes(file_bytes)
            for i, img in enumerate(images, start=1):
                page_path = PAGE_DIR / f"{job_id}_page_{i}.png"
                img.save(page_path, format="PNG")

                result = ocr.ocr(str(page_path), cls=True)
                result_data = serialize_ocr_result(result)
                all_results.append({
                    "page": i,
                    "page_image": str(page_path),
                    "ocr": result_data,
                })
                text_outputs.append(extract_text_from_result(result_data))
                page_count += 1
        else:
            try:
                img = Image.open(original_path)
                img.verify()
            except UnidentifiedImageError:
                raise HTTPException(status_code=400, detail="Only PDF or image files are supported")

            img = Image.open(original_path).convert("RGB")
            image_path = PAGE_DIR / f"{job_id}_image.png"
            img.save(image_path, format="PNG")

            result = ocr.ocr(str(image_path), cls=True)
            result_data = serialize_ocr_result(result)
            all_results.append({
                "page": 1,
                "page_image": str(image_path),
                "ocr": result_data,
            })
            text_outputs.append(extract_text_from_result(result_data))
            page_count = 1

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"OCR processing failed: {exc}") from exc

    json_path = RESULT_DIR / f"{job_id}.json"
    text_path = TEXT_DIR / f"{job_id}.txt"

    json_path.write_text(json.dumps(all_results, indent=2), encoding="utf-8")
    text_path.write_text("\n\n".join(text_outputs), encoding="utf-8")

    db = SessionLocal()
    try:
        db_job = OCRJob(
            job_id=job_id,
            original_filename=file.filename,
            original_file_path=str(original_path),
            result_json_path=str(json_path),
            text_file_path=str(text_path),
            page_count=page_count,
            status="completed",
        )
        db.add(db_job)
        db.commit()
    finally:
        db.close()

    return {
        "job_id": job_id,
        "status": "completed",
        "filename": file.filename,
        "page_count": page_count,
        "original_file_path": str(original_path),
        "result_json_path": str(json_path),
        "text_file_path": str(text_path),
    }
