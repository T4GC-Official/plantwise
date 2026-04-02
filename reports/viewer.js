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

const METADATA_COLUMNS = new Set([
  "Species",
  "Test AUC",
  "training_presence_count",
  "test_presence_count",
  "presence_summary",
]);

const state = {
  manifest: window.REPORT_MANIFEST || { reports: [] },
  baselineId: null,
  candidateId: null,
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

function getReport(id) {
  return state.manifest.reports.find((report) => report.id === id) || null;
}

function reportMetricLabel(report) {
  return report?.metric?.label || "Test AUC";
}

function reportLabel(report) {
  return report?.display_name || report?.name || "report";
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

function presenceSummary(row) {
  return row?.presence_summary || "No data";
}

function reportArgsSummary(report) {
  const commandLine = report?.summary?.maxent_args?.command_line_used;
  return commandLine || "Maxent args unavailable";
}

function presenceLabel(summary) {
  return summary || "No data";
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
  const envVars = Object.keys(baseline.rows[0] || {}).filter((key) => !METADATA_COLUMNS.has(key));

  const overlapRows = overlap.map((species) => {
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
      presence: "both",
      baselineAuc,
      candidateAuc,
      delta,
      topBaseline: topVariable(baselineRow, envVars),
      topCandidate: topVariable(candidateRow, envVars),
      baselinePresenceSummary: presenceSummary(baselineRow),
      candidatePresenceSummary: presenceSummary(candidateRow),
      contributions,
    };
  });

  const baselineOnlyRows = baselineOnly.map((species) => {
    const baselineRow = left.get(species);
    return {
      species,
      presence: "baseline_only",
      baselineAuc: Number(baselineRow["Test AUC"]),
      candidateAuc: null,
      delta: null,
      topBaseline: topVariable(baselineRow, envVars),
      topCandidate: { variable: null, value: null },
      baselinePresenceSummary: presenceSummary(baselineRow),
      candidatePresenceSummary: "No data",
      contributions: envVars.map((envVar) => ({
        variable: envVar,
        label: BIO_LABELS[envVar] || envVar,
        baseline: Number(baselineRow[envVar] || 0),
        candidate: null,
        delta: null,
      })).sort((a, b) => Math.abs((b.baseline ?? 0)) - Math.abs((a.baseline ?? 0))),
    };
  });

  const candidateOnlyRows = candidateOnly.map((species) => {
    const candidateRow = right.get(species);
    return {
      species,
      presence: "candidate_only",
      baselineAuc: null,
      candidateAuc: Number(candidateRow["Test AUC"]),
      delta: null,
      topBaseline: { variable: null, value: null },
      topCandidate: topVariable(candidateRow, envVars),
      baselinePresenceSummary: "No data",
      candidatePresenceSummary: presenceSummary(candidateRow),
      contributions: envVars.map((envVar) => ({
        variable: envVar,
        label: BIO_LABELS[envVar] || envVar,
        baseline: null,
        candidate: Number(candidateRow[envVar] || 0),
        delta: null,
      })).sort((a, b) => Math.abs((b.candidate ?? 0)) - Math.abs((a.candidate ?? 0))),
    };
  });

  return {
    overlap,
    baselineOnly,
    candidateOnly,
    diffRows: [...overlapRows, ...baselineOnlyRows, ...candidateOnlyRows],
  };
}

function sortDiffRows(rows) {
  const direction = DOM.sortSelect.value;
  const sorted = [...rows];
  sorted.sort((a, b) => {
    const aMissing = a.delta === null;
    const bMissing = b.delta === null;
    if (aMissing && bMissing) {
      return a.species.localeCompare(b.species);
    }
    if (aMissing) {
      return 1;
    }
    if (bMissing) {
      return -1;
    }
    return direction === "positive" ? b.delta - a.delta : a.delta - b.delta;
  });
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
    ? `Comparing <strong>${escapeHtml(reportMetricLabel(baseline))}</strong> from <code>${escapeHtml(reportLabel(baseline))}</code>
       against <strong>${escapeHtml(reportMetricLabel(candidate))}</strong> from <code>${escapeHtml(reportLabel(candidate))}</code>.`
    : `Metric mismatch: <code>${escapeHtml(reportLabel(baseline))}</code> uses <strong>${escapeHtml(reportMetricLabel(baseline))}</strong>,
       while <code>${escapeHtml(reportLabel(candidate))}</code> uses <strong>${escapeHtml(reportMetricLabel(candidate))}</strong>.
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
      <strong>Summary:</strong> ${escapeHtml(reportLabel(baseline))} is better in ${baselineBetter} species and
      ${escapeHtml(reportLabel(candidate))} is better in ${candidateBetter} species${unchanged ? `, with ${unchanged} unchanged` : ""}.<br>
      <strong>Species overlap:</strong> ${diff.overlap.length}/${union} species (${fmt(overlapPct, 1)}%) |
      <strong>Baseline only:</strong> ${diff.baselineOnly.length} (${fmt(baselineOnlyPct, 1)}%) |
      <strong>Candidate only:</strong> ${diff.candidateOnly.length} (${fmt(candidateOnlyPct, 1)}%)<br>
      <strong>${escapeHtml(reportLabel(baseline))} args:</strong> ${escapeHtml(reportArgsSummary(baseline))}<br>
      <strong>${escapeHtml(reportLabel(candidate))} args:</strong> ${escapeHtml(reportArgsSummary(candidate))}
    </div>
  `;
}

function renderDiffTable(diffRows) {
  DOM.diffTableBody.innerHTML = diffRows.map((row) => `
    <tr data-species="${escapeHtml(row.species)}" class="${row.species === state.selectedSpecies ? "selected" : ""}">
      <td>${escapeHtml(row.species)}</td>
      <td>${row.delta === null ? "NaN" : fmt(row.delta)}</td>
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
  const reportSource = selected.presence === "baseline_only" ? baseline : candidate;
  const argsSource = selected.presence === "baseline_only" ? baseline : candidate;

  DOM.speciesDetailBody.className = "";
  const presenceNote = selected.presence === "baseline_only"
    ? `<div class="detail-block score-line"><strong>Presence:</strong> Present only in ${escapeHtml(reportLabel(baseline))}.</div>`
    : selected.presence === "candidate_only"
      ? `<div class="detail-block score-line"><strong>Presence:</strong> Present only in ${escapeHtml(reportLabel(candidate))}.</div>`
      : "";
  DOM.speciesDetailBody.innerHTML = `
    <div class="species-heading">
      <h3>${escapeHtml(selected.species)}</h3>
    </div>
    ${presenceNote}
    <div class="detail-block score-line">
      <strong>Presence points</strong>:
      ${escapeHtml(reportLabel(baseline))} ${escapeHtml(presenceLabel(selected.baselinePresenceSummary))} |
      ${escapeHtml(reportLabel(candidate))} ${escapeHtml(presenceLabel(selected.candidatePresenceSummary))}
    </div>
    <div class="detail-block score-line">
      <strong>Top variable</strong>:
      ${escapeHtml(reportLabel(baseline))} ${escapeHtml(BIO_LABELS[selected.topBaseline.variable] || selected.topBaseline.variable || "-")} |
      ${escapeHtml(reportLabel(candidate))} ${escapeHtml(BIO_LABELS[selected.topCandidate.variable] || selected.topCandidate.variable || "-")}
    </div>
    <div class="detail-block score-line">
      <a class="report-button" href="${encodeURI(`/${reportSource.model_outputs_path}/${selected.species}.html`)}" target="_blank" rel="noopener noreferrer">
        Maxent report
      </a>
      <a class="report-button" href="${encodeURI(`/experiments/new?species=${selected.species}`)}">
        Run experiment
      </a>
    </div>
    <div class="detail-wrap">
      <table class="detail-table">
        <thead>
          <tr>
            <th>Variable</th>
            <th>Delta</th>
            <th>${escapeHtml(reportLabel(baseline))}</th>
            <th>${escapeHtml(reportLabel(candidate))}</th>
          </tr>
        </thead>
        <tbody>${tableMarkup}</tbody>
      </table>
    </div>
  `;
}

function populateSelects() {
  const reports = state.manifest.reports;
  DOM.baselineSelect.innerHTML = reports.map((report) => `<option value="${escapeHtml(report.id)}">${escapeHtml(report.display_name || report.name)}</option>`).join("");
  DOM.candidateSelect.innerHTML = reports.map((report) => `<option value="${escapeHtml(report.id)}">${escapeHtml(report.display_name || report.name)}</option>`).join("");

  if (!state.baselineId && reports.length) {
    const baselineReport = reports.find((report) => report.name === "baseline");
    state.baselineId = baselineReport ? baselineReport.id : reports[0].id;
  }
  if (!state.candidateId && reports.length) {
    state.candidateId = reports[reports.length - 1].id;
  }

  DOM.baselineSelect.value = state.baselineId || "";
  DOM.candidateSelect.value = state.candidateId || "";
}

function render() {
  const baseline = getReport(state.baselineId);
  const candidate = getReport(state.candidateId);
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
  state.baselineId = event.target.value;
  state.selectedSpecies = null;
  render();
});

DOM.candidateSelect.addEventListener("change", (event) => {
  state.candidateId = event.target.value;
  state.selectedSpecies = null;
  render();
});

DOM.sortSelect.addEventListener("change", render);

populateSelects();
render();
