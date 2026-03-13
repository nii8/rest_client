【粘贴 00_master.md 内容】

只修改 tests/test_client.py 中的 test_08 函数，不改其他函数。

问题：test_09_download 或 test_10_list 失败，原因是 test_08_upload 没有成功执行。

检查并修复 test_08_upload_success：
1. 上传路径必须是 "【路径前缀】test_upload.txt"
2. open() 写入内容必须是 "hello test"
3. 调用的方法名必须是 【上传方法名】

只输出修复后的 test_08 函数。
