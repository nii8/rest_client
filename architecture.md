# aust SDK 架构设计

## 包结构

```
aust/
├── aust/
│   ├── __init__.py      # 暴露 Client 类
│   ├── client.py        # 核心逻辑，Client 类
│   └── exception.py     # 输入校验 + 异常处理
├── setup.py
└── tests/
    ├── __init__.py
    ├── mock_server.py   # 模拟远端服务，Flask，端口5500
    └── test_client.py   # 测试用例
```

## 接口约定

| 功能 | 方法 | 路径 | 参数 |
|------|------|------|------|
| 上传 | POST | /upload | query: path, body: multipart file字段名file |
| 下载 | GET  | /download | query: path，响应为二进制流 |
| 陈列 | GET  | /list | query: path |

## 核心设计

- 一个 `Client` 类，构造函数接收可选的 `base_url`，默认 `http://127.0.0.1:5500`
- 3 个方法：`upload`、`download`、`list_files`
- 每个方法先做输入校验，校验失败直接返回统一错误结构，不调用接口
- 调用接口后统一处理 HTTP 错误和网络异常，不让 traceback 暴露给用户

## 统一返回结构

```python
# 成功
{"ok": True, "data": <response对象>}

# 失败
{"ok": False, "error": "错误描述"}
```

## exception.py 职责

两个函数：

**validate_remote_path(remote_path)**
- 路径为 None 或空字符串，返回 "路径不合法：路径不能为空"
- 路径含空格，返回 "路径不合法：不能含有空格"
- 路径不以 `/aa/bb/cc/` 开头，返回 "路径不合法：必须以 /aa/bb/cc/ 开头"
- 按顺序检测，空字符串 > 空格 > 前缀，优先返回第一个命中的错误
- 合法返回 None

**handle_response(response)**
- `200 <= status_code < 300`：返回 `{"ok": True, "data": response}`
- 其他所有状态码（3xx、4xx、5xx）：打印 `错误码: {status_code}，错误信息: {response.text}`，返回 `{"ok": False, "error": response.text}`

## client.py 每个方法的处理流程

```
输入校验（validate_remote_path）
  → 失败：打印提示，返回 {"ok": False, "error": "..."}
  → 通过：调用 requests
      → 网络异常（ConnectionError）：打印 "无法连接服务: {base_url}"，返回 {"ok": False, "error": "无法连接服务"}
      → 有响应：交给 handle_response 处理
```

**upload 额外校验：**
- 本地文件不存在 → 打印提示，返回错误结构，不调用接口

**download 额外处理：**
- 目标目录不存在 → 自动创建（`os.makedirs`）
- handle_response 返回 ok 为 True 时，把 response.content 写入本地文件

## 用户使用方式

```python
from aust import Client

c = Client()  # 或 Client("http://my-server:8080")

result = c.upload("/aa/bb/cc/file.txt", "/local/file.txt")
if result["ok"]:
    print("上传成功")

result = c.download("/aa/bb/cc/file.txt", "/local/save/file.txt")
result = c.list_files("/aa/bb/cc/")
```

## 安装与更新

**首次安装（开发模式，本地直接用）：**
```bash
cd aust
pip install -e .
```

**打包发布到 PyPI：**
```bash
pip install build twine
python -m build
twine upload dist/*
```

**用户通过 pip 安装：**
```bash
pip install aust
```

**更新包版本：**
1. 修改 `setup.py` 里的 `version` 字段
2. 重新打包发布：
```bash
python -m build
twine upload dist/*
```

**用户更新到最新版：**
```bash
pip install --upgrade aust
```

## 运行测试

测试文件在 `tests/` 目录，包含单元测试和集成测试，集成测试会自动在线程里启动 mock_server，无需手动启动服务。

**运行全部测试：**
```bash
cd aust
python -m unittest tests/test_client.py -v
```

**只跑单元测试（不需要服务）：**
```bash
python -m unittest tests.test_client.TestValidateRemotePath tests.test_client.TestHandleResponse -v
```

**只跑集成测试：**
```bash
python -m unittest tests.test_client.TestClientIntegration -v
```

**单独手动启动 mock_server（调试用）：**
```bash
python tests/mock_server.py
```

## 测试设计

### mock_server.py

用 Flask 实现，端口 5500，文件存放在 `tests/storage/` 目录，测试结束后自动清理。
提供 `GET /health` 健康检查接口，返回 200，供测试启动时轮询等待服务就绪。

实现路由：
- `GET /health` — 健康检查，返回 200
- `POST /upload?path=<remote_path>` — 接收 multipart file 字段，按 path 存到 storage 目录，自动创建目录，缺少 file 字段返回 400
- `GET /download?path=<remote_path>` — 从 storage 读文件返回二进制流，文件不存在返回 404
- `GET /list?path=<remote_path>` — 列出 storage 对应目录的文件名，返回 `{"files": [...]}`，目录不存在返回 404

### test_client.py

分两层，单元测试和集成测试放在同一文件。

**单元测试（不启动服务，直接调函数）**

- UT-01 validate_remote_path：传空字符串 → 返回错误信息
- UT-02 validate_remote_path：传 None → 返回错误信息
- UT-03 validate_remote_path：路径不以 `/aa/bb/cc/` 开头 → 返回错误信息
- UT-04 validate_remote_path：路径含空格 → 返回错误信息
- UT-05 validate_remote_path：含空格且前缀错误 → 优先返回空格错误
- UT-06 validate_remote_path：合法路径 `/aa/bb/cc/file.txt` → 返回 None
- UT-07 validate_remote_path：只有前缀 `/aa/bb/cc/` → 返回 None
- UT-08 handle_response：status_code=200 → `{"ok": True, "data": response}`
- UT-09 handle_response：status_code=201 → `{"ok": True, "data": response}`
- UT-10 handle_response：status_code=301 → `{"ok": False, "error": ...}`
- UT-11 handle_response：status_code=400 → `{"ok": False, "error": ...}`
- UT-12 handle_response：status_code=404 → `{"ok": False, "error": ...}`
- UT-13 handle_response：status_code=500 → `{"ok": False, "error": ...}`

**集成测试（自动启动 mock_server）**

setUpClass 用线程启动 Flask，轮询 `/health` 确认就绪后再跑测试。
tearDownClass 清理 storage 目录和所有临时文件。

- IT-01 默认 base_url：构造 `Client()`，断言 `base_url == "http://127.0.0.1:5500"`
- IT-02 自定义 base_url：构造 `Client("http://myserver:9000")`，断言正确保存
- IT-03 upload/download/list_files 传路径前缀错误 → 各返回 `{"ok": False}`，不发请求
- IT-04 upload/download/list_files 传路径含空格 → 各返回 `{"ok": False}`，不发请求
- IT-05 upload 本地文件不存在 → 返回 `{"ok": False}`
- IT-06 upload 正常上传 → 返回 `{"ok": True}`，storage 里存在文件且内容一致
- IT-07 upload 服务端返回 400（不带 file 字段触发）→ 返回 `{"ok": False}`，error 含服务端错误信息
- IT-08 download 正常下载 → 返回 `{"ok": True}`，本地文件内容与上传一致，result["data"] 是 response 对象
- IT-09 download 目标目录不存在 → 自动创建目录，文件写入成功，用 `tempfile.mkdtemp()` 构造路径
- IT-10 download 远端文件不存在 → 返回 `{"ok": False}`，error 含服务端错误信息，本地不产生文件
- IT-11 list_files 正常陈列 → 返回 `{"ok": True}`，result["data"].json()["files"] 包含已上传文件名
- IT-12 list_files 路径不存在 → 返回 `{"ok": False}`，error 含服务端错误信息
- IT-13 服务未启动（无效端口）→ 返回 `{"ok": False}`，error 含连接失败提示，无 traceback
