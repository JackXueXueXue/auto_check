#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用配置文件获取提交（更安全的方式）
"""

import json
import os
from git_commits_fetcher import main


def load_config(config_file='config.json'):
    """
    加载配置文件
    
    参数:
        config_file: 配置文件路径
    
    返回:
        配置字典
    """
    # 如果 config.json 不存在，尝试使用 config_example.json
    if not os.path.exists(config_file) and os.path.exists('config_example.json'):
        config_file = 'config_example.json'
        print(f'⚠️  使用示例配置文件: {config_file}')
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        print(f'❌ 配置文件未找到: {config_file}')
        print(f'   请复制 config_example.json 为 config.json 并填写正确的配置')
        return None
    except json.JSONDecodeError as e:
        print(f'❌ 配置文件格式错误: {str(e)}')
        return None
    except Exception as e:
        print(f'❌ 加载配置文件失败: {str(e)}')
        return None


def fetch_commits_with_config(branch=None, per_page=None, config_file='config.json'):
    """
    使用配置文件获取提交
    
    参数:
        branch: 分支名称（可选，覆盖配置文件中的默认值）
        per_page: 获取数量（可选，覆盖配置文件中的默认值）
        config_file: 配置文件路径
    
    返回:
        结果字典
    """
    # 加载配置
    config = load_config(config_file)
    if not config:
        return {
            'success': False,
            'commits': [],
            'count': 0,
            'error': '无法加载配置文件'
        }
    
    # 参数优先级：命令行参数 > 配置文件
    branch = branch or config.get('default_branch', 'dev')
    per_page = per_page or config.get('default_per_page', 20)
    
    print(f'=' * 80)
    print(f'使用配置获取提交:')
    print(f'  项目ID: {config.get("project_id")}')
    print(f'  项目名称: {config.get("project_name")}')
    print(f'  Git站点: {config.get("base_url", "").replace("/api/v4", "")}')
    print(f'  分支: {branch}')
    print(f'  获取数量: {per_page}')
    print(f'=' * 80)
    print()
    
    # 调用 main 函数
    result = main(
        access_token=config.get('access_token'),
        project_id=config.get('project_id'),
        platform=config.get('platform', 'gitlab'),
        base_url=config.get('base_url'),
        per_page=per_page,
        ref_name=branch
    )
    
    return result


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(
        description='使用配置文件获取 Git 提交'
    )
    parser.add_argument(
        '--config',
        default='config.json',
        help='配置文件路径 (默认: config.json)'
    )
    parser.add_argument(
        '--branch',
        help='分支名称 (覆盖配置文件中的默认值)'
    )
    parser.add_argument(
        '--per-page',
        type=int,
        help='获取的提交数量 (覆盖配置文件中的默认值)'
    )
    parser.add_argument(
        '--output',
        help='保存到 JSON 文件'
    )
    parser.add_argument(
        '--json-only',
        action='store_true',
        help='只输出 JSON 格式'
    )
    
    args = parser.parse_args()
    
    # 获取提交
    result = fetch_commits_with_config(
        branch=args.branch,
        per_page=args.per_page,
        config_file=args.config
    )
    
    # 输出结果
    if result['success']:
        print(f'\n✅ 成功获取 {result["count"]} 条提交记录\n')
        
        if args.json_only:
            # 只输出 JSON
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            # 输出 JSON 和可读格式
            print('=' * 80)
            print('JSON 格式:')
            print('=' * 80)
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            # 可读格式摘要
            print('\n' + '=' * 80)
            print('提交摘要:')
            print('=' * 80)
            for idx, commit in enumerate(result['commits'], 1):
                print(f"\n[{idx}] {commit.get('title', 'N/A')}")
                print(f"    作者: {commit.get('author_name', 'N/A')}")
                print(f"    时间: {commit.get('authored_date', 'N/A')}")
                print(f"    ID: {commit.get('short_id', 'N/A')}")
        
        # 保存到文件
        if args.output:
            try:
                with open(args.output, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                print(f'\n💾 结果已保存到: {args.output}')
            except Exception as e:
                print(f'\n❌ 保存文件失败: {str(e)}')
    else:
        print(f'\n❌ 获取失败: {result["error"]}')
        print('\n错误详情 (JSON):')
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # 退出码
    exit(0 if result['success'] else 1)

