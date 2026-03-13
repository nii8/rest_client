# Prompt 模板库使用说明

## 第一步：替换变量

打开每个提示词文件，把 `【】` 里的占位符替换成你的实际值：

| 变量 | 含义 | 示例 |
|------|------|------|
| 【包名】 | Python 包名 | aust |
| 【路径前缀】 | 路径前缀字符串（末尾必须有斜杠） | /aa/bb/cc/ |
| 【路径前缀常量名】 | 常量的变量名 | BASE_PATH |
| 【上传方法名】 | 上传方法名 | upload |
| 【下载方法名】 | 下载方法名 | download |
| 【列表方法名】 | 列表方法名 | list_files |
| 【上传路由】 | 上传 HTTP 路由 | upload |
| 【下载路由】 | 下载 HTTP 路由 | download |
| 【列表路由】 | 列表 HTTP 路由 | list |
| 【端口】 | 服务端口号 | 5500 |

---

## 第二步：生成代码（按顺序执行）

每次提示词最前面必须先粘贴 `00_master.md` 的内容，再粘贴当前提示词。

| 顺序 | 文件 | 生成内容 |
|------|------|------|
| 1 | `00_master.md` | 每次必带，单独不执行 |
| 2 | `01_exception.md` | 【包名】/exception.py |
| 3 | `02_client.md` | 【包名】/client.py |
| 4 | `03_mock_server.md` | tests/mock_server.py |
| 5 | `04_test_client.md` | tests/test_client.py |

---

## 第三步：运行测试

```
# 终端 1：启动服务
python tests/mock_server.py

# 终端 2：运行测试
python tests/test_client.py
```

---

## 出错了？用修复提示词

同样需要在最前面粘贴 `00_master.md`。

| 文件 | 什么时候用 |
|------|------|
| `fix_A_validation.md` | 路径校验对合法路径也报错 |
| `fix_B_import.md` | 运行报 ImportError |
| `fix_C_connection.md` | 测试报连接失败（不是代码问题） |
| `fix_D_test_order.md` | test_09 或 test_10 失败 |
