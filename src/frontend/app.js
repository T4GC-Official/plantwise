async function fetchJson(url, options = {}) {
  const response = await fetch(url, options);
  const data = await response.json();
  if (!response.ok) {
    throw data;
  }
  return data;
}

function setFeedback(id, kind, lines) {
  const el = document.getElementById(id);
  el.className = `feedback ${kind}`;
  el.innerHTML = Array.isArray(lines) ? lines.join("<br>") : lines;
}

function buildDatasetFormData() {
  const data = new FormData();
  const species = document.getElementById("species").value.trim();
  data.append("species", species);
  const files = document.getElementById("files").files;
  for (const file of files) {
    data.append("files", file);
  }
  return data;
}

async function validateName() {
  const name = document.getElementById("name").value.trim();
  try {
    const data = await fetchJson("/api/validate/name", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name }),
    });
    if (data.ok) {
      setFeedback("name-feedback", "ok", ["Run name is available."]);
    } else {
      setFeedback("name-feedback", "error", data.errors);
    }
    return data.ok;
  } catch (error) {
    setFeedback("name-feedback", "error", error.errors || ["Name validation failed."]);
    return false;
  }
}

async function validateDataset() {
  try {
    const data = await fetchJson("/api/validate/dataset", {
      method: "POST",
      body: buildDatasetFormData(),
    });
    if (data.ok) {
      const lines = [
        `Uploaded rows: ${data.uploaded_row_count}`,
        `Uploaded rows for species: ${data.uploaded_species_row_count}`,
        `Merged rows for species: ${data.merged_species_row_count}`,
      ];
      setFeedback("dataset-feedback", "ok", lines);
    } else {
      setFeedback("dataset-feedback", "error", data.errors);
    }
    return data.ok;
  } catch (error) {
    setFeedback("dataset-feedback", "error", error.errors || ["Dataset validation failed."]);
    return false;
  }
}

async function validateArgs() {
  const args = document.getElementById("maxent-args").value;
  try {
    const data = await fetchJson("/api/validate/maxent-args", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ args }),
    });
    if (data.ok) {
      setFeedback("args-feedback", "ok", [
        "Merged args:",
        data.merged_args.join(" "),
      ]);
    } else {
      setFeedback("args-feedback", "error", data.errors);
    }
    return data.ok;
  } catch (error) {
    setFeedback("args-feedback", "error", error.errors || ["Arg validation failed."]);
    return false;
  }
}

async function submitRun(event) {
  event.preventDefault();
  const checks = await Promise.all([validateName(), validateDataset(), validateArgs()]);
  if (checks.some((result) => !result)) {
    return;
  }

  const form = document.getElementById("run-form");
  const data = new FormData(form);

  try {
    const response = await fetchJson("/api/runs", {
      method: "POST",
      body: data,
    });
    window.location.href = response.run_url;
  } catch (error) {
    alert((error.errors || ["Run failed to start."]).join("\n"));
  }
}

async function loadConfig() {
  try {
    const data = await fetchJson("/api/config");
    document.getElementById("config-summary").textContent =
      `Seed data: ${data.seed_data} | Run root: ${data.run_root} | Required CSV columns: ${data.required_columns.join(", ")} | Default args: ${data.default_maxent_args.join(" ")}`;
    const argsField = document.getElementById("maxent-args");
    if (!argsField.value.trim()) {
      argsField.value = data.default_maxent_args.join(" ");
    }

    const params = new URLSearchParams(window.location.search);
    const species = params.get("species");
    if (species) {
      document.getElementById("species").value = species;
      const derivedName = `experiment-${species.toLowerCase().replace(/[^a-z0-9]+/g, "-")}`;
      if (!document.getElementById("name").value.trim()) {
        document.getElementById("name").value = derivedName;
      }
    }
  } catch {
    document.getElementById("config-summary").textContent = "Failed to load config.";
  }
}

document.getElementById("validate-name").addEventListener("click", validateName);
document.getElementById("validate-dataset").addEventListener("click", validateDataset);
document.getElementById("validate-args").addEventListener("click", validateArgs);
document.getElementById("run-form").addEventListener("submit", submitRun);

loadConfig();
