# aust SDK 架构设计

## 包结构

```
aust/
├── aust/
│   ├── __init__.py      # 暴露 Client 类
│   └── client.py        # 核心逻辑，Client 类
├── setup.py
└── README.md
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
- 每个方法用 `requests` 调接口，原样返回 `response` 对象
- 无异常捕获、无数据转换、无重试、无日志

## 用户使用方式

```python
from aust import Client

c = Client()  # 或 Client("http://my-server:8080")
c.upload("/remote/dir/file.txt", "/local/file.txt")
c.download("/remote/dir/file.txt", "/local/save/file.txt")
c.list_files("/remote/dir/")
```

## 测试用例设计

测试文件：`tests/test_client.py`，用 `unittest` + `unittest.mock` mock 掉 `requests`，不依赖真实服务。

### TC-01 默认 base_url

- 构造 `Client()`，断言内部 `base_url == "http://127.0.0.1:5500"`

### TC-02 自定义 base_url

- 构造 `Client("http://myserver:9000")`，断言内部 `base_url == "http://myserver:9000"`

### TC-03 upload 发送正确请求

- mock `requests.post` 返回假 response
- 调用 `upload("/remote/a.txt", "local.txt")`（本地文件用 `tmp_path` 创建）
- 断言 `requests.post` 被调用，URL 含 `?path=/remote/a.txt`，files 参数含字段 `file`
- 断言返回值就是 mock 的 response 对象

### TC-04 download 写入本地文件

- mock `requests.get` 返回 `content = b"hello"`
- 调用 `download("/remote/a.txt", "local_out.txt")`
- 断言本地文件内容为 `b"hello"`
- 断言 URL 含 `?path=/remote/a.txt`

### TC-05 list_files 返回 response

- mock `requests.get` 返回假 response
- 调用 `list_files("/remote/dir/")`
- 断言 URL 含 `?path=/remote/dir/`
- 断言返回值就是 mock 的 response 对象
