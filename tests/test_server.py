"""Standard-library smoke tests for LAN hosting and caching."""
import gzip
import http.client
import json
import threading
import unittest

from server import GameHandler
from http.server import ThreadingHTTPServer


class GameServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.httpd = ThreadingHTTPServer(("127.0.0.1", 0), GameHandler)
        cls.port = cls.httpd.server_address[1]
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()
        cls.thread.join(timeout=3)

    def request(self, method, route, body=None, headers=None):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        conn.request(method, route, body, headers or {})
        res = conn.getresponse()
        result = res.status, dict(res.getheaders()), res.read()
        conn.close()
        return result

    def test_root_and_gzip(self):
        status, headers, body = self.request("GET", "/", headers={"Accept-Encoding": "gzip"})
        self.assertEqual(status, 200)
        self.assertEqual(headers.get("Content-Encoding"), "gzip")
        self.assertIn(b"WINGS", gzip.decompress(body))
        self.assertIn(b"<html", gzip.decompress(body))
        status, _, data = self.request("GET", "/", headers={"If-None-Match": headers["ETag"]})
        self.assertEqual(status, 304)
        self.assertEqual(data, b"")

    def test_no_private_paths(self):
        status, _, _ = self.request("GET", "/.git/config")
        self.assertEqual(status, 404)

    def test_two_lan_players(self):
        def state(pid, x):
            return json.dumps({"id": pid, "name": pid, "x": x, "y": 5, "z": 0,
                               "angle": 0, "bank": 0, "flap": 1, "spd": 2}).encode()
        status, _, body = self.request("POST", "/api/state", state("dragon-1111", 0))
        self.assertEqual(status, 200)
        status, _, body = self.request("POST", "/api/state", state("dragon-2222", 5))
        self.assertEqual(status, 200)
        data = json.loads(body)
        self.assertGreaterEqual(data["online"], 2)
        self.assertIn("dragon-1111", [player["id"] for player in data["players"]])

    def test_health(self):
        status, _, body = self.request("GET", "/health")
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body)["status"], "ok")


if __name__ == "__main__":
    unittest.main()
