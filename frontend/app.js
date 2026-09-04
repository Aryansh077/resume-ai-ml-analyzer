const form = document.getElementById("form");
const resumeInput = document.getElementById("resume");
const jobInput = document.getElementById("job");
const button = document.getElementById("button");
const loading = document.getElementById("loading");
const result = document.getElementById("result");
const errorBox = document.getElementById("error");


// ---------------------------------------------------------
// Helper: safely get an error message
// ---------------------------------------------------------

function getErrorMessage(data) {

    if (!data) {
        return "Something went wrong.";
    }

    // FastAPI normally returns:
    // { "detail": "some message" }

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


// ---------------------------------------------------------
// Show error
// ---------------------------------------------------------

function showError(message) {

    if (!errorBox) {
        alert(message);
        return;
    }

    errorBox.textContent = message;
    errorBox.style.display = "block";
}


// ---------------------------------------------------------
// Hide error
// ---------------------------------------------------------

function hideError() {

    if (errorBox) {
        errorBox.style.display = "none";
        errorBox.textContent = "";
    }
}


// ---------------------------------------------------------
// Hide result
// ---------------------------------------------------------

function hideResult() {

    if (result) {
        result.style.display = "none";
    }
}


// ---------------------------------------------------------
// Show result
// ---------------------------------------------------------

function showResult() {

    if (result) {
        result.style.display = "block";
    }
}


// ---------------------------------------------------------
// Main form
// ---------------------------------------------------------

form.addEventListener("submit", async function (event) {

    event.preventDefault();

    hideError();
    hideResult();


    // -----------------------------------------------------
    // Validate resume
    // -----------------------------------------------------

    if (!resumeInput.files.length) {

        showError(
            "Please upload your resume first."
        );

        return;
    }


    // -----------------------------------------------------
    // Validate job description
    // -----------------------------------------------------

    const jobDescription =
        jobInput.value.trim();


    if (!jobDescription) {

        showError(
            "Please enter a job description."
        );

        return;
    }


    // -----------------------------------------------------
    // UI loading state
    // -----------------------------------------------------

    button.disabled = true;

    if (loading) {
        loading.style.display = "block";
    }


    // -----------------------------------------------------
    // Create form data
    // -----------------------------------------------------

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
            "Sending resume to API..."
        );


        // -------------------------------------------------
        // IMPORTANT
        //
        // We use a relative URL because the frontend
        // and FastAPI backend are hosted together on Render.
        // -------------------------------------------------

        const response = await fetch(
            "/analyze",
            {
                method: "POST",
                body: formData
            }
        );


        console.log(
            "API status:",
            response.status
        );


        // -------------------------------------------------
        // Read response
        // -------------------------------------------------

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
            "API response:",
            data
        );


        // -------------------------------------------------
        // Handle API error
        // -------------------------------------------------

        if (!response.ok) {

            throw new Error(
                getErrorMessage(data)
            );
        }


        // -------------------------------------------------
        // Display score
        // -------------------------------------------------

        const scoreElement =
            document.getElementById("score");

        if (scoreElement) {

            scoreElement.textContent =
                `${data.match_score}%`;
        }


        // -------------------------------------------------
        // Headline
        // -------------------------------------------------

        const headlineElement =
            document.getElementById("headline");

        if (headlineElement) {

            headlineElement.textContent =
                data.headline || "Analysis Complete";
        }


        // -------------------------------------------------
        // Summary
        // -------------------------------------------------

        const summaryElement =
            document.getElementById("summary");

        if (summaryElement) {

            summaryElement.textContent =
                data.summary || "";
        }


        // -------------------------------------------------
        // Matched skills
        // -------------------------------------------------

        const matchedElement =
            document.getElementById("matched");

        if (matchedElement) {

            matchedElement.innerHTML = "";

            const matched =
                data.matched_skills || [];


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


        // -------------------------------------------------
        // Missing skills
        // -------------------------------------------------

        const missingElement =
            document.getElementById("missing");

        if (missingElement) {

            missingElement.innerHTML = "";

            const missing =
                data.missing_skills || [];


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


        // -------------------------------------------------
        // ML probability
        // -------------------------------------------------

        const probabilityElement =
            document.getElementById("prob");

        if (probabilityElement) {

            probabilityElement.textContent =
                `${data.ml_probability ?? 0}%`;
        }


        // -------------------------------------------------
        // Similarity
        // -------------------------------------------------

        const similarityElement =
            document.getElementById("similarity");

        if (similarityElement) {

            similarityElement.textContent =
                `${data.similarity ?? 0}%`;
        }


        // -------------------------------------------------
        // Skill match
        // -------------------------------------------------

        const skillMatchElement =
            document.getElementById("skillmatch");

        if (skillMatchElement) {

            skillMatchElement.textContent =
                `${data.skill_match ?? 0}%`;
        }


        // -------------------------------------------------
        // Show result
        // -------------------------------------------------

        showResult();


    } catch (error) {

        console.error(
            "Analysis error:",
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