import json
import shlex
import sys
import threading
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from subprocess import PIPE, STDOUT, Popen
from typing import Any

import pandas as pd
from flask import Flask, Response, jsonify, redirect, render_template_string, request, send_from_directory

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = Path(__file__).resolve().parent / "config" / "config.json"
FRONTEND_DIR = PROJECT_ROOT / "src" / "frontend"
MAXENT_JAR = PROJECT_ROOT / "maxent.jar"
ENVIRONMENTAL_LAYERS = PROJECT_ROOT / "final_attributes"
REQUIRED_COLUMNS = ["Species", "Latitude", "Longitude"]
RESERVED_ARG_KEYS = {"samplesfile", "outputdirectory", "environmentallayers"}

sys.path.insert(0, str(PROJECT_ROOT))

from generate_reports import build_manifest, generate_report_bundle, get_run_identity


@dataclass
class RunRecord:
    name: str
    run_dir: Path
    status: str = "pending"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    pid: int | None = None
    process: Popen | None = None
    species: str | None = None
    report_dir: str | None = None
    error: str | None = None

    def as_dict(self):
        return {
            "name": self.name,
            "run_dir": str(self.run_dir),
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "pid": self.pid,
            "species": self.species,
            "report_dir": self.report_dir,
            "error": self.error,
        }


class ExperimentService:
    def __init__(self):
        self.config = self._load_config()
        self.run_root = self._resolve_path(self.config["run_root"])
        self.seed_data_path = self._resolve_path(self.config["seed_data"])
        self.run_root.mkdir(parents=True, exist_ok=True)
        self.seed_df = self._load_seed_df()
        self.allowed_args = {arg.lower() for arg in self.config["maxent_allowed_args"]}
        self.default_args = self._normalize_args(self.config["maxent_args"])
        self._validate_default_args()
        self.runs: dict[str, RunRecord] = {}
        self.lock = threading.Lock()

    def _load_config(self):
        config = json.loads(CONFIG_PATH.read_text())
        return config

    def _resolve_path(self, value: str) -> Path:
        path = Path(value)
        return path if path.is_absolute() else PROJECT_ROOT / path

    def _load_seed_df(self):
        df = pd.read_csv(self.seed_data_path)
        self._validate_dataframe_schema(df)
        return df

    def _validate_dataframe_schema(self, df: pd.DataFrame):
        if list(df.columns) != REQUIRED_COLUMNS:
            raise ValueError(
                f"CSV schema must match {REQUIRED_COLUMNS}. Received {list(df.columns)}"
            )
        for column in ["Latitude", "Longitude"]:
            pd.to_numeric(df[column], errors="raise")

    def _normalize_args(self, raw_args: list[str]):
        flags = set()
        keyed = {}
        for token in raw_args:
            key, value = self._parse_arg_token(token)
            if value is None:
                flags.add(key)
                keyed.pop(key, None)
            else:
                keyed[key] = value
                flags.discard(key)
        return {"flags": flags, "keyed": keyed}

    def _parse_arg_token(self, token: str):
        if "=" in token:
            key, value = token.split("=", 1)
            return key.strip().lower(), value.strip()
        return token.strip().lower(), None

    def _validate_default_args(self):
        errors = self.validate_maxent_args(" ".join(self.config["maxent_args"]))
        if not errors["ok"]:
            raise ValueError(f"Invalid default maxent_args: {errors['errors']}")

    def validate_run_name(self, name: str):
        errors = []
        if not name:
            errors.append("Run name is required.")
        if "/" in name or "\\" in name:
            errors.append("Run name must not contain path separators.")
        if (self.run_root / name).exists():
            errors.append(f"Run '{name}' already exists under {self.run_root}.")
        return {"ok": not errors, "errors": errors}

    def validate_uploaded_files(self, files, species: str | None):
        if not files:
            return {
                "ok": True,
                "errors": [],
                "uploaded_row_count": 0,
                "uploaded_species_row_count": 0,
                "merged_species_row_count": int((self.seed_df["Species"] == species).sum()) if species else None,
            }

        uploaded_frames = []
        errors = []
        for storage in files:
            if not storage.filename:
                continue
            try:
                df = pd.read_csv(storage.stream)
                self._validate_dataframe_schema(df)
                uploaded_frames.append(df)
            except Exception as exc:
                errors.append(f"{storage.filename}: {exc}")
            finally:
                storage.stream.seek(0)

        if errors:
            return {"ok": False, "errors": errors}

        uploaded_df = pd.concat(uploaded_frames, ignore_index=True) if uploaded_frames else pd.DataFrame(columns=REQUIRED_COLUMNS)
        uploaded_species_rows = int((uploaded_df["Species"] == species).sum()) if species else None
        merged_df = pd.concat([self.seed_df, uploaded_df], ignore_index=True)
        merged_species_rows = int((merged_df["Species"] == species).sum()) if species else None

        dataset_errors = []
        if species and uploaded_species_rows == 0:
            dataset_errors.append(f"Uploaded dataset does not contain species '{species}'.")

        return {
            "ok": not dataset_errors,
            "errors": dataset_errors,
            "uploaded_row_count": int(len(uploaded_df)),
            "uploaded_species_row_count": uploaded_species_rows,
            "merged_species_row_count": merged_species_rows,
        }

    def validate_maxent_args(self, raw_args: str):
        errors = []
        normalized = {"flags": set(self.default_args["flags"]), "keyed": dict(self.default_args["keyed"])}
        if raw_args.strip():
            try:
                tokens = shlex.split(raw_args)
            except ValueError as exc:
                return {"ok": False, "errors": [str(exc)], "merged_args": []}
            for token in tokens:
                key, value = self._parse_arg_token(token)
                if key not in self.allowed_args:
                    errors.append(f"Unknown Maxent arg '{key}'.")
                    continue
                if key in RESERVED_ARG_KEYS:
                    errors.append(f"Arg '{key}' is server-managed and cannot be overridden.")
                    continue
                if value is None:
                    normalized["flags"].add(key)
                    normalized["keyed"].pop(key, None)
                else:
                    normalized["keyed"][key] = value
                    normalized["flags"].discard(key)

        merged_args = sorted(normalized["flags"]) + [f"{key}={normalized['keyed'][key]}" for key in sorted(normalized["keyed"])]
        return {
            "ok": not errors,
            "errors": errors,
            "merged_args": merged_args,
            "normalized": {
                "flags": sorted(normalized["flags"]),
                "keyed": dict(sorted(normalized["keyed"].items())),
            },
        }

    def _write_request_metadata(self, run_dir: Path, payload: dict[str, Any]):
        (run_dir / "request.json").write_text(json.dumps(payload, indent=2) + "\n")

    def _prepare_run_dirs(self, name: str):
        run_dir = self.run_root / name
        data_dir = run_dir / "data"
        uploaded_dir = data_dir / "uploaded"
        model_dir = run_dir / "model"
        logs_dir = model_dir / "logs"
        res_dir = model_dir / "res"
        reports_dir = run_dir / "reports"
        for path in [uploaded_dir, logs_dir, res_dir, reports_dir]:
            path.mkdir(parents=True, exist_ok=True)
        return {
            "run_dir": run_dir,
            "data_dir": data_dir,
            "uploaded_dir": uploaded_dir,
            "model_dir": model_dir,
            "logs_dir": logs_dir,
            "res_dir": res_dir,
            "reports_dir": reports_dir,
        }

    def _save_uploaded_files(self, files, uploaded_dir: Path):
        uploaded_paths = []
        uploaded_frames = []
        for storage in files:
            if not storage.filename:
                continue
            target = uploaded_dir / Path(storage.filename).name
            storage.save(target)
            uploaded_paths.append(target)
            df = pd.read_csv(target)
            self._validate_dataframe_schema(df)
            uploaded_frames.append(df)
        return uploaded_paths, uploaded_frames

    def start_run(self, name: str, species: str, raw_args: str, files):
        name_validation = self.validate_run_name(name)
        if not name_validation["ok"]:
            return {"ok": False, "errors": name_validation["errors"]}

        dataset_validation = self.validate_uploaded_files(files, species)
        if not dataset_validation["ok"]:
            return {"ok": False, "errors": dataset_validation["errors"]}

        arg_validation = self.validate_maxent_args(raw_args)
        if not arg_validation["ok"]:
            return {"ok": False, "errors": arg_validation["errors"]}

        paths = self._prepare_run_dirs(name)
        uploaded_paths, uploaded_frames = self._save_uploaded_files(files, paths["uploaded_dir"])
        merged_df = pd.concat([self.seed_df, *uploaded_frames], ignore_index=True) if uploaded_frames else self.seed_df.copy()
        filtered_df = merged_df[merged_df["Species"] == species].copy()
        if filtered_df.empty:
            return {"ok": False, "errors": [f"No rows found for species '{species}' after merging seed and uploaded data."]}

        merged_path = paths["data_dir"] / "merged_input.csv"
        filtered_path = paths["data_dir"] / "filtered_species.csv"
        merged_df.to_csv(merged_path, index=False)
        filtered_df.to_csv(filtered_path, index=False)

        request_payload = {
            "name": name,
            "species": species,
            "seed_data": str(self.seed_data_path.relative_to(PROJECT_ROOT)),
            "uploaded_files": [str(path.relative_to(PROJECT_ROOT)) for path in uploaded_paths],
            "merged_args": arg_validation["merged_args"],
            "created_at": datetime.now().isoformat(),
        }
        self._write_request_metadata(paths["run_dir"], request_payload)

        record = RunRecord(name=name, run_dir=paths["run_dir"], status="queued", species=species)
        with self.lock:
            self.runs[name] = record

        worker = threading.Thread(
            target=self._run_worker,
            args=(record, filtered_path, paths, arg_validation["merged_args"]),
            daemon=True,
        )
        worker.start()

        return {
            "ok": True,
            "run_url": f"/runs/{name}",
            "api_url": f"/api/runs/{name}",
            "name": name,
        }

    def _run_worker(self, record: RunRecord, filtered_path: Path, paths: dict[str, Path], merged_args: list[str]):
        log_path = paths["logs_dir"] / "run.log"
        timing_path = paths["logs_dir"] / "maxent_timing.txt"
        start = datetime.now()
        record.status = "running"
        record.updated_at = start.isoformat()

        java_command = [
            "java",
            "-Djava.awt.headless=true",
            "-cp",
            str(MAXENT_JAR),
            "density.MaxEnt",
            *merged_args,
            f"outputdirectory={paths['res_dir']}",
            f"samplesfile={filtered_path}",
            f"environmentallayers={ENVIRONMENTAL_LAYERS}",
        ]

        with log_path.open("w") as log_file, timing_path.open("w") as timing_file:
            timing_file.write("Preparing to process 1 species files\n")
            timing_file.write(f"[1/1] Starting {filtered_path.name} (0 remaining after current)\n")
            log_file.write("Command:\n")
            log_file.write(" ".join(shlex.quote(part) for part in java_command) + "\n\n")
            try:
                process = Popen(
                    java_command,
                    stdout=PIPE,
                    stderr=STDOUT,
                    text=True,
                    cwd=PROJECT_ROOT,
                )
                record.process = process
                record.pid = process.pid
                for line in process.stdout:
                    log_file.write(line)
                    log_file.flush()
                return_code = process.wait()
                record.process = None
                end = datetime.now()
                elapsed = round((end - start).total_seconds(), 3)
                timing_file.write(f"[1/1] Finished {filtered_path.name} in {elapsed}s\n")

                if return_code != 0:
                    record.status = "failed"
                    record.error = f"Maxent exited with code {return_code}."
                    record.updated_at = end.isoformat()
                    return

                run_identity = get_run_identity(paths["model_dir"])
                report_dir = paths["reports_dir"] / run_identity["anchor_timestamp"]
                report_dir.mkdir(parents=True, exist_ok=True)
                result = generate_report_bundle(
                    root=PROJECT_ROOT,
                    report_dir=report_dir,
                    run_identity=run_identity,
                    res_dir=paths["res_dir"],
                    logs_dir=paths["logs_dir"],
                    display_name=f"experiments/{record.name}/reports/{report_dir.name}",
                    report_id=str(report_dir.relative_to(PROJECT_ROOT)),
                )
                record.report_dir = str(result["report_dir"].relative_to(PROJECT_ROOT))
                record.status = "completed"
                record.updated_at = datetime.now().isoformat()
            except Exception as exc:
                record.status = "failed"
                record.error = str(exc)
                record.updated_at = datetime.now().isoformat()
                with log_path.open("a") as log_file_append:
                    log_file_append.write(f"\nERROR: {exc}\n")

    def get_run_record(self, name: str):
        with self.lock:
            record = self.runs.get(name)
        if record:
            if record.process and record.process.poll() is not None and record.status == "running":
                record.status = "failed" if record.process.returncode else "completed"
                record.updated_at = datetime.now().isoformat()
                record.process = None
            return record

        run_dir = self.run_root / name
        if not run_dir.exists():
            return None

        request_path = run_dir / "request.json"
        request_payload = json.loads(request_path.read_text()) if request_path.exists() else {}
        status = "completed" if any((run_dir / "reports").glob("*/report_summary.json")) else "unknown"
        record = RunRecord(name=name, run_dir=run_dir, status=status, species=request_payload.get("species"))
        record.report_dir = self._discover_report_dir(run_dir)
        return record

    def _discover_report_dir(self, run_dir: Path):
        summaries = sorted((run_dir / "reports").glob("*/report_summary.json"))
        if not summaries:
            return None
        return str(summaries[-1].parent.relative_to(PROJECT_ROOT))

    def list_runs(self):
        names = sorted({path.name for path in self.run_root.iterdir() if path.is_dir()} | set(self.runs.keys()))
        return [self.get_run_record(name) for name in names if self.get_run_record(name)]


service = ExperimentService()
app = Flask(__name__)


def json_error(message: str, status: int = 400):
    return jsonify({"ok": False, "errors": [message]}), status


@app.route("/")
def frontend_index():
    return redirect("/reports/index.html")


@app.route("/experiments/new")
def experiment_form():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/experiments/static/<path:filename>")
def experiment_static(filename: str):
    return send_from_directory(FRONTEND_DIR, filename)


@app.route("/reports/")
@app.route("/reports/<path:filename>")
def reports_files(filename: str = "index.html"):
    return send_from_directory(PROJECT_ROOT / "reports", filename)


@app.route("/experiments/<path:filename>")
def experiments_files(filename: str):
    return send_from_directory(PROJECT_ROOT / "experiments", filename)


@app.route("/api/config")
def api_config():
    return jsonify(
        {
            "ok": True,
            "seed_data": str(service.seed_data_path.relative_to(PROJECT_ROOT)),
            "run_root": str(service.run_root.relative_to(PROJECT_ROOT)),
            "required_columns": REQUIRED_COLUMNS,
            "default_maxent_args": sorted(service.default_args["flags"]) + [f"{key}={service.default_args['keyed'][key]}" for key in sorted(service.default_args["keyed"])],
        }
    )


@app.route("/api/validate/name", methods=["POST"])
def validate_name():
    payload = request.get_json(force=True, silent=True) or {}
    result = service.validate_run_name(payload.get("name", "").strip())
    return jsonify(result)


@app.route("/api/validate/maxent-args", methods=["POST"])
def validate_maxent_args():
    payload = request.get_json(force=True, silent=True) or {}
    result = service.validate_maxent_args(payload.get("args", ""))
    return jsonify(result)


@app.route("/api/validate/dataset", methods=["POST"])
def validate_dataset():
    species = request.form.get("species", "").strip()
    files = request.files.getlist("files")
    result = service.validate_uploaded_files(files, species)
    return jsonify(result)


@app.route("/api/runs", methods=["POST"])
def create_run():
    name = request.form.get("name", "").strip()
    species = request.form.get("species", "").strip()
    raw_args = request.form.get("maxent_args", "")
    files = request.files.getlist("files")

    if not species:
        return json_error("Species is required.")

    result = service.start_run(name=name, species=species, raw_args=raw_args, files=files)
    if not result["ok"]:
        return jsonify(result), 400
    return jsonify(result)


@app.route("/api/runs")
def api_runs():
    return jsonify({"ok": True, "runs": [record.as_dict() for record in service.list_runs()]})


@app.route("/api/runs/<name>")
def api_run_detail(name: str):
    record = service.get_run_record(name)
    if not record:
        return json_error(f"Run '{name}' not found.", 404)

    log_path = record.run_dir / "model" / "logs" / "run.log"
    log_text = log_path.read_text(errors="ignore") if log_path.exists() else ""
    return jsonify({"ok": True, "run": record.as_dict(), "log": log_text})


RUN_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Run {{ name }}</title>
  <style>
    body { font-family: Georgia, serif; margin: 32px; background: #f7f4ec; color: #1d211f; }
    main { max-width: 1080px; margin: 0 auto; }
    .panel { background: #fffdf8; border: 1px solid #ddd3c1; border-radius: 14px; padding: 18px; margin-bottom: 18px; }
    pre { white-space: pre-wrap; word-break: break-word; background: #11181b; color: #edf3ef; padding: 16px; border-radius: 12px; overflow: auto; max-height: 60vh; }
    .status { font-weight: 700; }
    a.button { display: inline-block; margin-right: 10px; padding: 10px 14px; border-radius: 999px; background: #164b46; color: white; text-decoration: none; }
  </style>
</head>
<body>
  <main>
    <div class="panel">
      <h1>Run {{ name }}</h1>
      <p class="status">Status: {{ status }}</p>
      {% if error %}<p>Error: {{ error }}</p>{% endif %}
      {% if report_dir %}<p>Report: <code>{{ report_dir }}</code></p>{% endif %}
      <p>
        <a class="button" href="/">Back</a>
        <a class="button" href="/runs/{{ name }}">Refresh</a>
        {% if report_dir %}<a class="button" href="/reports/index.html">Regression viewer</a>{% endif %}
      </p>
    </div>
    <div class="panel">
      <h2>Logs</h2>
      <pre>{{ log_text }}</pre>
    </div>
  </main>
</body>
</html>
"""


@app.route("/runs/<name>")
def run_page(name: str):
    record = service.get_run_record(name)
    if not record:
        return json_error(f"Run '{name}' not found.", 404)

    log_path = record.run_dir / "model" / "logs" / "run.log"
    log_text = log_path.read_text(errors="ignore") if log_path.exists() else ""
    return render_template_string(
        RUN_TEMPLATE,
        name=record.name,
        status=record.status,
        error=record.error,
        report_dir=record.report_dir,
        log_text=log_text,
    )


@app.route("/runs")
def runs_page():
    items = service.list_runs()
    lines = [
        f"<li><a href='/runs/{record.name}'>{record.name}</a> - {record.status}</li>"
        for record in items
    ]
    return Response(
        "<html><body><h1>Runs</h1><ul>" + "".join(lines) + "</ul><p><a href='/'>Back</a></p></body></html>",
        mimetype="text/html",
    )


if __name__ == "__main__":
    build_manifest(PROJECT_ROOT)
    app.run(debug=True, host="0.0.0.0", port=5050)
