const BIO_LABELS = {
  "wc2.1_30s_bio_1_fc": "Annual Mean Temperature",
  "wc2.1_30s_bio_2_fc": "Mean Diurnal Range",
  "wc2.1_30s_bio_3_fc": "Isothermality",
  "wc2.1_30s_bio_4_fc": "Temperature Seasonality",
  "wc2.1_30s_bio_5_fc": "Max Temperature of Warmest Month",
  "wc2.1_30s_bio_6_fc": "Min Temperature of Coldest Month",
  "wc2.1_30s_bio_7_fc": "Temperature Annual Range",
  "wc2.1_30s_bio_8_fc": "Mean Temperature of Wettest Quarter",
  "wc2.1_30s_bio_9_fc": "Mean Temperature of Driest Quarter",
  "wc2.1_30s_bio_10_fc": "Mean Temperature of Warmest Quarter",
  "wc2.1_30s_bio_11_fc": "Mean Temperature of Coldest Quarter",
  "wc2.1_30s_bio_12_fc": "Annual Precipitation",
  "wc2.1_30s_bio_13_fc": "Precipitation of Wettest Month",
  "wc2.1_30s_bio_14_fc": "Precipitation of Driest Month",
  "wc2.1_30s_bio_15_fc": "Precipitation Seasonality",
  "wc2.1_30s_bio_16_fc": "Precipitation of Wettest Quarter",
  "wc2.1_30s_bio_17_fc": "Precipitation of Driest Quarter",
  "wc2.1_30s_bio_18_fc": "Precipitation of Warmest Quarter",
  "wc2.1_30s_bio_19_fc": "Precipitation of Coldest Quarter",
  "wc2.1_30s_bio_20_fc": "Annual Mean UV Index",
};

const state = {
  manifest: window.REPORT_MANIFEST || { reports: [] },
  baselineName: null,
  candidateName: null,
  selectedSpecies: null,
};

const DOM = {
  baselineSelect: document.getElementById("baseline-select"),
  candidateSelect: document.getElementById("candidate-select"),
  sortSelect: document.getElementById("sort-select"),
  metricBanner: document.getElementById("metric-banner"),
  coverageLine: document.getElementById("coverage-line"),
  diffTableBody: document.querySelector("#diff-table tbody"),
  speciesDetailBody: document.getElementById("species-detail-body"),
};

function fmt(value, digits = 3) {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return "-";
  }
  return Number(value).toFixed(digits);
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function getReport(name) {
  return state.manifest.reports.find((report) => report.name === name) || null;
}

function reportMetricLabel(report) {
  return report?.metric?.label || "Test AUC";
}

function topVariable(row, envVars) {
  let bestVar = null;
  let bestValue = -Infinity;
  envVars.forEach((envVar) => {
    const value = Number(row[envVar] || 0);
    if (value > bestValue) {
      bestValue = value;
      bestVar = envVar;
    }
  });
  return { variable: bestVar, value: bestValue };
}

function buildDiffRows(baseline, candidate) {
  const left = new Map(baseline.rows.map((row) => [row.Species, row]));
  const right = new Map(candidate.rows.map((row) => [row.Species, row]));
  const leftSpecies = [...left.keys()].sort();
  const rightSpecies = [...right.keys()].sort();
  const rightSet = new Set(rightSpecies);
  const leftSet = new Set(leftSpecies);
  const overlap = leftSpecies.filter((species) => rightSet.has(species));
  const baselineOnly = leftSpecies.filter((species) => !rightSet.has(species));
  const candidateOnly = rightSpecies.filter((species) => !leftSet.has(species));
  const envVars = Object.keys(baseline.rows[0] || {}).filter((key) => key !== "Species" && key !== "Test AUC");

  const diffRows = overlap.map((species) => {
    const baselineRow = left.get(species);
    const candidateRow = right.get(species);
    const baselineAuc = Number(baselineRow["Test AUC"]);
    const candidateAuc = Number(candidateRow["Test AUC"]);
    const delta = candidateAuc - baselineAuc;
    const contributions = envVars.map((envVar) => ({
      variable: envVar,
      label: BIO_LABELS[envVar] || envVar,
      baseline: Number(baselineRow[envVar] || 0),
      candidate: Number(candidateRow[envVar] || 0),
      delta: Number(candidateRow[envVar] || 0) - Number(baselineRow[envVar] || 0),
    })).sort((a, b) => Math.abs(b.delta) - Math.abs(a.delta));

    return {
      species,
      baselineAuc,
      candidateAuc,
      delta,
      topBaseline: topVariable(baselineRow, envVars),
      topCandidate: topVariable(candidateRow, envVars),
      contributions,
    };
  });

  return { overlap, baselineOnly, candidateOnly, diffRows };
}

function sortDiffRows(rows) {
  const direction = DOM.sortSelect.value;
  const sorted = [...rows];
  sorted.sort((a, b) => direction === "positive" ? b.delta - a.delta : a.delta - b.delta);
  return sorted;
}

function renderBanner(baseline, candidate) {
  if (!baseline || !candidate) {
    DOM.metricBanner.className = "panel banner muted";
    DOM.metricBanner.textContent = "Load the report manifest to begin.";
    return;
  }

  const sameMetric = reportMetricLabel(baseline) === reportMetricLabel(candidate);
  DOM.metricBanner.className = sameMetric ? "panel banner" : "panel banner warning";
  DOM.metricBanner.innerHTML = sameMetric
    ? `Comparing <strong>${escapeHtml(reportMetricLabel(baseline))}</strong> from <code>${escapeHtml(baseline.name)}</code>
       against <strong>${escapeHtml(reportMetricLabel(candidate))}</strong> from <code>${escapeHtml(candidate.name)}</code>.`
    : `Metric mismatch: <code>${escapeHtml(baseline.name)}</code> uses <strong>${escapeHtml(reportMetricLabel(baseline))}</strong>,
       while <code>${escapeHtml(candidate.name)}</code> uses <strong>${escapeHtml(reportMetricLabel(candidate))}</strong>.
       This is still useful for inspection, but it is not a like-for-like metric comparison.`;
}

function renderCoverageLine(baseline, candidate, diff) {
  if (!baseline || !candidate) {
    DOM.coverageLine.textContent = "Waiting for two reports to compare.";
    return;
  }

  const union = diff.overlap.length + diff.baselineOnly.length + diff.candidateOnly.length;
  const overlapPct = union ? (diff.overlap.length / union) * 100 : 0;
  const baselineOnlyPct = union ? (diff.baselineOnly.length / union) * 100 : 0;
  const candidateOnlyPct = union ? (diff.candidateOnly.length / union) * 100 : 0;
  const baselineBetter = diff.diffRows.filter((row) => row.delta < 0).length;
  const candidateBetter = diff.diffRows.filter((row) => row.delta > 0).length;
  const unchanged = diff.diffRows.filter((row) => row.delta === 0).length;

  DOM.coverageLine.innerHTML = `
    <div class="coverage-line">
      <strong>Summary:</strong> ${escapeHtml(baseline.name)} is better in ${baselineBetter} species and
      ${escapeHtml(candidate.name)} is better in ${candidateBetter} species${unchanged ? `, with ${unchanged} unchanged` : ""}.<br>
      <strong>Species overlap:</strong> ${diff.overlap.length}/${union} species (${fmt(overlapPct, 1)}%) |
      <strong>Baseline only:</strong> ${diff.baselineOnly.length} (${fmt(baselineOnlyPct, 1)}%) |
      <strong>Candidate only:</strong> ${diff.candidateOnly.length} (${fmt(candidateOnlyPct, 1)}%)
    </div>
  `;
}

function renderDiffTable(diffRows) {
  DOM.diffTableBody.innerHTML = diffRows.map((row) => `
    <tr data-species="${escapeHtml(row.species)}" class="${row.species === state.selectedSpecies ? "selected" : ""}">
      <td>${escapeHtml(row.species)}</td>
      <td>${fmt(row.delta)}</td>
    </tr>
  `).join("");

  DOM.diffTableBody.querySelectorAll("tr").forEach((tr) => {
    tr.addEventListener("click", () => {
      state.selectedSpecies = tr.dataset.species;
      render();
    });
  });
}

function renderSpeciesDetail(diffRows, baseline, candidate) {
  const selected = diffRows.find((row) => row.species === state.selectedSpecies);
  if (!selected) {
    DOM.speciesDetailBody.className = "muted";
    DOM.speciesDetailBody.textContent = "No species selected.";
    return;
  }

  const rows = [
    {
      label: reportMetricLabel(baseline),
      variable: "AUC",
      delta: selected.delta,
      baseline: selected.baselineAuc,
      candidate: selected.candidateAuc,
    },
    ...selected.contributions.slice(0, 12).map((item) => ({
      label: item.label,
      variable: item.variable,
      delta: item.delta,
      baseline: item.baseline,
      candidate: item.candidate,
    })),
  ];

  const tableMarkup = rows.map((item) => `
    <tr>
      <td>
        <strong>${escapeHtml(item.label)}</strong>
        <div class="raw-var">${escapeHtml(item.variable)}</div>
      </td>
      <td>${fmt(item.delta, item.variable === "AUC" ? 3 : 1)}</td>
      <td>${fmt(item.baseline, item.variable === "AUC" ? 3 : 1)}</td>
      <td>${fmt(item.candidate, item.variable === "AUC" ? 3 : 1)}</td>
    </tr>
  `).join("");

  DOM.speciesDetailBody.className = "";
  DOM.speciesDetailBody.innerHTML = `
    <div class="species-heading">
      <h3>${escapeHtml(selected.species)}</h3>
    </div>
    <div class="detail-block score-line">
      <strong>Top variable</strong>:
      ${escapeHtml(baseline.name)} ${escapeHtml(BIO_LABELS[selected.topBaseline.variable] || selected.topBaseline.variable)} |
      ${escapeHtml(candidate.name)} ${escapeHtml(BIO_LABELS[selected.topCandidate.variable] || selected.topCandidate.variable)}
    </div>
    <div class="detail-block score-line">
      <a class="report-button" href="${encodeURI(`${candidate.path}/model_outputs/${selected.species}.html`)}" target="_blank" rel="noopener noreferrer">
        Maxent report
      </a>
    </div>
    <div class="detail-wrap">
      <table class="detail-table">
        <thead>
          <tr>
            <th>Variable</th>
            <th>Delta</th>
            <th>${escapeHtml(baseline.name)}</th>
            <th>${escapeHtml(candidate.name)}</th>
          </tr>
        </thead>
        <tbody>${tableMarkup}</tbody>
      </table>
    </div>
  `;
}

function populateSelects() {
  const reportNames = state.manifest.reports.map((report) => report.name);
  DOM.baselineSelect.innerHTML = reportNames.map((name) => `<option value="${escapeHtml(name)}">${escapeHtml(name)}</option>`).join("");
  DOM.candidateSelect.innerHTML = reportNames.map((name) => `<option value="${escapeHtml(name)}">${escapeHtml(name)}</option>`).join("");

  if (!state.baselineName && reportNames.length) {
    state.baselineName = reportNames.includes("baseline") ? "baseline" : reportNames[0];
  }
  if (!state.candidateName && reportNames.length) {
    state.candidateName = reportNames[reportNames.length - 1];
  }

  DOM.baselineSelect.value = state.baselineName || "";
  DOM.candidateSelect.value = state.candidateName || "";
}

function render() {
  const baseline = getReport(state.baselineName);
  const candidate = getReport(state.candidateName);
  renderBanner(baseline, candidate);

  if (!baseline || !candidate) {
    DOM.coverageLine.textContent = "Waiting for two reports to compare.";
    DOM.diffTableBody.innerHTML = "";
    DOM.speciesDetailBody.className = "muted";
    DOM.speciesDetailBody.textContent = "No species selected.";
    return;
  }

  const diff = buildDiffRows(baseline, candidate);
  const sortedRows = sortDiffRows(diff.diffRows);
  if (!state.selectedSpecies && sortedRows.length) {
    state.selectedSpecies = sortedRows[0].species;
  }
  if (state.selectedSpecies && !sortedRows.find((row) => row.species === state.selectedSpecies)) {
    state.selectedSpecies = sortedRows[0]?.species || null;
  }

  renderCoverageLine(baseline, candidate, diff);
  renderDiffTable(sortedRows);
  renderSpeciesDetail(sortedRows, baseline, candidate);
}

DOM.baselineSelect.addEventListener("change", (event) => {
  state.baselineName = event.target.value;
  state.selectedSpecies = null;
  render();
});

DOM.candidateSelect.addEventListener("change", (event) => {
  state.candidateName = event.target.value;
  state.selectedSpecies = null;
  render();
});

DOM.sortSelect.addEventListener("change", render);

populateSelects();
render();
