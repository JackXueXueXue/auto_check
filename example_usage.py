#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用示例：如何调用Git提交获取程序
"""

from git_commits_fetcher import main

# 方式1: 直接使用Python代码
def example_direct_usage():
    """直接使用main函数的示例"""
    
    # 配置参数
    access_token = "your_access_token_here"  # 替换为你的访问令牌
    project_id = "12345"  # GitLab项目ID，或GitHub的 "owner/repo" 格式
    
    # GitLab示例
    result = main(
        access_token=access_token,
        project_id=project_id,
        platform='gitlab',
        per_page=20
    )
    
    # 检查结果
    if result['success']:
        print(f"成功获取 {result['count']} 条提交记录")
        
        # 遍历提交
        for commit in result['commits']:
            print(f"提交ID: {commit.get('short_id')}")
            print(f"标题: {commit.get('title')}")
            print(f"作者: {commit.get('author_name')}")
            print(f"时间: {commit.get('authored_date')}")
            print("-" * 40)
    else:
        print(f"获取失败: {result['error']}")


def example_github_usage():
    """GitHub示例"""
    
    access_token = "your_github_token"
    project_id = "owner/repo"  # GitHub格式
    
    result = main(
        access_token=access_token,
        project_id=project_id,
        platform='github',
        per_page=10,
        ref_name='main'  # 指定分支
    )
    
    if result['success']:
        print(f"成功获取 {result['count']} 条GitHub提交")
        for commit in result['commits']:
            print(f"SHA: {commit.get('short_sha')}")
            print(f"标题: {commit.get('title')}")
            print(f"链接: {commit.get('html_url')}")
            print()
    else:
        print(f"错误: {result['error']}")


def example_save_to_json():
    """保存结果到JSON文件的示例"""
    import json
    
    access_token = "your_token"
    project_id = "12345"
    
    result = main(
        access_token=access_token,
        project_id=project_id,
        platform='gitlab'
    )
    
    # 保存到JSON文件
    if result['success']:
        with open('commits_result.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print("结果已保存到 commits_result.json")


# 方式2: 命令行使用示例（在终端中运行）
"""
# GitLab示例:
python git_commits_fetcher.py --token YOUR_TOKEN --project-id 12345 --platform gitlab --per-page 20

# GitHub示例:
python git_commits_fetcher.py --token YOUR_TOKEN --project-id "owner/repo" --platform github --per-page 20

# 指定分支:
python git_commits_fetcher.py --token YOUR_TOKEN --project-id 12345 --ref main

# 保存到文件:
python git_commits_fetcher.py --token YOUR_TOKEN --project-id 12345 --output commits.json

# 自托管GitLab:
python git_commits_fetcher.py --token YOUR_TOKEN --project-id 12345 --base-url "https://gitlab.example.com/api/v4"
"""


if __name__ == "__main__":
    print("这是一个使用示例文件。")
    print("请编辑函数中的参数（access_token 和 project_id），然后运行。")
    print("\n或者使用命令行方式:")
    print("python git_commits_fetcher.py --token YOUR_TOKEN --project-id 12345")
    print("\n返回数据结构:")
    print({
        'success': True,  # 是否成功
        'commits': [],    # 提交列表
        'count': 0,       # 提交数量
        'error': None     # 错误信息
    })
