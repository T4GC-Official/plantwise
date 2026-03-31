import argparse
import csv
import hashlib
import json
import re
import shutil
from datetime import datetime
from pathlib import Path

import pandas as pd
from bs4 import BeautifulSoup


TIMING_PREP_RE = re.compile(r"Preparing to process (\d+) species files")
TIMING_FINISH_RE = re.compile(r"^\[(\d+)/(\d+)\] Finished (.+?) in ([0-9.]+)s$")
TIMING_SKIP_RE = re.compile(r"^Skipping (.+?): insufficient presence points$")
TIMING_RETRY_RE = re.compile(r"^Leaving (.+?) in sp_data_final for retry after failure$")
TEST_AUC_RE = re.compile(r"Test AUC is ([0-9.]+)", re.IGNORECASE)
TRAINING_AUC_RE = re.compile(r"training AUC is ([0-9.]+)", re.IGNORECASE)
VERSION_RE = re.compile(r"using Maxent version ([0-9.]+)", re.IGNORECASE)
BIO_VAR_RE = re.compile(r"^wc2\.1_30s_bio_(\d+)_fc$")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate a report bundle from PlantWise_v0 run artifacts."
    )
    parser.add_argument(
        "--root",
        default=".",
        help="PlantWise_v0 root directory. Default: current directory",
    )
    parser.add_argument(
        "--name",
        default=None,
        help="Report directory name under reports/. Default: timestamp",
    )
    return parser.parse_args()


def get_run_identity(root: Path):
    candidates = []
    for relative in [
        Path("logs") / "maxent_timing.txt",
        Path("logs") / "maxent_usage.csv",
    ]:
        path = root / relative
        if path.exists():
            stat = path.stat()
            candidates.append(
                {
                    "path": str(relative),
                    "size": stat.st_size,
                    "mtime_ns": stat.st_mtime_ns,
                }
            )

    html_paths = sorted((root / "res").glob("*.html"))
    if html_paths:
        mtimes = [path.stat().st_mtime_ns for path in html_paths]
        candidates.append(
            {
                "path": "res/*.html",
                "count": len(html_paths),
                "oldest_mtime_ns": min(mtimes),
                "newest_mtime_ns": max(mtimes),
            }
        )

    if not candidates:
        anchor_dt = datetime.now()
        payload = {"sources": [], "anchor": anchor_dt.isoformat()}
    else:
        timing_path = root / "logs" / "maxent_timing.txt"
        if timing_path.exists():
            anchor_dt = datetime.fromtimestamp(timing_path.stat().st_mtime)
        else:
            oldest_candidates = [item["oldest_mtime_ns"] for item in candidates if "oldest_mtime_ns" in item]
            if oldest_candidates:
                anchor_dt = datetime.fromtimestamp(min(oldest_candidates) / 1_000_000_000)
            else:
                anchor_dt = datetime.fromtimestamp(min(item["mtime_ns"] for item in candidates) / 1_000_000_000)
        payload = {"sources": candidates, "anchor": anchor_dt.isoformat()}

    signature = hashlib.sha1(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()[:12]
    return {
        "signature": signature,
        "anchor_timestamp": anchor_dt.strftime("%Y%m%d_%H%M%S"),
        "metadata": payload,
    }


def make_report_dir(root: Path, name: str | None, run_identity: dict) -> Path:
    reports_dir = root / "reports"
    reports_dir.mkdir(exist_ok=True)
    if name is None:
        for existing_dir in sorted([path for path in reports_dir.iterdir() if path.is_dir()], key=lambda path: path.name):
            summary_path = existing_dir / "report_summary.json"
            if not summary_path.exists():
                continue
            try:
                summary = json.loads(summary_path.read_text())
            except json.JSONDecodeError:
                continue
            if summary.get("run_signature") == run_identity["signature"]:
                return existing_dir
        name = run_identity["anchor_timestamp"]
    report_dir = reports_dir / name
    report_dir.mkdir(parents=True, exist_ok=True)
    return report_dir


def extract_metric_from_html(html_path: Path):
    html = html_path.read_text(errors="ignore")
    soup = BeautifulSoup(html, "html.parser")
    version_match = VERSION_RE.search(html)
    test_auc_match = TEST_AUC_RE.search(html)
    training_auc_match = TRAINING_AUC_RE.search(html)

    contributions = {}
    tables = soup.find_all("table")
    if len(tables) > 1:
        for row in tables[1].find_all("tr")[1:]:
            cells = [cell.get_text(" ", strip=True) for cell in row.find_all("td")]
            if len(cells) >= 2:
                try:
                    contributions[cells[0]] = float(cells[1])
                except ValueError:
                    continue

    return {
        "species": html_path.stem,
        "test_auc": float(test_auc_match.group(1)) if test_auc_match else None,
        "training_auc": float(training_auc_match.group(1)) if training_auc_match else None,
        "contributions": contributions,
        "maxent_version": version_match.group(1).rstrip(".") if version_match else None,
        "source": str(html_path.relative_to(html_path.parent.parent)),
    }


def ordered_env_vars(env_vars):
    def key(name):
        match = BIO_VAR_RE.match(name)
        if match:
            return (0, int(match.group(1)))
        return (1, name)

    return sorted(env_vars, key=key)


def build_auc_from_maxent_results(root: Path):
    return build_auc_from_maxent_results_dir(root / "res", root)


def build_auc_from_maxent_results_dir(res_dir: Path, root: Path):
    results_path = res_dir / "maxentResults.csv"
    if not results_path.exists():
        return None

    df = pd.read_csv(results_path)
    contribution_columns = [
        col for col in df.columns if col.endswith(" contribution")
    ]

    rows = []
    for _, row in df.iterrows():
        out = {
            "Species": row["Species"],
            "Test AUC": row["Training AUC"],
        }
        for col in contribution_columns:
            out[col.replace(" contribution", "")] = row[col]
        rows.append(out)

    out_df = pd.DataFrame(rows)
    ordered_cols = ["Species", "Test AUC"] + ordered_env_vars(
        [col for col in out_df.columns if col not in {"Species", "Test AUC"}]
    )
    out_df = out_df[ordered_cols].sort_values("Species").reset_index(drop=True)
    return out_df, {
        "auc_source": "Training AUC from res/maxentResults.csv mapped into compatibility column 'Test AUC'",
        "maxent_results_path": str(results_path.relative_to(root)),
        "species_count": len(out_df),
    }


def build_auc_from_html(root: Path):
    return build_auc_from_html_dir(root / "res", root)


def build_auc_from_html_dir(res_dir: Path, root: Path):
    html_paths = sorted(res_dir.glob("*.html"))
    metrics = [extract_metric_from_html(path) for path in html_paths]
    env_vars = ordered_env_vars(
        {
            var
            for item in metrics
            for var in item["contributions"].keys()
        }
    )

    rows = []
    versions = set()
    has_test_auc = any(item["test_auc"] is not None for item in metrics)
    for item in metrics:
        if item["maxent_version"]:
            versions.add(item["maxent_version"])
        row = {
            "Species": item["species"],
            "Test AUC": item["test_auc"] if item["test_auc"] is not None else item["training_auc"],
        }
        for env_var in env_vars:
            row[env_var] = item["contributions"].get(env_var, 0.0)
        rows.append(row)

    out_df = pd.DataFrame(rows)
    ordered_cols = ["Species", "Test AUC"] + env_vars
    out_df = out_df[ordered_cols].sort_values("Species").reset_index(drop=True)
    return out_df, {
        "auc_source": (
            "Test AUC parsed from per-species HTML"
            if has_test_auc
            else "Training AUC parsed from per-species HTML mapped into compatibility column 'Test AUC'"
        ),
        "html_report_count": len(html_paths),
        "maxent_versions_seen": sorted(versions),
        "species_count": len(out_df),
    }


def parse_timing_log(path: Path):
    if not path.exists():
        return {"present": False}

    prepared_total = None
    finished = []
    skipped = []
    retry_after_failure = []

    for raw_line in path.read_text(errors="ignore").splitlines():
        line = raw_line.strip()
        if not line:
            continue

        prepared_match = TIMING_PREP_RE.search(line)
        if prepared_match:
            prepared_total = int(prepared_match.group(1))
            continue

        finish_match = TIMING_FINISH_RE.match(line)
        if finish_match:
            finished.append(
                {
                    "index": int(finish_match.group(1)),
                    "total": int(finish_match.group(2)),
                    "species_file": finish_match.group(3),
                    "seconds": float(finish_match.group(4)),
                }
            )
            continue

        skip_match = TIMING_SKIP_RE.match(line)
        if skip_match:
            skipped.append(skip_match.group(1))
            continue

        retry_match = TIMING_RETRY_RE.match(line)
        if retry_match:
            retry_after_failure.append(retry_match.group(1))

    seconds = [item["seconds"] for item in finished]
    return {
        "present": True,
        "path": str(path),
        "prepared_total": prepared_total,
        "finished_count": len(finished),
        "avg_seconds": round(sum(seconds) / len(seconds), 3) if seconds else None,
        "max_seconds": max(seconds) if seconds else None,
        "min_seconds": min(seconds) if seconds else None,
        "skipped_insufficient_presence_count": len(skipped),
        "skipped_insufficient_presence_species": skipped,
        "retry_after_failure_count": len(retry_after_failure),
        "retry_after_failure_species": retry_after_failure,
    }


def parse_usage_log(path: Path):
    if not path.exists():
        return {"present": False}

    rows = []
    with path.open(newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            rows.append(row)

    if not rows:
        return {"present": True, "path": str(path), "sample_count": 0}

    def floats(key):
        return [float(row[key]) for row in rows if row.get(key)]

    total_cpu = floats("total_cpu_percent")
    total_rss_mb = floats("total_rss_mb")
    max_rss_mb = floats("max_rss_mb")

    return {
        "present": True,
        "path": str(path),
        "sample_count": len(rows),
        "avg_total_cpu_percent": round(sum(total_cpu) / len(total_cpu), 3) if total_cpu else None,
        "max_total_cpu_percent": max(total_cpu) if total_cpu else None,
        "avg_total_rss_mb": round(sum(total_rss_mb) / len(total_rss_mb), 3) if total_rss_mb else None,
        "max_total_rss_mb": max(total_rss_mb) if total_rss_mb else None,
        "max_observed_single_pid_rss_mb": max(max_rss_mb) if max_rss_mb else None,
    }


def copy_model_outputs(root: Path, report_dir: Path, source_dir: Path | None = None):
    source_dir = source_dir or (root / "res")
    output_dir = report_dir / "model_outputs"
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(exist_ok=True)

    copied = 0
    if source_dir.exists():
        for path in source_dir.rglob("*"):
            relative = path.relative_to(source_dir)
            dest = output_dir / relative
            if path.is_dir():
                dest.mkdir(parents=True, exist_ok=True)
                continue
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, dest)
            copied += 1

    return {
        "present": copied > 0,
        "path": str(output_dir.relative_to(root)),
        "file_count": copied,
        "html_count": len(list(output_dir.glob("*.html"))),
    }


def infer_metric(summary: dict | None):
    if not summary:
        return {
            "type": "test",
            "label": "Test AUC",
            "detail": "Legacy report without summary metadata.",
        }

    auc_source = summary.get("auc", {}).get("auc_source", "")
    if "Training AUC" in auc_source:
        return {
            "type": "train",
            "label": "Training AUC",
            "detail": auc_source,
        }
    if "Test AUC" in auc_source:
        return {
            "type": "test",
            "label": "Test AUC",
            "detail": auc_source,
        }

    return {
        "type": "test",
        "label": "Test AUC",
        "detail": auc_source or "Test AUC",
    }


def write_report_bundle(report_dir: Path, auc_df: pd.DataFrame, report_summary: dict):
    bundle = {
        "name": report_dir.name,
        "path": report_summary.get("report_dir", report_dir.name),
        "id": report_summary.get("report_id", report_dir.name),
        "display_name": report_summary.get("report_display_name", report_dir.name),
        "model_outputs_path": report_summary.get("model_outputs", {}).get("path", f"{report_dir.name}/model_outputs"),
        "metric": infer_metric(report_summary),
        "summary": report_summary,
        "rows": auc_df.to_dict(orient="records"),
    }
    (report_dir / "report_bundle.json").write_text(json.dumps(bundle, indent=2) + "\n")


def _load_report_entry(root: Path, report_dir: Path):
    auc_path = report_dir / "auc_and_contributions.csv"
    if not auc_path.exists():
        return None

    summary_path = report_dir / "report_summary.json"
    summary = json.loads(summary_path.read_text()) if summary_path.exists() else None
    auc_df = pd.read_csv(auc_path).sort_values("Species").reset_index(drop=True)
    report_id = str(report_dir.relative_to(root))
    if report_id.startswith("reports/"):
        display_name = report_dir.name
    else:
        display_name = report_id

    model_outputs_path = summary.get("model_outputs", {}).get("path") if summary else None
    if not model_outputs_path:
        model_outputs_path = str((report_dir / "model_outputs").relative_to(root))

    return {
        "name": report_dir.name,
        "id": report_id,
        "display_name": display_name,
        "path": str(report_dir.relative_to(root)),
        "model_outputs_path": model_outputs_path,
        "metric": infer_metric(summary),
        "summary": summary,
        "rows": auc_df.to_dict(orient="records"),
    }


def build_manifest(root: Path):
    config_path = root / "src" / "backend" / "config" / "config.json"
    reports_dir = root / "reports"
    manifest_reports = []

    if reports_dir.exists():
        for report_dir in sorted([path for path in reports_dir.iterdir() if path.is_dir()], key=lambda path: path.name):
            entry = _load_report_entry(root, report_dir)
            if entry:
                manifest_reports.append(entry)

    configured_run_root = root / "experiments"
    if config_path.exists():
        config = json.loads(config_path.read_text())
        run_root_value = config.get("run_root", "experiments")
        configured_run_root = Path(run_root_value) if Path(run_root_value).is_absolute() else (root / run_root_value)

    if configured_run_root.exists():
        experiment_report_dirs = sorted(configured_run_root.glob("*/reports/*"))
        for report_dir in experiment_report_dirs:
            if report_dir.is_dir():
                entry = _load_report_entry(root, report_dir)
                if entry:
                    manifest_reports.append(entry)

    manifest = {
        "generated_at": datetime.now().isoformat(),
        "reports": manifest_reports,
    }

    manifest_path = reports_dir / "report_manifest.js"
    manifest_path.write_text(
        "window.REPORT_MANIFEST = " + json.dumps(manifest, indent=2) + ";\n"
    )

    return manifest_path, len(manifest_reports)


def generate_report_bundle(
    root: Path,
    report_dir: Path,
    run_identity: dict,
    res_dir: Path | None = None,
    logs_dir: Path | None = None,
    display_name: str | None = None,
    report_id: str | None = None,
):
    res_dir = res_dir or (root / "res")
    logs_dir = logs_dir or (root / "logs")

    auc_bundle = build_auc_from_html_dir(res_dir, root)
    if auc_bundle[0].empty:
        auc_bundle = build_auc_from_maxent_results_dir(res_dir, root)
        if auc_bundle is None:
            raise FileNotFoundError(
                f"Could not find per-species HTML reports or maxentResults.csv under {res_dir}."
            )
    auc_df, auc_meta = auc_bundle

    auc_path = report_dir / "auc_and_contributions.csv"
    auc_df.to_csv(auc_path, index=False)

    timing_summary = parse_timing_log(logs_dir / "maxent_timing.txt")
    usage_summary = parse_usage_log(logs_dir / "maxent_usage.csv")
    model_outputs_summary = copy_model_outputs(root, report_dir, source_dir=res_dir)

    report_summary = {
        "generated_at": datetime.now().isoformat(),
        "report_dir": str(report_dir.relative_to(root)),
        "report_id": report_id or str(report_dir.relative_to(root)),
        "report_display_name": display_name or str(report_dir.relative_to(root)),
        "run_signature": run_identity["signature"],
        "run_anchor_timestamp": run_identity["anchor_timestamp"],
        "run_identity": run_identity["metadata"],
        "auc": auc_meta,
        "timing": timing_summary,
        "usage": usage_summary,
        "model_outputs": model_outputs_summary,
        "notes": [
            "This report bundle is derived from PlantWise_v0 run artifacts.",
            "The generated auc_and_contributions.csv uses the legacy filename for compatibility.",
            "If Maxent test AUC is unavailable in current outputs, Training AUC is mapped into the compatibility column 'Test AUC'.",
        ],
    }

    (report_dir / "report_summary.json").write_text(
        json.dumps(report_summary, indent=2) + "\n"
    )
    write_report_bundle(report_dir, auc_df, report_summary)
    manifest_path, manifest_count = build_manifest(root)
    return {
        "report_dir": report_dir,
        "auc_path": auc_path,
        "report_summary": report_summary,
        "model_outputs_summary": model_outputs_summary,
        "manifest_path": manifest_path,
        "manifest_count": manifest_count,
    }


def main():
    args = parse_args()
    root = Path(args.root).resolve()
    run_identity = get_run_identity(root)
    report_dir = make_report_dir(root, args.name, run_identity)
    result = generate_report_bundle(root=root, report_dir=report_dir, run_identity=run_identity)

    print(f"Wrote report bundle to {result['report_dir']}")
    print(f"  - {result['auc_path'].name}")
    print(f"  - report_summary.json")
    print(f"  - report_bundle.json")
    print(
        f"  - model_outputs/ ({result['model_outputs_summary']['file_count']} files, "
        f"{result['model_outputs_summary']['html_count']} html files)"
    )
    print(f"Updated {result['manifest_path']} with {result['manifest_count']} report entries")


if __name__ == "__main__":
    main()
