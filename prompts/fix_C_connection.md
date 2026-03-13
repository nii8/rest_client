这不是代码问题，按以下步骤操作：

第一步：开一个终端，运行：
python tests/mock_server.py

第二步：确认终端显示：
Running on http://127.0.0.1:【端口】

第三步：开另一个终端，运行测试：
python tests/test_client.py

如果 mock_server.py 启动报错，把报错内容贴给 OpenCode，加上以下要求：
只修复 tests/mock_server.py，不改其他文件，只输出修复后的完整 mock_server.py。
