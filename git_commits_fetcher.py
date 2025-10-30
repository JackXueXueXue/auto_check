#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Git提交内容获取工具
支持GitLab和GitHub API来获取项目的最新提交信息
"""

import requests
import json


def main(access_token, project_id, platform='gitlab', base_url=None, per_page=20, ref_name=None):
    """
    获取Git项目的最新提交内容
    
    参数:
        access_token: API访问令牌
        project_id: 项目ID（GitLab）或仓库路径（GitHub格式：owner/repo）
        platform: 平台类型，'gitlab' 或 'github'，默认 'gitlab'
        base_url: 自定义API基础URL（用于自托管GitLab等）
        per_page: 返回的提交数量，默认20
        ref_name: 分支或标签名称（可选）
    
    返回:
        字典结构:
        {
            'success': bool,  # 是否成功获取
            'commits': list,  # 提交列表
            'count': int,     # 提交数量
            'error': str      # 错误信息（如果有）
        }
    """
    # 初始化返回字典，确保结构一致
    response = {
        'success': False,
        'commits': [],
        'count': 0,
        'error': None
    }
    
    try:
        # 参数验证
        if not access_token or not project_id:
            response['error'] = '缺少必需参数: access_token 和 project_id'
            return response
        
        platform = platform.lower()
        
        # 设置API基础URL
        if base_url:
            api_base_url = base_url.rstrip('/')
        elif platform == 'gitlab':
            api_base_url = 'https://gitlab.com/api/v4'
        elif platform == 'github':
            api_base_url = 'https://api.github.com'
        else:
            response['error'] = f'不支持的平台: {platform}，请使用 gitlab 或 github'
            return response
        
        # 设置请求头
        if platform == 'gitlab':
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
        else:  # GitHub
            headers = {
                'Authorization': f'token {access_token}',
                'Accept': 'application/vnd.github.v3+json',
                'Content-Type': 'application/json'
            }
        
        # 构建API URL和参数
        if platform == 'gitlab':
            url = f'{api_base_url}/projects/{project_id}/repository/commits'
            params = {
                'per_page': per_page,
                'order_by': 'created_at',
                'sort': 'desc'
            }
            if ref_name:
                params['ref_name'] = ref_name
        else:  # GitHub
            url = f'{api_base_url}/repos/{project_id}/commits'
            params = {'per_page': per_page}
            if ref_name:
                params['sha'] = ref_name
        
        print(f'正在请求: {url}')
        
        # 发起API请求
        api_response = requests.get(url, headers=headers, params=params, timeout=30)
        api_response.raise_for_status()
        
        commits_data = api_response.json()
        
        print(f'成功获取 {len(commits_data)} 条提交记录')
        
        # 格式化提交数据
        formatted_commits = []
        
        if platform == 'gitlab':
            for commit_item in commits_data:
                formatted_commits.append({
                    'id': commit_item.get('id'),
                    'short_id': commit_item.get('short_id'),
                    'title': commit_item.get('title'),
                    'message': commit_item.get('message'),
                    'author_name': commit_item.get('author_name'),
                    'author_email': commit_item.get('author_email'),
                    'authored_date': commit_item.get('authored_date'),
                    'committer_name': commit_item.get('committer_name'),
                    'committer_email': commit_item.get('committer_email'),
                    'committed_date': commit_item.get('committed_date'),
                    'web_url': commit_item.get('web_url'),
                })
        else:  # GitHub
            for commit_item in commits_data:
                commit_info = commit_item.get('commit', {})
                author_info = commit_info.get('author', {})
                committer_info = commit_info.get('committer', {})
                formatted_commits.append({
                    'sha': commit_item.get('sha'),
                    'short_sha': commit_item.get('sha', '')[:7],
                    'message': commit_info.get('message', ''),
                    'title': commit_info.get('message', '').split('\n')[0],
                    'author_name': author_info.get('name'),
                    'author_email': author_info.get('email'),
                    'authored_date': author_info.get('date'),
                    'committer_name': committer_info.get('name'),
                    'committer_email': committer_info.get('email'),
                    'committed_date': committer_info.get('date'),
                    'html_url': commit_item.get('html_url'),
                })
        
        # 设置成功响应
        response['success'] = True
        response['commits'] = formatted_commits
        response['count'] = len(formatted_commits)
        
    except requests.exceptions.HTTPError as e:
        # HTTP错误处理
        error_msg = f'API请求失败: {str(e)}'
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_detail = e.response.json()
                error_msg += f' - {error_detail}'
            except ValueError:
                error_msg += f' - {e.response.text}'
        print(error_msg)
        response['error'] = error_msg
        
    except requests.exceptions.RequestException as e:
        # 网络请求异常
        error_msg = f'网络请求错误: {str(e)}'
        print(error_msg)
        response['error'] = error_msg
        
    except Exception as e:
        # 其他异常
        error_msg = f'发生错误: {str(e)}'
        print(error_msg)
        response['error'] = error_msg
    
    # 返回结果字典，确保所有情况下都有相同的键
    return response


if __name__ == '__main__':
    # 命令行使用示例
    import argparse
    
    parser = argparse.ArgumentParser(description='获取Git项目的最新提交内容')
    parser.add_argument('--token', required=True, help='API访问令牌')
    parser.add_argument('--project-id', required=True, help='项目ID (GitLab) 或仓库路径 (GitHub: owner/repo)')
    parser.add_argument('--platform', default='gitlab', choices=['gitlab', 'github'], help='平台类型 (默认: gitlab)')
    parser.add_argument('--base-url', help='自定义API基础URL')
    parser.add_argument('--per-page', type=int, default=20, help='返回的提交数量 (默认: 20)')
    parser.add_argument('--ref', help='分支或标签名称')
    parser.add_argument('--output', help='保存到JSON文件')
    
    args = parser.parse_args()
    
    # 调用main函数
    result = main(
        access_token=args.token,
        project_id=args.project_id,
        platform=args.platform,
        base_url=args.base_url,
        per_page=args.per_page,
        ref_name=args.ref
    )
    
    # 输出结果
    if result['success']:
        print(f"\n{'='*80}")
        print(f"成功获取 {result['count']} 条提交记录")
        print(f"{'='*80}\n")
        
        for idx, commit in enumerate(result['commits'], 1):
            print(f"[提交 #{idx}]")
            
            # GitLab使用id，GitHub使用sha
            if 'short_id' in commit:
                print(f"  ID: {commit.get('short_id', 'N/A')}")
            elif 'short_sha' in commit:
                print(f"  SHA: {commit.get('short_sha', 'N/A')}")
            
            print(f"  标题: {commit.get('title', 'N/A')}")
            print(f"  作者: {commit.get('author_name', 'N/A')} <{commit.get('author_email', 'N/A')}>")
            print(f"  提交时间: {commit.get('authored_date', 'N/A')}")
            
            if commit.get('web_url'):
                print(f"  链接: {commit.get('web_url')}")
            elif commit.get('html_url'):
                print(f"  链接: {commit.get('html_url')}")
            
            print(f"\n{'-'*80}\n")
        
        # 保存到文件
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"结果已保存到: {args.output}")
    else:
        print(f"\n错误: {result['error']}")

