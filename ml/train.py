"""
Train a lightweight Resume-Job Matching ML model.

Model:
    TF-IDF + Logistic Regression

This version intentionally does NOT use Sentence Transformers
or PyTorch so it can run on low-memory cloud instances.
"""

from pathlib import Path
import pandas as pd
import joblib

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_PATH = BASE_DIR / "data" / "dataset.csv"
MODEL_DIR = BASE_DIR / "ml" / "models"
MODEL_PATH = MODEL_DIR / "resume_matcher.joblib"


# ---------------------------------------------------------
# Load dataset
# ---------------------------------------------------------

print("Loading dataset...")

df = pd.read_csv(DATA_PATH)

required_columns = [
    "resume",
    "job_description",
    "label"
]

for column in required_columns:
    if column not in df.columns:
        raise ValueError(
            f"Missing required column: {column}"
        )


df = df.dropna(
    subset=[
        "resume",
        "job_description",
        "label"
    ]
).copy()


# ---------------------------------------------------------
# Prepare training text
# ---------------------------------------------------------

df["resume"] = df["resume"].astype(str)
df["job_description"] = df["job_description"].astype(str)

df["combined_text"] = (
    "RESUME "
    + df["resume"]
    + " JOB "
    + df["job_description"]
)


X_text = df["combined_text"]

y = df["label"].astype(int)


# ---------------------------------------------------------
# TF-IDF
# ---------------------------------------------------------

print("Creating TF-IDF features...")

vectorizer = TfidfVectorizer(
    lowercase=True,
    stop_words="english",
    ngram_range=(1, 2),
    max_features=3000,
    sublinear_tf=True
)

X = vectorizer.fit_transform(X_text)


# ---------------------------------------------------------
# Logistic Regression
# ---------------------------------------------------------

print("Training Logistic Regression...")

model = LogisticRegression(
    max_iter=500,
    class_weight="balanced"
)

model.fit(X, y)


# ---------------------------------------------------------
# Training accuracy
# ---------------------------------------------------------

accuracy = model.score(X, y)

print(
    f"Training accuracy: {accuracy * 100:.2f}%"
)


# ---------------------------------------------------------
# Save model
# ---------------------------------------------------------

MODEL_DIR.mkdir(
    parents=True,
    exist_ok=True
)

artifact = {
    "vectorizer": vectorizer,
    "model": model
}

joblib.dump(
    artifact,
    MODEL_PATH
)


print()
print("Model successfully saved!")
print(f"Location: {MODEL_PATH}")