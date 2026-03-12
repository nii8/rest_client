import unittest
from unittest.mock import patch, MagicMock
import tempfile
import os

from aust import Client


class TestClient(unittest.TestCase):

    def test_01_default_base_url(self):
        c = Client()
        self.assertEqual(c.base_url, "http://127.0.0.1:5500")

    def test_02_custom_base_url(self):
        c = Client("http://myserver:9000")
        self.assertEqual(c.base_url, "http://myserver:9000")

    @patch("aust.client.requests.post")
    def test_03_upload(self, mock_post):
        mock_response = MagicMock()
        mock_post.return_value = mock_response

        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b"data")
            tmp_path = tmp.name

        try:
            c = Client()
            result = c.upload("/remote/a.txt", tmp_path)
            call_kwargs = mock_post.call_args
            self.assertIn("path=/remote/a.txt", call_kwargs[1]["params"]["path"] if "params" in call_kwargs[1] else call_kwargs[0][0])
            self.assertIn("file", call_kwargs[1]["files"])
            self.assertEqual(result, mock_response)
        finally:
            os.unlink(tmp_path)

    @patch("aust.client.requests.get")
    def test_04_download(self, mock_get):
        mock_response = MagicMock()
        mock_response.content = b"hello"
        mock_get.return_value = mock_response

        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            out_path = tmp.name

        try:
            c = Client()
            c.download("/remote/a.txt", out_path)
            self.assertEqual(mock_get.call_args[1]["params"]["path"], "/remote/a.txt")
            with open(out_path, "rb") as f:
                self.assertEqual(f.read(), b"hello")
        finally:
            os.unlink(out_path)

    @patch("aust.client.requests.get")
    def test_05_list_files(self, mock_get):
        mock_response = MagicMock()
        mock_get.return_value = mock_response

        c = Client()
        result = c.list_files("/remote/dir/")
        self.assertEqual(mock_get.call_args[1]["params"]["path"], "/remote/dir/")
        self.assertEqual(result, mock_response)


if __name__ == "__main__":
    unittest.main()
