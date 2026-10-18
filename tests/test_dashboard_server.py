import json
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen

import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import dashboard_server as dashboard


class DashboardServerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.original_root = dashboard.ROOT
        dashboard.ROOT = Path(self.tmp.name)
        for name in ("candidate", "jobs", "state"):
            (dashboard.ROOT / name).mkdir()
        (dashboard.ROOT / "candidate" / "education.json").write_text('[{"institution":"Original College"}]\n')
        (dashboard.ROOT / "candidate" / "projects.json").write_text('[]\n')
        (dashboard.ROOT / "jobs" / "job_001.json").write_text('{"id":"job_001","pipeline_status":"NEW","url":"https://example.com"}\n')
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), dashboard.Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base = f"http://127.0.0.1:{self.server.server_port}"

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()
        dashboard.ROOT = self.original_root
        self.tmp.cleanup()

    def get_file(self, path):
        with urlopen(f"{self.base}/api/file?path={quote(path)}") as response:
            return json.load(response)

    def put_file(self, path, data, revision):
        payload = json.dumps({"data": data, "revision": revision}).encode()
        request = Request(f"{self.base}/api/file?path={quote(path)}", data=payload,
                          headers={"Content-Type": "application/json"}, method="PUT")
        return urlopen(request)

    def test_education_cannot_be_saved(self):
        before = self.get_file("candidate/education.json")
        with self.assertRaises(HTTPError) as error:
            self.put_file("candidate/education.json", [{"institution": "Changed"}], before["revision"])
        self.assertEqual(error.exception.code, 403)
        self.assertEqual(self.get_file("candidate/education.json")["data"], before["data"])

    def test_save_creates_backup_and_rejects_stale_revision(self):
        before = self.get_file("candidate/projects.json")
        with self.put_file("candidate/projects.json", [{"name": "Sample"}], before["revision"]) as response:
            saved = json.load(response)
        self.assertEqual(saved["data"], [{"name": "Sample"}])
        backups = list((dashboard.ROOT / ".dashboard" / "backups" / "candidate").glob("projects-*.json"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(json.loads(backups[0].read_text()), [])
        with self.assertRaises(HTTPError) as error:
            self.put_file("candidate/projects.json", [], before["revision"])
        self.assertEqual(error.exception.code, 409)

    def test_job_save_rejects_id_change_and_refreshes_pipeline(self):
        before = self.get_file("jobs/job_001.json")
        with self.assertRaises(HTTPError) as error:
            self.put_file("jobs/job_001.json", {"id": "other", "pipeline_status": "NEW"}, before["revision"])
        self.assertEqual(error.exception.code, 400)
        with self.put_file("jobs/job_001.json", before["data"], before["revision"]) as response:
            self.assertEqual(json.load(response)["data"]["id"], "job_001")
        pipeline = json.loads((dashboard.ROOT / "state" / "pipeline.json").read_text())
        self.assertEqual(pipeline["total_jobs"], 1)


if __name__ == "__main__":
    unittest.main()
