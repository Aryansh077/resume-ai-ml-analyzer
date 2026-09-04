from pathlib import Path
import joblib
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "ml" / "models" / "resume_matcher.joblib"

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

class ResumeMatcher:
    def __init__(self):
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                "ML model not found. Run: python ml/train.py"
            )
        self.model = joblib.load(MODEL_PATH)
        self.encoder = SentenceTransformer("all-MiniLM-L6-v2")

    @staticmethod
    def clean(text):
        return " ".join(str(text).lower().split())

    def skills(self, text):
        t = self.clean(text)
        return sorted({s for s in SKILLS if s in t})

    def analyze(self, resume, job):
        r, j = self.clean(resume), self.clean(job)
        resume_skills = set(self.skills(r))
        job_skills = set(self.skills(j))
        matched = sorted(resume_skills & job_skills)
        missing = sorted(job_skills - resume_skills)

        re, je = self.encoder.encode([r]), self.encoder.encode([j])
        similarity = float(cosine_similarity(re, je)[0][0])
        overlap = len(matched) / max(1, len(job_skills))

        features = [[similarity, overlap, len(resume_skills), len(job_skills)]]
        probability = float(self.model.predict_proba(features)[0][1])

        # Blend interpretable signals with the trained classifier.
        semantic_score = max(0.0, min(1.0, (similarity + 1) / 2))
        final_score = round(100 * (0.65 * probability + 0.35 * semantic_score))

        return {
            "match_score": final_score,
            "model_probability": round(probability * 100, 2),
            "semantic_similarity": round(similarity, 4),
            "skill_match_percentage": round(overlap * 100, 2),
            "matched_skills": matched,
            "missing_skills": missing,
            "resume_skills": sorted(resume_skills),
            "job_skills": sorted(job_skills),
        }
