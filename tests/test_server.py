"""Actual loopback HTTP boundary checks; no browser or Manim subprocesses."""
import ast
import hashlib
import http.client
import json
from pathlib import Path
import threading
import tempfile
import shutil
import unittest
from unittest import mock

from mathlab.server import Handler, ThreadingHTTPServer, canonical, decode_request, MAX_BODY
from mathlab import server as service


class DecodeControls(unittest.TestCase):
    def test_healthy_numeric_request(self):
        self.assertEqual(decode_request(b'{"lesson":"linear","params":{"a":0}}')['params'], {'a': 0})

    def test_invalid_changed_requests_have_healthy_twin(self):
        for raw in (b'', b'[]', b'{"lesson":"linear","code":"execute"}',
                    b'{"lesson":"linear","lesson":"derivative"}',
                    b'{"lesson":"linear","params":{"a":NaN}}',
                    b'{"lesson":"linear","params":{"a":true}}',
                    b'{"lesson":"linear","params":{"a":"1"}}',
                    b'{"lesson":"linear","params":{"a":1e309}}',
                    b'x' * (MAX_BODY + 1), b'\xff'):
            with self.subTest(raw=raw[:70]), self.assertRaises(ValueError):
                decode_request(raw)
        self.assertEqual(decode_request(b'{"lesson":"linear"}'), {'lesson': 'linear', 'params': {}})

    def test_source_identity_refuses_changed_disk_bytes_for_already_loaded_models(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'mathlab').mkdir()
            for name in service._PRODUCERS:
                shutil.copy2(service.ROOT / 'mathlab' / name, root / 'mathlab' / name)
            with mock.patch.object(service, 'ROOT', root):
                self.assertEqual(service.verify_producers(), service._PRODUCER_SHA)
                target = root / 'mathlab' / 'kernel.py'
                target.write_bytes(target.read_bytes() + b'\n# changed after module load\n')
                with self.assertRaises(service.ModelSourceChanged):
                    service.evaluate_request({'lesson': 'linear', 'params': {}})


class QuietHandler(Handler):
    def log_message(self, *_args):
        pass


class HTTPControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), QuietHandler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=3)

    def request(self, method, path, body=None, headers=None):
        connection = http.client.HTTPConnection('127.0.0.1', self.server.server_port, timeout=10)
        headers = headers or {}
        if body is not None and not isinstance(body, bytes):
            body = canonical(body)
            headers = {'Content-Type': 'application/json', **headers}
        connection.request(method, path, body=body, headers=headers)
        response = connection.getresponse()
        result = (response.status, dict(response.getheaders()), response.read())
        connection.close()
        return result

    def test_health_and_catalog_are_real(self):
        status, headers, data = self.request('GET', '/api/health')
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(data)['name'], 'x3d.mathlab')
        self.assertEqual(headers['X-Content-Type-Options'], 'nosniff')
        status, _, data = self.request('GET', '/api/catalog')
        self.assertEqual(status, 200)
        self.assertEqual(len(json.loads(data)['lessons']), 6)

    def test_every_default_model_has_matching_export_identity(self):
        for lesson in ('linear', 'derivative', 'integral', 'fourier', 'lorenz', 'gradient'):
            with self.subTest(lesson=lesson):
                status, _, raw = self.request('POST', '/api/evaluate', {'lesson': lesson})
                self.assertEqual(status, 200, raw[:300])
                payload = json.loads(raw)
                self.assertEqual(payload['sample']['lesson'], lesson)
                self.assertIn('<X3D', payload['x3d'])
                self.assertEqual(hashlib.sha256(payload['x3d'].encode()).hexdigest(), payload['identity']['x3d_sha256'])
                again = self.request('POST', '/api/evaluate', {'lesson': lesson})
                self.assertEqual(raw, again[2])

    def test_refused_models_and_inputs_do_not_replace_a_healthy_result(self):
        for body in ({'lesson': '__import__'}, {'lesson': 'linear', 'params': {'a': 100000}},
                     {'lesson': 'integral', 'params': {'n': 2.5}},
                     {'lesson': 'fourier', 'params': {'terms': 2, 'unknown': 1}}):
            self.assertEqual(self.request('POST', '/api/evaluate', body)[0], 400)
        self.assertEqual(self.request('POST', '/api/evaluate', {'lesson': 'linear'})[0], 200)

    def test_origin_host_size_and_content_type_refusals(self):
        self.assertEqual(self.request('GET', '/api/health', headers={'Host': 'other.example'})[0], 403)
        self.assertEqual(self.request('POST', '/api/evaluate', {'lesson': 'linear'}, {'Origin': 'https://other.example'})[0], 403)
        self.assertEqual(self.request('POST', '/api/evaluate', b'x', {'Content-Type': 'text/plain'})[0], 415)
        self.assertEqual(self.request('POST', '/api/evaluate', b'x' * (MAX_BODY + 1), {'Content-Type': 'application/json'})[0], 413)
        self.assertEqual(self.request('POST', '/api/evaluate', b'{"lesson":"linear","params":{"a":NaN}}', {'Content-Type': 'application/json'})[0], 400)

    def test_static_routes_cannot_read_source_outside_their_declared_roots(self):
        self.assertEqual(self.request('GET', '/../../pyproject.toml')[0], 404)
        self.assertEqual(self.request('GET', '/docs/%2e%2e/pyproject.toml')[0], 404)
        self.assertEqual(self.request('GET', '/src/manim_mcp/server.py')[0], 404)
        self.assertEqual(self.request('POST', '/api/execute', {'lesson': 'linear'})[0], 404)

    def test_manim_endpoint_generates_source_without_executing_it(self):
        status, _, raw = self.request('POST', '/api/manim', {'lesson': 'fourier', 'params': {'terms': 3}})
        self.assertEqual(status, 200, raw[:300])
        result = json.loads(raw)
        tree = ast.parse(result['source'])
        self.assertIn('MathlabScene', [node.name for node in tree.body if isinstance(node, ast.ClassDef)])
        self.assertIn('does not execute', result['scope'])


if __name__ == '__main__':
    unittest.main()
