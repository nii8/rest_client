【粘贴 00_master.md 内容】

实现文件：【包名】/client.py

导入：
import os
import requests
from .exception import validate_remote_path, handle_response, 【路径前缀常量名】

实现 Client 类：
- __init__(self, base_url="http://127.0.0.1:【端口】")，保存 self.base_url

每个方法的处理流程：
  1. validate_remote_path 校验 → 失败则打印错误并返回 {"ok": False, "error": err}
  2. requests 调用 → ConnectionError 则打印 "无法连接服务: {self.base_url}"，返回 {"ok": False, "error": "无法连接服务"}
  3. 返回 handle_response(response)

方法1：【上传方法名】(self, remote_path, local_path)
  - 额外校验：local_path 不存在 → 打印 "本地文件不存在: {local_path}"，返回 {"ok": False, "error": "本地文件不存在"}
  - 请求：POST {self.base_url}/【上传路由】?path=remote_path，multipart files={"file": 文件对象}

方法2：【下载方法名】(self, remote_path, local_path)
  - 请求前执行：dirname = os.path.dirname(local_path)，如果 dirname 不为空才执行 os.makedirs(dirname, exist_ok=True)
  - 请求：GET {self.base_url}/【下载路由】?path=remote_path
  - handle_response 返回 ok=True 时：把 response.content 写入 local_path

方法3：【列表方法名】(self, remote_path)
  - 请求：GET {self.base_url}/【列表路由】?path=remote_path
