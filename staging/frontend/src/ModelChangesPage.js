import React from 'react';
import { Link } from 'react-router-dom';
import logo from './logo.png';
import './DiffPage.css';

export default function ModelChangesPage() {
  return <div className="pw-diff"><header className="diff-header"><a href="/" className="diff-brand"><img src={logo} alt="" />PlantWise</a><nav><a href="/">Original site</a><Link to="/diff">Compare models</Link></nav></header>
    <main className="diff-main diff-model-page"><h1>Why can the predictions differ?</h1><p className="diff-intro">The same location and cutoff can produce different lists. Some species have no staging model; others have different scores.</p>
      <section><h2>Summary of model differences</h2><p><strong>Staging</strong> reads our newly trained maps. <strong>PlantWise India</strong> is fetched from the live website’s API for the same coordinates. We request both sets at a zero cutoff so lower scores remain visible.</p></section>
      <section><h2>What changed in staging?</h2><div className="diff-table-wrap"><table className="diff-model-table"><thead><tr><th>Part of the process</th><th>What staging does</th><th>What we know about the original</th></tr></thead><tbody>
        <tr><th>Species coverage</th><td>448 input species; 268 fitted models. 180 were excluded for too few usable cells.</td><td>The original source contains 514 species, including 66 not used in staging.</td></tr>
        <tr><th>Climate inputs</th><td>WorldClim BIO1–19, explicitly masked to the Western Ghats polygon.</td><td>BIO1–19 and the boundary match. Original material also includes an unidentified BIO20, which staging deliberately excludes.</td></tr>
        <tr><th>Background locations</th><td>10,000 fixed locations sampled using the supplied collection-effort proxy.</td><td>The archived trainer has no matching effort-background input. Its default workflow would sample background randomly.</td></tr>
        <tr><th>Model settings</th><td>Tests linear and linear/quadratic features with regularization 1 and 2, then selects an eligible model using AICc.</td><td>The archived local command uses Maxent’s automatic feature/default settings.</td></tr>
        <tr><th>Training and checking</th><td>Evaluates four geographic blocks, then serves one selected model fitted to all usable records.</td><td>The archived command uses a random 30% holdout. Its “jackknife” option measures variable importance, rather than doing spatial cross-validation.</td></tr>
        <tr><th>Score scale</th><td>Explicit Maxent cloglog suitability, with no extra API normalization.</td><td>The supplied Maxent jar also defaults to cloglog.</td></tr>
      </tbody></table></div></section>
      <section><h2>Why does a species have no staging score?</h2><p>A usable climate cell is a distinct raster cell containing an occurrence inside the Western Ghats with valid values in all 19 BIO layers. If any layer is missing at that cell, the occurrence is excluded. Repeated occurrences in the same cell count once. Training required at least eight usable cells and two validation points in each geographic block.</p><p>A species has no staging score if it has no fitted model, the query lies outside its observed latitude range, or its prediction pixel is NoData.</p></section>
      <Link className="diff-back" to="/diff">← Back to the comparison</Link>
    </main></div>;
}
