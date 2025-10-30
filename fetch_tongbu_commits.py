#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
获取 Tongbu.Tui.Nms.Inner 项目的最新提交
"""

import json
from git_commits_fetcher import main


def fetch_tongbu_commits(branch='dev', per_page=20):
    """
    获取同步推项目的最新提交
    
    参数:
        branch: 分支名称，默认 'dev'
        per_page: 获取的提交数量，默认 20
    
    返回:
        字典格式的结果
    """
    # 项目配置
    access_token = 'JyxNC-T2QxK-wDursXPs'
    project_id = '508'
    base_url = 'http://git.server.tongbu.com/api/v4'
    platform = 'gitlab'
    
    print(f'=' * 80)
    print(f'项目信息:')
    print(f'  项目ID: {project_id}')
    print(f'  项目名称: Tongbu.Tui.Nms.Inner')
    print(f'  项目路径: http://git.server.tongbu.com/tuigroup/tongbu.tui.nms.inner')
    print(f'  分支: {branch}')
    print(f'  获取数量: {per_page}')
    print(f'=' * 80)
    print()
    
    # 调用 main 函数获取提交
    result = main(
        access_token=access_token,
        project_id=project_id,
        platform=platform,
        base_url=base_url,
        per_page=per_page,
        ref_name=branch
    )
    
    return result


def print_commits_json(result):
    """
    以 JSON 格式输出提交内容
    
    参数:
        result: main 函数返回的结果字典
    """
    if result['success']:
        print(f'\n✅ 成功获取 {result["count"]} 条提交记录\n')
        
        # 输出完整的 JSON
        print('=' * 80)
        print('JSON 格式输出:')
        print('=' * 80)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
    else:
        print(f'\n❌ 获取失败: {result["error"]}\n')
        print('完整错误信息 (JSON):')
        print(json.dumps(result, indent=2, ensure_ascii=False))


def print_commits_readable(result):
    """
    以可读格式输出提交内容（补充显示）
    
    参数:
        result: main 函数返回的结果字典
    """
    if not result['success']:
        return
    
    print('\n' + '=' * 80)
    print('可读格式摘要:')
    print('=' * 80)
    
    for idx, commit in enumerate(result['commits'], 1):
        print(f"\n[提交 #{idx}]")
        print(f"  ID: {commit.get('short_id', 'N/A')}")
        print(f"  标题: {commit.get('title', 'N/A')}")
        print(f"  作者: {commit.get('author_name', 'N/A')} <{commit.get('author_email', 'N/A')}>")
        print(f"  时间: {commit.get('authored_date', 'N/A')}")
        
        if commit.get('web_url'):
            print(f"  链接: {commit.get('web_url')}")
        
        # 如果提交消息有多行，显示完整内容
        message = commit.get('message', '')
        if message and '\n' in message:
            print(f"  完整消息:")
            for line in message.split('\n'):
                if line.strip():
                    print(f"    {line}")
        
        print('-' * 80)


def save_to_json_file(result, filename='tongbu_commits.json'):
    """
    保存结果到 JSON 文件
    
    参数:
        result: main 函数返回的结果字典
        filename: 保存的文件名
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f'\n💾 结果已保存到文件: {filename}')
        return True
    except Exception as e:
        print(f'\n❌ 保存文件失败: {str(e)}')
        return False


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(
        description='获取 Tongbu.Tui.Nms.Inner 项目的最新提交'
    )
    parser.add_argument(
        '--branch', 
        default='dev', 
        help='分支名称 (默认: dev)'
    )
    parser.add_argument(
        '--per-page', 
        type=int, 
        default=20, 
        help='获取的提交数量 (默认: 20)'
    )
    parser.add_argument(
        '--output', 
        help='保存到 JSON 文件 (可选)'
    )
    parser.add_argument(
        '--json-only',
        action='store_true',
        help='只输出 JSON 格式，不显示可读格式摘要'
    )
    
    args = parser.parse_args()
    
    # 获取提交
    result = fetch_tongbu_commits(
        branch=args.branch,
        per_page=args.per_page
    )
    
    # 输出 JSON 格式
    print_commits_json(result)
    
    # 输出可读格式（除非指定 --json-only）
    if not args.json_only and result['success']:
        print_commits_readable(result)
    
    # 保存到文件（如果指定）
    if args.output:
        save_to_json_file(result, args.output)
    
    # 退出码
    exit(0 if result['success'] else 1)

