用 Python 写一个名为 aust 的 pip 包，完整结构如下：

aust/
├── aust/
│   ├── __init__.py
│   ├── client.py
│   └── exception.py
├── setup.py
└── tests/
    ├── __init__.py      # 空文件，必须存在，让 test_client.py 能 import tests.mock_server
    ├── mock_server.py
    └── test_client.py

---

## 一、exception.py

写两个函数：

### validate_remote_path(remote_path)
- 如果 remote_path 为 None 或空字符串，返回 "路径不合法：路径不能为空"
- 如果 remote_path 含空格，返回 "路径不合法：不能含有空格"
- 如果 remote_path 不以 /aa/bb/cc/ 开头，返回 "路径不合法：必须以 /aa/bb/cc/ 开头"
- 以上按顺序检测，优先返回第一个命中的错误
- 合法返回 None

### handle_response(response)
- 如果 200 <= response.status_code < 300，返回 {"ok": True, "data": response}
- 其他所有状态码（3xx、4xx、5xx），打印 f"错误码: {response.status_code}，错误信息: {response.text}"，返回 {"ok": False, "error": response.text}

---

## 二、client.py

写一个 Client 类：

### __init__(self, base_url="http://127.0.0.1:5500")
- 保存 base_url

### upload(self, remote_path, local_path)
处理流程：
1. 调用 validate_remote_path(remote_path)，不为 None 则打印错误，返回 {"ok": False, "error": 错误信息}
2. 检查 local_path 文件是否存在，不存在则打印 "本地文件不存在: {local_path}"，返回 {"ok": False, "error": "本地文件不存在"}
3. 用 try/except requests.exceptions.ConnectionError 包裹请求，捕获后打印 "无法连接服务: {base_url}"，返回 {"ok": False, "error": "无法连接服务"}
4. POST {base_url}/upload?path={remote_path}，multipart/form-data，字段名 file，二进制读取
5. 返回 handle_response(response)

### download(self, remote_path, local_path)
处理流程：
1. 调用 validate_remote_path(remote_path)，不为 None 则打印错误，返回 {"ok": False, "error": 错误信息}
2. 用 os.makedirs 自动创建 local_path 的父目录（exist_ok=True）
3. 用 try/except requests.exceptions.ConnectionError 包裹请求，捕获后打印 "无法连接服务: {base_url}"，返回 {"ok": False, "error": "无法连接服务"}
4. GET {base_url}/download?path={remote_path}
5. 调用 handle_response(response)，如果结果 ok 为 True，把 response.content 写入 local_path
6. 返回 handle_response 的结果

### list_files(self, remote_path)
处理流程：
1. 调用 validate_remote_path(remote_path)，不为 None 则打印错误，返回 {"ok": False, "error": 错误信息}
2. 用 try/except requests.exceptions.ConnectionError 包裹请求，捕获后打印 "无法连接服务: {base_url}"，返回 {"ok": False, "error": "无法连接服务"}
3. GET {base_url}/list?path={remote_path}
4. 返回 handle_response(response)

---

## 三、__init__.py

只写一行：
from .client import Client

---

## 四、setup.py

包名 aust，依赖 requests 和 flask

---

## 五、tests/mock_server.py

用 Flask 写一个模拟服务，端口 5500，文件存放在与 mock_server.py 同目录的 storage/ 子目录。

storage 路径拼接方式：remote_path 是带 /aa/bb/cc/ 前缀的完整路径，需要先 lstrip("/") 去掉开头斜杠，再用 os.path.join(STORAGE_DIR, path.lstrip("/")) 拼接，否则在 Windows 上会因绝对路径覆盖出错。

实现以下路由：

### GET /health
- 返回 200 + {"status": "ok"}，供测试启动时轮询等待服务就绪

### POST /upload
- 从 query string 取 path 参数
- 从 multipart 取 file 字段，缺少 file 字段返回 400 + {"error": "缺少文件"}
- 把文件保存到 storage/{path} 对应路径，自动创建目录
- 成功返回 200 + {"message": "上传成功"}

### GET /download
- 从 query string 取 path 参数
- 从 storage/{path} 读取文件，返回二进制流
- 文件不存在返回 404 + {"error": "文件不存在"}

### GET /list
- 从 query string 取 path 参数
- 列出 storage/{path} 目录下的文件名列表，返回 {"files": [...]}
- 目录不存在返回 404 + {"error": "路径不存在"}

mock_server.py 可以直接 python mock_server.py 启动，也可以被测试代码以线程方式启动。

---

## 六、tests/test_client.py

用 unittest 写测试，分单元测试和集成测试两部分放在同一个文件里。

集成测试在 setUpClass 里用线程启动 mock_server，启动后轮询 GET /health 直到返回 200 再继续（最多等5秒，超时报错）。
tearDownClass 里清理 storage 目录和所有临时文件。
测试用例之间相互独立，不依赖执行顺序。
临时文件路径用 tempfile 动态生成，不写死路径。

### 单元测试（不启动服务，直接调函数）

UT-01 validate_remote_path 传空字符串 → 返回错误信息字符串
UT-02 validate_remote_path 传 None → 返回错误信息字符串
UT-03 validate_remote_path 路径不以 /aa/bb/cc/ 开头 → 返回错误信息字符串
UT-04 validate_remote_path 路径含空格 → 返回错误信息字符串
UT-05 validate_remote_path 含空格且前缀错误 → 优先返回空格错误
UT-06 validate_remote_path 合法路径 /aa/bb/cc/file.txt → 返回 None
UT-07 validate_remote_path 只有前缀 /aa/bb/cc/ → 返回 None
UT-08 handle_response status_code=200 → {"ok": True, "data": response}
UT-09 handle_response status_code=201 → {"ok": True, "data": response}
UT-10 handle_response status_code=301 → {"ok": False, "error": ...}
UT-11 handle_response status_code=400 → {"ok": False, "error": ...}
UT-12 handle_response status_code=404 → {"ok": False, "error": ...}
UT-13 handle_response status_code=500 → {"ok": False, "error": ...}

### 集成测试（依赖 mock_server）

IT-01 默认 base_url
- 构造 Client()，断言 base_url == "http://127.0.0.1:5500"

IT-02 自定义 base_url
- 构造 Client("http://myserver:9000")，断言 base_url == "http://myserver:9000"

IT-03 三个接口传路径前缀错误
- upload/download/list_files 各传 /wrong/path/file.txt
- 断言每个都返回 {"ok": False}，不发网络请求

IT-04 三个接口传路径含空格
- upload/download/list_files 各传 /aa/bb/cc/my file.txt
- 断言每个都返回 {"ok": False}，不发网络请求

IT-05 upload 本地文件不存在
- 传一个不存在的本地路径，远端路径合法
- 断言返回 {"ok": False}

IT-06 upload 正常上传
- 用 tempfile 创建临时文件，写入 b"hello upload"
- 上传到 /aa/bb/cc/test_upload.txt
- 断言返回 {"ok": True}
- 断言 storage 目录里存在对应文件，内容为 b"hello upload"

IT-07 upload 服务端返回 400
- 直接用 requests.post 不带 file 字段请求 mock_server 的 /upload 接口触发 400
- 注意：不要通过 SDK 的 upload 方法，因为 SDK 永远会带 file 字段
- 拿到 400 的 response 后，调用 handle_response(response) 验证返回 {"ok": False}
- 断言 response.json()["error"] 含服务端错误信息（用 response.json() 解析，不要用 response.text 做字符串匹配，因为 Flask 返回的是 unicode 转义格式）

IT-08 download 正常下载
- 先上传 b"hello download" 到 /aa/bb/cc/test_download.txt
- 用 tempfile 生成本地输出路径，下载
- 断言返回 {"ok": True}，result["data"] 是 response 对象
- 断言本地文件内容 == b"hello download"

IT-09 download 目标目录不存在自动创建
- 用 tempfile.mkdtemp() 生成基础目录，拼接多级子目录作为输出路径
- 先上传一个文件，再下载到该路径
- 断言目录被自动创建，文件写入成功

IT-10 download 远端文件不存在
- 用 tempfile.mkstemp() 创建一个空的本地临时文件作为输出路径（初始大小为 0）
- 下载一个没有上传过的路径 /aa/bb/cc/nonexistent.txt
- 断言返回 {"ok": False}，error 含服务端错误信息
- 断言本地文件大小仍为 0（下载失败不写入内容）

IT-11 list_files 正常陈列
- 先上传两个文件到 /aa/bb/cc/list_test/ 目录
- 调用 list_files("/aa/bb/cc/list_test/")
- 断言返回 {"ok": True}
- 断言 result["data"].json()["files"] 包含两个上传的文件名

IT-12 list_files 路径不存在
- list 一个没有上传过文件的路径 /aa/bb/cc/nonexistent/
- 断言返回 {"ok": False}，error 含服务端错误信息

IT-13 服务未启动连接失败
- 构造 Client("http://127.0.0.1:19999")
- 分别调用 upload/download/list_files，传合法路径
- 断言每个都返回 {"ok": False}，error 含连接失败提示

---

代码要求：
- 简单直接，逻辑清晰
- 不要在 except 里打印 traceback
- 每个方法保持可读，不超过 15 行
- 测试用例之间相互独立，不依赖执行顺序
