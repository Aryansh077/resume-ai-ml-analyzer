"""
Lightweight Resume-Job Matcher

Uses:
    TF-IDF
    Logistic Regression
    Rule-based skill matching

No Sentence Transformers.
No PyTorch.
"""

from pathlib import Path
import re
import joblib


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = (
    BASE_DIR
    / "ml"
    / "models"
    / "resume_matcher.joblib"
)


# ---------------------------------------------------------
# Skills
# ---------------------------------------------------------

SKILLS = [
    # Programming
    "python",
    "java",
    "javascript",
    "typescript",
    "c++",
    "c#",

    # Machine Learning
    "machine learning",
    "deep learning",
    "artificial intelligence",
    "data science",
    "nlp",
    "natural language processing",

    # Python ecosystem
    "pandas",
    "numpy",
    "scikit-learn",
    "tensorflow",
    "pytorch",
    "keras",

    # AI / GenAI
    "generative ai",
    "genai",
    "llm",
    "large language models",
    "rag",
    "retrieval augmented generation",
    "embeddings",
    "prompt engineering",

    # Backend
    "fastapi",
    "django",
    "flask",
    "rest api",
    "api",

    # Databases
    "sql",
    "mysql",
    "postgresql",
    "postgres",
    "mongodb",
    "redis",
    "supabase",

    # Cloud
    "aws",
    "azure",
    "gcp",
    "google cloud",

    # DevOps
    "docker",
    "kubernetes",
    "git",
    "github",
    "linux",

    # Data
    "data analysis",
    "data analytics",
    "power bi",
    "tableau",

    # Other
    "statistics",
    "computer vision",
    "opencv",
]


# ---------------------------------------------------------
# Utility
# ---------------------------------------------------------

def normalize_text(text: str) -> str:
    """
    Normalize text for easier matching.
    """

    text = text.lower()

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def extract_skills(text: str) -> list:
    """
    Find known skills inside text.
    """

    text = normalize_text(text)

    found = []

    for skill in SKILLS:

        pattern = r"(?<!\w)" + re.escape(skill) + r"(?!\w)"

        if re.search(pattern, text):
            found.append(skill)

    return sorted(set(found))


# ---------------------------------------------------------
# Matcher
# ---------------------------------------------------------

class ResumeMatcher:

    def __init__(self):

        if not MODEL_PATH.exists():

            raise FileNotFoundError(
                f"ML model not found at {MODEL_PATH}. "
                "Run: python ml/train.py"
            )

        print("Loading lightweight ML model...")

        artifact = joblib.load(MODEL_PATH)

        self.vectorizer = artifact["vectorizer"]

        self.model = artifact["model"]

        print("ML model loaded successfully.")


    # -----------------------------------------------------
    # Analyze
    # -----------------------------------------------------

    def analyze(
        self,
        resume_text: str,
        job_description: str
    ):

        resume_text = normalize_text(
            resume_text
        )

        job_description = normalize_text(
            job_description
        )


        # -------------------------------------------------
        # Skill extraction
        # -------------------------------------------------

        resume_skills = set(
            extract_skills(resume_text)
        )

        job_skills = set(
            extract_skills(job_description)
        )


        matched_skills = sorted(
            resume_skills.intersection(
                job_skills
            )
        )

        missing_skills = sorted(
            job_skills.difference(
                resume_skills
            )
        )


        # -------------------------------------------------
        # Skill match percentage
        # -------------------------------------------------

        if len(job_skills) > 0:

            skill_match = (
                len(matched_skills)
                / len(job_skills)
            )

        else:

            skill_match = 0.0


        # -------------------------------------------------
        # TF-IDF similarity
        # -------------------------------------------------

        resume_vector = self.vectorizer.transform(
            [resume_text]
        )

        job_vector = self.vectorizer.transform(
            [job_description]
        )


        # cosine similarity
        numerator = (
            resume_vector @ job_vector.T
        ).toarray()[0][0]

        resume_norm = (
            resume_vector.multiply(
                resume_vector
            ).sum()
        ) ** 0.5

        job_norm = (
            job_vector.multiply(
                job_vector
            ).sum()
        ) ** 0.5


        if resume_norm > 0 and job_norm > 0:

            similarity = (
                numerator
                / (resume_norm * job_norm)
            )

        else:

            similarity = 0.0


        # -------------------------------------------------
        # ML prediction
        # -------------------------------------------------

        combined_text = (
            "RESUME "
            + resume_text
            + " JOB "
            + job_description
        )


        combined_vector = (
            self.vectorizer.transform(
                [combined_text]
            )
        )


        probability = self.model.predict_proba(
            combined_vector
        )[0]


        # Probability of positive class
        if 1 in self.model.classes_:

            positive_index = list(
                self.model.classes_
            ).index(1)

            ml_probability = float(
                probability[positive_index]
            )

        else:

            ml_probability = 0.0


        # -------------------------------------------------
        # Final score
        # -------------------------------------------------

        final_score = (
            (ml_probability * 0.50)
            + (similarity * 0.25)
            + (skill_match * 0.25)
        )


        final_score = max(
            0.0,
            min(
                1.0,
                final_score
            )
        )


        match_score = round(
            final_score * 100,
            2
        )


        # -------------------------------------------------
        # Headline
        # -------------------------------------------------

        if match_score >= 80:

            headline = "Excellent Match"

        elif match_score >= 65:

            headline = "Strong Match"

        elif match_score >= 50:

            headline = "Moderate Match"

        elif match_score >= 35:

            headline = "Weak Match"

        else:

            headline = "Low Match"


        # -------------------------------------------------
        # Summary
        # -------------------------------------------------

        summary = (
            f"The resume has a {headline.lower()} "
            f"with the provided job description. "
            f"It matches {len(matched_skills)} "
            f"of {len(job_skills)} detected job skills."
        )


        # -------------------------------------------------
        # Return
        # -------------------------------------------------

        return {

            "match_score": match_score,

            "headline": headline,

            "summary": summary,

            "matched_skills": matched_skills,

            "missing_skills": missing_skills,

            "ml_probability": round(
                ml_probability * 100,
                2
            ),

            "similarity": round(
                similarity * 100,
                2
            ),

            "skill_match": round(
                skill_match * 100,
                2
            ),

        }