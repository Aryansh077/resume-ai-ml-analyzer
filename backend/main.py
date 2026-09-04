from pathlib import Path
import os
import shutil
import tempfile

from fastapi import (
    FastAPI,
    File,
    Form,
    UploadFile,
    HTTPException
)

from fastapi.responses import FileResponse

from fastapi.staticfiles import StaticFiles

from .extractor import extract_text

from .matcher import ResumeMatcher


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

BASE_DIR = Path(
    __file__
).resolve().parent.parent

FRONTEND_DIR = BASE_DIR / "frontend"


# ---------------------------------------------------------
# FastAPI
# ---------------------------------------------------------

app = FastAPI(
    title="Resume AI/ML Analyzer",
    description=(
        "AI/ML Resume and Job Description "
        "Matching System"
    ),
    version="2.0.0"
)


# ---------------------------------------------------------
# Static files
# ---------------------------------------------------------

app.mount(
    "/static",
    StaticFiles(
        directory=str(FRONTEND_DIR)
    ),
    name="static"
)


# ---------------------------------------------------------
# ML Matcher
# ---------------------------------------------------------

matcher = None


@app.on_event("startup")
def load_model():

    global matcher

    matcher = ResumeMatcher()


# ---------------------------------------------------------
# Home
# ---------------------------------------------------------

@app.get("/")
def home():

    return FileResponse(
        FRONTEND_DIR / "index.html"
    )


# ---------------------------------------------------------
# Health check
# ---------------------------------------------------------

@app.get("/health")
def health():

    return {
        "status": "healthy",
        "model_loaded": matcher is not None
    }


# ---------------------------------------------------------
# Analyze resume
# ---------------------------------------------------------

@app.post("/analyze")
async def analyze_resume(
    resume: UploadFile = File(...),
    job: str = Form(...)
):

    if matcher is None:

        raise HTTPException(
            status_code=503,
            detail="ML model is not loaded."
        )


    # -----------------------------------------------------
    # Validate file
    # -----------------------------------------------------

    filename = resume.filename or ""

    extension = (
        Path(filename)
        .suffix
        .lower()
    )


    allowed_extensions = {
        ".pdf",
        ".docx"
    }


    if extension not in allowed_extensions:

        raise HTTPException(
            status_code=400,
            detail=(
                "Only PDF and DOCX files "
                "are supported."
            )
        )


    if not job.strip():

        raise HTTPException(
            status_code=400,
            detail=(
                "Please provide a job description."
            )
        )


    # -----------------------------------------------------
    # Temporary file
    # -----------------------------------------------------

    temp_path = None


    try:

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=extension
        ) as temp_file:

            temp_path = temp_file.name

            shutil.copyfileobj(
                resume.file,
                temp_file
            )


        # -------------------------------------------------
        # Extract resume text
        # -------------------------------------------------

        resume_text = extract_text(
            temp_path
        )


        if not resume_text.strip():

            raise HTTPException(
                status_code=400,
                detail=(
                    "Could not extract text "
                    "from the uploaded resume."
                )
            )


        # -------------------------------------------------
        # Analyze
        # -------------------------------------------------

        result = matcher.analyze(
            resume_text=resume_text,
            job_description=job
        )


        return result


    except HTTPException:

        raise


    except Exception as e:

        print(
            f"Analysis error: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "An error occurred while "
                "analyzing the resume."
            )
        )


    finally:

        # -------------------------------------------------
        # Delete temporary upload
        # -------------------------------------------------

        if temp_path and os.path.exists(
            temp_path
        ):

            try:

                os.remove(
                    temp_path
                )

            except Exception:

                pass