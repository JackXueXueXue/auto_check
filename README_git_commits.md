# Git 提交内容获取工具

通过 `access_token` 和 `project_id` 获取指定项目的最新提交内容。

## 功能特点

- ✅ 支持 GitLab 和 GitHub
- ✅ 返回统一的数据结构
- ✅ 完善的异常处理
- ✅ 支持命令行和 Python 代码调用
- ✅ 支持自托管 GitLab

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 方式1: Python 代码中调用

```python
from git_commits_fetcher import main

# GitLab 示例
result = main(
    access_token="your_token_here",
    project_id="12345",
    platform='gitlab',
    per_page=20
)

# 检查结果
if result['success']:
    print(f"成功获取 {result['count']} 条提交")
    for commit in result['commits']:
        print(f"标题: {commit['title']}")
        print(f"作者: {commit['author_name']}")
else:
    print(f"错误: {result['error']}")
```

### 方式2: 命令行调用

```bash
# GitLab 示例
python git_commits_fetcher.py --token YOUR_TOKEN --project-id 12345 --platform gitlab

# GitHub 示例
python git_commits_fetcher.py --token YOUR_TOKEN --project-id "owner/repo" --platform github

# 指定分支
python git_commits_fetcher.py --token YOUR_TOKEN --project-id 12345 --ref main

# 保存到文件
python git_commits_fetcher.py --token YOUR_TOKEN --project-id 12345 --output commits.json
```

## 参数说明

### 必需参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `access_token` | API 访问令牌 | `glpat-xxx` (GitLab) 或 `ghp_xxx` (GitHub) |
| `project_id` | 项目标识 | GitLab: `12345`<br>GitHub: `"owner/repo"` |

### 可选参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `platform` | 平台类型 | `'gitlab'` |
| `base_url` | 自定义 API 地址 | `None` |
| `per_page` | 返回的提交数量 | `20` |
| `ref_name` | 分支或标签名称 | `None` (默认分支) |

## 返回数据结构

```python
{
    'success': bool,      # 是否成功获取
    'commits': [          # 提交列表
        {
            'title': str,           # 提交标题
            'message': str,         # 完整提交消息
            'author_name': str,     # 作者名称
            'author_email': str,    # 作者邮箱
            'authored_date': str,   # 提交时间
            'id': str,              # 提交ID (GitLab)
            'sha': str,             # 提交SHA (GitHub)
            'web_url': str,         # 提交链接
            # ... 更多字段
        }
    ],
    'count': int,         # 提交数量
    'error': str or None  # 错误信息（如果有）
}
```

## 使用示例

### GitLab 私有仓库

```python
from git_commits_fetcher import main

result = main(
    access_token="glpat-xxxxxxxxxxxx",
    project_id="12345",
    platform='gitlab',
    per_page=10
)
```

### GitHub 公共仓库

```python
result = main(
    access_token="ghp_xxxxxxxxxxxx",
    project_id="torvalds/linux",
    platform='github',
    per_page=5,
    ref_name='master'
)
```

### 自托管 GitLab

```python
result = main(
    access_token="your_token",
    project_id="123",
    platform='gitlab',
    base_url="https://gitlab.example.com/api/v4"
)
```

## 获取 Access Token

### GitLab
1. 登录 GitLab
2. 点击头像 → Settings → Access Tokens
3. 创建新 Token，勾选 `read_api` 权限
4. 复制生成的 Token

### GitHub
1. 登录 GitHub
2. Settings → Developer settings → Personal access tokens
3. Generate new token，勾选 `repo` 权限
4. 复制生成的 Token

## 注意事项

- Access Token 请妥善保管，不要泄露
- Token 需要有相应的权限（GitLab: `read_api`，GitHub: `repo`）
- GitHub 的 project_id 格式为 `"owner/repo"`
- API 请求有速率限制，具体参考各平台文档

## 文件说明

- `git_commits_fetcher.py` - 主程序
- `example_usage.py` - 使用示例
- `requirements.txt` - 依赖包
- `README_git_commits.md` - 本文档

