# The purpose of this script is to monitor the cpu/ram usage via sampling,
# during the InitialImplementation.py run. See README.md for invocation. 
import argparse
import csv
import os
import signal
import subprocess
import sys


def parse_args():
    parser = argparse.ArgumentParser(
        description="Monitor Maxent Java processes with pidstat and write active samples to CSV."
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path to the CSV file to write."
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=1,
        help="Sampling interval in seconds. Default: 1"
    )
    return parser.parse_args()


def get_process_args(pid):
    try:
        result = subprocess.run(
            ["ps", "-p", str(pid), "-o", "args="],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError:
        return ""
    return result.stdout.strip()


def is_maxent_process(cmdline):
    return "maxent.jar" in cmdline or "density.MaxEnt" in cmdline


def parse_pidstat_line(line):
    tokens = line.split()
    if len(tokens) < 14:
        return None

    try:
        uid = tokens[-14]
        pid = int(tokens[-13])
        cpu_percent = float(tokens[-8])
        rss_kb = float(tokens[-3])
    except ValueError:
        return None

    timestamp = " ".join(tokens[:-14])
    command = tokens[-1]
    return {
        "timestamp": timestamp,
        "uid": uid,
        "pid": pid,
        "cpu_percent": cpu_percent,
        "rss_kb": rss_kb,
        "command": command,
    }


def ensure_parent_dir(path):
    parent = os.path.dirname(os.path.abspath(path))
    if parent:
        os.makedirs(parent, exist_ok=True)


def open_writer(path):
    ensure_parent_dir(path)
    file_exists = os.path.exists(path)
    csvfile = open(path, "a", newline="")
    writer = csv.DictWriter(
        csvfile,
        fieldnames=[
            "timestamp",
            "pid_count",
            "pids",
            "total_cpu_percent",
            "avg_cpu_percent",
            "max_cpu_percent",
            "total_rss_kb",
            "total_rss_mb",
            "max_rss_kb",
            "max_rss_mb",
        ],
    )
    if not file_exists or os.path.getsize(path) == 0:
        writer.writeheader()
        csvfile.flush()
    return csvfile, writer


def flush_sample(writer, csvfile, timestamp, matches):
    if not timestamp or not matches:
        return

    total_cpu = sum(item["cpu_percent"] for item in matches)
    total_rss_kb = sum(item["rss_kb"] for item in matches)
    max_cpu = max(item["cpu_percent"] for item in matches)
    max_rss_kb = max(item["rss_kb"] for item in matches)
    pids = ";".join(str(item["pid"]) for item in matches)

    writer.writerow(
        {
            "timestamp": timestamp,
            "pid_count": len(matches),
            "pids": pids,
            "total_cpu_percent": f"{total_cpu:.2f}",
            "avg_cpu_percent": f"{(total_cpu / len(matches)):.2f}",
            "max_cpu_percent": f"{max_cpu:.2f}",
            "total_rss_kb": f"{total_rss_kb:.0f}",
            "total_rss_mb": f"{total_rss_kb / 1024:.2f}",
            "max_rss_kb": f"{max_rss_kb:.0f}",
            "max_rss_mb": f"{max_rss_kb / 1024:.2f}",
        }
    )
    csvfile.flush()


def main():
    args = parse_args()
    csvfile, writer = open_writer(args.output)

    pidstat_cmd = [
        "pidstat",
        "-r",
        "-u",
        "-h",
        "-C",
        "java",
        str(args.interval),
    ]

    process = subprocess.Popen(
        pidstat_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    def shutdown(_signum=None, _frame=None):
        if process.poll() is None:
            process.terminate()
        csvfile.close()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    current_timestamp = None
    current_matches = []

    try:
        for raw_line in process.stdout:
            line = raw_line.strip()
            if not line or line.startswith("#") or line.startswith("Linux "):
                continue

            parsed = parse_pidstat_line(line)
            if not parsed:
                continue

            if current_timestamp is None:
                current_timestamp = parsed["timestamp"]
            elif parsed["timestamp"] != current_timestamp:
                flush_sample(writer, csvfile, current_timestamp, current_matches)
                current_timestamp = parsed["timestamp"]
                current_matches = []

            cmdline = get_process_args(parsed["pid"])
            if not is_maxent_process(cmdline):
                continue

            current_matches.append(parsed)

        flush_sample(writer, csvfile, current_timestamp, current_matches)
    finally:
        csvfile.close()


if __name__ == "__main__":
    main()
