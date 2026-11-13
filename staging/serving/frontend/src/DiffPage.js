import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import DiffMap from './DiffMap';
import logo from './logo.png';
import './DiffPage.css';

const initial = { latitude: 12.189703804004086, longitude: 75.94048174979808 };
const displayName = name => name.replace(/_/g, ' ');
const scored = side => side.status === 'scored';
export function comparisonKind(row, threshold, liveAvailable) {
  if (!liveAvailable) return 'unknown';
  const stage = scored(row.staging) && row.staging.score >= threshold;
  const live = scored(row.live) && row.live.score >= threshold;
  return stage && live ? 'both' : stage ? 'staging' : live ? 'live' : 'neither';
}
function Explanation({ row, threshold, liveAvailable }) {
  const kind = comparisonKind(row, threshold, liveAvailable);
  if (!liveAvailable) return <span>Live comparison unavailable. Retry to compare both sides.</span>;
  if (!scored(row.staging)) return <span>{row.staging.reason}</span>;
  if (!scored(row.live)) return <span>{row.live.reason} <span className="diff-caution">Possible cause; live does not expose its exclusion reason.</span></span>;
  if (kind === 'staging' || kind === 'live') return <span>{kind === 'staging' ? 'Live' : 'Staging'} is below the {threshold}% cutoff. The models assign different suitability. <Link to="/model">What changed?</Link></span>;
  return <span>{kind === 'both' ? 'Both meet the cutoff.' : 'Both are below the cutoff.'} <Link to="/model">About the model scores</Link></span>;
}
function Score({ side, threshold, whole = false }) {
  if (!scored(side)) return <span className="diff-no-score">{side.status === 'excluded' ? 'Excluded' : side.status === 'outside_latitude' ? 'Outside range' : side.status === 'nodata' ? 'NoData' : 'No score'}</span>;
  const below = side.score < threshold;
  return <div className={`diff-score ${below ? 'is-below' : 'is-above'}`} title={`${side.score}% - value used for the cutoff`}><strong>{side.score.toFixed(whole ? 0 : 2)}<small>%</small></strong><span>{below ? 'Below cutoff' : 'Meets cutoff'}</span></div>;
}
export default function DiffPage() {
  const [latitude, setLatitude] = useState(String(initial.latitude));
  const [longitude, setLongitude] = useState(String(initial.longitude));
  const [point, setPoint] = useState(initial), [threshold, setThreshold] = useState(50);
  const [data, setData] = useState(null), [loading, setLoading] = useState(false), [error, setError] = useState('');
  const [filter, setFilter] = useState('all'), [search, setSearch] = useState('');
  const controller = useRef(null);
  const compare = useCallback(async location => {
    controller.current?.abort();
    const request = new AbortController(); controller.current = request;
    setLoading(true); setError(''); setPoint(location);
    try {
      const params = new URLSearchParams(location);
      const response = await fetch(`/api/diff?${params}`, { signal: request.signal, cache: 'no-store' });
      const text = await response.text(); let body;
      try { body = JSON.parse(text); } catch { throw new Error('The comparison service did not return a valid response. Please retry.'); }
      if (!response.ok) throw new Error(typeof body.detail === 'string' ? body.detail : 'Enter valid latitude and longitude.');
      if (!Array.isArray(body.rows)) throw new Error('Comparison results are unavailable. Please retry.');
      if (!request.signal.aborted) setData(body);
    } catch (e) { if (e.name !== 'AbortError') setError(e.message); }
    finally { if (!request.signal.aborted) setLoading(false); }
  }, []);
  useEffect(() => () => controller.current?.abort(), []);
  const onMapSelect = useCallback(location => { setLatitude(String(location.latitude)); setLongitude(String(location.longitude)); setPoint(location); }, []);
  const submit = e => {
    e.preventDefault();
    const lat = Number(latitude), lon = Number(longitude);
    if (!latitude.trim() || !longitude.trim() || !Number.isFinite(lat) || !Number.isFinite(lon) || Math.abs(lat) > 90 || Math.abs(lon) > 180) { setError('Enter valid latitude and longitude.'); return; }
    compare({ latitude: lat, longitude: lon });
  };
  const locationChanged = data && (Number(latitude) !== data.query.latitude || Number(longitude) !== data.query.longitude);
  const liveAvailable = data?.live.status === 'available';
  const counts = useMemo(() => {
    const result = { staging: 0, live: 0, both: 0, different: 0, scores: 0 };
    for (const row of data?.rows || []) {
      if (scored(row.staging)) { result.scores++; if (row.staging.score >= threshold) result.staging++; }
      if (scored(row.live)) { if (!scored(row.staging)) result.scores++; if (row.live.score >= threshold) result.live++; }
      const kind = comparisonKind(row, threshold, liveAvailable);
      if (kind === 'both') result.both++; if (kind === 'staging' || kind === 'live') result.different++;
    }
    return result;
  }, [data, threshold, liveAvailable]);
  const rows = useMemo(() => (data?.rows || []).filter(row => {
    if (filter === 'different' && liveAvailable && !['staging', 'live'].includes(comparisonKind(row, threshold, liveAvailable))) return false;
    if ((filter === 'all' || (filter === 'different' && !liveAvailable)) && !scored(row.staging) && !scored(row.live)) return false;
    return displayName(row.species).toLowerCase().includes(search.toLowerCase().replace(/_/g, ' '));
  }).sort((a, b) => {
    const priority = r => { const k = comparisonKind(r, threshold, liveAvailable); return k === 'staging' || k === 'live' ? 0 : k === 'both' ? 1 : 2; };
    return priority(a) - priority(b) || Math.max(b.staging.score ?? -1, b.live.score ?? -1) - Math.max(a.staging.score ?? -1, a.live.score ?? -1) || a.species.localeCompare(b.species);
  }), [data, filter, search, threshold, liveAvailable]);
  return <div className="pw-diff">
    <header className="diff-header"><a href="/" className="diff-brand"><img src={logo} alt="" />PlantWise</a><nav><a href="/">Original site</a><Link to="/model">What changed?</Link></nav></header>
    <main className="diff-main">
      <div className="diff-title"><span className="diff-eyebrow">MODEL COMPARISON</span><h1>Click the map to compare staging with PlantWise India.</h1></div>
      <section className="diff-location"><DiffMap point={point} onSelect={onMapSelect} /><form className="diff-form" onSubmit={submit}>
        <h2>Choose a location</h2><p>Choose a point inside the highlighted Western Ghats area, or enter coordinates. Then select Compare both models.</p>
        <label htmlFor="diff-latitude">Latitude</label><input id="diff-latitude" type="number" step="any" value={latitude} onChange={e => setLatitude(e.target.value)} required />
        <label htmlFor="diff-longitude">Longitude</label><input id="diff-longitude" type="number" step="any" value={longitude} onChange={e => setLongitude(e.target.value)} required />
        <button className="diff-primary" type="submit" disabled={loading}>{loading ? 'Comparing…' : 'Compare both models'}</button>
      </form></section>
      <section className="diff-cutoff"><div><label htmlFor="diff-threshold">Suitability cutoff <strong>{threshold}%</strong></label><p>Both result sets are fetched at 0%. Move the cutoff to highlight recommendations.</p></div><input id="diff-threshold" aria-label="Suitability cutoff" type="range" min="0" max="100" step="1" value={threshold} onChange={e => setThreshold(Number(e.target.value))} /></section>
      {error && <div role="alert" className="diff-error">{error}</div>}
      {loading && <div role="status" className="diff-loading">Reading staging maps and fetching the live results…</div>}
      {data && !loading && !error && <>
        {locationChanged && <p role="status" className="diff-pending">Location changed. Select Compare both models to update results.</p>}
        {!liveAvailable && <div role="alert" className="diff-error">{data.live.error} Staging results are shown; differences are not classified.<button onClick={() => compare(data.query)}>Retry live comparison</button></div>}
        <section className="diff-summary" aria-label="Comparison summary">
          <div><span>Staging</span><strong data-testid="staging-count">{counts.staging}</strong><small>meet the cutoff</small></div>
          <div><span>PlantWise India - live</span><strong data-testid="live-count">{liveAvailable ? counts.live : '-'}</strong><small>{liveAvailable ? 'meet the cutoff' : 'unavailable'}</small></div>
          <div><span>Shared</span><strong data-testid="shared-count">{liveAvailable ? counts.both : '-'}</strong><small>in both lists</small></div>
          <div><span>Different</span><strong data-testid="different-count">{liveAvailable ? counts.different : '-'}</strong><small>in one list only</small></div>
        </section>
        <div className="diff-context"><span>Compared {data.query.latitude}, {data.query.longitude}</span><span>Live fetched {new Date(data.fetched_at).toLocaleTimeString()} - {data.live.score_precision === 'whole_percent' ? 'whole-percent live scores' : 'live-reported score precision'}</span></div>
        <div className="diff-toolbar"><div className="diff-tabs" aria-label="Result view">
          <button className={filter === 'all' ? 'selected' : ''} onClick={() => setFilter('all')}>All scores ({counts.scores})</button>
          <button className={filter === 'different' ? 'selected' : ''} disabled={!liveAvailable} onClick={() => setFilter('different')}>Only differences ({liveAvailable ? counts.different : '-'})</button>
          <button className={filter === 'species' ? 'selected' : ''} onClick={() => setFilter('species')}>Include unavailable species</button>
        </div><input aria-label="Search species" placeholder="Search species…" value={search} onChange={e => setSearch(e.target.value)} /></div>
        <p className="diff-legend"><span className="diff-dot" /> Below-cutoff scores are shaded. “No score” means unavailable, not zero. <Link to="/model">Read how the models differ.</Link></p>
        <div className="diff-table-wrap"><table className="diff-table"><thead><tr><th>Species</th><th>Staging</th><th>PlantWise India <small>Live API</small></th></tr></thead><tbody>
          {rows.map(row => { const kind = comparisonKind(row, threshold, liveAvailable); return <tr key={row.species} data-species={row.species} className={`kind-${kind}`}>
            <th scope="row"><span className="diff-species">{displayName(row.species)}</span>{(kind === 'staging' || kind === 'live') && <span className={`diff-badge badge-${kind}`}>{kind === 'staging' ? 'Staging only' : 'Live only'}</span>}
              <details><summary>Why?</summary><div className="diff-facts"><p><Explanation row={row} threshold={threshold} liveAvailable={liveAvailable} /></p>{row.staging.usable_cells != null && <p>Staging: {row.staging.usable_cells} distinct occurrence cells with valid BIO1-19 values.</p>}{row.staging.latitude_bounds && <p>Observed latitude: {row.staging.latitude_bounds.min} to {row.staging.latitude_bounds.max}.</p>}{row.staging.constant_model && <p>This staging model has no active climate coefficients and gives a constant score.</p>}<p>Staging block-CV AUC: {row.staging.auc != null ? row.staging.auc.toFixed(3) : 'unavailable'}.</p>{row.live.auc != null && <p>Live reported AUC: {row.live.auc}.</p>}</div></details>
            </th><td><Score side={row.staging} threshold={threshold} /></td><td><Score side={row.live} threshold={threshold} whole={data.live.score_precision === 'whole_percent'} /></td>
          </tr>; })}
        </tbody></table>{rows.length === 0 && <p className="diff-empty">No species match this view.</p>}</div>
        <p className="diff-footnote">Staging: {data.staging.release}. Live results come from plantwise-india.org’s API. <Link to="/model">Model differences</Link></p>
      </>}
    </main>
  </div>;
}
