import os
from flask import Flask, request, jsonify, send_file

app = Flask(__name__)

STORAGE_DIR = os.path.join(os.path.dirname(__file__), "storage")


def storage_path(remote_path):
    # 去掉开头的 / 拼到 storage 目录下
    return os.path.join(STORAGE_DIR, remote_path.lstrip("/"))


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.post("/upload")
def upload():
    remote_path = request.args.get("path", "")
    if "file" not in request.files:
        return jsonify({"error": "缺少文件"}), 400
    file = request.files["file"]
    dest = storage_path(remote_path)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    file.save(dest)
    return jsonify({"message": "上传成功"})


@app.get("/download")
def download():
    remote_path = request.args.get("path", "")
    dest = storage_path(remote_path)
    if not os.path.exists(dest):
        return jsonify({"error": "文件不存在"}), 404
    return send_file(dest)


@app.get("/list")
def list_files():
    remote_path = request.args.get("path", "")
    dest = storage_path(remote_path)
    if not os.path.isdir(dest):
        return jsonify({"error": "路径不存在"}), 404
    files = [f for f in os.listdir(dest) if os.path.isfile(os.path.join(dest, f))]
    return jsonify({"files": files})


if __name__ == "__main__":
    app.run(port=5500)
