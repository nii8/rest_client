import os
import sys
import shutil

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from aust import Client
from aust.exception import validate_remote_path, handle_response

BASE_URL = "http://127.0.0.1:5500"
client = Client(BASE_URL)


# 用于测试 handle_response 的简单假响应，不需要 mock
class FakeResponse:
    def __init__(self, status_code, text="error"):
        self.status_code = status_code
        self.text = text


# ── 路径校验 ──────────────────────────────────────

def test_01_validate_empty():
    assert validate_remote_path("") is not None

def test_02_validate_none():
    assert validate_remote_path(None) is not None

def test_03_validate_wrong_prefix():
    result = validate_remote_path("/wrong/path/file.txt")
    assert result is not None and "开头" in result

def test_04_validate_has_space():
    result = validate_remote_path("/aa/bb/cc/my file.txt")
    assert result is not None and "空格" in result

def test_05_validate_space_beats_prefix():
    # 同时有空格和前缀错误，应该优先报空格
    result = validate_remote_path("/wrong/my file.txt")
    assert result is not None and "空格" in result

def test_06_validate_valid():
    assert validate_remote_path("/aa/bb/cc/file.txt") is None

def test_07_validate_prefix_only():
    # 只有前缀本身也是合法路径
    assert validate_remote_path("/aa/bb/cc/") is None


# ── handle_response ───────────────────────────────

def test_08_handle_response_200():
    r = FakeResponse(200)
    result = handle_response(r)
    assert result["ok"] == True and result["data"] is r

def test_09_handle_response_201():
    result = handle_response(FakeResponse(201))
    assert result["ok"] == True

def test_10_handle_response_301():
    result = handle_response(FakeResponse(301))
    assert result["ok"] == False

def test_11_handle_response_400():
    result = handle_response(FakeResponse(400))
    assert result["ok"] == False

def test_12_handle_response_404():
    r = FakeResponse(404, "not found")
    result = handle_response(r)
    assert result["ok"] == False and result["error"] == "not found"

def test_13_handle_response_500():
    result = handle_response(FakeResponse(500))
    assert result["ok"] == False


# ── Client 基本 ───────────────────────────────────

def test_14_default_base_url():
    c = Client()
    assert c.base_url == "http://127.0.0.1:5500"

def test_15_custom_base_url():
    c = Client("http://myserver:9000")
    assert c.base_url == "http://myserver:9000"


# ── 上传 ──────────────────────────────────────────

def test_16_upload_local_not_exist():
    result = client.upload("/aa/bb/cc/x.txt", "/not/exist/file.txt")
    assert result["ok"] == False

def test_17_upload_success():
    with open("tmp_upload.txt", "w") as f:
        f.write("hello test")
    result = client.upload("/aa/bb/cc/test_upload.txt", "tmp_upload.txt")
    assert result["ok"] == True
    os.remove("tmp_upload.txt")


# ── 下载 ──────────────────────────────────────────

def test_18_download_success():
    result = client.download("/aa/bb/cc/test_upload.txt", "tmp_download.txt")
    assert result["ok"] == True
    with open("tmp_download.txt", "r") as f:
        assert f.read() == "hello test"
    os.remove("tmp_download.txt")

def test_19_download_auto_create_dir():
    # 目标目录不存在，应该自动创建
    result = client.download("/aa/bb/cc/test_upload.txt", "tmp_subdir/sub/out.txt")
    assert result["ok"] == True
    assert os.path.exists("tmp_subdir/sub/out.txt")
    shutil.rmtree("tmp_subdir")

def test_20_download_remote_not_exist():
    result = client.download("/aa/bb/cc/nonexistent.txt", "tmp_download.txt")
    assert result["ok"] == False and "error" in result


# ── 列表 ──────────────────────────────────────────

def test_21_list_success():
    result = client.list_files("/aa/bb/cc/")
    assert result["ok"] == True
    assert "test_upload.txt" in result["data"].json()["files"]

def test_22_list_not_exist():
    result = client.list_files("/aa/bb/cc/nonexistent/")
    assert result["ok"] == False and "error" in result


# ── 连接失败 ──────────────────────────────────────

def test_23_connection_refused_upload():
    c = Client("http://127.0.0.1:19999")
    with open("tmp_conn.txt", "w") as f:
        f.write("x")
    result = c.upload("/aa/bb/cc/x.txt", "tmp_conn.txt")
    assert result["ok"] == False and "无法连接服务" in result["error"]
    os.remove("tmp_conn.txt")

def test_24_connection_refused_download():
    c = Client("http://127.0.0.1:19999")
    result = c.download("/aa/bb/cc/x.txt", "tmp_conn_dl.txt")
    assert result["ok"] == False and "无法连接服务" in result["error"]

def test_25_connection_refused_list():
    c = Client("http://127.0.0.1:19999")
    result = c.list_files("/aa/bb/cc/")
    assert result["ok"] == False and "无法连接服务" in result["error"]


# ─────────────────────────────────────────────────

if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            print(f"运行 {name} ...", end=" ")
            try:
                fn()
                print("通过")
            except Exception as e:
                print(f"失败: {e}")
