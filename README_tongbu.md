# Tongbu.Tui.Nms.Inner 项目提交获取工具

## 项目信息

- **项目 ID**: 508
- **项目名称**: Tongbu.Tui.Nms.Inner
- **Git 站点**: http://git.server.tongbu.com/
- **完整路径**: http://git.server.tongbu.com/tuigroup/tongbu.tui.nms.inner
- **Access Token**: JyxNC-T2QxK-wDursXPs

## 快速使用

### 1. 获取 dev 分支的最新 20 条提交（JSON格式）

```bash
python fetch_tongbu_commits.py
```

### 2. 获取指定分支的提交

```bash
# 获取 master 分支
python fetch_tongbu_commits.py --branch master

# 获取 main 分支
python fetch_tongbu_commits.py --branch main

# 获取 dev 分支（默认）
python fetch_tongbu_commits.py --branch dev
```

### 3. 指定获取数量

```bash
# 获取最新 10 条提交
python fetch_tongbu_commits.py --per-page 10

# 获取最新 50 条提交
python fetch_tongbu_commits.py --per-page 50
```

### 4. 保存到 JSON 文件

```bash
# 保存到默认文件名
python fetch_tongbu_commits.py --output tongbu_commits.json

# 保存到自定义文件名
python fetch_tongbu_commits.py --output dev_commits_20250101.json
```

### 5. 只输出 JSON，不显示可读格式

```bash
python fetch_tongbu_commits.py --json-only
```

### 6. 组合使用

```bash
# 获取 dev 分支最新 30 条提交，保存到文件
python fetch_tongbu_commits.py --branch dev --per-page 30 --output dev_latest.json

# 获取 master 分支最新 5 条提交，只显示 JSON
python fetch_tongbu_commits.py --branch master --per-page 5 --json-only
```

## Python 代码中调用

```python
from fetch_tongbu_commits import fetch_tongbu_commits
import json

# 获取 dev 分支最新 20 条提交
result = fetch_tongbu_commits(branch='dev', per_page=20)

# 检查结果
if result['success']:
    print(f"成功获取 {result['count']} 条提交")
    
    # 输出 JSON
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # 遍历提交
    for commit in result['commits']:
        print(f"标题: {commit['title']}")
        print(f"作者: {commit['author_name']}")
        print(f"时间: {commit['authored_date']}")
        print(f"链接: {commit['web_url']}")
        print('-' * 40)
else:
    print(f"获取失败: {result['error']}")
```

## 返回的 JSON 数据结构

```json
{
  "success": true,
  "count": 20,
  "error": null,
  "commits": [
    {
      "id": "完整的commit ID",
      "short_id": "短commit ID",
      "title": "提交标题",
      "message": "完整的提交消息",
      "author_name": "作者名称",
      "author_email": "作者邮箱",
      "authored_date": "2025-01-30T10:30:00.000+08:00",
      "committer_name": "提交者名称",
      "committer_email": "提交者邮箱",
      "committed_date": "2025-01-30T10:30:00.000+08:00",
      "web_url": "http://git.server.tongbu.com/..."
    }
  ]
}
```

## 常见问题

### 1. 如何获取不同分支？

使用 `--branch` 参数指定分支名称：
```bash
python fetch_tongbu_commits.py --branch your_branch_name
```

### 2. 获取失败怎么办？

检查以下几点：
- 确认网络可以访问 http://git.server.tongbu.com/
- 确认 Access Token 是否有效
- 确认 Project ID (508) 是否正确
- 确认分支名称是否存在

### 3. 如何获取更多提交？

使用 `--per-page` 参数：
```bash
python fetch_tongbu_commits.py --per-page 100
```

### 4. 如何只看 JSON 输出？

使用 `--json-only` 参数：
```bash
python fetch_tongbu_commits.py --json-only
```

或者使用管道：
```bash
python fetch_tongbu_commits.py --json-only > commits.json
```

## 命令行参数说明

| 参数 | 说明 | 默认值 | 示例 |
|------|------|--------|------|
| `--branch` | 分支名称 | `dev` | `--branch master` |
| `--per-page` | 获取的提交数量 | `20` | `--per-page 50` |
| `--output` | 保存到 JSON 文件 | 无 | `--output result.json` |
| `--json-only` | 只输出 JSON 格式 | `False` | `--json-only` |

## 输出示例

### 标准输出（包含 JSON 和可读格式）

```
================================================================================
项目信息:
  项目ID: 508
  项目名称: Tongbu.Tui.Nms.Inner
  项目路径: http://git.server.tongbu.com/tuigroup/tongbu.tui.nms.inner
  分支: dev
  获取数量: 20
================================================================================

正在请求: http://git.server.tongbu.com/api/v4/projects/508/repository/commits
成功获取 20 条提交记录

✅ 成功获取 20 条提交记录

================================================================================
JSON 格式输出:
================================================================================
{
  "success": true,
  "commits": [...],
  "count": 20,
  "error": null
}

================================================================================
可读格式摘要:
================================================================================

[提交 #1]
  ID: abc123
  标题: 修复了某个bug
  作者: 张三 <zhangsan@example.com>
  时间: 2025-01-30T10:30:00.000+08:00
  链接: http://git.server.tongbu.com/...
```

## 注意事项

⚠️ **Access Token 安全**
- 代码中包含的 Access Token 仅供内部使用
- 请勿将包含 Token 的代码提交到公共仓库
- 建议使用环境变量或配置文件存储敏感信息

🔒 **网络访问**
- 确保运行环境可以访问 http://git.server.tongbu.com/
- 如有防火墙或代理，请配置相应的网络设置

