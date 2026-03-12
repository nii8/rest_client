用 Python 写一个名为 aust 的 pip 包，结构如下：

aust/
├── aust/
│   ├── __init__.py
│   └── client.py
├── setup.py

要求：

1. client.py 里写一个 Client 类
   - __init__(self, base_url="http://127.0.0.1:5500") 接收 base_url
   - 3 个方法，全部原样返回 requests 的 response 对象，不做任何处理

2. upload(self, remote_path, local_path)
   - POST {base_url}/upload?path={remote_path}
   - 用 multipart/form-data 上传本地文件，字段名为 file
   - 打开 local_path 文件，以二进制读取上传

3. download(self, remote_path, local_path)
   - GET {base_url}/download?path={remote_path}
   - 把响应的二进制内容写入 local_path 文件

4. list_files(self, remote_path)
   - GET {base_url}/list?path={remote_path}
   - 直接返回 response

5. __init__.py 只做一件事：from .client import Client

6. setup.py 包名 aust，依赖只有 requests

代码要求：简单直接，不要封装异常，不要加重试，不要加日志，不要类型注解，每个方法不超过 5 行。

7. 同时在 tests/test_client.py 写测试用例，用 unittest + unittest.mock，不依赖真实服务

测试用例如下：

TC-01 默认 base_url
- 构造 Client()，断言 base_url == "http://127.0.0.1:5500"

TC-02 自定义 base_url
- 构造 Client("http://myserver:9000")，断言 base_url == "http://myserver:9000"

TC-03 upload 发送正确请求
- mock requests.post 返回假 response
- 用 tmp 临时文件作为 local_path
- 调用 upload("/remote/a.txt", tmp文件路径)
- 断言 requests.post 的 URL 含 ?path=/remote/a.txt，files 参数含字段 file
- 断言返回值是 mock 的 response 对象

TC-04 download 写入本地文件
- mock requests.get 返回 content = b"hello"
- 调用 download("/remote/a.txt", 临时输出路径)
- 断言本地文件内容为 b"hello"
- 断言 URL 含 ?path=/remote/a.txt

TC-05 list_files 返回 response
- mock requests.get 返回假 response
- 调用 list_files("/remote/dir/")
- 断言 URL 含 ?path=/remote/dir/
- 断言返回值是 mock 的 response 对象

测试代码要求：简单直接，每个 test 方法不超过 15 行。
