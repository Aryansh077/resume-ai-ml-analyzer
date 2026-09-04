# Resume AI/ML Analyzer

A local AI/ML resume-to-job matching application.

## What it does

1. Upload a PDF/DOCX resume.
2. Extract resume text.
3. Paste a job description.
4. Generate semantic embeddings using a pretrained Sentence Transformer.
5. Calculate semantic similarity and job-related feature scores.
6. Use a trained Logistic Regression model to estimate a match probability.
7. Show matched/missing skills and an analysis report.

The model is designed for **job-related qualification matching**, not hiring decisions. It should not use or infer protected characteristics such as race, religion, sex, age, disability, etc.

## Important ML note

The included training dataset is a small **synthetic educational dataset** so the project runs immediately. It is not a scientifically validated hiring model. Replace it with a properly labeled dataset before making real-world decisions.

## Windows + VS Code setup

Open the project folder in VS Code terminal:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python ml/train.py
uvicorn backend.main:app --reload
```

Open:

http://127.0.0.1:8000

API docs:

http://127.0.0.1:8000/docs

## First test

Paste a job description containing skills such as:

Python, FastAPI, SQL, Docker, AWS, REST API, Git, machine learning

Then upload a relevant PDF/DOCX resume.

## ML pipeline

Raw resume + job description
-> text extraction
-> cleaning
-> skill extraction
-> sentence embeddings
-> cosine similarity
-> engineered features
-> Logistic Regression
-> match probability
-> explanation/report

## Model files

Running `python ml/train.py` creates:

- ml/models/resume_matcher.joblib

The embedding model is downloaded by Sentence Transformers on its first use.

## Improving the model

For a serious project:

- Collect a large, diverse resume/JD pair dataset.
- Have multiple people label match quality using clear criteria.
- Keep a separate test set.
- Measure precision, recall, F1, ROC-AUC and calibration.
- Audit errors and performance across relevant job categories.
- Never train on protected attributes or proxies for them.
