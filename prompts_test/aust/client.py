import os
import requests
from .exception import validate_remote_path, handle_response, BASE_PATH


class Client:
    def __init__(self, base_url="http://127.0.0.1:5500"):
        self.base_url = base_url

    def upload(self, remote_path, local_path):
        err = validate_remote_path(remote_path)
        if err:
            print(err)
            return {"ok": False, "error": err}
        if not os.path.exists(local_path):
            print(f"本地文件不存在: {local_path}")
            return {"ok": False, "error": "本地文件不存在"}
        try:
            with open(local_path, "rb") as f:
                response = requests.post(
                    f"{self.base_url}/upload",
                    params={"path": remote_path},
                    files={"file": f}
                )
        except requests.exceptions.ConnectionError:
            print(f"无法连接服务: {self.base_url}")
            return {"ok": False, "error": "无法连接服务"}
        return handle_response(response)

    def download(self, remote_path, local_path):
        err = validate_remote_path(remote_path)
        if err:
            print(err)
            return {"ok": False, "error": err}
        dirname = os.path.dirname(local_path)
        if dirname:
            os.makedirs(dirname, exist_ok=True)
        try:
            response = requests.get(
                f"{self.base_url}/download",
                params={"path": remote_path}
            )
        except requests.exceptions.ConnectionError:
            print(f"无法连接服务: {self.base_url}")
            return {"ok": False, "error": "无法连接服务"}
        result = handle_response(response)
        if result["ok"]:
            with open(local_path, "wb") as f:
                f.write(response.content)
        return result

    def list_files(self, remote_path):
        err = validate_remote_path(remote_path)
        if err:
            print(err)
            return {"ok": False, "error": err}
        try:
            response = requests.get(
                f"{self.base_url}/list",
                params={"path": remote_path}
            )
        except requests.exceptions.ConnectionError:
            print(f"无法连接服务: {self.base_url}")
            return {"ok": False, "error": "无法连接服务"}
        return handle_response(response)
