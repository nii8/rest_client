【粘贴 00_master.md 内容】

实现文件：tests/mock_server.py

用 Flask 实现，端口 【端口】，文件存放在 tests/storage/ 目录。

辅助函数 storage_path(remote_path)：
  return os.path.join(STORAGE_DIR, remote_path.lstrip("/"))

实现以下路由：
- GET /health → 返回 {"status": "ok"}，状态码 200
- POST /【上传路由】?path=<remote_path> → 接收 multipart file 字段名 "file"，按 path 存到 storage 目录，自动创建目录；缺少 file 字段返回 400
- GET /【下载路由】?path=<remote_path> → 从 storage 读文件返回二进制流，文件不存在返回 404
- GET /【列表路由】?path=<remote_path> → 列出 storage 对应目录所有文件名，返回 {"files": [...]}，目录不存在返回 404

末尾：
if __name__ == "__main__":
    app.run(port=【端口】)
