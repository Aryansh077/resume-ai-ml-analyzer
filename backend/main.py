from pathlib import Path
import shutil
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .extractor import extract_text
from .matcher import ResumeMatcher

ROOT = Path(__file__).resolve().parents[1]
UPLOADS = ROOT / "uploads"
UPLOADS.mkdir(exist_ok=True)

app = FastAPI(title="Resume AI/ML Analyzer", version="1.0.0")
app.mount("/static", StaticFiles(directory=ROOT / "frontend"), name="static")

matcher = None

@app.on_event("startup")
def startup():
    global matcher
    try:
        matcher = ResumeMatcher()
    except FileNotFoundError:
        matcher = None

@app.get("/")
def home():
    return FileResponse(ROOT / "frontend" / "index.html")

@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": matcher is not None}

@app.post("/analyze")
async def analyze(
    resume: UploadFile = File(...),
    job_description: str = Form(...)
):
    global matcher

    if matcher is None:
        raise HTTPException(
            status_code=500,
            detail="Model not found. Run 'python ml/train.py' first."
        )

    if not resume.filename.lower().endswith((".pdf", ".docx")):
        raise HTTPException(status_code=400, detail="Upload a PDF or DOCX resume.")

    if not job_description.strip():
        raise HTTPException(status_code=400, detail="Job description is required.")

    target = UPLOADS / Path(resume.filename).name
    with target.open("wb") as buffer:
        shutil.copyfileobj(resume.file, buffer)

    try:
        resume_text = extract_text(str(target))
        if len(resume_text.strip()) < 30:
            raise ValueError("Could not extract enough text from the resume.")

        result = matcher.analyze(resume_text, job_description)
        result["resume_filename"] = resume.filename
        return result

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        try:
            target.unlink(missing_ok=True)
        except Exception:
            pass
