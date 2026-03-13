BASE_PATH = "/aa/bb/cc/"


def validate_remote_path(remote_path):
    if not remote_path:
        return "路径不合法：路径不能为空"
    if " " in remote_path:
        return "路径不合法：不能含有空格"
    if not remote_path.startswith(BASE_PATH):
        return "路径不合法：必须以 /aa/bb/cc/ 开头"
    return None


def handle_response(response):
    if 200 <= response.status_code < 300:
        return {"ok": True, "data": response}
    print(f"错误码: {response.status_code}，错误信息: {response.text}")
    return {"ok": False, "error": response.text}
