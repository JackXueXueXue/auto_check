# AI代码审核功能使用说明

## 🎯 功能说明

现在工具已经支持获取每次提交的**具体改动内容（diff）**，可以直接将改动前后的代码传给AI大模型进行审核！

---

## 📋 数据结构说明

每个提交记录现在包含以下信息：

```python
{
    'id': '提交ID',
    'title': '提交标题',
    'message': '完整提交信息',
    'author_name': '作者',
    'diff': {
        'success': True,
        'files': [
            {
                'old_path': '原文件路径',
                'new_path': '新文件路径',
                'change_type': 'modified',  # added, deleted, modified, renamed
                'diff': '标准unified diff格式的改动内容',
                'additions': 10,  # 新增行数
                'deletions': 5   # 删除行数
            }
        ],
        'diff_text': '完整的diff文本'
    }
}
```

---

## 🚀 使用方法

### 方法1：直接运行（自动获取diff）

```bash
python reviews_scraper.py
```

会获取默认项目的提交记录，并**自动获取每个提交的改动内容**。

---

### 方法2：输出AI审核格式（Markdown）

在终端显示AI审核友好的格式：

```bash
python reviews_scraper.py --ai-review
```

输出示例：
```markdown
## 提交信息
提交ID: 56c6a6e0
标题: 修改:调整
作者: xuexiaojie
提交时间: 2025-03-05T19:37:40.000+08:00

## 改动统计
- 改动文件数: 2
- 新增行数: +15
- 删除行数: -8

## 代码改动详情

### 修改文件: src/main.py

```diff
--- a/src/main.py
+++ b/src/main.py
@@ -10,6 +10,7 @@ def main():
     print("Hello")
+    print("New line")
     return 0
```

---

### 方法3：保存AI审核格式到文件

将AI审核格式保存到Markdown文件：

```bash
python reviews_scraper.py --ai-review-output review.md
```

然后可以直接：
1. 打开 `review.md` 文件
2. 复制内容
3. 粘贴给AI大模型（如ChatGPT、Claude等）进行代码审核

---

### 方法4：保存完整JSON数据

保存包含所有diff信息的JSON文件：

```bash
python reviews_scraper.py --output commits.json
```

JSON文件中包含：
- 所有提交的完整信息
- 每个提交的diff内容（改动前后的代码对比）
- 可以编程方式处理数据

---

### 方法5：不获取diff（提高速度）

如果只需要提交基本信息，不需要改动内容：

```bash
python reviews_scraper.py --no-diff
```

这样可以提高运行速度，因为不需要为每个提交额外请求diff。

---

## 💡 AI审核示例提示词

将改动内容传给AI时，可以使用这样的提示词：

```
请帮我审核以下Git提交的代码改动：

[这里粘贴 --ai-review 输出的内容]

请检查：
1. 是否存在潜在bug
2. 代码逻辑是否合理
3. 是否有安全风险
4. 是否符合最佳实践
5. 是否需要改进建议
```

---

## 📝 在Python代码中使用

```python
from reviews_scraper import main, format_for_ai_review

# 获取提交记录（包含diff）
result = main(
    include_diff=True  # 获取改动内容
)

if result['success']:
    for commit in result['commits']:
        # 获取AI审核格式
        ai_review_text = format_for_ai_review(commit)
        if ai_review_text:
            print(ai_review_text)
            # 可以传给AI审核
            # send_to_ai(ai_review_text)
```

---

## 🎨 diff格式说明

工具返回的是**标准unified diff格式**，例如：

```diff
--- a/src/main.py
+++ b/src/main.py
@@ -10,7 +10,8 @@ def main():
     print("Hello")
-    old_code
+    new_code
     return 0
```

格式说明：
- `--- a/文件名` - 修改前的文件
- `+++ b/文件名` - 修改后的文件
- `@@ -行号,行数 +行号,行数 @@` - 改动的范围
- `-` 开头的行 - 删除的代码
- `+` 开头的行 - 新增的代码
- 没有前缀的行 - 未改动的上下文

---

## ⚡ 性能提示

- 获取diff会增加API请求次数（每个提交需要额外1次请求）
- 如果提交数量多，可能需要一些时间
- 建议先用 `--per-page 5` 测试少量提交

---

## 📚 完整示例

```bash
# 获取最近5个提交，包含改动内容，保存AI审核格式
python reviews_scraper.py --per-page 5 --ai-review-output review.md

# 获取提交并保存JSON（包含完整diff数据）
python reviews_scraper.py --per-page 10 --output commits.json

# 显示AI审核格式并保存到文件
python reviews_scraper.py --ai-review --ai-review-output review.md
```

---

## ✅ 已完成功能

- ✅ 自动获取每次提交的改动内容（diff）
- ✅ 支持标准unified diff格式
- ✅ 统计新增/删除行数
- ✅ 识别文件改动类型（新增/删除/修改/重命名）
- ✅ AI审核友好格式输出（Markdown）
- ✅ 保存JSON数据供编程处理
- ✅ 支持GitLab和GitHub

现在你可以轻松地将代码改动传给AI进行审核了！🎉

