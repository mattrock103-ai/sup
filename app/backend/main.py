from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from formatter import build_default_template_if_missing, render_cv
from parser import CVParser
from storage import (
    DEFAULT_TEMPLATE_PATH,
    MAX_CV_SIZE,
    MAX_TEMPLATE_SIZE,
    OUTPUTS_DIR,
    TEMPLATE_PATH,
    UPLOADS_DIR,
    ensure_dirs,
    get_template_path,
    template_exists,
)

ALLOWED_TEMPLATE_EXT = {".docx"}
ALLOWED_CV_EXT = {".docx", ".pdf"}

app = FastAPI(title="CV House-Style Formatter", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup() -> None:
    ensure_dirs()
    build_default_template_if_missing(DEFAULT_TEMPLATE_PATH)


@app.post("/api/template/upload")
async def upload_template(file: UploadFile = File(...)):
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_TEMPLATE_EXT:
        raise HTTPException(status_code=400, detail="Template must be a .docx file")

    content = await file.read()
    if len(content) > MAX_TEMPLATE_SIZE:
        raise HTTPException(status_code=400, detail="Template too large (max 10MB)")

    with TEMPLATE_PATH.open("wb") as f:
        f.write(content)

    return {"status": "ok"}


@app.get("/api/template/status")
def template_status():
    return {"exists": template_exists(), "path": str(get_template_path().name)}


@app.post("/api/parse/preview")
async def parse_preview(file: UploadFile = File(...)):
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_CV_EXT:
        raise HTTPException(status_code=400, detail="File must be .docx or .pdf")

    content = await file.read()
    if len(content) > MAX_CV_SIZE:
        raise HTTPException(status_code=400, detail="CV too large (max 12MB)")

    upload_path = UPLOADS_DIR / f"preview_input{suffix}"
    with upload_path.open("wb") as f:
        f.write(content)

    try:
        parsed = CVParser.parse(upload_path, suffix)
    finally:
        if upload_path.exists():
            upload_path.unlink(missing_ok=True)

    return parsed


@app.post("/api/cv/format")
async def format_cv(file: UploadFile = File(...)):
    template_path = get_template_path()
    if not template_path.exists():
        raise HTTPException(status_code=400, detail="No template found. Upload House Style CV first.")

    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_CV_EXT:
        raise HTTPException(status_code=400, detail="CV must be .docx or .pdf")

    content = await file.read()
    if len(content) > MAX_CV_SIZE:
        raise HTTPException(status_code=400, detail="CV too large (max 12MB)")

    safe_input = UPLOADS_DIR / f"cv_input{suffix}"
    with safe_input.open("wb") as f:
        f.write(content)

    try:
        parsed = CVParser.parse(safe_input, suffix)
        output_path = render_cv(template_path, parsed, OUTPUTS_DIR)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Formatting failed: {exc}") from exc
    finally:
        safe_input.unlink(missing_ok=True)

    return FileResponse(
        path=output_path,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename="formatted_cv.docx",
    )


FRONTEND_DIR = Path(__file__).resolve().parents[1] / "frontend"
app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
