from pathlib import Path
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "dataset.csv"
MODEL_DIR = ROOT / "ml" / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

SKILLS = [
    "python","java","javascript","typescript","c++","c#","go","rust",
    "react","node.js","django","flask","fastapi","spring boot",
    "sql","postgresql","mysql","mongodb","redis",
    "docker","kubernetes","aws","azure","gcp","terraform",
    "git","github","linux","rest api","graphql",
    "machine learning","deep learning","tensorflow","pytorch",
    "scikit-learn","pandas","numpy","nlp","computer vision",
    "power bi","excel","figma","photoshop","illustrator",
    "html","css","autocad","matlab"
]

def clean(text):
    return " ".join(str(text).lower().split())

def skill_set(text):
    t = clean(text)
    return {s for s in SKILLS if s in t}

def make_features(df, encoder):
    features = []
    for _, row in df.iterrows():
        r, j = clean(row["resume"]), clean(row["job_description"])
        rs, js = skill_set(r), skill_set(j)
        sim = float(cosine_similarity(
            encoder.encode([r]), encoder.encode([j])
        )[0][0])
        overlap = len(rs & js) / max(1, len(js))
        features.append([sim, overlap, len(rs), len(js)])
    return features

def main():
    df = pd.read_csv(DATA)
    encoder = SentenceTransformer("all-MiniLM-L6-v2")
    X = make_features(df, encoder)
    y = df["label"].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    model = Pipeline([
        ("scaler", StandardScaler()),
        ("classifier", LogisticRegression(max_iter=2000, class_weight="balanced"))
    ])
    model.fit(X_train, y_train)

    pred = model.predict(X_test)
    prob = model.predict_proba(X_test)[:, 1]

    print("\n=== Resume Matcher Evaluation ===")
    print(f"Accuracy : {accuracy_score(y_test, pred):.3f}")
    print(f"Precision: {precision_score(y_test, pred, zero_division=0):.3f}")
    print(f"Recall   : {recall_score(y_test, pred, zero_division=0):.3f}")
    print(f"F1       : {f1_score(y_test, pred, zero_division=0):.3f}")
    try:
        print(f"ROC-AUC  : {roc_auc_score(y_test, prob):.3f}")
    except ValueError:
        pass

    joblib.dump(model, MODEL_DIR / "resume_matcher.joblib")
    print(f"\nSaved model to: {MODEL_DIR / 'resume_matcher.joblib'}")

if __name__ == "__main__":
    main()
