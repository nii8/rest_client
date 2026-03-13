【粘贴 00_master.md 内容】

实现文件：【包名】/exception.py

要求：
1. 文件第一行定义全局常量：【路径前缀常量名】 = "【路径前缀】"
2. 实现函数 validate_remote_path(remote_path)：
   - remote_path 为 None 或空字符串 → 返回 "路径不合法：路径不能为空"
   - remote_path 含空格 → 返回 "路径不合法：不能含有空格"
   - remote_path 不以 【路径前缀常量名】 开头 → 返回 "路径不合法：必须以 【路径前缀】 开头"
   - 合法 → 返回 None
   - 检测顺序：空值 > 空格 > 前缀
3. 实现函数 handle_response(response)：
   - 200 <= status_code < 300 → 返回 {"ok": True, "data": response}
   - 其他 → 打印 "错误码: {status_code}，错误信息: {response.text}"，返回 {"ok": False, "error": response.text}
