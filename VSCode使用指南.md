# VSCode 使用指南 - Tongbu 项目提交获取工具

## 🎯 最简单的方法（推荐新手）

### 方法 1: 直接运行 `简单运行.py`

1. **在 VSCode 中打开 `简单运行.py` 文件**

2. **点击右上角的运行按钮** ▶️
   - 或者按快捷键 `Ctrl + F5`

3. **完成！** 程序会自动：
   - 获取 dev 分支最新 20 条提交
   - 显示 JSON 格式数据
   - 显示可读格式摘要
   - 保存到 `commits_output.json` 文件

4. **修改参数**（可选）：
   - 打开 `简单运行.py`
   - 找到第 17-20 行
   - 修改这些配置：

   ```python
   branch = 'dev'          # 改成你想要的分支
   per_page = 20           # 改成你想要的数量
   save_to_file = True     # 是否保存到文件
   output_filename = 'commits_output.json'  # 文件名
   ```

---

## 🎯 方法 2: 使用 VSCode 终端（支持参数）

### 打开终端：

1. 菜单栏：`终端` → `新建终端`
2. 或快捷键：`` Ctrl + ` `` (反引号键)

### 运行命令：

```bash
# 基本使用（dev 分支，20 条）
python fetch_tongbu_commits.py

# 获取 master 分支
python fetch_tongbu_commits.py --branch master

# 获取 50 条
python fetch_tongbu_commits.py --per-page 50

# 保存到文件
python fetch_tongbu_commits.py --output my_commits.json

# 组合使用
python fetch_tongbu_commits.py --branch dev --per-page 30 --output result.json
```

---

## 🎯 方法 3: 使用 VSCode 调试配置（高级）

### 步骤：

1. **按 `F5` 键**，或者点击左侧的 🐛 调试图标

2. **选择运行配置**：
   - `简单运行 - 获取提交` （推荐）
   - `获取 dev 分支 20 条`
   - `获取 master 分支 10 条`
   - `获取并保存到文件`
   - `运行测试`

3. **点击绿色播放按钮** ▶️

### 修改配置（可选）：

打开 `.vscode/launch.json`，可以添加自己的配置：

```json
{
    "name": "我的自定义配置",
    "type": "debugpy",
    "request": "launch",
    "program": "${workspaceFolder}/fetch_tongbu_commits.py",
    "console": "integratedTerminal",
    "args": [
        "--branch", "你的分支名",
        "--per-page", "数量",
        "--output", "文件名.json"
    ]
}
```

---

## 🎯 方法 4: 在 Python 交互式窗口运行

### 步骤：

1. **打开 Python 文件**（任意 .py 文件）

2. **右键选择**：`在交互式窗口中运行当前文件`

3. **或者在 Python 交互窗口中直接输入**：

```python
from fetch_tongbu_commits import fetch_tongbu_commits
import json

# 获取提交
result = fetch_tongbu_commits(branch='dev', per_page=20)

# 查看结果
print(json.dumps(result, indent=2, ensure_ascii=False))

# 查看第一条提交
if result['success']:
    print(result['commits'][0])
```

---

## 📝 快速参考

### 命令行参数：

| 参数 | 说明 | 示例 |
|------|------|------|
| `--branch` | 分支名称 | `--branch master` |
| `--per-page` | 获取数量 | `--per-page 50` |
| `--output` | 保存文件 | `--output result.json` |
| `--json-only` | 只输出JSON | `--json-only` |

### Python 函数参数：

```python
fetch_tongbu_commits(
    branch='dev',      # 分支名称
    per_page=20        # 获取数量
)
```

---

## 🧪 测试功能

### 运行测试：

**方式 1 - 直接运行：**
1. 打开 `test_tongbu.py`
2. 点击右上角 ▶️ 运行按钮

**方式 2 - 终端运行：**
```bash
python test_tongbu.py
```

**方式 3 - 调试运行：**
1. 按 `F5`
2. 选择 "运行测试"

---

## 🔍 查看输出结果

### JSON 文件查看：

1. 运行程序后，会生成 JSON 文件（如 `commits_output.json`）
2. 在 VSCode 中打开这个文件
3. 按 `Shift + Alt + F` 格式化 JSON（更易读）

### 终端输出：

- 程序会在终端显示详细的输出
- 包括 JSON 格式和可读格式
- 可以滚动查看历史输出

---

## ⚙️ 项目配置信息

已经配置好的信息（无需修改）：

```
✅ 项目 ID:      508
✅ 项目名称:     Tongbu.Tui.Nms.Inner
✅ Access Token: JyxNC-T2QxK-wDursXPs
✅ Git 站点:     http://git.server.tongbu.com/
✅ API 地址:     http://git.server.tongbu.com/api/v4
```

这些信息已经在 `fetch_tongbu_commits.py` 中配置好了。

---

## 🎬 完整演示流程

### 【最简单流程】

```
1. 打开 VSCode
2. 打开 "简单运行.py" 文件
3. 点击右上角 ▶️ 运行按钮
4. 等待几秒，查看输出结果
5. 完成！
```

### 【使用终端流程】

```
1. 打开 VSCode
2. 按 Ctrl+` 打开终端
3. 输入: python fetch_tongbu_commits.py
4. 按回车
5. 查看输出
```

### 【带参数流程】

```
1. 打开 VSCode
2. 按 Ctrl+` 打开终端
3. 输入: python fetch_tongbu_commits.py --branch master --per-page 30
4. 按回车
5. 查看输出
```

---

## ❓ 常见问题

### Q: 运行时提示 "找不到模块 requests"

**A:** 需要安装依赖：
```bash
pip install requests
```

或者：
```bash
pip install -r requirements.txt
```

### Q: 如何修改获取的分支？

**A:** 三种方式：

1. **修改 `简单运行.py` 第 17 行**：
   ```python
   branch = 'master'  # 改成你想要的分支
   ```

2. **终端命令加参数**：
   ```bash
   python fetch_tongbu_commits.py --branch master
   ```

3. **Python 代码调用**：
   ```python
   result = fetch_tongbu_commits(branch='master')
   ```

### Q: 如何获取更多提交？

**A:** 修改数量参数：

```bash
python fetch_tongbu_commits.py --per-page 100
```

或修改 `简单运行.py` 第 18 行：
```python
per_page = 100
```

### Q: 输出的 JSON 在哪里？

**A:** 
- 如果使用 `简单运行.py`，输出在 `commits_output.json`
- 如果使用 `--output` 参数，在你指定的文件名
- 可以在 VSCode 左侧文件列表中找到

### Q: 如何只看 JSON，不看其他输出？

**A:** 使用 `--json-only` 参数：
```bash
python fetch_tongbu_commits.py --json-only
```

---

## 💡 小技巧

### 1. 快速重复运行

在终端按 `↑` (上箭头) 可以重复上一条命令

### 2. 清空终端

在终端输入 `cls` (Windows) 或 `clear` (Mac/Linux)

### 3. 查看历史命令

在终端按多次 `↑` 可以查看历史命令

### 4. 停止运行

如果程序卡住了，按 `Ctrl + C` 停止

### 5. 格式化 JSON

打开 JSON 文件后，按 `Shift + Alt + F` 自动格式化

---

## 🎯 推荐使用方式

### 新手推荐：
```
使用 简单运行.py
只需点击运行按钮即可
```

### 日常使用：
```
在终端输入命令
灵活使用参数
```

### 开发调试：
```
使用 F5 调试
可以设置断点
```

---

## 📞 需要帮助？

如果遇到问题：
1. 检查网络连接（能否访问 http://git.server.tongbu.com/）
2. 确认 Python 已安装（在终端输入 `python --version`）
3. 确认 requests 包已安装（`pip list | findstr requests`）
4. 查看终端的错误信息

---

**祝使用愉快！** 🎉

