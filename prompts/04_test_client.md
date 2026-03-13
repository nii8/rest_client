【粘贴 00_master.md 内容】

实现文件：tests/test_client.py

硬性要求：
- 不使用 mock、不使用 threading、不使用 tempfile、不使用 setUp/tearDown、不使用测试类
- 只写普通函数，每个函数测一件事
- 用 open() 直接创建和读取文件，不用任何封装
- handle_response 的测试用文件内定义的 FakeResponse 类，不用 mock
- 运行测试前需手动启动服务：python tests/mock_server.py

文件顶部固定内容：
import os
import sys
import shutil
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from 【包名】 import Client
from 【包名】.exception import validate_remote_path, handle_response

BASE_URL = "http://127.0.0.1:【端口】"
client = Client(BASE_URL)

class FakeResponse:
    def __init__(self, status_code, text="error"):
        self.status_code = status_code
        self.text = text

实现以下 25 个测试函数：

# ── 路径校验 ──
def test_01_validate_empty():
    assert validate_remote_path("") is not None

def test_02_validate_none():
    assert validate_remote_path(None) is not None

def test_03_validate_wrong_prefix():
    result = validate_remote_path("/wrong/path/file.txt")
    assert result is not None and "开头" in result

def test_04_validate_has_space():
    result = validate_remote_path("【路径前缀】my file.txt")
    assert result is not None and "空格" in result

def test_05_validate_space_beats_prefix():
    result = validate_remote_path("/wrong/my file.txt")
    assert result is not None and "空格" in result

def test_06_validate_valid():
    assert validate_remote_path("【路径前缀】file.txt") is None

def test_07_validate_prefix_only():
    assert validate_remote_path("【路径前缀】") is None

# ── handle_response ──
def test_08_handle_response_200():
    r = FakeResponse(200)
    result = handle_response(r)
    assert result["ok"] == True and result["data"] is r

def test_09_handle_response_201():
    assert handle_response(FakeResponse(201))["ok"] == True

def test_10_handle_response_301():
    assert handle_response(FakeResponse(301))["ok"] == False

def test_11_handle_response_400():
    assert handle_response(FakeResponse(400))["ok"] == False

def test_12_handle_response_404():
    r = FakeResponse(404, "not found")
    result = handle_response(r)
    assert result["ok"] == False and result["error"] == "not found"

def test_13_handle_response_500():
    assert handle_response(FakeResponse(500))["ok"] == False

# ── Client 基本 ──
def test_14_default_base_url():
    c = Client()
    assert c.base_url == "http://127.0.0.1:【端口】"

def test_15_custom_base_url():
    c = Client("http://myserver:9000")
    assert c.base_url == "http://myserver:9000"

# ── 上传 ──
def test_16_upload_local_not_exist():
    result = client.【上传方法名】("【路径前缀】x.txt", "/not/exist/file.txt")
    assert result["ok"] == False

def test_17_upload_success():
    with open("tmp_upload.txt", "w") as f:
        f.write("hello test")
    result = client.【上传方法名】("【路径前缀】test_upload.txt", "tmp_upload.txt")
    assert result["ok"] == True
    os.remove("tmp_upload.txt")

# ── 下载 ──
def test_18_download_success():
    result = client.【下载方法名】("【路径前缀】test_upload.txt", "tmp_download.txt")
    assert result["ok"] == True
    with open("tmp_download.txt", "r") as f:
        assert f.read() == "hello test"
    os.remove("tmp_download.txt")

def test_19_download_auto_create_dir():
    result = client.【下载方法名】("【路径前缀】test_upload.txt", "tmp_subdir/sub/out.txt")
    assert result["ok"] == True
    assert os.path.exists("tmp_subdir/sub/out.txt")
    shutil.rmtree("tmp_subdir")

def test_20_download_remote_not_exist():
    result = client.【下载方法名】("【路径前缀】nonexistent.txt", "tmp_download.txt")
    assert result["ok"] == False and "error" in result

# ── 列表 ──
def test_21_list_success():
    result = client.【列表方法名】("【路径前缀】")
    assert result["ok"] == True
    assert "test_upload.txt" in result["data"].json()["files"]

def test_22_list_not_exist():
    result = client.【列表方法名】("【路径前缀】nonexistent/")
    assert result["ok"] == False and "error" in result

# ── 连接失败 ──
def test_23_connection_refused_upload():
    c = Client("http://127.0.0.1:19999")
    with open("tmp_conn.txt", "w") as f:
        f.write("x")
    result = c.【上传方法名】("【路径前缀】x.txt", "tmp_conn.txt")
    assert result["ok"] == False and "无法连接服务" in result["error"]
    os.remove("tmp_conn.txt")

def test_24_connection_refused_download():
    c = Client("http://127.0.0.1:19999")
    result = c.【下载方法名】("【路径前缀】x.txt", "tmp_conn_dl.txt")
    assert result["ok"] == False and "无法连接服务" in result["error"]

def test_25_connection_refused_list():
    c = Client("http://127.0.0.1:19999")
    result = c.【列表方法名】("【路径前缀】")
    assert result["ok"] == False and "无法连接服务" in result["error"]

末尾加：
if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            print(f"运行 {name} ...", end=" ")
            try:
                fn()
                print("通过")
            except Exception as e:
                print(f"失败: {e}")
