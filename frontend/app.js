const form = document.getElementById("form");
const resumeInput = document.getElementById("resume");
const jobInput = document.getElementById("job");
const button = document.getElementById("button");
const loading = document.getElementById("loading");
const result = document.getElementById("result");
const errorBox = document.getElementById("error");


// =========================================================
// ERROR MESSAGE HELPER
// =========================================================

function getErrorMessage(data) {

    if (!data) {
        return "Something went wrong.";
    }

    // FastAPI error:
    // { "detail": "Some error message" }

    if (typeof data === "string") {
        return data;
    }

    if (data.detail) {

        if (typeof data.detail === "string") {
            return data.detail;
        }

        return JSON.stringify(data.detail);
    }

    if (data.message) {
        return data.message;
    }

    return JSON.stringify(data);
}

function getAnalysisData(data) {

    if (!data || typeof data !== "object") {
        return {};
    }

    if (data.result && typeof data.result === "object") {
        return data.result;
    }

    if (data.analysis && typeof data.analysis === "object") {
        return data.analysis;
    }

    return data;
}

function getDisplayValue(value, fallback = "") {

    if (value === null || value === undefined) {
        return fallback;
    }

    if (typeof value === "object") {
        return value.name || value.label || value.skill || value.text || JSON.stringify(value);
    }

    return String(value);
}

function getSkillNames(skills) {

    if (!Array.isArray(skills)) {
        return [];
    }

    return skills
        .map(function (skill) {
            return getDisplayValue(skill).trim();
        })
        .filter(Boolean);
}


// =========================================================
// SHOW ERROR
// =========================================================

function showError(message) {

    if (errorBox) {

        errorBox.textContent = message;

        errorBox.style.display = "block";

    } else {

        alert(message);

    }
}


// =========================================================
// HIDE ERROR
// =========================================================

function hideError() {

    if (errorBox) {

        errorBox.textContent = "";

        errorBox.style.display = "none";

    }
}


// =========================================================
// HIDE RESULT
// =========================================================

function hideResult() {

    if (result) {

        result.style.display = "none";

    }
}


// =========================================================
// SHOW RESULT
// =========================================================

function showResult() {

    if (result) {

        result.style.display = "block";

    }
}


// =========================================================
// FORM SUBMISSION
// =========================================================

form.addEventListener("submit", async function (event) {

    event.preventDefault();

    console.log("Starting resume analysis...");

    hideError();

    hideResult();


    // =====================================================
    // VALIDATE RESUME
    // =====================================================

    if (!resumeInput.files.length) {

        showError(
            "Please upload your resume first."
        );

        return;
    }


    // =====================================================
    // VALIDATE JOB DESCRIPTION
    // =====================================================

    const jobDescription =
        jobInput.value.trim();


    if (!jobDescription) {

        showError(
            "Please enter a job description."
        );

        return;
    }


    // =====================================================
    // LOADING STATE
    // =====================================================

    button.disabled = true;

    if (loading) {

        loading.style.display = "block";

    }


    // =====================================================
    // CREATE FORM DATA
    // =====================================================

    const formData = new FormData();

    formData.append(
        "resume",
        resumeInput.files[0]
    );

    formData.append(
        "job",
        jobDescription
    );


    try {

        console.log(
            "Sending request to /analyze..."
        );


        // =================================================
        // CALL FASTAPI
        // =================================================

        const response = await fetch(
            "/analyze",
            {
                method: "POST",
                body: formData
            }
        );


        console.log(
            "Server response:",
            response.status
        );


        // =================================================
        // READ RESPONSE
        // =================================================

        const contentType =
            response.headers.get(
                "content-type"
            ) || "";


        let data;


        if (
            contentType.includes(
                "application/json"
            )
        ) {

            data = await response.json();

        } else {

            const text =
                await response.text();

            data = {
                detail: text
            };

        }


        console.log(
            "API data:",
            data
        );


        // =================================================
        // HANDLE ERROR
        // =================================================

        if (!response.ok) {

            throw new Error(
                getErrorMessage(data)
            );

        }

        const analysis = getAnalysisData(data);


        // =================================================
        // SCORE
        // =================================================

        const scoreElement =
            document.getElementById(
                "score"
            );


        if (scoreElement) {

            scoreElement.textContent =
                `${getDisplayValue(analysis.match_score, 0)}%`;

        }


        // =================================================
        // HEADLINE
        // =================================================

        const headlineElement =
            document.getElementById(
                "headline"
            );


        if (headlineElement) {

            headlineElement.textContent =
                getDisplayValue(analysis.headline, "Analysis Complete") ||
                "Analysis Complete";

        }


        // =================================================
        // SUMMARY
        // =================================================

        const summaryElement =
            document.getElementById(
                "summary"
            );


        if (summaryElement) {

            summaryElement.textContent =
                getDisplayValue(analysis.summary);

        }


        // =================================================
        // MATCHED SKILLS
        // =================================================

        const matchedElement =
            document.getElementById(
                "matched"
            );


        if (matchedElement) {

            matchedElement.innerHTML = "";


            const matched = getSkillNames(analysis.matched_skills);


            if (matched.length === 0) {

                matchedElement.innerHTML =
                    "<span>No matching skills detected.</span>";

            } else {

                matched.forEach(
                    function (skill) {

                        const span =
                            document.createElement(
                                "span"
                            );


                        span.className =
                            "skill-tag matched-skill";


                        span.textContent =
                            skill;


                        matchedElement.appendChild(
                            span
                        );

                    }
                );

            }

        }


        // =================================================
        // MISSING SKILLS
        // =================================================

        const missingElement =
            document.getElementById(
                "missing"
            );


        if (missingElement) {

            missingElement.innerHTML = "";


            const missing = getSkillNames(analysis.missing_skills);


            if (missing.length === 0) {

                missingElement.innerHTML =
                    "<span>No major missing skills detected.</span>";

            } else {

                missing.forEach(
                    function (skill) {

                        const span =
                            document.createElement(
                                "span"
                            );


                        span.className =
                            "skill-tag missing-skill";


                        span.textContent =
                            skill;


                        missingElement.appendChild(
                            span
                        );

                    }
                );

            }

        }


        // =================================================
        // ML PROBABILITY
        // =================================================

        const probabilityElement =
            document.getElementById(
                "prob"
            );


        if (probabilityElement) {

            probabilityElement.textContent =
                `${getDisplayValue(analysis.ml_probability, 0)}%`;

        }


        // =================================================
        // TF-IDF SIMILARITY
        // =================================================

        const similarityElement =
            document.getElementById(
                "similarity"
            );


        if (similarityElement) {

            similarityElement.textContent =
                `${getDisplayValue(analysis.similarity, 0)}%`;

        }


        // =================================================
        // SKILL MATCH
        // =================================================

        const skillMatchElement =
            document.getElementById(
                "skillmatch"
            );


        if (skillMatchElement) {

            skillMatchElement.textContent =
                `${getDisplayValue(analysis.skill_match, 0)}%`;

        }


        // =================================================
        // SHOW RESULT
        // =================================================

        showResult();


        console.log(
            "Analysis completed successfully."
        );


    } catch (error) {

        console.error(
            "Analysis failed:",
            error
        );


        showError(
            error.message ||
            "Unable to analyze the resume."
        );


    } finally {

        button.disabled = false;


        if (loading) {

            loading.style.display = "none";

        }

    }

});