#!/usr/bin/env python3
"""Local JSON workspace editor. Uses only the Python standard library."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import sys
import tempfile
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "web"
READ_ONLY = {"candidate/education.json"}
DIRECTORIES = ("candidate", "jobs", "state")
MAX_BODY = 2 * 1024 * 1024
sys.path.insert(0, str(ROOT / "tools"))
import job_state  # noqa: E402


def allowed_path(name: str) -> Path | None:
    if not re.fullmatch(r"(candidate|jobs|state)/[A-Za-z0-9_-]+\.json", name):
        return None
    path = ROOT / name
    if not path.is_file() or path.is_symlink():
        return None
    return path


def revision(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def snapshot(path: Path) -> tuple[object, str]:
    raw = path.read_bytes()
    return json.loads(raw), revision(raw)


def file_inventory() -> list[dict]:
    records = []
    for directory in DIRECTORIES:
        for path in sorted((ROOT / directory).glob("*.json")):
            name = path.relative_to(ROOT).as_posix()
            if allowed_path(name):
                records.append({"path": name, "read_only": name in READ_ONLY})
    return records


def backup_file(path: Path) -> None:
    backup_dir = ROOT / ".dashboard" / "backups" / path.parent.name
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    shutil.copy2(path, backup_dir / f"{path.stem}-{stamp}.json")


def write_json(path: Path, data: object) -> None:
    backup_file(path)
    payload = (json.dumps(data, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    fd, temp_name = tempfile.mkstemp(prefix=".dashboard-", suffix=".json", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as output:
            output.write(payload)
        os.chmod(temp_name, stat.S_IMODE(path.stat().st_mode))
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


class Handler(BaseHTTPRequestHandler):
    server_version = "ResumeWorkspace/1.0"

    def send_json(self, status: int, payload: object) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def error_json(self, status: int, message: str) -> None:
        self.send_json(status, {"error": message})

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/files":
            self.send_json(200, {"files": file_inventory()})
            return
        if parsed.path == "/api/summary":
            self.send_json(200, job_state.get_summary(str(ROOT / "jobs")))
            return
        if parsed.path == "/api/file":
            name = parse_qs(parsed.query).get("path", [""])[0]
            path = allowed_path(name)
            if path is None:
                self.error_json(404, "JSON file not found")
                return
            try:
                data, etag = snapshot(path)
            except (OSError, ValueError):
                self.error_json(500, "Could not read this JSON file")
                return
            self.send_json(200, {"path": name, "data": data, "revision": etag,
                                 "read_only": name in READ_ONLY})
            return
        static = {"/": ("index.html", "text/html"),
                  "/styles.css": ("styles.css", "text/css"),
                  "/app.js": ("app.js", "text/javascript")}
        if parsed.path not in static:
            self.send_error(404)
            return
        filename, mime = static[parsed.path]
        body = (WEB / filename).read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", f"{mime}; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_PUT(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path != "/api/file":
            self.error_json(404, "Unknown endpoint")
            return
        origin = self.headers.get("Origin")
        if origin and urlparse(origin).netloc != self.headers.get("Host"):
            self.error_json(403, "Cross-origin writes are blocked")
            return
        if self.headers.get("Content-Type", "").split(";")[0].strip() != "application/json":
            self.error_json(415, "Use application/json")
            return
        name = parse_qs(parsed.query).get("path", [""])[0]
        path = allowed_path(name)
        if path is None:
            self.error_json(404, "JSON file not found")
            return
        if name in READ_ONLY:
            self.error_json(403, "Education is read-only in this workflow")
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            length = 0
        if not 0 < length <= MAX_BODY:
            self.error_json(413, "Invalid or oversized JSON body")
            return
        try:
            request = json.loads(self.rfile.read(length))
            incoming = request["data"]
            expected = request["revision"]
            if not isinstance(expected, str):
                raise ValueError("Missing revision")
        except (ValueError, KeyError, TypeError):
            self.error_json(400, "Send valid JSON data and its current revision")
            return
        try:
            _, current = snapshot(path)
            if current != expected:
                self.error_json(409, "File changed on disk. Reload before saving.")
                return
            if name.startswith("jobs/"):
                if not isinstance(incoming, dict) or incoming.get("id") != path.stem:
                    self.error_json(400, "Job ID must match the filename")
                    return
                if incoming.get("pipeline_status") not in job_state.VALID_STATUSES:
                    self.error_json(400, "Invalid job pipeline status")
                    return
                # Use the workspace Job Object writer and refresh derived pipeline state.
                backup_file(path)
                job_state.save_job(incoming, str(ROOT / "jobs"))
                job_state.update_pipeline_state(str(ROOT / "jobs"), str(ROOT / "state"))
            else:
                write_json(path, incoming)
            saved, etag = snapshot(path)
        except (OSError, ValueError) as exc:
            self.error_json(500, f"Could not save: {exc}")
            return
        self.send_json(200, {"path": name, "data": saved, "revision": etag,
                             "read_only": False})


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the local JSON and resume preview website")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"Local dashboard: http://127.0.0.1:{args.port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
