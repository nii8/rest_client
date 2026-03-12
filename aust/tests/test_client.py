import os
import sys
import shutil
import tempfile
import threading
import time
import unittest
from unittest.mock import MagicMock

import requests

# 让测试能找到 aust 包
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from aust import Client
from aust.exception import validate_remote_path, handle_response
import tests.mock_server as mock_server_module

TESTS_DIR = os.path.dirname(__file__)
STORAGE_DIR = os.path.join(TESTS_DIR, "storage")
BASE_URL = "http://127.0.0.1:5500"


def start_mock_server():
    mock_server_module.app.run(port=5500, use_reloader=False)


def wait_for_server(timeout=5):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            r = requests.get(f"{BASE_URL}/health")
            if r.status_code == 200:
                return True
        except Exception:
            pass
        time.sleep(0.1)
    raise RuntimeError("mock_server 启动超时")


# ─────────────────────────────────────────────
# 单元测试：不依赖服务
# ─────────────────────────────────────────────

class TestValidateRemotePath(unittest.TestCase):

    def test_ut01_empty_string(self):
        self.assertIsNotNone(validate_remote_path(""))

    def test_ut02_none(self):
        self.assertIsNotNone(validate_remote_path(None))

    def test_ut03_wrong_prefix(self):
        result = validate_remote_path("/wrong/path/file.txt")
        self.assertIsNotNone(result)
        self.assertIn("开头", result)

    def test_ut04_has_space(self):
        result = validate_remote_path("/aa/bb/cc/my file.txt")
        self.assertIsNotNone(result)
        self.assertIn("空格", result)

    def test_ut05_space_takes_priority_over_prefix(self):
        result = validate_remote_path("/wrong/my file.txt")
        self.assertIsNotNone(result)
        self.assertIn("空格", result)

    def test_ut06_valid_path(self):
        self.assertIsNone(validate_remote_path("/aa/bb/cc/file.txt"))

    def test_ut07_prefix_only(self):
        self.assertIsNone(validate_remote_path("/aa/bb/cc/"))


class TestHandleResponse(unittest.TestCase):

    def _mock_response(self, status_code, text="some error"):
        r = MagicMock()
        r.status_code = status_code
        r.text = text
        return r

    def test_ut08_200(self):
        r = self._mock_response(200)
        result = handle_response(r)
        self.assertTrue(result["ok"])
        self.assertEqual(result["data"], r)

    def test_ut09_201(self):
        r = self._mock_response(201)
        result = handle_response(r)
        self.assertTrue(result["ok"])

    def test_ut10_301(self):
        r = self._mock_response(301)
        result = handle_response(r)
        self.assertFalse(result["ok"])

    def test_ut11_400(self):
        r = self._mock_response(400)
        result = handle_response(r)
        self.assertFalse(result["ok"])

    def test_ut12_404(self):
        r = self._mock_response(404, "not found")
        result = handle_response(r)
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"], "not found")

    def test_ut13_500(self):
        r = self._mock_response(500)
        result = handle_response(r)
        self.assertFalse(result["ok"])


# ─────────────────────────────────────────────
# 集成测试：依赖 mock_server
# ─────────────────────────────────────────────

class TestClientIntegration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        t = threading.Thread(target=start_mock_server, daemon=True)
        t.start()
        wait_for_server()
        cls.client = Client(BASE_URL)
        cls.tmp_files = []

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(STORAGE_DIR):
            shutil.rmtree(STORAGE_DIR)
        for f in cls.tmp_files:
            if os.path.exists(f):
                os.remove(f)

    def _tmp_file(self, content=b""):
        fd, path = tempfile.mkstemp()
        os.write(fd, content)
        os.close(fd)
        self.tmp_files.append(path)
        return path

    def test_it01_default_base_url(self):
        c = Client()
        self.assertEqual(c.base_url, "http://127.0.0.1:5500")

    def test_it02_custom_base_url(self):
        c = Client("http://myserver:9000")
        self.assertEqual(c.base_url, "http://myserver:9000")

    def test_it03_wrong_prefix_all_methods(self):
        path = "/wrong/path/file.txt"
        local = self._tmp_file(b"x")
        out = self._tmp_file()
        self.assertFalse(self.client.upload(path, local)["ok"])
        self.assertFalse(self.client.download(path, out)["ok"])
        self.assertFalse(self.client.list_files(path)["ok"])

    def test_it04_space_in_path_all_methods(self):
        path = "/aa/bb/cc/my file.txt"
        local = self._tmp_file(b"x")
        out = self._tmp_file()
        self.assertFalse(self.client.upload(path, local)["ok"])
        self.assertFalse(self.client.download(path, out)["ok"])
        self.assertFalse(self.client.list_files(path)["ok"])

    def test_it05_upload_local_file_not_exist(self):
        result = self.client.upload("/aa/bb/cc/file.txt", "/nonexistent/path/file.txt")
        self.assertFalse(result["ok"])

    def test_it06_upload_success(self):
        local = self._tmp_file(b"hello upload")
        result = self.client.upload("/aa/bb/cc/test_upload.txt", local)
        self.assertTrue(result["ok"])
        stored = os.path.join(STORAGE_DIR, "aa/bb/cc/test_upload.txt")
        self.assertTrue(os.path.exists(stored))
        with open(stored, "rb") as f:
            self.assertEqual(f.read(), b"hello upload")

    def test_it07_upload_server_400(self):
        # 直接发不带 file 字段的请求触发 400
        response = requests.post(f"{BASE_URL}/upload", params={"path": "/aa/bb/cc/x.txt"})
        self.assertEqual(response.status_code, 400)
        # 通过 handle_response 验证 SDK 会返回 ok=False
        result = handle_response(response)
        self.assertFalse(result["ok"])
        self.assertIn("缺少文件", response.json()["error"])

    def test_it08_download_success(self):
        local = self._tmp_file(b"hello download")
        self.client.upload("/aa/bb/cc/test_download.txt", local)
        out = self._tmp_file()
        result = self.client.download("/aa/bb/cc/test_download.txt", out)
        self.assertTrue(result["ok"])
        self.assertIn("data", result)
        with open(out, "rb") as f:
            self.assertEqual(f.read(), b"hello download")

    def test_it09_download_auto_create_dir(self):
        local = self._tmp_file(b"dir test")
        self.client.upload("/aa/bb/cc/dir_test.txt", local)
        base = tempfile.mkdtemp()
        out = os.path.join(base, "sub1", "sub2", "out.txt")
        result = self.client.download("/aa/bb/cc/dir_test.txt", out)
        self.assertTrue(result["ok"])
        self.assertTrue(os.path.exists(out))
        shutil.rmtree(base)

    def test_it10_download_remote_not_exist(self):
        out = self._tmp_file()
        result = self.client.download("/aa/bb/cc/nonexistent.txt", out)
        self.assertFalse(result["ok"])
        self.assertIn("error", result)
        # 下载失败不应写入文件内容（文件大小为0或不存在）
        self.assertEqual(os.path.getsize(out), 0)

    def test_it11_list_files_success(self):
        self.client.upload("/aa/bb/cc/list_test/a.txt", self._tmp_file(b"a"))
        self.client.upload("/aa/bb/cc/list_test/b.txt", self._tmp_file(b"b"))
        result = self.client.list_files("/aa/bb/cc/list_test/")
        self.assertTrue(result["ok"])
        files = result["data"].json()["files"]
        self.assertIn("a.txt", files)
        self.assertIn("b.txt", files)

    def test_it12_list_files_not_exist(self):
        result = self.client.list_files("/aa/bb/cc/nonexistent/")
        self.assertFalse(result["ok"])
        self.assertIn("error", result)

    def test_it13_connection_refused(self):
        c = Client("http://127.0.0.1:19999")
        local = self._tmp_file(b"x")
        out = self._tmp_file()
        r1 = c.upload("/aa/bb/cc/file.txt", local)
        r2 = c.download("/aa/bb/cc/file.txt", out)
        r3 = c.list_files("/aa/bb/cc/")
        self.assertFalse(r1["ok"])
        self.assertFalse(r2["ok"])
        self.assertFalse(r3["ok"])
        self.assertIn("无法连接服务", r1["error"])
        self.assertIn("无法连接服务", r2["error"])
        self.assertIn("无法连接服务", r3["error"])


if __name__ == "__main__":
    unittest.main()
