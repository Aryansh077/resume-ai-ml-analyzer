const form = document.getElementById("form");
const loading = document.getElementById("loading");
const result = document.getElementById("result");
const errorBox = document.getElementById("error");
const button = document.getElementById("button");

function tags(items) {
  if (!items.length) return "<span class='muted'>None detected</span>";
  return items.map(x => `<span class="tag">${x}</span>`).join("");
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  result.classList.add("hidden");
  errorBox.classList.add("hidden");
  loading.classList.remove("hidden");
  button.disabled = true;

  const data = new FormData();
  data.append("resume", document.getElementById("resume").files[0]);
  data.append("job_description", document.getElementById("job").value);

  try {
    const response = await fetch("/analyze", { method: "POST", body: data });
    const json = await response.json();
    if (!response.ok) throw new Error(json.detail || "Analysis failed.");

    document.getElementById("score").textContent = `${json.match_score}%`;
    document.getElementById("headline").textContent =
      json.match_score >= 75 ? "Strong qualification match" :
      json.match_score >= 50 ? "Moderate qualification match" :
      "Low qualification match";

    document.getElementById("summary").textContent =
      `${json.matched_skills.length} relevant skills matched and ${json.missing_skills.length} detected job skills are missing.`;

    document.getElementById("matched").innerHTML = tags(json.matched_skills);
    document.getElementById("missing").innerHTML = tags(json.missing_skills);
    document.getElementById("prob").textContent = `${json.model_probability}%`;
    document.getElementById("similarity").textContent = json.semantic_similarity;
    document.getElementById("skillmatch").textContent = `${json.skill_match_percentage}%`;

    result.classList.remove("hidden");
  } catch (err) {
    errorBox.textContent = err.message;
    errorBox.classList.remove("hidden");
  } finally {
    loading.classList.add("hidden");
    button.disabled = false;
  }
});
