import requests


class Client:
    def __init__(self, base_url="http://127.0.0.1:5500"):
        self.base_url = base_url

    def upload(self, remote_path, local_path):
        with open(local_path, "rb") as f:
            return requests.post(f"{self.base_url}/upload", params={"path": remote_path}, files={"file": f})

    def download(self, remote_path, local_path):
        response = requests.get(f"{self.base_url}/download", params={"path": remote_path})
        with open(local_path, "wb") as f:
            f.write(response.content)
        return response

    def list_files(self, remote_path):
        return requests.get(f"{self.base_url}/list", params={"path": remote_path})
